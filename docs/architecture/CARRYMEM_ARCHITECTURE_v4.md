# CarryMem v0.9 架构文档 (v2.0)

**日期**: 2026-04-21
**版本**: v2.0 (对应 CarryMem v0.7~v0.9)
**参考**: CARRYMEM_USER_STORIES.md, MCP_POSITIONING_CONSENSUS_v3.md

---

## 1. 系统架构总览

```
┌──────────────────────────────────────────────────────────────────┐
│                        AI Agent / IDE / CLI                       │
│                  (Claude Code / Cursor / Custom Agent)            │
└──────────────┬───────────────────────────────────┬───────────────┘
               │ MCP Protocol                      │ Python API
               ▼                                   ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│      MCP Server (3+3+3+2)    │    │     CarryMem Main Class      │
│                              │    │                              │
│  Core (3):                   │    │  classify_message()          │
│    classify_message          │    │  classify_and_remember()     │
│    get_classification_schema │    │  recall_memories()           │
│    batch_classify            │    │  forget_memory()             │
│                              │    │  declare()          ← v0.8   │
│  Storage (3):                │    │  get_memory_profile() ← v0.8 │
│    classify_and_remember     │    │  index_knowledge()   ← v0.7  │
│    recall_memories           │    │  recall_from_knowledge()←v0.7│
│    forget_memory             │    │  recall_all()        ← v0.7  │
│                              │    │                              │
│  Knowledge (3):       ← v0.7│    │  namespace="default" ← v0.9  │
│    index_knowledge           │    └──────────┬───────────────────┘
│    recall_from_knowledge     │               │
│    recall_all                │               │
│                              │               │
│  Profile (2):         ← v0.8│               │
│    declare_preference        │               │
│    get_memory_profile        │               │
└──────────────────────────────┘               │
                                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     MCE Classification Engine                     │
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │
│  │ Layer 1:    │   │ Layer 2:    │   │ Layer 3:    │            │
│  │ Rule Match  │──▶│ Pattern     │──▶│ Semantic    │            │
│  │ (60%+ hit)  │   │ Analysis    │   │ (LLM fallback)│          │
│  │ Zero cost   │   │ (30%+ hit)  │   │ (<10% hit)  │            │
│  └─────────────┘   └─────────────┘   └─────────────┘            │
│                                                                  │
│  + Confirmation Detection (EN/CN/JP) ← v0.5                     │
│  + Context Merge (ai_reply → decision) ← v0.5                   │
└──────────────────────────────────────────────────────────────────┘
                                               │
                                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Storage Adapter Layer                        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ SQLiteAdapter│  │ObsidianAdapter│  │  YourAdapter │           │
│  │ (Default)    │  │ (Read-Only)   │  │  (Custom)    │           │
│  │              │  │  ← v0.7      │  │              │           │
│  │ • FTS5       │  │ • FTS5       │  │              │           │
│  │ • Dedup      │  │ • Frontmatter│  │              │           │
│  │ • TTL        │  │ • Wiki-links │  │              │           │
│  │ • Namespace  │  │ • Incremental│  │              │           │
│  │   ← v0.9    │  │              │  │              │           │
│  └──────┬───────┘  └──────────────┘  └──────────────┘           │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────────────────────────────────┐                    │
│  │         memories table (SQLite)          │                    │
│  │                                          │                    │
│  │  id | type | content | confidence | tier  │                    │
│  │     | namespace | created_at | ...       │                    │
│  └──────────────────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. 数据流

### 2.1 被动分类流 (classify_and_remember)

```
User: "I prefer dark mode"
  → MCE Engine (3-layer funnel)
  → MemoryEntry(type=user_preference, confidence=0.95)
  → SQLiteAdapter.remember() [namespace="default"]
  → Stored in memories table
```

### 2.2 主动声明流 (declare) — v0.8

```
User: "I prefer dark mode" (主动告知)
  → MCE Engine (3-layer funnel, but confidence=1.0)
  → MemoryEntry(type=user_preference, confidence=1.0, source_layer="declaration")
  → SQLiteAdapter.remember() [namespace=current]
  → Stored with source="declaration" in metadata
```

### 2.3 知识库检索流 (recall_from_knowledge) — v0.7

```
User: "Python design patterns"
  → ObsidianAdapter.recall("Python design patterns")
  → FTS5 search in obsidian_index.db
  → Returns: [{title, content, tags, wiki_links}, ...]
```

### 2.4 统一检索流 (recall_all) — v0.7+v0.9

```
User: "Python design patterns"
  → SQLiteAdapter.recall(namespaces=[current, "global"])
  → ObsidianAdapter.recall("Python design patterns")
  → Merge: {memories: [...], knowledge: [...], priority: "memory_first"}
```

### 2.5 记忆画像流 (get_memory_profile) — v0.8

```
User: "What do you remember about me?"
  → SQLiteAdapter.get_profile()
  → SQL aggregation: COUNT by type, AVG confidence, top content
  → Returns: {summary, highlights, stats, namespace, last_updated}
```

---

## 3. 检索优先级策略

```
recall_all(query, namespaces=[...])
  │
  ├─ Layer 1a: 当前 namespace 的记忆 (project-specific)
  │    e.g., namespace="project-alpha" 的 user_preference
  │
  ├─ Layer 1b: 全局 namespace 的记忆 (user-level)
  │    e.g., namespace="global" 的通用偏好和纠正
  │
  ├─ Layer 2:  知识库 (Obsidian)
  │    e.g., Obsidian vault 中的笔记
  │
  └─ Layer 3:  外部 LLM (Agent 自己决定)
       e.g., GPT-4/Claude 生成回答
```

---

## 4. 模块依赖关系

```
carrymem.py (主入口)
  ├── engine.py (MCE 核心引擎)
  ├── adapters/
  │   ├── base.py (StorageAdapter ABC + MemoryEntry + StoredMemory)
  │   ├── sqlite_adapter.py (SQLiteAdapter + FTS5 + Dedup + TTL + Namespace)
  │   └── obsidian_adapter.py (ObsidianAdapter + FTS5 + Frontmatter + Wiki-links)
  ├── utils/
  │   ├── confirmation.py (确认模式检测 EN/CN/JP)
  │   └── ...
  └── integration/
      └── layer2_mcp/
          ├── tools.py (3+3+3+2 工具定义)
          └── handlers.py (工具处理器)
```

---

## 5. 版本演进

| 版本 | 架构变更 | 新增模块 |
|------|---------|---------|
| v0.5 | CarryMem 主类 + context 增强 | carrymem.py, confirmation.py |
| v0.6 | SQLiteAdapter + 3+3 MCP | sqlite_adapter.py |
| v0.7 | ObsidianAdapter + 3+3+3 MCP | obsidian_adapter.py |
| v0.8 | declare() + get_profile() + 3+3+3+2 MCP | base.py get_profile() |
| v0.9 | Namespace 隔离 + 跨 namespace 检索 | sqlite_adapter.py namespace 列 |
