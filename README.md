# Memory Classification Engine

<p align="center">
  <strong>轻量级 Agent 侧记忆分类引擎</strong><br>
  实时判断对话中哪些内容值得记忆，以什么形式存储，存入哪个记忆层级
</p>

<p align="center">
  <a href="./README-EN.md">English</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/issues">报告问题</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/discussions">讨论</a>
</p>

---

## 为什么需要这个？

大多数 AI Agent 的记忆方案采用"全量摘要"策略：对话结束后对整段对话做一次摘要存档。这导致记忆库充满噪音，检索信噪比极低。

Memory Classification Engine 的做法不同：

- **实时分类**，不是事后摘要。对话过程中逐条判断是否值得记忆
- **7 种记忆类型**区分存储：偏好、纠正、事实、决策、关系、任务模式、情感标记
- **三层判断管道**：规则匹配（零成本）→ 结构分析（轻量级）→ 语义推断（LLM，尽量少触发）
- **四层记忆存储**：工作记忆 → 程序性记忆 → 情节记忆 → 语义记忆
- **主动遗忘机制**：基于时间、频率和重要性的加权衰减，不是被动地存满再淘汰

一句话：**告诉 Agent 什么值得记，而不是把所有东西都存下来。**

## 与其他方案的区别

| | Mem0 | MemGPT | LangChain Memory | 本项目 |
|---|---|---|---|---|
| **写入时机** | 对话后全量提取 | 上下文窗口管理 | 手动/Hooks | **实时分类** |
| **记忆分类** | 基础 | 无 | 无 | **7 种类型 + 3 层管道** |
| **记忆层级** | 单层（向量库） | 两层（内存+硬盘） | 单层（会话） | **四层** |
| **遗忘机制** | 无 | 被动淘汰 | 无 | **主动加权衰减** |
| **学习能力** | 基础 | 无 | 无 | **模式自动晋升为规则** |
| **Agent 无关** | 是 | 否 | 是 | **是（独立模块 + SDK）** |

## 快速开始

```bash
# 克隆项目
git clone https://github.com/lulin70/memory-classification-engine.git
cd memory-classification-engine

# 安装（核心依赖只有 PyYAML，开箱即用）
pip install -e .
```

不需要数据库，不需要 API Key，装完就能跑：

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# 处理用户消息，引擎自动判断是否值得记忆
result = engine.process_message("记住，我不喜欢在代码中使用破折号")
print(result)
# {"matched": true, "memory_type": "user_preference", "tier": 2,
#  "content": "不喜欢在代码中使用破折号", "confidence": 1.0, "source": "rule:0"}

# 检索记忆
memories = engine.retrieve_memories("代码风格")
print(memories)
```

### 按需扩展

```bash
# 如需 RESTful API
pip install -e ".[api]"

# 如需 LLM 语义分类（Layer 3）
pip install -e ".[llm]"
export MCE_LLM_API_KEY="your_api_key"
export MCE_LLM_ENABLED=true

# 如需运行测试
pip install -e ".[testing]"
pytest
```

## 记忆分类类型

引擎会将对话内容实时分类为以下 7 种类型：

| 类型 | 标识 | 示例 |
|------|------|------|
| 用户偏好 | `user_preference` | "我喜欢用空格缩进" |
| 纠正信号 | `correction` | "不对，应该用 4 个空格" |
| 事实声明 | `fact_declaration` | "我们团队有 5 个人" |
| 决策记录 | `decision` | "那就用 Python 写吧" |
| 关系信息 | `relationship` | "张三负责后端开发" |
| 任务模式 | `task_pattern` | "每次部署前都要跑测试" |
| 情感标记 | `sentiment_marker` | "我很讨厌过度设计的架构" |

## 三层判断管道

这是引擎的核心设计思想：**尽量用便宜的方式判断，LLM 是最后的兜底。**

```
用户消息
  │
  ▼
┌──────────────────────┐
│ Layer 1: 规则匹配     │  正则 + 关键词，零成本，处理 60%+ 的常见场景
└────────┬─────────────┘
         │ 未匹配
         ▼
┌──────────────────────┐
│ Layer 2: 结构分析     │  对话交互模式识别，不依赖 LLM
└────────┬─────────────┘
         │ 未匹配
         ▼
┌──────────────────────┐
│ Layer 3: 语义推断     │  调用 LLM 做语义分析，高覆盖率
└────────┬─────────────┘
         │
         ▼
  去重 → 冲突检测 → 写入对应层级
```

## 四层记忆存储

| 层级 | 类型 | 存储方式 | 生命周期 |
|------|------|---------|---------|
| Tier 1 | 工作记忆 | 上下文窗口（LLM 原生管理） | 当前会话 |
| Tier 2 | 程序性记忆 | 配置文件 / 系统提示词 | 长期，主动加载 |
| Tier 3 | 情节记忆 | 向量数据库（ChromaDB / SQLite） | 加权衰减 |
| Tier 4 | 语义记忆 | 知识图谱（Neo4j / 内存图） | 长期，语义关联 |

## 技术选型

| 组件 | 默认方案 | 备选 |
|------|---------|------|
| 规则引擎 | YAML + 正则 | JSON Schema |
| 向量存储（Tier 3） | ChromaDB | Qdrant, Milvus |
| 知识图谱（Tier 4） | 内存图 | Neo4j |
| 语义分类（Layer 3） | 小模型 API | Ollama 本地模型 |
| Agent 适配 | 独立模块 + SDK | 插件扩展 |

核心依赖只有 `PyYAML`。向量数据库、知识图谱、LLM 都是可选的扩展，按需安装。

## Agent 框架集成

支持作为独立模块接入任何 Agent 框架：

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# 注册 Agent（支持 claude_code, work_buddy, trae, openclaw 等适配器）
engine.register_agent('my_agent', {
    'adapter': 'claude_code',
})

# 通过 Agent 处理消息
result = engine.process_message_with_agent('my_agent', "Hello, world!")
```

同时提供 RESTful API 和 Python SDK，方便外部系统集成。详见 [API 文档](docs/api/api.md) 和 [用户指南](docs/user_guides/user_guide.md)。

## 性能表现

| 指标 | 数据 |
|------|------|
| 单条消息处理 | ~10ms（Layer 1/2），< 500ms（Layer 3） |
| 检索延迟 | ~15ms |
| 并发吞吐 | 626 messages/s |
| 记忆压缩率 | 87-90% |
| 内存占用 | < 100MB（基础模式） |

## 项目结构

```
memory-classification-engine/
├── src/memory_classification_engine/
│   ├── engine.py              # 核心引擎（coordinator 架构）
│   ├── layers/                # 三层分类管道
│   │   ├── rule_matcher.py        # Layer 1: 规则匹配
│   │   ├── pattern_analyzer.py    # Layer 2: 结构分析
│   │   └── semantic_classifier.py # Layer 3: 语义推断
│   ├── storage/               # 分层存储
│   │   ├── tier2.py               # 程序性记忆
│   │   ├── tier3.py               # 情节记忆（向量）
│   │   ├── tier4.py               # 语义记忆（图谱）
│   │   └── neo4j_knowledge_graph.py
│   ├── privacy/               # 隐私与安全
│   ├── plugins/               # 插件系统
│   ├── agents/                # Agent 框架适配器
│   ├── sdk/                   # Python SDK
│   ├── api/                   # RESTful API
│   └── utils/                 # 工具集
├── config/rules.yaml          # 规则配置
├── examples/                  # 使用示例
├── tests/                     # 测试
└── setup.py
```

## 贡献

欢迎各种形式的贡献：提交代码、报告问题、完善文档、参与讨论。

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细流程。

## 许可证

[MIT License](LICENSE)

## 链接

- 项目主页：[github.com/lulin70/memory-classification-engine](https://github.com/lulin70/memory-classification-engine)
- 问题反馈：[Issues](https://github.com/lulin70/memory-classification-engine/issues)
- 讨论社区：[Discussions](https://github.com/lulin70/memory-classification-engine/discussions)
- 推进计划：[ROADMAP.md](ROADMAP.md)
