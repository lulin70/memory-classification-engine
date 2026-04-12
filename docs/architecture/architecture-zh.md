# 架构设计

## 1. 系统架构

Memory Classification Engine 采用分层架构设计，主要包括以下层次：

### 1.1 核心架构

```
┌──────────────────────────────────────────────────────────────────┐
│                       应用层 (Application)                     │
├──────────────────────────────────────────────────────────────────┤
│                     引擎层 (Engine)                           │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│ │  Rule Matcher   │  │ Pattern Analyzer │  │ Semantic Classifier │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├──────────────────────────────────────────────────────────────────┤
│                     存储层 (Storage)                          │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│ │   Tier 1 (WM)   │  │   Tier 2 (PM)   │  │   Tier 3 (EM)   │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│ ┌───────────────────────────────────────────────────────────┐ │
│ │                     Tier 4 (SM)                         │ │
│ └───────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────┤
│                     工具层 (Utilities)                       │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│ │    Helpers     │  │    Logger      │  │   Exceptions    │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 插件架构

```
┌──────────────────────────────────────────────────────────────────┐
│                     插件管理器 (PluginManager)                │
├──────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│ │  内置插件       │  │  外部插件       │  │  自定义插件     │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## 2. 核心组件

### 2.1 引擎层

#### 2.1.1 MemoryClassificationEngine
- **功能**：核心引擎，协调各组件工作
- **职责**：
  - 处理用户消息
  - 调用分类层进行记忆分类
  - 管理记忆存储
  - 协调插件执行
  - 提供API接口

#### 2.1.2 分类层

| 组件 | 功能 | 实现方式 |
|------|------|----------|
| Rule Matcher | 基于规则的匹配 | 正则表达式，关键词匹配 |
| Pattern Analyzer | 模式分析 | 模式识别，序列分析 |
| Semantic Classifier | 语义分类 | 文本分析，相似度计算 |

### 2.2 存储层

#### 2.2.1 存储层级

| 层级 | 名称 | 存储方式 | 特点 |
|------|------|----------|------|
| Tier 1 | 工作记忆 | 内存 | 临时存储，快速访问 |
| Tier 2 | 程序性记忆 | JSON文件 | 结构化存储，用户偏好 |
| Tier 3 | 情节记忆 | SQLite + FTS5 + 向量存储 | 大容量存储，全文搜索，向量检索 |
| Tier 4 | 语义记忆 | SQLite + 知识图谱 | 长期存储，语义关联，知识推理 |

#### 2.2.2 存储实现

- **Tier 1**：使用Python内存字典
- **Tier 2**：使用JSON文件存储
- **Tier 3**：使用SQLite+FTS5+向量存储（FAISS/TF-IDF）
- **Tier 4**：使用SQLite+知识图谱（NetworkX）

### 2.3 工具层

| 组件 | 功能 | 实现方式 |
|------|------|----------|
| Helpers | 工具函数 | 通用工具方法 |
| Logger | 日志系统 | 分级日志记录 |
| Exceptions | 异常处理 | 统一异常体系 |
| Cache | 缓存系统 | LRU缓存实现 |

### 2.4 插件系统

#### 2.4.1 PluginManager
- **功能**：管理插件的加载、执行和生命周期
- **职责**：
  - 发现和加载插件
  - 管理插件状态
  - 协调插件执行
  - 处理插件异常

#### 2.4.2 Plugin基类
- **功能**：定义插件接口
- **方法**：
  - initialize()：初始化插件
  - process_message()：处理消息
  - process_memory()：处理记忆
  - cleanup()：清理资源

## 3. 技术实现

### 3.1 核心技术栈

| 技术 | 用途 | 版本 |
|------|------|------|
| Python | 主要开发语言 | 3.9+ |
| SQLite | 数据存储 | 3.35+ |
| FTS5 | 全文搜索 | 内置 |
| FAISS | 向量存储和检索 | 1.7.4+ |
| scikit-learn | 文本向量化 | 1.3.0+ |
| JSON | 配置和数据存储 | 标准库 |
| Pytest | 测试框架 | 7.0+ |

### 3.2 关键模块实现

#### 3.2.1 存储模块

**BaseStorage**：抽象基类，定义存储接口
- 方法：store_memory(), retrieve_memories(), update_memory(), delete_memory()
- 辅助方法：_prepare_memory(), _handle_error()

**Tier3StorageFTS**：FTS5存储实现
- 特性：全文搜索，索引同步，缓存支持
- 性能：搜索速度提升2-3倍

#### 3.2.2 缓存模块

**LRUCache**：基于LRU算法的缓存
- 特性：大小限制，TTL过期，线程安全
- 性能：O(1)访问时间

**MemoryCache**：记忆缓存管理器
- 特性：预热机制，统计功能，失效机制
- 性能：缓存命中率>80%

#### 3.2.3 插件模块

**PluginManager**：插件管理器
- 特性：自动发现，动态加载，错误隔离
- 性能：插件加载时间<100ms

**SentimentAnalyzerPlugin**：情绪分析插件
- 特性：简单情绪分析，记忆增强
- 性能：分析时间<50ms

### 3.3 数据流

#### 3.3.1 消息处理流程

1. **输入**：用户消息
2. **分类**：通过三层分类器分析
3. **存储**：根据分类结果存储到对应层级
4. **插件处理**：通过插件进行额外处理
5. **返回**：处理结果

#### 3.3.2 搜索流程

1. **输入**：搜索关键词
2. **预处理**：关键词分析，查询优化
3. **搜索**：
   - 英文：FTS5全文搜索 + 向量搜索
   - 中文：LIKE查询 + 向量搜索
4. **排序**：按相关性和置信度排序
5. **返回**：搜索结果

## 4. 性能优化

### 4.1 存储优化

- **索引**：为常用查询创建索引
- **缓存**：热点数据缓存
- **批量操作**：减少数据库访问次数
- **连接池**：复用数据库连接

### 4.2 搜索优化

- **FTS5**：使用全文搜索索引
- **查询优化**：预处理查询语句
- **结果缓存**：缓存搜索结果
- **异步处理**：复杂查询异步执行

### 4.3 内存优化

- **内存限制**：设置合理的内存使用限制
- **垃圾回收**：及时清理不再使用的对象
- **数据压缩**：压缩存储数据
- **延迟加载**：按需加载数据

## 5. 扩展性设计

### 5.1 插件系统

- **热插拔**：支持运行时插件加载
- **隔离**：插件运行在隔离环境
- **API**：统一的插件API
- **管理**：插件生命周期管理

### 5.2 存储扩展

- **抽象接口**：统一的存储接口
- **适配器**：支持不同存储后端
- **分层**：可扩展的存储层级
- **迁移**：数据迁移工具

### 5.3 API扩展

- **REST API**：HTTP接口
- **SDK**：多语言SDK
- **WebSocket**：实时通信
- **事件系统**：事件驱动架构

## 6. 安全性设计

### 6.1 数据安全

- **加密**：敏感数据加密存储
- **备份**：定期数据备份
- **恢复**：灾难恢复机制
- **审计**：操作审计日志

### 6.2 访问控制

- **认证**：用户认证机制
- **授权**：基于角色的访问控制
- **限流**：API访问限流
- **防注入**：SQL注入防护

### 6.3 安全审计

- **日志**：安全相关日志
- **监控**：异常行为监控
- **扫描**：定期安全扫描
- **更新**：及时更新依赖

## 7. 部署与集成

### 7.1 部署方式

- **本地部署**：单机部署
- **容器化**：Docker容器
- **云部署**：云服务部署
- **边缘部署**：边缘设备部署

### 7.2 集成方式

- **API集成**：REST API
- **SDK集成**：多语言SDK
- **插件集成**：第三方插件
- **服务集成**：微服务集成

### 7.3 监控与维护

- **健康检查**：系统健康状态
- **性能监控**：关键指标监控
- **日志管理**：集中式日志
- **告警系统**：异常告警

## 8. 集成架构

### 8.1 三层集成策略

Memory Classification Engine 采用三层集成架构，最大化用户触达：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        集成架构 (Integration Architecture)              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 3: Framework Adapters (框架适配层)                        │   │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│  │ │LangChain │ │  CrewAI  │ │ AutoGen  │ │  其他    │            │   │
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▲                                         │
│  ┌───────────────────────────┴─────────────────────────────────────┐   │
│  │ Layer 2: MCP Server (MCP 服务层) ✅ 已完成                     │   │
│  │ ┌─────────────────────────────────────────────────────────┐    │   │
│  │ │  MCP Server (JSON-RPC over stdio)                       │    │   │
│  │ │  • classify_memory  • retrieve_memories                 │    │   │
│  │ │  • store_memory     • get_memory_stats                  │    │   │
│  │ │  • batch_classify   • find_similar                      │    │   │
│  │ │  • export_memories  • import_memories                   │    │   │
│  │ └─────────────────────────────────────────────────────────┘    │   │
│  │                              ▲                                 │   │
│  │  ┌───────────────────────────┼─────────────────────────────┐   │   │
│  │  │ Claude Code │ Cursor │ OpenClaw │ 其他 MCP 客户端      │   │   │
│  │  └───────────────────────────┴─────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▲                                         │
│  ┌───────────────────────────┴─────────────────────────────────────┐   │
│  │ Layer 1: Python SDK (Python SDK 层) ✅ 已完成                    │   │
│  │ ┌─────────────────────────────────────────────────────────┐    │   │
│  │ │  MemoryClassificationEngine (Python Library)            │    │   │
│  │ │  • pip install memory-classification-engine             │    │   │
│  │ └─────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 MCP Server 架构设计

#### 8.2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server 架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    MCP 客户端                            │   │
│  │         (Claude Code / Cursor / OpenClaw)               │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │ JSON-RPC over stdio             │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │                 MCP Server 核心                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │   Server    │  │   Tools     │  │   Config    │      │   │
│  │  │   主入口    │  │   工具定义  │  │   配置管理  │      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │              Memory Classification Engine                │   │
│  │         (通过 Python SDK 调用核心功能)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 8.2.2 MCP Tools 设计

| Tool 名称 | 功能描述 | 输入参数 | 返回值 |
|-----------|----------|----------|--------|
| `classify_memory` | 分析消息并判断是否需要记忆 | `message`: 用户消息<br>`context`: 对话上下文 | `matched`: 是否匹配<br>`memory_type`: 记忆类型<br>`confidence`: 置信度 |
| `store_memory` | 存储记忆到合适的层级 | `content`: 记忆内容<br>`memory_type`: 类型<br>`tier`: 层级 | `memory_id`: 记忆ID<br>`stored`: 是否成功 |
| `retrieve_memories` | 检索相关记忆 | `query`: 查询内容<br>`limit`: 结果数量 | `memories`: 记忆列表 |
| `get_memory_stats` | 获取记忆统计信息 | `tier`: 指定层级(可选) | `stats`: 统计信息 |
| `batch_classify` | 批量分类消息 | `messages`: 消息列表 | `results`: 分类结果列表 |
| `find_similar` | 查找相似记忆 | `content`: 内容<br>`threshold`: 相似度阈值 | `similar_memories`: 相似记忆 |
| `export_memories` | 导出记忆 | `format`: 导出格式<br>`tier`: 指定层级 | `data`: 导出数据 |
| `import_memories` | 导入记忆 | `data`: 导入数据<br>`format`: 数据格式 | `imported_count`: 导入数量 |

#### 8.2.3 MCP Server 配置

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

### 8.3 OpenClaw 集成设计

#### 8.3.1 OpenClaw 简介

OpenClaw 是一个开源的 AI 工具集成平台，类似于 Claude Code，支持通过配置文件定义工具和集成。

#### 8.3.2 集成架构

```
┌─────────────────────────────────────────────────────────────────┐
│                   OpenClaw 集成架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   OpenClaw 客户端                        │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │              OpenClaw 配置文件 (.clawrc)                 │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  tools:                                         │    │   │
│  │  │    - name: classify_memory                      │    │   │
│  │  │      command: mce-openclaw classify             │    │   │
│  │  │    - name: store_memory                         │    │   │
│  │  │      command: mce-openclaw store                │    │   │
│  │  │    - name: retrieve_memories                    │    │   │
│  │  │      command: mce-openclaw retrieve             │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │              OpenClaw 适配器 (CLI)                       │   │
│  │         封装 MCP Server 为命令行工具                     │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │              Memory Classification Engine                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 8.3.3 OpenClaw 工具配置示例

```yaml
# .clawrc
version: "1.0"

tools:
  - name: classify_memory
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

  - name: store_memory
    description: 存储记忆到合适的层级
    command: mce-openclaw store
    args:
      - name: content
        type: string
        required: true
        description: 记忆内容
      - name: memory_type
        type: string
        required: true
        description: 记忆类型
      - name: tier
        type: integer
        required: false
        description: 记忆层级

  - name: retrieve_memories
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
        description: 返回结果数量
```

### 8.4 Framework Adapters 架构

#### 8.4.1 LangChain 适配器

```python
# adapters/langchain.py
from langchain.tools import BaseTool
from memory_classification_engine import MemoryClassificationEngine

class MemoryClassifierTool(BaseTool):
    """LangChain Tool for memory classification"""
    
    name = "memory_classifier"
    description = "Classify and store user memories"
    
    def __init__(self, config_path: str = None):
        self.engine = MemoryClassificationEngine(config_path)
    
    def _run(self, message: str) -> dict:
        """Run the tool"""
        return self.engine.process_message(message)
```

#### 8.4.2 CrewAI 适配器

```python
# adapters/crewai.py
from crewai.tools import BaseTool
from memory_classification_engine import MemoryClassificationEngine

class MemoryTool(BaseTool):
    """CrewAI Tool for memory management"""
    
    name = "memory_tool"
    description = "Manage user memories"
    
    def __init__(self, config_path: str = None):
        self.engine = MemoryClassificationEngine(config_path)
```

#### 8.4.3 AutoGen 适配器

```python
# adapters/autogen.py
from autogen import ConversableAgent
from memory_classification_engine import MemoryClassificationEngine

class MemoryAgent(ConversableAgent):
    """AutoGen Agent with memory capabilities"""
    
    def __init__(self, config_path: str = None, **kwargs):
        super().__init__(**kwargs)
        self.engine = MemoryClassificationEngine(config_path)
```

### 8.5 集成对比

| 集成方式 | 复杂度 | 用户群体 | 优先级 | 时间投入 |
|----------|--------|----------|--------|----------|
| Python SDK | 低 | Python 开发者 | 已完成 | - |
| MCP Server | 中 | Claude/Cursor/OpenClaw 用户 | ⭐ 高 | 2-3周 |
| OpenClaw | 低 | OpenClaw 用户 | 高 | 1周 |
| LangChain | 中 | LangChain 用户 | 中 | 2周 |
| CrewAI | 中 | CrewAI 用户 | 中 | 2周 |
| AutoGen | 中 | AutoGen 用户 | 低 | 2周 |

## 9. 未来规划

### 9.1 功能扩展

- **多语言支持**：支持更多语言
- **AI增强**：集成AI模型
- **知识图谱**：构建记忆知识图谱
- **推荐系统**：智能记忆推荐

### 9.2 技术升级

- **分布式存储**：支持分布式部署
- **实时处理**：流处理能力
- **边缘计算**：边缘设备支持
- **量子计算**：量子算法优化

### 9.3 生态建设

- **插件市场**：插件生态系统
- **社区贡献**：开源社区建设
- **标准制定**：行业标准参与
- **教育资源**：学习和培训资源
