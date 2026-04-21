"""Obsidian Knowledge Adapter — CarryMem's knowledge base integration.

Reads Markdown files from an Obsidian vault, indexes them with FTS5,
and provides full-text search for retrieval.

Features:
- Direct Markdown file reading (no Obsidian API dependency)
- YAML frontmatter tag extraction
- FTS5 full-text search index
- Incremental indexing (only re-index changed files)
- Wiki-link extraction for relationship mapping
"""

import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .base import StorageAdapter


_OBSIDIAN_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    file_path TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    wiki_links TEXT,
    frontmatter TEXT,
    file_modified TEXT,
    content_hash TEXT NOT NULL,
    indexed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
    title,
    content,
    content='notes',
    content_rowid='rowid',
    tokenize='unicode61'
);

CREATE INDEX IF NOT EXISTS idx_notes_tags ON notes(tags);
CREATE INDEX IF NOT EXISTS idx_notes_file_path ON notes(file_path);
CREATE INDEX IF NOT EXISTS idx_notes_content_hash ON notes(content_hash);

CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, title, content)
    VALUES (new.rowid, new.title, new.content);
END;

CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, title, content)
    VALUES ('delete', old.rowid, old.title, old.content);
END;
"""

_FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
_WIKI_LINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
_TAG_RE = re.compile(r'(?:^|\s)#([a-zA-Z0-9_\-/]+)')


def _parse_frontmatter(content: str) -> Dict[str, Any]:
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}

    raw = match.group(1).strip()
    result: Dict[str, Any] = {}

    for line in raw.split('\n'):
        line = line.strip()
        if ':' not in line:
            continue
        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()

        if value.startswith('[') and value.endswith(']'):
            items = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
            result[key] = [i for i in items if i]
        elif value.lower() in ('true', 'false'):
            result[key] = value.lower() == 'true'
        elif value.isdigit():
            result[key] = int(value)
        else:
            result[key] = value.strip('"\'')

    return result


def _extract_tags(content: str, frontmatter: Dict[str, Any]) -> List[str]:
    tags = set()

    fm_tags = frontmatter.get('tags', [])
    if isinstance(fm_tags, list):
        tags.update(fm_tags)
    elif isinstance(fm_tags, str):
        tags.add(fm_tags)

    for match in _TAG_RE.finditer(content):
        tags.add(match.group(1))

    return sorted(tags)


def _extract_wiki_links(content: str) -> List[str]:
    return sorted(set(m.group(1).strip() for m in _WIKI_LINK_RE.finditer(content)))


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]


class ObsidianAdapter(StorageAdapter):
    """Obsidian vault knowledge adapter.

    Reads Markdown files from a vault directory, indexes them with FTS5,
    and provides full-text search. Does NOT modify vault files.

    Usage:
        adapter = ObsidianAdapter("/path/to/obsidian/vault")
        adapter.index_vault()
        results = adapter.recall("Python")
    """

    def __init__(self, vault_path: str, db_path: Optional[str] = None):
        self._vault_path = Path(vault_path).expanduser().resolve()

        if not self._vault_path.exists():
            raise FileNotFoundError(f"Obsidian vault not found: {self._vault_path}")

        if db_path is None:
            carrymem_dir = Path.home() / ".carrymem"
            carrymem_dir.mkdir(exist_ok=True)
            vault_hash = hashlib.md5(str(self._vault_path).encode()).hexdigest()[:8]
            db_path = str(carrymem_dir / f"obsidian_{vault_hash}.db")

        self._db_path = db_path
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._init_schema()

    def _init_schema(self):
        self._conn.executescript(_OBSIDIAN_SCHEMA_SQL)
        self._conn.commit()

    @property
    def name(self) -> str:
        return "obsidian"

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "vector_search": False,
            "fts": True,
            "ttl": False,
            "batch": True,
            "graph": True,
            "wiki_links": True,
            "frontmatter": True,
        }

    @property
    def vault_path(self) -> str:
        return str(self._vault_path)

    def index_vault(self) -> Dict[str, int]:
        md_files = list(self._vault_path.rglob("*.md"))
        new_count = 0
        updated_count = 0
        skipped_count = 0

        for md_file in md_files:
            if md_file.name.startswith("."):
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                skipped_count += 1
                continue

            c_hash = _content_hash(content)

            existing = self._conn.execute(
                "SELECT content_hash FROM notes WHERE file_path = ?",
                (str(md_file.relative_to(self._vault_path)),),
            ).fetchone()

            if existing and existing["content_hash"] == c_hash:
                skipped_count += 1
                continue

            title = md_file.stem
            frontmatter = _parse_frontmatter(content)
            tags = _extract_tags(content, frontmatter)
            wiki_links = _extract_wiki_links(content)

            body = content
            fm_match = _FRONTMATTER_RE.match(content)
            if fm_match:
                body = content[fm_match.end():]

            note_id = f"obs_{c_hash[:8]}_{title[:30].replace(' ', '_')}"

            if existing:
                self._conn.execute(
                    """UPDATE notes SET title=?, content=?, tags=?, wiki_links=?,
                       frontmatter=?, file_modified=?, content_hash=?, indexed_at=?
                       WHERE file_path=?""",
                    (
                        title, body, json.dumps(tags), json.dumps(wiki_links),
                        json.dumps(frontmatter),
                        datetime.fromtimestamp(md_file.stat().st_mtime).isoformat(),
                        c_hash, datetime.utcnow().isoformat(),
                        str(md_file.relative_to(self._vault_path)),
                    ),
                )
                updated_count += 1
            else:
                self._conn.execute(
                    """INSERT INTO notes (id, title, file_path, content, tags,
                       wiki_links, frontmatter, file_modified, content_hash, indexed_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        note_id, title,
                        str(md_file.relative_to(self._vault_path)),
                        body, json.dumps(tags), json.dumps(wiki_links),
                        json.dumps(frontmatter),
                        datetime.fromtimestamp(md_file.stat().st_mtime).isoformat(),
                        c_hash, datetime.utcnow().isoformat(),
                    ),
                )
                new_count += 1

        self._conn.commit()

        return {
            "total_files": len(md_files),
            "new": new_count,
            "updated": updated_count,
            "skipped": skipped_count,
        }

    def remember(self, entry) -> Any:
        raise NotImplementedError(
            "ObsidianAdapter is read-only. Use SQLiteAdapter for storing memories."
        )

    def remember_batch(self, entries: list) -> list:
        raise NotImplementedError(
            "ObsidianAdapter is read-only. Use SQLiteAdapter for storing memories."
        )

    def recall(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
    ) -> list:
        filters = filters or {}

        if query and query.strip():
            results = self._fts_search(query, filters, limit)
        else:
            results = self._filtered_search(filters, limit)

        return results

    def _fts_search(self, query: str, filters: Dict[str, Any], limit: int) -> list:
        conditions = []
        params = []

        if filters.get("tags"):
            tag_list = filters["tags"] if isinstance(filters["tags"], list) else [filters["tags"]]
            for tag in tag_list:
                conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')

        where_clause = ""
        if conditions:
            where_clause = "AND " + " AND ".join(conditions)

        sql = f"""
            SELECT n.* FROM notes n
            JOIN notes_fts f ON n.rowid = f.rowid
            WHERE n.rowid IN (
                SELECT rowid FROM notes_fts WHERE notes_fts MATCH ?
            )
            {where_clause}
            ORDER BY rank
            LIMIT ?
        """
        params_with_query = [query] + params + [limit]
        rows = self._conn.execute(sql, params_with_query).fetchall()

        return [self._row_to_dict(row) for row in rows]

    def _filtered_search(self, filters: Dict[str, Any], limit: int) -> list:
        conditions = []
        params = []

        if filters.get("tags"):
            tag_list = filters["tags"] if isinstance(filters["tags"], list) else [filters["tags"]]
            for tag in tag_list:
                conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')

        if filters.get("title"):
            conditions.append("title LIKE ?")
            params.append(f'%{filters["title"]}%')

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"SELECT * FROM notes {where_clause} ORDER BY indexed_at DESC LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()

        return [self._row_to_dict(row) for row in rows]

    def forget(self, storage_key: str) -> bool:
        raise NotImplementedError(
            "ObsidianAdapter is read-only. Delete notes from your vault directly."
        )

    def get_stats(self) -> Dict[str, Any]:
        total = self._conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        tag_rows = self._conn.execute(
            "SELECT tags FROM notes WHERE tags IS NOT NULL AND tags != '[]'"
        ).fetchall()

        all_tags: Dict[str, int] = {}
        for row in tag_rows:
            try:
                tags = json.loads(row["tags"])
                for tag in tags:
                    all_tags[tag] = all_tags.get(tag, 0) + 1
            except (json.JSONDecodeError, TypeError):
                pass

        return {
            "adapter": self.name,
            "vault_path": str(self._vault_path),
            "total_notes": total,
            "unique_tags": len(all_tags),
            "top_tags": dict(sorted(all_tags.items(), key=lambda x: -x[1])[:10]),
            "capabilities": self.capabilities,
        }

    def get_tags(self) -> Dict[str, int]:
        tag_rows = self._conn.execute(
            "SELECT tags FROM notes WHERE tags IS NOT NULL AND tags != '[]'"
        ).fetchall()

        all_tags: Dict[str, int] = {}
        for row in tag_rows:
            try:
                tags = json.loads(row["tags"])
                for tag in tags:
                    all_tags[tag] = all_tags.get(tag, 0) + 1
            except (json.JSONDecodeError, TypeError):
                pass

        return dict(sorted(all_tags.items(), key=lambda x: -x[1]))

    def get_linked_notes(self, note_title: str) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM notes WHERE wiki_links LIKE ?",
            (f'%"{note_title}"%',),
        ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        tags = []
        if row["tags"]:
            try:
                tags = json.loads(row["tags"])
            except (json.JSONDecodeError, TypeError):
                pass

        wiki_links = []
        if row["wiki_links"]:
            try:
                wiki_links = json.loads(row["wiki_links"])
            except (json.JSONDecodeError, TypeError):
                pass

        frontmatter = {}
        if row["frontmatter"]:
            try:
                frontmatter = json.loads(row["frontmatter"])
            except (json.JSONDecodeError, TypeError):
                pass

        return {
            "id": row["id"],
            "type": "knowledge_note",
            "title": row["title"],
            "content": row["content"][:500] + "..." if len(row["content"]) > 500 else row["content"],
            "file_path": row["file_path"],
            "tags": tags,
            "wiki_links": wiki_links,
            "frontmatter": frontmatter,
            "source": "obsidian",
            "confidence": 1.0,
        }

    def close(self):
        if self._conn:
            self._conn.close()

    def __del__(self):
        self.close()
