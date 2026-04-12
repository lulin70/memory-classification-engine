# Architecture Design

## 1. System Architecture

Memory Classification Engine adopts a layered architecture design, mainly including the following layers:

### 1.1 Core Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       Application Layer                        │
├──────────────────────────────────────────────────────────────────┤
│                     Engine Layer                               │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│ │  Rule Matcher   │  │ Pattern Analyzer │  │ Semantic Classifier │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├──────────────────────────────────────────────────────────────────┤
│                     Storage Layer                              │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│ │   Tier 1 (WM)   │  │   Tier 2 (PM)   │  │   Tier 3 (EM)   │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│ ┌───────────────────────────────────────────────────────────┐ │
│ │                     Tier 4 (SM)                         │ │
│ └───────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────┤
│                     Utilities Layer                         │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│ │    Helpers     │  │    Logger      │  │   Exceptions    │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Plugin Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Plugin Manager                            │
├──────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│ │  Built-in Plugins│  │  External Plugins│  │  Custom Plugins │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## 2. Core Components

### 2.1 Engine Layer

#### 2.1.1 MemoryClassificationEngine
- **Function**: Core engine, coordinates the work of various components
- **Responsibilities**:
  - Process user messages
  - Call classification layer for memory classification
  - Manage memory storage
  - Coordinate plugin execution
  - Provide API interfaces

#### 2.1.2 Classification Layer

| Component | Function | Implementation |
|-----------|----------|----------------|
| Rule Matcher | Rule-based matching | Regular expressions, keyword matching |
| Pattern Analyzer | Pattern analysis | Pattern recognition, sequence analysis |
| Semantic Classifier | Semantic classification | Text analysis, similarity calculation |

### 2.2 Storage Layer

#### 2.2.1 Storage Tiers

| Tier | Name | Storage Method | Features |
|------|------|---------------|----------|
| Tier 1 | Working Memory | In-memory | Temporary storage, fast access |
| Tier 2 | Procedural Memory | JSON files | Structured storage, user preferences |
| Tier 3 | Episodic Memory | SQLite + FTS5 + Vector storage | Large capacity storage, full-text search, vector retrieval |
| Tier 4 | Semantic Memory | SQLite + Knowledge Graph | Long-term storage, semantic associations, knowledge reasoning |

#### 2.2.2 Storage Implementation

- **Tier 1**: Using Python in-memory dictionary
- **Tier 2**: Using JSON file storage
- **Tier 3**: Using SQLite+FTS5+vector storage (FAISS/TF-IDF)
- **Tier 4**: Using SQLite+knowledge graph (NetworkX)

### 2.3 Utilities Layer

| Component | Function | Implementation |
|-----------|----------|----------------|
| Helpers | Utility functions | Common utility methods |
| Logger | Logging system | Hierarchical log recording |
| Exceptions | Exception handling | Unified exception system |
| Cache | Caching system | LRU cache implementation |

### 2.4 Plugin System

#### 2.4.1 PluginManager
- **Function**: Manages plugin loading, execution, and lifecycle
- **Responsibilities**:
  - Discover and load plugins
  - Manage plugin status
  - Coordinate plugin execution
  - Handle plugin exceptions

#### 2.4.2 Plugin Base Class
- **Function**: Defines plugin interface
- **Methods**:
  - initialize(): Initialize plugin
  - process_message(): Process message
  - process_memory(): Process memory
  - cleanup(): Clean up resources

## 3. Technical Implementation

### 3.1 Core Technology Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Main development language | 3.9+ |
| SQLite | Data storage | 3.35+ |
| FTS5 | Full-text search | Built-in |
| FAISS | Vector storage and retrieval | 1.7.4+ |
| scikit-learn | Text vectorization | 1.3.0+ |
| JSON | Configuration and data storage | Standard library |
| Pytest | Testing framework | 7.0+ |

### 3.2 Key Module Implementation

#### 3.2.1 Storage Module

**BaseStorage**: Abstract base class, defines storage interface
- Methods: store_memory(), retrieve_memories(), update_memory(), delete_memory()
- Helper methods: _prepare_memory(), _handle_error()

**Tier3StorageFTS**: FTS5 storage implementation
- Features: Full-text search, index synchronization, cache support
- Performance: Search speed improved by 2-3 times

#### 3.2.2 Cache Module

**LRUCache**: LRU algorithm-based cache
- Features: Size limit, TTL expiration, thread-safe
- Performance: O(1) access time

**MemoryCache**: Memory cache manager
- Features: Preheating mechanism, statistics, invalidation mechanism
- Performance: Cache hit rate > 80%

#### 3.2.3 Plugin Module

**PluginManager**: Plugin manager
- Features: Auto-discovery, dynamic loading, error isolation
- Performance: Plugin loading time < 100ms

**SentimentAnalyzerPlugin**: Sentiment analysis plugin
- Features: Simple sentiment analysis, memory enhancement
- Performance: Analysis time < 50ms

### 3.3 Data Flow

#### 3.3.1 Message Processing Flow

1. **Input**: User message
2. **Classification**: Analysis through three-layer classifier
3. **Storage**: Store to corresponding tier based on classification result
4. **Plugin Processing**: Additional processing through plugins
5. **Return**: Processing result

#### 3.3.2 Search Flow

1. **Input**: Search keywords
2. **Preprocessing**: Keyword analysis, query optimization
3. **Search**:
   - English: FTS5 full-text search + vector search
   - Chinese: LIKE query + vector search
4. **Sorting**: Sort by relevance and confidence
5. **Return**: Search results

## 4. Performance Optimization

### 4.1 Storage Optimization

- **Indexing**: Create indexes for common queries
- **Caching**: Hot data caching
- **Batch Operations**: Reduce database access times
- **Connection Pool**: Reuse database connections

### 4.2 Search Optimization

- **FTS5**: Use full-text search index
- **Query Optimization**: Preprocess query statements
- **Result Caching**: Cache search results
- **Asynchronous Processing**: Asynchronous execution for complex queries

### 4.3 Memory Optimization

- **Memory Limit**: Set reasonable memory usage limits
- **Garbage Collection**: Timely cleanup of unused objects
- **Data Compression**: Compress stored data
- **Lazy Loading**: On-demand data loading

## 5. Extensibility Design

### 5.1 Plugin System

- **Hot Plug**: Support runtime plugin loading
- **Isolation**: Plugins run in isolated environment
- **API**: Unified plugin API
- **Management**: Plugin lifecycle management

### 5.2 Storage Extension

- **Abstract Interface**: Unified storage interface
- **Adapters**: Support different storage backends
- **Tiering**: Extensible storage tiers
- **Migration**: Data migration tools

### 5.3 API Extension

- **REST API**: HTTP interface
- **SDK**: Multi-language SDK
- **WebSocket**: Real-time communication
- **Event System**: Event-driven architecture

## 6. Security Design

### 6.1 Data Security

- **Encryption**: Encrypted storage of sensitive data
- **Backup**: Regular data backup
- **Recovery**: Disaster recovery mechanism
- **Audit**: Operation audit logs

### 6.2 Access Control

- **Authentication**: User authentication mechanism
- **Authorization**: Role-based access control
- **Rate Limiting**: API access rate limiting
- **Injection Protection**: SQL injection prevention

### 6.3 Security Audit

- **Logging**: Security-related logs
- **Monitoring**: Abnormal behavior monitoring
- **Scanning**: Regular security scanning
- **Updates**: Timely dependency updates

## 7. Deployment and Integration

### 7.1 Deployment Methods

- **Local Deployment**: Single machine deployment
- **Containerization**: Docker containers
- **Cloud Deployment**: Cloud service deployment
- **Edge Deployment**: Edge device deployment

### 7.2 Integration Methods

- **API Integration**: REST API
- **SDK Integration**: Multi-language SDK
- **Plugin Integration**: Third-party plugins
- **Service Integration**: Microservice integration

### 7.3 Monitoring and Maintenance

- **Health Check**: System health status
- **Performance Monitoring**: Key metric monitoring
- **Log Management**: Centralized logging
- **Alert System**: Anomaly alerts

## 8. Integration Architecture

### 8.1 Three-layer Integration Strategy

Memory Classification Engine adopts a three-layer integration architecture to maximize user reach:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Integration Architecture                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 3: Framework Adapters (Framework Adaptation Layer)       │   │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│  │ │LangChain │ │  CrewAI  │ │ AutoGen  │ │  Others  │            │   │
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▲                                         │
│  ┌───────────────────────────┴─────────────────────────────────────┐   │
│  │ Layer 2: MCP Server (MCP Service Layer) ✅ Completed          │   │
│  │ ┌─────────────────────────────────────────────────────────┐    │   │
│  │ │  MCP Server (JSON-RPC over stdio)                       │    │   │
│  │ │  • classify_memory  • retrieve_memories                 │    │   │
│  │ │  • store_memory     • get_memory_stats                  │    │   │
│  │ │  • batch_classify   • find_similar                      │    │   │
│  │ │  • export_memories  • import_memories                   │    │   │
│  │ └─────────────────────────────────────────────────────────┘    │   │
│  │                              ▲                                 │   │
│  │  ┌───────────────────────────┼─────────────────────────────┐   │   │
│  │  │ Claude Code │ Cursor │ OpenClaw │ Other MCP Clients     │   │   │
│  │  └───────────────────────────┴─────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▲                                         │
│  ┌───────────────────────────┴─────────────────────────────────────┐   │
│  │ Layer 1: Python SDK (Python SDK Layer) ✅ Completed             │   │
│  │ ┌─────────────────────────────────────────────────────────┐    │   │
│  │ │  MemoryClassificationEngine (Python Library)            │    │   │
│  │ │  • pip install memory-classification-engine             │    │   │
│  │ └─────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 MCP Server Architecture Design

#### 8.2.1 Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    MCP Client                            │   │
│  │         (Claude Code / Cursor / OpenClaw)               │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │ JSON-RPC over stdio             │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │                 MCP Server Core                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │   Server    │  │   Tools     │  │   Config    │      │   │
│  │  │   Main Entry│  │   Tool Defs │  │   Config Mgmt│      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │              Memory Classification Engine                │   │
│  │         (Core functionality via Python SDK)             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 8.2.2 MCP Tools Design

| Tool Name | Description | Input Parameters | Return Value |
|-----------|-------------|------------------|--------------|
| `classify_memory` | Analyze message and determine if memory is needed | `message`: User message<br>`context`: Dialogue context | `matched`: Whether matched<br>`memory_type`: Memory type<br>`confidence`: Confidence |
| `store_memory` | Store memory to appropriate tier | `content`: Memory content<br>`memory_type`: Type<br>`tier`: Tier | `memory_id`: Memory ID<br>`stored`: Whether successful |
| `retrieve_memories` | Retrieve relevant memories | `query`: Query content<br>`limit`: Result count | `memories`: Memory list |
| `get_memory_stats` | Get memory statistics | `tier`: Specified tier (optional) | `stats`: Statistics |
| `batch_classify` | Batch classify messages | `messages`: Message list | `results`: Classification result list |
| `find_similar` | Find similar memories | `content`: Content<br>`threshold`: Similarity threshold | `similar_memories`: Similar memories |
| `export_memories` | Export memories | `format`: Export format<br>`tier`: Specified tier | `data`: Exported data |
| `import_memories` | Import memories | `data`: Import data<br>`format`: Data format | `imported_count`: Import count |

#### 8.2.3 MCP Server Configuration

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

### 8.3 OpenClaw Integration Design

#### 8.3.1 OpenClaw Introduction

OpenClaw is an open-source AI tool integration platform, similar to Claude Code, supporting tool definition and integration through configuration files.

#### 8.3.2 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   OpenClaw Integration Architecture             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   OpenClaw Client                        │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │              OpenClaw Configuration (.clawrc)            │   │
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
│  │              OpenClaw Adapter (CLI)                       │   │
│  │         Wraps MCP Server as command-line tool            │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │              Memory Classification Engine                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 8.3.3 OpenClaw Tool Configuration Example

```yaml
# .clawrc
version: "1.0"

tools:
  - name: classify_memory
    description: Analyze message and determine if memory is needed
    command: mce-openclaw classify
    args:
      - name: message
        type: string
        required: true
        description: User message content
      - name: context
        type: string
        required: false
        description: Dialogue context

  - name: store_memory
    description: Store memory to appropriate tier
    command: mce-openclaw store
    args:
      - name: content
        type: string
        required: true
        description: Memory content
      - name: memory_type
        type: string
        required: true
        description: Memory type
      - name: tier
        type: integer
        required: false
        description: Memory tier

  - name: retrieve_memories
    description: Retrieve relevant memories
    command: mce-openclaw retrieve
    args:
      - name: query
        type: string
        required: true
        description: Query content
      - name: limit
        type: integer
        required: false
        default: 5
        description: Number of results
```

### 8.4 Framework Adapters Architecture

#### 8.4.1 LangChain Adapter

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

#### 8.4.2 CrewAI Adapter

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

#### 8.4.3 AutoGen Adapter

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

### 8.5 Integration Comparison

| Integration Method | Complexity | User Group | Priority | Time Investment |
|--------------------|------------|------------|----------|------------------|
| Python SDK | Low | Python developers | Completed | - |
| MCP Server | Medium | Claude/Cursor/OpenClaw users | ⭐ High | 2-3 weeks |
| OpenClaw | Low | OpenClaw users | High | 1 week |
| LangChain | Medium | LangChain users | Medium | 2 weeks |
| CrewAI | Medium | CrewAI users | Medium | 2 weeks |
| AutoGen | Medium | AutoGen users | Low | 2 weeks |

## 9. Future Planning

### 9.1 Feature Expansion

- **Multi-language Support**: Support more languages
- **AI Enhancement**: Integrate AI models
- **Knowledge Graph**: Build memory knowledge graph
- **Recommendation System**: Intelligent memory recommendation

### 9.2 Technical Upgrade

- **Distributed Storage**: Support distributed deployment
- **Real-time Processing**: Stream processing capabilities
- **Edge Computing**: Edge device support
- **Quantum Computing**: Quantum algorithm optimization

### 9.3 Ecosystem Building

- **Plugin Marketplace**: Plugin ecosystem
- **Community Contribution**: Open source community building
- **Standard Setting**: Industry standard participation
- **Educational Resources**: Learning and training resources
