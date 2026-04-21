# CarryMem v0.5 用户故事 (v1.0)

**日期**: 2026-04-20
**版本**: v1.0 (对应 CarryMem v0.5~v0.6)
**参考**: MCP_POSITIONING_CONSENSUS_v3.md §9, CarryMem 产品方向讨论纪要

---

## 用户角色定义

| 角色 | 代号 | 描述 | 优先级 |
|------|------|------|--------|
| 独立开发者 | DEV | 给自己的 Agent 产品接入记忆功能 | P0 |
| Agent 产品团队 | TEAM | 在生产环境中使用 CarryMem | P1 |
| 终端用户 | USER | 和 Agent 聊天的人（间接受益） | 北极星 |

---

## P0 用户故事（v0.5~v0.6 必须完成）

### US-001: 三行代码接入

**作为** 独立开发者
**我希望** 用三行代码让我的 Agent 记住用户偏好
**以便** 不用自己写分类和存储逻辑

```python
from carrymem import CarryMem

cm = CarryMem()  # 自动使用 SQLite 默认存储
result = cm.classify_and_remember("I prefer dark mode in my editor")
# → {"type": "user_preference", "content": "prefer dark mode", "stored": True}
```

**验收标准**:
- [ ] `pip install carrymem` 成功安装
- [ ] 无需任何配置即可使用（SQLite 默认存储）
- [ ] 三行代码完成分类+存储
- [ ] 无外部服务依赖（纯本地运行）

### US-002: 分类后自动存储

**作为** 独立开发者
**我希望** 调用 classify_and_remember 后，记忆自动存入本地数据库
**以便** 下次对话时 Agent 能检索到之前的记忆

**验收标准**:
- [ ] classify_and_remember 返回 stored=True
- [ ] SQLite 数据库文件自动创建（默认 ~/.carrymem/memories.db）
- [ ] 存储的内容包含分类结果（type/tier/confidence）和原始消息
- [ ] 重复调用不会产生重复记录（去重）

### US-003: 按类型检索记忆

**作为** 独立开发者
**我希望** 按类型检索记忆（如只取 user_preference）
**以便** 在 Agent 的 system prompt 中注入相关记忆

```python
prefs = cm.recall_memories(filters={"type": "user_preference"}, limit=5)
# → [{"type": "user_preference", "content": "prefer dark mode", ...}, ...]
```

**验收标准**:
- [ ] 支持 type 过滤（7 种类型）
- [ ] 支持 tier 过滤（4 个层级）
- [ ] 支持 confidence 阈值过滤
- [ ] 支持关键词全文搜索
- [ ] 返回结果按 confidence 降序排列

### US-004: 纯分类模式（无存储）

**作为** 独立开发者
**我希望** 只使用分类功能，不使用内置存储
**以便** 把分类结果接入自己的存储系统（如 Supermemory/Mem0）

```python
from carrymem import CarryMem

cm = CarryMem(storage=None)  # 纯分类模式
result = cm.classify_message("I prefer dark mode")
# → {"type": "user_preference", "content": "prefer dark mode", "stored": False}
```

**验收标准**:
- [ ] 不配置存储时，3 个核心工具正常工作
- [ ] classify_message 不依赖任何存储后端
- [ ] 存储相关工具（recall_memories/forget_memory）在无存储时返回明确错误

### US-005: 删除过期记忆

**作为** 独立开发者
**我希望** 过期或不再需要的记忆能被自动清理
**以便** 记忆库不会无限增长

**验收标准**:
- [ ] forget_memory 按 ID 删除单条记忆
- [ ] tier=1（感觉记忆）默认 24 小时过期
- [ ] tier=4（语义记忆）永不过期
- [ ] forget_expired() 自动清理所有过期记忆

---

## P1 用户故事（v0.6~v0.7）

### US-006: 用户确认 AI 建议时补全内容

**作为** 独立开发者
**我希望** 当用户说"好的/行/就这样"接受 AI 建议时，MCE 能自动引用上一条 AI 回复
**以便** decision 类型记忆的内容是完整的，而不是空的

```python
result = cm.classify_message(
    message="行，就这样搞",
    context="AI建议: 使用SQLite作为默认存储方案"
)
# → {"type": "decision", "content": "确认采用SQLite作为默认存储方案"}
```

**验收标准**:
- [ ] context 参数可选，不传时行为不变
- [ ] 传入 context 且检测到用户确认模式时，自动合并内容
- [ ] 不影响非确认场景的分类结果

### US-007: MCP Server 3+3 模式

**作为** Agent 产品团队
**我希望** 通过 MCP Server 使用 CarryMem 的全部功能
**以便** Claude Code / Cursor 等 AI 工具能直接调用

**验收标准**:
- [ ] 核心工具（classify_message/batch_classify/get_schema）永远可用
- [ ] 可选工具（classify_and_remember/recall_memories/forget_memory）需配置 adapter
- [ ] 无 adapter 时可选工具返回 "storage_not_configured" 错误
- [ ] MCP Server 启动时自动检测 adapter 配置

### US-008: Obsidian 知识库检索

**作为** 独立开发者
**我希望** CarryMem 能检索我的 Obsidian 笔记
**以便** Agent 回答时能参考我的个人知识库

**验收标准**:
- [ ] 配置 Obsidian vault 路径后自动索引
- [ ] 支持 YAML frontmatter 标签提取
- [ ] FTS5 全文搜索笔记内容
- [ ] 检索优先级：记忆库 > 知识库

---

## 北极星用户故事（v1.0+）

### US-009: "AI 记得我"

**作为** 终端用户
**我希望** 换了设备或新开会话后，AI 还记得我的偏好和决策
**以便** 不用每次都重新告诉 AI 我喜欢什么

**验收标准**:
- [ ] Agent 在新会话中能检索到之前的 user_preference
- [ ] Agent 不会推荐用户明确拒绝过的东西
- [ ] 用户体验到"这个 AI 真的了解我"的感觉

### US-010: "先本地后外部"

**作为** 终端用户
**我希望** AI 先查我的个人记忆和知识库，不够再去问大模型
**以便** 回答更个性化，隐私更受保护

**验收标准**:
- [ ] 检索优先级：记忆库 → 知识库 → 外部 LLM
- [ ] 个人记忆中的信息优先于通用知识
- [ ] 隐私敏感信息不会发送到外部

---

## 非功能性用户故事

### US-NF01: 零 LLM 成本

**作为** 独立开发者
**我希望** 60% 的消息分类不需要调用 LLM
**以便** 控制运营成本

**验收标准**:
- [ ] 规则层 + 模式层覆盖 60%+ 的分类
- [ ] 仅在语义层（可选）才需要 LLM
- [ ] 无 LLM 时系统仍可工作（降级到模式层）

### US-NF02: 多语言支持

**作为** 国际开发者
**我希望** CarryMem 支持英文、中文、日文的消息分类
**以便** 我的 Agent 能服务全球用户

**验收标准**:
- [ ] 英文分类准确率 ≥90%
- [ ] 中文分类准确率 ≥85%
- [ ] 日文分类准确率 ≥80%
- [ ] 三语言的测试用例覆盖全部 7 种类型

### US-NF03: 命名迁移兼容

**作为** 旧版 MCE 用户
**我希望** 升级到 CarryMem 后，我的代码不需要改动
**以便** 平滑迁移

**验收标准**:
- [ ] `import mce` 仍然可用（别名）
- [ ] `pip install mce` 自动安装 carrymem
- [ ] 旧版 API 调用方式完全兼容
- [ ] 6 个月过渡期后 mce 别名标记 deprecated
