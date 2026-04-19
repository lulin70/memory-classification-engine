"""
Storage Adapter Abstract Base Class and MemoryEntry data class.

Pure Upstream Mode (v0.3.0): MCE does not store memories itself.
Instead, it outputs standardized MemoryEntry objects that downstream systems
consume via implementations of this adapter interface.

Available official adapters (planned):
- BuiltInStorageAdapter: Wraps MCE's internal SQLite (@deprecated)
- SupermemoryAdapter: Bridges to supermemory.ai cloud service
- ObsidianAdapter: Writes to local Obsidian vault markdown files
- Mem0Adapter: Connects to Mem0 self-hosted instance

Community adapters are welcome!
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class MemoryEntry:
    """Standardized memory entry — MCE output, Adapter input.

    This is the data contract between MCE's classification engine
    and any downstream storage system. All adapters receive MemoryEntry
    objects and map them to their native storage format.

    Uses __slots__ for memory efficiency when processing large batches.
    """

    __slots__ = (
        'id', 'type', 'content', 'confidence', 'tier',
        'source_layer', 'reasoning', 'suggested_action', 'metadata'
    )

    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get('id', '')
        self.type: str = data.get('type', 'unknown')
        self.content: str = data.get('content', '')
        self.confidence: float = data.get('confidence', 0.0)
        self.tier: int = data.get('tier', 2)
        self.source_layer: str = data.get('source_layer', 'unknown')
        self.reasoning: str = data.get('reasoning', '')
        self.suggested_action: str = data.get('suggested_action', 'store')
        self.metadata: Dict[str, Any] = data.get('metadata', {})

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to plain dict (JSON-safe)."""
        return {s: getattr(self, s) for s in self.__slots__}

    def __repr__(self) -> str:
        return (
            f"MemoryEntry(id={self.id!r}, type={self.type!r}, "
            f"conf={self.confidence:.2f}, action={self.suggested_action!r})"
        )


class StorageAdapter(ABC):
    """Abstract base class for downstream storage adapters.

    Every downstream storage system that wants to receive MCE's
    classification output must implement this interface.

    Implementation guide:
    1. Subclass StorageAdapter
    2. Implement all abstract methods
    3. Set name and capabilities properties
    4. Register with MCE via engine.set_storage_adapter(adapter)

    Example:
        class MyPostgresAdapter(StorageAdapter):
            @property
            def name(self) -> str:
                return "my_postgres"

            def store(self, entry: MemoryEntry) -> str:
                cursor.execute(
                    "INSERT INTO memories (type, content, confidence) VALUES (%s, %s, %s)",
                    (entry.type, entry.content, entry.confidence)
                )
                return cursor.fetchone()[0]
            # ... implement other methods
    """

    @abstractmethod
    def store(self, entry: MemoryEntry) -> str:
        """Store a single memory entry.

        Args:
            entry: The MemoryEntry to persist

        Returns:
            The storage system's unique ID for this entry
        """
        ...

    @abstractmethod
    def store_batch(self, entries: List[MemoryEntry]) -> List[str]:
        """Store multiple memory entries atomically.

        Args:
            entries: List of MemoryEntry objects to persist

        Returns:
            List of storage system IDs, one per entry (same order)
        """
        ...

    @abstractmethod
    def retrieve(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve memories matching a query.

        Args:
            query: Search query (keywords or natural language)
            limit: Maximum number of results

        Returns:
            List of memory dicts (format depends on implementation)
        """
        ...

    @abstractmethod
    def delete(self, storage_id: str) -> bool:
        """Delete a memory by its storage system ID.

        Args:
            storage_id: The ID returned by store()

        Returns:
            True if deleted, False if not found
        """
        ...

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get storage system statistics.

        Returns:
            Dict with stats like total_count, by_type breakdown, etc.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable adapter name (e.g., 'supermemory', 'obsidian')."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """Declare what this adapter supports.

        Example:
            {"vector_search": True, "graph": False, "ttl": False}
        """
        ...
