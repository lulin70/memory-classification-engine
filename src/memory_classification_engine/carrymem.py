"""CarryMem — 随身记忆库的主入口.

Usage:
    # Mode 1: Classify + Store (default SQLite)
    from carrymem import CarryMem
    cm = CarryMem()
    result = cm.classify_and_remember("I prefer dark mode")

    # Mode 2: Pure classification (no storage)
    cm = CarryMem(storage=None)
    result = cm.classify_message("I prefer dark mode")

    # Mode 3: Custom storage adapter
    from carrymem.adapters import SQLiteAdapter
    cm = CarryMem(storage=SQLiteAdapter("/path/to/custom.db"))
"""

from typing import Any, Dict, List, Optional

from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.adapters.base import MemoryEntry, StorageAdapter, StoredMemory
from memory_classification_engine.adapters.sqlite_adapter import SQLiteAdapter


class StorageNotConfiguredError(Exception):
    def __init__(self):
        super().__init__(
            "Storage adapter not configured. "
            "Use CarryMem(storage='sqlite') or CarryMem(storage=YourAdapter()) "
            "to enable storage features."
        )


class CarryMem:
    """CarryMem — 随身记忆库.

    让 AI Agent 记住用户。分类是核心，存储可替换，默认开箱即用。
    """

    def __init__(
        self,
        storage: Optional[Any] = "sqlite",
        db_path: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        self._engine = MemoryClassificationEngine()

        if storage is None:
            self._adapter = None
        elif storage == "sqlite":
            self._adapter = SQLiteAdapter(db_path=db_path)
        elif isinstance(storage, StorageAdapter):
            self._adapter = storage
        else:
            raise ValueError(
                f"Invalid storage type: {storage!r}. "
                "Use None, 'sqlite', or a StorageAdapter instance."
            )

    @property
    def engine(self) -> MemoryClassificationEngine:
        return self._engine

    @property
    def adapter(self) -> Optional[StorageAdapter]:
        return self._adapter

    def classify_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        result = self._engine.process_message(message, context=context)

        matches = result.get("matches", [])
        entries = []
        for m in matches:
            entry = MemoryEntry(
                id=m.get("id", ""),
                type=m.get("memory_type") or m.get("type", "unknown"),
                content=m.get("content", ""),
                confidence=m.get("confidence", 0.0),
                tier=m.get("tier", 2),
                source_layer=m.get("source_layer", "unknown"),
                reasoning=m.get("reasoning", ""),
                suggested_action=m.get("suggested_action", "store"),
                recall_hint=m.get("recall_hint"),
                metadata=m.get("metadata", {}),
            )
            entries.append(entry)

        return {
            "should_remember": len(entries) > 0,
            "entries": [e.to_dict() for e in entries],
            "summary": {
                "total_entries": len(entries),
                "by_type": self._count_by_type(entries),
            },
        }

    def classify_and_remember(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self._adapter:
            raise StorageNotConfiguredError()

        classify_result = self.classify_message(message, context=context)

        if not classify_result["should_remember"]:
            return {
                **classify_result,
                "stored": False,
                "storage_keys": [],
            }

        stored_memories = []
        storage_keys = []
        for entry_dict in classify_result["entries"]:
            entry = MemoryEntry.from_dict(entry_dict)
            if entry.suggested_action == "store":
                stored = self._adapter.remember(entry)
                stored_memories.append(stored.to_dict())
                storage_keys.append(stored.storage_key)

        return {
            "should_remember": True,
            "entries": stored_memories,
            "stored": True,
            "storage_keys": storage_keys,
            "summary": classify_result["summary"],
        }

    def recall_memories(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        if not self._adapter:
            raise StorageNotConfiguredError()

        results = self._adapter.recall(query or "", filters=filters, limit=limit)
        return [r.to_dict() for r in results]

    def forget_memory(self, memory_id: str) -> bool:
        if not self._adapter:
            raise StorageNotConfiguredError()

        return self._adapter.forget(memory_id)

    def get_stats(self) -> Dict[str, Any]:
        if not self._adapter:
            return {"adapter": None, "total_count": 0}

        return self._adapter.get_stats()

    def _count_by_type(self, entries: List[MemoryEntry]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in entries:
            counts[e.type] = counts.get(e.type, 0) + 1
        return counts
