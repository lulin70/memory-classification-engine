import os
import time
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.helpers import generate_memory_id, get_current_time
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.layers.rule_matcher import RuleMatcher
from memory_classification_engine.layers.pattern_analyzer import PatternAnalyzer
from memory_classification_engine.layers.semantic_classifier import SemanticClassifier
from memory_classification_engine.storage.tier2 import Tier2Storage
from memory_classification_engine.storage.tier3 import Tier3Storage
from memory_classification_engine.storage.tier4 import Tier4Storage
from memory_classification_engine.plugins import PluginManager
from memory_classification_engine.utils.performance import PerformanceMonitor, PerformanceOptimizer
from memory_classification_engine.utils.distributed import DistributedManager, DataSynchronizer
from memory_classification_engine.utils.tenant import TenantManager, Tenant

class MemoryClassificationEngine:
    """Memory Classification Engine."""
    
    def __init__(self, config_path: str = None):
        """Initialize the memory classification engine.
        
        Args:
            config_path: Path to the configuration file.
        """
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Initialize storage
        storage_path = self.config.get('storage.data_path', './data')
        os.makedirs(storage_path, exist_ok=True)
        
        self.tier2_storage = Tier2Storage(self.config.get('storage.tier2_path', './data/tier2'))
        self.tier3_storage = Tier3Storage(self.config.get('storage.tier3_path', './data/tier3'))
        self.tier4_storage = Tier4Storage(self.config.get('storage.tier4_path', './data/tier4'))
        
        # Initialize working memory
        self.working_memory = []
        self.max_work_memory_size = self.config.get('storage.max_work_memory_size', 100)
        
        # Initialize layers
        rules = self.config.get_rules().get('rules', [])
        self.rule_matcher = RuleMatcher(rules)
        self.pattern_analyzer = PatternAnalyzer()
        
        llm_enabled = self.config.get('llm.enabled', False)
        api_key = self.config.get('llm.api_key', '')
        self.semantic_classifier = SemanticClassifier(llm_enabled, api_key)
        
        # Initialize memory management
        self.forgetting_enabled = self.config.get('memory.forgetting.enabled', True)
        self.decay_factor = self.config.get('memory.forgetting.decay_factor', 0.9)
        self.min_weight = self.config.get('memory.forgetting.min_weight', 0.1)
        self.archive_interval = self.config.get('memory.forgetting.archive_interval', 86400)  # 24 hours
        
        self.deduplication_enabled = self.config.get('memory.deduplication.enabled', True)
        self.similarity_threshold = self.config.get('memory.deduplication.similarity_threshold', 0.8)
        
        self.conflict_resolution_strategy = self.config.get('memory.conflict_resolution.strategy', 'latest')
        
        # Initialize plugin manager
        plugins_dir = self.config.get('plugins.dir', None)
        self.plugin_manager = PluginManager(plugins_dir)
        self.plugin_manager.load_plugins()
        plugin_config = self.config.get('plugins', {})
        self.plugin_manager.initialize_plugins(plugin_config)
        
        # Initialize performance monitor
        perf_enabled = self.config.get('performance.enabled', True)
        log_interval = self.config.get('performance.log_interval', 60)
        self.performance_monitor = PerformanceMonitor(enabled=perf_enabled, log_interval=log_interval)
        self.performance_monitor.start()
        
        # Initialize distributed manager
        distributed_enabled = self.config.get('distributed.enabled', False)
        if distributed_enabled:
            node_id = self.config.get('distributed.node_id', None)
            port = self.config.get('distributed.port', 5000)
            discovery_interval = self.config.get('distributed.discovery_interval', 30)
            self.distributed_manager = DistributedManager(node_id, port, discovery_interval)
            self.distributed_manager.start()
        else:
            self.distributed_manager = None
        
        # Initialize last archive time
        self.last_archive_time = get_current_time()
        
        # Initialize cache
        self.cache = {}
        self.cache_size = 1000  # Maximum cache size
        self.cache_ttl = 3600  # Cache time-to-live in seconds
        
        # Initialize tenant manager
        self.tenant_manager = TenantManager()
        
        # Run initial archive
        self._run_archive()
    
    def _run_archive(self):
        """Run memory archive process to remove low-weight memories."""
        if not self.forgetting_enabled:
            return
        
        # Archive tier 2 memories
        self._archive_tier2_memories()
        
        # Archive tier 3 memories
        self._archive_tier3_memories()
        
        # Archive tier 4 memories
        self._archive_tier4_memories()
        
        # Clear cache since memories were archived
        self._clear_cache()
        
        # Update last archive time
        self.last_archive_time = get_current_time()
    
    def _archive_tier2_memories(self):
        """Archive low-weight memories in tier 2."""
        memories = self.tier2_storage.retrieve_memories()
        for memory in memories:
            weight = self._calculate_memory_weight(memory)
            if weight < self.min_weight:
                self.tier2_storage.delete_memory(memory.get('id'))
    
    def _archive_tier3_memories(self):
        """Archive low-weight memories in tier 3."""
        memories = self.tier3_storage.retrieve_memories()
        for memory in memories:
            weight = self._calculate_memory_weight(memory)
            if weight < self.min_weight:
                self.tier3_storage.delete_memory(memory.get('id'))
    
    def _archive_tier4_memories(self):
        """Archive low-weight memories in tier 4."""
        memories = self.tier4_storage.retrieve_memories()
        for memory in memories:
            weight = self._calculate_memory_weight(memory)
            if weight < self.min_weight:
                self.tier4_storage.delete_memory(memory.get('id'))
    
    def _calculate_memory_weight(self, memory: Dict[str, Any]) -> float:
        """Calculate memory weight based on confidence, recency, and frequency.
        
        Args:
            memory: The memory to calculate weight for.
            
        Returns:
            The calculated weight.
        """
        from datetime import datetime, timezone
        
        # Get memory properties
        confidence = memory.get('confidence', 1.0)
        last_accessed = memory.get('last_accessed', memory.get('created_at', get_current_time()))
        access_count = memory.get('access_count', 1)
        
        # Calculate days since last access
        try:
            last_accessed_dt = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
            current_dt = datetime.now(timezone.utc)
            days_since_last_access = (current_dt - last_accessed_dt).days
        except:
            days_since_last_access = 30  # Default to 30 days if parsing fails
        
        # Exponential decay for recency
        recency_score = 2 ** (-0.1 * days_since_last_access)
        
        # Logarithmic growth for frequency (边际递减)
        frequency_score = 1 + 0.5 * (access_count ** 0.5)
        
        # Calculate final weight
        weight = confidence * recency_score * frequency_score
        
        return weight
    
    def _check_archive_time(self):
        """Check if it's time to run the archive process."""
        from datetime import datetime, timezone, timedelta
        
        try:
            last_archive_dt = datetime.fromisoformat(self.last_archive_time.replace('Z', '+00:00'))
            current_dt = datetime.now(timezone.utc)
            time_since_last_archive = (current_dt - last_archive_dt).total_seconds()
            
            if time_since_last_archive >= self.archive_interval:
                self._run_archive()
        except Exception as e:
            logger.error(f"Error checking archive time: {e}", exc_info=True)
            # Run archive anyway if there's an error
            self._run_archive()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None if not found or expired.
        """
        from datetime import datetime, timezone
        
        if key not in self.cache:
            return None
        
        cached_item = self.cache[key]
        stored_time = cached_item['timestamp']
        value = cached_item['value']
        
        # Check if cache is expired
        try:
            stored_dt = datetime.fromisoformat(stored_time.replace('Z', '+00:00'))
            current_dt = datetime.now(timezone.utc)
            time_since_stored = (current_dt - stored_dt).total_seconds()
            
            if time_since_stored > self.cache_ttl:
                del self.cache[key]
                return None
            
            return value
        except Exception as e:
            logger.error(f"Error checking cache expiry: {e}", exc_info=True)
            del self.cache[key]
            return None
    
    def _add_to_cache(self, key: str, value: Any):
        """Add value to cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
        """
        # Remove oldest items if cache is full
        if len(self.cache) >= self.cache_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        # Add to cache
        self.cache[key] = {
            'value': value,
            'timestamp': get_current_time()
        }
    
    def _clear_cache(self):
        """Clear all cache."""
        self.cache = {}
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and classify memory.
        
        Args:
            message: The message to process.
            context: Optional context for the message.
            
        Returns:
            A dictionary containing the classification results.
        """
        start_time = time.time()
        
        # Check if it's time to run archive
        self._check_archive_time()
        
        # Step 1: Add message to working memory
        self._add_to_working_memory(message)
        
        # Step 2: Get or create tenant
        tenant_id = context.get('tenant_id') if context else None
        tenant = None
        
        if tenant_id:
            tenant = self.tenant_manager.get_tenant(tenant_id)
        
        if not tenant:
            # Create default tenant if not provided
            tenant_id = tenant_id or 'default'
            tenant = self.tenant_manager.create_tenant(
                tenant_id,
                f"Default Tenant {tenant_id}",
                'personal',
                user_id=tenant_id
            )
        
        # Step 3: Process message through plugins
        plugin_results = self.plugin_manager.process_message(message, context)
        
        # Step 4: Apply layers in order
        # Layer 1: Rule matching
        rule_matches = self.rule_matcher.match(message, context)
        
        # Layer 2: Pattern analysis
        pattern_matches = self.pattern_analyzer.analyze(message, context)
        
        # Layer 3: Semantic classification
        semantic_matches = self.semantic_classifier.classify(message, context)
        
        # Step 5: Combine results
        all_matches = rule_matches + pattern_matches + semantic_matches
        
        # Step 6: Deduplicate and resolve conflicts
        unique_matches = self._deduplicate_matches(all_matches)
        
        # If no matches found, add a default classification
        if not unique_matches:
            default_match = self._get_default_classification(message)
            if default_match:
                unique_matches.append(default_match)
        
        # Step 7: Store memories
        stored_memories = []
        for match in unique_matches:
            # Generate memory ID
            memory_id = generate_memory_id()
            match['id'] = memory_id
            
            # Add context if provided
            if context:
                match['context'] = context.get('conversation_id', '')
            
            # Add tenant information
            match['tenant_id'] = tenant.tenant_id
            
            # Rename memory_type to type for storage compatibility
            if 'memory_type' in match:
                match['type'] = match['memory_type']
            # Also keep memory_type for compatibility with retrieval
            if 'type' in match and 'memory_type' not in match:
                match['memory_type'] = match['type']
            
            # Process memory through plugins
            processed_match = self.plugin_manager.process_memory(match)
            
            # Store based on tier
            if processed_match.get('tier') == 2:
                self.tier2_storage.store_memory(processed_match)
            elif processed_match.get('tier') == 3:
                self.tier3_storage.store_memory(processed_match)
            elif processed_match.get('tier') == 4:
                self.tier4_storage.store_memory(processed_match)
            
            # Add to tenant's memory list
            tenant.add_memory(processed_match)
            
            # Add to distributed sync queue
            if self.distributed_manager:
                sync_item = {
                    'type': 'memory_add',
                    'memory': processed_match,
                    'timestamp': get_current_time()
                }
                self.distributed_manager.add_sync_item(sync_item)
            
            stored_memories.append(processed_match)
        
        # Clear cache since new memories were added
        self._clear_cache()
        
        # Record performance metrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('process_message', duration)
        self.performance_monitor.increment_throughput('messages_processed')
        self.performance_monitor.increment_throughput('memories_stored')
        self.performance_monitor.log_metrics()
        
        return {
            'message': message,
            'matches': stored_memories,
            'plugin_results': plugin_results,
            'working_memory_size': len(self.working_memory),
            'processing_time': duration,
            'tenant_id': tenant.tenant_id
        }
    
    def retrieve_memories(self, query: str = None, limit: int = 5, tenant_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve memories based on query.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            tenant_id: Optional tenant ID to filter memories by tenant.
            
        Returns:
            A list of matching memories.
        """
        start_time = time.time()
        
        # Optimize query
        if query:
            query = PerformanceOptimizer.optimize_query(query)
        
        # Generate cache key
        cache_key = PerformanceOptimizer.cache_key_generator('retrieve', query=query, limit=limit, tenant_id=tenant_id)
        
        # Check if result is in cache
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Retrieve from all tiers
        tier2_memories = self.tier2_storage.retrieve_memories(query, limit)
        tier3_memories = self.tier3_storage.retrieve_memories(query, limit)
        tier4_memories = self.tier4_storage.retrieve_memories(query, limit)
        
        # Combine and filter by tenant if specified
        all_memories = tier2_memories + tier3_memories + tier4_memories
        
        # Filter by tenant if specified
        if tenant_id:
            all_memories = [memory for memory in all_memories if memory.get('tenant_id') == tenant_id]
        
        # Sort by confidence
        all_memories.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Limit the result
        result = all_memories[:limit]
        
        # Store in cache
        self._add_to_cache(cache_key, result)
        
        # Record performance metrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('retrieve_memories', duration)
        self.performance_monitor.increment_throughput('queries_processed')
        self.performance_monitor.log_metrics()
        
        return result
    
    def manage_memory(self, action: str, memory_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage memory (view, edit, delete).
        
        Args:
            action: The action to perform (view, edit, delete).
            memory_id: The ID of the memory to manage.
            data: Optional data for editing.
            
        Returns:
            A dictionary containing the result.
        """
        # Try to find the memory in all tiers
        memory = None
        storage = None
        
        # Check tier 2
        tier2_memories = self.tier2_storage.retrieve_memories()
        for m in tier2_memories:
            if m.get('id') == memory_id:
                memory = m
                storage = self.tier2_storage
                break
        
        # Check tier 3
        if not memory:
            tier3_memories = self.tier3_storage.retrieve_memories()
            for m in tier3_memories:
                if m.get('id') == memory_id:
                    memory = m
                    storage = self.tier3_storage
                    break
        
        # Check tier 4
        if not memory:
            tier4_memories = self.tier4_storage.retrieve_memories()
            for m in tier4_memories:
                if m.get('id') == memory_id:
                    memory = m
                    storage = self.tier4_storage
                    break
        
        if not memory:
            return {'success': False, 'message': 'Memory not found'}
        
        if action == 'view':
            return {'success': True, 'memory': memory}
        
        elif action == 'edit':
            if data and storage:
                success = storage.update_memory(memory_id, data)
                if success:
                    # Get updated memory
                    updated_memory = None
                    if storage == self.tier2_storage:
                        for m in self.tier2_storage.retrieve_memories():
                            if m.get('id') == memory_id:
                                updated_memory = m
                                break
                    elif storage == self.tier3_storage:
                        for m in self.tier3_storage.retrieve_memories():
                            if m.get('id') == memory_id:
                                updated_memory = m
                                break
                    elif storage == self.tier4_storage:
                        for m in self.tier4_storage.retrieve_memories():
                            if m.get('id') == memory_id:
                                updated_memory = m
                                break
                    # Clear cache since memory was updated
                    self._clear_cache()
                    return {'success': True, 'memory': updated_memory}
            return {'success': False, 'message': 'Failed to update memory'}
        
        elif action == 'delete':
            if storage:
                success = storage.delete_memory(memory_id)
                if success:
                    # Clear cache since memory was deleted
                    self._clear_cache()
                return {'success': success, 'message': 'Memory deleted' if success else 'Failed to delete memory'}
        
        return {'success': False, 'message': 'Invalid action'}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the engine.
        
        Returns:
            A dictionary with statistics.
        """
        tier2_stats = self.tier2_storage.get_stats()
        tier3_stats = self.tier3_storage.get_stats()
        tier4_stats = self.tier4_storage.get_stats()
        
        return {
            'working_memory_size': len(self.working_memory),
            'tier2': tier2_stats,
            'tier3': tier3_stats,
            'tier4': tier4_stats,
            'total_memories': (
                tier2_stats.get('total_memories', 0) +
                tier3_stats.get('total_memories', 0) +
                tier4_stats.get('total_relationships', 0)
            )
        }
    
    def export_memories(self, format: str = "json") -> Dict[str, Any]:
        """Export memories.
        
        Args:
            format: Export format (json).
            
        Returns:
            A dictionary containing the exported memories.
        """
        tier2_memories = self.tier2_storage.retrieve_memories(limit=1000)
        tier3_memories = self.tier3_storage.retrieve_memories(limit=1000)
        tier4_memories = self.tier4_storage.retrieve_memories(limit=1000)
        
        if format == "json":
            return {
                'tier2': tier2_memories,
                'tier3': tier3_memories,
                'tier4': tier4_memories
            }
        
        return {'error': 'Unsupported format'}
    
    def import_memories(self, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        """Import memories.
        
        Args:
            data: The data to import.
            format: Import format (json).
            
        Returns:
            A dictionary containing the import result.
        """
        if format != "json":
            return {'error': 'Unsupported format'}
        
        imported_count = 0
        
        # Import tier 2 memories
        for memory in data.get('tier2', []):
            if self.tier2_storage.store_memory(memory):
                imported_count += 1
        
        # Import tier 3 memories
        for memory in data.get('tier3', []):
            if self.tier3_storage.store_memory(memory):
                imported_count += 1
        
        # Import tier 4 memories
        for memory in data.get('tier4', []):
            if self.tier4_storage.store_memory(memory):
                imported_count += 1
        
        # Clear cache since memories were imported
        self._clear_cache()
        
        return {'success': True, 'imported_count': imported_count}
    
    def _add_to_working_memory(self, message: str):
        """Add a message to working memory.
        
        Args:
            message: The message to add.
        """
        self.working_memory.append({
            'message': message,
            'timestamp': get_current_time()
        })
        
        # Limit working memory size
        if len(self.working_memory) > self.max_work_memory_size:
            self.working_memory.pop(0)
    
    def _deduplicate_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate matches.
        
        Args:
            matches: List of matches to deduplicate.
            
        Returns:
            List of unique matches.
        """
        if not self.deduplication_enabled:
            return matches
        
        unique_matches = []
        
        for match in matches:
            content = match.get('content', '').strip()
            memory_type = match.get('memory_type', '')
            source = match.get('source', '')
            is_duplicate = False
            
            for existing_match in unique_matches:
                existing_content = existing_match.get('content', '').strip()
                existing_memory_type = existing_match.get('memory_type', '')
                existing_source = existing_match.get('source', '')
                
                # Only consider duplicates if they have the same memory type
                if memory_type == existing_memory_type:
                    similarity = self._calculate_semantic_similarity(content, existing_content)
                    
                    if similarity > self.similarity_threshold:
                        is_duplicate = True
                        # Check for conflict
                        if self._detect_conflict(match, existing_match):
                            # Resolve conflict
                            resolved_match = self._resolve_conflict(match, existing_match)
                            unique_matches.remove(existing_match)
                            unique_matches.append(resolved_match)
                        else:
                            # Keep the match with higher confidence and better source
                            if self._is_better_match(match, existing_match):
                                unique_matches.remove(existing_match)
                                unique_matches.append(match)
                        break
            
            if not is_duplicate:
                unique_matches.append(match)
        
        return unique_matches
    
    def _is_better_match(self, match1: Dict[str, Any], match2: Dict[str, Any]) -> bool:
        """Determine if match1 is better than match2.
        
        Args:
            match1: First match.
            match2: Second match.
            
        Returns:
            True if match1 is better, False otherwise.
        """
        # 1. Compare confidence scores
        confidence1 = match1.get('confidence', 0)
        confidence2 = match2.get('confidence', 0)
        
        if confidence1 != confidence2:
            return confidence1 > confidence2
        
        # 2. Compare source priority
        source_priority = {
            'rule': 4,      # Rule-based matches are most reliable
            'pattern': 3,    # Pattern-based matches are next
            'semantic': 2,   # Semantic-based matches are less reliable
            'default': 1     # Default matches are least reliable
        }
        
        def get_source_priority(source):
            for key, priority in source_priority.items():
                if key in source:
                    return priority
            return 0
        
        priority1 = get_source_priority(match1.get('source', ''))
        priority2 = get_source_priority(match2.get('source', ''))
        
        if priority1 != priority2:
            return priority1 > priority2
        
        # 3. Compare timestamps (newer is better)
        time1 = match1.get('created_at', '')
        time2 = match2.get('created_at', '')
        
        return time1 > time2
    
    def _detect_conflict(self, memory1: Dict[str, Any], memory2: Dict[str, Any]) -> bool:
        """Detect if two memories conflict.
        
        Args:
            memory1: First memory.
            memory2: Second memory.
            
        Returns:
            True if memories conflict, False otherwise.
        """
        # Check for direct negation in Chinese
        content1 = memory1.get('content', '').lower()
        content2 = memory2.get('content', '').lower()
        
        # Check for direct negation in Chinese
        chinese_negation_words = ['不', '没', '没有', '不是', '不要', '不喜欢', '不想要', '反对', '拒绝', '否定']
        # Check for direct negation in English
        english_negation_words = ['not', 'no', 'don\'t', 'doesn\'t', 'didn\'t', 'won\'t', 'can\'t', 'never', 'against', 'reject', 'deny']
        
        # Check Chinese negation
        for word in chinese_negation_words:
            if word in content1 and word not in content2:
                # Check if the rest of the content is similar
                content1_without_negation = content1.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1_without_negation, content2)
                if similarity > self.similarity_threshold:
                    return True
            elif word in content2 and word not in content1:
                # Check if the rest of the content is similar
                content2_without_negation = content2.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1, content2_without_negation)
                if similarity > self.similarity_threshold:
                    return True
        
        # Check English negation
        for word in english_negation_words:
            if word in content1 and word not in content2:
                # Check if the rest of the content is similar
                content1_without_negation = content1.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1_without_negation, content2)
                if similarity > self.similarity_threshold:
                    return True
            elif word in content2 and word not in content1:
                # Check if the rest of the content is similar
                content2_without_negation = content2.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1, content2_without_negation)
                if similarity > self.similarity_threshold:
                    return True
        
        # Check for opposite sentiment
        if 'sentiment_marker' in memory1.get('memory_type', '') and 'sentiment_marker' in memory2.get('memory_type', ''):
            if '正面' in content1 and '负面' in content2:
                return True
            if '负面' in content1 and '正面' in content2:
                return True
            if 'positive' in content1 and 'negative' in content2:
                return True
            if 'negative' in content1 and 'positive' in content2:
                return True
        
        return False
    
    def _resolve_conflict(self, memory1: Dict[str, Any], memory2: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict between two memories.
        
        Args:
            memory1: First memory.
            memory2: Second memory.
            
        Returns:
            Resolved memory.
        """
        strategy = self.conflict_resolution_strategy
        
        if strategy == 'latest':
            # Use the latest memory
            time1 = memory1.get('created_at', '')
            time2 = memory2.get('created_at', '')
            return memory1 if time1 > time2 else memory2
        elif strategy == 'highest_confidence':
            # Use the memory with highest confidence
            confidence1 = memory1.get('confidence', 0)
            confidence2 = memory2.get('confidence', 0)
            return memory1 if confidence1 > confidence2 else memory2
        elif strategy == 'best_source':
            # Use the memory from the best source
            if self._is_better_match(memory1, memory2):
                return memory1
            else:
                return memory2
        elif strategy == 'merge':
            # Merge both memories with context
            merged_content = f"{memory1.get('content', '')} (conflict resolved: {memory2.get('content', '')})"
            merged_confidence = (memory1.get('confidence', 0) + memory2.get('confidence', 0)) / 2
            return {
                'memory_type': memory1.get('memory_type', memory2.get('memory_type')),
                'tier': max(memory1.get('tier', 3), memory2.get('tier', 3)),
                'content': merged_content,
                'confidence': merged_confidence,
                'source': f"conflict_resolved:{memory1.get('source', '')}:{memory2.get('source', '')}",
                'description': 'Conflict resolved by merging'
            }
        else:
            # Default to latest
            time1 = memory1.get('created_at', '')
            time2 = memory2.get('created_at', '')
            return memory1 if time1 > time2 else memory2
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score between 0 and 1.
        """
        # Simple bag-of-words similarity for now
        # In a real implementation, this would use word embeddings or LLM
        
        # Tokenize texts
        def tokenize(text):
            return set(word.lower() for word in text.split() if word.isalnum())
        
        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)
        
        if not tokens1 and not tokens2:
            return 1.0
        
        # Calculate Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0
    
    def _get_default_classification(self, message: str) -> Optional[Dict[str, Any]]:
        """Get default classification for a message when no other matches are found.
        
        Args:
            message: The message to classify.
            
        Returns:
            A default classification match if found, None otherwise.
        """
        message_lower = message.lower()
        
        # English patterns
        if any(keyword in message_lower for keyword in ["like", "love", "prefer", "enjoy"]):
            return {
                'memory_type': 'user_preference',
                'tier': 2,
                'content': message,
                'confidence': 0.9,
                'source': 'default:preference',
                'description': 'User preference detected'
            }
        elif any(keyword in message_lower for keyword in ["correct", "wrong", "fix"]):
            return {
                'memory_type': 'correction',
                'tier': 3,
                'content': message,
                'confidence': 0.8,
                'source': 'default:correction',
                'description': 'Correction detected'
            }
        elif any(keyword in message_lower for keyword in ["is", "are", "was", "were", "will be"]):
            return {
                'memory_type': 'fact_declaration',
                'tier': 3,
                'content': message,
                'confidence': 0.7,
                'source': 'default:fact',
                'description': 'Fact declaration detected'
            }
        elif any(keyword in message_lower for keyword in ["decide", "decision", "choose"]):
            return {
                'memory_type': 'decision',
                'tier': 2,
                'content': message,
                'confidence': 0.8,
                'source': 'default:decision',
                'description': 'Decision detected'
            }
        elif any(keyword in message_lower for keyword in ["friend", "family", "relationship"]):
            return {
                'memory_type': 'relationship',
                'tier': 3,
                'content': message,
                'confidence': 0.7,
                'source': 'default:relationship',
                'description': 'Relationship information detected'
            }
        elif any(keyword in message_lower for keyword in ["task", "todo", "need to"]):
            return {
                'memory_type': 'task_pattern',
                'tier': 2,
                'content': message,
                'confidence': 0.8,
                'source': 'default:task',
                'description': 'Task pattern detected'
            }
        elif any(keyword in message_lower for keyword in ["happy", "sad", "angry", "excited"]):
            return {
                'memory_type': 'sentiment_marker',
                'tier': 3,
                'content': message,
                'confidence': 0.7,
                'source': 'default:sentiment',
                'description': 'Sentiment detected'
            }
        else:
            # Default to general fact declaration
            return {
                'memory_type': 'fact_declaration',
                'tier': 3,
                'content': message,
                'confidence': 0.5,
                'source': 'default:general',
                'description': 'General fact declaration'
            }
    
    def clear_working_memory(self):
        """Clear working memory."""
        self.working_memory = []
    
    def reload_config(self):
        """Reload configuration."""
        self.config.reload()
        
        # Update storage paths if changed
        tier2_path = self.config.get('storage.tier2_path', './data/tier2')
        tier3_path = self.config.get('storage.tier3_path', './data/tier3')
        tier4_path = self.config.get('storage.tier4_path', './data/tier4')
        
        self.tier2_storage = Tier2Storage(tier2_path)
        self.tier3_storage = Tier3Storage(tier3_path)
        self.tier4_storage = Tier4Storage(tier4_path)
        
        # Update rules
        rules = self.config.get_rules().get('rules', [])
        self.rule_matcher = RuleMatcher(rules)
        
        # Update LLM settings
        llm_enabled = self.config.get('llm.enabled', False)
        api_key = self.config.get('llm.api_key', '')
        self.semantic_classifier = SemanticClassifier(llm_enabled, api_key)
    
    def create_tenant(self, tenant_id: str, name: str, tenant_type: str, **kwargs) -> Dict[str, Any]:
        """Create a new tenant.
        
        Args:
            tenant_id: Unique tenant identifier.
            name: Tenant name.
            tenant_type: Tenant type ('personal' or 'enterprise').
            **kwargs: Additional parameters.
            
        Returns:
            A dictionary containing the created tenant information.
        """
        tenant = self.tenant_manager.create_tenant(tenant_id, name, tenant_type, **kwargs)
        if tenant:
            return {
                'success': True,
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'type': tenant.tenant_type,
                'created_at': tenant.created_at
            }
        else:
            return {'success': False, 'message': 'Failed to create tenant'}
    
    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            A dictionary containing the tenant information.
        """
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if tenant:
            return {
                'success': True,
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'type': tenant.tenant_type,
                'created_at': tenant.created_at,
                'memory_count': len(tenant.memories)
            }
        else:
            return {'success': False, 'message': 'Tenant not found'}
    
    def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants.
        
        Returns:
            A list of tenant information dictionaries.
        """
        tenants = self.tenant_manager.list_tenants()
        return [
            {
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'type': tenant.tenant_type,
                'created_at': tenant.created_at,
                'memory_count': len(tenant.memories)
            }
            for tenant in tenants
        ]
    
    def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Delete a tenant.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            A dictionary containing the result.
        """
        success = self.tenant_manager.delete_tenant(tenant_id)
        return {'success': success, 'message': 'Tenant deleted' if success else 'Failed to delete tenant'}
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update tenant information.
        
        Args:
            tenant_id: Tenant ID.
            updates: Dictionary of updates.
            
        Returns:
            A dictionary containing the updated tenant information.
        """
        tenant = self.tenant_manager.update_tenant(tenant_id, updates)
        if tenant:
            return {
                'success': True,
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'type': tenant.tenant_type,
                'updated_at': tenant.updated_at
            }
        else:
            return {'success': False, 'message': 'Tenant not found'}
    
    def add_tenant_role(self, tenant_id: str, role_name: str, permissions: List[str]) -> Dict[str, Any]:
        """Add a role to an enterprise tenant.
        
        Args:
            tenant_id: Tenant ID.
            role_name: Role name.
            permissions: List of permissions.
            
        Returns:
            A dictionary containing the result.
        """
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return {'success': False, 'message': 'Tenant not found'}
        
        if tenant.tenant_type != 'enterprise':
            return {'success': False, 'message': 'Only enterprise tenants can have roles'}
        
        tenant.add_role(role_name, permissions)
        return {'success': True, 'message': 'Role added successfully'}
    
    def check_tenant_permission(self, tenant_id: str, role_name: str, permission: str) -> Dict[str, Any]:
        """Check if a role has a specific permission.
        
        Args:
            tenant_id: Tenant ID.
            role_name: Role name.
            permission: Permission to check.
            
        Returns:
            A dictionary containing the result.
        """
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return {'success': False, 'message': 'Tenant not found'}
        
        if tenant.tenant_type != 'enterprise':
            return {'success': False, 'message': 'Only enterprise tenants have roles'}
        
        has_permission = tenant.has_permission(role_name, permission)
        return {'success': True, 'has_permission': has_permission}
    
    def get_tenant_memories(self, tenant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories for a specific tenant.
        
        Args:
            tenant_id: Tenant ID.
            limit: Maximum number of memories to return.
            
        Returns:
            A list of memories for the tenant.
        """
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return []
        
        memories = tenant.get_memories()
        return memories[:limit]
