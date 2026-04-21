# CarryMem v0.9 用户故事 (v2.0)

**日期**: 2026-04-21
**版本**: v2.0 (对应 CarryMem v0.7~v0.9)
**参考**: MCP_POSITIONING_CONSENSUS_v3.md §11, NotebookLM 启发分析

---

## 用户角色定义

| 角色 | 代号 | 描述 | 优先级 |
|------|------|------|--------|
| 独立开发者 | DEV | 给自己的 Agent 产品接入记忆功能 | P0 |
| Agent 产品团队 | TEAM | 在生产环境中使用 CarryMem | P1 |
| 终端用户 | USER | 和 Agent 聊天的人（间接受益） | 北极星 |

---

## P0 用户故事（v0.5~v0.6）

### US-001: 三行代码接入 ✅

**作为** 独立开发者
**我希望** 用三行代码让我的 Agent 记住用户偏好
**以便** 不用自己写分类和存储逻辑

```python
from carrymem import CarryMem
cm = CarryMem()
result = cm.classify_and_remember("I prefer dark mode in my editor")
```

**验收标准**:
- [x] 无需任何配置即可使用（SQLite 默认存储）
- [x] 三行代码完成分类+存储
- [x] 无外部服务依赖（纯本地运行）

### US-002: 分类后自动存储 ✅

**验收标准**:
- [x] classify_and_remember 返回 stored=True
- [x] SQLite 数据库文件自动创建
- [x] 重复调用不会产生重复记录（去重）

### US-003: 按类型检索记忆 ✅

**验收标准**:
- [x] 支持 type/tier/confidence 过滤
- [x] 支持关键词全文搜索
- [x] 返回结果按 confidence 降序排列

### US-004: 纯分类模式（无存储） ✅

**验收标准**:
- [x] 不配置存储时，3 个核心工具正常工作
- [x] 存储相关工具在无存储时返回明确错误

### US-005: 删除过期记忆 ✅

**验收标准**:
- [x] forget_memory 按 ID 删除单条记忆
- [x] tier 过期机制自动清理

---

## P1 用户故事（v0.6~v0.7）

### US-006: 用户确认 AI 建议时补全内容 ✅

**作为** 独立开发者
**我希望** 当用户说"好的/行"接受 AI 建议时，MCE 能自动引用上一条 AI 回复
**以便** decision 类型记忆的内容是完整的

**验收标准**:
- [x] context 参数可选，不传时行为不变
- [x] 传入 context 且检测到确认模式时，自动合并内容

### US-007: MCP Server 3+3 模式 ✅

**作为** Agent 产品团队
**我希望** 通过 MCP Server 使用 CarryMem 的全部功能

**验收标准**:
- [x] 核心工具（3个）永远可用
- [x] 可选工具（3个）需配置 adapter
- [x] 无 adapter 时返回 "storage_not_configured" 错误

### US-008: Obsidian 知识库检索 ✅ (v0.7)

**作为** 独立开发者
**我希望** CarryMem 能检索我的 Obsidian 笔记
**以便** Agent 回答时能参考我的个人知识库

```python
from carrymem import CarryMem
from carrymem.adapters import ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()
results = cm.recall_from_knowledge("Python design patterns")
```

**验收标准**:
- [x] 配置 Obsidian vault 路径后自动索引
- [x] 支持 YAML frontmatter 标签提取
- [x] FTS5 全文搜索笔记内容
- [x] 支持 wiki-link 关系提取
- [x] 增量索引（只索引变更文件）
- [x] 只读设计（remember/forget 抛出 NotImplementedError）

### US-009: 统一检索（记忆 + 知识库） ✅ (v0.7)

**作为** 独立开发者
**我希望** 一次查询同时检索记忆库和知识库
**以便** Agent 能综合参考两类信息

```python
result = cm.recall_all("Python design patterns")
# → {
#     "memories": [...],      # SQLite 中的记忆
#     "knowledge": [...],     # Obsidian 中的笔记
#     "memory_count": 3,
#     "knowledge_count": 5,
#     "priority": "memory_first"
#   }
```

**验收标准**:
- [x] recall_all() 同时查询记忆库和知识库
- [x] 检索优先级：记忆 > 知识库
- [x] 任一数据源不可用时不影响另一个

---

## P1+ 用户故事（v0.8~v0.9 — NotebookLM 启发）

### US-010: 主动声明偏好 ✅ (v0.8)

**作为** 独立开发者
**我希望** 让用户主动告诉 AI 关于自己的事，而不是等 AI 从对话中被动提取
**以便** 记忆覆盖率更高，用户更有掌控感

```python
result = cm.declare("I prefer dark mode in my editor")
# → confidence=1.0, source_layer="declaration", suggested_action="store"
```

**验收标准**:
- [x] declare() 经过分类引擎但 confidence=1.0
- [x] source_layer 标记为 "declaration"
- [x] 主动声明的内容一定存储（suggested_action="store"）
- [x] 噪音内容仍然存储（用户主动说的不是噪音）
- [x] MCP 工具 declare_preference 可用

### US-011: 记忆画像 ✅ (v0.8)

**作为** 独立开发者
**我希望** 看到结构化的"AI 记住了关于用户的什么"
**以便** 在 Agent UI 中展示，让用户审计和掌控自己的记忆

```python
profile = cm.get_memory_profile()
# → {
#     "summary": "AI 记住了关于你的 42 条信息：12个偏好、3个纠正、5个决策",
#     "total_memories": 42,
#     "highlights": {
#         "user_preference": ["dark mode", "PostgreSQL", "camelCase"],
#         "correction": ["not MongoDB but PostgreSQL"],
#         "decision": ["use SQLite as default", "REST not GraphQL"]
#     },
#     "stats": {"by_type": {...}, "by_tier": {...}, "confidence_avg": 0.87},
#     "namespace": "default",
#     "last_updated": "2026-04-21T10:30:00Z"
#   }
```

**验收标准**:
- [x] get_memory_profile() 返回结构化聚合数据
- [x] highlights 包含各类型的代表性内容（top 5）
- [x] stats 包含 by_type/by_tier/confidence_avg
- [x] summary 包含人类可读的中文摘要
- [x] 空记忆库返回 "No memories yet"
- [x] MCP 工具 get_memory_profile 可用
- [x] 不做 UI，做数据 API（Agent UI 层消费）

### US-012: 项目级记忆空间 ✅ (v0.9)

**作为** 独立开发者
**我希望** 不同项目的记忆互相隔离
**以便** 项目 A 的偏好不会污染项目 B 的检索结果

```python
cm_alpha = CarryMem(db_path="memories.db", namespace="project-alpha")
cm_beta = CarryMem(db_path="memories.db", namespace="project-beta")

cm_alpha.declare("I prefer dark mode")   # → namespace="project-alpha"
cm_beta.declare("I prefer light mode")    # → namespace="project-beta"

# 各自只能看到自己的记忆
alpha_memories = cm_alpha.recall_memories()  # 只有 dark mode
beta_memories = cm_beta.recall_memories()    # 只有 light mode

# 跨项目检索
result = cm_alpha.recall_all("PostgreSQL", namespaces=["project-alpha", "global"])
```

**验收标准**:
- [x] CarryMem(namespace="project-alpha") 构造参数
- [x] 不同 namespace 的记忆互相隔离
- [x] forget 只删除当前 namespace 的记忆
- [x] get_profile 只统计当前 namespace 的记忆
- [x] recall_all(namespaces=[...]) 支持跨 namespace 查询
- [x] 不传 namespace 时默认 "default"，向后兼容
- [x] Schema 自动迁移（旧数据库自动加 namespace 列）

---

## 北极星用户故事（v1.0+）

### US-013: "AI 记得我"

**作为** 终端用户
**我希望** 换了设备或新开会话后，AI 还记得我的偏好和决策
**以便** 不用每次都重新告诉 AI 我喜欢什么

**验收标准**:
- [ ] Agent 在新会话中能检索到之前的 user_preference
- [ ] Agent 不会推荐用户明确拒绝过的东西
- [ ] 用户体验到"这个 AI 真的了解我"的感觉

### US-014: "先本地后外部"

**作为** 终端用户
**我希望** AI 先查我的个人记忆和知识库，不够再去问大模型
**以便** 回答更个性化，隐私更受保护

**验收标准**:
- [ ] 检索优先级：同namespace记忆 → 全局记忆 → 知识库 → 外部 LLM
- [ ] 个人记忆中的信息优先于通用知识
- [ ] 隐私敏感信息不会发送到外部

---

## 非功能性用户故事

### US-NF01: 零 LLM 成本 ✅

**验收标准**:
- [x] 规则层 + 模式层覆盖 60%+ 的分类
- [x] 仅在语义层（可选）才需要 LLM
- [x] 无 LLM 时系统仍可工作

### US-NF02: 多语言支持 ✅

**验收标准**:
- [x] 英文分类准确率 ≥90%
- [x] 中文分类准确率 ≥85%
- [x] 日文分类准确率 ≥80%

### US-NF03: 命名迁移兼容 ✅

**验收标准**:
- [x] 目录名从 memory-classification-engine → carrymem
- [x] 包名 carrymem，版本 0.9.0
- [x] 旧版 API 调用方式完全兼容

---

## 版本与用户故事映射

| 用户故事 | 版本 | 状态 |
|---------|------|------|
| US-001~005 | v0.5~v0.6 | ✅ 完成 |
| US-006~007 | v0.6 | ✅ 完成 |
| US-008~009 | v0.7 | ✅ 完成 |
| US-010~011 | v0.8 | ✅ 完成 |
| US-012 | v0.9 | ✅ 完成 |
| US-013~014 | v1.0+ | 📋 计划中 |
