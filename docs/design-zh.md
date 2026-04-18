# 记忆分类引擎 - 详细设计文档

## 1. 系统架构设计

### 1.1 整体架构

记忆分类引擎采用模块化、分层架构设计，由以下组件组成：

```
┌─────────────────────┐
│     外部系统       │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│    API/SDK接口      │
│ ┌─────────────────┐ │
│ │ Python SDK      │ │
│ ├─────────────────┤ │
│ │ REST API        │ │
│ ├─────────────────┤ │
│ │ MCP Server      │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  高级封装层        │
│ ┌─────────────────┐ │
│ │ MemoryOrchestrator││
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   核心引擎         │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  多层判断管道      │
│ ┌─────────────────┐ │
│ │ 规则匹配层       │ │
│ ├─────────────────┤ │
│ │ 结构分析层       │ │
│ ├─────────────────┤ │
│ │ 语义推断层       │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  记忆管理         │
│ ┌─────────────────┐ │
│ │ 去重与冲突检测   │ │
│ ├─────────────────┤ │
│ │ 遗忘机制         │ │
│ ├─────────────────┤ │
│ │ Nudge机制        │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  记忆质量评估      │
│ ┌─────────────────┐ │
│ │ 使用追踪         │ │
│ ├─────────────────┤ │
│ │ 反馈分析         │ │
│ ├─────────────────┤ │
│ │ 质量计算         │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  记忆迁移系统      │
│ ┌─────────────────┐ │
│ │ 数据导出         │ │
│ ├─────────────────┤ │
│ │ 数据导入         │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  存储层           │
│ ┌─────────────────┐ │
│ │ 工作记忆         │ │
│ ├─────────────────┤ │
│ │ 程序性记忆       │ │
│ ├─────────────────┤ │
│ │ 情节记忆         │ │
│ ├─────────────────┤ │
│ │ 语义记忆         │ │
│ └─────────────────┘ │
└─────────────────────┘
```

### 1.2 核心组件描述

1. **API/SDK接口**：提供外部系统与记忆分类引擎之间的交互接口，支持Python SDK、REST API和MCP Server。
   - **Python SDK**：核心编程接口，提供完整功能访问。
   - **REST API**：基于HTTP的接口，支持跨语言集成。
   - **MCP Server**：实现MCP协议，支持与Claude Code、Cursor等工具集成。

2. **高级封装层**：
   - **MemoryOrchestrator**：一站式记忆管理解决方案，提供统一的高级接口，集成分类、存储、检索、遗忘、质量评估和迁移功能。

3. **核心引擎**：协调各模块工作，处理外部请求，是整个系统的枢纽。

4. **多层判断管道**：
   - **规则匹配层**：基于正则表达式和关键词匹配，识别明确的用户信号。
   - **结构分析层**：分析对话的交互模式，识别重复提问、方案接受/拒绝等模式。
   - **语义推断层**：调用LLM进行语义分析，处理复杂的记忆识别。

5. **记忆管理**：
   - **去重与冲突检测**：避免重复记忆，处理记忆冲突。
   - **遗忘机制**：基于时间、频率和重要性的加权衰减算法。
   - **Nudge机制**：主动记忆审查和验证系统，定期检查和调整记忆。

6. **记忆质量评估**：
   - **使用追踪**：记录记忆使用频率和场景。
   - **反馈分析**：收集和分析用户对记忆的反馈。
   - **质量计算**：基于多维度指标计算记忆质量分数。

7. **记忆迁移系统**：
   - **数据导出**：将记忆导出为标准JSON格式。
   - **数据导入**：从标准JSON格式导入记忆。

8. **存储层**：
   - **工作记忆**：内存存储，会话结束后清除。
   - **程序性记忆**：基于文件系统的存储，适合用户偏好和行为规则。
   - **情节记忆**：基于SQLite的存储，适合决策记录和任务模式。
   - **语义记忆**：基于SQLite的存储，适合事实声明和关系信息。

## 2. 核心模块设计

### 2.1 核心引擎模块

#### 2.1.1 功能设计
- 初始化和配置管理
- 处理用户消息，协调多层判断管道
- 管理记忆存储和检索
- 提供外部接口

#### 2.1.2 类设计

```python
class MemoryClassificationEngine:
    def __init__(self, config_path=None):
        # 初始化引擎，加载配置
        pass
    
    def process_message(self, message, context=None):
        # 处理用户消息，返回记忆分类结果
        pass
    
    def retrieve_memories(self, query, limit=5):
        # 根据查询检索相关记忆
        pass
    
    def manage_memory(self, action, memory_id, data=None):
        # 管理记忆（查看、编辑、删除）
        pass
    
    def get_stats(self):
        # 获取系统统计信息
        pass
```

### 2.2 多层判断管道模块

#### 2.2.1 规则匹配层

**功能**：基于规则配置识别明确的用户信号。

**设计**：
- 规则配置：YAML格式，支持正则表达式和关键词匹配
- 规则加载：从配置文件加载规则
- 规则匹配：将规则应用到用户输入，识别记忆类型

**规则配置示例**：
```yaml
rules:
  - pattern: "记住(这个|这点|这条)"
    memory_type: user_preference
    tier: 2
    action: extract_following_content
  
  - pattern: "(不要|别|以后不)(用|写|做|说)"
    memory_type: user_preference
    tier: 2
    action: extract_following_content
  
  - pattern: "(不对|错了|不是|你搞错了|我说的是)"
    memory_type: correction
    tier: 3
    action: extract_surrounding_context
```

#### 2.2.2 结构分析层

**功能**：分析对话结构，识别模式。

**设计**：
- 对话状态跟踪：跟踪对话状态和模式
- 重复检测：检测重复提问和任务模式
- 方案接受/拒绝识别：识别用户对方案的接受或拒绝

#### 2.2.3 语义推断层

**功能**：使用LLM进行语义分析，处理复杂的记忆识别。

**设计**：
- LLM调用：调用轻量级LLM进行语义分析
- 提示词设计：设计有效的提示词引导LLM进行记忆分类
- 成本控制：限制LLM调用频率，缓存结果

**提示词示例**：
```
你是一个记忆分类器。分析以下对话片段，判断是否有值得长期记忆的信息。

记忆类型包括：
- user_preference: 用户表达的偏好或习惯
- fact_declaration: 用户陈述的客观事实
- decision: 明确达成的决定或结论
- relationship: 人、团队、组织之间的关系
- task_pattern: 重复的任务类型
- sentiment_marker: 用户对某话题的情感倾向
- correction: 用户对之前输出的纠正

如果对话中没有值得记忆的信息，请返回空。

当前对话：
{conversation_snippet}

已知用户记忆：
{existing_memory_summary}

请以JSON格式输出，包括以下字段：
- has_memory: boolean
- memory_type: string (枚举值)
- content: string (记忆内容，简洁准确)
- tier: int (2=程序性记忆, 3=情节记忆, 4=语义记忆)
- confidence: float (0.0-1.0)
- reasoning: string (简要判断原因)
```

### 2.3 记忆管理模块

#### 2.3.1 去重与冲突检测

**功能**：检测并处理记忆重复和冲突。

**设计**：
- 重复检测：基于内容相似度和记忆类型检测重复记忆
- 冲突检测：检测新旧记忆之间的冲突
- 冲突解决：基于时间戳和置信度提供冲突解决机制

#### 2.3.2 遗忘机制

**功能**：基于时间、频率和重要性自动衰减和淘汰低价值记忆。

**设计**：
- 记忆权重计算：基于时间衰减、访问频率和置信度计算记忆权重
- 记忆归档：当记忆权重低于阈值时标记为归档
- 记忆清理：定期清理归档记忆

**权重计算公式**：
```
记忆权重 = 置信度 × 新鲜度分数 × 频率分数

新鲜度分数 = exp(-λ × 上次访问天数)  # 指数衰减
频率分数 = log(1 + 访问次数)            # 对数增长，边际递减
```

### 2.3.5 反馈循环模块 (v2.0)

**目的**：通过用户反馈自动提升分类准确率

**核心组件**：

| 组件 | 功能 |
|------|------|
| `FeedbackEvent` | 记录单次反馈事件（memory_id, correction_type, suggested_type） |
| `FeedbackAnalyzer` | 从累积反馈中检测模式（最少出现 3 次） |
| `RuleTuner` | 根据检测到的模式生成规则建议 |
| `FeedbackLoop` | 编排完整流水线：记录 → 分析 → 调优 → 自动应用 |

**流水线流程**：
```
用户纠正 → FeedbackEvent → FeedbackAnalyzer(模式检测, min=3)
    → RuleTuner(规则生成) → 自动应用(confidence > threshold)
```

**配置**：自动应用阈值默认 0.8，可通过 `feedback_loop.auto_apply_threshold` 配置

**文件位置**：[layers/feedback_loop.py](../src/memory_classification_engine/layers/feedback_loop.py)

### 2.3.6 模型蒸馏接口 (v2.0)

**目的**：面向生产环境的成本感知路由，支持不同模型层级

**核心组件**：

| 组件 | 功能 |
|------|------|
| `DistillationMode` 枚举 | `EMBEDDING_ONLY`, `WEAK_MODEL`, `STRONG_MODEL` |
| `ModelTier` 枚举 | `EMBEDDING`, `SMALL_LLM`, `LARGE_LLM` |
| `ClassificationRequest` | 输入：消息 + 可选上下文 + 元数据 |
| `ConfidenceEstimator` | 估算分类难度（0.0–1.0） |
| `DistillationRouter` | 根据置信度路由到合适的模型层级 |

**路由逻辑**：
| 置信度范围 | 路由 | 成本 |
|-----------|------|------|
| > 0.85 | 仅 embedding | 零 LLM 成本 |
| 0.50 – 0.85 | 弱/小模型 | 低成本 |
| < 0.50 | 强/大模型 | 较高成本 |

**附加功能**：
- `export_training_data()`：导出分类数据用于离线模型蒸馏
- 运行时模式切换 via `set_mode()`

**文件位置**：[layers/distillation.py](../src/memory_classification_engine/layers/distillation.py)

### 2.4 存储层模块

#### 2.4.1 工作记忆

**功能**：存储当前会话的上下文信息。

**设计**：
- 内存存储：使用Python字典或队列存储
- 会话管理：会话结束后自动清除
- 大小限制：设置最大容量，避免过度内存使用

#### 2.4.2 程序性记忆

**功能**：存储用户偏好和行为规则等固定信息。

**设计**：
- 文件存储：使用YAML/JSON文件存储
- 分层加载：支持全局、项目级和本地级配置
- 格式设计：结构化格式，便于阅读和修改

**存储格式示例**：
```yaml
user_preferences:
  - id: "pref_001"
    content: "使用双引号而不是单引号"
    created_at: "2026-04-03T10:00:00Z"
    updated_at: "2026-04-03T10:00:00Z"
    confidence: 1.0
    source: "rule:0"
```

#### 2.4.3 情节记忆

**功能**：存储决策记录和任务模式等与时间相关的信息。

**设计**：
- SQLite存储：使用SQLite数据库存储
- 表结构设计：包含记忆元数据和内容
- 检索优化：支持基于时间和内容的检索

**表结构设计**：
```sql
CREATE TABLE episodic_memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_accessed TEXT NOT NULL,
    access_count INTEGER DEFAULT 0,
    confidence REAL NOT NULL,
    source TEXT NOT NULL,
    context TEXT,
    status TEXT DEFAULT 'active'
);
```

#### 2.4.4 语义记忆

**功能**：存储事实声明和关系信息等结构化知识。

**设计**：
- SQLite存储：使用SQLite数据库存储
- 关系模型：使用实体-关系-属性模型
- 查询优化：支持复杂关系查询

**表结构设计**：
```sql
CREATE TABLE semantic_entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE semantic_relationships (
    id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    confidence REAL NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES semantic_entities(id),
    FOREIGN KEY (object_id) REFERENCES semantic_entities(id)
);
```

### 2.5 高级封装模块

#### 2.5.1 MemoryOrchestrator

**功能**：提供一站式记忆管理解决方案，集成分类、存储、检索、遗忘、质量评估和迁移功能。

**设计**：
- 统一接口：提供简洁的API，隐藏底层复杂性
- 功能集成：集成学习、回忆、遗忘、搜索、质量评估和迁移等所有核心功能
- 错误处理：全面的异常捕获和错误处理
- 日志记录：详细的操作日志

**核心方法**：
```python
class MemoryOrchestrator:
    def learn(self, message, context=None, execution_context=None):
        # 学习新记忆
        pass
    
    def recall(self, query, memory_type=None, limit=10):
        # 回忆相关记忆
        pass
    
    def forget(self, memory_id, action='decrease_weight', weight_adjustment=0.1):
        # 遗忘或调整记忆
        pass
    
    def search(self, search_term, memory_types=None, min_confidence=0.5, limit=20):
        # 高级搜索
        pass
    
    def get_memory_quality(self, memory_id):
        # 获取记忆质量
        pass
    
    def generate_quality_report(self, days=30):
        # 生成质量报告
        pass
    
    def export_memories(self, include_metadata=True):
        # 导出记忆
        pass
    
    def import_memories(self, json_str, validate_checksum=True):
        # 导入记忆
        pass
```

### 2.6 记忆质量评估模块

**功能**：跟踪记忆使用、有效性和价值，提供质量评估和报告。

**设计**：
- 数据跟踪：记录记忆使用和用户反馈
- 多维度评估：基于使用频率、成功率、反馈分数、新鲜度和多样性计算质量
- 报告生成：生成质量报告和低价值记忆报告
- 实时更新：当记忆被使用时自动更新使用统计

**核心方法**：
```python
class MemoryQualityManager:
    def track_memory_usage(self, memory_id, query, result=True):
        # 跟踪记忆使用
        pass
    
    def track_feedback(self, memory_id, feedback, context=None):
        # 跟踪用户反馈
        pass
    
    def calculate_memory_quality(self, memory_id, memory):
        # 计算记忆质量
        pass
    
    def generate_low_value_report(self, threshold=0.3, days=30):
        # 生成低价值记忆报告
        pass
    
    def generate_quality_report(self, days=30):
        # 生成质量报告
        pass
```

### 2.7 记忆迁移模块

**功能**：实现记忆导出和导入，支持跨会话、跨Agent的记忆迁移。

**设计**：
- 标准格式：定义统一的JSON格式，确保跨平台兼容性
- 数据验证：生成和验证校验和，确保数据完整性
- 文件支持：支持导出到文件和从文件导入
- 错误处理：全面的异常捕获和错误处理

**核心方法**：
```python
class MemoryMigrationManager:
    def export_memories(self, memories, include_metadata=True):
        # 导出记忆到标准格式
        pass
    
    def import_memories(self, json_str, validate_checksum=True):
        # 从标准格式导入记忆
        pass
    
    def export_to_file(self, memories, file_path, include_metadata=True):
        # 导出记忆到文件
        pass
    
    def import_from_file(self, file_path, validate_checksum=True):
        # 从文件导入记忆
        pass
    
    def validate_export_data(self, json_str):
        # 验证导出数据有效性
        pass
```

### 2.8 MCP Server 模块

**功能**：实现MCP（Model Context Protocol）服务器，支持与Claude Code、Cursor等工具集成。

**设计**：
- HTTP服务器：基于标准库http.server实现
- 工具定义：提供8个核心工具用于记忆管理
- 配置管理：通过配置文件支持自定义服务器设置
- 错误处理：全面的异常捕获和错误响应

**核心工具**：
1. **classify_memory**：分析消息并判断是否需要记忆
2. **store_memory**：将记忆存储到合适的层级
3. **retrieve_memories**：检索相关记忆
4. **get_memory_stats**：获取记忆统计信息
5. **batch_classify**：批量分类多条消息
6. **find_similar**：查找相似记忆
7. **export_memories**：将记忆导出为标准格式
8. **import_memories**：从标准格式导入记忆

**实现状态**：✅ 已完成
**实现位置**：`src/memory_classification_engine/integration/layer2_mcp/`

## 3. 数据模型设计

### 3.1 记忆元数据模型

```json
{
  "id": "mem_20260403_001",
  "type": "user_preference",
  "tier": 2,
  "content": "使用双引号而不是单引号",
  "created_at": "2026-04-03T10:00:00Z",
  "updated_at": "2026-04-03T10:00:00Z",
  "last_accessed": "2026-04-03T10:30:00Z",
  "access_count": 5,
  "confidence": 1.0,
  "source": "rule:0",
  "context": "用户在讨论代码风格时提到",
  "status": "active"
}
```

### 3.2 记忆类型枚举

```python
MEMORY_TYPES = {
    "user_preference": "用户偏好",
    "correction": "纠正",
    "fact_declaration": "事实声明",
    "decision": "决策",
    "relationship": "关系",
    "task_pattern": "任务模式",
    "sentiment_marker": "情感标记"
}
```

### 3.3 记忆层级枚举

```python
MEMORY_TIERS = {
    1: "工作记忆",
    2: "程序性记忆",
    3: "情节记忆",
    4: "语义记忆"
}
```

## 4. API接口设计

### 4.1 Python SDK接口（Layer 1）

```python
class MemoryClassificationEngine:
    def __init__(self, config_path=None):
        """初始化引擎"""
        pass
    
    def process_message(self, message, context=None):
        """处理用户消息，返回记忆分类结果"""
        pass
    
    def retrieve_memories(self, query, limit=5):
        """根据查询检索相关记忆"""
        pass
    
    def manage_memory(self, action, memory_id, data=None):
        """管理记忆（查看、编辑、删除）"""
        pass
    
    def get_stats(self):
        """获取系统统计信息"""
        pass
    
    def export_memories(self, format="json"):
        """导出记忆数据"""
        pass
    
    def import_memories(self, data, format="json"):
        """导入记忆数据"""
        pass
```

### 4.2 MCP Server接口（Layer 2）⭐ 近期重点

#### 4.2.1 MCP Server架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server模块                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  server.py - MCP Server主入口                          │   │
│  │  • 初始化MCP Server                                      │   │
│  │  • 注册所有工具                                          │   │
│  │  • 处理JSON-RPC请求                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  tools.py - 工具定义                                   │   │
│  │  • 8个核心工具定义                                      │   │
│  │  • 输入/输出模式定义                                    │   │
│  │  • 参数验证                                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  handlers.py - 请求处理器                               │   │
│  │  • 每个工具的业务逻辑                                    │   │
│  │  • 调用引擎SDK                                          │   │
│  │  • 错误处理                                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2.2 MCP Tools详细设计

**工具1: classify_memory**

```python
{
    "name": "classify_memory",
    "description": "分析消息并判断是否需要记忆",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "用户消息内容"
            },
            "context": {
                "type": "string",
                "description": "对话上下文（可选）"
            }
        },
        "required": ["message"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "matched": {
                "type": "boolean",
                "description": "是否匹配记忆类型"
            },
            "memory_type": {
                "type": "string",
                "enum": ["user_preference", "correction", "fact_declaration", 
                        "decision", "relationship", "task_pattern", "sentiment_marker"],
                "description": "记忆类型"
            },
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "记忆层级"
            },
            "content": {
                "type": "string",
                "description": "提取的记忆内容"
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "置信度"
            },
            "reasoning": {
                "type": "string",
                "description": "判断原因"
            }
        }
    }
}
```

**工具2: store_memory**

```python
{
    "name": "store_memory",
    "description": "将记忆存储到合适的层级",
    "inputSchema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "记忆内容"
            },
            "memory_type": {
                "type": "string",
                "enum": ["user_preference", "correction", "fact_declaration", 
                        "decision", "relationship", "task_pattern", "sentiment_marker"],
                "description": "记忆类型"
            },
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "记忆层级（可选，默认自动确定）"
            },
            "context": {
                "type": "string",
                "description": "上下文信息（可选）"
            }
        },
        "required": ["content", "memory_type"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "memory_id": {
                "type": "string",
                "description": "记忆ID"
            },
            "stored": {
                "type": "boolean",
                "description": "是否成功存储"
            },
            "tier": {
                "type": "integer",
                "description": "实际存储层级"
            }
        }
    }
}
```

**工具3: retrieve_memories**

```python
{
    "name": "retrieve_memories",
    "description": "检索相关记忆",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "查询内容"
            },
            "limit": {
                "type": "integer",
                "default": 5,
                "description": "结果数量限制"
            },
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "指定层级（可选）"
            }
        },
        "required": ["query"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "memories": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "type": {"type": "string"},
                        "tier": {"type": "integer"},
                        "content": {"type": "string"},
                        "confidence": {"type": "number"},
                        "created_at": {"type": "string"},
                        "relevance_score": {"type": "number"}
                    }
                }
            }
        }
    }
}
```

**工具4: get_memory_stats**

```python
{
    "name": "get_memory_stats",
    "description": "获取记忆统计信息",
    "inputSchema": {
        "type": "object",
        "properties": {
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "指定层级（可选，不指定则返回所有层级）"
            }
        }
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "total_memories": {"type": "integer"},
            "by_tier": {
                "type": "object",
                "properties": {
                    "2": {"type": "integer"},
                    "3": {"type": "integer"},
                    "4": {"type": "integer"}
                }
            },
            "by_type": {
                "type": "object",
                "additionalProperties": {"type": "integer"}
            },
            "storage_size": {"type": "string"}
        }
    }
}
```

#### 4.2.3 MCP Server配置

**claude_desktop_config.json:**

```json
{
  "mcpServers": {
    "memory-classification-engine": {
      "command": "python",
      "args": ["-m", "mce_mcp_server"],
      "env": {
        "MCE_CONFIG_PATH": "/path/to/config.yaml",
        "MCE_DATA_PATH": "/path/to/data"
      }
    }
  }
}
```

**Cursor MCP配置:**

```json
{
  "mcpServers": {
    "memory-classification-engine": {
      "command": "python",
      "args": ["-m", "mce_mcp_server"],
      "env": {
        "MCE_CONFIG_PATH": "/path/to/config.yaml",
        "MCE_DATA_PATH": "/path/to/data"
      }
    }
  }
}
```

### 4.3 OpenClaw CLI接口（Layer 2）

#### 4.3.1 CLI命令设计

```bash
# 安装
pip install mce-openclaw

# 分类记忆
mce-openclaw classify --message "我喜欢使用双引号" --context "代码风格讨论"

# 存储记忆
mce-openclaw store --content "使用双引号" --type user_preference --tier 2

# 检索记忆
mce-openclaw retrieve --query "代码风格" --limit 5

# 获取统计信息
mce-openclaw stats [--tier 2]

# 批量分类
mce-openclaw batch-classify --file messages.json

# 查找相似记忆
mce-openclaw find-similar --content "代码风格偏好" --threshold 0.8

# 导出记忆
mce-openclaw export --format json --output memories.json [--tier 3]

# 导入记忆
mce-openclaw import --file memories.json --format json
```

#### 4.3.2 OpenClaw配置文件 (.clawrc)

```yaml
# .clawrc - OpenClaw配置文件
version: "1.0"

tools:
  - name: mce_classify
    description: 分析消息并判断是否需要记忆
    command: mce-openclaw classify
    args:
      - name: message
        type: string
        required: true
        description: 用户消息内容
      - name: context
        type: string
        required: false
        description: 对话上下文

  - name: mce_store
    description: 将记忆存储到合适的层级
    command: mce-openclaw store
    args:
      - name: content
        type: string
        required: true
        description: 记忆内容
      - name: type
        type: string
        required: true
        description: 记忆类型
      - name: tier
        type: integer
        required: false
        description: 记忆层级

  - name: mce_retrieve
    description: 检索相关记忆
    command: mce-openclaw retrieve
    args:
      - name: query
        type: string
        required: true
        description: 查询内容
      - name: limit
        type: integer
        required: false
        default: 5
        description: 结果数量

  - name: mce_stats
    description: 获取记忆统计信息
    command: mce-openclaw stats
    args:
      - name: tier
        type: integer
        required: false
        description: 指定层级
```

### 4.4 框架适配器接口（Layer 3）

#### 4.4.1 LangChain适配器

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional

class ClassifyMemoryInput(BaseModel):
    message: str = Field(description="用户消息内容")
    context: Optional[str] = Field(default=None, description="对话上下文")

class MemoryClassifierTool(BaseTool):
    """LangChain工具用于记忆分类"""
    
    name: str = "memory_classifier"
    description: str = "分类并存储用户记忆"
    args_schema: type[BaseModel] = ClassifyMemoryInput
    
    def __init__(self, config_path: str = None):
        super().__init__()
        from memory_classification_engine import MemoryClassificationEngine
        self.engine = MemoryClassificationEngine(config_path)
    
    def _run(self, message: str, context: Optional[str] = None) -> dict:
        """运行工具"""
        return self.engine.process_message(message, context)
    
    async def _arun(self, message: str, context: Optional[str] = None) -> dict:
        """异步运行"""
        return self._run(message, context)
```

#### 4.4.2 CrewAI适配器

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional

class StoreMemoryInput(BaseModel):
    content: str = Field(description="记忆内容")
    memory_type: str = Field(description="记忆类型")
    tier: Optional[int] = Field(default=None, description="记忆层级")

class MemoryTool(BaseTool):
    """CrewAI工具用于记忆管理"""
    
    name: str = "memory_tool"
    description: str = "管理用户记忆 - 分类、存储和检索"
    args_schema: Type[BaseModel] = StoreMemoryInput
    
    def __init__(self, config_path: str = None):
        super().__init__()
        from memory_classification_engine import MemoryClassificationEngine
        self.engine = MemoryClassificationEngine(config_path)
    
    def _run(self, content: str, memory_type: str, tier: Optional[int] = None) -> dict:
        """存储记忆"""
        return self.engine.store_memory(content, memory_type, tier)
```

#### 4.4.3 AutoGen适配器

```python
from autogen import ConversableAgent
from typing import Dict, Any, Optional

class MemoryAgent(ConversableAgent):
    """具有记忆能力的AutoGen Agent"""
    
    def __init__(
        self,
        name: str,
        config_path: Optional[str] = None,
        system_message: Optional[str] = None,
        **kwargs
    ):
        # 初始化记忆引擎
        from memory_classification_engine import MemoryClassificationEngine
        self.memory_engine = MemoryClassificationEngine(config_path)
        
        # 构建带有记忆能力的系统消息
        enhanced_system_message = self._build_system_message(system_message)
        
        super().__init__(
            name=name,
            system_message=enhanced_system_message,
            **kwargs
        )
    
    def _build_system_message(self, base_message: Optional[str]) -> str:
        """构建增强的系统消息"""
        memory_capabilities = """
你可以访问一个记忆分类引擎，它可以：
1. 分类用户消息中的重要信息以进行记忆
2. 将记忆存储到合适的层级
3. 根据上下文检索相关记忆

使用这些能力提供个性化的响应。
"""
        if base_message:
            return f"{base_message}\n\n{memory_capabilities}"
        return memory_capabilities
    
    def process_message_with_memory(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """处理消息并自动分类记忆"""
        # 首先检索相关记忆
        memories = self.memory_engine.retrieve_memories(message)
        
        # 分类当前消息
        classification = self.memory_engine.process_message(message, context)
        
        return {
            "memories": memories,
            "classification": classification
        }
```

### 4.5 REST API接口

#### 4.5.1 处理消息
- **URL**: `/api/message`
- **方法**: POST
- **请求体**:
  ```json
  {
    "message": "记住，我不喜欢在代码中使用连字符",
    "context": {}
  }
  ```
- **响应**:
  ```json
  {
    "matched": true,
    "memory_type": "user_preference",
    "tier": 2,
    "content": "不喜欢在代码中使用连字符",
    "confidence": 1.0,
    "source": "rule:0"
  }
  ```

#### 4.5.2 检索记忆
- **URL**: `/api/memories`
- **方法**: GET
- **查询参数**:
  - `query`: 检索查询
  - `limit`: 结果数量限制
- **响应**:
  ```json
  {
    "memories": [
      {
        "id": "mem_20260403_001",
        "type": "user_preference",
        "tier": 2,
        "content": "不喜欢在代码中使用连字符",
        "confidence": 1.0,
        "source": "rule:0"
      }
    ]
  }
  ```

#### 4.5.3 管理记忆
- **URL**: `/api/memories/{id}`
- **方法**: GET, PUT, DELETE
- **请求体** (PUT):
  ```json
  {
    "content": "不喜欢在代码中使用连字符和分号",
    "confidence": 1.0
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "memory": {
      "id": "mem_20260403_001",
      "type": "user_preference",
      "tier": 2,
      "content": "不喜欢在代码中使用连字符和分号",
      "confidence": 1.0,
      "source": "rule:0"
    }
  }
  ```

## 5. 测试计划设计

### 5.1 单元测试

**测试目标**：验证各模块的功能正确性。

**测试内容**：
- 核心引擎初始化和配置
- 规则匹配层的规则加载和匹配
- 结构分析层的模式识别
- 语义推断层的LLM调用和结果解析
- 记忆管理中的去重和冲突检测
- 遗忘机制中的权重计算和记忆归档
- 存储层的读写操作

**新增 - Layer 2单元测试**：
- MCP Server初始化
- MCP Tools参数验证
- MCP Tools业务逻辑
- OpenClaw CLI命令解析
- OpenClaw CLI参数验证

**测试工具**：
- pytest
- mock库（模拟LLM调用）
- pytest-asyncio（MCP Server异步测试）

### 5.2 集成测试

**测试目标**：验证模块之间的集成是否正常。

**测试内容**：
- 完整的记忆分类流程
- 记忆存储和检索流程
- 记忆管理操作
- API接口调用

**新增 - Layer 2/3集成测试**：
- MCP Server和Engine SDK集成
- MCP JSON-RPC协议兼容性
- Claude Code MCP客户端兼容性
- Cursor MCP客户端兼容性
- OpenClaw CLI和Engine SDK集成
- OpenClaw配置文件解析
- LangChain适配器集成
- CrewAI适配器集成
- AutoGen适配器集成

**测试工具**：
- pytest
- requests（测试REST API）
- mcp.client（MCP客户端测试）
- subprocess（CLI测试）

### 5.3 性能测试

**测试目标**：验证系统性能和资源使用情况。

**测试内容**：
- 记忆分类响应时间
- 记忆检索响应时间
- 系统处理并发请求的能力
- 内存使用情况
- 存储使用情况

**测试工具**：
- pytest-benchmark
- timeit
- memory-profiler

### 5.4 用户验收测试

**测试目标**：验证系统是否满足用户需求。

**测试内容**：
- 记忆分类准确性
- 记忆检索相关性
- 记忆管理的易用性
- 系统的整体用户体验

**测试方法**：
- 准备测试用例
- 让用户代表执行测试
- 收集用户反馈
- 分析测试结果

## 6. 部署计划设计

### 6.1 部署环境

**本地部署**：
- Python 3.8+
- 依赖：PyYAML, SQLite3, Flask（可选，用于REST API）

**容器部署**：
- Docker镜像
- Docker Compose配置

### 6.2 配置管理

**配置文件**：
- `config/config.yaml`：系统配置
- `config/rules.yaml`：规则配置

**环境变量**：
- `MCE_CONFIG_PATH`：配置文件路径
- `MCE_DATA_PATH`：数据存储路径
- `MCE_LLM_API_KEY`：LLM API密钥（可选）

### 6.3 部署步骤

**本地部署**：
1. 克隆代码仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 配置规则：编辑 `config/rules.yaml`
4. 启动服务：`python -m memory_classification_engine`

**容器部署**：
1. 构建镜像：`docker build -t memory-classification-engine .`
2. 运行容器：`docker run -p 5000:5000 memory-classification-engine`

### 6.4 监控与维护

**监控**：
- 日志记录：系统运行日志
- 性能监控：响应时间、资源使用情况
- 错误监控：异常和错误记录

**维护**：
- 定期数据备份
- 定期清理归档记忆
- 定期更新规则配置

## 7. 安全设计

### 7.1 数据安全

- **数据加密**：敏感记忆信息加密存储
- **访问控制**：基于角色的访问权限管理
- **数据最小化**：只存储必要的记忆信息
- **遗忘机制**：支持用户主动删除记忆
- **审计日志**：记录所有记忆访问和修改操作

### 7.2 API安全

- **认证**：API访问需要认证
- **授权**：基于角色的权限控制
- **输入验证**：验证用户输入以防止注入攻击
- **速率限制**：防止API滥用
- **HTTPS**：使用HTTPS保护传输数据

## 8. 可扩展性设计

### 8.1 模块扩展

- **记忆类型扩展**：支持添加新的记忆类型
- **存储后端扩展**：支持添加新的存储后端
- **判断层扩展**：支持添加新的判断层

### 8.2 集成扩展

- **Agent框架集成**：支持与不同的Agent框架集成
- **LLM集成**：支持与不同的LLM集成
- **第三方服务集成**：支持与第三方服务集成

## 9. 技术风险与应对措施

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 语义推断层性能问题 | 响应时间过长，影响用户体验 | 优先使用轻量级模型，设置调用频率限制，实现缓存机制 |
| 存储容量增长过快 | 系统性能下降，存储成本增加 | 实现自动遗忘机制，定期清理低价值记忆，优化存储结构 |
| 记忆冲突处理复杂 | 系统行为不可预测，用户体验差 | 设计明确的冲突解决策略，提供用户干预机制，记录冲突历史 |
| 多语言支持难度 | 跨语言记忆一致性问题 | 采用基于语义的记忆表示，优先支持英文和中文，使用翻译API进行跨语言映射 |
| LLM依赖风险 | LLM服务不可用，系统功能受限 | 实现降级策略，当LLM不可用时，仅使用规则匹配和结构分析层 |

## 10. 改进计划

### 10.1 改进背景

记忆分类引擎是AI Agent的核心组件，负责智能记忆分类、分层存储、高效检索和可控遗忘。随着AI技术的发展和应用场景的扩展，记忆分类引擎需要不断改进和优化，以满足日益复杂的需求。当前系统存在性能问题，需要优先优化性能，同时进行代码重构、配置管理改进、文档增强和依赖管理优化。

### 10.2 改进目标

#### 10.2.1 核心目标
- 优化存储和检索性能（主要目标）
- 提高记忆分类准确性和覆盖范围
- 增强系统可扩展性和可维护性
- 改善用户体验和集成能力

#### 10.2.2 具体目标
- 将记忆检索响应时间减少到50ms以内
- 将记忆分类准确性提高到90%以上
- 优化系统启动和运行时
- 支持更多语言和复杂场景
- 提供更灵活的集成接口
- 增强系统稳定性和可靠性
- 消除代码重复，提高代码复用性
- 将硬编码参数移至配置文件
- 完成系统级文档，包括架构设计、API文档等
- 使用虚拟环境和依赖锁定避免版本冲突

### 10.3 改进领域

#### 10.3.1 核心引擎改进
- 优化核心引擎性能和稳定性
- 改进记忆分类算法和策略
- 增强上下文理解能力
- 提高系统可配置性
- 消除代码重复，提高代码复用性

#### 10.3.2 存储层改进
- 优化存储结构和索引
- 提高存储后端性能
- 增强数据安全和隐私保护
- 支持更多存储后端选项

#### 10.3.3 检索和注入改进
- 优化记忆检索算法
- 改进记忆注入格式和策略
- 增强语义理解和相关性排序
- 支持更复杂的检索场景

#### 10.3.4 多语言支持
- 增强多语言记忆一致性
- 改进跨语言记忆映射
- 支持更多语言的记忆分类
- 优化语言检测和处理

#### 10.3.5 可扩展性和集成
- 提供更灵活的SDK和API
- 增强与不同Agent框架的集成
- 支持更多LLM模型
- 提供更多集成示例

#### 10.3.6 配置管理
- 将硬编码参数移至配置文件
- 建立统一的配置管理机制
- 支持环境变量和配置文件的混合配置
- 提供配置验证和默认值管理

#### 10.3.7 文档增强
- 完成系统级文档，包括架构设计、API文档等
- 全面更新各种需求/设计文档
- 完成README和英文版文档
- 提供详细的使用示例和教程

#### 10.3.8 依赖管理
- 使用虚拟环境和依赖锁定
- 避免版本冲突
- 优化依赖安装和管理
- 建立依赖更新策略

### 10.4 实施计划

#### 10.4.1 阶段1：性能评估和规划（2周）
- 任务1.1：性能评估 - 评估当前系统性能瓶颈和问题
- 任务1.2：代码分析 - 分析代码结构和重复
- 任务1.3：改进规划 - 制定详细的改进计划，优先考虑性能优化
- 任务1.4：技术研究 - 研究相关性能优化技术和解决方案

#### 10.4.2 阶段2：核心性能优化（4周）
- 任务2.1：存储层性能优化 - 优化存储结构和索引，提高存储和检索性能
- 任务2.2：检索算法优化 - 优化记忆检索算法，减少响应时间
- 任务2.3：核心引擎性能优化 - 优化核心引擎性能和稳定性
- 任务2.4：代码重构 - 消除代码重复，提高代码复用性
- 任务2.5：配置管理改进 - 将硬编码参数移至配置文件，建立统一的配置管理机制

#### 10.4.3 阶段3：功能增强和集成（3周）
- 任务3.1：记忆分类算法改进 - 改进记忆分类算法和策略，提高准确性
- 任务3.2：多语言支持增强 - 增强多语言记忆一致性和支持
- 任务3.3：SDK和API改进 - 提供更灵活的SDK和API
- 任务3.4：框架和LLM集成 - 增强与不同Agent框架和LLM模型的集成

#### 10.4.4 阶段4：文档增强和依赖管理（2周）
- 任务4.1：文档增强 - 完成系统级文档，包括架构设计、API文档等；全面更新各种需求/设计文档，包括README和英文版
- 任务4.2：依赖管理改进 - 使用虚拟环境和依赖锁定，避免版本冲突
- 任务4.3：测试和优化 - 编写和运行测试，基于测试结果进行优化和修复

#### 10.4.5 阶段5：部署和性能验证（1周）
- 任务5.1：部署准备 - 准备部署环境和配置
- 任务5.2：系统部署 - 将系统部署到目标环境
- 任务5.3：性能验证 - 验证系统性能是否达到目标
- 任务5.4：监控设置和培训 - 设置系统监控和告警，提供培训和文档

### 10.5 预期结果

#### 10.5.1 技术结果
- 优化的记忆分类引擎
- 改进的存储和检索性能
- 增强的多语言支持
- 更灵活的集成接口
- 完整的测试和文档

#### 10.5.2 业务结果
- 提高AI Agent的记忆能力
- 增强用户体验
- 减少系统资源使用
- 提高系统稳定性和可靠性
- 支持更多应用场景

### 10.6 成功指标

- 记忆分类准确性 ≥ 90%
- 记忆检索响应时间 ≤ 50ms
- 系统稳定性 ≥ 99.9%
- 用户满意度 ≥ 85%
- 集成成功率 ≥ 95%

## 11. 结论

本详细设计文档为记忆分类引擎提供了完整的技术实现方案，包括系统架构、核心模块设计、数据模型设计、API接口设计、测试计划设计、部署计划设计、安全设计和可扩展性设计。

该设计采用模块化、分层架构，确保系统的可扩展性和可维护性。同时，通过轻量级技术选型，确保系统能够在资源受限的环境中正常运行。

本设计充分考虑了用户需求和技术挑战，为记忆分类引擎提供了一个完整、实用的实现方案。

通过实施改进计划，记忆分类引擎将不断优化和改进，为AI Agent提供更智能、高效的记忆管理能力，支持更复杂的应用场景。