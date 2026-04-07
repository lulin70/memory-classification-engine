# Memory Classification Engine

> A lightweight Agent-side memory classification engine that real-time judges which content in conversations is worth remembering, in what form to store it, and which memory tier to store it in.

## Project Background

Current AI Agent memory management has a core problem: **What content is worth remembering?**

Most existing solutions adopt a "full summary" strategy, which summarizes the entire conversation after it ends. This leads to:
- Memory libraries filled with low-value noise, resulting in extremely low signal-to-noise ratio during retrieval
- Inability to distinguish between different types of information (preferences, facts, decisions, relationships)
- Forgetting and update mechanisms cannot be built on unclassified memory

The problem this project aims to solve is: **Implement a lightweight memory classification engine on the Agent side that real-time judges which content in conversations is worth remembering, in what form to store it, and which memory tier to store it in.**

## Core Features

### 1. Memory Classification
- **User Preference** (`user_preference`): User's explicitly expressed preferences, habits, and style requirements
- **Correction Signal** (`correction`): User's correction of AI's judgment or output
- **Fact Declaration** (`fact_declaration`): User's statements about themselves or business facts
- **Decision Record** (`decision`): Clear conclusions or choices reached in the conversation
- **Relationship Information** (`relationship`): Information about relationships between people, teams, and organizations
- **Task Pattern** (`task_pattern`): Repeated task types and their processing methods
- **Sentiment Marker** (`sentiment_marker`): User's explicit emotional tendency towards a topic

### 2. Memory Tiers
- **Tier 1 - Working Memory**: Current conversation context window, natively managed by LLM
- **Tier 2 - Procedural Memory**: User preferences, behavior rules, work habits, loaded as system prompts or configuration files
- **Tier 3 - Episodic Memory**: Decision records, task patterns, important conversation summaries, stored in vector database
- **Tier 4 - Semantic Memory**: Fact declarations, relationship information, domain knowledge, stored in knowledge graph or relational database

### 3. Three-Layer Judgment Pipeline
- **Layer 1: Rule Matching Layer**: Based on regular expressions and keyword matching, zero cost, high accuracy
- **Layer 2: Structure Analysis Layer**: Analyzes conversation interaction patterns, lightweight, does not rely on semantic understanding
- **Layer 3: Semantic Inference Layer**: Calls LLM for semantic analysis, high cost, high coverage

### 4. Memory Management
- **Write Process**: Deduplication check → Conflict handling → Write to corresponding tier storage
- **Intelligent Conflict Handling**: Automatically detects memory conflicts, resolves conflicts based on timestamp, confidence, and source priority, supports user intervention
- **Memory Weight Calculation**: Calculates memory weight based on multi-dimensional factors (confidence, timeliness, source reliability)
- **Forgetting Mechanism**: Weighted decay based on time, frequency, and importance
- **Retrieval Strategy**: Retrieves relevant memories from different tiers based on conversation content
- **Injection Format**: Structured memory injection into system prompts
- **Responsibility Boundary**: The classification engine can be used as an independent classification component or provide a complete memory read-write link, and access parties can choose the usage method according to their needs

## Technical Architecture

```
Conversation Content
  │
  ▼
┌─────────────────────┐
│ Layer 1: Rule Matching Layer  │  ← Deterministic rules, zero cost, high accuracy
└─────────┬───────────┘
          │ Unmatched content
          ▼
┌─────────────────────┐
│ Layer 2: Structure Analysis Layer  │  ← Conversation structure pattern recognition, lightweight
└─────────┬───────────┘
          │ Unmatched content
          ▼
┌─────────────────────┐
│ Layer 3: Semantic Inference Layer  │  ← LLM judgment, high cost, high coverage
└─────────┬───────────┘
          │
          ▼
   Memory Write Decision
          │
          ▼
┌─────────────────────┐
│  Deduplication and Conflict Detection    │
└─────────┬───────────┘
          │
          ├── Duplicate → Update existing memory
          │
          ├── Conflict → Intelligent Conflict Handling
          │       ├── Detect conflict type
          │       ├── Calculate memory weight
          │       ├── Mark conflict status
          │       └── Support user intervention
          │
          └── New memory → Write to corresponding Tier
                          │
                          ├── Tier 2 → Configuration files/System prompts
                          ├── Tier 3 → Vector database
                          └── Tier 4 → Knowledge graph
```

## Technology Selection

| Component | Recommended Solution | Alternative Solution |
|-----------|----------------------|----------------------|
| Rule Engine | YAML configuration + Regular expressions | JSON Schema |
| Conversation State Tracking | In-memory state machine | Redis |
| Vector Database (Tier 3) | ChromaDB (lightweight local) | Qdrant, Milvus |
| Knowledge Graph (Tier 4) | Neo4j | NetworkX (lightweight, suitable for start-up) |
| Configuration Storage (Tier 2) | YAML/JSON files | SQLite |
| Semantic Classification (Layer 3) | Small model API call | Local small model (Ollama) |
| Agent Framework Adaptation | Designed as an independent module, providing SDK | Extensible interface |

## Project Milestones

### Phase 1: Minimum Viable Product (MVP)
- Implement Layer 1 rule matching layer
- Implement Tier 2 procedural memory read/write
- Use ClaudeCode's CLAUDE.md format as the initial storage format
- Provide 3-5 default rules

### Phase 2: Structure Analysis
- Implement Layer 2 structure analysis layer
- Implement duplicate detection and pattern recognition
- Implement Tier 3 vector database storage and retrieval
- Implement deduplication and conflict detection

### Phase 3: Semantic Inference
- Implement Layer 3 semantic inference layer
- Design and optimize classification prompts
- Implement cost control mechanism

### Phase 4: Forgetting and Evolution
- Implement decay-based forgetting mechanism
- Implement memory compression (details → patterns)
- Implement intelligent conflict handling mechanism
- Implement memory weight calculation
- Implement user memory review interface (CLI)

### Phase 5: Ecosystem Expansion
- Support multiple Agent frameworks (priority adaptation to ClaudeCode, WorkBuddy, Cursor, etc.)
- Implement enterprise-level multi-user memory sharing and permission management
- Open memory import/export format standards

## Comparison with Mainstream AI Memory Systems

| Dimension | Mem0 | MemGPT | LangChain Memory | ClaudeCode | This Project (Memory Classification Engine) |
|-----------|------|--------|------------------|-----------|-------------------------------------------|
| Memory Classification | Yes (basic) | No | No (implicit) | No (by file hierarchy) | Yes (7 types, 3-layer judgment pipeline) |
| Write Judgment | Full extraction after each conversation | Based on context window management | Manual/Hooks | Manual/Hooks | Event-driven, real-time classification |
| Memory Tiers | Single layer (vector database) | Two layers (memory + hard disk) | Single layer (session) | Single layer (file) | Four layers (working/procedural/episodic/semantic) |
| Forgetting Mechanism | No | Yes (context elimination)<br><small>Note: Passive elimination, only triggered when context is full</small> | No | No | Yes (weighted decay + semantic compression)<br><small>Note: Active forgetting based on time, frequency, and importance</small> |
| Storage Method | Vector database | Virtual memory abstraction | Memory/file | File system | Multiple storage backends (file + vector + graph) |
| Agent Independence | Yes (SDK) | No (own Agent) | Yes (framework component) | No (own Agent) | Yes (independent module + SDK) |
| LLM Integration | Support | Own model | Framework integration | Own model | Flexible adaptation to multiple LLMs |
| Enterprise Features | Basic | None | Basic | None | Planned support for multi-user sharing and permission management |
| Lightweight Design | Medium | Heavy | Light | Light | Light (prioritizes local storage) |
| Learning Ability | Basic | None | None | None | Supports extracting procedural memory from episodic memory<br><small>Note: Repeated patterns automatically promote to rules, implementing memory evolution</small> |

## Quick Start

### Installation

```bash
# Clone the project
git clone https://github.com/lulin70/memory-classification-engine.git
cd memory-classification-engine

# Install dependencies
pip install -r requirements.txt
```

### Neo4j Configuration (Optional)

If you want to use Neo4j as the knowledge graph storage backend, you need to:

1. **Install Neo4j**:
   - Download and install Neo4j Desktop or Neo4j Community Server from [Neo4j website](https://neo4j.com/download/)
   - Or run Neo4j using Docker:
     ```bash
     docker run --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
     ```

2. **Start Neo4j**:
   - Start the Neo4j service
   - Access `http://localhost:7474` in your browser, log in with the default username `neo4j` and password `password`
   - You need to change the password when logging in for the first time, ensure it matches the configuration in `config/config.yaml`

3. **Verify Connection**:
   - Ensure the Neo4j service is running
   - Ensure the Neo4j configuration in `config/config.yaml` is correct

4. **Failover**:
   - If Neo4j is unavailable, the system will automatically fall back to in-memory storage to ensure normal operation

### Configuration

#### Environment Variables

For secure management of API keys, it is recommended to use environment variables:

```bash
# Set GLM API Key
export MCE_LLM_API_KEY="your_glm_api_key"

# Enable LLM functionality
export MCE_LLM_ENABLED=true

# Optional: Set configuration file path
export MCE_CONFIG_PATH="./config/config.yaml"
```

#### Configuration File

Edit the `config/config.yaml` file:

```yaml
# LLM settings (optional)
llm:
  enabled: false  # Defaults to false, set to true to enable
  api_key: ""  # Recommended to set via environment variable, not directly in this file
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

### Basic Usage

```python
from memory_classification_engine import MemoryClassificationEngine

# Initialize the engine
engine = MemoryClassificationEngine()

# Process user message
user_message = "Remember, I don't like using dashes in code"
result = engine.process_message(user_message)
print(result)
# Output: {"matched": true, "memory_type": "user_preference", "tier": 2, "content": "don't like using dashes in code", "confidence": 1.0, "source": "rule:0"}

# Retrieve memories
memories = engine.retrieve_memories("code style")
print(memories)
```

### SDK Usage

```python
from memory_classification_engine.sdk.python import MemoryClient

# Create a client
client = MemoryClient()

# Remember a message
result = client.remember("I prefer using spaces over tabs")
print(result)

# Recall memories
memories = client.recall("coding preferences")
print(memories)
```

## Project Structure

```
memory-classification-engine/
├── src/
│   ├── memory_classification_engine/
│   │   ├── __init__.py
│   │   ├── engine.py          # Core engine
│   │   ├── layers/
│   │   │   ├── rule_matcher.py    # Rule matching layer
│   │   │   ├── pattern_analyzer.py # Structure analysis layer
│   │   │   └── semantic_classifier.py # Semantic inference layer
│   │   ├── storage/
│   │   │   ├── tier2.py              # Procedural memory storage
│   │   │   ├── tier3.py              # Episodic memory storage
│   │   │   ├── tier4.py              # Semantic memory storage
│   │   │   └── neo4j_knowledge_graph.py  # Neo4j knowledge graph storage adapter
│   │   ├── utils/
│   │   │   ├── config.py       # Configuration management
│   │   │   └── helpers.py      # Helper functions
│   │   ├── api/
│   │   │   ├── server.py       # API server
│   │   │   └── client.py       # API client
│   │   └── sdk/
│   │       └── python.py       # Python SDK
├── config/
│   └── rules.yaml              # Rules configuration file
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

## Contribution Guidelines

We welcome contributions in various forms, including but not limited to:

- Reporting bugs and suggesting features
- Submitting code improvements and fixes
- Improving documentation
- Participating in discussions and providing suggestions

Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed contribution process.

## License

This project uses [MIT License](LICENSE).

## Open Issues

1. **Memory conflict resolution strategy**: When new memory conflicts with old memory, should it overwrite or coexist? Is user confirmation needed?
   - **Solution**: Implement conflict resolution mechanism based on timestamp and confidence. When new memory conflicts with old memory, the system will: 1) Mark conflicting memories; 2) Compare timestamps, default to newer memory; 3) Provide user intervention mechanism, allowing users to choose which memory to keep; 4) Record conflict history for subsequent analysis.

2. **Cross-language memory consistency**: When the same preference is expressed in Chinese and English, how to identify it as the same memory?
   - **Solution**: Adopt semantic-based memory representation, mapping the same concept in different languages to the same semantic representation. Initial implementation can: 1) Prioritize support for English and Chinese; 2) Use translation API for cross-language mapping; 3) Establish language-independent memory identifiers to ensure the same concept is recognized as the same memory in different languages.

3. **Memory privacy boundaries**: In multi-Agent collaboration scenarios, which memories can be shared and which must be isolated?
   - **Solution**: Implement multi-level privacy protection measures, including: 1) Data encryption: Encrypt sensitive memory information; 2) Access control: Role-based access permission management; 3) Data minimization: Only store necessary memory information; 4) Forgetting mechanism: Support users to actively delete memories; 5) Audit logs: Record all memory access and modification operations.

4. **Memory quality evaluation indicators**: How to measure how much a memory system "remembers correctly and incorrectly"?
   - **Solution**: Establish multi-dimensional evaluation indicators, including: 1) Memory classification accuracy: Test classification accuracy through manually annotated samples; 2) Retrieval relevance: Evaluate the relevance of retrieval results to the current task; 3) System performance: Monitor response time and resource usage; 4) User satisfaction: Evaluate system effectiveness through user feedback.

5. **Possibility of LLM-side memory**: When is KV Cache persistence technically feasible? When will the cost of fine-tuning personal memory models decrease to an acceptable range?
   - **Solution**: Adopt layered storage strategy, storing memories of different importance in different tiers. Procedural memory and semantic memory prioritize completeness, while episodic memory decays based on access frequency and time. Also implement memory compression mechanism, patternizing frequently accessed memories to reduce storage usage.

## Performance Optimization

### Optimization Results

Through comprehensive performance optimization, the Memory Classification Engine has achieved significant performance improvements:

1. **Processing Performance**: Average processing time reduced from 0.0245 seconds to 0.0104 seconds, with approximately 58% performance improvement
2. **Retrieval Performance**: Average retrieval time is 0.0146 seconds, far below the 50ms target
3. **Concurrent Performance**: Message processing throughput reached 626.33 messages/second
4. **Storage Optimization**: Memory compression rate reached 87-90%, significantly reducing storage overhead
5. **System Stability**: Eliminated concurrent modification errors, significantly improving system stability
6. **Monitoring Capabilities**: Added real-time performance monitoring and alerting functionality
7. **Test Coverage**: Written comprehensive performance test scripts to verify all optimization effects

### Optimization Measures

1. **Core Engine Optimization**:
   - Optimized processing logic, reducing unnecessary calculations and I/O operations
   - Improved multi-threaded processing, enhancing concurrent performance
   - Implemented batch storage and processing, reducing database operation frequency

2. **Storage Layer Optimization**:
   - Optimized database connection pool configuration, increasing maximum connections to 10
   - Implemented batch storage operations, reducing database I/O frequency
   - Implemented intelligent memory compression functionality, automatically compressing content based on memory age
   - Optimized SQLite configuration, improving database performance

3. **Memory Management**:
   - Implemented memory compression and expiration mechanisms, reducing storage overhead
   - Optimized caching strategy, improving cache hit rate
   - Fixed concurrent modification errors in memory association manager

4. **Performance Monitoring**:
   - Added real-time performance monitoring system, including memory, CPU, and disk usage
   - Implemented performance alerting functionality, sending alerts when metrics exceed thresholds
   - Provided detailed performance analysis reports

5. **Testing and Validation**:
   - Written comprehensive performance test scripts to verify all optimization effects
   - Conducted load testing and stability testing
   - Verified system performance in high-concurrency scenarios

## Contact

- Project homepage: https://github.com/lulin70/memory-classification-engine
- Issue feedback: https://github.com/lulin70/memory-classification-engine/issues
- Discussion community: https://github.com/lulin70/memory-classification-engine/discussions