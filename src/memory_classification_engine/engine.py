import os
import time
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.helpers import generate_memory_id, get_current_time
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.language import language_manager
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
from memory_classification_engine.utils.memory_manager import MemoryManager, SmartCache

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
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(self.config)
        self.memory_manager.start()
        
        # Initialize smart cache
        cache_size = self.config.get('memory.limits.cache', 1000)
        cache_ttl = self.config.get('memory.cache.ttl', 3600)
        self.cache = SmartCache(initial_size=cache_size, ttl=cache_ttl)
        
        # Initialize tenant manager
        self.tenant_manager = TenantManager()
        
        # Initialize semantic utility
        from memory_classification_engine.utils.semantic import semantic_utility
        self.semantic_utility = semantic_utility
        
        # Initialize memory association manager
        from memory_classification_engine.utils.memory_association import memory_association_manager
        self.memory_association_manager = memory_association_manager
        
        # Initialize recommendation system
        from memory_classification_engine.utils.recommendation import recommendation_system
        self.recommendation_system = recommendation_system
        
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
        return self.cache.get(key)
    
    def _add_to_cache(self, key: str, value: Any):
        """Add value to cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
        """
        self.cache.set(key, value)
    
    def _clear_cache(self):
        """Clear all cache."""
        self.cache.clear()
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and classify memory.
        
        Args:
            message: The message to process.
            context: Optional context for the message.
            
        Returns:
            A dictionary containing the classification results.
        """
        start_time = time.time()
        
        # 快速路径：如果消息为空，直接返回
        if not message or not message.strip():
            duration = time.time() - start_time
            return {
                'message': message,
                'matches': [],
                'plugin_results': {},
                'working_memory_size': len(self.working_memory),
                'processing_time': duration,
                'tenant_id': 'default',
                'language': 'unknown',
                'language_confidence': 0.0
            }
        
        # Check if it's time to run archive (异步执行，避免阻塞主流程)
        import threading
        threading.Thread(target=self._check_archive_time).start()
        
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
        
        # Step 3: Detect language
        language, lang_confidence = language_manager.detect_language(message)
        
        # Step 4: Process message through plugins
        plugin_results = self.plugin_manager.process_message(message, context)
        
        # Step 5: Apply layers in order
        # Layer 1: Rule matching (最快，优先执行)
        rule_matches = self.rule_matcher.match(message, context)
        
        # 如果规则匹配成功，直接使用规则匹配结果，跳过后续昂贵的分析
        if rule_matches:
            all_matches = rule_matches
        else:
            # Layer 2: Pattern analysis (次快)
            pattern_matches = self.pattern_analyzer.analyze(message, context)
            
            # 如果模式分析成功，使用模式分析结果
            if pattern_matches:
                all_matches = pattern_matches
            else:
                # Layer 3: Semantic classification (最慢，最后执行)
                semantic_matches = self.semantic_classifier.classify(message, context)
                all_matches = semantic_matches
        
        # Step 6: Deduplicate and resolve conflicts
        unique_matches = self._deduplicate_matches(all_matches)
        
        # If no matches found, add a default classification
        if not unique_matches:
            default_match = self._get_default_classification(message, language)
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
                # Add conversation history for context awareness
                match['conversation_history'] = context.get('conversation_history', [])
            
            # Add tenant information
            match['tenant_id'] = tenant.tenant_id
            
            # Add language information
            match['language'] = language
            match['language_confidence'] = lang_confidence
            
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
        
        # Build associations between newly stored memories (异步执行)
        if stored_memories:
            def build_associations():
                try:
                    # Get all existing memories to compare against
                    all_memories = []
                    all_memories.extend(self.tier2_storage.retrieve_memories(limit=100))  # 限制数量，提高性能
                    all_memories.extend(self.tier3_storage.retrieve_memories(limit=100))
                    all_memories.extend(self.tier4_storage.retrieve_memories(limit=100))
                    
                    # Build associations for each new memory
                    for memory in stored_memories:
                        self.memory_association_manager.update_memory_associations(memory, all_memories)
                        
                        # Add context-aware associations based on conversation history
                        if context and 'conversation_history' in context:
                            self._build_context_aware_associations(memory, context['conversation_history'])
                except Exception as e:
                    logger.error(f"Error building associations: {e}")
            
            threading.Thread(target=build_associations).start()
        
        # Clear cache since new memories were added
        self._clear_cache()
        
        # Record performance metrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('process_message', duration)
        self.performance_monitor.increment_throughput('messages_processed')
        self.performance_monitor.increment_throughput('memories_stored')
        
        return {
            'message': message,
            'matches': stored_memories,
            'plugin_results': plugin_results,
            'working_memory_size': len(self.working_memory),
            'processing_time': duration,
            'tenant_id': tenant.tenant_id,
            'language': language,
            'language_confidence': lang_confidence
        }
    
    def _build_context_aware_associations(self, memory: Dict[str, Any], conversation_history: List[Dict[str, Any]]):
        """Build context-aware associations based on conversation history.
        
        Args:
            memory: The current memory.
            conversation_history: List of previous messages in the conversation.
        """
        if not conversation_history:
            return
        
        # Get memory content
        memory_content = memory.get('content', '')
        if not memory_content:
            return
        
        # Find related memories in the conversation history
        recent_memories = []
        for msg in conversation_history[-10:]:  # Consider last 10 messages
            msg_content = msg.get('content', '')
            if msg_content:
                # Create a temporary memory object for association
                temp_memory = {
                    'id': f"temp_{msg.get('id', '')}",
                    'content': msg_content,
                    'memory_type': 'conversation_context',
                    'tier': 3
                }
                recent_memories.append(temp_memory)
        
        # Build associations with recent conversation memories
        if recent_memories:
            self.memory_association_manager.update_memory_associations(memory, recent_memories, min_similarity=0.5)
        
        # Also check for topic continuity
        self._detect_topic_continuity(memory, conversation_history)
    
    def _detect_topic_continuity(self, memory: Dict[str, Any], conversation_history: List[Dict[str, Any]]):
        """Detect topic continuity between the current memory and conversation history.
        
        Args:
            memory: The current memory.
            conversation_history: List of previous messages in the conversation.
        """
        if not conversation_history or len(conversation_history) < 2:
            return
        
        # Get memory content
        memory_content = memory.get('content', '')
        if not memory_content:
            return
        
        # Analyze topic continuity with previous messages
        previous_messages = conversation_history[-5:]  # Consider last 5 messages
        topic_continuity_score = 0
        
        for i, msg in enumerate(previous_messages):
            msg_content = msg.get('content', '')
            if msg_content:
                # Calculate semantic similarity
                similarity = self.semantic_utility.calculate_similarity(memory_content, msg_content)
                # Weight similarity based on recency
                weight = (len(previous_messages) - i) / len(previous_messages)
                topic_continuity_score += similarity * weight
        
        # Normalize score
        topic_continuity_score /= len(previous_messages)
        
        # If topic continuity is high, add a special association
        if topic_continuity_score > 0.6:
            # Get the most recent message
            most_recent_msg = previous_messages[-1]
            most_recent_content = most_recent_msg.get('content', '')
            
            if most_recent_content:
                # Create a topic continuity association
                metadata = {
                    'topic_continuity_score': topic_continuity_score,
                    'conversation_context': True,
                    'recency_weighted': True
                }
                
                # Create a temporary memory ID for the recent message
                recent_msg_id = f"topic_{most_recent_msg.get('id', 'recent')}"
                
                # Create association
                self.memory_association_manager.create_association(
                    memory.get('id'),
                    recent_msg_id,
                    topic_continuity_score,
                    metadata
                )
    
    def retrieve_memories(self, query: str = None, limit: int = 5, tenant_id: str = None, include_associations: bool = False) -> List[Dict[str, Any]]:
        """Retrieve memories based on query.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            tenant_id: Optional tenant ID to filter memories by tenant.
            include_associations: Whether to include associated memories in the results.
            
        Returns:
            A list of matching memories sorted by semantic relevance.
        """
        start_time = time.time()
        
        # Optimize query
        if query:
            query = PerformanceOptimizer.optimize_query(query)
        
        # Generate cache key
        cache_key = PerformanceOptimizer.cache_key_generator('retrieve', query=query, limit=limit, tenant_id=tenant_id, include_associations=include_associations)
        
        # Check if result is in cache
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Retrieve from all tiers
        tier2_memories = self.tier2_storage.retrieve_memories(query, limit * 2)  # Get more results for semantic ranking
        tier3_memories = self.tier3_storage.retrieve_memories(query, limit * 2)
        tier4_memories = self.tier4_storage.retrieve_memories(query, limit * 2)
        
        # Combine and filter by tenant if specified
        all_memories = tier2_memories + tier3_memories + tier4_memories
        
        # Filter by tenant if specified
        if tenant_id:
            all_memories = [memory for memory in all_memories if memory.get('tenant_id') == tenant_id]
        
        # If query is provided, rank by semantic similarity
        if query:
            # Calculate semantic similarity for each memory
            ranked_memories = []
            for memory in all_memories:
                content = memory.get('content', '')
                if content:
                    similarity = self.semantic_utility.calculate_similarity(query, content)
                    memory['semantic_similarity'] = similarity
                    ranked_memories.append(memory)
            
            # Sort by semantic similarity and then by confidence
            ranked_memories.sort(key=lambda x: (x.get('semantic_similarity', 0), x.get('confidence', 0)), reverse=True)
            all_memories = ranked_memories
        else:
            # No query, sort by confidence and recency
            all_memories.sort(key=lambda x: (x.get('confidence', 0), x.get('last_accessed', ''), x.get('created_at', '')), reverse=True)
        
        # Get top results
        top_memories = all_memories[:limit]
        
        # Include associated memories if requested
        if include_associations and top_memories:
            associated_memories = []
            for memory in top_memories:
                memory_id = memory.get('id')
                if memory_id:
                    # Get associated memories
                    associations = self.memory_association_manager.get_associations(memory_id, min_similarity=0.7, limit=2)
                    for assoc in associations:
                        # Find the actual memory for this association
                        assoc_memory = next((m for m in all_memories if m.get('id') == assoc['target_id']), None)
                        if assoc_memory and assoc_memory not in top_memories and assoc_memory not in associated_memories:
                            assoc_memory['association_score'] = assoc['similarity']
                            associated_memories.append(assoc_memory)
            
            # Add associated memories to the result
            result = top_memories + associated_memories[:limit // 2]  # Add up to half the limit
            # Remove duplicates
            seen_ids = set()
            result = [m for m in result if not (m.get('id') in seen_ids or seen_ids.add(m.get('id')))]
            # Limit to original limit
            result = result[:limit]
        else:
            result = top_memories
        
        # Store in cache
        self._add_to_cache(cache_key, result)
        
        # Record user behavior for recommendation
        if tenant_id:
            for memory in result:
                memory_id = memory.get('id')
                if memory_id:
                    # Record view action
                    self.recommendation_system.record_user_behavior(
                        user_id=tenant_id,
                        memory_id=memory_id,
                        action='view',
                        context={'query': query, 'retrieval_time': get_current_time()}
                    )
        
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
        
        # Get memory management stats
        memory_summary = self.memory_manager.get_memory_summary()
        cache_stats = self.cache.get_stats()
        
        return {
            'working_memory_size': len(self.working_memory),
            'tier2': tier2_stats,
            'tier3': tier3_stats,
            'tier4': tier4_stats,
            'total_memories': (
                tier2_stats.get('total_memories', 0) +
                tier3_stats.get('total_memories', 0) +
                tier4_stats.get('total_relationships', 0)
            ),
            'memory': memory_summary,
            'cache': cache_stats
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
        return self.semantic_utility.calculate_similarity(text1, text2)
    
    def _calculate_bag_of_words_similarity(self, text1: str, text2: str) -> float:
        """Calculate bag-of-words similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score between 0 and 1.
        """
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
    
    def _get_default_classification(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Get default classification for a message when no other matches are found.
        
        Args:
            message: The message to classify.
            language: The detected language code.
            
        Returns:
            A default classification match if found, None otherwise.
        """
        message_lower = message.lower()
        
        # Get language-specific keywords from LanguageManager
        preference_keywords = language_manager.get_keywords('user_preference', language)
        correction_keywords = language_manager.get_keywords('correction', language)
        fact_keywords = language_manager.get_keywords('fact_declaration', language)
        decision_keywords = language_manager.get_keywords('decision', language)
        relationship_keywords = language_manager.get_keywords('relationship', language)
        task_keywords = language_manager.get_keywords('task_pattern', language)
        sentiment_keywords = language_manager.get_keywords('sentiment_marker', language)
        
        # Check for user preferences
        if any(keyword in message_lower for keyword in preference_keywords):
            return {
                'memory_type': 'user_preference',
                'tier': 2,
                'content': message,
                'confidence': 0.9,
                'source': 'default:preference',
                'description': 'User preference detected',
                'language': language
            }
        # Check for corrections
        elif any(keyword in message_lower for keyword in correction_keywords):
            return {
                'memory_type': 'correction',
                'tier': 3,
                'content': message,
                'confidence': 0.8,
                'source': 'default:correction',
                'description': 'Correction detected',
                'language': language
            }
        # Check for fact declarations
        elif any(keyword in message_lower for keyword in fact_keywords):
            return {
                'memory_type': 'fact_declaration',
                'tier': 3,
                'content': message,
                'confidence': 0.7,
                'source': 'default:fact',
                'description': 'Fact declaration detected',
                'language': language
            }
        # Check for decisions
        elif any(keyword in message_lower for keyword in decision_keywords):
            return {
                'memory_type': 'decision',
                'tier': 2,
                'content': message,
                'confidence': 0.8,
                'source': 'default:decision',
                'description': 'Decision detected',
                'language': language
            }
        # Check for relationships
        elif any(keyword in message_lower for keyword in relationship_keywords):
            return {
                'memory_type': 'relationship',
                'tier': 3,
                'content': message,
                'confidence': 0.7,
                'source': 'default:relationship',
                'description': 'Relationship information detected',
                'language': language
            }
        # Check for task patterns
        elif any(keyword in message_lower for keyword in task_keywords):
            return {
                'memory_type': 'task_pattern',
                'tier': 2,
                'content': message,
                'confidence': 0.8,
                'source': 'default:task',
                'description': 'Task pattern detected',
                'language': language
            }
        # Check for sentiment markers
        elif any(keyword in message_lower for keyword in sentiment_keywords):
            return {
                'memory_type': 'sentiment_marker',
                'tier': 3,
                'content': message,
                'confidence': 0.7,
                'source': 'default:sentiment',
                'description': 'Sentiment detected',
                'language': language
            }
        else:
            # Default to general fact declaration
            return {
                'memory_type': 'fact_declaration',
                'tier': 3,
                'content': message,
                'confidence': 0.5,
                'source': 'default:general',
                'description': 'General fact declaration',
                'language': language
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
        
        # Update memory manager
        self.memory_manager = MemoryManager(self.config)
        self.memory_manager.start()
        
        # Update cache settings
        cache_size = self.config.get('memory.limits.cache', 1000)
        self.cache.set_size(cache_size)
    
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
    
    def get_recommendations(self, user_id: str, query: Optional[str] = None, limit: int = 5, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user.
        
        Args:
            user_id: User ID.
            query: Optional query string to filter recommendations.
            limit: Maximum number of recommendations to return.
            tenant_id: Optional tenant ID to filter memories by tenant.
            
        Returns:
            A list of recommended memories sorted by recommendation score.
        """
        start_time = time.time()
        
        # Retrieve all memories
        tier2_memories = self.tier2_storage.retrieve_memories(limit=100)
        tier3_memories = self.tier3_storage.retrieve_memories(limit=100)
        tier4_memories = self.tier4_storage.retrieve_memories(limit=100)
        
        # Combine memories
        all_memories = tier2_memories + tier3_memories + tier4_memories
        
        # Filter by tenant if specified
        if tenant_id:
            all_memories = [memory for memory in all_memories if memory.get('tenant_id') == tenant_id]
        
        # Generate recommendations
        recommendations = self.recommendation_system.generate_recommendations(
            user_id=user_id,
            query=query,
            limit=limit,
            all_memories=all_memories
        )
        
        # Record performance metrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('get_recommendations', duration)
        self.performance_monitor.increment_throughput('recommendations_generated')
        
        return recommendations
    
    def record_user_behavior(self, user_id: str, memory_id: str, action: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record user behavior for recommendation.
        
        Args:
            user_id: User ID.
            memory_id: Memory ID.
            action: Action type (view, interact, like, share).
            context: Optional context information.
            
        Returns:
            A dictionary containing the result.
        """
        try:
            self.recommendation_system.record_user_behavior(user_id, memory_id, action, context)
            return {'success': True, 'message': 'User behavior recorded'}
        except Exception as e:
            logger.error(f"Error recording user behavior: {e}", exc_info=True)
            return {'success': False, 'message': 'Failed to record user behavior'}
    
    def get_user_behavior_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user behavior summary.
        
        Args:
            user_id: User ID.
            
        Returns:
            User behavior summary.
        """
        return self.recommendation_system.get_user_behavior_summary(user_id)
    
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
