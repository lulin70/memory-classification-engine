# CarryMem 解耦架构图 (v4.0)

**日期**: 2026-04-20
**版本**: v4.0 (对应 CarryMem v0.5~v0.6)

---

## 1. 整体架构

```
╔══════════════════════════════════════════════════════════════════════╗
║                        CarryMem — 随身记忆库                         ║
║                      "带着你的记忆走"                                 ║
╚══════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────┐
│                        AI Agent / Claude Code                       │
│                          (数据生产者)                                 │
│                                                                     │
│  Claude Code ──┐                                                    │
│  Cursor ───────┤── MCP Protocol ──→ CarryMem MCP Server             │
│  Trae ─────────┤                                                    │
│  Custom Agent ─┘                                                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MCP Server (3+3 可选模式)                         │
│                                                                     │
│  ┌─────────────────────── 核心 (永远可用) ──────────────────────┐   │
│  │  ① classify_message       → 分类单条消息                     │   │
│  │  ② get_classification_schema → 查看 Schema                  │   │
│  │  ③ batch_classify          → 批量分类                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────── 可选 (需 adapter) ───────────────────┐   │
│  │  ④ classify_and_remember   → 分类+存储一键完成               │   │
│  │  ⑤ recall_memories         → 检索记忆(按type/tier过滤)       │   │
│  │  ⑥ forget_memory           → 删除记忆                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
            │                              │
            │ MemoryEntry (JSON)           │ StoredMemory
            ▼                              ▼
┌─────────────────────────┐    ┌─────────────────────────────────────┐
│   LAYER 1: MCE ENGINE   │    │      LAYER 2: STORAGE ADAPTERS      │
│   ★ 核心壁垒 ★          │    │      (可插拔后端)                    │
│                         │    │                                     │
│  ┌───────────────────┐  │    │  ┌─────────────────────────────┐   │
│  │  Rule Matcher     │  │    │  │  StorageAdapter ABC          │   │
│  │  Recall: 40-50%   │──┼──→ │  │  ┌─ remember(entry)          │   │
│  │  Cost: 0ms LLM    │  │    │  │  ├─ recall(query, filters)   │   │
│  │  定位: 成本控制器   │  │    │  │  └─ forget(id)              │   │
│  └────────┬──────────┘  │    │  └─────────────────────────────┘   │
│           │             │    │                                     │
│  ┌────────▼──────────┐  │    │  官方适配器:                         │
│  │  Pattern Analyzer  │  │    │  ┌──────────┐ ┌──────────────┐    │
│  │  Recall: 70-80%   │──┼──→ │  │ SQLite   │ │ Supermemory  │    │
│  │  Cost: 0ms LLM    │  │    │  │ (默认)    │ │ (云端)        │    │
│  │  定位: 信号增强器   │  │    │  └──────────┘ └──────────────┘    │
│  └────────┬──────────┘  │    │  ┌──────────┐ ┌──────────────┐    │
│           │             │    │  │ Obsidian │ │ Mem0         │    │
│  ┌────────▼──────────┐  │    │  │ (知识库)  │ │ (向量+图)     │    │
│  │  Semantic Class.   │  │    │  └──────────┘ └──────────────┘    │
│  │  Recall: 90%+     │──┼──→ │  ┌──────────┐ ┌──────────────┐    │
│  │  Cost: 可选LLM     │  │    │  │ JSON文件 │ │ PostgreSQL   │    │
│  │  定位: 兜底保障     │  │    │  │ (简单)    │ │ (企业)        │    │
│  └───────────────────┘  │    │  └──────────┘ └──────────────┘    │
│                         │    │                                     │
│  7 种记忆类型:           │    │  社区适配器:                         │
│  · correction           │    │  via entry_points 插件机制           │
│  · sentiment_marker     │    │                                     │
│  · task_pattern         │    └─────────────────────────────────────┘
│  · decision             │
│  · user_preference      │
│  · relationship         │
│  · fact_declaration     │
│                         │
│  4 个存储层级:           │
│  · Tier 1: 感觉记忆     │
│  · Tier 2: 程序性记忆   │
│  · Tier 3: 情景记忆     │
│  · Tier 4: 语义记忆     │
└─────────────────────────┘
```

---

## 2. 数据流

### 2.1 分类+存储流程 (classify_and_remember)

```
用户消息 ──→ MCP Server ──→ CarryMem.classify_and_remember()
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Rule Matcher   Pattern Analyzer  Semantic Classifier
              (0ms LLM)      (0ms LLM)         (可选 LLM)
                    │               │               │
                    └───────┬───────┘───────────────┘
                            ▼
                    MemoryEntry (JSON)
                    {type, content, tier, confidence, ...}
                            │
                    ┌───────┴───────┐
                    │ should_store? │
                    └───┬───────┬───┘
                        │       │
                   Yes  │       │ No
                        ▼       ▼
                adapter.remember()  return {stored: False}
                        │
                        ▼
                StoredMemory (含 storage_key, created_at)
                        │
                        ▼
                return {stored: True, ...}
```

### 2.2 检索流程 (recall_memories)

```
检索请求 ──→ MCP Server ──→ CarryMem.recall_memories(query, filters)
                                        │
                                        ▼
                                adapter.recall(query, filters)
                                        │
                                ┌───────┴───────┐
                                │               │
                          SQLite FTS5      其他适配器
                          全文搜索         原生检索
                                │               │
                                └───────┬───────┘
                                        ▼
                                List[StoredMemory]
                                (按 confidence 降序)
                                        │
                                        ▼
                                return memories
```

### 2.3 检索优先级策略 (v0.7+)

```
Agent 收到用户消息
        │
        ▼
┌───────────────────┐
│ Layer 1: 记忆库    │ ← recall_memories(type="user_preference")
│ (SQLite/其他)      │ ← recall_memories(type="decision", limit=3)
└────────┬──────────┘
         │ 不够?
         ▼
┌───────────────────┐
│ Layer 2: 知识库    │ ← recall_from_knowledge(query="当前话题")
│ (Obsidian)        │
└────────┬──────────┘
         │ 还不够?
         ▼
┌───────────────────┐
│ Layer 3: 外部 LLM  │ ← Agent 自己决定
│ (不在 CarryMem 内) │
└───────────────────┘
```

---

## 3. 模块依赖图

```
carrymem/                          ← 产品包名 (PyPI)
├── __init__.py                    ← from carrymem import CarryMem
├── engine.py                      ← CarryMem 主类
│   ├── classify_message()         ← 纯分类
│   ├── classify_and_remember()    ← 分类+存储
│   ├── recall_memories()          ← 检索
│   └── forget_memory()           ← 删除
│
├── mce/                           ← 引擎内部模块 (类似 InnoDB)
│   ├── __init__.py
│   ├── layers/
│   │   ├── rule_matcher.py        ← Layer 1: 规则匹配
│   │   ├── pattern_analyzer.py    ← Layer 2: 模式分析
│   │   └── semantic_classifier.py ← Layer 3: 语义分类
│   ├── coordinators/
│   │   └── classification_pipeline.py
│   ├── engine.py                  ← MCE 核心引擎
│   └── utils/
│       ├── language.py            ← 多语言支持
│       └── ...
│
├── adapters/                      ← 存储适配器
│   ├── base.py                    ← StorageAdapter ABC
│   ├── sqlite_adapter.py          ← 默认实现
│   ├── obsidian_adapter.py        ← 知识库 (v0.7)
│   └── ...
│
├── mcp/                           ← MCP Server
│   ├── server.py
│   ├── handlers.py
│   └── tools.py
│
└── cli.py                         ← carrymem run / carrymem classify

mce/                               ← 别名包 (向前兼容)
└── __init__.py                    ← from mce import * → carrymem
```

---

## 4. 与 v3.0 的架构对比

```
v3.0 (11工具全栈)              v4.0 (3+3 解耦)
─────────────────              ────────────────
MCP Server                     MCP Server
├── classify_memory            ├── classify_message        (核心)
├── batch_classify             ├── batch_classify          (核心)
├── store_memory    ← 硬耦合   ├── get_classification_schema (核心)
├── retrieve_memories ← 硬耦合 ├── classify_and_remember   (可选, 解耦)
├── get_memory_stats ← 硬耦合  ├── recall_memories         (可选, 解耦)
├── find_similar    ← 硬耦合   └── forget_memory           (可选, 解耦)
├── export_memories ← 硬耦合
├── import_memories ← 硬耦合       Engine ←→ Adapter (ABC)
├── mce_recall      ← 硬耦合       解耦! 可替换!
├── mce_forget      ← 硬耦合
└── mce_status

存储逻辑写在 handler 里          存储通过 StorageAdapter ABC
不配 DB 就不能用                 没有 adapter 时 3 个核心工具照常工作
定位: 完整记忆系统               定位: 分类是核心，存储让体验完整
```

---

## 5. 关键设计决策

| 决策 | 选择 | 理由 | 替代方案 |
|------|------|------|---------|
| 引擎与存储的关系 | 解耦 (ABC) | 引擎纯净，存储可替换 | 硬耦合 (v3.0) |
| 默认存储 | SQLite | 零配置，单文件，FTS5 | 无默认 (v3.3) |
| MCP 工具模式 | 3+3 可选 | 核心永远可用，存储按需 | 全部必选 / 全部可选 |
| 包名迁移 | 双包名过渡 | 向前兼容 | 一次性切换 |
| 检索优先级 | Agent prompt 层定义 | 灵活，不硬编码 | CarryMem 内置调度 |
| 知识库适配 | 直接读 Markdown | 通用，不依赖 Obsidian API | Obsidian Local REST API |
