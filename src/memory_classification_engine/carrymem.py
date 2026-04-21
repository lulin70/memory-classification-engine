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

    # Mode 4: With knowledge base (Obsidian)
    from carrymem.adapters import ObsidianAdapter
    cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
    cm.index_knowledge()
    results = cm.recall_from_knowledge("Python design patterns")
"""

from typing import Any, Dict, List, Optional

from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.adapters.base import MemoryEntry, StorageAdapter, StoredMemory
from memory_classification_engine.adapters.sqlite_adapter import SQLiteAdapter
from memory_classification_engine.adapters.obsidian_adapter import ObsidianAdapter


class StorageNotConfiguredError(Exception):
    def __init__(self):
        super().__init__(
            "Storage adapter not configured. "
            "Use CarryMem(storage='sqlite') or CarryMem(storage=YourAdapter()) "
            "to enable storage features."
        )


class KnowledgeNotConfiguredError(Exception):
    def __init__(self):
        super().__init__(
            "Knowledge adapter not configured. "
            "Use CarryMem(knowledge_adapter=ObsidianAdapter('/path/to/vault')) "
            "to enable knowledge base features."
        )


class CarryMem:
    """CarryMem — 随身记忆库.

    让 AI Agent 记住用户。分类是核心，存储可替换，默认开箱即用。
    知识库只读，记忆可读写。检索优先级：记忆 > 知识库。
    """

    def __init__(
        self,
        storage: Optional[Any] = "sqlite",
        db_path: Optional[str] = None,
        knowledge_adapter: Optional[StorageAdapter] = None,
        namespace: str = "default",
        config: Optional[Dict] = None,
    ):
        self._engine = MemoryClassificationEngine()
        self._namespace = namespace

        if storage is None:
            self._adapter = None
        elif storage == "sqlite":
            self._adapter = SQLiteAdapter(db_path=db_path, namespace=namespace)
        elif isinstance(storage, StorageAdapter):
            self._adapter = storage
        else:
            raise ValueError(
                f"Invalid storage type: {storage!r}. "
                "Use None, 'sqlite', or a StorageAdapter instance."
            )

        self._knowledge_adapter = knowledge_adapter

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def engine(self) -> MemoryClassificationEngine:
        return self._engine

    @property
    def adapter(self) -> Optional[StorageAdapter]:
        return self._adapter

    @property
    def knowledge_adapter(self) -> Optional[StorageAdapter]:
        return self._knowledge_adapter

    def index_knowledge(self) -> Dict[str, Any]:
        if not self._knowledge_adapter:
            raise KnowledgeNotConfiguredError()

        if isinstance(self._knowledge_adapter, ObsidianAdapter):
            return self._knowledge_adapter.index_vault()

        return {"error": "Knowledge adapter does not support indexing"}

    def recall_from_knowledge(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        if not self._knowledge_adapter:
            raise KnowledgeNotConfiguredError()

        results = self._knowledge_adapter.recall(query, filters=filters, limit=limit)
        if isinstance(results, list) and results and isinstance(results[0], dict):
            return results
        return [r.to_dict() if hasattr(r, 'to_dict') else r for r in results]

    def recall_all(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        namespaces: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        memory_results = []
        knowledge_results = []

        if self._adapter:
            try:
                if isinstance(self._adapter, SQLiteAdapter) and namespaces:
                    stored = self._adapter.recall(
                        query or "", filters=filters, limit=limit, namespaces=namespaces,
                    )
                    memory_results = [r.to_dict() for r in stored]
                else:
                    memory_results = self.recall_memories(query=query, filters=filters, limit=limit)
            except Exception:
                pass

        if self._knowledge_adapter:
            try:
                knowledge_results = self.recall_from_knowledge(query=query, filters=filters, limit=limit)
            except Exception:
                pass

        return {
            "memories": memory_results,
            "knowledge": knowledge_results,
            "memory_count": len(memory_results),
            "knowledge_count": len(knowledge_results),
            "total_count": len(memory_results) + len(knowledge_results),
            "namespace": self._namespace,
            "priority": "memory_first",
        }

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

    def declare(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self._adapter:
            raise StorageNotConfiguredError()

        result = self._engine.process_message(message, context=context)
        matches = result.get("matches", [])

        if not matches:
            entry = MemoryEntry(
                id="",
                type="user_preference",
                content=message,
                confidence=1.0,
                tier=2,
                source_layer="declaration",
                reasoning="User主动声明",
                suggested_action="store",
                metadata={"original_message": message, "source": "declaration"},
            )
            matches = [entry]
        else:
            entries = []
            for m in matches:
                entry = MemoryEntry(
                    id=m.get("id", ""),
                    type=m.get("memory_type") or m.get("type", "unknown"),
                    content=m.get("content", ""),
                    confidence=1.0,
                    tier=m.get("tier", 2),
                    source_layer="declaration",
                    reasoning=m.get("reasoning", "") + " (主动声明)",
                    suggested_action="store",
                    recall_hint=m.get("recall_hint"),
                    metadata={**m.get("metadata", {}), "source": "declaration"},
                )
                entries.append(entry)
            matches = entries

        stored_memories = []
        storage_keys = []
        for entry in matches:
            stored = self._adapter.remember(entry)
            stored_memories.append(stored.to_dict())
            storage_keys.append(stored.storage_key)

        return {
            "declared": True,
            "entries": stored_memories,
            "storage_keys": storage_keys,
            "source": "declaration",
            "summary": {
                "total_entries": len(stored_memories),
                "by_type": self._count_by_type(matches),
            },
        }

    def get_memory_profile(self) -> Dict[str, Any]:
        if not self._adapter:
            return {
                "summary": "No storage configured",
                "total_memories": 0,
                "highlights": {},
                "stats": {},
            }

        profile = self._adapter.get_profile()
        return profile

    def _count_by_type(self, entries: List[MemoryEntry]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in entries:
            counts[e.type] = counts.get(e.type, 0) + 1
        return counts
