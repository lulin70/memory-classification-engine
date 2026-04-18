# Memory Classification Engine

<p align="center">
  <strong>不是什么都记，只记值得记的。</strong><br>
  <sub>AI Agent 实时记忆分类引擎。60%+ 零 LLM 成本。</sub>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README-JP.md">日本語</a> ·
  <a href="./ROADMAP-ZH.md">路线图</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/issues">问题反馈</a>
</p>

---

## 问题：你的 Agent 要么全忘，要么全记

每个 AI Agent 都面临同一个记忆困境。

方案 A：**什么都不存。** 每次新会话从零开始。用户重复说过的话。Agent 犯已经犯过的错。

方案 B：**全都存。** 把每段对话压缩成摘要扔进向量库。刚开始没问题，50 轮之后检索返回的全是模糊噪音，因为信号被噪声淹没了。成本随消息量线性增长（每条消息 = 一次 LLM 调用）。

根本原因：**大多数系统在存储之前不做分类**。它们把用户的偏好（"用双引号"）、决策（"选了 PostgreSQL"）、闲聊（"今天天气不错"）一视同仁，当成一大团东西存起来。

## MCE 的做法不同

MCE 在存储前对**每条消息做实时分类**：

```
消息："上次那个方案太复杂了，换个简单点的"

传统系统：
  → 存为摘要片段："讨论了方案的复杂度"
  → 丢失上下文：这是对之前某个决策的**否定**
  → 检索结果：埋在 50 条其他摘要里，相关度低

MCE：
  → [correction] "否决了之前的复杂方案，倾向简化"
  → 自动关联到 decision_001（原来的复杂方案）
  → 置信度: 0.89 | 来源: 模式分析 | 层级: 情节记忆
  → LLM 成本: $0（在 Layer 2 命中）
```

同一条消息。传统系统存的是噪声。MCE 存的是一条**可执行的、带类型的、自动关联的记忆，且零 LLM 成本**。

**每千条消息的成本对比：**

| 方案 | LLM 调用次数 | 成本 |
|------|-------------|------|
| 全量摘要 | 1,000 | $0.50 - $2.00 |
| **MCE** | **<100** | **$0.05 - $0.20** |

---

## 三层管道：先便宜的，后贵的

```
用户消息
       │
       ▼
┌─────────────────────┐   60%+ 的消息        │  零成本
│ Layer 1: 规则匹配    │   在这里处理完        │  正则 + 关键词
│   "记住", "以后都..." │                     │  确定性判断
└──────────┬──────────┘
           │ 未匹配
           ▼
┌─────────────────────┐   30%+ 的消息        │  仍然不需要 LLM
│ Layer 2: 结构分析    │   在这里处理完        │  对话模式识别
│                     │   "连续3次纠正=偏好"   │
└──────────┬──────────┘
           │ 未匹配
           ▼
┌─────────────────────┐   <10% 的消息         │  LLM 兜底
│ Layer 3: 语义推断   │   才会走到这里        │  处理模糊边缘情况
└─────────────────────┘
```

大多数方案从 Layer 3 开始。MCE 从 Layer 1 开始，只在必要时升级。这就是为什么 60%+ 的分类是零成本的。

---

## 快速开始

```bash
pip install memory-classification-engine
```

不需要数据库、不需要 API Key、不需要配置。开箱即用。

### 30 秒上手

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# 场景 1：用户否定了之前的方案（隐含纠正信号）
engine.process_message(
    "上次那个方案太复杂了，我们换个简单点的"
)
# → [correction] 否决了之前的复杂方案，倾向简化
#   置信度: 0.89, 来源: pattern, 层级: episodic
#   自动关联: decision_001

# 场景 2：抱怨背后隐藏着反复出现的痛点
engine.process_message(
    "每次部署前都要跑测试，这个流程太繁琐了"
)
# → [sentiment_marker] 对部署流程的不满
#   隐含模式: 部署前跑测试（自动提取）

# 场景 3：一句话里的团队分工
engine.process_message(
    "张三负责后端，李四做前端，我统筹整体架构"
)
# → [relationship] 张三→后端, 李四→前端, 用户→架构
#   置信度: 0.95, 层级: semantic
```

### 自适应检索模式 (v2.0)

MCE v2.0 引入三种检索模式以适配不同场景：

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# 紧凑模式：仅关键词匹配，延迟 <10ms，零 LLM 成本
memories = engine.retrieve_memories("部署检查清单", limit=5,
                                     retrieval_mode='compact')

# 均衡模式：默认 — 语义排序 + 优化流水线（推荐）
memories = engine.retrieve_memories("部署检查清单", limit=5,
                                     retrieval_mode='balanced')

# 全面模式：深度分析 + 关联查询 + 复合评分
memories = engine.retrieve_memories("部署检查清单", limit=5,
                                     retrieval_mode='comprehensive',
                                     include_associations=True)
```

| 模式 | 延迟 | 适用场景 |
|------|------|---------|
| `compact` | <10ms | 高频查询、关键词为主的场景 |
| `balanced` | ~15-50ms | 通用场景（默认） |
| `comprehensive` | 50-200ms | 深度研究、决策回顾 |

### 跨会话记忆回放

用户真正感知到的价值：新开一个对话，Agent **记得**之前重要的事。

```python
from memory_classification_engine import MemoryOrchestrator

memory = MemoryOrchestrator()

# ... 使用一周之后 ...

# 新会话开始，加载相关记忆
memories = memory.recall(context="coding", limit=5)
for m in memories:
    print(f"[{m['type']}] {m['content']} (置信度: {m['confidence']}, 来源: {m['source']})")
# 输出:
# [user_preference] 使用双引号不用单引号 (置信度: 0.95, 来源: rule)
# [decision] 项目用 Python 不用 Go (置信度: 0.91, 来源: rule)
# [relationship] 张三负责后端 API (置信度: 0.88, 来源: semantic)
# [correction] 不要过度设计，保持简单 (置信度: 0.89, 来源: pattern)
# [fact_declaration] 生产环境跑 Ubuntu 22.04 (置信度: 0.92, 来源: rule)
#
# 统计: 加载 5 条 | 过滤 12 条噪声 | 0 次 LLM 调用
```

---

## MCP Server：2 分钟接入 Claude Code

MCE 内置 MCP Server（**生产版 v1.0.0**）。这是在 Claude Code / Cursor 等 MCP 兼容工具中使用 MCE 最快的方式。

```bash
cd mce-mcp
python3 server.py
# MCP Server 启动于 http://localhost:9001
```

添加到 Claude Code 配置 (`~/.claude/settings.json`)：

```json
{
  "mcpServers": {
    "mce": {
      "command": "python3",
      "args": ["/path/to/mce-mcp/server.py"]
    }
  }
}
```

可用工具：`classify_message`、`retrieve_memories`、`store_memory`、`search_memories`、`get_memory_stats`、`delete_memory`、`update_memory`、`export_memories`、`import_memories`。

你在 Claude Code 里发送的每条消息都可以被自动分类和存储。每次新会话都会加载结构化的记忆摘要。

完整文档见 [API Reference](./docs/api/API_REFERENCE_V1.md)。

---

## 分类什么：7 种记忆类型

| 类型 | 示例 | 存储位置 |
|------|------|---------|
| **user_preference** | "我喜欢空格不用 tab" | Tier 2: 程序性记忆 |
| **correction** | "不对，应该这样做" | Tier 3: 情节记忆 |
| **fact_declaration** | "公司有 100 人" | Tier 3: 情节记忆 |
| **decision** | "缓存用 Redis 吧" | Tier 3: 情节记忆 |
| **relationship** | "张三负责后端" | Tier 4: 语义记忆 |
| **task_pattern** | "部署前要跑测试" | Tier 2: 程序性记忆 |
| **sentiment_marker** | "这个流程太烦了" | Tier 3: 情节记忆 |

不是每条消息都会产生记忆。寒暄、确认词（"好的"、"谢谢"）、低信号内容会在存储前被过滤掉。

---

## 自我进化：模式自动晋升为规则

引擎使用时间越长，成本越低，准确率越高。

| 时间 | Layer 1 规则 | Layer 2 模式 | Layer 3 LLM | 成本/千条 |
|------|-------------|-------------|-------------|----------|
| 第 1 周 | 30% 命中率 | 40% | 30% | $0.15 |
| 第 4 周 | 50%（+20 条自动规则） | 35% | 15% | $0.08（-47%） |
| 第 3 月 | 65%（+50 条自动规则） | 25% | 10% | $0.05（-67%） |

自动规则示例：

```yaml
# 系统初始规则（第一天就有）：
- pattern: "记住.*喜欢"
  type: user_preference

# 使用 1 个月后自动学习到的：
- pattern: "太复杂.*简单"
  type: correction
  source: learned_from_user_behavior

- pattern: "每次.*都要.*烦"
  type: sentiment_marker
  source: learned_from_user_behavior
```

你的使用模式会自动变成免费的分类规则。无需手动调优。

### 反馈循环自动化 (v2.0)

MCE v2.0 内置自动化反馈循环，持续提升分类准确率：

- **FeedbackAnalyzer**：检测用户纠正中的模式（最少出现 3 次）
- **RuleTuner**：根据检测到的模式生成规则建议
- **Auto-apply**：置信度超过阈值的规则自动生效

```python
result = engine.process_feedback(memory_id="mem_001",
                                  correction_type="wrong_type",
                                  suggested_type="decision")
# → 模式检测到：第 3 次用户将 episodic 纠正为 decision
# → 规则建议已生成，等待自动应用（置信度: 0.85）
```

### 模型蒸馏接口 (v2.0)

面向需要成本优化的生产环境部署：

```python
from memory_classification_engine.layers.distillation import DistillationRouter

router = DistillationRouter()
request = ClassificationRequest(message="关于代码风格的用户偏好")

# 根据预估置信度路由：
# >0.85 → 仅 embedding（零 LLM）
# 0.5-0.85 → 弱模型（低成本）
# <0.5 → 强模型（高精度）
result = router.classify(request)
```

---

## 与其他方案对比

| 功能 | Mem0 | MemGPT | LangChain Memory | **MCE** |
|------|------|--------|------------------|---------|
| 写入时机 | 对话后批量提取 | 上下文窗口管理 | 手动/Hooks | **实时逐条分类** |
| 记忆分类 | 基础标签 | 无 | 无 | **7 种类型 + 三层管道** |
| 记忆层级 | 单层（向量库） | 两层（内存+磁盘） | 单层（会话） | **四层（工作/程序性/情节/语义）** |
| 遗忘机制 | 无 | 被动溢出 | 无 | **主动衰减 + Nudge 审查** |
| 学习能力 | 静态 | 无 | 无 | **模式自动晋升 + 反馈循环** |
| LLM 成本 | 每条消息 | 中等 | 低 | **60%+ 零成本分类** |
| 跨会话 | 仅导出 | 无 | 无 | **结构化迁移标准** |
| MCP 支持 | 无 | 无 | 无 | **内置 MCP Server (v1.0.0 生产版)** |
| 高级 API | 无 | 无 | 基础 | **MemoryOrchestrator（学习/回放/导入/导出）** |
| 检索模式 | 全量内容 | 全量内容 | 全量内容 | **3 种自适应模式 + 类型化记忆** |
| 反馈循环 | 无 | 无 | 无 | **自动化模式检测与规则调优** |

---

## 四层记忆存储

| 层级 | 名称 | 存储方式 | 生命周期 |
|------|------|---------|---------|
| T1 | 工作记忆 | 上下文窗口（LLM 原生管理） | 仅当前会话 |
| T2 | 程序性记忆 | 配置文件 / 系统提示词 | 长期，始终加载 |
| T3 | 情节记忆 | 向量数据库（ChromaDB / SQLite） | 加权衰减 |
| T4 | 语义记忆 | 知识图谱（Neo4j / 内存图） | 长期，交叉关联 |

核心依赖：**仅 PyYAML**。向量库、图数据库、LLM 都是可选扩展，按需安装。

---

## 性能表现

基准测试数据来自 `benchmarks/baseline_benchmark.py`（Phase 1 优化后）：

| 指标 | 优化前 | 优化后 | 提升幅度 |
|------|--------|--------|---------|
| `process_message` P99 延迟 | 5,669 ms | 1,452 ms | **-74%** |
| `retrieve_memories` 长句 P99 | 85 ms | 50 ms | **-41%** |
| 缓存命中率（预热后） | 0% | 97.83% | **+97.83pp** |
| 测试套件 | 661 个测试 | 696 个测试 | **+35 个测试** |
| 单条消息处理（Layer 1/2） | ~10ms | ~10ms | 基线 |
| 检索延迟（均衡模式） | ~15ms | ~15ms | 基线 |
| 并发吞吐 | 626 msg/s | 626 msg/s | 基线 |
| 内存占用 | <100MB | <100MB | 基线 |
| LLM 调用比例 | <10% | <10% | 基线 |
| 记忆压缩率 | 87-90% 噪声消除 | 87-90% | 基线 |

**关键优化项：**
- FAISS 维度不匹配修复（消除每次调用时的 AssertionError）
- SmartCache 重写：基于 OrderedDict 的 O(1) LRU 淘汰 + 启动预热
- 并行查询：ThreadPoolExecutor 跨存储层并发获取
- 哈希索引：O(1) 复杂度的 `get_memory` 查找
- 批量向量编码 + 预计算排序键用于语义排名

---

## 技术选型

| 组件 | 默认方案 | 备选 |
|------|---------|------|
| 规则引擎 | YAML + 正则 | JSON Schema |
| 向量存储（T3） | ChromaDB | Qdrant, Milvus |
| 知识图谱（T4） | 内存图 | Neo4j |
| 语义分类器（L3） | 小模型 API | Ollama 本地模型 |
| Agent 适配 | 独立 SDK | 插件扩展 |
| 缓存 | OrderedDict SmartCache（LRU + 预热） | Redis（外部） |

---

## 项目结构

```
memory-classification-engine/
├── mce-mcp/                         # MCP Server（Claude Code / Cursor 集成）
│   ├── server.py                    #   服务入口（v1.0.0 生产版）
│   ├── tools/                       #   MCP 工具实现
│   └── config.yaml                  #   服务配置
│
├── src/memory_classification_engine/
│   ├── engine.py                    # 核心协调器（自适应检索模式）
│   ├── layers/
│   │   ├── rule_matcher.py          #   Layer 1: 规则匹配
│   │   ├── pattern_analyzer.py      #   Layer 2: 结构分析
│   │   ├── semantic_classifier.py   #   Layer 3: LLM 兜底
│   │   ├── feedback_loop.py         #   v2.0: 自动反馈与规则调优
│   │   └── distillation.py          #   v2.0: 模型蒸馏路由
│   ├── storage/
│   │   └── tier3.py                 #   FAISS 向量索引（维度安全）
│   ├── coordinators/
│   │   └── storage_coordinator.py   #   并行查询 + 哈希索引
│   ├── utils/
│   │   └── memory_manager.py        #   SmartCache（OrderedDict + 预热）
│   ├── orchestrator.py              # MemoryOrchestrator 高级 API
│   └── privacy/
│
├── benchmarks/
│   ├── baseline_benchmark.py        # 性能测量工具
│   └── final_results.json           # 优化后的基准数据
│
├── examples/                        # 可运行示例
├── tests/                           # 测试套件（696 测试全部通过）
├── config/rules.yaml                # 分类规则配置
├── setup.py                         # PyPI 包配置
└── README.md
```

---

## 安装方式

```bash
# 核心（仅需分类引擎）
pip install memory-classification-engine

# 带 RESTful API 服务器
pip install -e ".[api]"

# 带 LLM 语义分类（Layer 3）
pip install -e ".[llm]"
export MCE_LLM_API_KEY="your-key"
export MCE_LLM_ENABLED=true

# 安装 scikit-learn（用于向量编码优化）
pip install scikit-learn

# 运行测试
pip install -e ".[testing]"
pytest
```

---

## 许可证

MIT

---

## 链接

- 项目主页：[github.com/lulin70/memory-classification-engine](https://github.com/lulin70/memory-classification-engine)
- 路线图：[ROADMAP-ZH.md](./ROADMAP-ZH.md)
- API 文档：[docs/api/API_REFERENCE_V1.md](./docs/api/API_REFERENCE_V1.md)
- 优化路线图：[docs/OPTIMIZATION_ROADMAP_V1.md](./docs/OPTIMIZATION_ROADMAP_V1.md)
- Claude Code MCP 配置：[docs/claude_code_mcp_config.md](./docs/claude_code_mcp_config.md)
- 问题反馈 / 讨论
