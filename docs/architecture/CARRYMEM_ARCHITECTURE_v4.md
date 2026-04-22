# CarryMem v0.3 架构文档 (v3.0)

**日期**: 2026-04-22
**版本**: v3.0 (对应 CarryMem v0.3.0)
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
│      MCP Server (3+3+3+2+1)  │    │     CarryMem Main Class      │
│                              │    │                              │
│  Core (3):                   │    │  classify_message()          │
│    classify_message          │    │  classify_and_remember()     │
│    get_classification_schema │    │  recall_memories()           │
│    batch_classify            │    │  forget_memory()             │
│                              │    │                              │
│  Storage (3):                │    │  declare()                   │
│    classify_and_remember     │    │  get_memory_profile()        │
│    recall_memories           │    │                              │
│    forget_memory             │    │  index_knowledge()           │
│                              │    │  recall_from_knowledge()     │
│  Knowledge (3):              │    │  recall_all()                │
│    index_knowledge           │    │                              │
│    recall_from_knowledge     │    │  build_system_prompt()       │
│    recall_all                │    │                              │
│                              │    │  namespace="default"         │
│  Profile (2):                │    └──────────┬───────────────────┘
│    declare_preference        │               │
│    get_memory_profile        │               ▼
│                              │    ┌──────────────────────────────┐
│  Prompt (1):                 │    │   MCE Classification Engine   │
│    get_system_prompt         │    │                              │
└──────────────────────────────┘    │  ┌─────────┐┌────────┐┌──────┐ │
                                       │  │Rule Match│Pattern │Semantic│ │
                                       │  │(60%+hit)│(30%+hit)│(<10%) │ │
                                       │  └─────────┴────────┴──────┘ │
                                       │  + Confirmation (EN/CN/JP)  │
                                       └──────────────┬───────────────┘
                                                      │
                                                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Storage Adapter Layer                        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ SQLiteAdapter│  │ObsidianAdapter│  │  YourAdapter │           │
│  │ (Default)    │  │ (Read-Only)   │  │  (Custom)    │           │
│  │              │  │              │  │              │           │
│  │ • FTS5       │  │ • FTS5       │  │              │           │
│  │ • Dedup      │  │ • Frontmatter│  │              │           │
│  │ • TTL        │  │ • Wiki-links │  │              │           │
│  │ • Namespace  │  │ • Incremental│  │              │           │
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

### 2.2 主动声明流 (declare)

```
User: "I prefer dark mode" (主动告知)
  → MCE Engine (3-layer funnel, but confidence=1.0)
  → MemoryEntry(type=user_preference, confidence=1.0, source_layer="declaration")
  → SQLiteAdapter.remember() [namespace=current]
  → Stored with source="declaration" in metadata
```

### 2.3 知识库检索流 (recall_from_knowledge)

```
User: "Python design patterns"
  → ObsidianAdapter.recall("Python design patterns")
  → FTS5 search in obsidian_index.db
  → Returns: [{title, content, tags, wiki_links}, ...]
```

### 2.4 统一检索流 (recall_all)

```
User: "Python design patterns"
  → SQLiteAdapter.recall(namespaces=[current, "global"])
  → ObsidianAdapter.recall("Python design patterns")
  → Merge: {memories: [...], knowledge: [...], priority: "memory_first"}
```

### 2.5 记忆画像流 (get_memory_profile)

```
User: "What do you remember about me?"
  → SQLiteAdapter.get_profile()
  → SQL aggregation: COUNT by type, AVG confidence, top content
  → Returns: {summary, highlights, stats, namespace, last_updated}
```

### 2.6 智能调度流 (build_system_prompt)

```
Agent needs context for "dark mode" conversation
  → cm.build_system_prompt(context="dark mode", language="en")
  → Recall relevant memories (max_memories=10)
  → Recall knowledge base entries (max_knowledge=5)
  → Generate EN/CN/JP prompt with priority ordering:
      1. User Memories (highest priority)
      2. Knowledge Base
      3. General Knowledge (lowest priority)
```

---

## 3. 检索优先级策略

```
build_system_prompt(context, max_memories, max_knowledge, language)
  │
  ├─ Layer 1a: 当前 namespace 的记忆 (project-specific)
  │    e.g., namespace="project-alpha" 的 user_preference
  │
  ├─ Layer 1b: 全局 namespace 的记忆 (user-level)
  │    e.g., namespace="global" 的通用偏好和纠正
  │
  ├─ Layer 2:  知识库 (Obsidian vault)
  │    e.g., Obsidian vault 中的笔记
  │
  └─ Layer 3:  外部 LLM (Agent 自己决定)
       e.g., GPT-4/Claude 生成回答
```

---

## 4. 模块依赖关系

```
carrymem.py (主入口)
  ├── engine.py (MCE 核心引擎 — slim refactored)
  ├── adapters/
  │   ├── base.py (StorageAdapter ABC + MemoryEntry + StoredMemory)
  │   ├── sqlite_adapter.py (SQLiteAdapter + FTS5 + Dedup + TTL + Namespace)
  │   ├── obsidian_adapter.py (ObsidianAdapter + FTS5 + Frontmatter + Wiki-links)
  │   └── loader.py (Plugin adapter loader via entry_points)
  ├── layers/
  │   ├── rule_matcher.py (Layer 1: 规则匹配)
  │   ├── pattern_analyzer.py (Layer 2: 结构分析)
  │   └── semantic_classifier.py (Layer 3: 语义推断)
  ├── coordinators/
  │   └── classification_pipeline.py (分类管道编排)
  ├── utils/
  │   ├── confirmation.py (确认模式检测 EN/CN/JP)
  │   ├── config.py (配置管理)
  │   ├── helpers.py (工具函数)
  │   ├── language.py (多语言支持)
  │   ├── constants.py (常量定义)
  │   └── logger.py (日志)
  └── integration/
      └── layer2_mcp/
          ├── tools.py (3+3+3+2+1 工具定义)
          └── handlers.py (工具处理器)
```

---

## 5. 版本演进

| 版本 | 架构变更 | 新增模块 |
|------|---------|---------|
| v0.6 | CarryMem 主类 + context 增强 + SQLiteAdapter | carrymem.py, sqlite_adapter.py |
| v0.7 | ObsidianAdapter + 3+3+3 MCP | obsidian_adapter.py |
| v0.8 | declare() + get_profile() + 3+3+3+2 MCP | base.py get_profile(), handlers |
| v0.9 | Namespace 隔离 + 跨 namespace 检索 | sqlite_adapter.py namespace 列 |
| v0.10 | build_system_prompt() + Plugin System + MCE-Bench Public | loader.py, prompt templates |
| **v0.3.0** | **Engine slim refactoring + Project cleanup** | engine.py (2263→182 lines), test_carrymem.py |

**关键重构 (v0.3.0)**:
- engine.py 从 2263 行精简到 182 行（移除企业级功能：tenants, access_control, encryption, distributed 等）
- 删除所有遗留目录和文件（dashboard/, demo/, examples/, mce-mcp/, scripts/, vscode-extension/ 等）
- 统一测试套件为 tests/test_carrymem.py (32 个测试，全部通过)
