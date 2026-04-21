# CarryMem 产品共识 × 架构决策 × 四方评审 (v4.0)
**日期**: 2026-04-20 (v4.0 重大更新)
**决策**: **从纯分类中间件升级为随身记忆库 — CarryMem**
**输入**: 产品方向讨论纪要 + 创始人本心 + 11篇公众号文章叙事链 + v3.3共识
**参与方**: PM / ARCH / QA / DEV

**v4.0 核心变更**:
- 产品名: MCE → **CarryMem** (MCE 保留为引擎层内部模块名)
- 定位: 纯分类中间件 → **随身记忆库** (分类是核心壁垒，存储让体验完整)
- MCP 工具: 3 个纯分类 → **3+3 可选** (核心3永远可用，存储3按需启用)
- 目标用户: 开发者 → **开发者(P0) + Agent团队(P1) + 终端用户(北极星)**

---

## 0. 决策摘要：为什么选路线 B

### 0.1 核心矛盾（已确认）

当前 MCP Server 暴露 **11 个工具**，构成比例：

| 类别 | 工具 | 数量 | 占比 |
|------|------|------|------|
| **纯分类** | `classify_memory`, `batch_classify` | 2 | 18% |
| **存储 CRUD** | `store_memory`, `retrieve_memories`, `get_memory_stats`, `find_similar`, `export_memories`, `import_memories`, `mce_recall`, `mce_forget` | 8 | 73% |
| **系统状态** | `mce_status` | 1 | 9% |

**信号问题**: 存储工具占 73%，对外传递的信号是"完整记忆系统"，与 MCE 的核心叙事"分类引擎"直接矛盾。

### 0.2 三条路线对比（最终结论）

| 维度 | A: 全栈(Supermemory路线) | **B: 纯上游(推荐)** | C: 双模式 |
|------|--------------------------|---------------------|-----------|
| 差异化 | ❌ 和 Mem0/Supermemory 同质化 | ✅ 全球唯一"记忆分类中间件" | ❌ 自相矛盾 |
| 竞争态势 | ⚠️ 对抗 64k+ stars | ✅ 无直接竞争对手 | ❌ 内耗 |
| 上手门槛 | ✅ 零配置 | ⚠️ 需搭链路（有 adapter 降低） | ❌ 选择困难 |
| 技术债务 | ❌ 存储耦合深 | ✅ 架构最干净 | ❌ 双倍维护 |
| 叙事一致性 | ❌ 自相矛盾 | ✅ 完美一致 | ❌ 混乱 |
| 资源需求 | 低（维持现状） | 中（需写 adapter + 文档） | 高（两套体系） |
| 长期天花板 | 低（存储打不过） | **高（成为分类标准）** | 中（分裂风险） |

### 0.3 WORKBUDDY AI 的关键论据（已采纳）

> "正面竞争打不过。Supermemory 背后有 YC、顶级 Benchmark、Cloudflare 级基础设施，Mem0 有 18k GitHub Star、有融资。MCE 一个人做，存储层做到及格线就已经耗尽全力了，但'及格线的存储'在用户眼里等于'不好用'，不如不做。"
>
> "但分类层没有人做。这是事实。Supermemory 的 memory 工具收到一条消息，直接存，没有分类。Mem0 的 add_memory 也是直接存，然后靠 retrieval 的时候用语义相似度去捞。它们都在'存什么'这个问题上选择了回避。"
>
> "MCE 证明了一件事：60% 的消息不需要存，或者至少不需要用 LLM 去处理。这个判断本身就有独立价值，不依赖存储层。"
>
> "叙事应该是这样的：'你的 Agent 现在用 Mem0 或者 Supermemory 存记忆，没问题。但你在往里倒东西之前，是不是应该先想想什么值得倒？MCE 就是那个门口的安检机。'"
>
> "这样 Supermemory 不是竞品，是下游客户。Mem0 也是。甚至 Claude Code 自己的 CLAUDE.md 机制也是。"

### 0.4 最终定位声明 (v4.0 更新)

```
┌─────────────────────────────────────────────────────┐
│                   AI Agent / Claude Code             │
│                      (数据生产者)                     │
└──────────────────────┬──────────────────────────────┘
                       │ 对话消息
                       ▼
┌─────────────────────────────────────────────────────┐
│              ★ CarryMem — 随身记忆库 ★                │
│                                                     │
│   "带着你的记忆走"                                    │
│                                                     │
│   ┌─────────────────────────────────────────────┐   │
│   │  MCE (Memory Classification Engine)          │   │
│   │  引擎层 — 核心壁垒，类似 MySQL 里的 InnoDB    │   │
│   │                                              │   │
│   │  输入: 原始对话消息  →  输出: 结构化 MemoryEntry│   │
│   │  ("该存吗?什么类型?多重要?将来怎么找?")         │   │
│   │                                              │   │
│   │  核心价值: 让存入变聪明，让检索变简单            │   │
│   │  · 存入: 自动分类+过滤 → 只存值得存的           │   │
│   │  · 检索: type/tier/confidence → 精准调取       │   │
│   │  · 成本: 60% 零 LLM，三层漏斗                  │   │
│   └─────────────────────────────────────────────┘   │
│                       │                              │
│                       ▼                              │
│   ┌─────────────────────────────────────────────┐   │
│   │  Storage Layer — 可插拔存储                    │   │
│   │                                              │   │
│   │  默认: SQLite (开箱即用)                       │   │
│   │  可选: Supermemory / Mem0 / Obsidian / 自定义  │   │
│   │                                              │   │
│   │  接口: remember() / recall() / forget()       │   │
│   └─────────────────────────────────────────────┘   │
│                                                     │
│   MCP 暴露 6 个工具 (3核心 + 3可选):                  │
│   ① classify_message        (核心，永远可用)          │
│   ② get_classification_schema (核心)                 │
│   ③ batch_classify           (核心)                  │
│   ④ classify_and_remember    (可选，需配置adapter)    │
│   ⑤ recall_memories          (可选)                  │
│   ⑥ forget_memory            (可选)                  │
│                                                     │
│   目标用户:                                          │
│   · P0: 开发者 (接入方) — pip install carrymem       │
│   · P1: Agent 产品团队 — 生产级存储适配器             │
│   · 北极星: 终端用户 — "你的 AI 记得你"               │
└──────────────────────┬──────────────────────────────┘
                       │ MemoryEntry (JSON)
                       ▼
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  ┌──────────┐  ┌───────────┐  ┌──────────┐
  │Supermemory│  │   Mem0    │  │ Obsidian │
  │  (云端)   │  │ (自托管)  │  │ (本地文件) │
  └──────────┘  └───────────┘  └──────────┘
        ↓              ↓              ↓
     长期存储        向量检索       Markdown归档
```

**v3 → v4 定位变更核心**:

| 维度 | v3.3 (纯分类) | v4.0 (CarryMem) | 变更原因 |
|------|-------------|----------------|---------|
| 产品名 | MCE | **CarryMem** | MCE 描述引擎功能，不描述产品愿景 |
| 定位 | 分类中间件 | **随身记忆库** | 创始人本心 + 文章叙事一致性 |
| 存储 | 完全交给下游 | **SQLite 默认 + 可替换** | "3行代码接入"需要完整链路 |
| MCP 工具 | 3 个纯分类 | **3+3 可选** | 核心纯净 + 体验完整 |
| 目标用户 | 仅开发者 | **开发者 + Agent团队 + 终端用户(北极星)** | 分层触达 |
| 竞品关系 | 互补 Supermemory/Mem0 | **互补 + 可选替代** | SQLite 默认让轻量用户不需要它们 |

**为什么这不是 v3.0 的"11工具全栈"回退**:
1. v3.0 的 11 工具是**硬耦合**（存储逻辑写在 handler 里）→ v4.0 是**解耦**（StorageAdapter ABC）
2. v3.0 的存储是**必选**（不配 DB 就不能用）→ v4.0 是**可选**（没有 adapter 时 3 个核心工具照常工作）
3. v3.0 的定位是"完整记忆系统"→ v4.0 的定位是"分类是核心，存储让体验完整"
4. 核心差异：**引擎层永远纯净，存储层永远可替换**

---

## 1. 工具裁剪清单（具体到每个工具）

### 1.1 保留的工具（3 个）→ 核心 MCP 接口

#### Tool ①: `classify_message`（重命名自 `classify_memory`）

**变更说明**: 名称从 `classify_memory` 改为 `classify_message`，更准确表达"分类消息"而非"分类记忆"。

```json
{
  "name": "classify_message",
  "description": "分析消息是否包含值得记忆的信息，返回标准化 MemoryEntry。MCE 是记忆分类中间件，不负责存储——输出结果可对接任意下游存储方案（Supermemory/Mem0/Obsidian/自定义）。",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "用户消息内容"
      },
      "context": {
        "type": "string",
        "description": "对话上下文（可选）。当用户表达确认/接受时，传入上一条AI回复可提高decision/correction分类质量，补全约15%的信息缺口（详见§8.5.2）。"
      }
    },
    "required": ["message"]
  }
}
```

**输出 Schema** (这是最重要的设计决策 — 标准 MemoryEntry):

```json
{
  "schema_version": "1.0.0",
  "should_remember": true,
  "entries": [
    {
      "id": "mce_20260419_001",
      "type": "user_preference",
      "type_label_zh": "用户偏好",
      "content": "用户喜欢用双引号而不是单引号",
      "confidence": 0.92,
      "tier": 2,
      "tier_label": "程序性记忆(Working)",
      "source_layer": "rule",           // rule / pattern / semantic / llm
      "reasoning": "包含明确的偏好表达关键词 'prefer'",
      "extracted_entities": ["双引号", "单引号"],
      "suggested_action": "store",      // store / ignore / defer
      "recall_hint": null,              // v0.6+: {"trigger_keywords": [...], "max_context_items": 3}
      "metadata": {
        "original_message": "I prefer double quotes in my code",
        "processing_time_ms": 12,
        "timestamp_utc": "2026-04-19T10:30:00Z"
      }
    }
  ],
  "summary": {
    "total_entries": 1,
    "by_type": {"user_preference": 1},
    "by_tier": {2: 1},
    "avg_confidence": 0.92,
    "filtered_count": 0,
    "llm_calls_used": 0
  },
  "engine_info": {
    "version": "0.2.0",
    "mode": "classification_only"
  }
}
```

**关键设计决策**:
- `should_remember`: 布尔值，让下游一眼知道要不要存
- `suggested_action`: `store` / `ignore` / `defer` — 下游可以直接照做
- `tier`: 保留层级信息，但标注为"建议存储层级"，由下游决定是否遵循
- `schema_version`: 便于未来演进时保持向后兼容
- `engine_info.mode`: 明确标记 `"classification_only"`，防止误解

#### Tool ②: `get_classification_schema`（新增）

**这是用户明确要求的新工具** — 返回 MCE 的分类体系定义，让下游知道怎么解析输出。

```json
{
  "name": "get_classification_schema",
  "description": "返回 MCE 的完整分类体系定义，包括 7 种记忆类型、4 层存储层级、置信度阈值等。下游系统可用此 schema 自动映射 MCE 输出到自己的存储结构。",
  "inputSchema": {
    "type": "object",
    "properties": {
      "format": {
        "type": "string",
        "enum": ["json", "markdown"],
        "default": "json",
        "description": "输出格式"
      }
    }
  }
}
```

**输出示例**:

```json
{
  "schema_version": "1.0.0",
  "engine_version": "0.2.0",
  "memory_types": [
    {
      "id": "user_preference",
      "label_en": "User Preference",
      "label_zh": "用户偏好",
      "description": "用户的习惯、喜好、风格选择",
      "examples": ["I prefer dark mode", "Use camelCase naming"],
      "default_tier": 2,
      "persistence_hint": "short_term_to_long_term",
      "downstream_mapping": {
        "supermemory": "preference",
        "mem0": "user_profile",
        "obsidian": "# Preferences"
      }
    },
    {
      "id": "correction",
      "label_en": "Correction",
      "label_zh": "纠正信号",
      "description": "对之前信息的修正、澄清、否定",
      "examples": ["No, that's wrong", "Actually it should be X"],
      "default_tier": 2,
      "persistence_hint": "immediate",
      "downstream_mapping": { ... }
    },
    // ... 其余 5 种类型（fact_declaration, decision, relationship, task_pattern, sentiment_marker）
  ],
  "storage_tiers": [
    {"id": 1, "name": "Sensory", "zh_name": "感觉记忆", "duration": "<1s", "action": "ignore"},
    {"id": 2, "name": "Working", "zh_name": "程序性记忆", "duration": "hours-days", "action": "cache"},
    {"id": 3, "name": "Episodic", "zh_name": "情节记忆", "duration": "days-months", "action": "persist"},
    {"id": 4, "name": "Semantic", "zh_name": "语义记忆", "duration": "months-years", "action": "archive"}
  ],
  "confidence_thresholds": {
    "high": 0.85,
    "medium": 0.60,
    "low": 0.30
  },
  "output_format": {
    "root_keys": ["schema_version", "should_remember", "entries", "summary", "engine_info"],
    "entry_keys": ["id", "type", "content", "confidence", "tier", "source_layer", "reasoning", "suggested_action", "metadata"]
  }
}
```

**价值**: 这个工具让任何下游开发者可以在 **5 分钟内** 完成 MCE 输出到自己存储系统的映射。不需要读源码，不需要猜字段含义。

#### Tool ③: `batch_classify`（保留，调整输出）

**保留但修改**: 输出从当前的扁平列表改为 MemoryEntry 数组，和 `classify_message` 保持一致。

```json
{
  "name": "batch_classify",
  "description": "批量分类多条消息，每条消息返回独立 MemoryEntry。适用于对话历史回放、日志分析等批量场景。",
  "inputSchema": {
    "type": "object",
    "properties": {
      "messages": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "message": { "type": "string" },
            "context": { "type": "string" }
          },
          "required": ["message"]
        }
      }
    },
    "required": ["messages"]
  }
}
```

**输出**: `{ "results": [MemoryEntry, MemoryEntry, ...], "summary": {...} }`

### 1.2 移除的工具（8 个）→ 不再属于 MCP 接口

| # | 工具名 | 当前行数(handlers.py) | 移除原因 | 替代方案 |
|---|--------|----------------------|----------|----------|
| 1 | `store_memory` | L136-183 | 存储是下游职责 | 下游收到 `suggested_action: "store"` 后自行存储 |
| 2 | `retrieve_memories` | L185-237 | 检索是下游职责 | Supermemory `recall()`, Mem0 `search()`, Obsidian grep |
| 3 | `get_memory_stats` | L239-277 | 统计是下游职责 | 各自有 stats API |
| 4 | `find_similar` | L324-376 | 相似搜索是下游职责 | 向量数据库原生支持 |
| 5 | `export_memories` | L378-416 | 导出是下游职责 | 各自已有 export 功能 |
| 6 | `import_memories` | L418-457 | 导入是下游职责 | 通过各自 API 导入 |
| 7 | `mce_recall` | L459-564 | 召回是下游职责 | Supermemory `context()`, Mem0 `recall()` |
| 8 | `mce_forget` | L626-669 | 遗忘是下游职责 | 各自已有 delete API |

### 1.3 保留但降级的工具（1 个）

| # | 工具名 | 处理方式 | 原因 |
|---|--------|----------|------|
| 9 | `mce_status` | **保留**，但改为只返回引擎状态（不含存储统计） | 用于健康检查和调试，不涉及存储 |

**修改后的 `mce_status` 输出**:
```json
{
  "status": "active",
  "mode": "classification_only",
  "version": "0.2.0",
  "schema_version": "1.0.0",
  "capabilities": {
    "classification_types": 7,
    "storage_tiers": 4,
    "supported_output_formats": ["json"]
  },
  "uptime_seconds": 3600,
  "messages_processed_today": 42
}
```

---

## 2. 代码变更清单（精确到文件和函数）

### 2.1 Phase 0: 文档对齐（v0.2.0 发布前，立即执行，不改代码）

#### F0-MCP-01: README.md 首屏定位重写

**位置**: [README.md](file:///Users/lin/trae_projects/memory-classification-engine/README.md) 第 1-10 行

**当前**:
```markdown
# Memory Classification Engine (MCE)
A multi-layer memory classification engine for AI agents.
```

**改为**:
```markdown
# Memory Classification Engine (MCE)
**记忆分类中间件** — AI Agent 的"记忆安检机"

> MCE 不存储记忆。MCE 告诉你**什么值得记**、**记成什么类型**、**存在哪一层**。
> 存储的事，交给 Supermemory / Mem0 / Obsidian / 你自己的系统。

[![PyPI version](https://img.shields.io/pypi/v/memory-classification-engine)](https://pypi.org/project/memory-classification-engine/)
[![Tests](https://img.shields.io/badge/tests-874 passing-green)](https://github.com/linzichun/memory-classification-engine)
[![MCP](https://img.shields.io/badge/MCP-Production%20Ready-blue)](https://modelcontextprotocol.io)
```

#### F0-MCP-02: tools.py 存储工具加 `[Deprecated]` 标记

**位置**: [tools.py](file:///Users/lin/trae_projects/memory-classification-engine/src/memory_classification_engine/integration/layer2_mcp/tools.py) L30-L301

**操作**: 在 8 个存储工具的 description 前加上 `[Deprecated v0.3] ` 前缀

示例:
```python
# 当前 (L31):
"description": "将记忆内容存储到合适的层级，支持7种记忆类型",

# 改为:
"description": "[Deprecated v0.3] 将记忆内容存储到合适的层级 — 将移至 StorageAdapter 插件。请使用 classify_message 获取 MemoryEntry 后自行存储。",
```

**受影响的工具**: store_memory(L31), retrieve_memories(L67), get_memory_stats(L93), find_similar(L135), export_memories(L163), import_memories(L196), mce_recall(L222), mce_forget(L284)

#### F0-MCP-03: server.py serverInfo 版本修正

**位置**: [server.py](file:///Users/lin/trae_projects/memory-classification-engine/src/memory_classification_engine/integration/layer2_mcp/server.py) L161

**当前**:
```python
"version": "0.1.0"
```
**改为**:
```python
"version": "0.2.0"
```

#### F0-MCP-04: 新建 STORAGE_STRATEGY.md

**路径**: `docs/user_guides/STORAGE_STRATEGY.md`

**内容大纲**:
```
# MCE 存储策略指南

## 核心原则: MCE 只分类，不存储

## 推荐下游方案

### 方案 A: Supermemory (云端)
- 适用场景: 需要 Benchmark 级检索质量 + 自动遗忘
- 安装: npx install-mcp ...
- 映射表: MCE type → Supermemory tag

### 方案 B: Mem0 (自托管)
- 适用场景: 需要图存储 + 向量混合检索
- 安装: pip install mem0 ...
- 映射表: MCE type → Mem0 category

### 方案 C: Obsidian (本地 Markdown)
- 适用场景: 知识工作者，需要人工审阅
- 映射: MCE type → Obsidian folder/#tag

### 方案 D: 自定义 (StorageAdapter)
- 适用场景: 有特殊存储需求
- 实现: 继承 StorageAdapter ABC

## 快速开始: MCE + Supermemory 集成示例
## 快速开始: MCE + Obsidian 集成示例
## Migration Guide: 从内置存储迁移到下游
```

#### F0-MCP-05: installation_guide_v2.md 更新 MCP 章节

**位置**: [installation_guide_v2.md](file:///Users/lin/trae_projects/memory-classification-engine/docs/user_guides/installation_guide_v2.md)

**变更**: MCP 配置章节增加说明：
> "MCE MCP Server 默认以**纯分类模式**运行。当前版本(v0.2.0)仍包含内置存储工具(标记为 Deprecated)，v0.3.0 将移除。建议新用户直接使用 classify_message + 下游存储方案。"

---

### 2.2 Phase 1: 架构分层（v0.3.0，下周执行）

#### V3-MCP-01: tools.py 重写 — 从 11 个工具缩减为 4 个

**文件**: [tools.py](file:///Users/lin/trae_projects/memory-classification-engine/src/memory_classification_engine/integration/layer2_mcp/tools.py)

**最终 TOOLS 列表**:
```python
TOOLS: List[Dict[str, Any]] = [
    # ① 核心分类
    {
        "name": "classify_message",
        "description": "分析消息是否包含值得记忆的信息，返回标准化 MemoryEntry (JSON Schema v1.0)。MCE 是记忆分类中间件——不负责存储，输出可对接 Supermemory/Mem0/Obsidian/任意自定义存储。",
        "inputSchema": { ... }  # 见 1.1 节
    },
    # ② 分类体系查询
    {
        "name": "get_classification_schema",
        "description": "返回 MCE 完整分类体系定义（7种类型+4层存储+置信度阈值+下游映射表）。用于下游系统自动映射 MCE 输出到自身存储结构。",
        "inputSchema": { ... }  # 见 1.1 节
    },
    # ③ 批量分类
    {
        "name": "batch_classify",
        "description": "批量分类多条消息，每条返回独立 MemoryEntry。适用于对话历史回放、日志分析等场景。",
        "inputSchema": { ... }  # 见 1.1 节
    },
    # ④ 系统状态（纯引擎状态，不含存储）
    {
        "name": "mce_status",
        "description": "返回 MCE 引擎状态信息（版本、能力、运行时间）。不包含存储统计——存储统计请查询下游系统。",
        "inputSchema": { ... }  # 见 1.3 节
    }
]
```

**删除**: store_memory, retrieve_memories, get_memory_stats, find_similar, export_memories, import_memories, mce_recall, mce_forget

**净变化**: 11 → 4 个工具 (-63%)

#### V3-MCP-02: handlers.py 重写 — 删除 8 个存储 handler

**文件**: [handlers.py](file:///Users/lin/trae_projects/memory-classification-engine/src/memory_classification_engine/integration/layer2_mcp/handlers.py)

**删除的方法**:
- `handle_store_memory` (L136-183, 48 行)
- `handle_retrieve_memories` (L185-237, 53 行)
- `handle_get_memory_stats` (L239-277, 39 行)
- `handle_find_similar` (L324-376, 53 行)
- `handle_export_memories` (L378-416, 39 行)
- `handle_import_memories` (L418-457, 40 行)
- `handle_mce_recall` (L459-564, 106 行)
- `handle_mce_forget` (L626-669, 44 行)

**总计删除**: ~422 行 (handlers.py 当前 674 行的 63%)

**保留并修改的方法**:
- `handle_classify_memory` → **重命名为 `handle_classify_message`**, 输出改为 MemoryEntry Schema
- `handle_batch_classify` → 输出改为 MemoryEntry[] 数组
- `handle_mce_status` → 移除 storage_service 调用，只返回引擎状态
- `handler_map` → 更新路由表

**新增的方法**:
- `handle_get_classification_schema` → 返回静态 schema 定义 (约 30 行)

**净变化**: 674 行 → ~250 行 (-63%)

#### V3-MCP-03: engine.py 新增 `to_memory_entry()` 方法

**文件**: [engine.py](file:///Users/lin/trae_projects/memory-classification-engine/src/memory_classification_engine/engine.py)

**新增方法**:
```python
def to_memory_entry(self, message: str, context: str = None) -> Dict[str, Any]:
    """
    将 process_message 结果转换为标准 MemoryEntry 格式。
    
    这是 MCP classify_message 的底层方法。
    输出符合 MemoryEntry JSON Schema v1.0。
    
    Args:
        message: 原始消息
        context: 可选上下文
        
    Returns:
        符合 Schema v1.0 的 MemoryEntry 字典
    """
    result = self.process_message(message, context)
    
    entries = []
    for match in result.get("matches", []):
        entry = {
            "id": f"mce_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}",
            "type": match.get("memory_type") or match.get("type"),
            "content": match.get("content") or message[:200],
            "confidence": match.get("confidence", 0.0),
            "tier": match.get("tier", 2),
            "tier_label": self._tier_label(match.get("tier", 2)),
            "source_layer": match.get("source", "unknown"),
            "reasoning": match.get("reasoning", ""),
            "suggested_action": "store" if match.get("confidence", 0) > 0.5 else "defer",
            "metadata": {
                "original_message": message,
                "processing_time_ms": result.get("processing_time", 0) * 1000,
                "timestamp_utc": datetime.utcnow().isoformat() + "Z"
            }
        }
        entries.append(entry)
    
    return {
        "schema_version": "1.0.0",
        "should_remember": len(entries) > 0,
        "entries": entries,
        "summary": {
            "total_entries": len(entries),
            "by_type": self._count_by_type(entries),
            "by_tier": self._count_by_tier(entries),
            "avg_confidence": sum(e["confidence"] for e in entries) / max(len(entries), 1),
            "filtered_count": 0,
            "llm_calls_used": 0  # TODO: 从 engine 内部计数器获取
        },
        "engine_info": {
            "version": ENGINE_VERSION,
            "mode": "classification_only"
        }
    }
```

#### V3-MCP-04: StorageAdapter ABC 定义（核心抽象层）

**新建文件**: `src/memory_classification_engine/adapters/base.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class MemoryEntry:
    """标准化的记忆条目 — MCE 输出，Adapter 输入"""
    
    __slots__ = ('id', 'type', 'content', 'confidence', 'tier',
                 'source_layer', 'reasoning', 'suggested_action', 'metadata')
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.type = data.get('type')
        self.content = data.get('content')
        self.confidence = data.get('confidence', 0.0)
        self.tier = data.get('tier', 2)
        self.source_layer = data.get('source_layer', 'unknown')
        self.reasoning = data.get('reasoning', '')
        self.suggested_action = data.get('suggested_action', 'store')
        self.metadata = data.get('metadata', {})
    
    def to_dict(self) -> Dict[str, Any]:
        return {s: getattr(self, s) for s in self.__slots__}


class StorageAdapter(ABC):
    """存储适配器基类 — 所有下游存储方案的统一接口"""
    
    @abstractmethod
    def store(self, entry: MemoryEntry) -> str:
        """存储一条记忆，返回存储系统的 ID"""
        ...
    
    @abstractmethod
    def store_batch(self, entries: List[MemoryEntry]) -> List[str]:
        """批量存储，返回 ID 列表"""
        ...
    
    @abstractmethod
    def retrieve(self, query: str, limit: int = 20) -> List[Dict]:
        """检索记忆"""
        ...
    
    @abstractmethod
    def delete(self, storage_id: str) -> bool:
        """删除记忆"""
        ...
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取存储统计"""
        ...
    
    @property
    @abstractmethod
    def name(self) -> str:
        """适配器名称，如 'supermemory', 'obsidian', 'mem0'"""
        ...
    
    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """能力声明: {'vector_search': True, 'graph': False, ...}"""
        ...
```

#### V3-MCP-05: BuiltInStorageAdapter（当前 SQLite 逻辑封装）

**新建文件**: `src/memory_classification_engine/adapters/builtin.py`

**目的**: 将当前 engine.py/storage_coordinator.py 中的存储逻辑封装为 Adapter，标记 `@deprecated`

```python
from .base import StorageAdapter, MemoryEntry
import warnings


class BuiltInStorageAdapter(StorageAdapter):
    """
    MCE 内置 SQLite 存储。
    
    ⚠️ Deprecated in v0.3.0 — 仅用于过渡期兼容。
    新项目应使用 SupermemoryAdapter / ObsidianAdapter / 自定义 Adapter。
    """
    
    def __init__(self, config_path=None):
        warnings.warn(
            "BuiltInStorageAdapter is deprecated since v0.3.0. "
            "Use a dedicated downstream adapter instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # ... 封装现有 storage_coordinator 逻辑
    
    @property
    def name(self) -> str:
        return "builtin_sqlite"
```

#### V3-MCP-06: server.py handler_map 更新

**文件**: [server.py](file:///Users/lin/trae_projects/memory-classification-engine/src/memory_classification_engine/integration/layer2_mcp/server.py) — 不变，因为 handler_map 在 handlers.py 中

**但需确认**: handlers.py 的 `handle_tool()` 方法中的 routing table 同步更新。

---

## 3. 四方角色深度分析（针对路线 B）

### 3.1 👔 产品经理 (PM)

#### PM-B1: 叙事终于一致了 ✅

**之前的痛点**:
- README 说 "分类引擎"
- MCP 暴露 11 个工具（73% 是存储）
- 用户困惑："这到底是分类器还是记忆系统？"

**路线 B 解决后**:
- README: "**记忆分类中间件** — AI Agent 的'记忆安检机'"
- MCP: 4 个工具（75% 是分类）
- 用户理解零成本："MCE 分类，别人存储"

#### PM-B2: 竞品关系重构 🔄

**之前（全栈模式）**:
```
竞品: Supermemory, Mem0, Graphiti, Cognee, ...
关系: 你死我活的替代品竞争
胜算: 低（一个人 vs YC 投资的公司）
```

**现在（上游模式）**:
```
客户: Supermemory, Mem0, Obsidian, Claude Code CLAUDE.md, 自建系统
关系: 互补合作（MCE 是它们的前置组件）
壁垒: 先发优势 + 分类质量护城河
话术: "你的 Agent 用 Mem0 存记忆？很好。但存之前先过一遍 MCE，过滤掉 60% 的噪音。"
```

**具体营销角度**:
1. "Why Classification Matters More Than Storage" — 基于 7 篇竞品文章的分析
2. "MCE + Supermemory = 完整记忆链路" — 合作案例
3. "MCE + Obsidian = 开发者知识库" — 场景案例
4. Benchmark 角度转变: 不比存储，**比分类准确率**

#### PM-B3: 上门槛问题的解决方案 ⚠️

**顾虑**: 纯上游模式用户需要自己搭存储链路，门槛高。

**解决方案分层**:

| 用户类型 | 方案 | 门槛 |
|----------|------|------|
| **只想试试** | `pip install mce[mcp]` + Claude Code 配置 + 只用 classify_message | 5 分钟（和现在一样）|
| **想存起来** | STORAGE_STRATEGY.md 里的 4 种方案，选一个跟着做 | 15-30 分钟 |
| **深度集成** | 写自定义 StorageAdapter | ~2 小时 |

**关键洞察**: 用户不需要"搭链路"才能用 MCE。他们可以用 `classify_message` 直接拿到结构化 JSON，手动复制粘贴到任何地方。**存储适配器是进阶功能，不是入门门槛。**

#### PM-B4: FAQ 需要重写

**新增 Q&A**:
> **Q: MCE 和 Supermemory 是竞品吗？**
> A: 不是。Supermemory 负责存储和检索，MCE 负责分类和过滤。你可以同时使用两者：MCE 做前置分类 → Supermemory 做持久存储。
>
> **Q: 为什么不把存储也做了？**
> A: 专注。Supermemory 有 YC 投资和 Cloudflare 级基础设施，Mem0 有 18k Stars 和完整向量+图存储。MCE 一个人做，与其做一个"及格线"的存储，不如做一个"行业最好"的分类器。
>
> **Q: 我的数据安全吗？**
> A: MCE 是纯本地运行的分类器，你的消息不会发送到任何外部服务器。选择哪个下游存储方案，由你自己决定数据去向。
>
> **Q: MCE 会告诉我什么时候该查记忆吗？**
> A: 不会。MCE 在存入时打好元数据标签（type/tier/confidence），检索时机和策略由 Agent 的 system prompt 或框架层决定。MCE 让检索变简单（可以按 type 过滤），但不做检索本身。类比：MCE 是图书馆的分类编目员，负责给每本书打标签、定位置；检索时读者问"给我找管理类最近入库的5本"，图书馆系统按标签查——但编目员不替读者决定该找什么书。
>
> **Q: MCE 只记用户说的，不记 AI 回复，会不会丢信息？**
> A: 会，约 15% 的缺口。主要模式是"用户默认接受 AI 建议"（如 AI 建议"用 SQLite"，用户说"行"）。解法不是记 AI 输出（会暴增记忆量），而是在用户确认时通过 context 参数传入上一条 AI 回复作为补充。详见 §8.5。
>
> **Q: 规则层的关键词不够用怎么办？**
> A: 规则层的定位是"成本控制器"，不是"分类器"。目标召回率 40-50%，不是 100%。剩余信号交给 Pattern Analyzer（目标 70-80%）和 Semantic Classifier（目标 90%+）。关键词清单应优先覆盖明确信号词，隐式/文化表达交给语义层。详见 §7.5.2。

---

### 3.2 🏗️ 架构师 (ARCH)

#### ARCH-B1: 架构复杂度大幅下降 📉

**量化对比**:

| 指标 | v0.2.0 (当前, 11 工具) | v0.3.0 (路线 B, 4 工具) | 变化 |
|------|------------------------|-------------------------|------|
| tools.py 行数 | 305 (含验证) | ~120 | -61% |
| handlers.py 行数 | 674 | ~250 | -63% |
| MCP handler 数量 | 11 | 4 | -64% |
| 依赖 storage_service? | 是 (8 个 handler) | 否 (0 个 handler) | **解耦** |
| 可独立测试? | 部分 (依赖 DB) | **完全** (纯函数) | 质量跃升 |
| 循环依赖风险 | 高 (handler→engine→storage→handler) | **无** | 架构干净 |

#### ARCH-B2: StorageAdapter 是正确的抽象 ✅

**设计原则**:
```
MCE Core (纯分类逻辑)
    ↓ 输出: MemoryEntry (标准 JSON)
    ↓
StorageAdapter Interface (ABC)
    ├── BuiltInSQLite  (@deprecated, 兼容旧用户)
    ├── SupermemoryAdapter  (规划中, v0.3.1)
    ├── ObsidianAdapter     (规划中, v0.3.2)
    ├── Mem0Adapter         (社区贡献?)
    └── CustomAdapter       (用户自建)
```

**为什么这个抽象是对的**:
1. **开放封闭原则**: MCE core 对存储方案封闭（不依赖具体实现），对扩展开放（新的 Adapter 即新的存储方案）
2. **依赖倒置**: Core 依赖 Adapter 接口，不依赖具体存储
3. **单一责任**: 每个 Adapter 只负责一种存储方案的对接

#### ARCH-B3: MemoryEntry Schema 是核心资产 🏆

**这个 Schema 设计决定了 MCE 能否成为行业标准**。

关键设计决策及其理由:

| 决策 | 选择 | 理由 |
|------|------|------|
| `should_remember` 布尔值 | 保留 | 让下游一行代码判断 `if not result['should_remember']: return` |
| `suggested_action` 三态 | store/ignore/defer | 比单纯的布尔值更有语义；`defer` 表示"低置信度，稍后再决定" |
| `tier` 信息保留 | 保留 | 下游可能用它决定存储位置（如 tier 4 → 归档库） |
| `source_layer` 字段 | 保留(rule/pattern/semantic/llm) | 让下游了解分类的可信度来源 |
| `schema_version` | 保留 | 未来如果加第 8 种类型或改字段名，下游可以做兼容处理 |
| `downstream_mapping` (in schema tool) | 保留 | 降低下游集成成本的核心功能 |

#### ARCH-B4: 版本兼容性策略

**v0.2.0 → v0.3.0 迁移路径**:

```
v0.2.0 (当前发布版)
├── MCP: 11 tools (8 个存储 + 2 分类 + 1 状态)
├── 输出: 自定义 dict (matches[].memory_type)
└── 存储: 内置 SQLite (硬编码)
    │
    │  ← 用户升级 pip install --upgrade mce
    ▼
v0.3.0 (下一版)
├── MCP: 4 tools (3 分类 + 1 状态)  ← 8 个存储工具移除
├── 输出: MemoryEntry Schema v1.0   ← 标准化 JSON
├── 新增: get_classification_schema  ← 下游映射神器
├── 新增: StorageAdapter ABC         ← 扩展点
├── 内置存储: BuiltInStorageAdapter  ← 标记 @deprecated
└── Breaking Change?                ← ⚠️ 是，但可控
```

**Breaking Change 缓解措施**:
1. v0.2.0 的 8 个存储工具在 v0.3.0 中**彻底移除**（不是 deprecated，是删除）
2. 但提供 `mce-migrate` 脚本帮助用户迁移内置存储数据到下游
3. RELEASE NOTES 中清晰列出 breaking changes
4. 提供 v0.2.0 → v0.3.0 迁移指南

---

### 3.3 🧪 测试专家 (QA)

#### QA-B1: 测试矩阵简化 🎯

**当前测试负担** (11 个工具):

| 工具 | 测试场景数 | 依赖 | 稳定性 |
|------|-----------|------|--------|
| classify_memory | ~15 | 纯逻辑 | ✅ 高 |
| batch_classify | ~8 | 纯逻辑 | ✅ 高 |
| store_memory | ~12 | SQLite | ⚠️ 中 |
| retrieve_memories | ~10 | SQLite | ⚠️ 中 |
| get_memory_stats | ~5 | SQLite | ⚠️ 中 |
| find_similar | ~8 | FAISS/SQLite | ❌ 低 |
| export_memories | ~6 | SQLite | ⚠️ 中 |
| import_memories | ~8 | SQLite + 文件IO | ❌ 低 |
| mce_recall | ~10 | SQLite | ⚠️ 中 |
| mce_forget | ~6 | SQLite | ⚠️ 中 |
| mce_status | ~4 | SQLite | ⚠️ 中 |
| **合计** | **~92** | | |

**路线 B 后测试负担** (4 个工具):

| 工具 | 测试场景数 | 依赖 | 稳定性 |
|------|-----------|------|--------|
| classify_message | ~20 | 纯逻辑 | ✅ **极高** |
| get_classification_schema | ~5 | 静态数据 | ✅ **极高** |
| batch_classify | ~12 | 纯逻辑 | ✅ **极高** |
| mce_status | ~6 | 纯逻辑 | ✅ **极高** |
| **合计** | **~43** | **无 DB 依赖** | |

**净变化**: 92 → 43 个测试场景 (-53%)，且全部无 DB 依赖

#### QA-B2: 可以深挖分类质量了 🔬

**之前的问题**: 大量测试时间花在存储 CRUD 上，分类器的 edge case 没时间覆盖。

**释放的资源可以用于**:

1. **MCE-Bench 正式版** (100 条手工标注测试集):
   ```
   测试维度:
   - 7 种类型的正样本 (每种 15 条) = 105 条
   - 负样本 (不该被记住的消息) = 30 条
   - 边界 case (模糊消息、多类型混合) = 25 条
   - 对抗样本 (试图欺骗分类器的消息) = 20 条
   总计: ~180 条
   ```

2. **Fuzz Testing**:
   ```python
   # 随机生成消息，验证分类器不会崩溃
   def test_fuzz_classify():
       for _ in range(1000):
           msg = generate_random_string(length=random.randint(1, 500))
           result = engine.to_memory_entry(msg)
           assert "schema_version" in result
           assert "entries" in result
   ```

3. **回归防护**: 每次 classify 逻辑修改后跑全量 180-case benchmark，确保准确率不下降

#### QA-B3: CI 速度提升 ⚡

**当前 CI 问题**: demo D4 (100 条顺序消息) 跑了 66 分钟，因为存储操作有 I/O 等待。

**路线 B 后**: 
- classify_message 是纯 CPU 计算（规则匹配 + embedding），无 I/O
- 预估 180-case benchmark: < 30 秒
- Fuzz 1000 条: < 60 秒
- 全量回归: < 5 分钟（vs 当前 23 分钟）

---

### 3.4 💻 独立开发者 (DEV)

#### DEV-B1: 代码维护成本减半 💰

**量化**:

| 指标 | v0.2.0 | v0.3.0 (路线B) | 节省 |
|------|--------|---------------|------|
| layer2_mcp/ 总行数 | ~1580 (tools+handlers+server) | ~650 | -59% |
| 需理解的存储 API | storage_coordinator 全部公开方法 | 0 (Adapter 隔离) | -100% |
| Bug 表面积 (存储相关) | 8 handler × N bugs | 0 | -100% |
| 新增存储方案成本 | 改 engine.py + storage_coordinator | 新建一个 Adapter 文件 (~150行) | **模块化** |

#### DEV-B2: 贡献者友好度大幅提升 🤝

**之前** (全栈模式): 
- 想给 MCE 贡献代码？你需要理解:
  - engine.py (核心分类)
  - storage_coordinator.py (三层存储)
  - SQLite schema
  - FAISS 向量索引
  - Neo4j 图查询
  - **门槛极高**

**之后** (上游模式):
- 想给 MCE 贡献代码？你只需要理解:
  - engine.py (核心分类)
  - MemoryEntry Schema
  - **如果想加存储支持**: 写一个 Adapter (~150 行)，不影响 core
- **门槛大幅降低**

#### DEV-B3: "快递分拣中心"隐喻的实现对应 📦

WORKBUDDY AI 的比喻: **"MCE 不是要自己建仓库，是要做快递分拣中心的传送带。"**

代码层面的对应:

```
快递包裹 (原始消息)
    ↓
📦 分拣传送带 (MCE classify_message)
    ├── 📦 [偏好] → 通道 A → 目的地: Supermemory preference 库
    ├── 📦 [纠正] → 通道 B → 目的地: Supermemory correction 库  
    ├── 📦 [事实] → 通道 C → 目的地: Obsidian #Facts
    ├── 📦 [决策] → 通道 D → 目的地: Mem0 decisions
    ├── 📦 [噪音] → 通道 X → ♻️ 丢弃 (should_remember=false)
    └── 📦 [模糊] → 通道 ? → ⏸️ 延迟判断 (suggested_action=defer)
```

**每个通道 = 一种 StorageAdapter 的 store() 方法**

---

## 4. 更新后的顾虑总矩阵 (v3 — 融入路线 B 决策)

### 4.1 顾虑状态变更

| # | 顾虑 | v2 状态 | v3 状态 | 变更原因 |
|---|------|---------|---------|----------|
| 1 | README v2.0 功能无 Beta 标注 | 🔴 P0 | 🟢 **RESOLVED** | 路线 B 重写首屏，不再有 v2.0 功能混淆 |
| 2 | v0.2.0 Release Notes 缺失 | 🔴 P0 | 🔴 P0 | 不变，仍需创建 |
| 3 | mce-mcp 包未构建+fresh install 未验 | 🔴 P0 | 🔴 P0 | 不变 |
| 4 | A3.2/A3.5 分类准确度漏洞 | 🔴 P0 | 🔴 P0 | **更重要了** — 分类是唯一核心竞争力 |
| 5 | HTTP server vs stdio server 混淆 | 🟡 P1 | 🟢 **RESOLVED** | stdio server 成为唯一 MCP server |
| 6 | Supermemory 云 MCP 的竞争压力 | 🟡 P1 | 🟢 **RECLASSIFIED** | 不再是竞品，是**下游标杆客户** |
| 7 | 缺少 30s Value Pitch | 🟡 P1 | 🟢 **RESOLVED** | "记忆安检机" 就是 Value Pitch |
| 8 | Roadmap 星数目标不现实 | 🟡 P1 | 🟡 P1 | 需重写（融入路线 B） |
| 9 | 对比表→FAQ + 加入新竞品 | 🟡 P1 | 🟢 **RESOLVED** | FAQ 已重新设计（见 PM-B4） |
| 10 | 功能成熟度分级不清 | 🟡 P1 | 🟢 **RESOLVED** | 4 个工具全是 Production 级别 |
| 11 | 性能数据缺测试条件 | 🟢 P2 | 🟡 P2 | 不变 |
| 12 | Feedback Loop/Distillation 测试缺失 | 🟡 P1 | 🟡 P1 | 不变 |
| 13 | 分类准确率量化基准缺失 | 🟡 P1 | 🔴 **ESCALATED** | **P0** — 分类是唯一产品，必须量化 |
| 14 | audit.py 异常处理测试缺失 | 🟢 P2 | 🟢 P2 | 不变 |
| 15 | 版本号策略未文档化 | 🟢 P2 | 🟢 P2 | 不变 |
| 16 | pip extras 不完整 | 🟡 P1 | 🟢 **MODIFIED** | 不再需要 faiss/neo4j extras（存储交给下游），保留 api/llm/testing |
| 17 | 缺少 CLI/一键安装工具 | 🟢 P2 | 🟡 P2 | 优先级降低 |
| 18 | 缺少 30s demo GIF/视频 | 🟢 P2 | 🟢 P2 | 不变 |
| 19 | SessionRecall 应输出结构化画像 | 🟡 P1 | 🟢 **RECLASSIFIED** | SessionRecall 概念**取消** — 召回是下游职责 |
| 20 | 7 类型 vs 简单模式的认知负担 | 🟡 P1 | 🟡 P1 | 不变，但有了 `get_classification_schema` 工具降低负担 |
| **21 (NEW)** | **Pure upstream 冷启动: 用户如何从 classify 到存储?** | — | 🟡 **P1** | 需要 STORAGE_STRATEGY.md + 集成示例 |
| **22 (NEW)** | **Breaking Change: v0.3 移除 8 个存储工具的迁移路径** | — | 🟡 **P1** | 需要迁移指南 + 数据导出脚本 |
| **23 (NEW)** | **MemoryEntry Schema v1.0 的向后兼容性保证** | — | 🟢 **P2** | 需要在 schema 中设计 versioning 策略 |

### 4.2 统计

| 级别 | v2 数量 | v3 数量 | 变化 |
|------|---------|---------|------|
| 🔴 P0 | 4 | **4** | #13 升级为 P0，#6 降级解决 |
| 🟡 P1 | 10 | **8** | #5/#7/#9/#10 解决，#16 修改，#19 重分类，#21/#22 新增 |
| 🟢 P2 | 6 | **7** | #23 新增 |
| **总计** | **20** | **19** | 净减 1 项（3 解决 + 1 升级 + 2 新增 - 1 降级 + 1 重分类） |

---

## 5. 修订后的推进计划 (v3 — 路线 B 版)

### Phase 0: v0.2.0 发布收尾 (今天, 2h) — **增强: 加入 MCP 定位对齐**

| # | 任务 | Owner | 类型 | 说明 |
|---|------|-------|------|------|
| F0-1 | README 首屏定位重写 | PM | **修改** | 加入"记忆安检机"定位，见 F0-MCP-01 |
| F0-2 | GitHub Release v0.2.0 | PM | 不变 | changelog + MCP 定位说明 |
| F0-3 | mce-mcp 构建 + fresh install | DEV | 不变 | |
| F0-4 | HTTP server Deprecated | DEV | 不变 | |
| F0-5 | Commit + Push | DEV | 不变 | |
| **F0-MCP-01** | **tools.py 8 个存储工具加 [Deprecated]** | **DEV** | **新增** | **见 2.1.2** |
| **F0-MCP-02** | **server.py 版本 0.1.0→0.2.0** | **DEV** | **新增** | **见 2.1.3** |
| **F0-MCP-03** | **新建 STORAGE_STRATEGY.md** | **PM** | **新增** | **见 2.1.4** |
| **F0-MCP-04** | **installation_guide MCP 章节更新** | **PM** | **新增** | **见 2.1.5** |

### Phase 1: README/Roadmap 重构 (本周, 4h) — **重写: 融入路线 B 叙事**

| # | 任务 | Owner | 说明 |
|---|------|-------|------|
| F1-1 | README 完整重写 | PM | "记忆安检机"叙事 + 架构图 + 4 工具列表 + 下游集成示例 |
| F1-2 | FAQ 重写 | PM | 含 "和 Supermemory 的关系"/"为什么不存存储"/"数据安全" 等 |
| F1-3 | ROADMAP 重写 | PM | v0.3.0 里程碑改为 "Pure Upstream Migration" |
| F1-4 | Performance 章节 | ARCH | 分类性能数据（不再含存储性能） |
| F1-5 | 中日文同步 | PM | ROADMAP-ZH/JP 同步更新 |
| F1-6 | README 全文审核 | QA | 确保叙事一致 |

### Phase 2: v0.3.0 Pure Upstream Migration (下周, ~6 人日) — **重大变更: 11→4 工具**

| # | 任务 | Owner | 估时 | 文件 | 说明 |
|---|------|-------|------|------|------|
| **V3-MCP-01** | **tools.py 重写 (11→4 工具)** | **DEV** | **0.5d** | **tools.py** | **删除 8 个存储工具，新增 get_classification_schema** |
| **V3-MCP-02** | **handlers.py 重写 (删 422 行)** | **DEV** | **0.5d** | **handlers.py** | **删 8 个存储 handler，改 classify 输出为 MemoryEntry** |
| **V3-MCP-03** | **engine.py 新增 to_memory_entry()** | **DEV** | **0.5d** | **engine.py** | **核心方法: process_message → MemoryEntry 转换** |
| **V3-MCP-04** | **StorageAdapter ABC + MemoryEntry** | **ARCH** | **0.5d** | **adapters/base.py (新建)** | **核心抽象层** |
| **V3-MCP-05** | **BuiltInStorageAdapter (@deprecated)** | **DEV** | **0.5d** | **adapters/builtin.py (新建)** | **封装现有存储，标记废弃** |
| V3-06 | A3.2 correction 修复 | DEV | 0.5d | semantic_classifier.py | 分类准确度 P0 |
| V3-07 | A3.5 sentiment 修复 | DEV | 0.5d | distillation.py | 分类准确度 P0 |
| V3-08 | **MCE-Bench 180-case** | **QA** | **1d** | **tests/benchmark/classification_accuracy.py** | **新增: 分类准确率基准 (P0 升级)** |
| V3-09 | **Fuzz Testing (1000 cases)** | **QA+DEV** | **0.5d** | **tests/fuzz/test_classify_fuzz.py** | **新增: 分类器稳定性** |
| V3-10 | **MCP 集成测试 (4 工具)** | **QA** | **0.5d** | **tests/integration/test_mcp_pure_upstream.py** | **替换旧的 11 工具集成测试** |
| V3-11 | 文档更新 | PM | 0.5d | STORAGE_STRATEGY.md 完善 + Migration Guide | 含 v0.2→v0.3 迁移路径 |
| V3-12 | Case Study | PM | 1d | docs/case_studies/mce_plus_supermemory.md | "MCE + Supermemory = 完整链路" |
| V3-13 | 全量回归 | QA | 0.5d | — | 目标: 全绿 + 准确率 >85% |

### Phase 3: 内容营销 (与 Phase 2 并行) — **重写: 围绕"分类优先"叙事**

| # | 任务 | Owner | 说明 |
|---|------|-------|------|
| F3-1 | MCP 社区提交 | PM | 强调 "Classification-only MCP for AI Memory" |
| F3-2 | **"Classification First" 英文文章** | PM | **核心营销文: 为什么分类比存储更重要** |
| F3-3 | Reddit r/ClaudeAI | PM | "I built a pre-filter for your AI memory system" |
| F3-4 | GitHub Discussions | PM | "Show HN: MCE — Memory Classification Middleware" |
| F3-5 | 30s demo GIF/视频 | PM | 展示: Claude Code → MCE classify → JSON 输出 |

---

## 6. 竞品定位图更新 (v3 — 路线 B 版)

```
                    复杂度/功能完整度 ↑
                                  │
         MemOS (学术)          M-FLOW (学术前沿)    Cognee (企业)
              Graphiti (时序)                          
                                                   
Mem0 (易用)                                          Supermemory (全能平台)
          ↖️ 下游客户                                   ↙️ 下游客户
              
              ● MCE (记忆分类中间件) ★ ← 我们在这里
              ╱   ╲
    纯分类(MCP 4工具)    StorageAdapter(插件式扩展)
        
         Memori (SQL轻量)                        
                                                   
         MemPalace (存档)    GBrain (知识加工)          
                    │
                    简单度/易用性 ↑
```

**关键变化** (vs v2 定位图):
- MCE 从 "分类引擎" 明确为 **"记忆分类中间件"**
- 新增箭头指向 Mem0/Supermemory: **"下游客户"** 关系（非竞争）
- MCE 内部分为两圈: 内圈=纯分类(核心)，外圈=StorageAdapter(扩展)
- Y 轴坐标下移: 功能完整度降低（砍掉存储），但**定位更精准**

---

## 7. 风险与缓解

### 7.1 关键风险

| # | 风险 | 概率 | 影响 | 缓解措施 |
|---|------|------|------|----------|
| R-1 | 现有 v0.2.0 用户依赖 8 个存储工具 | 高 | 中 | v0.3.0 提供 6 个月共存期（Deprecated 非 Delete）；提供数据迁移脚本 |
| R-2 | "只有 3 个分类工具"显得功能太少 | 中 | 低 | 用 `get_classification_schema` 补充信息密度；强调"少即是精" |
| R-3 | 下游不知道怎么接 MCE | 中 | 中 | STORAGE_STRATEGY.md + 4 种集成示例 + Supermemory/Obsidian 适配器 |
| R-4 | 分类准确率 <80%，失去可信度 | 中 | **致命** | V3-08 MCE-Bench 180-case 必须在 v0.3.0 前完成; 准确率目标 >85% |
| R-5 | Supermemory 自己加了分类功能 | 低 | 高 | 加速建立分类质量护城河；MCE 的 7 类型体系是他们短期内无法复制的 |

### 7.2 R-4 深入讨论: 分类准确率是生死线

**论断**: 路线 B 的核心假设是 **"MCE 的分类质量足够好，好到用户愿意为此单独引入一个组件"**。

如果分类准确率只有 60%（demo 测试中的数据），那么:
- 用户会想: "还不如我自己 if/else 判断"
- 或者: "不如让 Supermemory 全存，靠检索时候的语义相似度过滤"
- **MCE 失去存在理由**

**因此 V3-08 (MCE-Bench 180-case) 不是"锦上添花"，而是"生存必需"。**

**目标设定**:
- v0.3.0 发布时: **准确率 >85%** (清晰消息)
- v0.4.0: **准确率 >90%** (含边界 case)
- v1.0.0: **准确率 >95%** (接近人类水平)

---

## 7.5 🔄 分层解耦新架构评审 (v3.1 补充)

**日期**: 2026-04-19 (Phase A+B 完成后)
**触发**: 用户提出"如果我解耦呢？默认 SQLite 实现"方案
**参与方**: PM / ARCH / QA / DEV + WORKBUDDY AI 顾问

### 7.5.1 提案概述

**核心思想**: 从"纯上游不存存储"升级为"分层解耦 + 默认可用"

```
三层架构:
┌─────────────────────────────────────────────────────┐
│ Layer 1: 引擎层 (MCE Core) ★ 核心资产              │
│  • 只管分类: message → MemoryEntry JSON           │
│  • 零外部依赖（纯规则 + 可选 ML）                  │
│  • 分类准确率是唯一 KPI                             │
└──────────────────────┬──────────────────────────────┘
                       │ MemoryEntry (JSON)
                       ▼
┌─────────────────────────────────────────────────────┐
│ Layer 2: 适配器层 (Storage Adapters)                │
│  • 统一接口: remember() / recall() / forget()      │
│  • ABC 定义契约，任何存储实现即可                    │
│  • 官方适配器: Supermemory / Mem0 / Obsidian        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Layer 3: 默认实现 (SQLite Adapter)                   │
│  • 开箱即用: pip install 后无需配置                 │
│  • SQLite 一文件搞定                                 │
│  • CRUD + FTS5 语义检索 + 遗忘机制                  │
└─────────────────────────────────────────────────────┘

叙事: "默认就能用，不满意可换"
类比: "引擎是心脏，适配器是血管，SQLite 是起搏器"
```

### 7.5.2 分类漏斗职责定义 (v3.3 新增)

**核心原则**: 规则层是成本控制器，不是分类器。每层有明确的召回率目标和职责边界。

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: Rule Matcher (规则匹配)                               │
│   职责: 快速捞出明确信号，降低下游计算成本                       │
│   目标: Recall 40-50%, Precision ≥95%                         │
│   成本: 0ms LLM, <1ms 总耗时                                  │
│   定位: 成本控制器 — 不是分类器                                 │
│   覆盖: 正则匹配(邮箱/电话/URL/日期) + 关键词(like/prefer)      │
│   产出: 高置信度匹配(confidence=1.0)，直接返回不进入下游         │
├──────────────────────────────────────────────────────────────┤
│ Layer 2: Pattern Analyzer (模式分析)                           │
│   职责: 结构化模式识别（语法+语义混合），处理规则层漏掉的信号     │
│   目标: Recall 70-80%, Precision ≥90%                         │
│   成本: 0ms LLM, <5ms 总耗时                                  │
│   定位: 信号增强器 — 核心分类层                                 │
│   覆盖: 3-tier检测(correction/fact/preference等) + 噪声过滤    │
│   产出: 多类型匹配(可同时输出fact+relationship)                 │
├──────────────────────────────────────────────────────────────┤
│ Layer 3: Semantic Classifier (语义分类)                        │
│   职责: 捕获模糊但高价值的信号，兜底保障                        │
│   目标: Recall 90%+, Precision ≥85%                           │
│   成本: 可选LLM, 50-200ms                                     │
│   定位: 兜底保障 — 处理前两层无法判断的边界case                  │
│   覆盖: embedding相似度 + 可选LLM推理                          │
│   产出: 低置信度匹配(confidence<0.6)，标记suggested_action=defer│
└──────────────────────────────────────────────────────────────┘

关键设计决策:
1. 规则层匹配后直接返回，不进入下游 → 节省90%+计算成本
2. Pattern Analyzer 可输出多类型 → 一条消息可以同时是fact+relationship
3. Semantic Classifier 是可选层 → 无LLM时仍可工作(降级到Pattern层)
4. 噪声过滤在Pattern层入口执行 → 确保不浪费下游计算资源
```

**关键词清单维护原则**:

规则层的关键词不可能穷举所有表达方式。维护方向：
- ✅ 收集**明确信号词**（prefer/decided/correction）→ 高Precision
- ✅ 补充**否定偏好词**（不太喜欢/不打算）→ 提升隐式偏好覆盖
- ✅ 补充**过去式声明**（之前说过/上次提到）→ 提升事实覆盖
- ✅ 补充**比较倾向词**（更喜欢/相比之下）→ 提升偏好覆盖
- ❌ 不追求覆盖**隐式/文化表达**（"这个还可以吧"）→ 交给语义层
- ❌ 不追求覆盖**问句倾向**（"为什么不直接用SQLite?"）→ 交给语义层

### 7.5.4 WORKBUDDY AI 评价 (已采纳)

> "这个思路比'纯上游只做分类'要好，而且更务实。本质上你做的是**分层解耦**，不是砍掉存储，而是把存储从核心引擎里拆出来变成可插拔的后端。
>
> **对用户**: 小白用户一行命令装完就能用，和 Supermemory 体验差不多，上手零门槛。进阶用户可以换成 PostgreSQL/Supabase/Mem0。
>
> **对你来说**: 引擎层代码完全不用管存储的事，测试干净，分类准确率才是唯一 KPI。SQLite 适配器是独立模块，写得粗糙也没关系。
>
> **唯一的权衡**: 精力分配。建议**引擎层稳定之后再做 SQLite 适配器**，别同时开两条线。
>
> 一句话：**心脏先做强，再搭血管。**"

### 7.5.5 四方角色评审矩阵

| 角色 | 投票 | 核心条件 | 主要顾虑 |
|------|------|---------|---------|
| 👨‍💼 PM | ✅ 强烈支持 | 上手≤3步，叙事一致 | #1 会否稀释定位? #2 SQLite 够用? |
| 🏗️ ARCH | ✅ 有条件支持 | Engine 先于 Adapter | #3 是否拖累开发? #4 Schema 分层? |
| 🧪 QA | ✅ 支持 | 契约测试覆盖 | #5 质量标准? #6 回归风险? |
| 💻 DEV | ✅ 支持 | 代码量可控 | #7 依赖膨胀? #8 维护成本? |

### 7.5.6 顾虑清单与解答

#### 🔴 PM 顾虑

**#1 会否稀释"纯上游"定位？**
- **顾虑**: 加了 SQLite 后又变成带存储的系统
- **解答**: ❌ 不会。关键在**分层清晰**
  - 对外叙事: MCE 是分类引擎，SQLite 是"让你能跑起来"的便利选项
  - 类比: Express.js 不因自带 session 存储就变成数据库框架
  - 文档明确标注: SQLite = 开发/演示用, 生产环境推荐切换下游

**#2 SQLite 会被吐槽"玩具级存储"吗？**
- **解答**: ⚠️ 可能，但通过**分级定位**缓解
  - ✅ 开发/Demo/个人项目 → SQLite 默认够用
  - ⚠️ 生产/团队协作 → 推荐切换到 Supermemory/Mem0
  - 🔧 高级需求 → 自定义 Adapter
  - 文档示例: FastAPI 的 Uvicorn (dev) vs Gunicorn (prod)

#### 🟡 ARCH 顾虑

**#3 SQLite Adapter 开发会拖累 Engine 吗？**
- **解答**: ❌ 不会，**严格串行依赖**
  ```
  P0: Engine v0.4.0 (Accuracy ≥85%) ← 当前进行中
       ↓
  P1: StorageAdapter ABC (1-2天, 接口定义)
       ↓  
  P2: SQLite Adapter v0.5 (3-5天, 基础CRUD) ← 后续迭代
  ```
  - Engine pytest 不 import sqlite3
  - SQLite 测试独立在 tests/adapters/

**#4 MemoryEntry Schema 需要为存储扩展吗？**
- **解答**: ✅ 采用**双层 Schema 设计**
  ```python
  # Layer 1: Classification Output (Engine 定义, 不可变)
  @dataclass
  class MemoryEntry:
      id, type, content, confidence, tier, source_layer, suggested_action, metadata
  
  # Layer 2: Storage Extension (Adapter 定义, 可扩展)
  @dataclass
  class StoredMemory(MemoryEntry):
      created_at, updated_at, storage_key, vector_embedding, expiry_date
  ```
  - Engine 只产出 Layer 1, Layer 2 由 Adapter 在存储时附加

#### 🟢 QA 顾虑

**#5 SQLite 质量标准是什么？需要 881 tests 吗？**
- **解答**: ❌ 不需要，**分级别标准**
  | 组件 | 覆盖率目标 | 关键指标 |
  |------|-----------|---------|
  | Engine Core | ≥95% | MCE-Bench F1≥85% |
  | StorageAdapter ABC | 100% | 所有方法有 mock test |
  | SQLite Adapter | ≥80% | CRUD+FTS+遗忘 smoke test |

**#6 Engine 升级如何不破坏 Adapter？**
- **解答**: ✅ **契约测试（Contract Testing）**
  - 定义 `TestStorageAdapterContract` 基类
  - 所有 Adapter 必须继承并通过
  - Engine 升级只需跑 Engine tests + Contract tests

#### 💻 DEV 顾虑

**#7 代码量会增加多少？**
- **解答**: 预估 **+800~1100 lines**
  | 模块 | 行数 | 复杂度 |
  |------|------|--------|
  | StorageAdapter ABC | ~100 | 低 |
  | SQLite Adapter | ~500-800 | 中 |
  | CLI/Web wrapper | ~200 | 低 |
  - **对比收益**: 上手门槛↓90%, Issue复现↑10x, Demo成本↓80%

**#8 会引入新依赖吗？**
- **解答**: ❌ Engine 保持零依赖
  ```
  pip install memory-classification-engine       # 仅 Engine (零依赖)
  pip install memory-classification-engine[sqlite] # + SQLite (可选)
  ```
  - Python 内置 sqlite3 模块就够用
  - `apsw` 只是性能优化（可选 extras）

### 7.5.7 共识结论

```
✅ 全票通过: 采用「分层解耦」新架构 (v3.1 更新)

四大原则:
1. ★★★★★ Engine First: 分类准确率 ≥85% 才启动 Adapter
2. Interface Before Implementation: ABC 先行，实现后继
3. Default but Replaceable: SQLite = 便利选项, 不是锁定
4. Test Isolation: Engine 测试零存储依赖

执行路线图:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
当前 (v0.3.0 Phase A+B):  Classification Accuracy Overhaul
  ↓ [进行中]
P0: Engine v0.4.0 (Accuracy ≥85%, F1≥82%)     ← 当前目标
  ↓ [预估 1-2 周]
P1: StorageAdapter ABC + Interface Spec         ← 新增
  ↓ [预估 3-5 天]
P2: SQLite Adapter v0.5 (Basic CRUD)            ← 新增
  ↓ [预估 2-3 天]  
P3: SQLite v0.6 (FTS5 + Forgetting Mechanism)   ← 新增
  ↓ [v0.7+]
P4: Official Adapters (Supermemory/Mem0/Obsidian)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

架构影响评估:
┌─────────────────────┬──────────┬──────────┐
│ Metric               │ v3.0     │ v3.1     │
├─────────────────────┼──────────┼──────────┤
│ MCP Tools            │ 4        │ 4 (不变) │
│ Code (layer2_mcp/)  │ ~650行   │ ~650行   │
│ New: adapters/      │ N/A      │ ~1000行  │
│ Total Project Size  │ ~15K行   │ ~16K行   │
│ Test Cases          │ 881      │ 881+     │
│ Dependencies        │ 零       │ 零(核心) │
│ User Onboarding     │ 5 steps  │ 1 step  │ ✅
│ Narrative           │ "安检机"  │ "安检机+起搏器" ✅
└─────────────────────┴──────────┴──────────┘
```

---

## 8. 共识签字 (v3.1 更新)

```
================================================================================
        MCE MCP 纯上游路线 × 分层解耦 × 四方共识 (v3.1)
                    2026-04-19 (Phase A+B 完成后)
================================================================================

战略决策 (v3.0 继承):
  ✅ 路线 B 确认: MCP Server 只暴露分类接口 (4 工具)
  ✅ StorageAdapter ABC 作为核心抽象层
  ✅ MemoryEntry JSON Schema v1.0 作为标准输出格式
  ✅ Supermemory/Mem0/Obsidian 重分类为"下游客户"

新增决策 (v3.1 分层解耦):
  ✅ 三层架构: Engine Core → Storage Adapters → SQLite Default
  ✅ "默认就能用，不满意可换" 叙事升级
  ✅ Engine First 原则: Accuracy ≥85% 后才启动 Adapter 开发
  ✅ 双层 Schema: MemoryEntry (Engine) → StoredMemory (Adapter)
  ✅ 契约测试模式: TestStorageAdapterContract 保证兼容性

关键数据 (Phase A+B 成果):
  - Precision: 40.5% → 94.1% (+53.6pp) ✅
  - F1 Score: 57.7% → 84.2% (+26.5pp) ✅
  - FP Rate: 40% → 0.6% (-99%) ✅
  - TN (True Negatives): 0 → 54 ✅
  - Tech Terms Whitelist: 7 → 200+ terms ✅
  - CRITICAL BUG FIX: analyze() method truncation resolved ✅

顾虑统计:
  v3.0 原有顾虑: 19 项 (全部解决或升级)
  v3.1 新增顾虑: 8 项 (#1~#8, 全部解答)
  总顾虑: 27 项

推进计划:
  当前 → P0: Engine v0.4.0 (Accuracy ≥85%) [进行中]
       → P1: StorageAdapter ABC [预估 1-2 天]
       → P2: SQLite Adapter v0.5 [预估 3-5 天]
       → P3: FTS + Forgetting [预估 2-3 天]
       → P4: Official Adapters [v0.7+]

SIGNATURES:

  👔 Product Manager:     ✅ APPROVED    Date: 2026-04-19
    核心观点 (v3.0): "叙事终于一致了。竞品变客户是最爽的战略转型。"
    核心观点 (v3.1): "上手门槛从5步降到1步，'安检机+起搏器'比单纯'安检机'更有说服力。SQLite不会稀释定位，反而解决了最大痛点：拿到JSON后还得自己搭存储。"

  🏗️ Architect:           ✅ APPROVED    Date: 2026-04-19
    核心观点 (v3.0): "架构复杂度降 60%，StorageAdapter 是正确的抽象。"
    核心观点 (v3.1): "分层解耦比纯上游更务实。Engine零依赖保持不变，Adapter是独立模块。双层Schema设计让Engine和Storage完全解耦。串行依赖策略（Engine First）避免了精力分散风险。"

  🧪 Test Expert (QA):    ✅ APPROVED    Date: 2026-04-19
    核心观点 (v3.0): "测试矩阵减半且无DB依赖。MCE-Bench 180-case是生存必需。"
    核心观点 (v3.1): "契约测试模式确保Engine升级不破坏Adapter。分级质量标准（Engine≥95%, ABC=100%, SQLite≥80%）让资源分配更合理。PhaseA+B的Precision94.1%证明分类质量已达生产候选水平。"

  💻 Developer:           ✅ APPROVED    Date: 2026-04-19
    核心观点 (v3.0): "维护成本减半，贡献者友好度大幅提升。"
    核心观点 (v3.1): "+800~1100行代码换来了上手门槛↓90%、Issue复现↑10x、Demo成本↓80%。这个ROI太值了。而且Engine保持零依赖，SQLite通过extras可选安装，完美。"

  🤖 WORKBUDDY AI:      ✅ ENDORSED   Date: 2026-04-19
    核心观点: "'心脏先做强，再搭血管'——这是最务实的路径。Express.js不因自带session就变成数据库框架，MCE也不会因自带SQLite就变成存储系统。分层清晰是关键。"

CONSENSUS: ✅ UNANIMOUS (5/5) — 执行 Engine v0.4.0 (Accuracy ≥85%) → ABC Interface → SQLite Adapter
================================================================================

---

## 8. Engine First 门槛调整 — 决策 C (v3.2, 2026-04-20)

### 8.1 背景

V4-01~05 完成后，MCE-Bench 数据：

```
┌─────────────────────┬──────────┬──────────┬──────────┐
│ Metric               │ v3.1目标  │ v3.2实际  │ 差距      │
├─────────────────────┼──────────┼──────────┼──────────┤
│ Accuracy             │ ≥85%     │ 71.7%    │ -13.3pp  │
│ F1 Score             │ ≥75%     │ 90.7%    │ ✅ +15.7pp│
│ Precision            │ ≥80%     │ 86.1%    │ ✅ +6.1pp │
│ Recall               │ ≥80%     │ 84.4%    │ ✅ +4.4pp │
│ Types with F1≥50%    │ 7/7      │ 6/7      │ -1类型   │
└─────────────────────┴──────────┴──────────┴──────────┘
```

**关键发现**:
- F1/Precision/Recall 全部超额达标
- 6/7 类型F1≥50%，唯一弱项fact_declaration(40%)是pipeline优先级问题而非根本缺陷
- Accuracy gap从46.1pp降到13.3pp，**已关闭71%**

### 8.2 三选项评估

| 选项 | 门槛 | 优点 | 风险 |
|------|------|------|------|
| A | 保持85% | 最高质量 | 需2-3轮迭代，推迟ABC |
| B | 降至75% | 当前71.7%接近达标 | 略降低标准 |
| **C** | **并行推进** | **不阻塞ABC开发** | **资源分两条线** |

### 8.3 决策 C: 并行推进

**决策**: 选择选项C — 一边继续V4优化，一边启动v0.5 ABC定义

**理由**:
1. **F1=90.7%证明引擎足够强壮** — "心脏"已经在有效跳动
2. **fact_declaration 40%是可修复的优先级问题** — 直接检测已达66.7%
3. **ABC定义不依赖Accuracy 85%** — 接口设计是独立工作
4. **并行推进加速整体进度** — V4优化和ABC定义互不阻塞

**执行计划**:
```
并行轨道:
├── 轨道A: V4优化 (V4-06~10)
│   ├── V4-06: fact_declaration pipeline TP 5→8
│   ├── V4-07: FP清理 11→<8
│   └── V4-08: Multi-type handling
│
└── 轨道B: v0.5 ABC定义 (V5-01~04)
    ├── V5-01: StorageAdapter ABC接口
    ├── V5-02: StoredMemory dataclass
    ├── V5-03: Contract Tests
    └── V5-04: Adapter开发指南
```

### 8.4 签名确认 (v3.2)

**决策日期**: 2026-04-20
**决策内容**: Engine First门槛调整 — 选择选项C并行推进

SIGNATURES (v3.2):

  👔 Product Manager:     ✅ APPROVED
    "F1=90.7%说明分类质量已经很强。并行推进让产品更快到达用户手中。"

  🏗️ Architect:           ✅ APPROVED
    "ABC接口定义与引擎优化完全解耦，并行是合理的架构决策。"

  🧪 Test Expert (QA):    ✅ APPROVED
    "Contract Tests可以独立于引擎优化进行，不影响质量保证。"

  💻 Developer:           ✅ APPROVED
    "并行开发意味着更快看到完整产品，动力更足。"

  🤖 WORKBUDDY AI:      ✅ ENDORSED
    "心脏已经在有力跳动(90.7% F1)，可以开始搭血管了。并行是最务实的路径。"

CONSENSUS: ✅ UNANIMOUS (5/5) — 执行并行推进: V4优化 + v0.5 ABC定义
================================================================================

---

## 8.5 已知边界与信息缺口 (v3.3, 2026-04-20)

### 8.5.1 核心边界：MCE 只分类用户输入

**设计原则**: MCE 只处理用户发送的消息，不分类 AI 的回复/输出。

**理由**:
1. AI 输出量大且冗余，全量分类会导致记忆暴增
2. AI 输出是"服务"而非"偏好"，分类价值低
3. 用户输入才是真正的记忆信号源

### 8.5.2 信息缺口分析（~15% 覆盖率缺口）

| 缺口模式 | 示例 | 当前分类结果 | 理想结果 | 缺口原因 |
|----------|------|-------------|---------|---------|
| 用户确认AI建议 | AI: "建议用SQLite" → 用户: "行，这样搞" | decision（内容不完整） | decision（含AI建议内容） | 用户没复述AI建议 |
| 用户接受AI输出 | AI: 写完文章 → 用户: "好，就这样" | sentiment_marker 或 noise | decision（认可方向） | 确认词被当作闲聊 |
| 用户隐式纠正 | "上次那个方案其实没那么好" | 可能漏检 | correction | 无明确纠正关键词 |

### 8.5.3 解决方案路线

| 方案 | 描述 | 优先级 | 版本 |
|------|------|--------|------|
| **A: context 参数增强** | `classify_message` 的 `context` 参数传入上一条 AI 回复，当检测到用户确认/接受时，将 AI 回复摘要附入 content | P1 | v0.5 |
| **B: 接受确认词扩展** | 补充"好的/行/就这样/可以/没问题"等接受确认词到 decision 检测器 | P1 | v0.4 |
| **C: recall_hint 字段** | MemoryEntry 输出 `recall_hint` 字段，建议未来检索触发条件 | P2 | v0.6+ |

**方案 A 的实现思路**:
```python
# classify_message 的 context 参数增强
result = mce.classify_message(
    message="行，这样搞",
    context="AI建议: 使用SQLite作为默认存储方案"  # 上一条AI回复
)

# 当检测到用户确认模式时，自动合并上下文
# 输出: {"type": "decision", "content": "确认采用SQLite作为默认存储方案"}
```

**不采用的方案**: 直接分类 AI 输出 — 会导致记忆量暴增 3-5 倍，且 AI 输出的分类价值低。

### 8.5.4 关键词维护方向

当前规则层的关键词清单以**主动表达词**为主（我想/我喜欢/我偏好），需要补充以下四类：

| 类别 | 示例（中文） | 示例（英文） | 目标类型 |
|------|-------------|-------------|---------|
| **否定偏好词** | 不太喜欢/不打算/不想再/别用 | don't like/would rather not/stop using | user_preference |
| **过去式声明** | 之前说过/上次提到/我提过 | I mentioned before/as I said/last time | fact_declaration |
| **比较倾向词** | 更喜欢/相比之下/还是X好 | prefer X over/rather go with/X is better | user_preference |
| **接受确认词** | 好的/行/就这样/可以/没问题 | okay/sounds good/go ahead/let's do it | decision (需context) |

**维护原则**: 规则层的意义在于降低 LLM 触发频率，而不是取代语义理解。关键词清单不可能穷举，目标是覆盖 40-50% 的明确信号，剩余交给 Pattern Analyzer 和 Semantic Classifier。

---

## 9. CarryMem 产品方向决策 (v4.0, 2026-04-20)

### 9.1 战略转折：从分类中间件到随身记忆库

**转折动因**:

1. **创始人本心**: "让普通人和 AI 之间的记忆能被保留下来的东西" — 分类引擎是手段，不是目的
2. **文章叙事矛盾**: 第8篇承诺"5行代码接入，AI就能记住你"，但纯分类只交付了 JSON，用户还得自己接存储
3. **热情缺口**: "只做分类让我失去了热情" — 因为产品只交付了引擎，没有交付体验
4. **11篇文章叙事链**: 从"帮别人落地AI" → "记忆系统建设者" → "战略收缩到分类" → 现在需要回到完整愿景

**核心判断**: MCE 分类引擎是 CarryMem 里面最难的部分，是壁垒。但它不再是 CarryMem 的全部。

### 9.2 产品命名

| 层级 | 名称 | 定位 | 类比 |
|------|------|------|------|
| **产品名** | CarryMem | 随身记忆库，对外品牌 | MySQL |
| **引擎名** | MCE | 分类引擎，内部模块 | InnoDB |
| **中文名** | 随身记忆 | 定位描述 | — |

**命名理由**: "带着你的记忆走" — 简洁、动作感强、准确传达产品核心理念。

**可用性**: GitHub / npm / PyPI 均无同名项目。

### 9.3 四步产品路线

```
Step 1: 引擎 (MCE) ─── 已完成 ✅
  · 分类准确率 90.6%, F1 97.9%
  · 7/7 类型 F1≥50%
  · 60% 零 LLM 成本
  · 这是技术壁垒，别人很难复制

Step 2: 默认存储 (SQLite) ─── v0.6 目标
  · 可选的轻量存储实现
  · 不只存分类结果，还存原始记忆内容
  · 提供 remember / recall / forget 三个接口
  · pip install carrymem → 三行代码接入
  · ★ 这是兑现"AI就能记住你"承诺的关键一步

Step 3: 知识库适配 (Obsidian 等) ─── v0.7 目标
  · 把用户的个人笔记作为第二检索源
  · 分类时打标签标注与笔记主题的关联
  · 检索时先查记忆库，再查知识库
  · 技术方案: 直接读 Markdown 文件 + FTS5 索引

Step 4: 智能调度 ─── v0.8+ 考虑
  · "先本地后外部"的检索策略
  · 可能是 prompt 模板 + MCP 工具编排
  · 不一定是 CarryMem 的代码，但可以作为生态的一部分
```

**每一步独立可交付**，不依赖后续步骤。

### 9.4 MCP 工具重新规划 (3+3 可选模式)

**核心原则**: 引擎层永远纯净，存储层永远可替换。

| 工具 | 类型 | 描述 | 可用条件 |
|------|------|------|---------|
| `classify_message` | 核心 | 分类单条消息 | 永远可用 |
| `get_classification_schema` | 核心 | 查看 Schema | 永远可用 |
| `batch_classify` | 核心 | 批量分类 | 永远可用 |
| `classify_and_remember` | 可选 | 分类+存储一键完成 | 需配置 adapter |
| `recall_memories` | 可选 | 检索记忆(按type/tier过滤) | 需配置 adapter |
| `forget_memory` | 可选 | 删除记忆 | 需配置 adapter |

**与 v3.0 的 11 工具的本质区别**:
- v3.0: 存储逻辑硬编码在 handler → **耦合**
- v4.0: 存储通过 StorageAdapter ABC → **解耦**
- v3.0: 不配 DB 就不能用 → **必选**
- v4.0: 没有 adapter 时 3 个核心工具照常工作 → **可选**

### 9.5 目标用户分层

| 优先级 | 用户 | 需求 | CarryMem 交付 | 版本 |
|--------|------|------|-------------|------|
| **P0** | 开发者 | 三行代码接入，Agent 能记住用户偏好 | classify + SQLite 默认存储 | v0.6 |
| **P1** | Agent 产品团队 | 生产级存储，性能数据，SLA | Supermemory/PostgreSQL 适配器 | v0.7 |
| **北极星** | 终端用户 | "AI 记得我" | 通过 Agent 产品间接触达 | v1.0+ |

**关键判断**: 开发者是唯一能在当前阶段付费/贡献的用户。但终端用户的体验是产品设计的北极星——每个技术决策都要问"这能让 Agent 更好地记住用户吗？"

### 9.6 命名迁移方案

| 阶段 | 版本 | 动作 | 兼容性 |
|------|------|------|--------|
| 1 | v0.5 | 内部代码保持 MCE，文档开始用 CarryMem | 100% 兼容 |
| 2 | v0.6 | PyPI 包名 `carrymem`，`mce` 作为别名 | 双包名兼容 |
| 3 | v0.7 | GitHub 仓库重命名 `carrymem`，旧名重定向 | URL 兼容 |
| 4 | v1.0 | `mce` 别名标记 deprecated | 6个月过渡期 |

### 9.7 检索优先级策略

**创始人原话**: "先在个人记忆和个人知识库内寻求资料，判断，不够再去外部大模型寻找思路。"

```
检索优先级:
  Layer 1: 记忆库 (SQLite/其他 adapter)
    → recall_memories(type="user_preference", limit=5)
    → recall_memories(type="decision", limit=3)

  Layer 2: 知识库 (Obsidian adapter)
    → recall_from_knowledge(query="当前话题", limit=3)

  Layer 3: 外部 LLM (Agent 自己决定)
    → 不在 CarryMem 范围内

实现位置: Agent 的 system prompt 里定义检索策略
CarryMem 的角色: 提供结构化的 recall 接口，让策略可编程
```

### 9.8 四方角色评审

| 角色 | 投票 | 核心判断 | 主要顾虑 |
|------|------|---------|---------|
| 👔 PM | ✅ 支持 | 文章叙事终于和产品对齐了 | 命名迁移的沟通成本 |
| 🏗️ ARCH | ✅ 支持 | 解耦架构没变，只是加了默认实现 | 3+3 工具模式的复杂度 |
| 🧪 QA | ✅ 支持 | 引擎测试不受影响，适配器独立测试 | 集成测试覆盖度 |
| 💻 DEV | ✅ 支持 | 代码改动量可控，核心不变 | 双包名维护成本 |

**CONSENSUS**: ✅ UNANIMOUS — CarryMem 方向确认，引擎已完成，下一步 SQLite 默认存储

================================================================================
CONSENSUS: ✅ UNANIMOUS (5/5) — CarryMem: 分类是核心壁垒，存储让体验完整
================================================================================

---

## 10. CarryMem v0.5 文档评审 (v4.0, 2026-04-20)

### 10.1 文档清单

| # | 文档 | 路径 | 状态 |
|---|------|------|------|
| 1 | 用户故事 | [CARRYMEM_USER_STORIES.md](../planning/CARRYMEM_USER_STORIES.md) | ✅ 完成 |
| 2 | 解耦架构图 | [CARRYMEM_ARCHITECTURE_v4.md](../architecture/CARRYMEM_ARCHITECTURE_v4.md) | ✅ 完成 |
| 3 | 设计文档 | [CARRYMEM_DESIGN_v4.md](../architecture/CARRYMEM_DESIGN_v4.md) | ✅ 完成 |
| 4 | 测试计划 | [CARRYMEM_TEST_PLAN_v4.md](../testing/CARRYMEM_TEST_PLAN_v4.md) | ✅ 完成 |
| 5 | 命名迁移计划 | [CARRYMEM_MIGRATION_PLAN.md](../planning/CARRYMEM_MIGRATION_PLAN.md) | ✅ 完成 |

### 10.2 四方评审矩阵

| 角色 | 投票 | 核心判断 | 顾虑 | 需确认 |
|------|------|---------|------|--------|
| 👔 PM | ✅ 通过 | 用户故事覆盖 P0~北极星全层级 | US-009/010 何时兑现 | 已确认: 不需要用户调研 |
| 🏗️ ARCH | ✅ 通过 | 3+3 解耦架构清晰，SQLite Schema 合理 | context 合并逻辑的边界 | 已确认: recall_hint v0.6预留null |
| 🧪 QA | ✅ 通过 | 6 层测试覆盖，EN/CN/JP 各 30 条 | 日文分类准确率可能偏低 | 已确认: 日文≥80% |
| 💻 DEV | ✅ 通过 | 包结构清晰，迁移方案分阶段 | 内部 import 替换量大 | 已确认: v0.6分支保护 |

### 10.3 待确认事项

| # | 问题 | 提出者 | 建议 | 决策 |
|---|------|--------|------|------|
| 1 | 品牌名是否需要用户调研？ | PM | 不需要，11篇文章已验证 | ✅ 不需要 |
| 2 | recall_hint 字段何时实现？ | ARCH | v0.6 预留 null，v0.7 实现 | ✅ v0.6 预留 null |
| 3 | 日文分类准确率目标？ | QA | ≥80%（当前无日文规则，依赖语义层） | ✅ ≥80% |
| 4 | Phase 2 是否需要分支保护？ | DEV | 是，创建 carrymem-v0.6 分支 | ✅ 是 |
| 5 | 本地目录何时重命名？ | DEV | v0.6 开始开发时 | ✅ v0.6 开发时 |
| 6 | GitHub 仓库何时重命名？ | DEV | v0.7 (Phase 3) | ✅ v0.7 |
