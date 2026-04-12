# Memory Classification Engine - Detailed Design Document

## 1. System Architecture Design

### 1.1 Overall Architecture

The Memory Classification Engine adopts a modular, layered architecture design, consisting of the following components:

```
┌─────────────────────┐
│     External Systems│
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│    API/SDK Interface│
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
│  Advanced Wrapper  │
│ ┌─────────────────┐ │
│ │ MemoryOrchestrator││
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   Core Engine      │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  Multi-layered      │
│  Judgment Pipeline  │
│ ┌─────────────────┐ │
│ │ Rule Matching   │ │
│ ├─────────────────┤ │
│ │ Pattern Analysis │ │
│ ├─────────────────┤ │
│ │ Semantic Inference││
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  Memory Management  │
│ ┌─────────────────┐ │
│ │ Deduplication   │ │
│ ├─────────────────┤ │
│ │ Forgetting      │ │
│ ├─────────────────┤ │
│ │ Nudge Mechanism │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  Memory Quality    │
│  Assessment        │
│ ┌─────────────────┐ │
│ │ Usage Tracking  │ │
│ ├─────────────────┤ │
│ │ Feedback Analysis││
│ ├─────────────────┤ │
│ │ Quality Calculation││
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  Memory Migration  │
│  System           │
│ ┌─────────────────┐ │
│ │ Data Export     │ │
│ ├─────────────────┤ │
│ │ Data Import     │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  Storage Layer     │
│ ┌─────────────────┐ │
│ │ Working Memory  │ │
│ ├─────────────────┤ │
│ │ Procedural Memory││
│ ├─────────────────┤ │
│ │ Episodic Memory │ │
│ ├─────────────────┤ │
│ │ Semantic Memory │ │
│ └─────────────────┘ │
└─────────────────────┘
```

### 1.2 Core Component Description

1. **API/SDK Interface**: Provides interaction interfaces between external systems and the Memory Classification Engine, supporting Python SDK, REST API, and MCP Server.
   - **Python SDK**: Core programming interface providing full functionality access.
   - **REST API**: HTTP-based interface supporting cross-language integration.
   - **MCP Server**: Implements MCP protocol, supporting integration with tools like Claude Code and Cursor.

2. **Advanced Wrapper Layer**:
   - **MemoryOrchestrator**: One-stop memory management solution, providing a unified high-level interface that integrates classification, storage, retrieval, forgetting, quality assessment, and migration functions.

3. **Core Engine**: Coordinates the work of various modules, handles external requests, and is the hub of the entire system.

4. **Multi-layered Judgment Pipeline**:
   - **Rule Matching Layer**: Based on regular expressions and keyword matching, identifies clear user signals.
   - **Pattern Analysis Layer**: Analyzes dialogue interaction patterns, identifies repeated questions, plan acceptance/rejection patterns, etc.
   - **Semantic Inference Layer**: Calls LLM for semantic analysis, handling complex memory recognition.

5. **Memory Management**:
   - **Deduplication and Conflict Detection**: Avoids duplicate memories and handles memory conflicts.
   - **Forgetting Mechanism**: Weighted decay algorithm based on time, frequency, and importance.
   - **Nudge Mechanism**: Active memory review and validation system, regularly checking and adjusting memories.

6. **Memory Quality Assessment**:
   - **Usage Tracking**: Records memory usage frequency and scenarios.
   - **Feedback Analysis**: Collects and analyzes user feedback on memories.
   - **Quality Calculation**: Calculates memory quality scores based on multi-dimensional indicators.

7. **Memory Migration System**:
   - **Data Export**: Exports memories to standard JSON format.
   - **Data Import**: Imports memories from standard JSON format.

8. **Storage Layer**:
   - **Working Memory**: In-memory storage, cleared after session ends.
   - **Procedural Memory**: File system-based storage, suitable for user preferences and behavior rules.
   - **Episodic Memory**: SQLite-based storage, suitable for decision records and task patterns.
   - **Semantic Memory**: SQLite-based storage, suitable for fact declarations and relationship information.

## 2. Core Module Design

### 2.1 Core Engine Module

#### 2.1.1 Function Design
- Initialization and configuration management
- Processing user messages, coordinating multi-layered judgment pipeline
- Managing memory storage and retrieval
- Providing external interfaces

#### 2.1.2 Class Design

```python
class MemoryClassificationEngine:
    def __init__(self, config_path=None):
        # Initialize engine, load configuration
        pass
    
    def process_message(self, message, context=None):
        # Process user message, return memory classification result
        pass
    
    def retrieve_memories(self, query, limit=5):
        # Retrieve relevant memories based on query
        pass
    
    def manage_memory(self, action, memory_id, data=None):
        # Manage memory (view, edit, delete)
        pass
    
    def get_stats(self):
        # Get system statistics
        pass
```

### 2.2 Multi-layered Judgment Pipeline Module

#### 2.2.1 Rule Matching Layer

**Function**: Identifies clear user signals based on rule configuration.

**Design**:
- Rule configuration: YAML format, supporting regular expressions and keyword matching
- Rule loading: Load rules from configuration files
- Rule matching: Apply rules to user input, identify memory types

**Rule Configuration Example**:
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

#### 2.2.2 Pattern Analysis Layer

**Function**: Analyzes dialogue structure, identifies patterns.

**Design**:
- Dialogue state tracking: Tracks dialogue state and patterns
- Duplication detection: Detects repeated questions and task patterns
- Plan acceptance/rejection identification: Identifies user acceptance or rejection of plans

#### 2.2.3 Semantic Inference Layer

**Function**: Uses LLM for semantic analysis, handling complex memory recognition.

**Design**:
- LLM invocation: Calls lightweight LLM for semantic analysis
- Prompt design: Designs effective prompts to guide LLM for memory classification
- Cost control: Limits LLM call frequency, caches results

**Prompt Example**:
```
You are a memory classifier. Analyze the following dialogue snippet and determine if there is information worth long-term memory.

Memory types include:
- user_preference: User-expressed preferences or habits
- fact_declaration: Objective facts stated by the user
- decision: Explicit decisions or conclusions reached
- relationship: Relationships between people, teams, organizations
- task_pattern: Repeated task types
- sentiment_marker: User's emotional tendency on a topic
- correction: User's correction of previous output

If there is no information worth remembering in the dialogue, return empty.

Current dialogue:
{conversation_snippet}

Known user memories:
{existing_memory_summary}

Please output in JSON format, including the following fields:
- has_memory: boolean
- memory_type: string (enumeration value)
- content: string (memory content, concise and accurate)
- tier: int (2=procedural memory, 3=episodic memory, 4=semantic memory)
- confidence: float (0.0-1.0)
- reasoning: string (brief judgment reason)
```

### 2.3 Memory Management Module

#### 2.3.1 Deduplication and Conflict Detection

**Function**: Detects and handles memory duplication and conflicts.

**Design**:
- Duplication detection: Detects duplicate memories based on content similarity and memory type
- Conflict detection: Detects conflicts between new and old memories
- Conflict resolution: Provides conflict resolution mechanism based on timestamp and confidence

#### 2.3.2 Forgetting Mechanism

**Function**: Automatically decays and eliminates low-value memories based on time, frequency, and importance.

**Design**:
- Memory weight calculation: Calculates memory weight based on time decay, access frequency, and confidence
- Memory archiving: Marks memories as archived when their weight falls below threshold
- Memory cleanup: Regularly cleans up archived memories

**Weight Calculation Formula**:
```
Memory weight = confidence × recency_score × frequency_score

recency_score = exp(-λ × days_since_last_access)  # Exponential decay
frequency_score = log(1 + access_count)            # Logarithmic growth, marginal decrease
```

### 2.4 Storage Layer Module

#### 2.4.1 Working Memory

**Function**: Stores context information of the current session.

**Design**:
- In-memory storage: Uses Python dictionary or queue storage
- Session management: Automatically cleared after session ends
- Size limit: Sets maximum capacity to avoid excessive memory usage

#### 2.4.2 Procedural Memory

**Function**: Stores fixed information such as user preferences and behavior rules.

**Design**:
- File storage: Uses YAML/JSON files for storage
- Hierarchical loading: Supports global, project-level, and local-level configurations
- Format design: Structured format for easy reading and modification

**Storage Format Example**:
```yaml
user_preferences:
  - id: "pref_001"
    content: "Use double quotes instead of single quotes"
    created_at: "2026-04-03T10:00:00Z"
    updated_at: "2026-04-03T10:00:00Z"
    confidence: 1.0
    source: "rule:0"
```

#### 2.4.3 Episodic Memory

**Function**: Stores time-related information such as decision records and task patterns.

**Design**:
- SQLite storage: Uses SQLite database for storage
- Table structure design: Includes memory metadata and content
- Retrieval optimization: Supports time and content-based retrieval

**Table Structure Design**:
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

#### 2.4.4 Semantic Memory

**Function**: Stores structured knowledge such as fact declarations and relationship information.

**Design**:
- SQLite storage: Uses SQLite database for storage
- Relationship model: Uses entity-relationship-attribute model
- Query optimization: Supports complex relationship queries

**Table Structure Design**:
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

### 2.5 Advanced Wrapper Module

#### 2.5.1 MemoryOrchestrator

**Function**: Provides a one-stop memory management solution, integrating classification, storage, retrieval, forgetting, quality assessment, and migration functions.

**Design**:
- Unified interface: Provides concise API, hiding underlying complexity
- Function integration: Integrates all core functions including learning, recall, forgetting, searching, quality assessment, and migration
- Error handling: Comprehensive exception capture and error handling
- Logging: Detailed operation logs

**Core Methods**:
```python
class MemoryOrchestrator:
    def learn(self, message, context=None, execution_context=None):
        # Learn new memory
        pass
    
    def recall(self, query, memory_type=None, limit=10):
        # Recall relevant memories
        pass
    
    def forget(self, memory_id, action='decrease_weight', weight_adjustment=0.1):
        # Forget or adjust memory
        pass
    
    def search(self, search_term, memory_types=None, min_confidence=0.5, limit=20):
        # Advanced search
        pass
    
    def get_memory_quality(self, memory_id):
        # Get memory quality
        pass
    
    def generate_quality_report(self, days=30):
        # Generate quality report
        pass
    
    def export_memories(self, include_metadata=True):
        # Export memories
        pass
    
    def import_memories(self, json_str, validate_checksum=True):
        # Import memories
        pass
```

### 2.6 Memory Quality Assessment Module

**Function**: Tracks memory usage, effectiveness, and value, providing quality assessment and reports.

**Design**:
- Data tracking: Records memory usage and user feedback
- Multi-dimensional assessment: Calculates quality based on usage frequency, success rate, feedback score, freshness, and diversity
- Report generation: Generates quality reports and low-value memory reports
- Real-time updates: Automatically updates usage statistics when memories are used

**Core Methods**:
```python
class MemoryQualityManager:
    def track_memory_usage(self, memory_id, query, result=True):
        # Track memory usage
        pass
    
    def track_feedback(self, memory_id, feedback, context=None):
        # Track user feedback
        pass
    
    def calculate_memory_quality(self, memory_id, memory):
        # Calculate memory quality
        pass
    
    def generate_low_value_report(self, threshold=0.3, days=30):
        # Generate low-value memory report
        pass
    
    def generate_quality_report(self, days=30):
        # Generate quality report
        pass
```

### 2.7 Memory Migration Module

**Function**: Implements memory export and import, supporting cross-session, cross-Agent memory migration.

**Design**:
- Standard format: Defines unified JSON format to ensure cross-platform compatibility
- Data validation: Generates and validates checksums to ensure data integrity
- File support: Supports exporting to files and importing from files
- Error handling: Comprehensive exception capture and error handling

**Core Methods**:
```python
class MemoryMigrationManager:
    def export_memories(self, memories, include_metadata=True):
        # Export memories to standard format
        pass
    
    def import_memories(self, json_str, validate_checksum=True):
        # Import memories from standard format
        pass
    
    def export_to_file(self, memories, file_path, include_metadata=True):
        # Export memories to file
        pass
    
    def import_from_file(self, file_path, validate_checksum=True):
        # Import memories from file
        pass
    
    def validate_export_data(self, json_str):
        # Validate export data validity
        pass
```

### 2.8 MCP Server Module

**Function**: Implements MCP (Model Context Protocol) server, supporting integration with tools like Claude Code and Cursor.

**Design**:
- HTTP server: Implemented based on standard library http.server
- Tool definition: Provides 8 core tools for memory management
- Configuration management: Supports custom server settings through configuration files
- Error handling: Comprehensive exception capture and error response

**Core Tools**:
1. **classify_memory**: Analyzes messages and determines if memory is needed
2. **store_memory**: Stores memory to appropriate tier
3. **retrieve_memories**: Retrieves relevant memories
4. **get_memory_stats**: Gets memory statistics
5. **batch_classify**: Batch classifies multiple messages
6. **find_similar**: Finds similar memories
7. **export_memories**: Exports memories to standard format
8. **import_memories**: Imports memories from standard format

**Implementation Status**: ✅ Completed
**Implementation Location**: `src/memory_classification_engine/integration/layer2_mcp/`

## 3. Data Model Design

### 3.1 Memory Metadata Model

```json
{
  "id": "mem_20260403_001",
  "type": "user_preference",
  "tier": 2,
  "content": "Use double quotes instead of single quotes",
  "created_at": "2026-04-03T10:00:00Z",
  "updated_at": "2026-04-03T10:00:00Z",
  "last_accessed": "2026-04-03T10:30:00Z",
  "access_count": 5,
  "confidence": 1.0,
  "source": "rule:0",
  "context": "User mentioned during code style discussion",
  "status": "active"
}
```

### 3.2 Memory Type Enumeration

```python
MEMORY_TYPES = {
    "user_preference": "User Preference",
    "correction": "Correction",
    "fact_declaration": "Fact Declaration",
    "decision": "Decision",
    "relationship": "Relationship",
    "task_pattern": "Task Pattern",
    "sentiment_marker": "Sentiment Marker"
}
```

### 3.3 Memory Tier Enumeration

```python
MEMORY_TIERS = {
    1: "Working Memory",
    2: "Procedural Memory",
    3: "Episodic Memory",
    4: "Semantic Memory"
}
```

## 4. API Interface Design

### 4.1 Python SDK Interface (Layer 1)

```python
class MemoryClassificationEngine:
    def __init__(self, config_path=None):
        """Initialize engine"""
        pass
    
    def process_message(self, message, context=None):
        """Process user message, return memory classification result"""
        pass
    
    def retrieve_memories(self, query, limit=5):
        """Retrieve relevant memories based on query"""
        pass
    
    def manage_memory(self, action, memory_id, data=None):
        """Manage memory (view, edit, delete)"""
        pass
    
    def get_stats(self):
        """Get system statistics"""
        pass
    
    def export_memories(self, format="json"):
        """Export memory data"""
        pass
    
    def import_memories(self, data, format="json"):
        """Import memory data"""
        pass
```

### 4.2 MCP Server Interface (Layer 2) ⭐ Recent Focus

#### 4.2.1 MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Module                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  server.py - MCP Server Main Entry                    │   │
│  │  • Initialize MCP Server                                 │   │
│  │  • Register all Tools                                    │   │
│  │  • Handle JSON-RPC Requests                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  tools.py - Tools Definition                           │   │
│  │  • 8 Core Tools Definition                              │   │
│  │  • Input/Output Schema Definition                      │   │
│  │  • Parameter Validation                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  handlers.py - Request Handlers                        │   │
│  │  • Business Logic for each Tool                         │   │
│  │  • Call Engine SDK                                     │   │
│  │  • Error Handling                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2.2 MCP Tools Detailed Design

**Tool 1: classify_memory**

```python
{
    "name": "classify_memory",
    "description": "Analyze message and determine if memory is needed",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "User message content"
            },
            "context": {
                "type": "string",
                "description": "Dialogue context (optional)"
            }
        },
        "required": ["message"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "matched": {
                "type": "boolean",
                "description": "Whether memory type is matched"
            },
            "memory_type": {
                "type": "string",
                "enum": ["user_preference", "correction", "fact_declaration", 
                        "decision", "relationship", "task_pattern", "sentiment_marker"],
                "description": "Memory type"
            },
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "Memory tier"
            },
            "content": {
                "type": "string",
                "description": "Extracted memory content"
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Confidence"
            },
            "reasoning": {
                "type": "string",
                "description": "Judgment reason"
            }
        }
    }
}
```

**Tool 2: store_memory**

```python
{
    "name": "store_memory",
    "description": "Store memory to appropriate tier",
    "inputSchema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Memory content"
            },
            "memory_type": {
                "type": "string",
                "enum": ["user_preference", "correction", "fact_declaration", 
                        "decision", "relationship", "task_pattern", "sentiment_marker"],
                "description": "Memory type"
            },
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "Memory tier (optional, default automatically determined)"
            },
            "context": {
                "type": "string",
                "description": "Context information (optional)"
            }
        },
        "required": ["content", "memory_type"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "memory_id": {
                "type": "string",
                "description": "Memory ID"
            },
            "stored": {
                "type": "boolean",
                "description": "Whether successfully stored"
            },
            "tier": {
                "type": "integer",
                "description": "Actual storage tier"
            }
        }
    }
}
```

**Tool 3: retrieve_memories**

```python
{
    "name": "retrieve_memories",
    "description": "Retrieve relevant memories",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Query content"
            },
            "limit": {
                "type": "integer",
                "default": 5,
                "description": "Result quantity limit"
            },
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "Specified tier (optional)"
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

**Tool 4: get_memory_stats**

```python
{
    "name": "get_memory_stats",
    "description": "Get memory statistics",
    "inputSchema": {
        "type": "object",
        "properties": {
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "Specified tier (optional, returns all tiers if not specified)"
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

#### 4.2.3 MCP Server Configuration

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

**Cursor MCP Configuration:**

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

### 4.3 OpenClaw CLI Interface (Layer 2)

#### 4.3.1 CLI Command Design

```bash
# Installation
pip install mce-openclaw

# Classify memory
mce-openclaw classify --message "I like using double quotes" --context "Code style discussion"

# Store memory
mce-openclaw store --content "Use double quotes" --type user_preference --tier 2

# Retrieve memory
mce-openclaw retrieve --query "Code style" --limit 5

# Get statistics
mce-openclaw stats [--tier 2]

# Batch classify
mce-openclaw batch-classify --file messages.json

# Find similar
mce-openclaw find-similar --content "Code style preference" --threshold 0.8

# Export memory
mce-openclaw export --format json --output memories.json [--tier 3]

# Import memory
mce-openclaw import --file memories.json --format json
```

#### 4.3.2 OpenClaw Configuration File (.clawrc)

```yaml
# .clawrc - OpenClaw configuration file
version: "1.0"

tools:
  - name: mce_classify
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

  - name: mce_store
    description: Store memory to appropriate tier
    command: mce-openclaw store
    args:
      - name: content
        type: string
        required: true
        description: Memory content
      - name: type
        type: string
        required: true
        description: Memory type
      - name: tier
        type: integer
        required: false
        description: Memory tier

  - name: mce_retrieve
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
        description: Result quantity

  - name: mce_stats
    description: Get memory statistics
    command: mce-openclaw stats
    args:
      - name: tier
        type: integer
        required: false
        description: Specified tier
```

### 4.4 Framework Adapters Interface (Layer 3)

#### 4.4.1 LangChain Adapter

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional

class ClassifyMemoryInput(BaseModel):
    message: str = Field(description="User message content")
    context: Optional[str] = Field(default=None, description="Dialogue context")

class MemoryClassifierTool(BaseTool):
    """LangChain Tool for memory classification"""
    
    name: str = "memory_classifier"
    description: str = "Classify and store user memories"
    args_schema: type[BaseModel] = ClassifyMemoryInput
    
    def __init__(self, config_path: str = None):
        super().__init__()
        from memory_classification_engine import MemoryClassificationEngine
        self.engine = MemoryClassificationEngine(config_path)
    
    def _run(self, message: str, context: Optional[str] = None) -> dict:
        """Run the tool"""
        return self.engine.process_message(message, context)
    
    async def _arun(self, message: str, context: Optional[str] = None) -> dict:
        """Async run"""
        return self._run(message, context)
```

#### 4.4.2 CrewAI Adapter

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional

class StoreMemoryInput(BaseModel):
    content: str = Field(description="Memory content")
    memory_type: str = Field(description="Memory type")
    tier: Optional[int] = Field(default=None, description="Memory tier")

class MemoryTool(BaseTool):
    """CrewAI Tool for memory management"""
    
    name: str = "memory_tool"
    description: str = "Manage user memories - classify, store, and retrieve"
    args_schema: Type[BaseModel] = StoreMemoryInput
    
    def __init__(self, config_path: str = None):
        super().__init__()
        from memory_classification_engine import MemoryClassificationEngine
        self.engine = MemoryClassificationEngine(config_path)
    
    def _run(self, content: str, memory_type: str, tier: Optional[int] = None) -> dict:
        """Store a memory"""
        return self.engine.store_memory(content, memory_type, tier)
```

#### 4.4.3 AutoGen Adapter

```python
from autogen import ConversableAgent
from typing import Dict, Any, Optional

class MemoryAgent(ConversableAgent):
    """AutoGen Agent with memory capabilities"""
    
    def __init__(
        self,
        name: str,
        config_path: Optional[str] = None,
        system_message: Optional[str] = None,
        **kwargs
    ):
        # Initialize memory engine
        from memory_classification_engine import MemoryClassificationEngine
        self.memory_engine = MemoryClassificationEngine(config_path)
        
        # Build system message with memory capabilities
        enhanced_system_message = self._build_system_message(system_message)
        
        super().__init__(
            name=name,
            system_message=enhanced_system_message,
            **kwargs
        )
    
    def _build_system_message(self, base_message: Optional[str]) -> str:
        """Build enhanced system message"""
        memory_capabilities = """
You have access to a memory classification engine that can:
1. Classify user messages for important information to remember
2. Store memories in appropriate tiers
3. Retrieve relevant memories based on context

Use these capabilities to provide personalized responses.
"""
        if base_message:
            return f"{base_message}\n\n{memory_capabilities}"
        return memory_capabilities
    
    def process_message_with_memory(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process message and automatically classify memory"""
        # First retrieve relevant memories
        memories = self.memory_engine.retrieve_memories(message)
        
        # Classify current message
        classification = self.memory_engine.process_message(message, context)
        
        return {
            "memories": memories,
            "classification": classification
        }
```

### 4.2 REST API Interface

#### 4.2.1 Process Message
- **URL**: `/api/message`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "message": "Remember, I don't like using dashes in code",
    "context": {}
  }
  ```
- **Response**:
  ```json
  {
    "matched": true,
    "memory_type": "user_preference",
    "tier": 2,
    "content": "Don't like using dashes in code",
    "confidence": 1.0,
    "source": "rule:0"
  }
  ```

#### 4.2.2 Retrieve Memories
- **URL**: `/api/memories`
- **Method**: GET
- **Query Parameters**:
  - `query`: Retrieval query
  - `limit`: Result quantity limit
- **Response**:
  ```json
  {
    "memories": [
      {
        "id": "mem_20260403_001",
        "type": "user_preference",
        "tier": 2,
        "content": "Don't like using dashes in code",
        "confidence": 1.0,
        "source": "rule:0"
      }
    ]
  }
  ```

#### 4.2.3 Manage Memory
- **URL**: `/api/memories/{id}`
- **Method**: GET, PUT, DELETE
- **Request Body** (PUT):
  ```json
  {
    "content": "Don't like using dashes and semicolons in code",
    "confidence": 1.0
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "memory": {
      "id": "mem_20260403_001",
      "type": "user_preference",
      "tier": 2,
      "content": "Don't like using dashes and semicolons in code",
      "confidence": 1.0,
      "source": "rule:0"
    }
  }
  ```

## 5. Test Plan Design

### 5.1 Unit Testing

**Test Objective**: Verify the functional correctness of each module.

**Test Content**:
- Core engine initialization and configuration
- Rule loading and matching in the rule matching layer
- Pattern recognition in the pattern analysis layer
- LLM invocation and result parsing in the semantic inference layer
- Deduplication and conflict detection in memory management
- Weight calculation and memory archiving in the forgetting mechanism
- Read/write operations in the storage layer

**New - Layer 2 Unit Testing**:
- MCP Server initialization
- MCP Tools parameter validation
- MCP Tools business logic
- OpenClaw CLI command parsing
- OpenClaw CLI parameter validation

**Test Tools**:
- pytest
- mock library (simulating LLM calls)
- pytest-asyncio (MCP Server async testing)

### 5.2 Integration Testing

**Test Objective**: Verify the integration between modules is normal.

**Test Content**:
- Complete memory classification process
- Memory storage and retrieval process
- Memory management operations
- API interface calls

**New - Layer 2/3 Integration Testing**:
- MCP Server and Engine SDK integration
- MCP JSON-RPC protocol compatibility
- Claude Code MCP client compatibility
- Cursor MCP client compatibility
- OpenClaw CLI and Engine SDK integration
- OpenClaw configuration file parsing
- LangChain Adapter integration
- CrewAI Adapter integration
- AutoGen Adapter integration

**Test Tools**:
- pytest
- requests (testing REST API)
- mcp.client (MCP client testing)
- subprocess (CLI testing)

### 5.3 Performance Testing

**Test Objective**: Verify system performance and resource usage.

**Test Content**:
- Memory classification response time
- Memory retrieval response time
- System's ability to handle concurrent requests
- Memory usage
- Storage usage

**Test Tools**:
- pytest-benchmark
- timeit
- memory-profiler

### 5.4 User Acceptance Testing

**Test Objective**: Verify if the system meets user requirements.

**Test Content**:
- Memory classification accuracy
- Memory retrieval relevance
- Ease of use for memory management
- Overall user experience of the system

**Test Methods**:
- Prepare test cases
- Have user representatives execute tests
- Collect user feedback
- Analyze test results

## 6. Deployment Plan Design

### 6.1 Deployment Environment

**Local Deployment**:
- Python 3.8+
- Dependencies: PyYAML, SQLite3, Flask (optional, for REST API)

**Container Deployment**:
- Docker image
- Docker Compose configuration

### 6.2 Configuration Management

**Configuration Files**:
- `config/config.yaml`: System configuration
- `config/rules.yaml`: Rule configuration

**Environment Variables**:
- `MCE_CONFIG_PATH`: Configuration file path
- `MCE_DATA_PATH`: Data storage path
- `MCE_LLM_API_KEY`: LLM API key (optional)

### 6.3 Deployment Steps

**Local Deployment**:
1. Clone the code repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure rules: Edit `config/rules.yaml`
4. Start the service: `python -m memory_classification_engine`

**Container Deployment**:
1. Build the image: `docker build -t memory-classification-engine .`
2. Run the container: `docker run -p 5000:5000 memory-classification-engine`

### 6.4 Monitoring and Maintenance

**Monitoring**:
- Logging: System operation logs
- Performance monitoring: Response time, resource usage
- Error monitoring: Exception and error records

**Maintenance**:
- Regular data backup
- Regular cleanup of archived memories
- Regular update of rule configurations

## 7. Security Design

### 7.1 Data Security

- **Data Encryption**: Sensitive memory information is encrypted for storage
- **Access Control**: Role-based access permission management
- **Data Minimization**: Only store necessary memory information
- **Forgetting Mechanism**: Support user-initiated memory deletion
- **Audit Logs**: Record all memory access and modification operations

### 7.2 API Security

- **Authentication**: API access requires authentication
- **Authorization**: Role-based permission control
- **Input Validation**: Validate user input to prevent injection attacks
- **Rate Limiting**: Prevent API abuse
- **HTTPS**: Use HTTPS to protect transmitted data

## 8. Extensibility Design

### 8.1 Module Extension

- **Memory Type Extension**: Support adding new memory types
- **Storage Backend Extension**: Support adding new storage backends
- **Judgment Layer Extension**: Support adding new judgment layers

### 8.2 Integration Extension

- **Agent Framework Integration**: Support integration with different Agent frameworks
- **LLM Integration**: Support integration with different LLMs
- **Third-party Service Integration**: Support integration with third-party services

## 9. Technical Risks and Countermeasures

| Risk | Impact | Countermeasure |
|------|--------|----------------|
| Semantic inference layer performance issues | Excessively long response time, affecting user experience | Prioritize lightweight models, set call frequency limits, implement caching mechanism |
| Storage capacity growing too fast | System performance degradation, increased storage costs | Implement automatic forgetting mechanism, regularly clean up low-value memories, optimize storage structure |
| Complex memory conflict handling | Unpredictable system behavior, poor user experience | Design clear conflict resolution strategies, provide user intervention mechanisms, record conflict history |
| Multi-language support difficulty | Cross-language memory consistency issues | Adopt semantic-based memory representation, prioritize English and Chinese support, use translation API for cross-language mapping |
| LLM dependency risk | LLM service unavailable, system functionality limited | Implement degradation strategy, when LLM is unavailable, only use rule matching and pattern analysis layers |

## 10. Improvement Plan

### 10.1 Improvement Background

Memory Classification Engine is a core component of AI Agent, responsible for intelligent memory classification, layered storage, efficient retrieval, and controllable forgetting. With the development of AI technology and the expansion of application scenarios, Memory Classification Engine needs continuous improvement and optimization to meet increasingly complex requirements. The current system has performance issues, requiring priority optimization of performance, along with code refactoring, configuration management improvement, documentation enhancement, and dependency management optimization.

### 10.2 Improvement Objectives

#### 10.2.1 Core Objectives
- Optimize storage and retrieval performance (primary objective)
- Improve memory classification accuracy and coverage
- Enhance system scalability and maintainability
- Improve user experience and integration capabilities

#### 10.2.2 Specific Objectives
- Reduce memory retrieval response time to within 50ms
- Improve memory classification accuracy to over 90%
- Optimize system startup and runtime
- Support more languages and complex scenarios
- Provide more flexible integration interfaces
- Enhance system stability and reliability
- Eliminate code duplication, improve code reusability
- Move hardcoded parameters to configuration files
- Complete system-level documentation, including architecture design, API documentation, etc.
- Use virtual environments and dependency locking to avoid version conflicts

### 10.3 Improvement Areas

#### 10.3.1 Core Engine Improvement
- Optimize core engine performance and stability
- Improve memory classification algorithms and strategies
- Enhance context understanding capabilities
- Improve system configurability
- Eliminate code duplication, improve code reusability

#### 10.3.2 Storage Layer Improvement
- Optimize storage structure and indexing
- Improve storage backend performance
- Enhance data security and privacy protection
- Support more storage backend options

#### 10.3.3 Retrieval and Injection Improvement
- Optimize memory retrieval algorithms
- Improve memory injection format and strategies
- Enhance semantic understanding and relevance ranking
- Support more complex retrieval scenarios

#### 10.3.4 Multi-language Support
- Enhance multi-language memory consistency
- Improve cross-language memory mapping
- Support memory classification for more languages
- Optimize language detection and processing

#### 10.3.5 Extensibility and Integration
- Provide more flexible SDK and API
- Enhance integration with different Agent frameworks
- Support more LLM models
- Provide more integration examples

#### 10.3.6 Configuration Management
- Move hardcoded parameters to configuration files
- Establish unified configuration management mechanism
- Support mixed configuration of environment variables and configuration files
- Provide configuration validation and default value management

#### 10.3.7 Documentation Enhancement
- Complete system-level documentation, including architecture design, API documentation, etc.
- Comprehensive update of various requirement/design documents
- Complete README and English version documentation
- Provide detailed usage examples and tutorials

#### 10.3.8 Dependency Management
- Use virtual environments and dependency locking
- Avoid version conflicts
- Optimize dependency installation and management
- Establish dependency update strategy

### 10.4 Implementation Plan

#### 10.4.1 Phase 1: Performance Assessment and Planning (2 weeks)
- Task 1.1: Performance Assessment - Evaluate current system performance bottlenecks and issues
- Task 1.2: Code Analysis - Analyze code structure and duplication
- Task 1.3: Improvement Planning - Develop detailed improvement plan, prioritize performance optimization
- Task 1.4: Technical Research - Research relevant performance optimization technologies and solutions

#### 10.4.2 Phase 2: Core Performance Optimization (4 weeks)
- Task 2.1: Storage Layer Performance Optimization - Optimize storage structure and indexing, improve storage and retrieval performance
- Task 2.2: Retrieval Algorithm Optimization - Optimize memory retrieval algorithms, reduce response time
- Task 2.3: Core Engine Performance Optimization - Optimize core engine performance and stability
- Task 2.4: Code Refactoring - Eliminate code duplication, improve code reusability
- Task 2.5: Configuration Management Improvement - Move hardcoded parameters to configuration files, establish unified configuration management mechanism

#### 10.4.3 Phase 3: Function Enhancement and Integration (3 weeks)
- Task 3.1: Memory Classification Algorithm Improvement - Improve memory classification algorithms and strategies, increase accuracy
- Task 3.2: Multi-language Support Enhancement - Enhance multi-language memory consistency and support
- Task 3.3: SDK and API Improvement - Provide more flexible SDK and API
- Task 3.4: Framework and LLM Integration - Enhance integration with different Agent frameworks and LLM models

#### 10.4.4 Phase 4: Documentation Enhancement and Dependency Management (2 weeks)
- Task 4.1: Documentation Enhancement - Complete system-level documentation, including architecture design, API documentation, etc.; comprehensively update various requirement/design documents, including README and English version
- Task 4.2: Dependency Management Improvement - Use virtual environments and dependency locking, avoid version conflicts
- Task 4.3: Testing and Optimization - Write and run tests, optimize and fix based on test results

#### 10.4.5 Phase 5: Deployment and Performance Verification (1 week)
- Task 5.1: Deployment Preparation - Prepare deployment environment and configuration
- Task 5.2: System Deployment - Deploy system to target environment
- Task 5.3: Performance Verification - Verify system performance meets targets
- Task 5.4: Monitoring Setup and Training - Set up system monitoring and alerts, provide training and documentation

### 10.5 Expected Results

#### 10.5.1 Technical Results
- Optimized Memory Classification Engine
- Improved storage and retrieval performance
- Enhanced multi-language support
- More flexible integration interfaces
- Complete testing and documentation

#### 10.5.2 Business Results
- Improved memory capability of AI Agent
- Enhanced user experience
- Reduced system resource usage
- Improved system stability and reliability
- Support for more application scenarios

### 10.6 Success Metrics

- Memory classification accuracy ≥ 90%
- Memory retrieval response time ≤ 50ms
- System stability ≥ 99.9%
- User satisfaction ≥ 85%
- Integration success rate ≥ 95%

## 11. Conclusion

This detailed design document provides a complete technical implementation plan for the Memory Classification Engine, including system architecture, core module design, data model design, API interface design, test plan design, deployment plan design, security design, and extensibility design.

The design adopts a modular, layered architecture to ensure system scalability and maintainability. At the same time, through lightweight technology selection, it ensures the system can run normally in resource-constrained environments.

This design fully considers user needs and technical challenges, providing a complete, practical implementation plan for the Memory Classification Engine.

Through the implementation of the improvement plan, the Memory Classification Engine will continue to be optimized and improved, providing more intelligent, efficient memory management capabilities for AI Agent, supporting more complex application scenarios.