# CarryMem v0.9 设计文档 (v2.0)

**日期**: 2026-04-21
**版本**: v2.0 (对应 CarryMem v0.7~v0.9)
**参考**: CARRYMEM_ARCHITECTURE_v4.md, CARRYMEM_USER_STORIES.md

---

## 1. CarryMem 主类设计

### 1.1 类接口

```python
class CarryMem:
    """CarryMem — 随身记忆库.

    Usage:
        # Mode 1: Classify + Store (default SQLite)
        cm = CarryMem()
        result = cm.classify_and_remember("I prefer dark mode")

        # Mode 2: Pure classification (no storage)
        cm = CarryMem(storage=None)
        result = cm.classify_message("I prefer dark mode")

        # Mode 3: Custom storage adapter
        cm = CarryMem(storage=SQLiteAdapter("/path/to/custom.db"))

        # Mode 4: With knowledge base (Obsidian)
        cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
        cm.index_knowledge()
        results = cm.recall_from_knowledge("Python design patterns")

        # Mode 5: With namespace isolation
        cm = CarryMem(namespace="project-alpha")
        cm.declare("I prefer dark mode")

        # Mode 6: Full-featured
        cm = CarryMem(
            storage="sqlite",
            knowledge_adapter=ObsidianAdapter("/path/to/vault"),
            namespace="project-alpha",
        )
    """

    def __init__(
        self,
        storage: Optional[Any] = "sqlite",
        db_path: Optional[str] = None,
        knowledge_adapter: Optional[StorageAdapter] = None,
        namespace: str = "default",
        config: Optional[Dict] = None,
    ):
        """
        Args:
            storage: 存储适配器。"sqlite"(默认) / None(纯分类) / StorageAdapter实例
            db_path: SQLite 数据库路径 (默认 ~/.carrymem/memories.db)
            knowledge_adapter: 知识库适配器 (如 ObsidianAdapter)
            namespace: 记忆空间隔离 (默认 "default")
            config: 引擎配置 (可选)
        """
```

### 1.2 方法列表

| 方法 | 版本 | 存储要求 | 说明 |
|------|------|---------|------|
| `classify_message()` | v0.5 | 无 | 纯分类，不存储 |
| `classify_and_remember()` | v0.5 | storage | 分类+存储 |
| `recall_memories()` | v0.5 | storage | 检索记忆 |
| `forget_memory()` | v0.5 | storage | 删除记忆 |
| `declare()` | v0.8 | storage | 主动声明，confidence=1.0 |
| `get_memory_profile()` | v0.8 | storage | 记忆画像 |
| `index_knowledge()` | v0.7 | knowledge | 索引知识库 |
| `recall_from_knowledge()` | v0.7 | knowledge | 检索知识库 |
| `recall_all()` | v0.7 | storage or knowledge | 统一检索 |

### 1.3 错误类型

```python
class StorageNotConfiguredError(Exception):
    """未配置存储适配器时调用存储相关方法"""

class KnowledgeNotConfiguredError(Exception):
    """未配置知识库适配器时调用知识库相关方法"""
```

---

## 2. SQLite 适配器设计

### 2.1 数据库 Schema (v0.9)

```sql
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
    namespace TEXT NOT NULL DEFAULT 'default',  -- v0.9 新增
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT,
    access_count INTEGER NOT NULL DEFAULT 0,
    content_hash TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace);  -- v0.9 新增
```

### 2.2 Namespace 隔离策略

```python
# 写入时自动附加 namespace
adapter = SQLiteAdapter(db_path="memories.db", namespace="project-alpha")
adapter.remember(entry)  # → namespace="project-alpha"

# 查询时自动过滤 namespace
adapter.recall("query")  # → WHERE namespace = 'project-alpha'

# 跨 namespace 查询
adapter.recall("query", namespaces=["project-alpha", "global"])
# → WHERE namespace IN ('project-alpha', 'global')

# 删除时只删除当前 namespace
adapter.forget("storage_key")  # → WHERE namespace = 'project-alpha'
```

### 2.3 Schema 迁移

```python
def _migrate_namespace(self):
    """自动检测并添加 namespace 列"""
    try:
        self._conn.execute("SELECT namespace FROM memories LIMIT 1")
    except sqlite3.OperationalError:
        self._conn.executescript("ALTER TABLE memories ADD COLUMN namespace TEXT NOT NULL DEFAULT 'default'")
        self._conn.executescript("CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace)")
        self._conn.commit()
```

---

## 3. Obsidian 适配器设计 (v0.7)

### 3.1 核心特性

| 特性 | 说明 |
|------|------|
| Markdown 直读 | 直接读取 .md 文件，无需 Obsidian API |
| FTS5 全文索引 | 自动建索引，增量更新 |
| YAML frontmatter | 自动提取 tags、自定义字段 |
| Wiki-links | `[[Target Note]]` 关系提取 |
| 只读设计 | remember/forget 抛出 NotImplementedError |
| 增量索引 | 只索引变更文件（基于 mtime） |

### 3.2 索引结构

```sql
-- ~/.carrymem/obsidian_{vault_hash}.db
CREATE TABLE notes (
    path TEXT PRIMARY KEY,
    title TEXT,
    content TEXT,
    frontmatter TEXT,  -- JSON
    tags TEXT,         -- JSON array
    wiki_links TEXT,   -- JSON array
    mtime REAL,
    indexed_at TEXT
);

CREATE VIRTUAL TABLE notes_fts USING fts5(
    title, content, tags,
    content='notes',
    content_rowid='rowid'
);
```

---

## 4. MCP 工具设计 (3+3+3+2 模式)

### 4.1 工具分组

```
Core (3):       classify_message, get_classification_schema, batch_classify
Storage (3):    classify_and_remember, recall_memories, forget_memory
Knowledge (3):  index_knowledge, recall_from_knowledge, recall_all
Profile (2):    declare_preference, get_memory_profile
```

### 4.2 declare_preference (v0.8 新增)

```json
{
    "name": "declare_preference",
    "description": "Let the user proactively tell the AI about themselves. User declarations are classified by the engine but always stored with confidence=1.0 and source_layer='declaration'.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "What the user wants to declare"
            }
        },
        "required": ["message"]
    }
}
```

### 4.3 get_memory_profile (v0.8 新增)

```json
{
    "name": "get_memory_profile",
    "description": "Get a structured summary of what the AI remembers about the user. Returns highlights, statistics, and a human-readable summary.",
    "inputSchema": {
        "type": "object",
        "properties": {}
    }
}
```

### 4.4 无适配器时的行为

| 工具组 | 缺失适配器 | 错误 |
|--------|-----------|------|
| Storage 工具 | 无 storage | `storage_not_configured` |
| Knowledge 工具 | 无 knowledge_adapter | `knowledge_not_configured` |
| Profile 工具 | 无 storage | `storage_not_configured` |
| Core 工具 | 无 | 永远可用 |

---

## 5. declare() vs classify_message() 设计对比

| 维度 | classify_message | declare |
|------|-----------------|---------|
| 来源 | 对话中的被动提取 | 用户主动告知 |
| confidence | 0.3~0.95（引擎判断） | **1.0**（用户说的） |
| suggested_action | store/defer/ignore | **store**（一定存） |
| 噪声过滤 | 经过 _is_noise() | **跳过** |
| source_layer | rule/pattern/semantic | **declaration** |
| 存储保证 | 可能不存（低置信度） | **一定存** |

---

## 6. get_memory_profile() 输出设计

```json
{
    "summary": "AI 记住了关于你的 42 条信息：12个偏好、3个纠正、5个决策",
    "total_memories": 42,
    "highlights": {
        "user_preference": ["dark mode", "PostgreSQL", "camelCase"],
        "correction": ["not MongoDB but PostgreSQL"],
        "decision": ["use SQLite as default", "REST not GraphQL"]
    },
    "stats": {
        "by_type": {"user_preference": 12, "correction": 3, "decision": 5, ...},
        "by_tier": {"2": 20, "3": 15, "4": 7},
        "confidence_avg": 0.87
    },
    "namespace": "default",
    "last_updated": "2026-04-21T10:30:00Z"
}
```

**设计原则**：
- 不做 UI，做数据 API
- highlights 只返回 top 5 条代表性内容
- summary 包含人类可读的中文摘要
- 任何 Agent UI 都可以消费这个 JSON

---

## 7. 过期策略

| Tier | 名称 | 默认 TTL | 说明 |
|------|------|---------|------|
| 1 | 感觉记忆 | 24 小时 | 临时信息，快速遗忘 |
| 2 | 程序性记忆 | 90 天 | 习惯/偏好，中期保留 |
| 3 | 情景记忆 | 365 天 | 重要事件，长期保留 |
| 4 | 语义记忆 | 永不过期 | 核心知识，永久保留 |
