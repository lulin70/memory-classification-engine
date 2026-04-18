"""Storage coordinator for managing all storage tiers."""

import threading
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from memory_classification_engine.storage.tier2 import Tier2Storage
from memory_classification_engine.storage.tier3 import Tier3Storage
from memory_classification_engine.storage.tier4 import Tier4Storage
from memory_classification_engine.utils.logger import logger


class StorageCoordinator:
    """Coordinates storage operations across all tiers."""
    
    def __init__(self, config: Any):
        """Initialize storage coordinator.
        
        Args:
            config: Configuration manager instance.
        """
        self.config = config
        storage_path = config.get('storage.data_path', './data')
        
        # Format stats outputs
        self.tier2_storage = Tier2Storage(config.get('storage.tier2_path', './data/tier2'))
        self.tier3_storage = Tier3Storage(config.get('storage.tier3_path', './data/tier3'))
        self.tier4_storage = Tier4Storage(config.get('storage.tier4_path', './data/tier4'))
        
        # GC scheduling params
        self.min_weight = config.get('memory.forgetting.min_weight', 0.1)
        
        # Thread-safe hash index for O(1) get_memory lookups
        self._id_index: Dict[str, tuple] = {}
        self._index_dirty = True
        self._index_lock = threading.RLock()
    
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        """Store a memory in the appropriate tier.
        
        Args:
            memory: The memory to store.
            
        Returns:
            True if successful, False otherwise.
        """
        tier = memory.get('tier', 3)
        
        if tier == 2:
            result = self.tier2_storage.store_memory(memory)
        elif tier == 3:
            result = self.tier3_storage.store_memory(memory)
        elif tier == 4:
            result = self.tier4_storage.store_memory(memory)
        else:
            logger.warning(f"Unknown tier {tier}, defaulting to tier 3")
            result = self.tier3_storage.store_memory(memory)
        
        if result and memory.get('id'):
            storage_map = {2: self.tier2_storage, 3: self.tier3_storage, 4: self.tier4_storage}
            with self._index_lock:
                self._id_index[memory['id']] = (storage_map.get(tier, self.tier3_storage), tier)
        
        return result
    
    def store_memories_batch(self, memories: List[Dict[str, Any]]) -> bool:
        """Store multiple memories in batch to reduce I/O operations.
        
        Args:
            memories: List of memories to store.
            
        Returns:
            True if all memories were stored successfully, False otherwise.
        """
        try:
            # Format stats output
            tiered_memories = {
                2: [],
                3: [],
                4: []
            }
            
            for memory in memories:
                tier = memory.get('tier', 3)
                tiered_memories[tier].append(memory)
            
            # Store memories by tier
            success = True
            
            if tiered_memories[2]:
                for memory in tiered_memories[2]:
                    if not self.tier2_storage.store_memory(memory):
                        logger.warning(f"Failed to store memory in tier 2: {memory.get('id')}")
                        success = False
            
            if tiered_memories[3]:
                for memory in tiered_memories[3]:
                    if not self.tier3_storage.store_memory(memory):
                        logger.warning(f"Failed to store memory in tier 3: {memory.get('id')}")
                        success = False
            
            if tiered_memories[4]:
                for memory in tiered_memories[4]:
                    if not self.tier4_storage.store_memory(memory):
                        logger.warning(f"Failed to store memory in tier 4: {memory.get('id')}")
                        success = False
            
            return success
        except Exception as e:
            logger.error(f"Error storing memories in batch: {e}", exc_info=True)
            return False
    
    def retrieve_memories(self, query: str, limit: int = 5, tier: Optional[int] = None, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve memories from storage.
        
        Args:
            query: Query string to search for.
            limit: Maximum number of memories to return.
            tier: Specific tier to retrieve from (None for all tiers).
            memory_type: Optional memory type to filter memories.
            
        Returns:
            List of memories.
        """
        if tier == 2:
            memories = self.tier2_storage.retrieve_memories(query, limit)
        elif tier == 3:
            memories = self.tier3_storage.retrieve_memories(query, limit)
        elif tier == 4:
            memories = self.tier4_storage.retrieve_memories(query, limit)
        else:
            # Format stats outputs - parallel retrieval
            memories = self._retrieve_parallel(query, limit)
        
        # GC execution handler
        if memory_type:
            memories = [memory for memory in memories if memory.get('memory_type') == memory_type]
        
        return memories
    
    def _retrieve_parallel(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories from all tiers in parallel."""
        def _fetch(tier_storage, lim):
            try:
                return tier_storage.retrieve_memories(query, lim)
            except Exception as e:
                logger.warning(f"Parallel retrieval error: {e}")
                return []
        
        all_memories = []
        seen_ids = set()
        
        with ThreadPoolExecutor(max_workers=3, thread_name_prefix='mce_tier') as executor:
            futures = {
                executor.submit(_fetch, self.tier2_storage, limit // 3): 'tier2',
                executor.submit(_fetch, self.tier3_storage, limit // 3 * 2): 'tier3',
                executor.submit(_fetch, self.tier4_storage, limit // 3): 'tier4',
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    for memory in result:
                        mid = memory.get('id')
                        if mid and mid not in seen_ids:
                            seen_ids.add(mid)
                            all_memories.append(memory)
                except Exception as e:
                    logger.warning(f"Parallel retrieval future error: {e}")
        
        return all_memories
    
    def archive_low_weight_memories(self, weight_calculator: Callable[[Dict[str, Any]], float]):
        """Archive low-weight memories across all tiers.
        
        Args:
            weight_calculator: Function to calculate memory weight.
        """
        self._archive_tier_memories(self.tier2_storage, weight_calculator)
        self._archive_tier_memories(self.tier3_storage, weight_calculator)
        self._archive_tier_memories(self.tier4_storage, weight_calculator)
    
    def _archive_tier_memories(self, storage: Any, weight_calculator: Callable[[Dict[str, Any]], float]):
        """Archive low-weight memories in a specific tier.
        
        Args:
            storage: The storage instance to archive.
            weight_calculator: Function to calculate memory weight.
        """
        try:
            memories = storage.retrieve_memories()
            archived_count = 0
            
            for memory in memories:
                weight = weight_calculator(memory)
                if weight < self.min_weight:
                    storage.delete_memory(memory.get('id'))
                    archived_count += 1
            
            if archived_count > 0:
                logger.info(f"Archived {archived_count} low-weight memories from {storage.__class__.__name__}")
        except Exception as e:
            logger.error(f"Error archiving memories from {storage.__class__.__name__}: {e}", exc_info=True)
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID using hash index (O(1)).
        
        Thread-safe: uses RLock to protect _id_index and _index_dirty
        against concurrent access from MCP Server multi-request scenarios.
        
        Args:
            memory_id: The memory ID.
            
        Returns:
            The memory if found, None otherwise.
        """
        with self._index_lock:
            if not self._index_dirty and memory_id in self._id_index:
                storage, _ = self._id_index[memory_id]
                try:
                    return storage.get_memory_by_id(memory_id)
                except AttributeError:
                    self._index_dirty = True
        
        if self._index_dirty:
            self._rebuild_index()
        
        with self._index_lock:
            if memory_id in self._id_index:
                storage, _ = self._id_index[memory_id]
                try:
                    return storage.get_memory_by_id(memory_id)
                except AttributeError:
                    pass
        
        # Fallback: linear scan (only when index misses)
        for storage in [self.tier2_storage, self.tier3_storage, self.tier4_storage]:
            try:
                memories = storage.retrieve_memories()
                for memory in memories:
                    if memory.get('id') == memory_id:
                        with self._index_lock:
                            self._id_index[memory_id] = (storage, memory.get('tier', 3))
                        return memory
            except Exception as e:
                logger.warning(f"Error searching {storage.__class__.__name__}: {e}")
        
        return None
    
    def _rebuild_index(self):
        """Rebuild the ID-to-storage hash index. Thread-safe: caller must hold _index_lock or call from single-threaded context."""
        with self._index_lock:
            self._id_index.clear()
            for storage, tier_val in [(self.tier2_storage, 2), (self.tier3_storage, 3), (self.tier4_storage, 4)]:
                try:
                    memories = storage.retrieve_memories()
                    for m in memories:
                        mid = m.get('id')
                        if mid:
                            self._id_index[mid] = (storage, tier_val)
                except Exception:
                    pass
            self._index_dirty = False
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory.
        
        Args:
            memory_id: The memory ID.
            updates: Dictionary of updates.
            
        Returns:
            True if successful, False otherwise.
        """
        result = self._update_memory_internal(memory_id, updates)
        if result:
            with self._index_lock:
                self._id_index.pop(memory_id, None)
                self._index_dirty = True
        return result
    
    def _update_memory_internal(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        # Vector index update handler
        memory = self.get_memory(memory_id)
        if not memory:
            return False
        
        # Vector index update handler
        tier = memory.get('tier', 3)
        if tier == 2:
            return self.tier2_storage.update_memory(memory_id, updates)
        elif tier == 3:
            return self.tier3_storage.update_memory(memory_id, updates)
        elif tier == 4:
            return self.tier4_storage.update_memory(memory_id, updates)
        
        return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory.
        
        Args:
            memory_id: The memory ID.
            
        Returns:
            True if successful, False otherwise.
        """
        # Vector index update handler
        memory = self.get_memory(memory_id)
        if not memory:
            return False
        
        # Vector index update handler
        tier = memory.get('tier', 3)
        result = False
        if tier == 2:
            result = self.tier2_storage.delete_memory(memory_id)
        elif tier == 3:
            result = self.tier3_storage.delete_memory(memory_id)
        elif tier == 4:
            result = self.tier4_storage.delete_memory(memory_id)
        
        if result:
            with self._index_lock:
                self._id_index.pop(memory_id, None)
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Dictionary with statistics.
        """
        tier2_stats = self.tier2_storage.get_stats()
        tier3_stats = self.tier3_storage.get_stats()
        tier4_stats = self.tier4_storage.get_stats()
        
        # 安全地获取总记忆数，确保类型正确
        def get_safe_total(stats):
            if isinstance(stats, dict):
                total = stats.get('total_memories', 0)
                return int(total) if isinstance(total, (int, float)) else 0
            return 0
        
        total_memories = (
            get_safe_total(tier2_stats) +
            get_safe_total(tier3_stats) +
            get_safe_total(tier4_stats)
        )
        
        return {
            'tier2': tier2_stats,
            'tier3': tier3_stats,
            'tier4': tier4_stats,
            'total_memories': total_memories
        }
