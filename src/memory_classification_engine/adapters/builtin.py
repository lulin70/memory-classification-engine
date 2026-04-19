"""
Built-in SQLite Storage Adapter.

⚠️ **DEPRECATED since v0.3.0** — This adapter wraps MCE's internal
SQLite storage coordinator for transition compatibility only.

New projects should use a dedicated downstream adapter:
- SupermemoryAdapter (cloud, best retrieval quality)
- ObsidianAdapter (local markdown, human-readable)
- Mem0Adapter (self-hosted, vector+graph)
- Or implement your own StorageAdapter subclass (~150 lines).

This adapter will be removed in v0.4.0.
"""

import warnings
from typing import Any, Dict, List

from .base import MemoryEntry, StorageAdapter


class BuiltInStorageAdapter(StorageAdapter):
    """Wraps MCE's internal SQLite storage as a StorageAdapter.

    DEPRECATED: Only for transition from v0.2.0 built-in storage to
    v0.3.0+ pure upstream mode. Will be removed in v0.4.0.
    """

    def __init__(self, engine=None):
        warnings.warn(
            "BuiltInStorageAdapter is deprecated since v0.3.0. "
            "Use a dedicated downstream adapter instead "
            "(SupermemoryAdapter / ObsidianAdapter / custom). "
            "This adapter will be removed in v0.4.0.",
            DeprecationWarning,
            stacklevel=2
        )
        self._engine = engine
        self._coordinator = None
        if engine:
            self._coordinator = getattr(engine, 'storage_coordinator', None)

    @property
    def name(self) -> str:
        return "builtin_sqlite"

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "vector_search": False,
            "graph": False,
            "ttl": False,
            "full_text_search": True,
            "tiered_storage": True
        }

    def store(self, entry: MemoryEntry) -> str:
        """Store via internal storage coordinator."""
        if not self._coordinator:
            raise RuntimeError("BuiltInStorageAdapter requires an engine with storage_coordinator")
        memory_data = {
            "content": entry.content,
            "memory_type": entry.type,
            "confidence": entry.confidence,
            "tier": entry.tier,
            "source": entry.source_layer,
            "metadata": entry.metadata
        }
        result = self._coordinator.store_memory(memory_data)
        return result.get("id", "")

    def store_batch(self, entries: List[MemoryEntry]) -> List[str]:
        """Batch store via internal storage coordinator."""
        return [self.store(entry) for entry in entries]

    def retrieve(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve via internal storage coordinator."""
        if not self._coordinator:
            raise RuntimeError("BuiltInStorageAdapter requires an engine with storage_coordinator")
        return self._coordinator.retrieve_memories(query, limit)

    def delete(self, storage_id: str) -> bool:
        """Delete via internal storage coordinator."""
        if not self._coordinator:
            raise RuntimeError("BuiltInStorageAdapter requires an engine with storage_coordinator")
        try:
            self._coordinator.delete_memory(storage_id)
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get stats from internal storage coordinator."""
        if not self._coordinator:
            return {"adapter": "builtin_sqlite", "error": "no_coordinator"}
        try:
            stats = self._coordinator.get_stats()
            stats["adapter"] = "builtin_sqlite"
            stats["deprecated"] = True
            return stats
        except Exception as e:
            return {"adapter": "builtin_sqlite", "error": str(e)}
