# Memory Classification Engine

> 一个轻量级的Agent侧记忆分类引擎，实时判断对话中哪些内容值得记忆，以什么形式存储，存入哪个记忆层级。

## 英文版文档

请查看 [README-EN.md](README-EN.md) 文件获取英文版文档。

## 项目背景

当前AI Agent的记忆管理存在一个核心问题：**什么内容值得被记住？**

大多数现有方案采用"全量摘要"策略，在对话结束后对整段对话做摘要存档。这导致：
- 记忆库中充满低价值噪音，检索时信噪比极低
- 无法区分不同类型的信息（偏好、事实、决策、关系）
- 遗忘和更新机制无法建立在无分类的记忆之上

本项目要解决的问题是：**在Agent侧实现一个轻量级的记忆分类引擎，实时判断对话中哪些内容值得记忆，以什么形式存储，存入哪个记忆层级。**

## 核心功能

### 1. 记忆分类
- **用户偏好** (`user_preference`)：用户明确表达的喜好、习惯、风格要求
- **纠正信号** (`correction`)：用户纠正AI的判断或输出
- **事实声明** (`fact_declaration`)：用户陈述的关于自身或业务的事实
- **决策记录** (`decision`)：对话中达成的明确结论或选择
- **关系信息** (`relationship`)：涉及人物、团队、组织之间的关系
- **任务模式** (`task_pattern`)：反复出现的任务类型及其处理方式
- **情感标记** (`sentiment_marker`)：用户对某话题的明确情感倾向

### 2. 记忆层级
- **Tier 1 - 工作记忆**：当前会话的上下文窗口，由LLM原生管理
- **Tier 2 - 程序性记忆**：用户偏好、行为规则、工作习惯，以系统提示词或配置文件形式加载
- **Tier 3 - 情节记忆**：决策记录、任务模式、重要对话摘要，存入向量数据库
- **Tier 4 - 语义记忆**：事实声明、关系信息、领域知识，存入知识图谱或关系型数据库

### 3. 三层判断管道
- **Layer 1: 规则匹配层**：基于正则表达式和关键词匹配，零成本，高准确率
- **Layer 2: 结构分析层**：分析对话的交互模式，轻量级，不依赖语义理解
- **Layer 3: 语义推断层**：调用LLM做语义分析，高成本，高覆盖率

### 4. 记忆管理
- **写入流程**：去重检查 → 冲突处理 → 写入对应层级存储
- **智能冲突处理**：自动检测记忆冲突，基于时间戳、置信度和来源优先级解决冲突，支持用户干预
- **记忆权重计算**：基于多维度因素（置信度、时效性、来源可靠性）计算记忆权重
- **遗忘机制**：基于时间、频率和重要性的加权衰减
- **检索策略**：根据对话内容从不同层级检索相关记忆
- **注入格式**：结构化记忆注入到系统提示词
- **职责边界**：分类引擎既可以作为独立的分类组件使用，也可以提供完整的记忆读写链路，接入方可以根据需要选择使用方式

### 5. 隐私保护
- **敏感度分析**：自动分析记忆内容的敏感度，分为high、medium和low三个级别
- **可见性管理**：支持private、team、org三个级别的可见性标签，确保记忆只对有权限的用户可见
- **场景校验**：根据使用场景过滤记忆，确保在不同场景下只使用适合的记忆
- **数据加密**：对敏感记忆进行加密存储
- **访问控制**：基于角色的访问权限管理
- **合规性**：支持GDPR和CCPA等隐私法规要求
- **审计日志**：记录所有记忆访问和修改操作

### 6. 语义理解与智能分析
- **语义推断层**：基于LLM的语义分析，提高分类准确率
- **语义相似度计算**：计算记忆之间的语义相似度，建立语义关联
- **关键词提取**：从记忆中提取关键词，提高检索效率
- **语言检测**：自动检测记忆内容的语言，支持多语言处理
- **智能记忆管理**：基于语义的记忆关联、权重调整和压缩优化

### 7. 遗忘机制与系统进化
- **基于衰减的遗忘机制**：基于时间、频率和重要性的加权衰减算法，支持记忆的自动遗忘和归档
- **系统的进化能力**：基于用户反馈的分类模型优化，支持记忆分类规则的自动调整
- **智能记忆管理增强**：记忆的自动压缩和合并，支持记忆的分层存储和检索
- **性能优化**：系统性能的自动调优，确保高性能和轻量级

### 8. 生态扩展与集成
- **多种Agent框架支持**：支持ClaudeCode、WorkBuddy、TRAE、openclaw等Agent框架，提供统一的API接口
- **知识库集成**：与Obsidian集成，实现记忆写回知识库的机制和从知识库获取上下文增强的功能
- **Agent框架的自动发现和注册**：实现Agent框架的自动发现和注册机制，支持动态加载和卸载
- **知识库的自动同步和更新**：支持知识库的自动同步和更新，确保数据的一致性

## 技术架构

```
对话内容
  │
  ▼
┌─────────────────────┐
│ Layer 1: 规则匹配层  │  ← 确定性规则，零成本，高准确率
└─────────┬───────────┘
          │ 未匹配的内容
          ▼
┌─────────────────────┐
│ Layer 2: 结构分析层  │  ← 对话结构模式识别，轻量级
└─────────┬───────────┘
          │ 未匹配的内容
          ▼
┌─────────────────────┐
│ Layer 3: 语义推断层  │  ← LLM判断，高成本，高覆盖率
└─────────┬───────────┘
          │
          ▼
   记忆写入决策
          │
          ▼
┌─────────────────────┐
│  去重与冲突检测    │
└─────────┬───────────┘
          │
          ├── 重复 → 更新已有记忆
          │
          ├── 冲突 → 智能冲突处理
          │       ├── 检测冲突类型
          │       ├── 计算记忆权重
          │       ├── 标记冲突状态
          │       └── 支持用户干预
          │
          └── 新记忆 → 写入对应Tier
                          │
                          ├── Tier 2 → 配置文件/系统提示词
                          ├── Tier 3 → 向量数据库
                          └── Tier 4 → 知识图谱
```

## 技术选型

| 组件 | 建议方案 | 备选方案 |
|------|---------|---------|
| 规则引擎 | YAML配置 + 正则表达式 | JSON Schema |
| 对话状态跟踪 | 内存状态机 | Redis |
| 向量数据库（Tier 3） | ChromaDB（轻量本地） | Qdrant, Milvus |
| 知识图谱（Tier 4） | Neo4j | 内存存储（轻量级，适合起步） |
| 配置存储（Tier 2） | YAML/JSON文件 | SQLite |
| 语义分类（Layer 3） | 小模型API调用 | 本地小模型（Ollama） |
| Agent框架适配 | 设计为独立模块，提供SDK | 可扩展接口 |

## 项目里程碑

### Phase 1: 最小可用版本（MVP）
- 实现Layer 1规则匹配层
- 实现Tier 2程序性记忆的读写
- 以ClaudeCode的CLAUDE.md格式作为初始存储格式
- 提供3-5条默认规则

### Phase 2: 结构分析与隐私保护
- 实现Layer 2结构分析层
- 实现重复检测和模式识别
- 实现Tier 3向量数据库存储和检索
- 实现去重和冲突检测
- 实现敏感度分析模块
- 实现可见性管理模块
- 实现场景校验模块
- 实现数据加密和访问控制

### Phase 3: 语义理解与智能分析
- 实现Layer 3语义推断层
- 基于LLM的语义分析
- 设计并调优分类Prompt
- 实现语义相似度计算
- 实现关键词提取
- 实现语言检测
- 实现智能记忆管理

### Phase 4: 遗忘机制与系统进化
- 实现基于衰减的遗忘机制
- 实现系统的进化能力
- 实现智能记忆管理增强
- 实现性能优化
- 实现成本控制机制

### Phase 5: 生态扩展与集成
- 实现多种Agent框架支持（ClaudeCode、WorkBuddy、TRAE、openclaw）
- 实现知识库集成（与Obsidian集成）
- 实现Agent框架的自动发现和注册机制
- 实现知识库的自动同步和更新
- 实现企业级的多用户记忆共享和权限管理
- 开放记忆导入/导出格式标准

## 与主流AI记忆系统的对比

| 维度 | Mem0 | MemGPT | LangChain Memory | ClaudeCode | 本项目（Memory Classification Engine） |
|------|------|--------|------------------|-----------|--------------------------------------|
| 记忆分类 | 有（基础） | 无 | 无（隐式） | 无（按文件层级） | 有（7种类型，3层判断管道） |
| 写入判断 | 每次对话后全量提取 | 基于上下文窗口管理 | 手动/Hooks | 手动/Hooks | 事件驱动，实时分类 |
| 记忆层级 | 单层（向量库） | 两层（内存+硬盘） | 单层（会话） | 单层（文件） | 四层（工作/程序性/情节/语义） |
| 遗忘机制 | 无 | 有（上下文淘汰）<br><small>备注：被动淘汰，上下文满了才触发</small> | 无 | 无 | 有（加权衰减+语义压缩）<br><small>备注：主动遗忘，基于时间、频率和重要性</small> |
| 存储方式 | 向量数据库 | 虚拟内存抽象 | 内存/文件 | 文件系统 | 多存储后端（文件+向量+图谱） |
| Agent无关性 | 是（SDK） | 否（自有Agent） | 是（框架组件） | 否（自有Agent） | 是（独立模块+SDK） |
| LLM集成 | 支持 | 自有模型 | 框架集成 | 自有模型 | 灵活适配多种LLM |
| 企业级特性 | 基础 | 无 | 基础 | 无 | 计划支持多用户共享和权限管理 |
| 轻量级设计 | 中 | 重 | 轻 | 轻 | 轻（优先使用本地存储） |
| 学习能力 | 基础 | 无 | 无 | 无 | 支持从情节记忆提炼程序性记忆<br><small>备注：反复出现的模式自动晋升为规则，实现记忆进化</small> |

## 快速开始

### 安装

详细的安装指南请参考 [安装指南](docs/user_guides/installation_guide.md)。

快速安装步骤：

```bash
# 克隆项目
git clone https://github.com/lulin70/memory-classification-engine.git
cd memory-classification-engine

# 安装依赖
pip install -r requirements.txt
```

### Neo4j 配置（可选）

如果你想使用Neo4j作为知识图谱存储后端，需要：

1. **安装Neo4j**：
   - 从 [Neo4j官网](https://neo4j.com/download/) 下载并安装Neo4j Desktop或Neo4j Community Server
   - 或者使用Docker运行Neo4j：
     ```bash
     docker run --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
     ```

2. **启动Neo4j**：
   - 启动Neo4j服务
   - 在浏览器中访问 `http://localhost:7474`，使用默认用户名 `neo4j` 和密码 `password` 登录
   - 首次登录时需要修改密码，确保与 `config/config.yaml` 中的配置一致

3. **验证连接**：
   - 确保Neo4j服务正在运行
   - 确保 `config/config.yaml` 中的Neo4j配置正确

4. **故障转移**：
   - 如果Neo4j不可用，系统会自动回退到内存存储，确保系统正常运行

### 配置

#### 环境变量配置

为了安全管理API Key，建议使用环境变量来配置：

```bash
# 设置GLM API Key
export MCE_LLM_API_KEY="your_glm_api_key"

# 启用LLM功能
export MCE_LLM_ENABLED=true

# 可选：设置配置文件路径
export MCE_CONFIG_PATH="./config/config.yaml"
```

#### 配置文件

编辑 `config/config.yaml` 文件：

```yaml
# LLM settings (optional)
llm:
  enabled: false  # 默认为false，设置为true启用
  api_key: ""  # 建议通过环境变量设置，不要直接在此文件中填写
  model: "glm-4-plus"
  temperature: 0.3
  max_tokens: 500
  timeout: 30  # In seconds

# Neo4j settings (optional)
neo4j:
  enabled: true
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "password"
  database: "neo4j"
  connection_pool_size: 10
  max_transaction_retry_time: 30
```

### 基本使用

```python
from memory_classification_engine import MemoryClassificationEngine

# 初始化引擎
engine = MemoryClassificationEngine()

# 处理用户消息
user_message = "记住，我不喜欢在代码中使用破折号"
result = engine.process_message(user_message)
print(result)
# 输出: {"matched": true, "memory_type": "user_preference", "tier": 2, "content": "不喜欢在代码中使用破折号", "confidence": 1.0, "source": "rule:0"}

# 检索记忆
memories = engine.retrieve_memories("代码风格")
print(memories)
```

### Agent框架使用

```python
from memory_classification_engine import MemoryClassificationEngine

# 初始化引擎
engine = MemoryClassificationEngine()

# 注册Agent
agent_config = {
    'adapter': 'claude_code',  # 支持的适配器：claude_code, work_buddy, trae, openclaw
    'api_key': 'your_api_key'  # 如果需要API密钥
}
engine.register_agent('my_agent', agent_config)

# 列出所有注册的Agent
agents = engine.list_agents()
print("注册的Agent:", agents)

# 使用Agent处理消息
result = engine.process_message_with_agent('my_agent', "Hello, world!")
print("Agent处理结果:", result)

# 注销Agent
engine.unregister_agent('my_agent')
```

### 知识库集成使用

```python
from memory_classification_engine import MemoryClassificationEngine

# 初始化引擎（需要在配置文件中设置Obsidian vault路径）
engine = MemoryClassificationEngine()

# 处理消息并创建记忆
user_message = "我喜欢阅读科幻小说"
result = engine.process_message(user_message)
memory_id = result['matches'][0]['id']

# 将记忆写回知识库
write_result = engine.write_memory_to_knowledge(memory_id)
print("写回知识库结果:", write_result)

# 从知识库获取相关知识
knowledge = engine.get_knowledge("科幻小说")
print("知识库检索结果:", knowledge)

# 同步知识库
engine.sync_knowledge_base()
print("知识库同步完成")

# 获取知识库统计信息
stats = engine.get_knowledge_statistics()
print("知识库统计信息:", stats)
```

## 项目结构

```
memory-classification-engine/
├── src/
│   ├── memory_classification_engine/
│   │   ├── __init__.py
│   │   ├── engine.py          # 核心引擎
│   │   ├── layers/
│   │   │   ├── rule_matcher.py    # 规则匹配层
│   │   │   ├── pattern_analyzer.py # 结构分析层
│   │   │   └── semantic_classifier.py # 语义推断层
│   │   ├── storage/
│   │   │   ├── tier2.py              # 程序性记忆存储
│   │   │   ├── tier3.py              # 情节记忆存储
│   │   │   ├── tier4.py              # 语义记忆存储
│   │   │   └── neo4j_knowledge_graph.py  # Neo4j知识图谱存储适配器
│   │   ├── privacy/
│   │   │   ├── encryption.py          # 数据加密模块
│   │   │   ├── access_control.py      # 访问控制模块
│   │   │   ├── privacy_settings.py    # 隐私设置模块
│   │   │   ├── compliance.py          # 合规性模块
│   │   │   ├── audit.py               # 审计日志模块
│   │   │   ├── sensitivity_analyzer.py # 敏感度分析模块
│   │   │   ├── visibility_manager.py   # 可见性管理模块
│   │   │   └── scenario_validator.py  # 场景校验模块
│   │   └── utils/
│   │       ├── config.py       # 配置管理
│   │       └── helpers.py      # 辅助函数
├── config/
│   └── rules.yaml              # 规则配置文件
├── tests/
│   ├── test_engine.py
│   ├── test_layers.py
│   └── test_storage.py
├── examples/
│   ├── basic_usage.py
│   └── agent_integration.py
├── requirements.txt
└── README.md
```

## 贡献指南

我们欢迎各种形式的贡献，包括但不限于：

- 报告bug和提出功能请求
- 提交代码改进和修复
- 完善文档
- 参与讨论和提供建议

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 文件了解详细的贡献流程。

## 许可证

本项目采用 [MIT License](LICENSE)。

## 开放问题

1. **记忆冲突的解决策略**：当新记忆与旧记忆矛盾时，是覆盖还是并存？是否需要用户确认？
   - **解决方案**：实现基于时间戳和置信度的冲突解决机制。当新记忆与旧记忆冲突时，系统会：1) 标记冲突记忆；2) 比较时间戳，默认采用较新的记忆；3) 提供用户干预机制，允许用户选择保留哪个记忆；4) 记录冲突历史，便于后续分析。

2. **跨语言记忆一致性**：同一偏好用中文和英文分别表达时，如何识别为同一条记忆？
   - **解决方案**：采用基于语义的记忆表示，将不同语言的相同概念映射到同一语义表示。初期实现可以：1) 优先支持英文和中文两种主要语言；2) 使用翻译API进行跨语言映射；3) 建立语言无关的记忆标识符，确保同一概念在不同语言下被识别为相同记忆。

3. **记忆隐私边界**：在多Agent协作场景下，哪些记忆可以共享，哪些必须隔离？
   - **解决方案**：实施多层次隐私保护措施，包括：1) 数据加密：对敏感记忆信息进行加密存储；2) 访问控制：基于角色的访问权限管理；3) 数据最小化：只存储必要的记忆信息；4) 遗忘机制：支持用户主动删除记忆；5) 审计日志：记录所有记忆访问和修改操作。

4. **记忆质量的评估指标**：如何衡量一个记忆系统"记对了多少、记错了多少"？
   - **解决方案**：建立多维度评估指标，包括：1) 记忆分类准确率：通过人工标注样本测试分类准确性；2) 检索相关性：评估检索结果与当前任务的相关性；3) 系统性能：监控响应时间和资源占用；4) 用户满意度：通过用户反馈评估系统效果。

5. **LLM侧记忆的可能性**：KV Cache持久化在工程上何时可行？Fine-tune个人记忆模型的成本何时降到可接受范围？
   - **解决方案**：采用分层存储策略，将不同重要性的记忆存储到不同层级。程序性记忆和语义记忆优先保证完整性，情节记忆则根据访问频率和时间进行衰减。同时实现记忆压缩机制，将高频访问的记忆模式化，减少存储占用。

## 性能优化

### 优化成果

通过全面的性能优化，记忆分类引擎的性能得到了显著提升：

1. **处理性能**：平均处理时间从0.0245秒减少到0.0104秒，性能提升约58%
2. **检索性能**：平均检索时间为0.0146秒，远低于50ms目标
3. **并发性能**：消息处理吞吐量达到626.33 messages/second
4. **存储优化**：记忆压缩率达到87-90%，大大减少了存储开销
5. **系统稳定性**：消除了并发修改错误，系统稳定性显著提高
6. **监控能力**：添加了实时性能监控和告警功能
7. **测试覆盖**：编写了全面的性能测试脚本，验证了所有优化效果

### 优化措施

1. **核心引擎优化**：
   - 优化了处理逻辑，减少了不必要的计算和I/O操作
   - 改进了多线程处理，提高了并发性能
   - 实现了批量存储和处理，减少了数据库操作次数

2. **存储层优化**：
   - 优化了数据库连接池配置，增加了最大连接数到10
   - 实现了批量存储操作，减少了数据库I/O次数
   - 实现了智能记忆压缩功能，根据记忆年龄自动压缩内容
   - 优化了SQLite配置，提高了数据库性能

3. **内存管理**：
   - 实现了记忆压缩和过期机制，减少了存储开销
   - 优化了缓存策略，提高了缓存命中率
   - 修复了内存关联管理器的并发修改错误

4. **性能监控**：
   - 添加了实时性能监控系统，包括内存、CPU、磁盘使用情况
   - 实现了性能告警功能，当指标超过阈值时发出警报
   - 提供了详细的性能分析报告

5. **测试与验证**：
   - 编写了全面的性能测试脚本，验证了所有优化效果
   - 进行了负载测试和稳定性测试
   - 验证了系统在高并发场景下的表现

## 联系方式

- 项目主页：https://github.com/lulin70/memory-classification-engine
- 问题反馈：https://github.com/lulin70/memory-classification-engine/issues
- 讨论社区：https://github.com/lulin70/memory-classification-engine/discussions