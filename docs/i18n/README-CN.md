# CarryMem — AI 的身份层

**AI 记住你是谁。不只是你说了什么。**

> 你的便携式 AI 身份层 — 偏好、决策和纠正，跨模型、跨工具、跨设备随身携带。

CarryMem 是一个轻量级、零依赖的 AI 记忆系统，存储**你是谁** — 你的偏好、决策、纠正 — 并将这个身份提供给任何 AI 工具。从 Cursor 切换到 Claude Code，从 GPT 切换到 Claude，你的 AI 始终认识你。

[English](../../README.md) | **中文** | [日本語](README-JP.md)

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.2-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-447%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/accuracy-90.6%25-green" alt="Accuracy">
  <img src="https://img.shields.io/badge/zero--dependencies-core-brightgreen" alt="Zero Deps">
</p>

---

## 为什么需要 CarryMem？

### 问题：AI 总是忘记你是谁

每次新对话，AI 都从零开始：
- 你偏好深色模式？**忘了。**
- 你上次纠正过？**忘了。**
- 你决定用 React？**忘了。**

换工具（Cursor → Windsurf），换模型（Claude → GPT）— 每次都从零开始。

### 解决方案：CarryMem 身份层

CarryMem 不只是存储文本 — 它理解**你是谁**：

```bash
$ carrymem whoami

  你是谁（根据你的 AI）
  ==================================================

  你的偏好：
    ⭐ 我偏好所有编辑器都用深色模式
    ⭐ 我用 PostgreSQL 做数据库
    ⭐ 我总是用 Python 做数据分析

  你的决策：
    🎯 前端用 React

  你的纠正：
    🔧 端口号应该是 5432

  记忆画像：
    总计: 19 | 主导类型: user_preference | 平均置信度: 73%
```

---

## 快速开始

### 安装

```bash
pip install -e .
```

### 5 行代码

```python
from memory_classification_engine import CarryMem

cm = CarryMem()
cm.classify_and_remember("我偏好深色模式")              # 自动分类为偏好
cm.classify_and_remember("用 PostgreSQL 不用 MySQL")    # 自动分类为纠正
memories = cm.recall_memories("数据库")                  # 语义召回
print(cm.build_system_prompt())                          # 注入任何 AI
cm.close()
```

### 命令行（19 个命令）

```bash
carrymem init                           # 初始化
carrymem add "我偏好深色模式"            # 存储记忆
carrymem add "测试笔记" --force         # 强制存储（跳过分类）
carrymem list                           # 列出记忆
carrymem search "主题"                  # 搜索记忆
carrymem show <key>                     # 查看记忆详情
carrymem edit <key> "新内容"            # 编辑记忆
carrymem forget <key>                   # 删除记忆
carrymem whoami                         # AI 认为你是谁
carrymem profile export identity.json   # 导出 AI 身份
carrymem stats                          # 记忆统计
carrymem check                          # 质量与冲突检查
carrymem clean --expired --dry-run      # 预览清理
carrymem doctor                         # 诊断安装
carrymem setup-mcp --tool cursor        # 一行配置 MCP
carrymem tui                            # 终端界面
carrymem export backup.json             # 导出所有记忆
carrymem import backup.json             # 导入记忆
carrymem version                        # 显示版本
```

---

## 核心功能

### 1. 自动分类（7 种记忆类型）

CarryMem 自动识别你分享的信息类型：

| 类型 | 图标 | 示例 |
|------|------|------|
| `user_preference` | ⭐ | "我偏好深色模式" |
| `correction` | 🔧 | "不对，是 Python 3.11 不是 3.10" |
| `decision` | 🎯 | "前端用 React" |
| `fact_declaration` | 📌 | "我在东京的一家创业公司工作" |
| `task_pattern` | 🔄 | "我总是先写测试" |
| `contextual_observation` | 👁 | "用户似乎有些沮丧" |
| `knowledge` | 📚 | "PostgreSQL 使用 MVCC" |

### 2. 语义召回（跨语言）

```python
cm.classify_and_remember("我偏好使用PostgreSQL")

# 以下查询都能找到：
cm.recall_memories("PostgreSQL")     # 精确匹配
cm.recall_memories("数据库")          # 同义词扩展
cm.recall_memories("Postgres")       # 拼写纠正
cm.recall_memories("データベース")    # 跨语言（日语）
```

### 3. 身份层（whoami）

```python
identity = cm.whoami()
print(identity["preferences"])   # ["我偏好深色模式", ...]
print(identity["decisions"])     # ["前端用 React", ...]
print(identity["corrections"])   # ["端口号应该是 5432", ...]
```

### 4. 重要性评分与生命周期

每条记忆都有随时间演变的重要性评分：

```
importance = confidence × type_weight × recency_factor × access_factor
```

- **30 天半衰期衰减** — 旧记忆逐渐淡忘，除非被访问
- **访问强化** — 频繁召回的记忆保持新鲜
- **类型加权** — 纠正 (1.3x) > 决策 (1.2x) > 偏好 (1.1x)

### 5. 质量管理

```bash
carrymem check                    # 全面检查
carrymem check --conflicts        # 检测矛盾
carrymem check --quality          # 发现低质量记忆
carrymem check --expired          # 发现过期记忆
carrymem clean --expired --dry-run # 预览清理
```

### 6. 安全与可靠性

| 功能 | 说明 |
|------|------|
| **加密** | AES-128 (Fernet) 或 HMAC-CTR 回退，零依赖 |
| **备份** | 零停机 SQLite VACUUM INTO |
| **审计日志** | 只追加的操作历史 |
| **版本历史** | 每次编辑追踪，支持回滚 |
| **输入验证** | SQL 注入、XSS、路径遍历防护 |

### 7. MCP 集成（一行配置）

```bash
# 配置 Cursor
carrymem setup-mcp --tool cursor

# 配置 Claude Code
carrymem setup-mcp --tool claude-code

# 配置所有
carrymem setup-mcp --tool all
```

12 个 MCP 工具：核心 (3) · 存储 (3) · 知识库 (3) · 画像 (2) · 提示 (1)

### 8. 终端界面

```bash
pip install textual
carrymem tui
```

交互式终端界面，侧边栏过滤、搜索、添加模式。

---

## 竞品对比

|  | CarryMem | Mem0 | OpenChronicle | ima |
|--|----------|------|---------------|-----|
| **零依赖** | ✅ 仅 SQLite | ❌ 需要 Milvus | ✅ | ❌ 云端 |
| **自动分类** | ✅ 7 种类型 | ❌ | ❌ 手动 | ❌ |
| **身份画像** | ✅ whoami | ❌ | ❌ | ❌ |
| **命令行** | ✅ 19 个命令 | ❌ | ❌ | ❌ |
| **终端界面** | ✅ textual | ❌ | ❌ | ✅ App |
| **加密** | ✅ 内置 | ❌ | ❌ | ❌ |
| **版本历史** | ✅ 回滚 | ❌ | ❌ | ❌ |
| **冲突检测** | ✅ 内置 | ❌ | ❌ | ❌ |
| **数据所有权** | ✅ 本地文件 | ⚠️ 云端 | ✅ 本地 | ❌ 云端 |
| **5 行代码接入** | ✅ | ❌ | ❌ | ❌ |
| **跨语言召回** | ✅ 中/英/日 | ❌ | ❌ | ❌ |

**核心差异**：其他产品存储你读过什么。CarryMem 存储你是谁。

---

## 性能指标

| 指标 | 数值 |
|------|------|
| 分类准确率 | **90.6%** |
| F1 分数 | **97.9%** |
| 零成本分类 | **60%+** |
| 召回延迟 (P50) | **~45ms** |
| 测试通过 | **447/447** |

---

## 架构

```
用户输入
    ↓
自动分类（7 种类型，4 个层级）
    ↓
重要性评分（confidence × type × recency × access）
    ↓
智能存储（SQLite + FTS5，去重，TTL，加密）
    ↓
语义召回（FTS5 + 同义词 + 拼写纠正 + 跨语言）
    ↓
上下文注入（token 预算，相关性排序）
    ↓
AI 工具（Cursor / Claude Code / 任何 MCP 客户端）
```

**三层分类策略**：
```
规则引擎 (60%+) → 模式分析 (30%) → 语义推断 (10%)
     ↓                  ↓                  ↓
 零成本            近零成本           Token 成本
```

---

## 高级用法

### Obsidian 知识库

```python
from memory_classification_engine import CarryMem, ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()
results = cm.recall_from_knowledge("Python 设计模式")
```

### 异步 API

```python
from memory_classification_engine import AsyncCarryMem

async with AsyncCarryMem() as cm:
    await cm.classify_and_remember("我偏好深色模式")
    memories = await cm.recall_memories("主题")
```

### JSON 适配器（无需 SQLite）

```python
from memory_classification_engine import CarryMem, JSONAdapter

cm = CarryMem(adapter=JSONAdapter("/path/to/memories.json"))
```

### 加密

```python
cm = CarryMem(encryption_key="my-secret-key")
# 所有内容静态加密，读取时解密
```

### 记忆版本化

```python
cm.update_memory(key, "更新后的内容")     # 创建版本 2
history = cm.get_memory_history(key)      # [v1, v2]
cm.rollback_memory(key, version=1)        # 恢复到 v1
```

### 导出身份给其他 AI

```python
# 导出你的 AI 身份
cm.export_profile(output_path="my_identity.json")

# 在另一台设备或 AI 工具上
cm.import_memories(input_path="backup.json")
```

---

## 文档

- [快速入门指南](../QUICK_START_GUIDE.md)
- [架构设计](../ARCHITECTURE.md)
- [API 参考](../API_REFERENCE.md)
- [用户故事](../USER_STORIES.md)
- [路线图](../guides/ROADMAP.md)
- [贡献指南](../../CONTRIBUTING.md)

---

## 适合谁？

**开发者** — 构建需要跨会话记住用户的 AI Agent

**高级用户** — 希望 AI 工具（Cursor、Claude Code、Windsurf）记住自己

**团队** — 通过共享记忆命名空间分享组织知识

---

## 项目状态

**当前版本**：v0.1.2
**测试**：447/447 通过
**准确率**：90.6%

**v0.8.x 更新日志**：
- v0.1.2：身份层（whoami、profile 导出）、竞品差异化
- v0.8.1：用户视角 CLI 改进（show/edit/clean、彩色输出、--force）
- v0.8.0：增强 CLI（19 命令）、TUI、MCP 配置、doctor、质量管理
- v0.7.0：MCP HTTP/SSE、JSON 适配器、异步 API
- v0.6.0：加密、备份、审计日志
- v0.5.0：智能上下文注入、重要性评分、缓存、合并、版本化

---

## 贡献

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd carrymem
pip install -e ".[dev]"
pytest
```

详见 [贡献指南](../../CONTRIBUTING.md)。

---

## 许可证

MIT 许可证 — 详见 [LICENSE](../../LICENSE)

---

**CarryMem — AI 记住你是谁。只有你拥有数据。** 🚀
