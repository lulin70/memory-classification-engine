# CarryMem

**AI 记住你。而不是反过来。**

> 你的随身 AI 记忆层 — 跨模型、跨工具、跨设备

CarryMem 是一个可携带的 AI 记忆系统，让 AI 助手记住你的偏好、纠正和决策。换工具不丢记忆，换设备随身携带。

[English](../../README.md) | **中文** | [日本語](README-JP.md)

<p align="center">
  <img src="https://img.shields.io/badge/version-0.6.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-308%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/accuracy-90.6%25-green" alt="Accuracy">
  <img src="https://img.shields.io/badge/zero--cost-60%25%2B-brightgreen" alt="Zero Cost">
</p>

---

## 🎯 为什么需要 CarryMem？

### 问题：AI 总是忘记你

每次新对话，AI 都像第一次认识你：
- ❌ 你的偏好？忘了
- ❌ 你的纠正？忘了
- ❌ 你的决策？忘了

换工具（Cursor → Windsurf），换模型（Claude → GPT），每次都从零开始。

### 解决方案：CarryMem

✅ **AI 自动记住你** — 偏好、纠正、决策自动分类存储
✅ **记忆可携带** — 导出/导入，换工具不丢数据
✅ **60%+ 零成本** — 智能分类，不浪费 Token
✅ **5 分钟上手** — 零配置，开箱即用

---

## ⚡ 快速开始

### 安装

```bash
pip install carrymem
```

### 第一条记忆（1 分钟）

```python
from memory_classification_engine import CarryMem

with CarryMem() as cm:
    # AI 自动分类并存储你的偏好
    cm.classify_and_remember("I prefer dark mode")
    cm.classify_and_remember("I use PostgreSQL for databases")
    cm.classify_and_remember("I work at a startup in Tokyo")

    # 召回记忆
    memories = cm.recall_memories(query="database")
    for mem in memories:
        print(f"{mem['type']}: {mem['content']}")
```

就这么简单！🎉 CarryMem 自动在 `~/.carrymem/memories.db` 创建数据库。

---

## 💡 核心功能

### 1. 自动分类（7 种记忆类型）

CarryMem 自动识别消息类型，只存储有价值的信息：

```python
cm.classify_and_remember("I prefer dark mode")
# → type: user_preference, confidence: 0.95

cm.classify_and_remember("No, I meant Python 3.11, not 3.10")
# → type: correction, confidence: 0.98

cm.classify_and_remember("Let's use React for the frontend")
# → type: decision, confidence: 0.92
```

**7 种记忆类型**：`user_preference` · `correction` · `fact_declaration` · `decision` · `relationship` · `task_pattern` · `sentiment_marker`

### 2. 语义召回（v0.4.0+）

```python
# 用中文存储，用英文查询 — 跨语言召回！
cm.classify_and_remember("我偏好使用PostgreSQL")

# 以下查询都能找到这条记忆：
memories = cm.recall_memories(query="PostgreSQL")      # ✅ 精确匹配
memories = cm.recall_memories(query="数据库")            # ✅ 同义词扩展
memories = cm.recall_memories(query="Postgres")          # ✅ 拼写纠正
memories = cm.recall_memories(query="データベース")      # ✅ 跨语言（日语）
```

**特性**：同义词扩展 · 拼写纠正 · 跨语言映射（中/英/日） · 零外部依赖

### 3. 主动声明

```python
cm.declare("I prefer PostgreSQL over MySQL")
# → confidence=1.0，保证被记住
```

### 4. 记忆画像

```python
profile = cm.get_memory_profile()
print(profile['summary'])
# → "AI 记住了关于你的 12 件事：5 个偏好、3 个纠正、2 个决策"
```

### 5. 导出与导入（可携带性）

```python
# 导出记忆 — 数据属于你
cm.export_memories(output_path="my_memories.json")

# 在新设备上导入
with CarryMem() as cm2:
    cm2.import_memories(input_path="my_memories.json")
    # 所有记忆恢复！
```

---

## 🎨 实际使用场景

### 场景 1：代码助手记住你的风格

```python
with CarryMem() as cm:
    cm.classify_and_remember("I prefer using type hints in Python")
    cm.classify_and_remember("I like to use dataclasses instead of dicts")

    # 下次对话，AI 自动知道你的偏好
    memories = cm.recall_memories(query="Python coding style")
```

### 场景 2：跨工具使用

```python
# 在 Cursor 中
with CarryMem(namespace="cursor") as cm_cursor:
    cm_cursor.classify_and_remember("I prefer dark mode")

# 在 Windsurf 中，使用相同的记忆
with CarryMem(namespace="cursor") as cm_windsurf:
    memories = cm_windsurf.recall_memories(query="theme")  # 找到了！
```

### 场景 3：项目隔离

```python
# 项目 A
with CarryMem(namespace="project-a") as cm_a:
    cm_a.classify_and_remember("Use React for frontend")

# 项目 B — 互不干扰
with CarryMem(namespace="project-b") as cm_b:
    cm_b.classify_and_remember("Use Vue for frontend")
```

---

## 🔥 为什么 CarryMem 更好

|  | CarryMem | Mem0 | LangMem | Zep |
|--|----------|------|---------|-----|
| **自动分类** | ✅ 7 种类型 | ❌ 全部存储 | ⚠️ 需要 LLM | ⚠️ 事后摘要 |
| **可携带性** | ✅ 你的文件 | ❌ 云端锁定 | ❌ 工具锁定 | ❌ 服务锁定 |
| **成本** | ✅ 60%+ 零成本 | ❌ 每次调用 | ❌ 每次调用 | ❌ 每次调用 |
| **项目隔离** | ✅ 命名空间 | ❌ 无 | ❌ 无 | ❌ 无 |
| **知识库** | ✅ Obsidian | ❌ 无 | ❌ 无 | ❌ 无 |
| **开源** | ✅ 完全开源 | ⚠️ 部分 | ✅ 完全开源 | ⚠️ 部分 |

**核心差异**：CarryMem 的记忆属于你。换模型、换工具、换设备 — 记忆跟着你走。

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 分类准确率 | **90.6%** |
| F1 分数 | **97.9%** |
| 零成本分类 | **60%+** |
| 召回延迟 (P50) | **~45ms** |
| 测试通过 | **308/308** |

---

## 🏗️ 工作原理

### 三层分类策略

```
用户输入 → 规则引擎 (60%+) → 模式分析 (30%) → 语义推断 (10%)
              ↓                     ↓                    ↓
          零成本               近零成本             Token 成本
          高速度               中等速度              低速度
```

**60%+ 的分类不需要 LLM 调用！**

### 数据流

```
1. 用户输入
   ↓
2. 自动分类（7 种类型）
   ↓
3. 智能存储（去重 + TTL）
   ↓
4. 语义召回（FTS5 + 同义词）
   ↓
5. 返回相关记忆
```

---

## 🌟 高级功能

### Obsidian 知识库集成

```python
from memory_classification_engine import CarryMem, ObsidianAdapter

with CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault")) as cm:
    cm.index_knowledge()
    results = cm.recall_from_knowledge("Python design patterns")
```

### MCP 服务器

添加到你的 MCP 客户端配置（如 Claude Code、Cursor）：

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

**12 个工具**：核心 (3) · 存储 (3) · 知识库 (3) · 画像 (2) · 提示 (1)

---

## 📚 文档

- 📖 [快速入门指南](../QUICK_START_GUIDE.md)
- 🏗️ [架构设计](../ARCHITECTURE.md)
- 📋 [API 参考](../API_REFERENCE.md)
- 🎯 [用户故事](../USER_STORIES.md)
- 🗺️ [路线图](../guides/ROADMAP.md)
- 🤝 [贡献指南](../../CONTRIBUTING.md)

---

## 🎯 适合谁？

**开发者** — 构建需要记住用户的 AI Agent

**产品团队** — 需要持久记忆，不想从零构建分类逻辑

**高级用户** — 希望 AI 工具记住自己，而不是反过来

---

## 🚦 项目状态

**当前版本**：v0.6.0
**测试**：308/308 通过
**准确率**：90.6%

---

## 🤝 贡献

欢迎贡献！参见 [贡献指南](../../CONTRIBUTING.md)。

### 开发环境搭建

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd carrymem
pip install -e ".[dev]"
pytest
```

---

## 📄 许可证

MIT 许可证 — 详见 [LICENSE](../../LICENSE)

---

**开始使用 CarryMem，让 AI 记住你！** 🚀

```bash
pip install carrymem
```
