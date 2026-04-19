# Memory Classification Engine (MCE)

<p align="center">
  <strong>记忆分类中间件 — AI Agent 的"记忆安检机"</strong><br>
  <sub>MCE 不存储记忆。MCE 告诉你<strong>什么值得记</strong>、<strong>记成什么类型</strong>、<strong>存在哪一层</strong>。<br>
  存储的事，交给 Supermemory / Mem0 / Obsidian / 你自己的系统。</sub>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README-JP.md">日本語</a> ·
  <a href="./ROADMAP-CN.md">路线图</a> ·
  <a href="./docs/user_guides/STORAGE_STRATEGY.md">存储策略</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/issues">问题反馈</a>
</p>

---

## 问题：没有人在存储之前做分类

每个 AI 记忆系统都有同一个盲点。

**Supermemory** 收到一条消息 → 直接存。不做分类。
**Mem0** 收到一条消息 → 直接存。不做分类。
**Claude Code CLAUDE.md** → 你手动决定写什么。没有结构。

它们都回答了 **"怎么存"**，但从不回答 **"什么值得存"**。

结果：

| 消息 | 该不该存？ | 大多数系统的做法 |
|------|-----------|-----------------|
| "我偏好用双引号" | 是 — 偏好 | 存了（正确） |
| "好的，听起来不错" | 否 — 应答 | 也存了（噪音） |
| "那个方案太复杂了" | 是 — 纠正 | 当通用摘要存了（丢失类型信息） |
| "今天天气真好" | 否 — 闲聊 | 存了（污染检索） |

**60%+ 的消息不应该被存储。** 但当前系统要么全存（噪音爆炸），要么全不存（失忆）。

**MCE 就是那个缺失的前置过滤器。**

---

## MCE 做什么

MCE 是一个**分类中间件**。它位于你的 Agent 和你的记忆系统之间：

```
你的 AI Agent / Claude Code
        │  (原始对话消息)
        ▼
┌───────────────────────────────┐
│     MCE (分类引擎)            │
│                               │
│   输入:  "我偏好 Python 用双引号"
│                               │
│   输出: {                     │
│     should_remember: true,    │
│     type: "user_preference", │
│     confidence: 0.95,         │
│     tier: 2,                  │
│     suggested_action: "store" │
│   }                          │
└──────────────┬────────────────┘
               │  结构化 MemoryEntry (JSON)
               ▼
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 [Supermemory] [Mem0] [Obsidian] [你的数据库]
    (云端)      (自托管)   (本地)      (自定义)
```

**MCE 只做好一件事**：判断消息是否包含值得记忆的信息，如果是，则分类为 7 种类型之一并给出置信度评分。

**MCE 不做**：存储、检索、搜索、删除、导出、导入或召回记忆。这些是下游系统的职责。

---

## 为什么分类比存储更重要

### 论据一：60% 过滤器

MCE 的三层管道在进入任何昂贵处理前过滤掉 60%+ 的消息：

```
进入的消息
       │
       ▼
┌─────────────────────┐   60%+ 消息在此过滤   │ 零成本
│ 第一层: 规则匹配    │                       │ 正则 + 关键词
│   "记住"、"总是"...│                       │ 确定性匹配
└──────────┬──────────┘
           │ 未命中 (~40%)
           ▼
┌─────────────────────┐   30%+ 消息在此分类   │ 仍零 LLM
│ 第二层: 模式分析    │                       │ 对话结构
│   "第三次拒绝=偏好"  │                       │
└──────────┬──────────┘
           │ 模糊 (~10%)
           ▼
┌─────────────────────┐   <10% 消息到达这里    │ LLM 兜底
│ 第三层: 语义推理    │                       │ 仅边界 case
└─────────────────────┘
```

大多数方案从第三层开始（每条消息都用 LLM）。MCE 从第一层开始。

**每 1000 条消息的成本**：

| 方案 | LLM 调用次数 | 成本 |
|------|-------------|------|
| 全部发给 LLM | 1,000 次 | $0.50 - $2.00 |
| **MCE（先 L1 + L2）** | **<100 次** | **$0.05 - $0.20** |

### 论据二：有类型的记忆比原始摘要更有用

```
消息: "上个方案太复杂了，我们简化一下吧"

没有 MCE（原始存储）:
  → 存为: "用户讨论了方案复杂度"
  → 问题: 丢失了"拒绝"的上下文。搜索"方案"会返回噪音。

有 MCE（分类后）:
  → [纠正] "拒绝了之前的复杂方案，偏好更简单的方案"
  → 置信度: 0.89 | 来源: 模式 | 层级: 情节
  → 好处: 下游可以按不同类型路由处理
```

### 论据三：7 种类型 > 1 个桶

| 类型 | 示例 | 为什么重要 |
|------|------|-----------|
| **用户偏好** | "我偏好空格而非 Tab" | 影响未来所有代码生成 |
| **纠正信号** | "不对，应该这样做" | 必须覆盖之前的事实/决策 |
| **事实声明** | "我们有 100 名员工" | 可验证的真理，很少变化 |
| **决策记录** | "我们选 Redis 做缓存" | 解释架构为什么长这样 |
| **关系映射** | "Alice 负责后端" | 支持角色感知的回复 |
| **任务模式** | "部署前必须测试" | 可自动化的工作流规则 |
| **情感标记** | "这个工作流很烦人" | 标识流程痛点 |

不是每条消息都会产生记忆。闲聊（"好的"、"谢谢"）、应答和低信号内容会被自动过滤。

---

## 快速开始

```bash
pip install memory-classification-engine
```

无需数据库。无需 API Key。无需配置。纯分类。

### 30 秒完成消息分类

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# 处理消息 — 返回包含 'matches' 列表的字典
result = engine.process_message(
    "上个方案太复杂了，我们简化一下吧"
)

# 获取分类结果：
if result.get('matches'):
    entry = result['matches'][0]
    print(f"类型: {entry.get('type')}")          # 'correction'
    print(f"置信度: {entry.get('confidence')}")  # 0.89
    print(f"层级: {entry.get('tier')}")           # 3 (情节)
    print(f"应该存储: {entry.get('confidence', 0) > 0.5}")  # True
```

### 更多示例

```python
# 场景 1: 用户偏好
engine.process_message("我偏好 Python 里用双引号")
# → [user_preference] 置信度: 0.95, 层级: 2, 来源: 规则
#   ↓ 存到 Supermemory/Mem0/Obsidian 作为 "preference"

# 场景 2: 纠正（覆盖已有知识）
engine.process_message("不对，我们在用 PostgreSQL 不是 MongoDB")
# → [correction] 置信度: 0.92, 层级: 2, 来源: 模式
#   ↓ 下游应该更新已有事实，而非重复创建

# 场景 3: 决策（解释架构选择）
engine.process_message("我们决定用 Redis 做会话缓存")
# → [decision] 置信度: 0.88, 层级: 3, 来源: 语义
#   ↓ 高价值，存到长期记忆

# 场景 4: 噪音（自动过滤）
engine.process_message("好的，我看看")
# → [] （空 matches — 不需要记忆）

# 场景 5: 关系提取
engine.process_message("Alice 负责后端，Bob 做前端")
# → [relationship] 置信度: 0.95, 层级: 4 (语义/图谱)
#   ↓ 图谱存储的好候选
```

### 批量分类

```python
messages = [
    {"message": "我偏好暗色模式"},
    {"message": "我们选了 PostgreSQL"},
    {"message": "谢谢帮忙"},  # ← 会被过滤
    {"message": "Alice 负责 API"},
]

result = engine.batch_process(messages)
# 返回结果列表，每项包含 matches/confidence/tier
```

---

## 建议存储层级

MCE 为每个分类后的记忆分配一个**建议存储层级**。这是给下游系统的建议——不是强制要求。

| 层级 | 名称 | 生命周期 | 使用场景 |
|------|------|----------|---------|
| T1 | 感觉记忆 | < 1 秒 | 永不存储（已被 MCE 过滤） |
| T2 | 程序性记忆 | 小时–天 | 活跃偏好、模式、纠正 |
| T3 | 情节记忆 | 天–月 | 决策、事实、事件 |
| T4 | 语义记忆 | 月–年 | 关系、领域知识 |

你的下游系统可以遵循这些建议，也可以实现自己的保留策略。参见[存储策略指南](./docs/user_guides/STORAGE_STRATEGY.md)了解与 Supermemory、Mem0 和 Obsidian 的集成示例。

---

## 自进化：模式随时间变为规则

引擎运行时间越长，成本越低、准确率越高。

| 时间 | 第一层（规则） | 第二层（模式） | 第三层（LLM） | 成本/千条 |
|------|--------------|---------------|-------------|----------|
| 第 1 周 | 30% 命中率 | 40% | 30% | $0.15 |
| 第 4 周 | 50%（+20 自动规则） | 35% | 15% | $0.08 (-47%) |
| 第 3 月 | 65%（+50 自动规则） | 25% | 10% | $0.05 (-67%) |

自动生成的规则示例如下：

```yaml
# 系统种子（第一天）:
- pattern: "记住.*偏好"
  type: user_preference

# 使用 1 个月后学习到的:
- pattern: "太复杂.*简单点"
  type: correction
  source: learned_from_user_behavior

- pattern: "总是得.*很繁琐"
  type: sentiment_marker
  source: learned_from_user_behavior
```

你的使用模式会变成免费的分类规则。无需手动调优。

### 反馈循环 (v2.0)

```python
result = engine.process_feedback(memory_id="mem_001",
                                feedback={"type": "wrong_type",
                                           "correct_type": "decision"})
# → 模式检测到: 用户第 3 次将 episodic 纠正为 decision
# → 规则建议已生成，等待自动应用（置信度: 0.85）
```

> **API 注意**: `process_feedback(memory_id, feedback)` 接受 2 个参数 — `feedback` 是包含纠正详情的字典。参见 [API 参考](./docs/api/API_REFERENCE_V1.md) 了解完整签名。

---

## MCP Server：2 分钟集成 Claude Code

MCE 内置 MCP Server（**v0.2.0, 生产就绪**）。MCE 完全在本地运行 —— **你的数据不会离开本机**。

> **定位**: MCE 是**分类中间件**，不是完整记忆系统。MCP Server 只暴露分类工具；存储委托给下游系统（Supermemory、Mem0、Obsidian 或你自己的）。

### 配置

```bash
python3 -m memory_classification_engine.integration.layer2_mcp
```

添加到 Claude Code 配置 (`~/.claude/settings.json`)：

```json
{
  "mcpServers": {
    "mce": {
      "command": "python3",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
      "env": {}
    }
  }
}
```

### 可用工具 (v0.2.0)

| 工具 | 状态 | 说明 |
|------|------|------|
| `classify_memory` | 核心 | 分类消息 → 结构化 MemoryEntry（类型、层级、置信度） |
| `batch_classify` | 核心 | 批量分类多条消息 |
| `mce_status` | 核心 | 引擎状态（版本、能力、运行时间） |
| `store_memory` | ⚠️ v0.3 废弃 | 存储移至下游适配器 |
| `retrieve_memories` | ⚠️ v0.3 废弃 | 检索移至下游系统 |
| `get_memory_stats` | ⚠️ v0.3 废弃 | 统计从下游获取 |
| `find_similar` | ⚠️ v0.3 废弃 | 向量搜索从下游获取 |
| `export_memories` | ⚠️ v0.3 废弃 | 导出由下游完成 |
| `import_memories` | ⚠️ v0.3 废弃 | 导入到下游 |
| `mce_recall` | ⚠️ v0.3 废弃 | 召回由下游完成（如 Supermemory `recall()`） |
| `mce_forget` | ⚠️ v0.3 废弃 | 删除通过下游 |

> **迁移说明**: v0.3.0 将移除废弃工具。MCP Server 将只暴露 4 个工具：`classify_message`、`get_classification_schema`、`batch_classify`、`mce_status`。参见[存储策略指南](./docs/user_guides/STORAGE_STRATEGY.md)了解下游集成选项。

### 实际使用流程

```
你（在 Claude Code 中）:  "我偏好 Python 用双引号"
         │
         ▼
   MCE MCP Server:  classify_memory("我偏好 Python 用双引号...")
         │
         ▼
   输出 (MemoryEntry JSON):
   {
     "should_remember": true,
     "entries": [{
       "type": "user_preference",
       "confidence": 0.95,
       "tier": 2,
       "suggested_action": "store",
       "content": "用户偏好双引号而非单引号"
     }]
   }
         │
         ▼
   你的选择: 存到 Supermemory / Obsidian / Mem0 / 自定义
```

参见 [API 参考](./docs/api/API_REFERENCE_V1.md) 和[存储策略](./docs/user_guides/STORAGE_STRATEGY.md)了解完整文档。

---

## 性能

来自 `benchmarks/baseline_benchmark.py` 的基准测试结果：

### 分类性能（核心指标）

| 指标 | 数值 | 条件 |
|------|------|------|
| `process_message` P50 延迟 | ~45 ms | 热缓存，规则命中 |
| `process_message` P99 延迟 | **1,452 ms** | 最坏情况（LLM 兜底） |
| 第一层命中率 | 60%+ | 使用 1 周后 |
| 缓存命中率（热启动） | **97.83%** | 初始预热后 |
| LLM 调用比例 | **<10%** | 大部分消息由 L1/L2 处理 |

### 测试质量

| 指标 | 数值 |
|------|------|
| 总测试数 | **874 通过, 0 失败** |
| Demo 场景 | **26/30 通过 (87%)** |

### 成本效率

| 场景 | 消息量 | 估算 LLM 调用 | 估算成本 |
|------|--------|-------------|---------|
| 轻度使用（10 条/天） | 300/月 | ~30 | **<$0.01** |
| 重度使用（100 条/天） | 3,000/月 | ~300 | **~$0.10** |
| 极客使用（500 条/天） | 15,000/月 | ~1,500 | **~$0.50** |

---

## FAQ

### MCE 会替代 Supermemory / Mem0 吗？

**不会。MCE 与它们互补。**

可以这样理解：
- **Supermemory / Mem0** = 仓库（存储和检索记忆）
- **MCE** = 仓库入口的安检机（决定什么可以进去）

你可以同时使用两者：MCE 分类 → Supermemory 存储 → Supermemory 召回。或者 MCE 分类 → Obsidian 存为 markdown。MCE 不关心数据去哪里。

### 为什么不在 MCE 里也做存储？

三个原因：

1. **Supermemory 有 YC 投资、Cloudflare 基础设施、Benchmark 排名第一。** 一个开发者无法在存储质量上竞争。
2. **Mem0 有 18k GitHub Stars、向量+图混合存储、完整的工程师团队。** 它们的存储久经考验。
3. **但它们都没有在存储前做分类。** 这就是 MCE 填补的空白。而且一旦 MCE 完成分类，任何下游系统都会受益于更干净的输入数据。

MCE 致力于成为**世界上最好的记忆分类器**，而不是一个平庸的记忆系统。

### 我的数据安全吗？

**安全。** MCE 完全在你的机器上本地运行。分类过程中数据不会发送到任何外部服务器。分类后的数据去向取决于你选择的下游系统 —— 这完全在**你的控制之下**。

### 如果我不想搭建下游系统怎么办？

没问题！把 MCE 当纯分类服务使用：

```python
result = engine.process_message("我偏好暗色模式")
if result.get('matches'):
    entry = result['matches'][0]
    print(f"[{entry['type']}] {entry['content']} (置信度: {entry['confidence']})")
    # 日志输出、打印、复制粘贴到任何地方
```

MCE 的价值在于**分类决策**，而不在于持久化。

### Roadmap 怎么规划的？

参见 [ROADMAP-CN.md](./ROADMAP-CN.md)。关键里程碑：
- **v0.2.0**（当前）：分类引擎 + MCP Server（11 工具，8 个废弃）
- **v0.3.0**（下一版）：纯上游迁移 — MCP 缩减为 4 工具，StorageAdapter 抽象基类，MemoryEntry Schema v1.0
- **v0.4.0**: Supermemory、Mem0、Obsidian 官方适配器
- **v1.0.0**: 行业标准分类基准（MCE-Bench）

### MCE 和其他方案的对比？

| 问题 | 回答 |
|------|------|
| **vs Supermemory？** | 互补关系。MCE 分类，Supermemory 存储。两者配合使用。 |
| **vs Mem0？** | 互补关系。MCE 在 Mem0 存储之前增加有类型分类。 |
| **vs Claude Code CLAUDE.md？** | MCE 自动化你在 CLAUDE.md 中手动编写的内容。结构化、有类型、带置信度评分。 |
| **vs 自己写 if/else？** | MCE 有 7 种类型、三层管道、自动学习规则、60%+ 零成本过滤。自己写很快就会变得昂贵且难以维护。 |

---

## 安装

```bash
# 核心（仅分类引擎 — 纯 Python，无重量依赖）
pip install memory-classification-engine

# 带 RESTful API 服务端
pip install -e ".[api]"

# 带 LLM 语义分类（第三层，可选）
pip install -e ".[llm]"
export MCE_LLM_API_KEY="your-key"
export MCE_LLM_ENABLED=true

# 运行测试
pip install -e ".[testing]"
pytest  # 874 个测试，约 10 分钟
```

**最低依赖**: 仅 PyYAML。其余所有依赖（向量库、图库、LLM）均为可选。

---

## 项目结构

```
memory-classification-engine/
├── src/memory_classification_engine/
│   ├── engine.py                    # 核心协调器
│   ├── layers/
│   │   ├── rule_matcher.py          # 第一层: 规则匹配 (60%+ 覆盖)
│   │   ├── pattern_analyzer.py      # 第二层: 结构分析 (30%+)
│   │   ├── semantic_classifier.py   # 第三层: LLM 兜底 (<10%)
│   │   ├── feedback_loop.py         # 从纠正中自动学习
│   │   └── distillation.py          # 成本优化路由
│   ├── adapters/                    # v0.3.0: StorageAdapter ABC（规划中）
│   ├── storage/                     # 内置存储（v0.3 中废弃）
│   ├── coordinators/
│   └── utils/
│
├── src/memory_classification_engine/integration/layer2_mcp/
│   ├── server.py                    # MCP stdio 服务端（生产版 v0.2.0）
│   ├── tools.py                     # 11 个工具定义（→ v0.3.0 缩减为 4 个）
│   └── handlers.py                  # 工具处理器
│
├── mce-mcp/mce_mcp_server/server.py # HTTP 服务端（已废弃，请用 stdio）
├── benchmarks/                      # 性能测量
├── tests/                           # 874 个测试全部通过
├── config/rules.yaml                # 可编辑的分类规则
├── docs/
│   ├── consensus/                   # 战略决策与分析
│   └── user_guides/                 # 安装指南、存储策略
├── setup.py                         # PyPI 包配置
└── README.md
```

---

## 许可证

MIT

---

## 相关链接

- **代码仓库**: [github.com/lulin70/memory-classification-engine](https://github.com/lulin70/memory-classification-engine)
- **路线图**: [ROADMAP-CN.md](./ROADMAP-CN.md)
- **存储策略**: [STORAGE_STRATEGY.md](./docs/user_guides/STORAGE_STRATEGY.md) — 如何对接下游系统
- **API 参考**: [docs/api/API_REFERENCE_V1.md](./docs/api/API_REFERENCE_V1.md)
- **战略共识**: [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md) — 为什么选择纯上游路径
