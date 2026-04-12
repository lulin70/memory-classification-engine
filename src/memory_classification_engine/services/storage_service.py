"""Storage Service for Memory Classification Engine."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from memory_classification_engine.services.base_service import BaseService
from memory_classification_engine.coordinators.storage_coordinator import StorageCoordinator
from memory_classification_engine.utils.helpers import get_current_time


class StorageService(BaseService):
    """Service for memory storage operations.

    This service handles:
    - Memory CRUD operations
    - Storage tier management
    - Batch operations
    - Memory retrieval and search
    """

    def __init__(self, config):
        """Initialize storage service.

        Args:
            config: Configuration manager.
        """
        super().__init__(config)
        self.storage_coordinator = None

    def initialize(self) -> None:
        """Initialize storage resources."""
        self.storage_coordinator = StorageCoordinator(self.config)
        self._initialized = True
        self.log_info("Storage service initialized")

    def shutdown(self) -> None:
        """Clean up storage resources."""
        if self.storage_coordinator:
            self.storage_coordinator.close()
        self._initialized = False
        self.log_info("Storage service shutdown")

    def store_memory(self, memory: Dict[str, Any]) -> bool:
        """Store a single memory.

        Args:
            memory: Memory data to store.

        Returns:
            True if successful, False otherwise.
        """
        if not self._initialized:
            raise RuntimeError("Storage service not initialized")

        try:
            # Comment in Chinese removednt
            if 'created_at' not in memory:
                memory['created_at'] = get_current_time()
            if 'updated_at' not in memory:
                memory['updated_at'] = memory['created_at']

            self.storage_coordinator.store_memory(memory)
            return True
        except Exception as e:
            self.log_error(f"Failed to store memory: {e}")
            return False

    def store_memories_batch(self, memories: List[Dict[str, Any]]) -> int:
        """Store multiple memories in batch.

        Args:
            memories: List of memory data to store.

        Returns:
            Number of successfully stored memories.
        """
        if not self._initialized:
            raise RuntimeError("Storage service not initialized")

        if not memories:
            return 0

        try:
            # Comment in Chinese removedmps
            current_time = get_current_time()
            for memory in memories:
                if 'created_at' not in memory:
                    memory['created_at'] = current_time
                if 'updated_at' not in memory:
                    memory['updated_at'] = current_time

            self.storage_coordinator.store_memories_batch(memories)
            return len(memories)
        except Exception as e:
            self.log_error(f"Failed to store memories batch: {e}")
            return 0

    def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a memory by ID.

        Args:
            memory_id: Memory identifier.

        Returns:
            Memory data or None if not found.
        """
        if not self._initialized:
            raise RuntimeError("Storage service not initialized")

        try:
            return self.storage_coordinator.retrieve_memory(memory_id)
        except Exception as e:
            self.log_error(f"Failed to retrieve memory {memory_id}: {e}")
            return None

    def retrieve_memories(
        self,
        query: Optional[str] = None,
        tier: Optional[int] = None,
        limit: int = 100,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve memories with optional filtering.

        Args:
            query: Optional search query.
            tier: Optional storage tier filter.
            limit: Maximum number of memories to retrieve.
            memory_type: Optional memory type filter.

        Returns:
            List of memory data.
        """
        if not self._initialized:
            raise RuntimeError("Storage service not initialized")

        try:
            memories = self.storage_coordinator.retrieve_memories(
                query=query,
                tier=tier,
                limit=limit
            )

            # Comment in Chinese removedd
            if memory_type:
                memories = [
                    m for m in memories
                    if m.get('type') == memory_type or m.get('memory_type') == memory_type
                ]

            return memories
        except Exception as e:
            self.log_error(f"Failed to retrieve memories: {e}")
            return []

    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory.

        Args:
            memory_id: Memory identifier.
            updates: Dictionary of fields to update.

        Returns:
            True if successful, False otherwise.
        """
        if not self._initialized:
            raise RuntimeError("Storage service not initialized")

        try:
            # Comment in Chinese removedmp
            updates['updated_at'] = get_current_time()

            self.storage_coordinator.update_memory(memory_id, updates)
            return True
        except Exception as e:
            self.log_error(f"Failed to update memory {memory_id}: {e}")
            return False

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory.

        Args:
            memory_id: Memory identifier.

        Returns:
            True if successful, False otherwise.
        """
        if not self._initialized:
            raise RuntimeError("Storage service not initialized")

        try:
            self.storage_coordinator.delete_memory(memory_id)
            return True
        except Exception as e:
            self.log_error(f"Failed to delete memory {memory_id}: {e}")
            return False

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with storage statistics.
        """
        if not self._initialized:
            return {'error': 'Storage service not initialized'}

        try:
            return self.storage_coordinator.get_stats()
        except Exception as e:
            self.log_error(f"Failed to get storage stats: {e}")
            return {'error': str(e)}

    def archive_memories(self, memory_ids: List[str]) -> int:
        """Archive memories to long-term storage.

        Args:
            memory_ids: List of memory identifiers to archive.

        Returns:
            Number of successfully archived memories.
        """
        if not self._initialized:
            raise RuntimeError("Storage service not initialized")

        archived_count = 0
        for memory_id in memory_ids:
            try:
                memory = self.retrieve_memory(memory_id)
                if memory:
                    memory['archived'] = True
                    memory['archived_at'] = get_current_time()
                    if self.store_memory(memory):
                        archived_count += 1
            except Exception as e:
                self.log_error(f"Failed to archive memory {memory_id}: {e}")

        return archived_count
