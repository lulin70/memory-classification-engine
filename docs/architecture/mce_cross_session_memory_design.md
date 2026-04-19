# MCE 跨会话记忆回放：体验设计方案
> 核心目标：让用户在新开会话时**立刻感知到"AI 记住了我之前说过的话"**，而且比竞品记得更准、更细、更智能。

> 参考反馈："Hermes 短期记忆比 OpenClaw 好，不会新开会话就忘记之前的对话"

> 设计日期：2026-04-12 | 状态：草案

---

## 一、问题定义

### 1.1 用户真正感知到的"记忆好"是什么

不是三层管道、60%+ 零 LLM 成本、7 种记忆类型。用户能感知到的只有三个具体体验：

| # | 用户体验 | 正面例子 | 负面例子（没有记忆） |
|---|---------|---------|-------------------|
| E1 | 偏好一次说，永久生效 | "用空格不用 tab"说过后永远遵守 | 每次都要重新提醒 |
| E2 | 决策有上下文 | 选 Python 后新对话继续基于此 | 新对话重新问"用什么语言" |
| E3 | 纠正不重犯 | 单引号被纠正过后自动用双引号 | 同样的错误反复出现 |

### 1.2 竞品现状

| 方案 | 实现方式 | 用户感知到的效果 |
|------|---------|---------------|
| OpenClaw | 基本无跨会话记忆 | "新开会话就忘了" |
| Hermes Agent | SQLite 摘要 + MEMORY.md 加载 | "比 OpenClaw 好，但记的是模糊摘要" |
| Mem0 | 对话后全量提取 + 向量检索 | "能搜到一些东西，但噪音多" |
| **MCE（目标）** | **实时分类 + 结构化存储 + 主动回放** | **精准记住每类信息，带置信度和来源** |

### 1.3 MCE 要赢的关键差异

不只是"记住了"，而是：
- **记得更准**（结构化 vs 模糊摘要）
- **记得更细**（7 种类型区分 vs 一段混合文本）
- **更聪明**（主动遗忘低价值信息 vs 全量堆积）
- **成本更低**（回放时零 LLM 调用）

---

## 二、核心设计：主动式记忆回放

### 2.1 设计原则

**原则一：不要静默加载，要主动展示**

大多数方案的记忆是静默的。AI 在后台加载了记忆，用户不知道。MCE 的做法是：新开会话时，**主动向用户展示当前加载了哪些记忆**。这个展示本身就是最好的"我在乎你说过的话"的信号。

**原则二：展示的是洞察，不是数据 dump**

不要把所有记忆都列出来。按相关性排序，只展示 top N 条最相关的，并且每条都附带可操作的信息（类型、置信度、来源）。

**原则三：顺便告诉用户成本**

在回放展示的末尾附上一行统计："本次回忆过滤噪音 X 条，LLM 调用 0 次"。这既是差异化卖点，也是让开发者觉得专业的细节。

### 2.2 回放界面规范

#### 文本格式（适用于 Claude Code / 终端场景）

```
📝 MCE Memory Recall

## 已加载的记忆 (5/20)
- [偏好] 使用双引号而非单引号          置信度0.95 规则层   引用8次
- [偏好] 不喜欢过度设计的架构            置信度0.92 语义层   引用5次
- [决策] 项目采用Python技术栈             置信度0.89 模式层   +3关联
- [纠正] 否决复杂方案->倾向简化           置信度0.89 模式层
- [关系] 张三负责后端，李四做前端         置信度0.95 规则层

## 统计信息
- 过滤噪音: 23条
- LLM调用: 0次
- 处理消息: 342条
- 本周新增: 7条记忆

💡 这些记忆将影响我的回复，确保一致性体验
```

#### 富文本格式（适用于 WorkBuddy / IDE 场景）
- 使用卡片式布局，每条记忆一个卡片
- 颜色编码：偏好(蓝色)、决策(绿色)、纠正(黄色)、关系(紫色)、事实(灰色)
- 支持点击展开详情、标记为不重要、手动遗忘等操作

---

## 三、接口设计

### 3.1 MCP Server 接口扩展

#### mce_recall：记忆回放
- name: mce_recall
- description: Recall relevant memories for current context, sorted by relevance.
- params:
  - context (string, default="general"): 当前会话上下文 (coding / deployment / general)
  - limit (int, default=5, max=20): 返回最大记忆数量
  - types (array of enum): 按记忆类型过滤，空=全部
    - user_preference, correction, fact_declaration, decision, relationship, task_pattern, sentiment_marker
  - format (enum "text"/"json", default="text"): 输出格式
  - include_pending (bool, default=true): 是否包含低置信度待确认记忆

#### mce_process：消息分类处理（已有）
- name: mce_process
- params: message (required), context, auto_store

#### mce_status：记忆状态查看
- name: mce_status | detail_level (summary/full)

#### mce_forget：手动遗忘
- name: mce_forget | memory_id (required), reason (optional)

### 3.2 会话生命周期集成

#### 完整流程

1. **会话开始**
   - 触发 `mce_recall` 获取相关记忆
   - 以格式化方式展示记忆列表
   - 注入记忆到系统提示（可选）

2. **会话进行中**
   - 对每条用户消息调用 `mce_process`
   - 自动存储有价值的信息
   - 实时更新记忆质量指标

3. **会话结束**
   - 生成本次会话的记忆摘要
   - 清理临时记忆
   - 更新长期记忆存储

#### 集成流程图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  会话开始       │────>│  记忆回放展示   │────>│  处理用户消息   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          ^                       │                       │
          │                       │                       │
          │                       │                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  会话结束       │<────│  记忆质量评估   │<────│  记忆分类存储   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 四、平台适配方案

### 4.1 Claude Code 适配

- 接入方式: MCP 配置 + CLAUDE.md 自定义指令

MCP 配置 (~/.claude/mcp.json):
{"mcpServers": {"memory-classification-engine": {"command": "python", "args": ["-m", "memory_classification_engine.mcp_server"]}}}

CLAUDE.md 追加指令:
## Memory System
When starting a new conversation, ALWAYS call mce_recall first.
Present results in a formatted list before responding to the user.
During conversation, call mce_process on each message that may contain memorable info.

- 用户体验流程: 新开会话 -> 发首条消息 -> Claude 调用 recall -> 展示记忆列表 -> 用户感知到"AI 记得我"

### 4.2 WorkBuddy 适配

- 接入方式: 原生 MCP 支持 + Agent 配置
- 额外优势: 可将 recall 结果注入 system prompt, 实现"记忆即身份"

### 4.3 TRAE 适配

- 接入方式: MCP 插件或 SDK 直接调用
- 如果不支持 MCP, 通过 Python SDK:
from memory_classification_engine import MemoryClassificationEngine
engine = MemoryClassificationEngine()
def on_session_start(): memories = engine.recall(context="coding", limit=5); render_to_panel(memories)
def on_user_message(msg): result = engine.process_message(msg); if result["matched"]: log_to_console(f"MCE recorded")

### 4.4 各平台对比

| 平台 | 接入方式 | 回放展示位置 | 配置复杂度 |
|------|---------|------------|-----------|
| Claude Code | MCP + CLAUDE.md | 对话窗口内 | 低 (2步) |
| WorkBuddy | MCP + Agent 配置 | 对话窗口/System Prompt | 低 (2步) |
| TRAE | MCP 或 SDK | IDE侧边栏/面板 | 中(需插件) |
| Cursor | MCP | 内联展示 | 低 (2步) |
| VS Code | MCP 扩展 | 侧边栏面板 | 中(需扩展) |

---

## 五、「首次使用 vs 使用一周后」对比策略

### 5.1 第一次使用（空记忆状态）

MCE Memory Recall (0 memories loaded)
- 还没有任何记忆记录。
- 随着我们对话，我会记住你的偏好、决策和重要信息。

### 5.2 使用一周后（丰富记忆状态）

MCE Memory Recall (7 memories loaded, 23 noise filtered, 0 LLM calls)
- [偏好] 使用双引号而非单引号          置信度0.95 规则层   引用8次
- [偏好] 不喜欢过度设计的架构            置信度0.92 语义层   引用5次
- [决策] 项目采用Python技术栈             置信度0.89 模式层   +3关联
- [纠正] 否决复杂方案->倾向简化           置信度0.89 模式层
- [关系] 张三负责后端，李四做前端         置信度0.95 规则层
- [任务模式] 每次部署前跑测试套件         置信度0.91 自动晋升规则
- 本周统计: 处理消息342条 | LLM调用28次(8.2%) | 新增规则3条

### 5.3 制作建议

- 录制两个GIF(空状态vs丰富状态)，并排做对比图
- 放入README顶部、Show HN/Reddit帖子配图、公众号文章视觉素材

---

## 六、实施优先级

### P0（本周完成）
- [ ] mce_recall 接口实现
- [ ] 文本格式渲染器
- [ ] Claude Code MCP + CLAUDE.md 适配文档
- [ ] 首次使用/使用一周后的截图或 GIF

### P1（两周内）
- [ ] mce_status 和 mce_forget 接口
- [ ] WorkBuddy 适配文档和示例
- [ ] TRAE SDK 适配示例代码
- [ ] 会话结束时的新增记忆摘要功能

### P2（一个月内）
- [ ] Cursor/VS Code 侧边栏面板
- [ ] 记忆质量自评估仪表盘
- [ ] 待确认记忆的用户交互流程
- [ ] Nudge 主动复习机制

---

## 七、风险和注意事项

1. **隐私敏感度**: 回放时注意不要展示包含密码、密钥等敏感信息，需加入PII过滤规则
2. **性能要求**: recall操作必须在50ms内完成(纯存储层查询,不涉及LLM)
3. **记忆膨胀**: 必须严格限制返回数量(默认5条),提供分页或详情入口
4. **平台兼容性**: 文本格式需兼容纯终端/富文本/IDE面板三种场景

* 本文档随MCP Server开发进展持续更新 *
