# CarryMem v0.3 设计文档 (v3.0)

**日期**: 2026-04-22
**版本**: v3.0 (对应 CarryMem v0.3.0)
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

        # Mode 6: Plugin adapter
        cm = CarryMem(storage="my_custom_adapter")

        # Mode 7: Full-featured
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
| `build_system_prompt()` | v0.10 | storage or knowledge | 智能调度 Prompt |

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
    namespace TEXT NOT NULL DEFAULT 'default',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT,
    access_count INTEGER NOT NULL DEFAULT 0,
    content_hash TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace);
```

### 2.2 Namespace 隔离策略

```python
adapter = SQLiteAdapter(db_path="memories.db", namespace="project-alpha")
adapter.remember(entry)  # → namespace="project-alpha"
adapter.recall("query")  # → WHERE namespace = 'project-alpha'
adapter.recall("query", namespaces=["project-alpha", "global"])
# → WHERE namespace IN ('project-alpha', 'global')
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

---

## 4. MCP 工具设计 (3+3+3+2+1 模式)

### 4.1 工具分组

```
Core (3):       classify_message, get_classification_schema, batch_classify
Storage (3):    classify_and_remember, recall_memories, forget_memory
Knowledge (3):  index_knowledge, recall_from_knowledge, recall_all
Profile (2):    declare_preference, get_memory_profile
Prompt (1):     get_system_prompt
```

### 4.2 get_system_prompt (v0.10 新增)

```json
{
    "name": "get_system_prompt",
    "description": "Generate a context-aware system prompt with user memories and knowledge base entries. Supports EN/CN/JP languages with memory-first retrieval priority.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "context": {"type": "string", "description": "Current conversation context for relevance filtering"},
            "max_memories": {"type": "integer", "default": 10},
            "max_knowledge": {"type": "integer", "default": 5},
            "language": {"type": "string", "enum": ["en", "zh", "ja"], "default": "en"}
        }
    }
}
```

### 4.3 无适配器时的行为

| 工具组 | 缺失适配器 | 错误 |
|--------|-----------|------|
| Storage 工具 | 无 storage | `storage_not_configured` |
| Knowledge 工具 | 无 knowledge_adapter | `knowledge_not_configured` |
| Profile 工具 | 无 storage | `storage_not_configured` |
| Prompt 工具 | 无 storage | 返回基础 prompt（无记忆） |
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
    "last_updated": "2026-04-22T10:30:00Z"
}
```

**设计原则**：不做 UI，做数据 API

---

## 7. build_system_prompt() 设计 (v0.10)

### 7.1 Prompt 模板结构

```
[语言特定的角色描述]
[检索优先级说明]
  1. User Memories (highest priority)
  2. Knowledge Base
  3. General Knowledge (lowest priority)

## User Memories (if any)
- [Type] content (confidence: XX%)

## Knowledge Base (if any)
- title [tags]: content[:200]

## Guidelines
- Always respect user preferences and corrections
- Corrections override original facts
```

### 7.2 多语言支持

| 语言 | 角色描述 | 优先级标题 | 指导原则 |
|------|---------|-----------|---------|
| EN | "You are an AI assistant with access to the user's memory..." | User Memories / Knowledge Base | "Always respect user preferences..." |
| ZH | "你是一个拥有用户记忆和知识库访问权限的AI助手..." | 用户记忆 / 知识库 | "始终尊重用户的偏好和纠正..." |
| JA | "あなたはユーザーの記憶とナレッジベースにアクセスできるAIアシスタント..." | ユーザー記憶 / ナレッジベース | "ユーザーの好みと訂正を常に尊重..." |

---

## 8. Plugin 适配器加载 (v0.10)

### 8.1 加载策略

```python
def load_adapter(name: str) -> Optional[Type[StorageAdapter]]:
    # 1. Check builtins (sqlite, obsidian)
    # 2. Check entry_points (carrymem.adapters group)
    # 3. Try as fully-qualified class name
```

### 8.2 注册方式

```python
# setup.py of plugin package
setup(
    name="carrymem-redis",
    entry_points={
        "carrymem.adapters": [
            "redis = carrymem_redis:RedisAdapter",
        ]
    },
)
```

---

## 9. 过期策略

| Tier | 名称 | 默认 TTL | 说明 |
|------|------|---------|------|
| 1 | 感觉记忆 | 24 小时 | 临时信息，快速遗忘 |
| 2 | 程序性记忆 | 90 天 | 习惯/偏好，中期保留 |
| 3 | 情景记忆 | 365 天 | 重要事件，长期保留 |
| 4 | 语义记忆 | 永不过期 | 核心知识，永久保留 |
