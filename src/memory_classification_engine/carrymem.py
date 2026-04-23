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
import json
import os
from datetime import datetime

from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.adapters.base import MemoryEntry, StorageAdapter, StoredMemory
from memory_classification_engine.adapters.sqlite_adapter import SQLiteAdapter
from memory_classification_engine.adapters.obsidian_adapter import ObsidianAdapter
from memory_classification_engine.adapters.loader import load_adapter


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
        elif isinstance(storage, str):
            adapter_cls = load_adapter(storage)
            if adapter_cls is None:
                raise ValueError(
                    f"Unknown adapter: {storage!r}. "
                    "Use 'sqlite', 'obsidian', a StorageAdapter instance, "
                    "or install a plugin that registers this adapter name."
                )
            if storage == "obsidian":
                self._adapter = adapter_cls()
            else:
                self._adapter = adapter_cls()
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
    def storage(self) -> Optional[StorageAdapter]:
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

    def declare_preference(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.declare(message, context)

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

    def export_memories(
        self,
        output_path: Optional[str] = None,
        format: str = "json",
        namespace: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Export memories to a portable format.

        Args:
            output_path: File path to write. If None, returns dict without writing.
            format: Export format ('json' or 'markdown').
            namespace: Export only this namespace. If None, export current namespace.

        Returns:
            Dict with export metadata and data.
        """
        if not self._adapter:
            raise StorageNotConfiguredError()

        ns = namespace or self._namespace
        stats = self._adapter.get_stats()
        all_memories = self._adapter.recall("", limit=10000)

        if ns != "default" and isinstance(self._adapter, SQLiteAdapter):
            all_memories = self._adapter.recall("", limit=10000, namespaces=[ns])

        export_data = {
            "schema_version": "1.0.0",
            "export_format": "carrymem_portable",
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "source": {
                "version": "0.3.0",
                "namespace": ns,
                "total_memories": len(all_memories),
            },
            "memories": [m.to_dict() for m in all_memories],
        }

        if format == "markdown":
            md_lines = [
                f"# CarryMem Memory Export",
                f"",
                f"- **Exported**: {export_data['exported_at']}",
                f"- **Namespace**: {ns}",
                f"- **Total memories**: {len(all_memories)}",
                f"",
            ]
            by_type: Dict[str, list] = {}
            for m in all_memories:
                d = m.to_dict()
                t = d.get("type", "unknown")
                by_type.setdefault(t, []).append(d)

            for mem_type, items in sorted(by_type.items()):
                md_lines.append(f"## {mem_type}")
                md_lines.append("")
                for item in items:
                    content = item.get("content", "")
                    conf = item.get("confidence", 0)
                    tier = item.get("tier", "?")
                    md_lines.append(f"- [{tier}] {content} (confidence: {conf:.0%})")
                md_lines.append("")

            md_content = "\n".join(md_lines)
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
            return {
                "exported": True,
                "format": "markdown",
                "path": output_path,
                "total_memories": len(all_memories),
                "namespace": ns,
                "content": md_content if not output_path else None,
            }

        json_content = json.dumps(export_data, ensure_ascii=False, indent=2)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_content)

        return {
            "exported": True,
            "format": "json",
            "path": output_path,
            "total_memories": len(all_memories),
            "namespace": ns,
            "data": export_data if not output_path else None,
        }

    def import_memories(
        self,
        input_path: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        merge_strategy: str = "skip_existing",
    ) -> Dict[str, Any]:
        """Import memories from a portable format.

        Args:
            input_path: File path to read. If None, uses data parameter.
            data: Direct dict data (alternative to file).
            namespace: Import into this namespace. If None, uses current.
            merge_strategy: 'skip_existing' or 'overwrite'.

        Returns:
            Dict with import results.
        """
        if not self._adapter:
            raise StorageNotConfiguredError()

        if input_path:
            with open(input_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)
        elif data:
            import_data = data
        else:
            raise ValueError("Either input_path or data must be provided")

        target_ns = namespace or self._namespace
        memories = import_data.get("memories", [])

        imported = 0
        skipped = 0
        errors = 0

        for mem_dict in memories:
            try:
                content_hash = mem_dict.get("content_hash", "")
                if merge_strategy == "skip_existing" and content_hash:
                    existing = self._adapter.recall(
                        mem_dict.get("content", "")[:50], limit=5
                    )
                    if any(
                        hasattr(e, 'content_hash') and e.content_hash == content_hash
                        for e in existing
                    ):
                        skipped += 1
                        continue

                entry = MemoryEntry(
                    id=mem_dict.get("id", ""),
                    type=mem_dict.get("type", "unknown"),
                    content=mem_dict.get("content", ""),
                    confidence=mem_dict.get("confidence", 0.5),
                    tier=mem_dict.get("tier", 2),
                    source_layer=mem_dict.get("source_layer", "import"),
                    reasoning=mem_dict.get("reasoning", ""),
                    suggested_action="store",
                    recall_hint=mem_dict.get("recall_hint"),
                    metadata={
                        **mem_dict.get("metadata", {}),
                        "imported_from": import_data.get("source", {}).get("namespace", "unknown"),
                        "imported_at": datetime.utcnow().isoformat() + "Z",
                    },
                )
                self._adapter.remember(entry)
                imported += 1
            except Exception:
                errors += 1

        return {
            "imported": imported,
            "skipped": skipped,
            "errors": errors,
            "total_processed": len(memories),
            "namespace": target_ns,
            "merge_strategy": merge_strategy,
        }

    def build_system_prompt(
        self,
        context: Optional[str] = None,
        max_memories: int = 10,
        max_knowledge: int = 5,
        language: str = "en",
    ) -> str:
        memories_section = ""
        knowledge_section = ""

        if self._adapter:
            try:
                query = context or ""
                if query:
                    mem_results = self.recall_memories(query=query, limit=max_memories)
                else:
                    mem_results = self.recall_memories(limit=max_memories)

                if mem_results:
                    type_labels = {
                        "user_preference": "Preference",
                        "correction": "Correction",
                        "decision": "Decision",
                        "fact_declaration": "Fact",
                        "relationship": "Relationship",
                        "task_pattern": "Pattern",
                        "sentiment_marker": "Sentiment",
                    }
                    lines = []
                    for m in mem_results:
                        label = type_labels.get(m.get("type", ""), m.get("type", "Info"))
                        content = m.get("content", "")
                        conf = m.get("confidence", 0)
                        source = m.get("source_layer", "")
                        src_tag = f" [{source}]" if source and source != "unknown" else ""
                        lines.append(f"- [{label}{src_tag}] {content} (confidence: {conf:.0%})")
                    memories_section = "\n".join(lines)
            except Exception:
                pass

        if self._knowledge_adapter and context:
            try:
                kn_results = self.recall_from_knowledge(query=context, limit=max_knowledge)
                if kn_results:
                    lines = []
                    for k in kn_results:
                        title = k.get("title", "Untitled")
                        content = k.get("content", "")[:200]
                        tags = k.get("tags", [])
                        tag_str = f" [{', '.join(tags[:3])}]" if tags else ""
                        lines.append(f"- {title}{tag_str}: {content}")
                    knowledge_section = "\n".join(lines)
            except Exception:
                pass

        if language == "zh":
            return self._build_prompt_zh(memories_section, knowledge_section, context)
        elif language == "ja":
            return self._build_prompt_ja(memories_section, knowledge_section, context)
        else:
            return self._build_prompt_en(memories_section, knowledge_section, context)

    def _build_prompt_en(self, memories: str, knowledge: str, context: Optional[str]) -> str:
        parts = [
            "You are an AI assistant with access to the user's memory and knowledge base.",
            "Follow these retrieval priorities when responding:",
            "1. **User Memories** (highest priority) — Personal preferences, corrections, and decisions the user has shared.",
            "2. **Knowledge Base** — Notes and documents from the user's personal vault.",
            "3. **General Knowledge** (lowest priority) — Use only when memories and knowledge base don't cover the topic.",
        ]

        if memories:
            parts.append("\n## User Memories\n" + memories)

        if knowledge:
            parts.append("\n## Knowledge Base\n" + knowledge)

        parts.append("\n## Guidelines")
        parts.append("- Always respect user preferences and corrections, even if they contradict general best practices.")
        parts.append("- If a user previously corrected something, the correction overrides the original.")
        parts.append("- Reference specific memories when relevant: 'Based on your preference for...'")

        return "\n".join(parts)

    def _build_prompt_zh(self, memories: str, knowledge: str, context: Optional[str]) -> str:
        parts = [
            "你是一个拥有用户记忆和知识库访问权限的AI助手。",
            "回复时请遵循以下检索优先级：",
            "1. **用户记忆**（最高优先级）— 用户的个人偏好、纠正和决策。",
            "2. **知识库** — 来自用户个人笔记库的文档。",
            "3. **通用知识**（最低优先级）— 仅在记忆和知识库未覆盖时使用。",
        ]

        if memories:
            parts.append("\n## 用户记忆\n" + memories)

        if knowledge:
            parts.append("\n## 知识库\n" + knowledge)

        parts.append("\n## 指导原则")
        parts.append("- 始终尊重用户的偏好和纠正，即使与通用最佳实践矛盾。")
        parts.append("- 如果用户之前纠正过某事，纠正内容覆盖原始内容。")
        parts.append("- 相关时引用具体记忆：'根据你对...的偏好...'")

        return "\n".join(parts)

    def _build_prompt_ja(self, memories: str, knowledge: str, context: Optional[str]) -> str:
        parts = [
            "あなたはユーザーの記憶とナレッジベースにアクセスできるAIアシスタントです。",
            "回答時は以下の検索優先度に従ってください：",
            "1. **ユーザー記憶**（最優先）— ユーザーの個人的な好み、訂正、決定。",
            "2. **ナレッジベース** — ユーザーの個人vaultのドキュメント。",
            "3. **一般知識**（最低優先）— 記憶とナレッジベースでカバーされていない場合のみ使用。",
        ]

        if memories:
            parts.append("\n## ユーザー記憶\n" + memories)

        if knowledge:
            parts.append("\n## ナレッジベース\n" + knowledge)

        parts.append("\n## ガイドライン")
        parts.append("- 一般的なベストプラクティスと矛盾しても、ユーザーの好みと訂正を常に尊重してください。")
        parts.append("- ユーザーが以前何かを訂正した場合、訂正が元の内容を上書きします。")
        parts.append("- 関連する場合は具体的な記憶を参照：'...の好みに基づいて...'")

        return "\n".join(parts)

    def _count_by_type(self, entries: List[MemoryEntry]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in entries:
            counts[e.type] = counts.get(e.type, 0) + 1
        return counts
