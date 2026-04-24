"""SQLite Storage Adapter — CarryMem default storage backend.

Features:
- Zero-config: auto-creates database at ~/.carrymem/memories.db
- FTS5 full-text search for content and original_message
- Content deduplication via content_hash
- Tier-based TTL expiry
- Atomic batch operations via transactions
- **v0.4.0**: Semantic recall with synonym expansion, spell correction,
  cross-language mapping, and result fusion (zero external dependencies)
"""

import hashlib
import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .base import MemoryEntry, StorageAdapter, StoredMemory


def _escape_like(value: str) -> str:
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

try:
    from ..semantic.expander import SemanticExpander
    from ..semantic.merger import ResultMerger
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    original_message TEXT,
    confidence REAL NOT NULL DEFAULT 0.0,
    tier INTEGER NOT NULL DEFAULT 2,
    source_layer TEXT NOT NULL DEFAULT 'unknown',
    reasoning TEXT,
    suggested_action TEXT NOT NULL DEFAULT 'store',
    recall_hint TEXT,
    metadata TEXT,
    storage_key TEXT UNIQUE NOT NULL,
    namespace TEXT NOT NULL DEFAULT 'default',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT,
    access_count INTEGER NOT NULL DEFAULT 0,
    content_hash TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content,
    original_message,
    content='memories',
    content_rowid='rowid',
    tokenize='trigram'
);

CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_tier ON memories(tier);
CREATE INDEX IF NOT EXISTS idx_memories_confidence ON memories(confidence);
CREATE INDEX IF NOT EXISTS idx_memories_expires ON memories(expires_at);
CREATE INDEX IF NOT EXISTS idx_memories_content_hash ON memories(content_hash);
CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace);

-- Composite indexes for common query patterns (v0.4.1 optimization)
CREATE INDEX IF NOT EXISTS idx_memories_type_confidence ON memories(type, confidence DESC);
CREATE INDEX IF NOT EXISTS idx_memories_namespace_tier ON memories(namespace, tier);
CREATE INDEX IF NOT EXISTS idx_memories_namespace_type ON memories(namespace, type);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memories_namespace_created ON memories(namespace, created_at DESC);

CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, content, original_message)
    VALUES (new.rowid, new.content, new.original_message);
END;

CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content, original_message)
    VALUES ('delete', old.rowid, old.content, old.original_message);
END;
"""

_MIGRATION_SQL = """
ALTER TABLE memories ADD COLUMN namespace TEXT NOT NULL DEFAULT 'default';
"""

_CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace);
"""

_TIER_TTL = {
    1: timedelta(hours=24),
    2: timedelta(days=90),
    3: timedelta(days=365),
    4: None,
}


def _content_hash(content: str, entry_type: str) -> str:
    return hashlib.sha256(f"{entry_type}:{content}".encode()).hexdigest()[:16]


def _default_db_path() -> str:
    home = os.path.expanduser("~")
    carrymem_dir = os.path.join(home, ".carrymem")
    os.makedirs(carrymem_dir, exist_ok=True)
    return os.path.join(carrymem_dir, "memories.db")


class SQLiteAdapter(StorageAdapter):
    """SQLite-based storage adapter — CarryMem's default backend.

    Usage:
        adapter = SQLiteAdapter()  # auto-creates ~/.carrymem/memories.db
        adapter = SQLiteAdapter(":memory:")  # in-memory for testing
        adapter = SQLiteAdapter("/path/to/custom.db")  # custom path
        adapter = SQLiteAdapter(namespace="project-alpha")  # namespace isolation
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        namespace: str = "default",
        enable_semantic_recall: bool = True,
        semantic_config: Optional[Dict[str, Any]] = None,
    ):
        self._namespace = namespace
        self._db_path = db_path or _default_db_path()
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()
        self._migrate_namespace()

        # v0.4.0: Initialize semantic recall components
        self._enable_semantic = enable_semantic_recall and SEMANTIC_AVAILABLE
        self._expander = None
        self._merger = None

        if self._enable_semantic:
            config = semantic_config or {}
            try:
                self._expander = SemanticExpander(
                    custom_synonym_files=config.get("custom_synonym_files"),
                    enable_spell_correction=config.get("enable_spell_correction", True),
                    max_expansions=config.get("max_expansions", 50),
                    edit_distance_threshold=config.get("edit_distance_threshold", 2),
                )
                self._merger = ResultMerger(
                    min_relevance=config.get("min_relevance", 0.3),
                )
            except Exception as e:
                self._enable_semantic = False
                from memory_classification_engine.utils.logger import logger
                logger.warning(f"Semantic recall initialization failed: {e}")

    def _init_schema(self):
        self._conn.executescript(_SCHEMA_SQL)
        self._conn.commit()
        self._migrate_fts_tokenizer()

    def _migrate_namespace(self):
        try:
            self._conn.execute("SELECT namespace FROM memories LIMIT 1")
        except sqlite3.OperationalError:
            self._conn.executescript(_MIGRATION_SQL)
            self._conn.executescript(_CREATE_INDEX_SQL)
            self._conn.commit()

    def _migrate_fts_tokenizer(self):
        try:
            row = self._conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='memories_fts'"
            ).fetchone()
            if row and 'unicode61' in (row[0] or ''):
                self._conn.execute("INSERT INTO memories_fts(memories_fts) VALUES('rebuild')")
                self._conn.commit()
        except sqlite3.OperationalError:
            pass

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def name(self) -> str:
        return "sqlite"

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "vector_search": False,
            "fts": True,
            "ttl": True,
            "batch": True,
            "graph": False,
            "semantic_recall": self._enable_semantic,  # v0.4.0
        }

    @property
    def semantic_enabled(self) -> bool:
        """v0.4.0: Return whether semantic recall is enabled."""
        return self._enable_semantic

    @property
    def expander(self):
        """v0.4.0: Return the SemanticExpander instance (for custom synonym management)."""
        return self._expander

    def enable_semantic_recall(self, enabled: bool = True):
        """v0.4.0: Enable or disable semantic recall at runtime."""
        self._enable_semantic = enabled and SEMANTIC_AVAILABLE and (self._expander is not None)

    def remember(self, entry: MemoryEntry, _skip_commit: bool = False) -> StoredMemory:
        with self._lock:
            return self._remember_impl(entry, _skip_commit)

    def _remember_impl(self, entry: MemoryEntry, _skip_commit: bool = False) -> StoredMemory:
        c_hash = _content_hash(entry.content, entry.type)

        existing = self._conn.execute(
            "SELECT storage_key FROM memories WHERE content_hash = ? AND namespace = ?",
            (c_hash, self._namespace),
        ).fetchone()
        if existing:
            stored = self._row_to_stored(
                self._conn.execute(
                    "SELECT * FROM memories WHERE content_hash = ? AND namespace = ?",
                    (c_hash, self._namespace),
                ).fetchone()
            )
            return stored

        storage_key = f"cm_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{c_hash[:8]}"
        now = datetime.now(timezone.utc)

        ttl = _TIER_TTL.get(entry.tier)
        expires_at = (now + ttl).isoformat() if ttl else None

        metadata_json = json.dumps(entry.metadata) if entry.metadata else "{}"
        recall_hint_json = json.dumps(entry.recall_hint) if entry.recall_hint else None
        original_message = entry.metadata.get("original_message", "") if entry.metadata else ""

        self._conn.execute(
            """INSERT INTO memories
               (id, type, content, original_message, confidence, tier,
                source_layer, reasoning, suggested_action, recall_hint,
                metadata, storage_key, namespace, created_at, updated_at, expires_at,
                access_count, content_hash)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)""",
            (
                entry.id or storage_key,
                entry.type,
                entry.content,
                original_message,
                entry.confidence,
                entry.tier,
                entry.source_layer,
                entry.reasoning,
                entry.suggested_action,
                recall_hint_json,
                metadata_json,
                storage_key,
                self._namespace,
                now.isoformat(),
                now.isoformat(),
                expires_at,
                c_hash,
            ),
        )
        if not _skip_commit:
            self._conn.commit()

        return StoredMemory.from_memory_entry(entry, storage_key=storage_key, created_at=now)

    def remember_batch(self, entries: List[MemoryEntry]) -> List[StoredMemory]:
        with self._lock:
            results = []
            try:
                self._conn.execute("BEGIN")
                for entry in entries:
                    result = self._remember_impl(entry, _skip_commit=True)
                    results.append(result)
                self._conn.commit()
            except Exception as e:
                self._conn.rollback()
                from memory_classification_engine.utils.logger import logger
                logger.warning(f"Batch remember failed, rolled back: {e}")
                raise
            return results

    _ALLOWED_FILTER_KEYS = {"type", "tier", "confidence_min", "created_after"}
    _VALID_MEMORY_TYPES = {
        "user_preference", "correction", "fact_declaration",
        "decision", "relationship", "task_pattern", "sentiment_marker",
    }

    def recall(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        namespaces: Optional[List[str]] = None,
    ) -> List[StoredMemory]:
        with self._lock:
            return self._recall_impl(query, filters, limit, namespaces)

    def _recall_impl(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        namespaces: Optional[List[str]] = None,
    ):
        filters = filters or {}

        for key in filters:
            if key not in self._ALLOWED_FILTER_KEYS:
                raise ValueError(
                    f"Invalid filter key: '{key}'. "
                    f"Allowed keys: {self._ALLOWED_FILTER_KEYS}"
                )

        if filters.get("type") and filters["type"] not in self._VALID_MEMORY_TYPES:
            raise ValueError(
                f"Invalid memory type: '{filters['type']}'. "
                f"Valid types: {self._VALID_MEMORY_TYPES}"
            )

        if limit < 0 or limit > 100000:
            raise ValueError(f"Limit must be between 0 and 100000, got {limit}")

        if namespaces:
            for ns in namespaces:
                if not ns or not isinstance(ns, str) or len(ns) > 128:
                    raise ValueError(
                        f"Invalid namespace: '{ns}'. "
                        "Must be non-empty string, max 128 chars."
                    )

        if query and len(query) > 10000:
            raise ValueError(f"Query too long: {len(query)} chars (max 10000)")

        ns = namespaces or [self._namespace]
        placeholders = ",".join(["?"] * len(ns))
        conditions = [f"namespace IN ({placeholders})"]
        params = list(ns)

        if filters.get("type"):
            conditions.append("type = ?")
            params.append(filters["type"])

        if filters.get("tier") is not None:
            conditions.append("tier = ?")
            params.append(filters["tier"])

        if filters.get("confidence_min") is not None:
            conditions.append("confidence >= ?")
            params.append(filters["confidence_min"])

        if filters.get("created_after"):
            conditions.append("created_at >= ?")
            params.append(filters["created_after"])

        where_clause = "WHERE " + " AND ".join(conditions)

        if query and query.strip():
            # Phase 1: Original FTS5 / LIKE search
            rows = self._fts_search(query, where_clause, params, limit)

            if not rows and self._has_cjk(query):
                rows = self._like_search(query, where_clause, params, limit)

            # Phase 2 (v0.4.0): Semantic expansion if results insufficient
            if self._enable_semantic and len(rows) < limit and self._expander and self._merger:
                original_results = [self._row_to_stored(r) for r in rows if r]
                expanded_rows = self._semantic_recall(query, where_clause, params, limit)
                expanded_results = [self._row_to_stored(r) for r in expanded_rows if r]

                # Only use semantic results if we got new matches
                if expanded_results:
                    merged = self._merger.merge(
                        original_results=original_results,
                        expanded_results=expanded_results,
                        query=query,
                        limit=limit,
                        source="synonym",
                    )
                    # Convert merged dicts back to StoredMemory objects
                    final_results = []
                    for item in merged:
                        if isinstance(item, StoredMemory):
                            final_results.append(item)
                        elif isinstance(item, dict):
                            stored = self._dict_to_stored(item)
                            if stored:
                                final_results.append(stored)

                    # Update access counts and return
                    seen_keys = set()
                    results = []
                    for stored in final_results:
                        if stored.storage_key not in seen_keys:
                            seen_keys.add(stored.storage_key)
                            self._conn.execute(
                                "UPDATE memories SET access_count = access_count + 1 WHERE storage_key = ?",
                                (stored.storage_key,),
                            )
                            results.append(stored)
                    self._conn.commit()
                    return results
        else:
            sql = f"""
                SELECT * FROM memories
                {where_clause}
                ORDER BY confidence DESC
                LIMIT ?
            """
            params.append(limit)
            rows = self._conn.execute(sql, params).fetchall()

        results = []
        seen_keys = set()
        for row in rows:
            stored = self._row_to_stored(row)
            if stored and stored.storage_key not in seen_keys:
                seen_keys.add(stored.storage_key)
                self._conn.execute(
                    "UPDATE memories SET access_count = access_count + 1 WHERE storage_key = ?",
                    (stored.storage_key,),
                )
                results.append(stored)
        self._conn.commit()

        return results

    def _semantic_recall(self, query: str, where_clause: str, params: List, limit: int):
        """v0.4.0: Perform semantic expansion search.

        Expands query using synonym graph, spell correction, cross-language mapping,
        then re-searches FTS5 with expanded terms.
        """
        if not self._expander:
            return []

        try:
            expansions = self._expander.expand(query)

            all_expanded_rows = []
            seen_row_ids = set()

            for exp_query in expansions[1:]:  # Skip original query (already searched)
                if not exp_query or not exp_query.strip():
                    continue

                exp_rows = self._fts_search(exp_query, where_clause, params, limit)

                for row in exp_rows:
                    row_id = row["id"] if hasattr(row, "__getitem__") else None
                    if row_id and row_id not in seen_row_ids:
                        seen_row_ids.add(row_id)
                        all_expanded_rows.append(row)

                # Also try LIKE for CJK expanded queries
                if self._has_cjk(exp_query) and len(all_expanded_rows) < limit:
                    like_rows = self._like_search(exp_query, where_clause, params, limit)
                    for row in like_rows:
                        row_id = row["id"] if hasattr(row, "__getitem__") else None
                        if row_id and row_id not in seen_row_ids:
                            seen_row_ids.add(row_id)
                            all_expanded_rows.append(row)

            return all_expanded_rows[:limit]

        except Exception as e:
            from memory_classification_engine.utils.logger import logger
            logger.warning(f"Semantic recall search failed: {e}")
            return []

    def _has_cjk(self, text: str) -> bool:
        return any(
            "\u4e00" <= char <= "\u9fff"
            or "\u3040" <= char <= "\u309f"
            or "\u30a0" <= char <= "\u30ff"
            for char in text
        )

    def _fts_search(self, query, where_clause, params, limit):
        try:
            fts_sql = f"""
                SELECT m.* FROM memories m
                JOIN memories_fts f ON m.rowid = f.rowid
                {where_clause}
                AND m.rowid IN (
                    SELECT rowid FROM memories_fts WHERE memories_fts MATCH ?
                )
                ORDER BY m.confidence DESC
                LIMIT ?
            """
            params_with_query = params + [query, limit]
            return self._conn.execute(fts_sql, params_with_query).fetchall()
        except sqlite3.OperationalError:
            return []

    def _like_search(self, query, where_clause, params, limit):
        escaped = _escape_like(query)
        like_clause = " AND (content LIKE ? ESCAPE '\\' OR original_message LIKE ? ESCAPE '\\')"
        like_params = [f"%{escaped}%", f"%{escaped}%"]
        sql = f"""
            SELECT * FROM memories
            {where_clause}
            {like_clause}
            ORDER BY confidence DESC
            LIMIT ?
        """
        all_params = params + like_params + [limit]
        return self._conn.execute(sql, all_params).fetchall()

    def forget(self, storage_key: str) -> bool:
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM memories WHERE storage_key = ? AND namespace = ?",
                (storage_key, self._namespace),
            )
            self._conn.commit()
            return cursor.rowcount > 0

    def forget_expired(self) -> int:
        with self._lock:
            now = datetime.now(timezone.utc).isoformat()
            cursor = self._conn.execute(
                "DELETE FROM memories WHERE namespace = ? AND expires_at IS NOT NULL AND expires_at < ?",
                (self._namespace, now),
            )
            self._conn.commit()
            return cursor.rowcount

    def get_stats(self) -> Dict[str, Any]:
        total = self._conn.execute(
            "SELECT COUNT(*) FROM memories WHERE namespace = ?",
            (self._namespace,),
        ).fetchone()[0]
        by_type_rows = self._conn.execute(
            "SELECT type, COUNT(*) as cnt FROM memories WHERE namespace = ? GROUP BY type",
            (self._namespace,),
        ).fetchall()
        by_type = {row["type"]: row["cnt"] for row in by_type_rows}

        return {
            "adapter": self.name,
            "namespace": self._namespace,
            "total_count": total,
            "by_type": by_type,
            "capabilities": self.capabilities,
            "db_path": self._db_path,
        }

    def get_profile(self) -> Dict[str, Any]:
        total = self._conn.execute(
            "SELECT COUNT(*) FROM memories WHERE namespace = ?",
            (self._namespace,),
        ).fetchone()[0]

        if total == 0:
            return {
                "summary": "No memories yet",
                "total_memories": 0,
                "highlights": {},
                "stats": {"by_type": {}, "by_tier": {}, "confidence_avg": 0.0},
                "namespace": self._namespace,
                "last_updated": None,
            }

        by_type_rows = self._conn.execute(
            "SELECT type, COUNT(*) as cnt FROM memories WHERE namespace = ? GROUP BY type",
            (self._namespace,),
        ).fetchall()
        by_type = {row["type"]: row["cnt"] for row in by_type_rows}

        by_tier_rows = self._conn.execute(
            "SELECT tier, COUNT(*) as cnt FROM memories WHERE namespace = ? GROUP BY tier",
            (self._namespace,),
        ).fetchall()
        by_tier = {str(row["tier"]): row["cnt"] for row in by_tier_rows}

        avg_conf = self._conn.execute(
            "SELECT AVG(confidence) FROM memories WHERE namespace = ?",
            (self._namespace,),
        ).fetchone()[0] or 0.0

        highlight_types = [
            "user_preference",
            "correction",
            "decision",
            "fact_declaration",
        ]
        highlights: Dict[str, List[str]] = {}
        for mem_type in highlight_types:
            rows = self._conn.execute(
                "SELECT content FROM memories WHERE namespace = ? AND type = ? ORDER BY confidence DESC LIMIT 5",
                (self._namespace, mem_type),
            ).fetchall()
            items = [row["content"][:100] for row in rows]
            if items:
                highlights[mem_type] = items

        last_updated_row = self._conn.execute(
            "SELECT MAX(updated_at) FROM memories WHERE namespace = ?",
            (self._namespace,),
        ).fetchone()
        last_updated = last_updated_row[0] if last_updated_row else None

        type_parts = []
        type_labels = {
            "user_preference": "偏好",
            "correction": "纠正",
            "decision": "决策",
            "fact_declaration": "事实",
            "relationship": "关系",
            "task_pattern": "任务模式",
            "sentiment_marker": "情感",
        }
        for t, cnt in by_type.items():
            label = type_labels.get(t, t)
            type_parts.append(f"{cnt}个{label}")

        summary = f"AI 记住了关于你的 {total} 条信息：" + "、".join(type_parts)

        return {
            "summary": summary,
            "total_memories": total,
            "highlights": highlights,
            "stats": {
                "by_type": by_type,
                "by_tier": by_tier,
                "confidence_avg": round(avg_conf, 4),
            },
            "namespace": self._namespace,
            "last_updated": last_updated,
        }

    def _row_to_stored(self, row: Optional[sqlite3.Row]) -> Optional[StoredMemory]:
        if not row:
            return None

        metadata = {}
        if row["metadata"]:
            try:
                metadata = json.loads(row["metadata"])
            except (json.JSONDecodeError, TypeError):
                metadata = {}

        recall_hint = None
        if row["recall_hint"]:
            try:
                recall_hint = json.loads(row["recall_hint"])
            except (json.JSONDecodeError, TypeError):
                recall_hint = None

        expires_at = None
        if row["expires_at"]:
            try:
                expires_at = datetime.fromisoformat(row["expires_at"])
            except (ValueError, TypeError):
                expires_at = None

        created_at = None
        if row["created_at"]:
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except (ValueError, TypeError):
                created_at = None

        updated_at = None
        if row["updated_at"]:
            try:
                updated_at = datetime.fromisoformat(row["updated_at"])
            except (ValueError, TypeError):
                updated_at = None

        return StoredMemory(
            id=row["id"],
            type=row["type"],
            content=row["content"],
            confidence=row["confidence"],
            tier=row["tier"],
            source_layer=row["source_layer"] or "unknown",
            reasoning=row["reasoning"] or "",
            suggested_action=row["suggested_action"] or "store",
            recall_hint=recall_hint,
            metadata=metadata,
            storage_key=row["storage_key"],
            created_at=created_at,
            updated_at=updated_at,
            expires_at=expires_at,
            access_count=row["access_count"] or 0,
        )

    def _dict_to_stored(self, d: Dict) -> Optional[StoredMemory]:
        """v0.4.0: Convert a dict back to StoredMemory (for merged results)."""
        if not d or not isinstance(d, dict):
            return None

        try:
            metadata = {}
            if d.get("metadata"):
                if isinstance(d["metadata"], str):
                    metadata = json.loads(d["metadata"])
                elif isinstance(d["metadata"], dict):
                    metadata = d["metadata"]

            recall_hint = None
            if d.get("recall_hint"):
                if isinstance(d["recall_hint"], str):
                    recall_hint = json.loads(d["recall_hint"])
                else:
                    recall_hint = d["recall_hint"]

            expires_at = None
            if d.get("expires_at"):
                if isinstance(d["expires_at"], str):
                    expires_at = datetime.fromisoformat(d["expires_at"])
                else:
                    expires_at = d["expires_at"]

            created_at = None
            if d.get("created_at"):
                if isinstance(d["created_at"], str):
                    created_at = datetime.fromisoformat(d["created_at"])
                else:
                    created_at = d["created_at"]

            updated_at = None
            if d.get("updated_at"):
                if isinstance(d["updated_at"], str):
                    updated_at = datetime.fromisoformat(d["updated_at"])
                else:
                    updated_at = d["updated_at"]

            return StoredMemory(
                id=d.get("id"),
                type=d.get("type", "unknown"),
                content=d.get("content", ""),
                confidence=d.get("confidence", 0.0),
                tier=d.get("tier", 2),
                source_layer=d.get("source_layer", "unknown"),
                reasoning=d.get("reasoning", ""),
                suggested_action=d.get("suggested_action", "store"),
                recall_hint=recall_hint,
                metadata=metadata,
                storage_key=d.get("storage_key"),
                created_at=created_at,
                updated_at=updated_at,
                expires_at=expires_at,
                access_count=d.get("access_count", 0),
            )
        except Exception as e:
            from memory_classification_engine.utils.logger import logger
            logger.debug(f"Failed to convert dict to StoredMemory: {e}")
            return None

    def close(self):
        if self._conn:
            self._conn.close()

    def __del__(self):
        self.close()
