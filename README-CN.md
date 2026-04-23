# CarryMem

**你的随身 AI 记忆层。**

> 不要记住一切。只记住重要的。

CarryMem 为 AI Agent 提供持久、可携带的记忆层。它实时分类对话，存储值得记住的内容，让用户可以把记忆带到任何地方——跨模型、跨工具、跨设备。

**AI 记住你。而不是反过来。**

<p align="center">
  <img src="https://img.shields.io/badge/version-0.3.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-125%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/MCP-3%2B3%2B3%2B2%2B1-blue" alt="MCP">
  <img src="https://img.shields.io/badge/Accuracy-90.6%25-green" alt="Accuracy">
</p>

[English](README.md) | **中文** | [日本語](README-JP.md)

---

## 问题

每次你和 AI Agent 开始新对话，它都会忘记你。

你的偏好、你的纠正、你的决策——全部消失。你不断重复自己。Agent 推荐你已经否决的东西。从 Claude 换到 GPT，从 Cursor 换到 Windsurf，从一个 MCP 服务器换到另一个，就像重新认识一个陌生人。

现有方案有三个问题：

1. **记忆被锁定。** 大多数记忆工具把数据存在自己的系统里。换工具，丢记忆。
2. **什么都存。** 它们把整个对话倒进向量数据库，指望语义搜索能搞定。昂贵、嘈杂、缓慢。
3. **没有分类。** 不理解一条消息*是什么*（偏好？纠正？闲聊？），检索就是盲目的。

**60%+ 的消息不应该被存储。** 但现有系统要么全存（噪声爆炸），要么全不存（失忆）。

CarryMem 解决了这三个问题。

---

## 工作原理

```
用户消息 → MCE 引擎（分类）→ 存储层（存储）→ Agent 上下文（检索）
```

### 第一步：分类（MCE 引擎）

每条用户消息流经三层分类漏斗：

| 层级 | 方法 | 成本 | 覆盖率 |
|------|------|------|--------|
| 规则匹配 | 正则 + 关键词 | 零 | ~60% |
| 模式分析 | NLP 模式 | 近零 | ~30% |
| 语义推断 | LLM（仅按需） | Token 成本 | <10% |

**60%+ 的分类零 LLM 成本。**

### 第二步：分类为 7 种记忆类型

| 类型 | 描述 | 示例 |
|------|------|------|
| `user_preference` | 表述的喜好 | "我喜欢深色主题" |
| `correction` | 对 AI 的明确纠正 | "不对，我说的是 Python 版本" |
| `fact_declaration` | 关于用户的事实 | "我在东京一家创业公司工作" |
| `decision` | 做出的选择 | "我们用 React 吧" |
| `relationship` | 社交/上下文信息 | "我的队友负责后端" |
| `task_pattern` | 重复的工作模式 | "我总是先写 README" |
| `sentiment_marker` | 对输出的情感反应 | "这正是我需要的" |

### 第三步：按优先级分层存储

不是所有记忆都同等重要。CarryMem 为每条分类记忆分配一个层级：

| 层级 | 名称 | 默认 TTL | 描述 |
|------|------|---------|------|
| **Tier 1** | 感觉记忆 | 24 小时 | 临时信息，快速遗忘 |
| **Tier 2** | 程序性记忆 | 90 天 | 习惯/偏好，中期保留 |
| **Tier 3** | 情景记忆 | 365 天 | 重要事件，长期保留 |
| **Tier 4** | 语义记忆 | 永久 | 核心知识，永不过期 |

### 第四步：按需检索

当新对话开始时，CarryMem 将相关记忆注入 Agent 的上下文窗口。Agent 不仅仅是响应——它*记得*。

检索优先级：**记忆 > 知识库 > 外部 LLM**

---

## 快速开始

### 安装

```bash
pip install carrymem
```

### 分类 + 记忆（3 行代码）

```python
from carrymem import CarryMem

cm = CarryMem()  # 自动 SQLite 存储，位于 ~/.carrymem/memories.db
result = cm.classify_and_remember("我喜欢深色主题")
# → {"type": "user_preference", "confidence": 0.95, "stored": True}
```

### 主动声明偏好

```python
# 用户主动告知 AI 关于自己的信息
result = cm.declare("我喜欢深色主题")
# → confidence=1.0, source_layer="declaration", 一定存储
```

### 查看 AI 记住了什么

```python
profile = cm.get_memory_profile()
# → {
#     "summary": "AI 记住了关于你的 12 条信息：5个偏好、3个纠正、2个决策",
#     "highlights": {"user_preference": ["深色主题", "PostgreSQL"], ...},
#     "stats": {"by_type": {...}, "confidence_avg": 0.92}
#   }
```

### Obsidian 知识库

```python
from carrymem import CarryMem
from carrymem.adapters import ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()
results = cm.recall_from_knowledge("Python 设计模式")
```

### 项目级隔离

```python
cm_alpha = CarryMem(namespace="project-alpha")
cm_beta = CarryMem(namespace="project-beta")

cm_alpha.declare("我喜欢深色主题")   # 隔离在 project-alpha
cm_beta.declare("我喜欢浅色主题")    # 隔离在 project-beta

# 跨项目搜索
result = cm_alpha.recall_all("PostgreSQL", namespaces=["project-alpha", "global"])
```

### 智能系统提示词

```python
# 为你的 Agent 生成上下文感知的系统提示词
prompt = cm.build_system_prompt(context="深色主题", language="zh")
# → 包含相关记忆和知识库，按优先级排序
```

### 插件适配器

```python
# 通过 entry_points 加载第三方适配器
from carrymem.adapters import load_adapter, list_available_adapters

CustomAdapter = load_adapter("my_custom_adapter")
adapters = list_available_adapters()
# → {"sqlite": "...", "obsidian": "...", "my_custom_adapter": "... (plugin)"}
```

### 导出与导入（可携带性）

```python
# 导出你的记忆——它们属于你
result = cm.export_memories(output_path="my_memories.json")
# → {"exported": True, "total_memories": 42, "format": "json"}

# 导出为人类可读的 Markdown
result = cm.export_memories(output_path="my_memories.md", format="markdown")

# 导入到新的 CarryMem 实例（不同工具、不同设备）
cm2 = CarryMem(db_path="new_device.db")
cm2.import_memories(input_path="my_memories.json")
# → {"imported": 42, "skipped": 0, "errors": 0}
```

---

## MCP 服务器：3+3+3+2+1 可选模式

| 分组 | 工具 | 要求 |
|------|------|------|
| **核心 (3)** | `classify_message`, `get_classification_schema`, `batch_classify` | 始终可用 |
| **存储 (3)** | `classify_and_remember`, `recall_memories`, `forget_memory` | 存储适配器 |
| **知识库 (3)** | `index_knowledge`, `recall_from_knowledge`, `recall_all` | 知识库适配器 |
| **画像 (2)** | `declare_preference`, `get_memory_profile` | 存储适配器 |
| **提示词 (1)** | `get_system_prompt` | 存储适配器 |

### 配置

```json
{
  "mcpServers": {
    "carrymem": {
      "command": "python3",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
      "env": {}
    }
  }
}
```

---

## 对比

|  | CarryMem | Mem0 | LangMem | Zep |
|--|----------|------|---------|-----|
| **分类** | 实时，7 种类型 | 无（全量存储） | 通过 LLM 链 | 事后总结 |
| **存储** | 可携带（SQLite/你的 DB） | 锁定在 Mem0 云 | 锁定在 LangChain | 锁定在 Zep |
| **LLM 成本** | 60%+ 零成本 | 始终嵌入 | 始终 LLM | 始终 LLM |
| **记忆类型** | 7 种结构化类型 | 非结构化 | 3 种类型 | 2 种类型 |
| **遗忘** | 主动（4 层 TTL） | 仅 TTL | 手动 | 仅 TTL |
| **知识库** | Obsidian（只读） | 无 | 无 | 无 |
| **主动声明** | 是（confidence=1.0） | 否 | 否 | 否 |
| **项目隔离** | 基于命名空间 | 否 | 否 | 否 |
| **开源** | 完全 | 部分 | 完全 | 部分 |
| **可携带性** | 你的文件，带走 | 否 | 否 | 否 |

**关键区别：** CarryMem 的记忆是你的。不是我们的，不是任何人的。换模型、换工具、换设备——你的记忆跟着你。

---

## 性能

| 指标 | 数值 |
|------|------|
| 分类准确率 | **90.6%** |
| F1 分数 | **97.9%** |
| 集成测试 | **125/125 通过** |
| LLM 调用比例 | **<10%** |
| P50 延迟（规则匹配） | ~45ms |

---

## 架构

```
CarryMem（主类）
  ├── MCE 引擎（三层分类漏斗）
  │   ├── 规则匹配器（60%+ 命中，零成本）
  │   ├── 模式分析器（30%+ 命中，近零成本）
  │   └── 语义分类器（<10% 命中，LLM 回退）
  ├── 存储适配器（SQLite 默认，可替换）
  │   ├── SQLiteAdapter: FTS5 + 去重 + TTL + 命名空间
  │   ├── ObsidianAdapter: Markdown + Frontmatter + Wiki-links（只读）
  │   └── 插件适配器: 通过 entry_points
  ├── declare(): 主动声明（confidence=1.0）
  ├── get_memory_profile(): 结构化记忆画像
  ├── build_system_prompt(): 智能提示词生成（EN/CN/JP）
  ├── export_memories(): 导出记忆（JSON/Markdown）
  ├── import_memories(): 导入记忆（JSON）
  └── MCP 服务器: 3+3+3+2+1 工具
```

---

## 项目结构

```
carrymem/
├── src/memory_classification_engine/
│   ├── carrymem.py              # CarryMem 主类
│   ├── engine.py                # MCE 核心引擎（精简版）
│   ├── adapters/
│   │   ├── base.py              # StorageAdapter ABC + MemoryEntry + StoredMemory
│   │   ├── sqlite_adapter.py    # SQLite + FTS5 + 命名空间
│   │   ├── obsidian_adapter.py  # Obsidian（只读）
│   │   └── loader.py            # 插件适配器加载器
│   ├── layers/                  # 三层分类漏斗
│   ├── coordinators/            # 分类管道
│   ├── utils/
│   │   ├── confirmation.py      # 确认模式检测（EN/CN/JP）
│   │   └── ...
│   └── integration/layer2_mcp/  # MCP 服务器
├── tests/                       # 125 个测试通过
├── benchmarks/                  # MCE-Bench 180 用例数据集
├── docs/
│   ├── consensus/               # 战略决策
│   ├── architecture/            # 架构 + 设计文档
│   ├── planning/                # 用户故事 + 状态
│   └── testing/                 # 测试计划
└── setup.py                     # carrymem v0.3.0
```

---

## 适合谁？

**开发者** — 构建 AI Agent，需要跨会话记住用户。

**Agent 产品团队** — 需要持久记忆，但不想从零构建分类逻辑。

**高级用户** — 希望 AI 工具记住自己，而不是反过来。

---

## 许可证

MIT
