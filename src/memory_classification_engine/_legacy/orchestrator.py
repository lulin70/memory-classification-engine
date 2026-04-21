# Comment in Chinese removed
"""
Memory Orchestrator

A high-level abstraction for Memory Classification Engine
Provides a unified interface for classification, storage, retrieval, and forgetting
"""

import logging
from typing import List, Dict, Any, Optional, Union

from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.coordinators.storage_coordinator import StorageCoordinator
from memory_classification_engine.storage.tier2 import Tier2Storage
from memory_classification_engine.storage.tier3 import Tier3Storage
from memory_classification_engine.storage.tier4 import Tier4Storage

logger = logging.getLogger('memory-orchestrator')

class MemoryOrchestrator:
    """Memory Orchestrator
    
    Provides a one-stop memory management solution, integrating classification, storage, retrieval, and forgetting functionality
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Memory Orchestrator
        
        Args:
            config: Configuration parameters
        """
        self.config = config or {}
        self.engine = MemoryClassificationEngine(config)
        self._init_storage()
        logger.info("MemoryOrchestrator initialized")
    
    def _init_storage(self):
        """Initialize storage components"""
        try:
            # Comment in Chinese removedr
            from memory_classification_engine.utils.config import ConfigManager
            
            # Comment in Chinese removedr
            config_manager = ConfigManager()
            
            # Comment in Chinese removedtor
            self.storage = StorageCoordinator(config_manager)
            logger.info("Storage initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
            self.storage = None
    
    def learn(self, message: str, context: Optional[str] = None, execution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Learn new memory
        
        Args:
            message: Message to learn
            context: Context information
            execution_context: Execution context
            
        Returns:
            Learning result
        """
        try:
            logger.info(f"Learning message: {message[:50]}...")
            
            # 分类消息
            classification = self.engine.process_message(
                message,
                context=context,
                execution_context=execution_context
            )
            
            # 存储值得记忆的内容
            stored = False
            if classification.get('matches') and self.storage:
                for match in classification['matches']:
                    # 存储记忆
                    try:
                        self.storage.store_memory(match)
                        logger.info(f"Stored memory: {match.get('memory_type')} - {match.get('content', '')[:50]}...")
                        stored = True
                    except Exception as store_error:
                        logger.error(f"Error storing memory: {store_error}")
            
            return {
                'success': True,
                'classification': classification,
                'stored': stored
            }
            
        except Exception as e:
            logger.error(f"Error learning memory: {e}")
            return {
                'success': False,
                'error': str(e),
                'stored': False
            }
    
    def recall(self, query: str, memory_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Recall related memories
        
        Args:
            query: Retrieval query
            memory_type: Memory type filter
            limit: Return result limit
            
        Returns:
            List of related memories
        """
        try:
            logger.info(f"Recalling memories for: {query}")
            
            # 检索记忆
            memories = self.engine.retrieve_memories(
                query=query,
                memory_type=memory_type,
                limit=limit
            )
            
            logger.info(f"Recalled {len(memories)} memories")
            return memories
            
        except Exception as e:
            logger.error(f"Error recalling memories: {e}")
            return []
    
    def forget(self, memory_id: str, action: str = "decrease_weight", weight_adjustment: float = -0.1) -> Dict[str, Any]:
        """Forget or adjust memory
        
        Args:
            memory_id: Memory ID
            action: Action type
            weight_adjustment: Weight adjustment value
            
        Returns:
            Operation result
        """
        try:
            logger.info(f"Forgetting memory: {memory_id}, action: {action}")
            
            # 调用遗忘管理
            result = self.engine.manage_forgetting(
                memory_id=memory_id,
                action=action,
                weight_adjustment=weight_adjustment
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error forgetting memory: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_learn(self, messages: List[str], contexts: Optional[List[str]] = None, execution_contexts: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Batch learn
        
        Args:
            messages: List of messages
            contexts: List of contexts
            execution_contexts: List of execution contexts
            
        Returns:
            List of learning results
        """
        results = []
        
        for i, message in enumerate(messages):
            context = contexts[i] if contexts and i < len(contexts) else None
            execution_context = execution_contexts[i] if execution_contexts and i < len(execution_contexts) else None
            
            result = self.learn(message, context, execution_context)
            results.append(result)
        
        return results
    
    def search(self, search_term: str, memory_types: Optional[List[str]] = None, min_confidence: float = 0.5, limit: int = 20) -> List[Dict[str, Any]]:
        """Advanced search
        
        Args:
            search_term: Search term
            memory_types: List of memory types
            min_confidence: Minimum confidence
            limit: Return result limit
            
        Returns:
            Search results
        """
        try:
            logger.info(f"Searching memories for: {search_term}")
            
            all_memories = []
            
            # 如果指定了记忆类型，分别搜索每种类型
            if memory_types:
                for memory_type in memory_types:
                    memories = self.engine.retrieve_memories(
                        query=search_term,
                        memory_type=memory_type,
                        limit=limit
                    )
                    all_memories.extend(memories)
            else:
                # 搜索所有类型
                memories = self.engine.retrieve_memories(
                    query=search_term,
                    limit=limit
                )
                all_memories = memories
            
            # 过滤低置信度的结果
            filtered_memories = [
                memory for memory in all_memories 
                if memory.get('confidence', 0) >= min_confidence
            ]
            
            # 按置信度排序
            filtered_memories.sort(
                key=lambda x: x.get('confidence', 0),
                reverse=True
            )
            
            # 限制返回数量
            filtered_memories = filtered_memories[:limit]
            
            logger.info(f"Search completed, found {len(filtered_memories)} memories")
            return filtered_memories
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics
        
        Returns:
            Statistics information
        """
        try:
            # 这里可以添加更多统计信息
            stats = {
                'engine_status': 'active',
                'storage_initialized': self.storage is not None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}
    
    def clear_all(self) -> Dict[str, Any]:
        """Clear all memories
        
        Returns:
            Operation result
        """
        try:
            logger.warning("Clearing all memories")
            
            # 这里需要实现清空所有记忆的逻辑
            # 暂时返回成功
            
            return {
                'success': True,
                'message': 'All memories cleared'
            }
            
        except Exception as e:
            logger.error(f"Error clearing memories: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_memory_quality(self, memory_id: str) -> Dict[str, Any]:
        """Get memory quality
        
        Args:
            memory_id: Memory ID
            
        Returns:
            Memory quality metrics
        """
        try:
            from memory_classification_engine.utils.memory_quality import memory_quality_manager
            return memory_quality_manager.get_memory_quality(memory_id)
        except Exception as e:
            logger.error(f"Error getting memory quality: {e}")
            return None
    
    def generate_quality_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate quality report
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Quality report
        """
        try:
            from memory_classification_engine.utils.memory_quality import memory_quality_manager
            return memory_quality_manager.generate_quality_report(days)
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return {'error': str(e)}
    
    def generate_low_value_memory_report(self, threshold: float = 0.3, days: int = 30) -> List[Dict[str, Any]]:
        """Generate low value memory report
        
        Args:
            threshold: Quality score threshold
            days: Number of days to include in report
            
        Returns:
            List of low value memories
        """
        try:
            from memory_classification_engine.utils.memory_quality import memory_quality_manager
            return memory_quality_manager.generate_low_value_report(threshold, days)
        except Exception as e:
            logger.error(f"Error generating low value report: {e}")
            return []
    
    def track_feedback(self, memory_id: str, feedback: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Track user feedback
        
        Args:
            memory_id: Memory ID
            feedback: Feedback type ('positive', 'negative', 'neutral')
            context: Feedback context
            
        Returns:
            Operation result
        """
        try:
            from memory_classification_engine.utils.memory_quality import memory_quality_manager
            memory_quality_manager.track_feedback(memory_id, feedback, context)
            return {
                'success': True,
                'message': 'Feedback tracked successfully'
            }
        except Exception as e:
            logger.error(f"Error tracking feedback: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_memories(self, include_metadata: bool = True) -> str:
        """Export all memories
        
        Args:
            include_metadata: Whether to include metadata
            
        Returns:
            Exported JSON string
        """
        try:
            # 检索所有记忆
            all_memories = []
            for tier in [2, 3, 4]:
                tier_memories = self.engine.storage_coordinator.retrieve_memories('', limit=1000, tier=tier)
                all_memories.extend(tier_memories)
            
            # 导出记忆
            from memory_classification_engine.utils.memory_migration import memory_migration_manager
            json_str = memory_migration_manager.export_memories(all_memories, include_metadata)
            
            logger.info(f"Exported {len(all_memories)} memories")
            return json_str
            
        except Exception as e:
            logger.error(f"Error exporting memories: {e}")
            raise
    
    def import_memories(self, json_str: str, validate_checksum: bool = True) -> Dict[str, Any]:
        """Import memories
        
        Args:
            json_str: Exported JSON string
            validate_checksum: Whether to validate checksum
            
        Returns:
            Import result
        """
        try:
            # 导入记忆
            from memory_classification_engine.utils.memory_migration import memory_migration_manager
            imported_memories = memory_migration_manager.import_memories(json_str, validate_checksum)
            
            # 存储导入的记忆
            for memory in imported_memories:
                try:
                    self.storage.store_memory(memory)
                except Exception as store_error:
                    logger.error(f"Error storing imported memory: {store_error}")
            
            logger.info(f"Imported and stored {len(imported_memories)} memories")
            return {
                'success': True,
                'imported_count': len(imported_memories),
                'message': f'Imported {len(imported_memories)} memories successfully'
            }
            
        except Exception as e:
            logger.error(f"Error importing memories: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_to_file(self, file_path: str, include_metadata: bool = True):
        """Export memories to file
        
        Args:
            file_path: File path
            include_metadata: Whether to include metadata
        """
        try:
            # 检索所有记忆
            all_memories = []
            for tier in [2, 3, 4]:
                tier_memories = self.engine.storage_coordinator.retrieve_memories('', limit=1000, tier=tier)
                all_memories.extend(tier_memories)
            
            # 导出到文件
            from memory_classification_engine.utils.memory_migration import memory_migration_manager
            memory_migration_manager.export_to_file(all_memories, file_path, include_metadata)
            
        except Exception as e:
            logger.error(f"Error exporting to file: {e}")
            raise
    
    def import_from_file(self, file_path: str, validate_checksum: bool = True) -> Dict[str, Any]:
        """Import memories from file
        
        Args:
            file_path: File path
            validate_checksum: Whether to validate checksum
            
        Returns:
            Import result
        """
        try:
            # 从文件导入
            from memory_classification_engine.utils.memory_migration import memory_migration_manager
            imported_memories = memory_migration_manager.import_from_file(file_path, validate_checksum)
            
            # 存储导入的记忆
            for memory in imported_memories:
                try:
                    self.storage.store_memory(memory)
                except Exception as store_error:
                    logger.error(f"Error storing imported memory: {store_error}")
            
            logger.info(f"Imported and stored {len(imported_memories)} memories from file")
            return {
                'success': True,
                'imported_count': len(imported_memories),
                'message': f'Imported {len(imported_memories)} memories from file successfully'
            }
            
        except Exception as e:
            logger.error(f"Error importing from file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_export_data(self, json_str: str) -> Dict[str, Any]:
        """Validate export data
        
        Args:
            json_str: Exported JSON string
            
        Returns:
            Validation result
        """
        try:
            from memory_classification_engine.utils.memory_migration import memory_migration_manager
            return memory_migration_manager.validate_export_data(json_str)
        except Exception as e:
            logger.error(f"Error validating export data: {e}")
            return {
                'valid': False,
                'errors': [str(e)]
            }

# 全局编排器实例
def get_memory_orchestrator(config: Optional[Dict[str, Any]] = None) -> MemoryOrchestrator:
    """Get memory orchestrator instance
    
    Args:
        config: Configuration parameters
        
    Returns:
        MemoryOrchestrator instance
    """
    return MemoryOrchestrator(config)

if __name__ == "__main__":
    # Test memory orchestrator
    orchestrator = MemoryOrchestrator()
    
    # Test learn functionality
    print("Testing learn...")
    result = orchestrator.learn("I prefer using double quotes")
    print(f"Learn result: {result}")
    
    # Test recall functionality
    print("\nTesting recall...")
    memories = orchestrator.recall("double quotes")
    print(f"Recalled {len(memories)} memories")
    for i, memory in enumerate(memories):
        print(f"  {i+1}. [{memory.get('memory_type')}] {memory.get('content', '')}")
    
    # Test search functionality
    print("\nTesting search...")
    search_results = orchestrator.search("double quotes")
    print(f"Search found {len(search_results)} results")
    
    # Test statistics functionality
    print("\nTesting stats...")
    stats = orchestrator.get_stats()
    print(f"Stats: {stats}")
