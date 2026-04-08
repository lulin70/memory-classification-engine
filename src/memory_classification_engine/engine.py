"""Refactored Memory Classification Engine with coordinator architecture."""

import os
import time
import threading
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.helpers import generate_memory_id, get_current_time
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.language import language_manager
from memory_classification_engine.utils.performance import PerformanceMonitor
from memory_classification_engine.utils.distributed import DistributedManager
from memory_classification_engine.utils.memory_manager import MemoryManager, SmartCache
from memory_classification_engine.utils.tenant import TenantManager
from memory_classification_engine.plugins import PluginManager
from memory_classification_engine.coordinators.storage_coordinator import StorageCoordinator
from memory_classification_engine.coordinators.classification_pipeline import ClassificationPipeline
from memory_classification_engine.services.deduplication_service import DeduplicationService
from memory_classification_engine.privacy.encryption import encryption_manager
from memory_classification_engine.privacy.access_control import access_control_manager
from memory_classification_engine.privacy.privacy_settings import privacy_manager
from memory_classification_engine.privacy.compliance import compliance_manager
from memory_classification_engine.privacy.audit import audit_manager
from memory_classification_engine.privacy.sensitivity_analyzer import SensitivityAnalyzer
from memory_classification_engine.privacy.visibility_manager import VisibilityManager
from memory_classification_engine.privacy.scenario_validator import ScenarioValidator


class MemoryClassificationEngine:
    """Memory Classification Engine - refactored with coordinator architecture.
    
    This refactored version uses a coordinator pattern to separate concerns:
    - StorageCoordinator: Manages all storage tiers (tier2, tier3, tier4)
    - ClassificationPipeline: Coordinates classification layers
    - DeduplicationService: Handles deduplication and conflict resolution
    - PluginManager: Manages plugins
    - TenantManager: Manages tenants
    """
    
    def __init__(self, config_path: str = None):
        """Initialize the memory classification engine.
        
        Args:
            config_path: Path to the configuration file.
        """
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Initialize core coordinators (separation of concerns)
        self.storage_coordinator = StorageCoordinator(self.config)
        self.classification_pipeline = ClassificationPipeline(self.config)
        self.deduplication_service = DeduplicationService(self.config)
        
        # Initialize plugin manager
        plugins_dir = self.config.get('plugins.dir', None)
        self.plugin_manager = PluginManager(plugins_dir)
        self.plugin_manager.load_plugins()
        plugin_config = self.config.get('plugins', {})
        self.plugin_manager.initialize_plugins(plugin_config)
        
        # Initialize tenant manager
        self.tenant_manager = TenantManager()
        
        # Initialize working memory
        self.working_memory = []
        self.max_work_memory_size = self.config.get('storage.max_work_memory_size', 100)
        
        # Initialize memory management utilities
        self.forgetting_enabled = self.config.get('memory.forgetting.enabled', True)
        self.decay_factor = self.config.get('memory.forgetting.decay_factor', 0.9)
        self.min_weight = self.config.get('memory.forgetting.min_weight', 0.1)
        self.archive_interval = self.config.get('memory.forgetting.archive_interval', 86400)
        
        # Initialize cache
        cache_size = self.config.get('memory.limits.cache', 1000)
        cache_ttl = self.config.get('memory.cache.ttl', 3600)
        self.cache = SmartCache(initial_size=cache_size, ttl=cache_ttl)
        
        # Initialize performance monitor
        perf_enabled = self.config.get('performance.enabled', True)
        log_interval = self.config.get('performance.log_interval', 60)
        self.performance_monitor = PerformanceMonitor(enabled=perf_enabled, log_interval=log_interval)
        self.performance_monitor.start()
        
        # Initialize distributed manager (optional)
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
        
        # Import semantic utility for weight calculation
        from memory_classification_engine.utils.semantic import semantic_utility
        self.semantic_utility = semantic_utility
        
        # Initialize privacy protection modules
        self.encryption_manager = encryption_manager
        self.access_control_manager = access_control_manager
        self.privacy_manager = privacy_manager
        self.compliance_manager = compliance_manager
        self.audit_manager = audit_manager
        
        # Initialize privacy modules for Phase 2
        self.sensitivity_analyzer = SensitivityAnalyzer(self.config)
        self.visibility_manager = VisibilityManager(self.config)
        self.scenario_validator = ScenarioValidator(self.config)
        
        # Initialize forgetting and evolution modules for Phase 4
        from memory_classification_engine.utils.forgetting import ForgettingManager
        from memory_classification_engine.utils.evolution import EvolutionManager
        from memory_classification_engine.utils.intelligent_memory import IntelligentMemoryManager
        
        self.forgetting_manager = ForgettingManager(self.config)
        self.evolution_manager = EvolutionManager(self.config)
        self.intelligent_memory_manager = IntelligentMemoryManager(self.config)
        
        # Run initial archive
        self._run_archive()
    
    def _run_archive(self):
        """Run memory archive process to remove low-weight memories."""
        if not self.forgetting_enabled:
            return
        
        # Use storage coordinator to archive all tiers (eliminates duplicate code)
        self.storage_coordinator.archive_low_weight_memories(self._calculate_memory_weight)
        
        # Clear cache since memories were archived
        self.cache.clear()
        
        # Update last archive time
        self.last_archive_time = get_current_time()
    
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
            self._run_archive()
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and classify memory.
        
        Args:
            message: The message to process.
            context: Optional context for the message.
            
        Returns:
            A dictionary containing the classification results.
        """
        start_time = time.time()
        
        # Quick path: return early if message is empty
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
        
        # Check if it's time to run archive (async to avoid blocking main flow)
        threading.Thread(target=self._check_archive_time).start()
        
        # Step 1: Add message to working memory
        self._add_to_working_memory(message)
        
        # Step 2: Get or create tenant
        tenant_id = context.get('tenant_id') if context else None
        tenant = None
        
        if tenant_id:
            tenant = self.tenant_manager.get_tenant(tenant_id)
        
        if not tenant:
            tenant_id = tenant_id or 'default'
            tenant = self.tenant_manager.create_tenant(
                tenant_id,
                f"Default Tenant {tenant_id}",
                'personal',
                user_id=tenant_id
            )
        
        # Step 3: Detect language
        language, lang_confidence = language_manager.detect_language(message)
        
        # Step 4: Check access control
        user_id = context.get('user_id') if context else tenant_id
        if not self.access_control_manager.check_permission(user_id, 'memory', 'write'):
            self.audit_manager.log(user_id, 'access_denied', 'process_message', {'message': 'Access denied'})
            return {
                'message': message,
                'matches': [],
                'plugin_results': {},
                'working_memory_size': len(self.working_memory),
                'processing_time': time.time() - start_time,
                'tenant_id': tenant.tenant_id,
                'language': language,
                'language_confidence': lang_confidence,
                'error': 'Access denied'
            }
        
        # Step 5: Process message through plugins
        plugin_results = self.plugin_manager.process_message(message, context)
        
        # Step 6: Classify through pipeline (delegated to ClassificationPipeline)
        matches = self.classification_pipeline.classify_with_defaults(message, language, context)
        
        # Step 7: Deduplicate matches (delegated to DeduplicationService)
        unique_matches = self.deduplication_service.deduplicate(matches)
        
        # Step 8: Store memories in batch to reduce I/O operations
        stored_memories = []
        batch_memories = []
        
        for match in unique_matches:
            # Generate memory ID
            memory_id = generate_memory_id()
            match['id'] = memory_id
            
            # Add context if provided
            if context:
                match['context'] = context.get('conversation_id', '')
                # Limit conversation history to reduce memory usage
                conversation_history = context.get('conversation_history', [])
                if len(conversation_history) > 10:
                    match['conversation_history'] = conversation_history[-10:]
                else:
                    match['conversation_history'] = conversation_history
            
            # Add tenant information
            match['tenant_id'] = tenant.tenant_id
            
            # Add language information
            match['language'] = language
            match['language_confidence'] = lang_confidence
            
            # Normalize memory_type field
            if 'memory_type' in match:
                match['type'] = match['memory_type']
            if 'type' in match and 'memory_type' not in match:
                match['memory_type'] = match['type']
            
            # Process memory through plugins
            processed_match = self.plugin_manager.process_memory(match)
            
            # Add creator information
            processed_match['created_by'] = user_id
            
            # Analyze sensitivity
            sensitivity_level = self.sensitivity_analyzer.analyze_memory_sensitivity(processed_match)
            processed_match['sensitivity_level'] = sensitivity_level
            
            # Set visibility (default to private)
            processed_match['visibility'] = 'private'
            
            # Encrypt sensitive data if needed
            if self.encryption_manager.is_sensitive_data(str(processed_match)):
                # 简化处理，暂时不加密，因为需要密钥
                stored_memories.append(processed_match)
                batch_memories.append(processed_match)
            else:
                stored_memories.append(processed_match)
                batch_memories.append(processed_match)
        
        # Store memories in batch (delegated to StorageCoordinator)
        if batch_memories:
            self.storage_coordinator.store_memories_batch(batch_memories)
            
            # Add to tenant's memory list
            for memory in batch_memories:
                tenant.add_memory(memory)
            
            # Add to distributed sync queue
            if self.distributed_manager:
                for memory in batch_memories:
                    sync_item = {
                        'type': 'memory_add',
                        'memory': memory,
                        'timestamp': get_current_time()
                    }
                    self.distributed_manager.add_sync_item(sync_item)
        
        # Build associations (async)
        if stored_memories:
            self._build_associations_async(stored_memories, context)
        
        # Clear cache selectively instead of completely
        if stored_memories:
            # Invalidate only relevant cache keys by clearing the entire cache
            # SmartCache doesn't have a delete method, so we'll clear the cache
            self.cache.clear()
        
        # Run forgetting mechanism (async to avoid blocking main flow)
        if stored_memories:
            threading.Thread(target=self._run_forgetting).start()
        
        # Record performance metrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('process_message', duration)
        self.performance_monitor.increment_throughput('messages_processed')
        # Record memories stored count
        for _ in range(len(stored_memories)):
            self.performance_monitor.increment_throughput('memories_stored')
        
        # Record performance to evolution manager
        self.evolution_manager.record_performance('process_message', duration)
        
        # Log operation
        self.audit_manager.log(user_id, 'success', 'process_message', {
            'message_length': len(message),
            'memories_stored': len(stored_memories),
            'processing_time': duration
        })
        
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
    
    def _build_associations_async(self, memories: List[Dict[str, Any]], context: Optional[Dict[str, Any]]):
        """Build memory associations asynchronously.
        
        Args:
            memories: List of memories to build associations for.
            context: Optional context.
        """
        def build_associations():
            try:
                # Import memory association manager
                from memory_classification_engine.utils.memory_association import memory_association_manager
                
                # Limit the number of memories to process at once
                batch_size = 10
                for i in range(0, len(memories), batch_size):
                    batch_memories = memories[i:i+batch_size]
                    
                    # Get all existing memories to compare against (limited to reduce memory usage)
                    all_memories = []
                    all_memories.extend(self.storage_coordinator.retrieve_memories(limit=50, tier=2))
                    all_memories.extend(self.storage_coordinator.retrieve_memories(limit=100, tier=3))
                    all_memories.extend(self.storage_coordinator.retrieve_memories(limit=50, tier=4))
                    
                    # Build associations for each new memory in batch
                    for memory in batch_memories:
                        memory_association_manager.update_memory_associations(memory, all_memories)
                        
                        # Add context-aware associations based on conversation history
                        if context and 'conversation_history' in context:
                            self._build_context_aware_associations(memory, context['conversation_history'])
            except Exception as e:
                logger.error(f"Error building associations: {e}", exc_info=True)
        
        # Use a daemon thread to avoid blocking
        thread = threading.Thread(target=build_associations)
        thread.daemon = True
        thread.start()
    
    def _build_context_aware_associations(self, memory: Dict[str, Any], conversation_history: List[Dict[str, Any]]):
        """Build context-aware associations based on conversation history.
        
        Args:
            memory: The current memory.
            conversation_history: List of previous messages in the conversation.
        """
        from memory_classification_engine.utils.memory_association import memory_association_manager
        
        if not conversation_history:
            return
        
        # Get memory content
        memory_content = memory.get('content', '')
        if not memory_content:
            return
        
        # Find related memories in the conversation history
        recent_memories = []
        for msg in conversation_history[-10:]:
            msg_content = msg.get('content', '')
            if msg_content:
                temp_memory = {
                    'id': f"temp_{msg.get('id', '')}",
                    'content': msg_content,
                    'memory_type': 'conversation_context',
                    'tier': 3
                }
                recent_memories.append(temp_memory)
        
        # Build associations with recent conversation memories
        if recent_memories:
            memory_association_manager.update_memory_associations(memory, recent_memories, min_similarity=0.5)
        
        # Also check for topic continuity
        self._detect_topic_continuity(memory, conversation_history)
    
    def _detect_topic_continuity(self, memory: Dict[str, Any], conversation_history: List[Dict[str, Any]]):
        """Detect topic continuity between the current memory and conversation history.
        
        Args:
            memory: The current memory.
            conversation_history: List of previous messages in the conversation.
        """
        from memory_classification_engine.utils.memory_association import memory_association_manager
        
        if not conversation_history or len(conversation_history) < 2:
            return
        
        # Get memory content
        memory_content = memory.get('content', '')
        if not memory_content:
            return
        
        # Analyze topic continuity with previous messages
        previous_messages = conversation_history[-5:]
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
            most_recent_msg = previous_messages[-1]
            most_recent_content = most_recent_msg.get('content', '')
            
            if most_recent_content:
                metadata = {
                    'topic_continuity_score': topic_continuity_score,
                    'conversation_context': True,
                    'recency_weighted': True
                }
                
                recent_msg_id = f"topic_{most_recent_msg.get('id', 'recent')}"
                
                memory_association_manager.create_association(
                    memory.get('id'),
                    recent_msg_id,
                    topic_continuity_score,
                    metadata
                )
    
    def _run_forgetting(self):
        """运行遗忘机制"""
        try:
            # 获取所有记忆
            all_memories = []
            for tenant in self.tenant_manager.tenants.values():
                all_memories.extend(tenant.memories)
            
            # 更新记忆权重并检查是否需要遗忘
            updated_memories, forgotten_memories = self.forgetting_manager.batch_update_weights(all_memories)
            
            # 处理遗忘的记忆
            for memory in forgotten_memories:
                logger.info(f"Forgetting memory: {memory.get('id')}")
                # 这里可以添加遗忘逻辑，如从存储中删除或归档
        except Exception as e:
            logger.error(f"Error running forgetting mechanism: {e}")
    
    def process_feedback(self, memory_id, feedback):
        """处理用户反馈"""
        # 查找记忆
        memory = None
        for tenant in self.tenant_manager.tenants.values():
            for m in tenant.memories:
                if m.get('id') == memory_id:
                    memory = m
                    break
            if memory:
                break
        
        if not memory:
            return {'error': 'Memory not found'}
        
        # 处理反馈
        updated_memory = self.evolution_manager.process_feedback(memory, feedback)
        
        # 更新存储
        updates = {k: v for k, v in updated_memory.items() if k != 'id'}
        self.storage_coordinator.update_memory(memory_id, updates)
        
        return {'success': True, 'memory': updated_memory}
    
    def optimize_system(self):
        """优化系统"""
        # 优化记忆权重计算
        all_memories = []
        for tenant in self.tenant_manager.tenants.values():
            all_memories.extend(tenant.memories)
        
        optimized_memories = self.evolution_manager.optimize_weight_calculation(all_memories)
        
        # 批量更新记忆
        for memory in optimized_memories:
            memory_id = memory.get('id')
            if memory_id:
                updates = {k: v for k, v in memory.items() if k != 'id'}
                self.storage_coordinator.update_memory(memory_id, updates)
        
        # 优化系统性能
        self.evolution_manager.optimize_performance()
        
        return {'success': True, 'optimized_count': len(optimized_memories)}
    
    def compress_memories(self, tenant_id):
        """压缩记忆"""
        # 获取租户
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return {'error': 'Tenant not found'}
        
        # 压缩记忆
        compressed_memories = self.intelligent_memory_manager.compress_memories(tenant.memories)
        
        # 更新存储
        for memory in compressed_memories:
            memory_id = memory.get('id')
            if memory_id:
                updates = {k: v for k, v in memory.items() if k != 'id'}
                self.storage_coordinator.update_memory(memory_id, updates)
        
        # 更新租户的记忆列表
        tenant.memories = compressed_memories
        
        return {'success': True, 'compressed_count': len(compressed_memories)}
    
    def retrieve_memories(self, query: str = None, limit: int = 5, tenant_id: str = None, include_associations: bool = False, user_id: str = None, scenario: str = None) -> List[Dict[str, Any]]:
        """Retrieve memories based on query.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            tenant_id: Optional tenant ID to filter memories by tenant.
            include_associations: Whether to include associated memories in the results.
            user_id: Optional user ID for access control.
            scenario: Optional scenario for memory validation.
            
        Returns:
            A list of matching memories sorted by semantic relevance.
        """
        start_time = time.time()
        
        # Check access control
        if not self.access_control_manager.check_permission(user_id or tenant_id, 'memory', 'read'):
            self.audit_manager.log(user_id or tenant_id, 'access_denied', 'retrieve_memories', {'query': query, 'tenant_id': tenant_id})
            return []
        
        # Optimize query
        if query:
            from memory_classification_engine.utils.performance import PerformanceOptimizer
            query = PerformanceOptimizer.optimize_query(query)
        
        # Generate cache key
        from memory_classification_engine.utils.performance import PerformanceOptimizer
        try:
            cache_key = PerformanceOptimizer.cache_key_generator('retrieve', query=query, limit=limit, tenant_id=tenant_id, include_associations=include_associations, user_id=user_id)
        except Exception as e:
            logger.error(f"Cache key generation failed: {e}, query={query}, limit={limit}, tenant_id={tenant_id}")
            cache_key = f"retrieve:query:{query}:limit:{limit}"
        
        # Check if result is in cache
        try:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                # Decrypt cached results if needed
                decrypted_result = []
                for memory in cached_result:
                    if memory.get('is_encrypted'):
                        decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                        if decrypted_memory:
                            decrypted_result.append(decrypted_memory)
                    else:
                        decrypted_result.append(memory)
                return decrypted_result
        except Exception as e:
            logger.warning(f"Cache get failed: {e}, cache_key={cache_key}")
        
        # Retrieve from all tiers (delegated to StorageCoordinator)
        # Use tier-specific retrieval for better performance
        tier2_memories = self.storage_coordinator.retrieve_memories(query, limit // 3, tier=2)
        tier3_memories = self.storage_coordinator.retrieve_memories(query, limit // 3 * 2, tier=3)
        tier4_memories = self.storage_coordinator.retrieve_memories(query, limit // 3, tier=4)
        
        # Combine and deduplicate memories
        all_memories = []
        seen_ids = set()
        for memory in tier2_memories + tier3_memories + tier4_memories:
            memory_id = memory.get('id')
            if memory_id and memory_id not in seen_ids:
                seen_ids.add(memory_id)
                all_memories.append(memory)
        
        # Filter by tenant if specified
        if tenant_id:
            all_memories = [memory for memory in all_memories if memory.get('tenant_id') == tenant_id]
        
        # Filter by visibility
        if user_id:
            all_memories = self.visibility_manager.filter_by_visibility(all_memories, user_id)
        
        # If query is provided, rank by semantic similarity
        if query:
            ranked_memories = []
            for memory in all_memories:
                content = memory.get('content', '')
                if content:
                    # Optimize semantic similarity calculation
                    similarity = self.semantic_utility.calculate_similarity(query, content)
                    memory['semantic_similarity'] = similarity
                    ranked_memories.append(memory)
            
            # Sort by semantic similarity, confidence, and recency
            ranked_memories.sort(key=lambda x: (x.get('semantic_similarity', 0), x.get('confidence', 0), x.get('last_accessed', ''), x.get('created_at', '')), reverse=True)
            all_memories = ranked_memories
        else:
            # No query, sort by confidence, recency, and tier priority
            all_memories.sort(key=lambda x: (x.get('confidence', 0), x.get('last_accessed', ''), x.get('created_at', ''), x.get('tier', 0)), reverse=True)
        
        # Get top results
        top_memories = all_memories[:limit]
        
        # Include associated memories if requested
        if include_associations and top_memories:
            from memory_classification_engine.utils.memory_association import memory_association_manager
            
            associated_memories = []
            for memory in top_memories:
                memory_id = memory.get('id')
                if memory_id:
                    associations = memory_association_manager.get_associations(memory_id, min_similarity=0.6, limit=3)
                    for assoc in associations:
                        # Use storage coordinator to get associated memory
                        assoc_memory = self.storage_coordinator.get_memory(assoc['target_id'])
                        if assoc_memory and assoc_memory.get('id') not in seen_ids:
                            seen_ids.add(assoc_memory['id'])
                            assoc_memory['association_score'] = assoc['similarity']
                            associated_memories.append(assoc_memory)
            
            # Combine and sort results
            result = top_memories + associated_memories[:limit // 2]
            # Sort by semantic similarity or association score
            result.sort(key=lambda x: (x.get('semantic_similarity', x.get('association_score', 0)), x.get('confidence', 0)), reverse=True)
            result = result[:limit]
        else:
            result = top_memories
        
        # Store in cache
        try:
            self.cache.set(cache_key, result)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}, cache_key type: {type(cache_key)}")
        
        # Record user behavior for recommendation
        if tenant_id:
            from memory_classification_engine.utils.recommendation import recommendation_system
            for memory in result:
                memory_id = memory.get('id')
                if memory_id:
                    recommendation_system.record_user_behavior(
                        user_id=tenant_id,
                        memory_id=memory_id,
                        action='view',
                        context={'query': query, 'retrieval_time': get_current_time()}
                    )
        
        # Decrypt memories if needed
        decrypted_result = []
        for memory in result:
            if memory.get('is_encrypted'):
                decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                if decrypted_memory:
                    decrypted_result.append(decrypted_memory)
            else:
                decrypted_result.append(memory)
        result = decrypted_result
        
        # Validate scenario
        if scenario:
            result = self.scenario_validator.validate_scenario(result, scenario)
        
        # Store in cache
        try:
            self.cache.set(cache_key, result)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}, cache_key type: {type(cache_key)}")
        
        # Record performance metrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('retrieve_memories', duration)
        self.performance_monitor.increment_throughput('queries_processed')
        self.performance_monitor.log_metrics()
        
        # Log operation
        self.audit_manager.log(user_id or tenant_id, 'success', 'retrieve_memories', {
            'query': query,
            'limit': limit,
            'tenant_id': tenant_id,
            'results_count': len(result),
            'processing_time': duration
        })
        
        return result
    
    def manage_memory(self, action: str, memory_id: str, data: Optional[Dict[str, Any]] = None, user_id: str = None) -> Dict[str, Any]:
        """Manage memory (view, edit, delete).
        
        Args:
            action: The action to perform (view, edit, delete).
            memory_id: The ID of the memory to manage.
            data: Optional data for editing.
            user_id: Optional user ID for access control.
            
        Returns:
            A dictionary containing the result.
        """
        # Check access control
        if action == 'view':
            if not self.access_control_manager.check_permission(user_id, 'memory', 'read'):
                self.audit_manager.log(user_id, 'access_denied', 'manage_memory', {'action': action, 'memory_id': memory_id})
                return {'success': False, 'message': 'Access denied'}
        elif action == 'edit':
            if not self.access_control_manager.check_permission(user_id, 'memory', 'write'):
                self.audit_manager.log(user_id, 'access_denied', 'manage_memory', {'action': action, 'memory_id': memory_id})
                return {'success': False, 'message': 'Access denied'}
        elif action == 'delete':
            if not self.access_control_manager.check_permission(user_id, 'memory', 'delete'):
                self.audit_manager.log(user_id, 'access_denied', 'manage_memory', {'action': action, 'memory_id': memory_id})
                return {'success': False, 'message': 'Access denied'}
        
        # Try to find the memory (delegated to StorageCoordinator)
        memory = self.storage_coordinator.get_memory(memory_id)
        
        if not memory:
            self.audit_manager.log(user_id, 'not_found', 'manage_memory', {'action': action, 'memory_id': memory_id})
            return {'success': False, 'message': 'Memory not found'}
        
        if action == 'view':
            # Decrypt memory if needed
            if memory.get('is_encrypted'):
                decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                if decrypted_memory:
                    self.audit_manager.log(user_id, 'view', 'manage_memory', {'memory_id': memory_id})
                    return {'success': True, 'memory': decrypted_memory}
                else:
                    self.audit_manager.log(user_id, 'decrypt_failed', 'manage_memory', {'memory_id': memory_id})
                    return {'success': False, 'message': 'Failed to decrypt memory'}
            else:
                self.audit_manager.log(user_id, 'view', 'manage_memory', {'memory_id': memory_id})
                return {'success': True, 'memory': memory}
        
        elif action == 'edit':
            if data:
                # Encrypt sensitive data if needed
                if self.encryption_manager.is_sensitive_data(str(data)):
                    # 简化处理，暂时不加密，因为需要密钥
                    success = self.storage_coordinator.update_memory(memory_id, data)
                else:
                    success = self.storage_coordinator.update_memory(memory_id, data)
                
                if success:
                    self.cache.clear()
                    updated_memory = self.storage_coordinator.get_memory(memory_id)
                    # Decrypt updated memory if needed
                    if updated_memory.get('is_encrypted'):
                        decrypted_updated_memory = self.encryption_manager.decrypt_memory(updated_memory, user_id)
                        if decrypted_updated_memory:
                            updated_memory = decrypted_updated_memory
                    self.audit_manager.log(user_id, 'edit', 'manage_memory', {'memory_id': memory_id, 'changes': list(data.keys())})
                    return {'success': True, 'memory': updated_memory}
            self.audit_manager.log(user_id, 'edit_failed', 'manage_memory', {'memory_id': memory_id})
            return {'success': False, 'message': 'Failed to update memory'}
        
        elif action == 'delete':
            success = self.storage_coordinator.delete_memory(memory_id)
            if success:
                self.cache.clear()
            self.audit_manager.log(user_id, 'delete', 'manage_memory', {'memory_id': memory_id, 'success': success})
            return {'success': success, 'message': 'Memory deleted' if success else 'Failed to delete memory'}
        
        self.audit_manager.log(user_id, 'invalid_action', 'manage_memory', {'action': action, 'memory_id': memory_id})
        return {'success': False, 'message': 'Invalid action'}
    
    def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics about the engine.
        
        Args:
            user_id: Optional user ID for access control.
            
        Returns:
            A dictionary with statistics.
        """
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'user', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'get_stats', {})
            return {'error': 'Access denied'}
        
        storage_stats = self.storage_coordinator.get_stats()
        memory_summary = self.memory_manager.get_memory_summary()
        cache_stats = self.cache.get_stats()
        
        stats = {
            'working_memory_size': len(self.working_memory),
            'storage': storage_stats,
            'memory': memory_summary,
            'cache': cache_stats
        }
        
        self.audit_manager.log(user_id, 'success', 'get_stats', {})
        
        return stats
    
    def export_memories(self, format: str = "json", user_id: str = None) -> Dict[str, Any]:
        """Export memories.
        
        Args:
            format: Export format (json).
            user_id: Optional user ID for access control.
            
        Returns:
            A dictionary containing the exported memories.
        """
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'export_memories', {'format': format})
            return {'error': 'Access denied'}
        
        if format == "json":
            # Retrieve memories
            tier2_memories = self.storage_coordinator.retrieve_memories(tier=2, limit=1000)
            tier3_memories = self.storage_coordinator.retrieve_memories(tier=3, limit=1000)
            tier4_memories = self.storage_coordinator.retrieve_memories(tier=4, limit=1000)
            
            # Decrypt memories if needed
            decrypted_tier2 = []
            for memory in tier2_memories:
                if memory.get('is_encrypted'):
                    decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                    if decrypted_memory:
                        decrypted_tier2.append(decrypted_memory)
                else:
                    decrypted_tier2.append(memory)
            
            decrypted_tier3 = []
            for memory in tier3_memories:
                if memory.get('is_encrypted'):
                    decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                    if decrypted_memory:
                        decrypted_tier3.append(decrypted_memory)
                else:
                    decrypted_tier3.append(memory)
            
            decrypted_tier4 = []
            for memory in tier4_memories:
                if memory.get('is_encrypted'):
                    decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                    if decrypted_memory:
                        decrypted_tier4.append(decrypted_memory)
                else:
                    decrypted_tier4.append(memory)
            
            self.audit_manager.log(user_id, 'success', 'export_memories', {
                'format': format,
                'tier2_count': len(decrypted_tier2),
                'tier3_count': len(decrypted_tier3),
                'tier4_count': len(decrypted_tier4)
            })
            
            return {
                'tier2': decrypted_tier2,
                'tier3': decrypted_tier3,
                'tier4': decrypted_tier4
            }
        
        self.audit_manager.log(user_id, 'unsupported_format', 'export_memories', {'format': format})
        return {'error': 'Unsupported format'}
    
    def import_memories(self, data: Dict[str, Any], format: str = "json", user_id: str = None) -> Dict[str, Any]:
        """Import memories.
        
        Args:
            data: The data to import.
            format: Import format (json).
            user_id: Optional user ID for access control.
            
        Returns:
            A dictionary containing the import result.
        """
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'write'):
            self.audit_manager.log(user_id, 'access_denied', 'import_memories', {'format': format})
            return {'error': 'Access denied'}
        
        if format != "json":
            self.audit_manager.log(user_id, 'unsupported_format', 'import_memories', {'format': format})
            return {'error': 'Unsupported format'}
        
        imported_count = 0
        
        # Import tier 2 memories
        for memory in data.get('tier2', []):
            # Encrypt sensitive data if needed
            if self.encryption_manager.is_sensitive_data(str(memory)):
                # 简化处理，暂时不加密，因为需要密钥
                if self.storage_coordinator.store_memory(memory):
                    imported_count += 1
            else:
                if self.storage_coordinator.store_memory(memory):
                    imported_count += 1
        
        # Import tier 3 memories
        for memory in data.get('tier3', []):
            # Encrypt sensitive data if needed
            if self.encryption_manager.is_sensitive_data(str(memory)):
                # 简化处理，暂时不加密，因为需要密钥
                if self.storage_coordinator.store_memory(memory):
                    imported_count += 1
            else:
                if self.storage_coordinator.store_memory(memory):
                    imported_count += 1
        
        # Import tier 4 memories
        for memory in data.get('tier4', []):
            # Encrypt sensitive data if needed
            if self.encryption_manager.is_sensitive_data(str(memory)):
                # 简化处理，暂时不加密，因为需要密钥
                if self.storage_coordinator.store_memory(memory):
                    imported_count += 1
            else:
                if self.storage_coordinator.store_memory(memory):
                    imported_count += 1
        
        # Clear cache since memories were imported
        self.cache.clear()
        
        self.audit_manager.log(user_id, 'success', 'import_memories', {
            'format': format,
            'imported_count': imported_count
        })
        
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
    
    def clear_working_memory(self):
        """Clear working memory."""
        self.working_memory = []
    
    def reload_config(self, user_id: str = None):
        """Reload configuration.
        
        Args:
            user_id: Optional user ID for access control.
        """
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'user', 'write'):
            self.audit_manager.log(user_id, 'access_denied', 'reload_config', {})
            return {'error': 'Access denied'}
        
        self.config.reload()
        
        # Reload coordinators
        self.storage_coordinator = StorageCoordinator(self.config)
        self.classification_pipeline = ClassificationPipeline(self.config)
        self.deduplication_service = DeduplicationService(self.config)
        
        # Update memory manager
        self.memory_manager = MemoryManager(self.config)
        self.memory_manager.start()
        
        self.audit_manager.log(user_id, 'success', 'reload_config', {})
        
        return {'success': True, 'message': 'Configuration reloaded'}
    
    # Tenant management methods (delegated to TenantManager)
    def create_tenant(self, tenant_id: str, name: str, tenant_type: str, user_id: str = None, **kwargs) -> Dict[str, Any]:
        """Create a new tenant."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'user', 'write'):
            self.audit_manager.log(user_id, 'access_denied', 'create_tenant', {'tenant_id': tenant_id, 'tenant_type': tenant_type})
            return {'success': False, 'message': 'Access denied'}
        
        tenant = self.tenant_manager.create_tenant(tenant_id, name, tenant_type, **kwargs)
        if tenant:
            self.audit_manager.log(user_id, 'success', 'create_tenant', {'tenant_id': tenant_id, 'tenant_type': tenant_type})
            return {
                'success': True,
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'type': tenant.tenant_type,
                'created_at': tenant.created_at
            }
        else:
            self.audit_manager.log(user_id, 'failed', 'create_tenant', {'tenant_id': tenant_id, 'tenant_type': tenant_type})
            return {'success': False, 'message': 'Failed to create tenant'}
    
    def get_tenant(self, tenant_id: str, user_id: str = None) -> Dict[str, Any]:
        """Get tenant information."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'user', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'get_tenant', {'tenant_id': tenant_id})
            return {'success': False, 'message': 'Access denied'}
        
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if tenant:
            self.audit_manager.log(user_id, 'success', 'get_tenant', {'tenant_id': tenant_id})
            return {
                'success': True,
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'type': tenant.tenant_type,
                'created_at': tenant.created_at,
                'memory_count': len(tenant.memories)
            }
        else:
            self.audit_manager.log(user_id, 'not_found', 'get_tenant', {'tenant_id': tenant_id})
            return {'success': False, 'message': 'Tenant not found'}
    
    def list_tenants(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List all tenants."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'user', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'list_tenants', {})
            return []
        
        tenants = self.tenant_manager.list_tenants()
        self.audit_manager.log(user_id, 'success', 'list_tenants', {'tenant_count': len(tenants)})
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
    
    def delete_tenant(self, tenant_id: str, user_id: str = None) -> Dict[str, Any]:
        """Delete a tenant."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'user', 'delete'):
            self.audit_manager.log(user_id, 'access_denied', 'delete_tenant', {'tenant_id': tenant_id})
            return {'success': False, 'message': 'Access denied'}
        
        success = self.tenant_manager.delete_tenant(tenant_id)
        self.audit_manager.log(user_id, 'success' if success else 'failed', 'delete_tenant', {'tenant_id': tenant_id, 'success': success})
        return {'success': success, 'message': 'Tenant deleted' if success else 'Failed to delete tenant'}
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Update tenant information."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'user', 'write'):
            self.audit_manager.log(user_id, 'access_denied', 'update_tenant', {'tenant_id': tenant_id})
            return {'success': False, 'message': 'Access denied'}
        
        tenant = self.tenant_manager.update_tenant(tenant_id, updates)
        if tenant:
            self.audit_manager.log(user_id, 'success', 'update_tenant', {'tenant_id': tenant_id, 'changes': list(updates.keys())})
            return {
                'success': True,
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'type': tenant.tenant_type,
                'updated_at': tenant.updated_at
            }
        else:
            self.audit_manager.log(user_id, 'not_found', 'update_tenant', {'tenant_id': tenant_id})
            return {'success': False, 'message': 'Tenant not found'}
    
    def get_tenant_memories(self, tenant_id: str, limit: int = 10, user_id: str = None) -> List[Dict[str, Any]]:
        """Get memories for a specific tenant."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'get_tenant_memories', {'tenant_id': tenant_id})
            return []
        
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            self.audit_manager.log(user_id, 'not_found', 'get_tenant_memories', {'tenant_id': tenant_id})
            return []
        
        memories = tenant.get_memories()
        # Decrypt memories if needed
        decrypted_memories = []
        for memory in memories:
            if memory.get('is_encrypted'):
                decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                if decrypted_memory:
                    decrypted_memories.append(decrypted_memory)
            else:
                decrypted_memories.append(memory)
        
        self.audit_manager.log(user_id, 'success', 'get_tenant_memories', {'tenant_id': tenant_id, 'memory_count': len(decrypted_memories[:limit])})
        return decrypted_memories[:limit]
    
    def add_tenant_role(self, tenant_id: str, role_name: str, permissions: List[str], user_id: str = None) -> Dict[str, Any]:
        """Add a role to an enterprise tenant."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'role', 'write'):
            self.audit_manager.log(user_id, 'access_denied', 'add_tenant_role', {'tenant_id': tenant_id, 'role_name': role_name})
            return {'success': False, 'message': 'Access denied'}
        
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            self.audit_manager.log(user_id, 'not_found', 'add_tenant_role', {'tenant_id': tenant_id, 'role_name': role_name})
            return {'success': False, 'message': 'Tenant not found'}
        
        if tenant.tenant_type != 'enterprise':
            self.audit_manager.log(user_id, 'invalid_type', 'add_tenant_role', {'tenant_id': tenant_id, 'tenant_type': tenant.tenant_type})
            return {'success': False, 'message': 'Only enterprise tenants can have roles'}
        
        tenant.add_role(role_name, permissions)
        self.audit_manager.log(user_id, 'success', 'add_tenant_role', {'tenant_id': tenant_id, 'role_name': role_name, 'permission_count': len(permissions)})
        return {'success': True, 'message': 'Role added successfully'}
    
    def check_tenant_permission(self, tenant_id: str, role_name: str, permission: str, user_id: str = None) -> Dict[str, Any]:
        """Check if a role has a specific permission."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'role', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'check_tenant_permission', {'tenant_id': tenant_id, 'role_name': role_name, 'permission': permission})
            return {'success': False, 'message': 'Access denied'}
        
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            self.audit_manager.log(user_id, 'not_found', 'check_tenant_permission', {'tenant_id': tenant_id, 'role_name': role_name, 'permission': permission})
            return {'success': False, 'message': 'Tenant not found'}
        
        if tenant.tenant_type != 'enterprise':
            self.audit_manager.log(user_id, 'invalid_type', 'check_tenant_permission', {'tenant_id': tenant_id, 'tenant_type': tenant.tenant_type})
            return {'success': False, 'message': 'Only enterprise tenants have roles'}
        
        has_permission = tenant.has_permission(role_name, permission)
        self.audit_manager.log(user_id, 'success', 'check_tenant_permission', {'tenant_id': tenant_id, 'role_name': role_name, 'permission': permission, 'has_permission': has_permission})
        return {'success': True, 'has_permission': has_permission}
    
    # Recommendation methods (using recommendation_system directly)
    def get_recommendations(self, user_id: str, query: Optional[str] = None, limit: int = 5, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'get_recommendations', {'query': query, 'tenant_id': tenant_id})
            return []
        
        from memory_classification_engine.utils.recommendation import recommendation_system
        
        start_time = time.time()
        
        # Retrieve all memories
        all_memories = self.storage_coordinator.retrieve_memories(limit=300)
        
        # Filter by tenant if specified
        if tenant_id:
            all_memories = [memory for memory in all_memories if memory.get('tenant_id') == tenant_id]
        
        # Decrypt memories if needed
        decrypted_memories = []
        for memory in all_memories:
            if memory.get('is_encrypted'):
                decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                if decrypted_memory:
                    decrypted_memories.append(decrypted_memory)
            else:
                decrypted_memories.append(memory)
        
        # Generate recommendations
        recommendations = recommendation_system.generate_recommendations(
            user_id=user_id,
            query=query,
            limit=limit,
            all_memories=decrypted_memories
        )
        
        # Record performance metrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('get_recommendations', duration)
        self.performance_monitor.increment_throughput('recommendations_generated')
        
        # Log operation
        self.audit_manager.log(user_id, 'success', 'get_recommendations', {
            'query': query,
            'limit': limit,
            'tenant_id': tenant_id,
            'recommendation_count': len(recommendations),
            'processing_time': duration
        })
        
        return recommendations
    
    def record_user_behavior(self, user_id: str, memory_id: str, action: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record user behavior for recommendation."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'write'):
            self.audit_manager.log(user_id, 'access_denied', 'record_user_behavior', {'memory_id': memory_id, 'action': action})
            return {'success': False, 'message': 'Access denied'}
        
        from memory_classification_engine.utils.recommendation import recommendation_system
        
        try:
            recommendation_system.record_user_behavior(user_id, memory_id, action, context)
            self.audit_manager.log(user_id, 'success', 'record_user_behavior', {'memory_id': memory_id, 'action': action})
            return {'success': True, 'message': 'User behavior recorded'}
        except Exception as e:
            logger.error(f"Error recording user behavior: {e}", exc_info=True)
            self.audit_manager.log(user_id, 'failed', 'record_user_behavior', {'memory_id': memory_id, 'action': action, 'error': str(e)})
            return {'success': False, 'message': 'Failed to record user behavior'}
    
    def get_user_behavior_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user behavior summary."""
        # Check access control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'get_user_behavior_summary', {})
            return {'error': 'Access denied'}
        
        from memory_classification_engine.utils.recommendation import recommendation_system
        try:
            summary = recommendation_system.get_user_behavior_summary(user_id)
            self.audit_manager.log(user_id, 'success', 'get_user_behavior_summary', {})
            return summary
        except Exception as e:
            logger.error(f"Error getting user behavior summary: {e}", exc_info=True)
            self.audit_manager.log(user_id, 'failed', 'get_user_behavior_summary', {'error': str(e)})
            return {'error': 'Failed to get user behavior summary'}
