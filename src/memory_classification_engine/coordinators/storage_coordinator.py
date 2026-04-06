"""Storage coordinator for managing all storage tiers."""

from typing import Dict, List, Optional, Any, Callable
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
        
        # Initialize storage tiers
        self.tier2_storage = Tier2Storage(config.get('storage.tier2_path', './data/tier2'))
        self.tier3_storage = Tier3Storage(config.get('storage.tier3_path', './data/tier3'))
        self.tier4_storage = Tier4Storage(config.get('storage.tier4_path', './data/tier4'))
        
        # Archive settings
        self.min_weight = config.get('memory.forgetting.min_weight', 0.1)
    
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        """Store a memory in the appropriate tier.
        
        Args:
            memory: The memory to store.
            
        Returns:
            True if successful, False otherwise.
        """
        tier = memory.get('tier', 3)
        
        if tier == 2:
            return self.tier2_storage.store_memory(memory)
        elif tier == 3:
            return self.tier3_storage.store_memory(memory)
        elif tier == 4:
            return self.tier4_storage.store_memory(memory)
        else:
            logger.warning(f"Unknown tier {tier}, defaulting to tier 3")
            return self.tier3_storage.store_memory(memory)
    
    def store_memories_batch(self, memories: List[Dict[str, Any]]) -> bool:
        """Store multiple memories in batch to reduce I/O operations.
        
        Args:
            memories: List of memories to store.
            
        Returns:
            True if all memories were stored successfully, False otherwise.
        """
        try:
            # Group memories by tier
            tiered_memories = {
                2: [],
                3: [],
                4: []
            }
            
            for memory in memories:
                tier = memory.get('tier', 3)
                tiered_memories[tier].append(memory)
            
            # Store memories in batch per tier
            success = True
            
            if tiered_memories[2]:
                for memory in tiered_memories[2]:
                    if not self.tier2_storage.store_memory(memory):
                        success = False
            
            if tiered_memories[3]:
                for memory in tiered_memories[3]:
                    if not self.tier3_storage.store_memory(memory):
                        success = False
            
            if tiered_memories[4]:
                for memory in tiered_memories[4]:
                    if not self.tier4_storage.store_memory(memory):
                        success = False
            
            return success
        except Exception as e:
            logger.error(f"Error storing memories in batch: {e}", exc_info=True)
            return False
    
    def retrieve_memories(self, query: str = None, limit: int = None, tier: int = None) -> List[Dict[str, Any]]:
        """Retrieve memories from storage.
        
        Args:
            query: Optional query string.
            limit: Maximum number of memories to return.
            tier: Specific tier to retrieve from (None for all tiers).
            
        Returns:
            List of memories.
        """
        if tier == 2:
            return self.tier2_storage.retrieve_memories(query, limit)
        elif tier == 3:
            return self.tier3_storage.retrieve_memories(query, limit)
        elif tier == 4:
            return self.tier4_storage.retrieve_memories(query, limit)
        else:
            # Retrieve from all tiers
            tier2_memories = self.tier2_storage.retrieve_memories(query, limit)
            tier3_memories = self.tier3_storage.retrieve_memories(query, limit)
            tier4_memories = self.tier4_storage.retrieve_memories(query, limit)
            return tier2_memories + tier3_memories + tier4_memories
    
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
        """Get a specific memory by ID.
        
        Args:
            memory_id: The memory ID.
            
        Returns:
            The memory if found, None otherwise.
        """
        # Check tier 2
        for memory in self.tier2_storage.retrieve_memories():
            if memory.get('id') == memory_id:
                return memory
        
        # Check tier 3
        for memory in self.tier3_storage.retrieve_memories():
            if memory.get('id') == memory_id:
                return memory
        
        # Check tier 4
        for memory in self.tier4_storage.retrieve_memories():
            if memory.get('id') == memory_id:
                return memory
        
        return None
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory.
        
        Args:
            memory_id: The memory ID.
            updates: Dictionary of updates.
            
        Returns:
            True if successful, False otherwise.
        """
        # Find the memory and its storage
        memory = self.get_memory(memory_id)
        if not memory:
            return False
        
        # Determine which storage to use
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
        # Find the memory and its storage
        memory = self.get_memory(memory_id)
        if not memory:
            return False
        
        # Determine which storage to use
        tier = memory.get('tier', 3)
        if tier == 2:
            return self.tier2_storage.delete_memory(memory_id)
        elif tier == 3:
            return self.tier3_storage.delete_memory(memory_id)
        elif tier == 4:
            return self.tier4_storage.delete_memory(memory_id)
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Dictionary with statistics.
        """
        tier2_stats = self.tier2_storage.get_stats()
        tier3_stats = self.tier3_storage.get_stats()
        tier4_stats = self.tier4_storage.get_stats()
        
        return {
            'tier2': tier2_stats,
            'tier3': tier3_stats,
            'tier4': tier4_stats,
            'total_memories': (
                tier2_stats.get('total_memories', 0) +
                tier3_stats.get('total_memories', 0) +
                tier4_stats.get('total_memories', 0)
            )
        }
