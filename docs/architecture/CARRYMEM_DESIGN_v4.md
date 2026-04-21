# CarryMem v0.5 设计文档 (v1.0)

**日期**: 2026-04-20
**版本**: v1.0 (对应 CarryMem v0.5~v0.6)
**参考**: CARRYMEM_ARCHITECTURE_v4.md, CARRYMEM_USER_STORIES.md

---

## 1. CarryMem 主类设计

### 1.1 类接口

```python
class CarryMem:
    """CarryMem — 随身记忆库的主入口。

    使用方式:
        # 模式1: 分类+存储 (默认 SQLite)
        cm = CarryMem()
        result = cm.classify_and_remember("I prefer dark mode")

        # 模式2: 纯分类 (无存储)
        cm = CarryMem(storage=None)
        result = cm.classify_message("I prefer dark mode")

        # 模式3: 自定义存储
        from carrymem.adapters import SupermemoryAdapter
        cm = CarryMem(storage=SupermemoryAdapter(api_key="..."))
    """

    def __init__(
        self,
        storage: Optional[StorageAdapter] = "sqlite",
        db_path: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        """
        Args:
            storage: 存储适配器实例。
                     - "sqlite" (默认): 自动创建 SQLiteAdapter
                     - None: 纯分类模式，不存储
                     - StorageAdapter 实例: 使用自定义适配器
            db_path: SQLite 数据库路径 (仅 storage="sqlite" 时有效)
                     默认: ~/.carrymem/memories.db
            config: 引擎配置 (可选)
        """

    def classify_message(
        self,
        message: str,
        context: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """分类单条消息 (纯分类，不存储)。

        Args:
            message: 用户消息内容
            context: 对话上下文 (可选，用于补全确认类消息)
            language: 语言代码 (可选，自动检测)

        Returns:
            {
                "should_remember": True,
                "entries": [MemoryEntry.to_dict(), ...],
                "summary": {"total_entries": 1, "by_type": {...}}
            }
        """

    def classify_and_remember(
        self,
        message: str,
        context: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """分类+存储一键完成。

        等价于: classify_message() → adapter.remember()

        Returns:
            {
                "should_remember": True,
                "entries": [StoredMemory.to_dict(), ...],
                "stored": True,
                "storage_keys": ["mce_20260420_001", ...]
            }

        Raises:
            StorageNotConfiguredError: 未配置存储适配器时
        """

    def recall_memories(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """检索记忆。

        Args:
            query: 搜索关键词 (可选)
            filters: 过滤条件 (可选)
                     - type: 记忆类型 (如 "user_preference")
                     - tier: 存储层级 (1-4)
                     - confidence_min: 最低置信度
                     - created_after: ISO 时间戳
            limit: 最大返回数量

        Returns:
            List[StoredMemory.to_dict()]

        Raises:
            StorageNotConfiguredError: 未配置存储适配器时
        """

    def forget_memory(self, memory_id: str) -> bool:
        """删除记忆。

        Args:
            memory_id: 记忆 ID (storage_key)

        Returns:
            True if deleted, False if not found

        Raises:
            StorageNotConfiguredError: 未配置存储适配器时
        """
```

### 1.2 错误类型

```python
class CarryMemError(Exception):
    """CarryMem 基础异常"""

class StorageNotConfiguredError(CarryMemError):
    """未配置存储适配器时调用存储相关方法"""
    def __init__(self):
        super().__init__(
            "Storage adapter not configured. "
            "Use CarryMem(storage='sqlite') or CarryMem(storage=YourAdapter()) "
            "to enable storage features."
        )

class ClassificationError(CarryMemError):
    """分类过程中的错误"""

class AdapterError(CarryMemError):
    """存储适配器操作错误"""
```

---

## 2. SQLite 适配器设计

### 2.1 数据库 Schema

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
    recall_hint TEXT,  -- JSON, v0.6+: null
    metadata TEXT,     -- JSON

    -- 存储元数据
    storage_key TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT,
    access_count INTEGER NOT NULL DEFAULT 0,

    -- 去重
    content_hash TEXT NOT NULL
);

-- FTS5 全文搜索
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content,
    original_message,
    content='memories',
    content_rowid='rowid',
    tokenize='unicode61'
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_tier ON memories(tier);
CREATE INDEX IF NOT EXISTS idx_memories_confidence ON memories(confidence);
CREATE INDEX IF NOT EXISTS idx_memories_expires ON memories(expires_at);
CREATE INDEX IF NOT EXISTS idx_memories_content_hash ON memories(content_hash);

-- FTS5 同步触发器
CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, content, original_message)
    VALUES (new.rowid, new.content, new.original_message);
END;

CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content, original_message)
    VALUES ('delete', old.rowid, old.content, old.original_message);
END;
```

### 2.2 去重策略

```python
import hashlib

def _content_hash(content: str, type: str) -> str:
    """内容去重哈希。

    同一内容 + 同一类型 = 同一哈希 → 跳过存储。
    同一内容 + 不同类型 = 不同哈希 → 允许存储（多类型）。
    """
    return hashlib.sha256(f"{type}:{content}".encode()).hexdigest()[:16]
```

### 2.3 过期策略

| Tier | 名称 | 默认 TTL | 说明 |
|------|------|---------|------|
| 1 | 感觉记忆 | 24 小时 | 临时信息，快速遗忘 |
| 2 | 程序性记忆 | 90 天 | 习惯/偏好，中期保留 |
| 3 | 情景记忆 | 365 天 | 重要事件，长期保留 |
| 4 | 语义记忆 | 永不过期 | 核心知识，永久保留 |

---

## 3. MCP 工具设计 (3+3 模式)

### 3.1 核心工具 (永远可用)

#### classify_message (不变)

```json
{
    "name": "classify_message",
    "description": "Analyze whether a message contains memorable information. Returns structured MemoryEntry with type, tier, and confidence. CarryMem is a memory classification engine — it decides WHAT to remember, then optionally stores it.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "User message content"},
            "context": {"type": "string", "description": "Conversation context (optional). When user confirms/accepts AI suggestion, pass the previous AI reply to improve decision/correction classification quality (see §8.5.2)."},
            "language": {"type": "string", "description": "Language code (optional, auto-detected)"}
        },
        "required": ["message"]
    }
}
```

#### batch_classify (不变)

#### get_classification_schema (不变)

### 3.2 可选工具 (需 adapter)

#### classify_and_remember (新增)

```json
{
    "name": "classify_and_remember",
    "description": "Classify a message AND store it if worth remembering. One-step operation: classify → store → return. Requires storage adapter to be configured.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "User message content"},
            "context": {"type": "string", "description": "Conversation context (optional)"},
            "language": {"type": "string", "description": "Language code (optional)"}
        },
        "required": ["message"]
    }
}
```

#### recall_memories (新增)

```json
{
    "name": "recall_memories",
    "description": "Retrieve stored memories. Supports filtering by type, tier, and confidence. Supports full-text search. Requires storage adapter.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query (optional)"},
            "filters": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "Memory type filter"},
                    "tier": {"type": "integer", "description": "Tier filter (1-4)"},
                    "confidence_min": {"type": "number", "description": "Minimum confidence threshold"}
                }
            },
            "limit": {"type": "integer", "description": "Max results (default 20)"}
        }
    }
}
```

#### forget_memory (新增)

```json
{
    "name": "forget_memory",
    "description": "Delete a stored memory by ID. Requires storage adapter.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "memory_id": {"type": "string", "description": "Memory ID to delete"}
        },
        "required": ["memory_id"]
    }
}
```

### 3.3 无 adapter 时的行为

```json
{
    "error": "storage_not_configured",
    "message": "Storage adapter not configured. Use CarryMem(storage='sqlite') to enable storage features.",
    "available_tools": ["classify_message", "batch_classify", "get_classification_schema"]
}
```

---

## 4. context 参数增强设计

### 4.1 确认模式检测

```python
CONFIRMATION_PATTERNS = {
    'en': [
        r'^(ok|okay|sure|yes|yeah|yep|got it|sounds good|go ahead|let\'s do it|agreed|fine|right|exactly)$',
        r'^(good|great|perfect|nice|cool|alright|absolutely|definitely)$',
    ],
    'zh': [
        r'^(好的|行|可以|没问题|就这样|同意|确认|对|嗯|是|好的呀|行吧)$',
    ],
    'ja': [
        r'^(はい|いいよ|わかりました|オッケー|OK|そうしよう|賛成)$',
    ],
}
```

### 4.2 内容合并逻辑

```python
def _merge_context(self, message: str, context: str, result: Dict) -> Dict:
    """当检测到用户确认模式时，合并 AI 上下文到 content 字段。"""
    if not context:
        return result

    if not self._is_confirmation(message):
        return result

    for entry in result.get('entries', []):
        if entry.get('type') in ('decision', 'correction'):
            ai_summary = self._summarize(context, max_length=100)
            entry['content'] = f"确认: {ai_summary}"
            entry['metadata']['context_source'] = 'ai_reply'
            entry['metadata']['original_user_message'] = message

    return result
```

---

## 5. 包结构设计

### 5.1 PyPI 包名

```
carrymem/                    ← 主包 (pip install carrymem)
├── __init__.py              ← from carrymem import CarryMem
├── engine.py                ← CarryMem 主类
├── exceptions.py            ← CarryMemError, StorageNotConfiguredError
├── mce/                     ← 引擎内部模块
│   ├── __init__.py
│   ├── engine.py            ← MCE 核心引擎 (现有代码)
│   ├── layers/              ← 三层漏斗
│   ├── coordinators/        ← 分类管线
│   └── utils/               ← 工具函数
├── adapters/                ← 存储适配器
│   ├── __init__.py
│   ├── base.py              ← StorageAdapter ABC
│   ├── sqlite_adapter.py    ← SQLite 默认实现
│   └── ...
├── mcp/                     ← MCP Server
│   ├── server.py
│   ├── handlers.py
│   └── tools.py
└── cli.py                   ← carrymem run / carrymem classify

mce/                         ← 别名包 (pip install mce → 安装 carrymem)
└── __init__.py              ← from mce import * → carrymem.*
```

### 5.2 setup.py / pyproject.toml

```toml
[project]
name = "carrymem"
version = "0.5.0"
description = "CarryMem — 随身记忆库. Let your AI agent remember users."
readme = "README.md"

[project.optional-dependencies]
sqlite = []  # 内置，无需额外依赖
obsidian = []  # v0.7
supermemory = ["httpx"]  # v0.7

[project.scripts]
carrymem = "carrymem.cli:main"

[tool.setuptools.packages.find]
include = ["carrymem*"]
```

---

## 6. 配置设计

### 6.1 默认配置

```yaml
# ~/.carrymem/config.yaml (可选，不配置也能用)
storage:
  adapter: sqlite
  sqlite:
    db_path: ~/.carrymem/memories.db

engine:
  language: auto  # auto / en / zh / ja
  semantic_layer: disabled  # disabled / optional / required

recall:
  default_limit: 20
  confidence_min: 0.5

forgetting:
  tier1_ttl_hours: 24
  tier2_ttl_days: 90
  tier3_ttl_days: 365
  tier4_ttl: null  # 永不过期
  auto_cleanup: true
  cleanup_interval_hours: 24
```

### 6.2 环境变量

```bash
CARRYMEM_STORAGE=sqlite          # 存储适配器
CARRYMEM_DB_PATH=~/.carrymem/memories.db  # SQLite 路径
CARRYMEM_LANGUAGE=auto           # 语言
CARRYMEM_LOG_LEVEL=INFO          # 日志级别
```
