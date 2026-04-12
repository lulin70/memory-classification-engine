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
from memory_classification_engine.utils.semantic import semantic_utility
from memory_classification_engine.utils.forgetting import ForgettingManager
from memory_classification_engine.utils.evolution import EvolutionManager
from memory_classification_engine.utils.intelligent_memory import IntelligentMemoryManager
from memory_classification_engine.agents.agent_manager import AgentManager
from memory_classification_engine.knowledge.knowledge_manager import KnowledgeManager
from memory_classification_engine.utils.constants import (
    DEFAULT_WORK_MEMORY_SIZE,
    DEFAULT_DECAY_FACTOR,
    DEFAULT_MIN_WEIGHT,
    DEFAULT_ARCHIVE_INTERVAL,
    DEFAULT_CACHE_SIZE,
    DEFAULT_CACHE_TTL,
    DEFAULT_DISCOVERY_PORT,
    DEFAULT_RECENCY_DECAY_RATE,
    DEFAULT_FREQUENCY_MULTIPLIER,
    DEFAULT_FREQUENCY_EXPONENT,
    DEFAULT_MIN_SIMILARITY,
    DEFAULT_STRONG_ASSOCIATION_THRESHOLD,
    DEFAULT_MEMORY_RETRIEVAL_LIMIT,
    DEFAULT_ASSOCIATION_RETRIEVAL_LIMIT,
    DEFAULT_TOTAL_MEMORY_RETRIEVAL_LIMIT,
    DEFAULT_TIER_MEMORY_RETRIEVAL_LIMIT,
    DEFAULT_TOPIC_CONTINUITY_THRESHOLD,
    DEFAULT_BATCH_SIZE,
    DEFAULT_CONVERSATION_HISTORY_LIMIT,
    ENGINE_VERSION
)
from memory_classification_engine.utils.pending_memories import PendingMemoryManager
from memory_classification_engine.utils.nudge_mechanism import NudgeManager


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
        # Comment in Chinese removedtion
        self.config = ConfigManager(config_path)
        
        # Comment in Chinese removedrns)
        self.storage_coordinator = StorageCoordinator(self.config)
        self.classification_pipeline = ClassificationPipeline(self.config)
        self.deduplication_service = DeduplicationService(self.config)
        
        # Comment in Chinese removedr
        plugins_dir = self.config.get('plugins.dir', None)
        self.plugin_manager = PluginManager(plugins_dir)
        self.plugin_manager.load_plugins()
        plugin_config = self.config.get('plugins', {})
        self.plugin_manager.initialize_plugins(plugin_config)
        
        # Comment in Chinese removedr
        self.tenant_manager = TenantManager()
        
        # Comment in Chinese removedmory
        self.working_memory = []
        self.max_work_memory_size = self.config.get('storage.max_work_memory_size', DEFAULT_WORK_MEMORY_SIZE)
        
        # Comment in Chinese removeds
        self.forgetting_enabled = self.config.get('memory.forgetting.enabled', True)
        self.decay_factor = self.config.get('memory.forgetting.decay_factor', DEFAULT_DECAY_FACTOR)
        self.min_weight = self.config.get('memory.forgetting.min_weight', DEFAULT_MIN_WEIGHT)
        self.archive_interval = self.config.get('memory.forgetting.archive_interval', DEFAULT_ARCHIVE_INTERVAL)

        # Comment in Chinese removed
        cache_size = self.config.get('memory.limits.cache', DEFAULT_CACHE_SIZE)
        cache_ttl = self.config.get('memory.cache.ttl', DEFAULT_CACHE_TTL)
        self.cache = SmartCache(initial_size=cache_size, ttl=cache_ttl)

        # Comment in Chinese removed monitor
        perf_enabled = self.config.get('performance.enabled', True)
        log_interval = self.config.get('performance.log_interval', 60)
        self.performance_monitor = PerformanceMonitor(enabled=perf_enabled, log_interval=log_interval)
        self.performance_monitor.start()

        # Comment in Chinese removedl)
        distributed_enabled = self.config.get('distributed.enabled', False)
        if distributed_enabled:
            node_id = self.config.get('distributed.node_id', None)
            port = self.config.get('distributed.port', DEFAULT_DISCOVERY_PORT)
            discovery_interval = self.config.get('distributed.discovery_interval', 30)
            self.distributed_manager = DistributedManager(node_id, port, discovery_interval)
            self.distributed_manager.start()
        else:
            self.distributed_manager = None
        
        # Comment in Chinese removed
        self.last_archive_time = get_current_time()
        
        # Comment in Chinese removednism
        self.last_nudge_time = time.time()
        self.message_history = []
        
        # Comment in Chinese removedr
        self.memory_manager = MemoryManager(self.config)
        self.memory_manager.start()
        
        # Comment in Chinese removedl)
        self.semantic_utility = semantic_utility
        
        # Comment in Chinese removeds
        self.encryption_manager = encryption_manager
        self.access_control_manager = access_control_manager
        self.privacy_manager = privacy_manager
        self.compliance_manager = compliance_manager
        self.audit_manager = audit_manager
        
        # Comment in Chinese removed
        self.sensitivity_analyzer = SensitivityAnalyzer(self.config)
        self.visibility_manager = VisibilityManager(self.config)
        self.scenario_validator = ScenarioValidator(self.config)
        
        # Comment in Chinese removed
        self.forgetting_manager = ForgettingManager(self.config)
        self.evolution_manager = EvolutionManager(self.config)
        self.intelligent_memory_manager = IntelligentMemoryManager(self.config)
        
        # Comment in Chinese removed
        self._run_archive()
        
        # Comment in Chinese removed
        self.agent_manager = AgentManager(self.config)
        self.knowledge_manager = KnowledgeManager(self.config)
        
        # Initialize pending memory manager
        self.pending_memory_manager = PendingMemoryManager(self.storage_coordinator)
        
        # Initialize nudge mechanism
        self.nudge_manager = NudgeManager(self.storage_coordinator)
    
    def _run_archive(self):
        """Run memory archive process to remove low-weight memories."""
        if not self.forgetting_enabled:
            return
        
        # Comment in Chinese removed)
        self.storage_coordinator.archive_low_weight_memories(self._calculate_memory_weight)
        
        # Comment in Chinese removedd
        self.cache.clear()
        
        # Comment in Chinese removed
        self.last_archive_time = get_current_time()
    
    def _calculate_memory_weight(self, memory: Dict[str, Any]) -> float:
        """Calculate memory weight based on confidence, recency, and frequency.
        
        Args:
            memory: The memory to calculate weight for.
            
        Returns:
            The calculated weight.
        """
        from datetime import datetime, timezone
        
        # Comment in Chinese removeds
        confidence = memory.get('confidence', 1.0)
        last_accessed = memory.get('last_accessed', memory.get('created_at', get_current_time()))
        access_count = memory.get('access_count', 1)
        
        # Comment in Chinese removedss
        try:
            if isinstance(last_accessed, float):
                # Handle timestamp float
                last_accessed_dt = datetime.fromtimestamp(last_accessed, timezone.utc)
            else:
                # Handle ISO string
                last_accessed_dt = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
            current_dt = datetime.now(timezone.utc)
            days_since_last_access = (current_dt - last_accessed_dt).days
        except (ValueError, TypeError):
            days_since_last_access = 30  # Comment in Chinese removedils
        
        # Comment in Chinese removedncy
        recency_score = 2 ** (-DEFAULT_RECENCY_DECAY_RATE * days_since_last_access)

        # Comment in Chinese removedncy (边际递减)
        frequency_score = 1 + DEFAULT_FREQUENCY_MULTIPLIER * (access_count ** DEFAULT_FREQUENCY_EXPONENT)
        
        # Calculate final weight
        weight = confidence * recency_score * frequency_score
        
        return weight
    
    def add_pending_memory(self, memory: Dict[str, Any]) -> str:
        """Add a memory to the pending queue for user confirmation.
        
        Args:
            memory: Memory data to add to pending queue
            
        Returns:
            Memory ID
        """
        return self.pending_memory_manager.add_pending_memory(memory)
    
    def get_pending_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending memories for user review.
        
        Args:
            limit: Maximum number of pending memories to return
            
        Returns:
            List of pending memories
        """
        return self.pending_memory_manager.get_pending_memories(limit)
    
    def approve_memory(self, memory_id: str) -> bool:
        """Approve a pending memory and store it permanently.
        
        Args:
            memory_id: ID of the pending memory to approve
            
        Returns:
            True if successful, False otherwise
        """
        return self.pending_memory_manager.approve_memory(memory_id)
    
    def reject_memory(self, memory_id: str) -> bool:
        """Reject a pending memory and remove it from the queue.
        
        Args:
            memory_id: ID of the pending memory to reject
            
        Returns:
            True if successful, False otherwise
        """
        return self.pending_memory_manager.reject_memory(memory_id)
    
    def get_pending_count(self) -> int:
        """Get the number of pending memories.
        
        Returns:
            Number of pending memories
        """
        return self.pending_memory_manager.get_pending_count()
    
    def get_nudge_candidates(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get memory candidates for nudge based on review frequency and importance.
        
        Args:
            limit: Maximum number of nudge candidates to return
            
        Returns:
            List of memory candidates for review
        """
        return self.nudge_manager.get_nudge_candidates(limit)
    
    def generate_nudge_prompt(self, memory: Dict[str, Any]) -> str:
        """Generate a nudge prompt for a memory review.
        
        Args:
            memory: Memory data
            
        Returns:
            Formatted nudge prompt
        """
        return self.nudge_manager.generate_nudge_prompt(memory)
    
    def record_nudge_interaction(self, memory_id: str, action: str) -> bool:
        """Record a nudge interaction.
        
        Args:
            memory_id: Memory ID
            action: User action (confirm, update, archive, delete)
            
        Returns:
            True if successful, False otherwise
        """
        return self.nudge_manager.record_nudge_interaction(memory_id, action)
    
    def should_nudge(self) -> bool:
        """Determine if a nudge should be sent based on time and conditions.
        
        Returns:
            True if a nudge should be sent, False otherwise
        """
        return self.nudge_manager.should_nudge()
    
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
    
    def _check_nudge_time(self):
        """Check if it's time to run nudge."""
        try:
            # Comment in Chinese removedy
            if len(self.message_history) % 50 == 0 or time.time() - self.last_nudge_time > 86400:
                self._run_nudge()
        except Exception as e:
            logger.error(f"Error checking nudge time: {e}", exc_info=True)
            self._run_nudge()
    
    def _run_nudge(self):
        """Run nudge mechanism to review and validate memories."""
        logger.info("Running nudge mechanism...")
        try:
            # Comment in Chinese removedntly
            recent_memories = self.storage_coordinator.retrieve_memories(query="", limit=50)
            
            # Comment in Chinese removedys
            old_memories = []
            current_time = time.time()
            for memory in recent_memories:
                last_accessed = memory.get('last_accessed', 0)
                if isinstance(last_accessed, str):
                    try:
                        last_accessed = float(last_accessed)
                    except:
                        continue
                
                if current_time - last_accessed > 604800:  # Comment in Chinese removedys
                    old_memories.append(memory)
            
            logger.info(f"Found {len(old_memories)} old memories for review")
            
            # Comment in Chinese removedmory
            for memory in old_memories:
                self._nudge_review_memory(memory)
            
            self.last_nudge_time = time.time()
        except Exception as e:
            logger.error(f"Error running nudge: {e}", exc_info=True)
    
    def _nudge_review_memory(self, memory):
        """Review a memory and determine if it needs validation or adjustment."""
        try:
            memory_type = memory.get('memory_type', '')
            content = memory.get('content', '')
            created_at = memory.get('created_at', 0)
            last_accessed = memory.get('last_accessed', 0)
            
            if isinstance(created_at, str):
                try:
                    created_at = float(created_at)
                except:
                    created_at = 0
            
            if isinstance(last_accessed, str):
                try:
                    last_accessed = float(last_accessed)
                except:
                    last_accessed = 0
            
            current_time = time.time()
            age_days = (current_time - created_at) / 86400
            
            # Comment in Chinese removedd
            if self._is_memory_outdated(memory_type, content, age_days):
                logger.info(f"Nudge: Memory likely outdated - {content[:50]}...")
                # Comment in Chinese removedst
                self._mark_memory_for_review(memory)
            
            # Comment in Chinese removedd)
            if last_accessed == 0 and age_days > 30:
                logger.info(f"Nudge: Low value memory (never accessed) - {content[:50]}...")
                # Comment in Chinese removedrchiving
                self._adjust_memory_weight(memory, 0.5)  # Comment in Chinese removed%
                
        except Exception as e:
            logger.error(f"Error reviewing memory: {e}", exc_info=True)
    
    def _is_memory_outdated(self, memory_type, content, age_days):
        """Determine if a memory is likely outdated."""
        # Comment in Chinese removedd
        if memory_type == 'fact_declaration' and age_days > 90:
            return True
        
        # Comment in Chinese removed
        if memory_type == 'task_pattern' and age_days > 60:
            return True
        
        # Comment in Chinese removednt
        time_keywords = ['今天', '明天', '本周', '本月', '今年', '现在', '当前', '最新',
                       'today', 'tomorrow', 'this week', 'this month', 'this year', 'now', 'current', 'latest']
        
        for keyword in time_keywords:
            if keyword in content.lower():
                return age_days > 7
        
        return False
    
    def _mark_memory_for_review(self, memory):
        """Mark a memory for user review."""
        try:
            memory_id = memory.get('id')
            if memory_id:
                # Comment in Chinese removedmory
                memory['needs_review'] = True
                memory['review_timestamp'] = time.time()
                # Comment in Chinese removed
                self.storage_coordinator.update_memory(memory_id, memory)
                logger.info(f"Marked memory {memory_id} for review")
        except Exception as e:
            logger.error(f"Error marking memory for review: {e}", exc_info=True)
    
    def _adjust_memory_weight(self, memory, factor):
        """Adjust the weight of a memory by a factor."""
        try:
            memory_id = memory.get('id')
            if memory_id:
                current_weight = memory.get('weight', 1.0)
                new_weight = max(0.1, current_weight * factor)  # Comment in Chinese removed
                memory['weight'] = new_weight
                memory['weight_adjusted_at'] = time.time()
                # Comment in Chinese removed
                self.storage_coordinator.update_memory(memory_id, memory)
                logger.info(f"Adjusted memory {memory_id} weight from {current_weight:.2f} to {new_weight:.2f}")
        except Exception as e:
            logger.error(f"Error adjusting memory weight: {e}", exc_info=True)
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None, execution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and classify memory.
        
        Args:
            message: The message to process.
            context: Optional context for the message.
            execution_context: Optional execution context containing feedback signals.
            
        Returns:
            A dictionary containing the classification results.
        """
        start_time = time.time()
        
        # Comment in Chinese removedmpty
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
        
        # Comment in Chinese removedlow)
        threading.Thread(target=self._check_archive_time).start()
        
        # Comment in Chinese removedlow)
        threading.Thread(target=self._check_nudge_time).start()
        
        # Comment in Chinese removedmory
        self._add_to_working_memory(message)
        
        # Comment in Chinese removednt
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
        
        # Comment in Chinese removed
        language, lang_confidence = language_manager.detect_language(message)
        
        # Comment in Chinese removedss control
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
        
        # Comment in Chinese removedgins
        plugin_results = self.plugin_manager.process_message(message, context)
        
        # Comment in Chinese removed)
        matches = self.classification_pipeline.classify_with_defaults(message, language, context, execution_context)
        
        # Comment in Chinese removed)
        unique_matches = self.deduplication_service.deduplicate(matches)
        
        # Comment in Chinese removedtions
        stored_memories = []
        batch_memories = []
        
        for match in unique_matches:
            # Comment in Chinese removed
            memory_id = generate_memory_id()
            match['id'] = memory_id
            
            # Comment in Chinese removedd
            if context:
                match['context'] = context.get('conversation_id', '')
                # Comment in Chinese removed
                conversation_history = context.get('conversation_history', [])
                if len(conversation_history) > DEFAULT_CONVERSATION_HISTORY_LIMIT:
                    match['conversation_history'] = conversation_history[-DEFAULT_CONVERSATION_HISTORY_LIMIT:]
                else:
                    match['conversation_history'] = conversation_history
            
            # Comment in Chinese removedtion
            match['tenant_id'] = tenant.tenant_id
            
            # Comment in Chinese removedtion
            match['language'] = language
            match['language_confidence'] = lang_confidence
            
            # Comment in Chinese removedld
            if 'memory_type' in match:
                match['type'] = match['memory_type']
            if 'type' in match and 'memory_type' not in match:
                match['memory_type'] = match['type']
            
            # Comment in Chinese removedgins
            processed_match = self.plugin_manager.process_memory(match)
            
            # Comment in Chinese removedtion
            processed_match['created_by'] = user_id
            
            # Comment in Chinese removednsitivity
            sensitivity_level = self.sensitivity_analyzer.analyze_memory_sensitivity(processed_match)
            processed_match['sensitivity_level'] = sensitivity_level
            
            # Comment in Chinese removed)
            processed_match['visibility'] = 'private'
            
            # Comment in Chinese removedd
            if self.encryption_manager.is_sensitive_data(str(processed_match)):
                # 简化处理，暂时不加密，因为需要密钥
                stored_memories.append(processed_match)
                batch_memories.append(processed_match)
            else:
                stored_memories.append(processed_match)
                batch_memories.append(processed_match)
        
        # Comment in Chinese removedtor)
        if batch_memories:
            self.storage_coordinator.store_memories_batch(batch_memories)
            
            # Comment in Chinese removedmory list
            for memory in batch_memories:
                tenant.add_memory(memory)
            
            # Comment in Chinese removed
            if self.distributed_manager:
                for memory in batch_memories:
                    sync_item = {
                        'type': 'memory_add',
                        'memory': memory,
                        'timestamp': get_current_time()
                    }
                    self.distributed_manager.add_sync_item(sync_item)
        
        # Comment in Chinese removedsync)
        if stored_memories:
            self._build_associations_async(stored_memories, context)
        
        # Comment in Chinese removedly
        if stored_memories:
            # Comment in Chinese removed
            # Comment in Chinese removed
            self.cache.clear()
        
        # Comment in Chinese removedlow)
        if stored_memories:
            threading.Thread(target=self._run_forgetting).start()
        
        # Comment in Chinese removedtrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('process_message', duration)
        self.performance_monitor.increment_throughput('messages_processed')
        # Comment in Chinese removednt
        for _ in range(len(stored_memories)):
            self.performance_monitor.increment_throughput('memories_stored')
        
        # Comment in Chinese removedr
        self.evolution_manager.record_performance('process_message', duration)
        
        # Comment in Chinese removedtion
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
    
    def process_message_with_agent(self, agent_name: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用Agent处理消息"""
        # Comment in Chinese removednt处理消息
        agent_result = self.agent_manager.process_message(agent_name, message, context)
        
        # 然后使用引擎处理消息
        engine_result = self.process_message(message, context)
        
        # 合并结果
        result = {
            'agent_result': agent_result,
            'engine_result': engine_result
        }
        
        return result
    
    def write_memory_to_knowledge(self, memory_id: str) -> Dict[str, Any]:
        """将记忆写回知识库"""
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
        
        # 写回知识库
        success = self.knowledge_manager.write_memory_to_knowledge(memory)
        
        if success:
            return {'success': True, 'memory_id': memory_id}
        else:
            return {'error': 'Failed to write memory to knowledge base'}
    
    def get_knowledge(self, query: str) -> Dict[str, Any]:
        """获取知识库中的相关知识"""
        knowledge = self.knowledge_manager.get_knowledge(query)
        return {'knowledge': knowledge}
    
    def sync_knowledge_base(self) -> Dict[str, Any]:
        """同步知识库"""
        self.knowledge_manager.sync_knowledge_base()
        return {'success': True}
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return self.knowledge_manager.get_knowledge_statistics()
    
    def register_agent(self, agent_name: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """注册Agent"""
        success = self.agent_manager.register_agent(agent_name, agent_config)
        if success:
            return {'success': True, 'agent_name': agent_name}
        else:
            return {'error': 'Failed to register agent'}
    
    def unregister_agent(self, agent_name: str) -> Dict[str, Any]:
        """注销Agent"""
        success = self.agent_manager.unregister_agent(agent_name)
        if success:
            return {'success': True, 'agent_name': agent_name}
        else:
            return {'error': 'Failed to unregister agent'}
    
    def list_agents(self) -> Dict[str, Any]:
        """列出所有Agent"""
        agents = self.agent_manager.list_agents()
        return {'agents': agents}
    
    def process_with_agent(self, agent_name: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用Agent处理消息"""
        return self.agent_manager.process_message(agent_name, message, context)
    
    def assign_tenant(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """分配租户"""
        try:
            self.access_control_manager.assign_tenant(user_id, tenant_id)
            self.audit_manager.log(user_id, 'success', 'assign_tenant', {'tenant_id': tenant_id})
            return {'success': True, 'tenant_id': tenant_id}
        except Exception as e:
            self.audit_manager.log(user_id, 'error', 'assign_tenant', {'tenant_id': tenant_id, 'error': str(e)})
            return {'error': str(e)}
    
    def get_user_tenant(self, user_id: str) -> Dict[str, Any]:
        """获取用户租户"""
        try:
            tenant_id = self.access_control_manager.get_user_tenant(user_id)
            return {'success': True, 'tenant_id': tenant_id}
        except Exception as e:
            return {'error': str(e)}
    
    def share_memory(self, memory_id: str, user_ids: List[str], permission: str = 'read', user_id: str = None) -> Dict[str, Any]:
        """共享记忆"""
        # 检查权限
        if not self.access_control_manager.check_permission(user_id, 'memory', 'share'):
            self.audit_manager.log(user_id, 'access_denied', 'share_memory', {'memory_id': memory_id})
            return {'error': 'Access denied'}
        
        try:
            self.access_control_manager.share_memory(memory_id, user_ids, permission)
            self.audit_manager.log(user_id, 'success', 'share_memory', {
                'memory_id': memory_id,
                'user_ids': user_ids,
                'permission': permission
            })
            return {'success': True, 'memory_id': memory_id, 'shared_with': user_ids}
        except Exception as e:
            self.audit_manager.log(user_id, 'error', 'share_memory', {
                'memory_id': memory_id,
                'error': str(e)
            })
            return {'error': str(e)}
    
    def unshare_memory(self, memory_id: str, user_id: str, unshare_user_id: str) -> Dict[str, Any]:
        """取消共享记忆"""
        # 检查权限
        if not self.access_control_manager.check_permission(user_id, 'memory', 'share'):
            self.audit_manager.log(user_id, 'access_denied', 'unshare_memory', {'memory_id': memory_id})
            return {'error': 'Access denied'}
        
        try:
            self.access_control_manager.unshare_memory(memory_id, unshare_user_id)
            self.audit_manager.log(user_id, 'success', 'unshare_memory', {
                'memory_id': memory_id,
                'unshare_user_id': unshare_user_id
            })
            return {'success': True, 'memory_id': memory_id, 'unshared_from': unshare_user_id}
        except Exception as e:
            self.audit_manager.log(user_id, 'error', 'unshare_memory', {
                'memory_id': memory_id,
                'error': str(e)
            })
            return {'error': str(e)}
    
    def get_memory_shares(self, memory_id: str, user_id: str) -> Dict[str, Any]:
        """获取记忆共享信息"""
        # 检查权限
        if not self.access_control_manager.check_permission(user_id, 'memory', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'get_memory_shares', {'memory_id': memory_id})
            return {'error': 'Access denied'}
        
        try:
            shares = self.access_control_manager.get_memory_shares(memory_id)
            return {'success': True, 'shares': shares}
        except Exception as e:
            return {'error': str(e)}
    
    def check_memory_access(self, user_id: str, memory_id: str, action: str) -> Dict[str, Any]:
        """检查记忆访问权限"""
        try:
            has_access = self.access_control_manager.check_memory_access(user_id, memory_id, action)
            return {'success': True, 'has_access': has_access}
        except Exception as e:
            return {'error': str(e)}
    
    def _build_associations_async(self, memories: List[Dict[str, Any]], context: Optional[Dict[str, Any]]):
        """Build memory associations asynchronously.
        
        Args:
            memories: List of memories to build associations for.
            context: Optional context.
        """
        def build_associations():
            try:
                # Comment in Chinese removedr
                from memory_classification_engine.utils.memory_association import memory_association_manager

                # Comment in Chinese removed
                batch_size = DEFAULT_BATCH_SIZE
                for i in range(0, len(memories), batch_size):
                    batch_memories = memories[i:i+batch_size]

                    # Comment in Chinese removed)
                    all_memories = []
                    all_memories.extend(self.storage_coordinator.retrieve_memories(limit=DEFAULT_MEMORY_RETRIEVAL_LIMIT//2, tier=2))
                    all_memories.extend(self.storage_coordinator.retrieve_memories(limit=DEFAULT_MEMORY_RETRIEVAL_LIMIT, tier=3))
                    all_memories.extend(self.storage_coordinator.retrieve_memories(limit=DEFAULT_MEMORY_RETRIEVAL_LIMIT//2, tier=4))
                    
                    # Comment in Chinese removedtch
                    for memory in batch_memories:
                        memory_association_manager.update_memory_associations(memory, all_memories)
                        
                        # Comment in Chinese removedtion history
                        if context and 'conversation_history' in context:
                            self._build_context_aware_associations(memory, context['conversation_history'])
            except Exception as e:
                logger.error(f"Error building associations: {e}", exc_info=True)
        
        # Comment in Chinese removedvoid blocking
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
        
        # Comment in Chinese removednt
        memory_content = memory.get('content', '')
        if not memory_content:
            return
        
        # Comment in Chinese removedtion history
        recent_memories = []
        for msg in conversation_history[-DEFAULT_CONVERSATION_HISTORY_LIMIT:]:
            msg_content = msg.get('content', '')
            if msg_content:
                temp_memory = {
                    'id': f"temp_{msg.get('id', '')}",
                    'content': msg_content,
                    'memory_type': 'conversation_context',
                    'tier': 3
                }
                recent_memories.append(temp_memory)

        # Comment in Chinese removeds
        if recent_memories:
            memory_association_manager.update_memory_associations(memory, recent_memories, min_similarity=DEFAULT_MIN_SIMILARITY)
        
        # Comment in Chinese removedity
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
        
        # Comment in Chinese removednt
        memory_content = memory.get('content', '')
        if not memory_content:
            return
        
        # Comment in Chinese removeds
        previous_messages = conversation_history[-5:]
        topic_continuity_score = 0
        
        for i, msg in enumerate(previous_messages):
            msg_content = msg.get('content', '')
            if msg_content:
                # Comment in Chinese removedrity
                similarity = self.semantic_utility.calculate_similarity(memory_content, msg_content)
                # Comment in Chinese removedncy
                weight = (len(previous_messages) - i) / len(previous_messages)
                topic_continuity_score += similarity * weight
        
        # Comment in Chinese removed
        topic_continuity_score /= len(previous_messages)
        
        # Comment in Chinese removedtion
        if topic_continuity_score > DEFAULT_TOPIC_CONTINUITY_THRESHOLD:
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
    
    def manage_forgetting(self, memory_id: str, action: str = 'decrease_weight', weight_adjustment: float = 0.1, tenant_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """Manage memory forgetting process.
        
        Args:
            memory_id: ID of the memory to manage.
            action: Action to perform ('decrease_weight', 'mark_expired', 'delete', 'refresh').
            weight_adjustment: Amount to adjust weight by.
            tenant_id: Optional tenant ID for access control.
            user_id: Optional user ID for access control.
            
        Returns:
            Result of the forgetting operation.
        """
        try:
            # Comment in Chinese removedss control
            if not self.access_control_manager.check_permission(user_id or tenant_id, 'memory', 'update'):
                self.audit_manager.log(user_id or tenant_id, 'access_denied', 'manage_forgetting', {'memory_id': memory_id, 'action': action})
                return {'success': False, 'message': 'Access denied'}
            
            # Comment in Chinese removedrs
            memory = None
            for tier in [2, 3, 4]:
                tier_memories = self.storage_coordinator.retrieve_memories('', limit=100, tier=tier)
                for mem in tier_memories:
                    if mem.get('id') == memory_id:
                        memory = mem
                        break
                if memory:
                    break
            
            if not memory:
                return {'success': False, 'message': f'Memory {memory_id} not found'}
            
            # Comment in Chinese removedction
            if action == 'decrease_weight':
                # Comment in Chinese removedight
                current_weight = memory.get('weight', 0.5)
                new_weight = max(0.1, current_weight - weight_adjustment)
                memory['weight'] = new_weight
                # Comment in Chinese removedmory
                self.storage_coordinator.store_memories_batch([memory])
                return {'success': True, 'message': f'Weight decreased to {new_weight}'}
            
            elif action == 'mark_expired':
                # Comment in Chinese removedd
                memory['status'] = 'expired'
                self.storage_coordinator.store_memories_batch([memory])
                return {'success': True, 'message': 'Memory marked as expired'}
            
            elif action == 'delete':
                # Comment in Chinese removed)
                return {'success': False, 'message': 'Delete action not implemented'}
            
            elif action == 'refresh':
                # Comment in Chinese removedight)
                current_weight = memory.get('weight', 0.5)
                new_weight = min(1.0, current_weight + weight_adjustment)
                memory['weight'] = new_weight
                memory['last_accessed'] = time.time()
                self.storage_coordinator.store_memories_batch([memory])
                return {'success': True, 'message': f'Memory refreshed, weight increased to {new_weight}'}
            
            else:
                return {'success': False, 'message': f'Unknown action: {action}'}
                
        except Exception as e:
            logger.error(f"Error managing forgetting: {e}", exc_info=True)
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def retrieve_memories(self, query: str = None, limit: int = 5, memory_type: str = None, tenant_id: str = None, include_associations: bool = False, user_id: str = None, scenario: str = None) -> List[Dict[str, Any]]:
        """Retrieve memories based on query.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            memory_type: Optional memory type to filter memories.
            tenant_id: Optional tenant ID to filter memories by tenant.
            include_associations: Whether to include associated memories in the results.
            user_id: Optional user ID for access control.
            scenario: Optional scenario for memory validation.
            
        Returns:
            A list of matching memories sorted by semantic relevance.
        """
        start_time = time.time()
        
        # Comment in Chinese removedss control
        if not self.access_control_manager.check_permission(user_id or tenant_id, 'memory', 'read'):
            self.audit_manager.log(user_id or tenant_id, 'access_denied', 'retrieve_memories', {'query': query, 'tenant_id': tenant_id, 'memory_type': memory_type})
            return []
        
        # Comment in Chinese removedry
        if query:
            from memory_classification_engine.utils.performance import PerformanceOptimizer
            query = PerformanceOptimizer.optimize_query(query)
        
        # Comment in Chinese removedy
        from memory_classification_engine.utils.performance import PerformanceOptimizer
        try:
            cache_key = PerformanceOptimizer.cache_key_generator('retrieve', query=query, limit=limit, tenant_id=tenant_id, include_associations=include_associations, user_id=user_id)
        except Exception as e:
            logger.error(f"Cache key generation failed: {e}, query={query}, limit={limit}, tenant_id={tenant_id}")
            cache_key = f"retrieve:query:{query}:limit:{limit}"
        
        # Comment in Chinese removed
        try:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                # Comment in Chinese removedd
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
        
        # Comment in Chinese removedtor)
        # Comment in Chinese removed
        tier2_memories = self.storage_coordinator.retrieve_memories(query, limit // 3, tier=2, memory_type=memory_type)
        tier3_memories = self.storage_coordinator.retrieve_memories(query, limit // 3 * 2, tier=3, memory_type=memory_type)
        tier4_memories = self.storage_coordinator.retrieve_memories(query, limit // 3, tier=4, memory_type=memory_type)
        
        # Comment in Chinese removeds
        all_memories = []
        seen_ids = set()
        for memory in tier2_memories + tier3_memories + tier4_memories:
            memory_id = memory.get('id')
            if memory_id and memory_id not in seen_ids:
                seen_ids.add(memory_id)
                all_memories.append(memory)
        
        # Comment in Chinese removedd
        if tenant_id:
            all_memories = [memory for memory in all_memories if memory.get('tenant_id') == tenant_id]
        
        # Comment in Chinese removedr by visibility
        if user_id:
            all_memories = self.visibility_manager.filter_by_visibility(all_memories, user_id)
        
        # Comment in Chinese removedrity
        if query:
            ranked_memories = []
            for memory in all_memories:
                content = memory.get('content', '')
                if content:
                    # Comment in Chinese removedtion
                    similarity = self.semantic_utility.calculate_similarity(query, content)
                    memory['semantic_similarity'] = similarity
                    ranked_memories.append(memory)
            
            # Comment in Chinese removedncy
            ranked_memories.sort(key=lambda x: (x.get('semantic_similarity', 0), x.get('confidence', 0), x.get('last_accessed', ''), x.get('created_at', '')), reverse=True)
            all_memories = ranked_memories
        else:
            # Comment in Chinese removedr priority
            all_memories.sort(key=lambda x: (x.get('confidence', 0), x.get('last_accessed', ''), x.get('created_at', ''), x.get('tier', 0)), reverse=True)
        
        # Comment in Chinese removedlts
        top_memories = all_memories[:limit]
        
        # Comment in Chinese removedd
        if include_associations and top_memories:
            from memory_classification_engine.utils.memory_association import memory_association_manager
            
            associated_memories = []
            for memory in top_memories:
                memory_id = memory.get('id')
                if memory_id:
                    associations = memory_association_manager.get_associations(memory_id, min_similarity=DEFAULT_STRONG_ASSOCIATION_THRESHOLD, limit=DEFAULT_ASSOCIATION_RETRIEVAL_LIMIT)
                    for assoc in associations:
                        # Comment in Chinese removedmory
                        assoc_memory = self.storage_coordinator.get_memory(assoc['target_id'])
                        if assoc_memory and assoc_memory.get('id') not in seen_ids:
                            seen_ids.add(assoc_memory['id'])
                            assoc_memory['association_score'] = assoc['similarity']
                            associated_memories.append(assoc_memory)
            
            # Comment in Chinese removedlts
            result = top_memories + associated_memories[:limit // 2]
            # Comment in Chinese removed
            result.sort(key=lambda x: (x.get('semantic_similarity', x.get('association_score', 0)), x.get('confidence', 0)), reverse=True)
            result = result[:limit]
        else:
            result = top_memories
        
        # Comment in Chinese removed
        try:
            self.cache.set(cache_key, result)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}, cache_key type: {type(cache_key)}")
        
        # Comment in Chinese removedtion
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
        
        # Comment in Chinese removednt
        from memory_classification_engine.utils.memory_quality import memory_quality_manager
        for memory in result:
            memory_id = memory.get('id')
            if memory_id:
                memory_quality_manager.track_memory_usage(
                    memory_id=memory_id,
                    query=query or '',
                    result=True
                )
        
        # Comment in Chinese removedd
        decrypted_result = []
        for memory in result:
            if memory.get('is_encrypted'):
                decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                if decrypted_memory:
                    decrypted_result.append(decrypted_memory)
            else:
                decrypted_result.append(memory)
        result = decrypted_result
        
        # Comment in Chinese removedrio
        if scenario:
            result = self.scenario_validator.validate_scenario(result, scenario)
        
        # Comment in Chinese removed
        try:
            self.cache.set(cache_key, result)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}, cache_key type: {type(cache_key)}")
        
        # Comment in Chinese removedtrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('retrieve_memories', duration)
        self.performance_monitor.increment_throughput('queries_processed')
        self.performance_monitor.log_metrics()
        
        # Comment in Chinese removedtion
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
        # Comment in Chinese removedss control
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
        
        # Comment in Chinese removedtor)
        memory = self.storage_coordinator.get_memory(memory_id)
        
        if not memory:
            self.audit_manager.log(user_id, 'not_found', 'manage_memory', {'action': action, 'memory_id': memory_id})
            return {'success': False, 'message': 'Memory not found'}
        
        if action == 'view':
            # Comment in Chinese removedd
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
                # Comment in Chinese removedd
                if self.encryption_manager.is_sensitive_data(str(data)):
                    # 简化处理，暂时不加密，因为需要密钥
                    success = self.storage_coordinator.update_memory(memory_id, data)
                else:
                    success = self.storage_coordinator.update_memory(memory_id, data)
                
                if success:
                    self.cache.clear()
                    updated_memory = self.storage_coordinator.get_memory(memory_id)
                    # Comment in Chinese removedd
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
        # Comment in Chinese removedss control
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
    
    def export_memories(self, format: str = "json", user_id: str = None, tenant_id: str = None, memory_types: List[str] = None) -> Dict[str, Any]:
        """Export memories.
        
        Args:
            format: Export format (json).
            user_id: Optional user ID for access control.
            tenant_id: Optional tenant ID to filter memories by tenant.
            memory_types: Optional list of memory types to export.
            
        Returns:
            A dictionary containing the exported memories.
        """
        # Comment in Chinese removedss control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'export_memories', {'format': format})
            return {'error': 'Access denied'}
        
        if format == "json":
            # Comment in Chinese removeds
            tier2_memories = self.storage_coordinator.retrieve_memories(tier=2, limit=DEFAULT_TIER_MEMORY_RETRIEVAL_LIMIT)
            tier3_memories = self.storage_coordinator.retrieve_memories(tier=3, limit=DEFAULT_TIER_MEMORY_RETRIEVAL_LIMIT)
            tier4_memories = self.storage_coordinator.retrieve_memories(tier=4, limit=DEFAULT_TIER_MEMORY_RETRIEVAL_LIMIT)
            
            # Comment in Chinese removeds
            all_memories = tier2_memories + tier3_memories + tier4_memories
            
            # Comment in Chinese removedd
            if tenant_id:
                all_memories = [memory for memory in all_memories if memory.get('tenant_id') == tenant_id]
            
            # Comment in Chinese removedd
            if memory_types:
                all_memories = [memory for memory in all_memories if memory.get('type') in memory_types]
            
            # Comment in Chinese removedd
            decrypted_memories = []
            for memory in all_memories:
                if memory.get('is_encrypted'):
                    decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                    if decrypted_memory:
                        decrypted_memories.append(decrypted_memory)
                else:
                    decrypted_memories.append(memory)
            
            # Comment in Chinese removed
            export_data = {
                "version": "1.0",
                "metadata": {
                    "exported_at": get_current_time(),
                    "exported_by": user_id,
                    "engine_version": ENGINE_VERSION,
                    "total_memories": len(decrypted_memories)
                },
                "memories": decrypted_memories
            }
            
            self.audit_manager.log(user_id, 'success', 'export_memories', {
                'format': format,
                'total_count': len(decrypted_memories),
                'tenant_id': tenant_id,
                'memory_types': memory_types
            })
            
            return export_data
        
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
        # Comment in Chinese removedss control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'write'):
            self.audit_manager.log(user_id, 'access_denied', 'import_memories', {'format': format})
            return {'error': 'Access denied'}
        
        if format != "json":
            self.audit_manager.log(user_id, 'unsupported_format', 'import_memories', {'format': format})
            return {'error': 'Unsupported format'}
        
        # Comment in Chinese removedt
        if 'version' not in data or 'memories' not in data:
            self.audit_manager.log(user_id, 'invalid_format', 'import_memories', {'format': format})
            return {'error': 'Invalid format: missing version or memories field'}
        
        imported_count = 0
        
        # Comment in Chinese removeds
        for memory in data.get('memories', []):
            # Comment in Chinese removedlds
            required_fields = ['id', 'type', 'memory_type', 'content', 'confidence', 'source', 'tier', 'created_at']
            for field in required_fields:
                if field not in memory:
                    continue  # Comment in Chinese removedlds
            
            # Comment in Chinese removedd
            if self.encryption_manager.is_sensitive_data(str(memory)):
                # 简化处理，暂时不加密，因为需要密钥
                if self.storage_coordinator.store_memory(memory):
                    imported_count += 1
            else:
                if self.storage_coordinator.store_memory(memory):
                    imported_count += 1
        
        # Comment in Chinese removedd
        self.cache.clear()
        
        self.audit_manager.log(user_id, 'success', 'import_memories', {
            'format': format,
            'imported_count': imported_count,
            'total_memories': len(data.get('memories', []))
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
        
        # Comment in Chinese removednism
        self.message_history.append({
            'message': message,
            'timestamp': time.time()
        })
        
        # Comment in Chinese removed
        if len(self.working_memory) > self.max_work_memory_size:
            self.working_memory.pop(0)
        
        # Comment in Chinese removed
        if len(self.message_history) > 1000:  # Comment in Chinese removeds
            self.message_history.pop(0)
    
    def clear_working_memory(self):
        """Clear working memory."""
        self.working_memory = []
    
    def reload_config(self, user_id: str = None):
        """Reload configuration.
        
        Args:
            user_id: Optional user ID for access control.
        """
        # Comment in Chinese removedss control
        if not self.access_control_manager.check_permission(user_id, 'user', 'write'):
            self.audit_manager.log(user_id, 'access_denied', 'reload_config', {})
            return {'error': 'Access denied'}
        
        self.config.reload()
        
        # Comment in Chinese removedtors
        self.storage_coordinator = StorageCoordinator(self.config)
        self.classification_pipeline = ClassificationPipeline(self.config)
        self.deduplication_service = DeduplicationService(self.config)
        
        # Comment in Chinese removedr
        self.memory_manager = MemoryManager(self.config)
        self.memory_manager.start()
        
        self.audit_manager.log(user_id, 'success', 'reload_config', {})
        
        return {'success': True, 'message': 'Configuration reloaded'}
    
    # Comment in Chinese removedr)
    def create_tenant(self, tenant_id: str, name: str, tenant_type: str, user_id: str = None, **kwargs) -> Dict[str, Any]:
        """Create a new tenant."""
        # Comment in Chinese removedss control
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
        # Comment in Chinese removedss control
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
        # Comment in Chinese removedss control
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
        # Comment in Chinese removedss control
        if not self.access_control_manager.check_permission(user_id, 'user', 'delete'):
            self.audit_manager.log(user_id, 'access_denied', 'delete_tenant', {'tenant_id': tenant_id})
            return {'success': False, 'message': 'Access denied'}
        
        success = self.tenant_manager.delete_tenant(tenant_id)
        self.audit_manager.log(user_id, 'success' if success else 'failed', 'delete_tenant', {'tenant_id': tenant_id, 'success': success})
        return {'success': success, 'message': 'Tenant deleted' if success else 'Failed to delete tenant'}
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Update tenant information."""
        # Comment in Chinese removedss control
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
        # Comment in Chinese removedss control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'get_tenant_memories', {'tenant_id': tenant_id})
            return []
        
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            self.audit_manager.log(user_id, 'not_found', 'get_tenant_memories', {'tenant_id': tenant_id})
            return []
        
        memories = tenant.get_memories()
        # Comment in Chinese removedd
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
        # Comment in Chinese removedss control
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
        # Comment in Chinese removedss control
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
    
    # Comment in Chinese removedctly)
    def get_recommendations(self, user_id: str, query: Optional[str] = None, limit: int = 5, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user."""
        # Comment in Chinese removedss control
        if not self.access_control_manager.check_permission(user_id, 'memory', 'read'):
            self.audit_manager.log(user_id, 'access_denied', 'get_recommendations', {'query': query, 'tenant_id': tenant_id})
            return []
        
        from memory_classification_engine.utils.recommendation import recommendation_system
        
        start_time = time.time()
        
        # Comment in Chinese removeds
        all_memories = self.storage_coordinator.retrieve_memories(limit=DEFAULT_TOTAL_MEMORY_RETRIEVAL_LIMIT)
        
        # Comment in Chinese removedd
        if tenant_id:
            all_memories = [memory for memory in all_memories if memory.get('tenant_id') == tenant_id]
        
        # Comment in Chinese removedd
        decrypted_memories = []
        for memory in all_memories:
            if memory.get('is_encrypted'):
                decrypted_memory = self.encryption_manager.decrypt_memory(memory, user_id)
                if decrypted_memory:
                    decrypted_memories.append(decrypted_memory)
            else:
                decrypted_memories.append(memory)
        
        # Comment in Chinese removedtions
        recommendations = recommendation_system.generate_recommendations(
            user_id=user_id,
            query=query,
            limit=limit,
            all_memories=decrypted_memories
        )
        
        # Comment in Chinese removedtrics
        duration = time.time() - start_time
        self.performance_monitor.record_response_time('get_recommendations', duration)
        self.performance_monitor.increment_throughput('recommendations_generated')
        
        # Comment in Chinese removedtion
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
        # Comment in Chinese removedss control
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
        # Comment in Chinese removedss control
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
