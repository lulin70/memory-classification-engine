# Memory Classification Engine - Product Requirements Document

## 1. User Stories

### 1.1 Core User Stories

#### Story 1: Intelligent Assistant Developer
**As** an intelligent assistant developer
**I want** to integrate a memory classification engine into my assistant system
**So that** the assistant can remember user preferences and important information, providing more personalized services

#### Story 2: Enterprise Customer Service System Administrator
**As** an enterprise customer service system administrator
**I want** the system to intelligently remember customer historical needs and preferences
**So that** customer service representatives can quickly understand customer backgrounds and provide more efficient service

#### Story 3: Individual User
**As** an individual user
**I want** conversations with AI assistants to maintain continuity without repeating the same information
**So that** I can get a more natural and personalized interaction experience

### 1.2 Detailed User Scenarios

#### Scenario 1: Code Style Preference Memory
**User**: Developer
**Scenario**: User mentions "I like using double quotes instead of single quotes" in a conversation with the AI assistant, and the assistant classifies this information as a user preference and stores it
**Result**: Subsequent generated code automatically uses double quotes without the user needing to repeat the reminder

#### Scenario 2: Business Fact Memory
**User**: Enterprise employee
**Scenario**: User mentions "Our company has 5 departments, with 20 people in the technical department"
**Result**: The assistant classifies this information as a fact declaration and stores it in semantic memory, enabling subsequent related questions to be answered based on this information

#### Scenario 3: Decision Record Memory
**User**: Project manager
**Scenario**: After team discussion, consensus is reached: "We decided to use React as the frontend framework"
**Result**: The assistant stores this decision record in episodic memory, enabling subsequent related discussions to reference this decision

#### Scenario 4: Memory Management
**User**: System administrator
**Scenario**: User discovers that some memory information is outdated or incorrect and wants to delete or update it
**Result**: The assistant provides a memory management interface allowing users to view, edit, and delete stored memories

## 2. User Requirements

### 2.1 Functional Requirements

| Requirement ID | Requirement Description | Priority |
|---------------|-------------------------|----------|
| FR-001 | Memory Classification: Automatically identify and classify memory information in user input (preferences, facts, decisions, etc.) | High |
| FR-002 | Tiered Storage: Store different types of memories in different tiers (working memory, procedural memory, episodic memory, semantic memory) | High |
| FR-003 | Memory Retrieval: Retrieve relevant memories from different tiers based on current conversation content | High |
| FR-004 | Memory Injection: Inject retrieved memories into system prompts in a structured format | High |
| FR-005 | Forgetting Mechanism: Automatically decay and eliminate low-value memories based on time, frequency, and importance | Medium |
| FR-006 | Memory Management: Allow users to view, edit, and delete stored memories | Medium |
| FR-007 | Conflict Handling: Provide conflict resolution mechanism when new memories conflict with old ones | Medium |
| FR-008 | Multi-language Support: Identify and process memory information in different languages | Low |

### 2.2 Non-Functional Requirements

| Requirement ID | Requirement Description | Priority |
|---------------|-------------------------|----------|
| NFR-001 | Performance: Memory classification and retrieval response time not exceeding 100ms | High |
| NFR-002 | Reliability: Memory data not lost in case of system failure | High |
| NFR-003 | Security: Sensitive memory information encrypted for storage | High |
| NFR-004 | Scalability: Support for adding new memory types and storage backends in the future | Medium |
| NFR-005 | Resource Usage: Lightweight design suitable for running on edge devices and cloud environments | Medium |
| NFR-006 | Integratability: Provide SDK and API for easy integration with existing systems | High |

### 2.3 Data Requirements

| Requirement ID | Requirement Description | Priority |
|---------------|-------------------------|----------|
| DR-001 | Memory Metadata: Each memory contains metadata such as ID, type, tier, content, creation time, update time, access count, confidence, etc. | High |
| DR-002 | Memory Classification: Support for at least 7 memory types (user preference, correction signal, fact declaration, decision record, relationship information, task pattern, sentiment marker) | High |
| DR-003 | Memory Tiers: Support for 4 memory storage tiers (working memory, procedural memory, episodic memory, semantic memory) | High |
| DR-004 | Data Persistence: Ensure memory data remains available after system restart | High |
| DR-005 | Data Export: Support for exporting memory data to standard formats | Medium |

### 2.4 Integration Requirements

#### 2.4.1 MCP Server Requirements

| Requirement ID | Requirement Description | Priority |
|---------------|-------------------------|----------|
| MCP-001 | MCP Server Implementation: Provide server implementation compliant with Model Context Protocol standard | High |
| MCP-002 | classify_memory Tool: Analyze messages and determine if memory is needed | High |
| MCP-003 | store_memory Tool: Store memory to appropriate tier | High |
| MCP-004 | retrieve_memories Tool: Retrieve relevant memories | High |
| MCP-005 | get_memory_stats Tool: Get memory statistics | Medium |
| MCP-006 | batch_classify Tool: Batch classify messages | Medium |
| MCP-007 | find_similar Tool: Find similar memories | Medium |
| MCP-008 | export_memories Tool: Export memory data | Low |
| MCP-009 | import_memories Tool: Import memory data | Low |
| MCP-010 | Claude Code Compatibility: Ensure compatibility with Claude Code's MCP client | High |
| MCP-011 | Cursor Compatibility: Ensure compatibility with Cursor's MCP client | High |

#### 2.4.2 OpenClaw Integration Requirements

| Requirement ID | Requirement Description | Priority |
|---------------|-------------------------|----------|
| OC-001 | OpenClaw CLI Adapter: Provide command-line tool for OpenClaw to call | High |
| OC-002 | OpenClaw Configuration File: Provide .clawrc configuration file template | High |
| OC-003 | classify_memory Command: Analyze messages and determine if memory is needed | High |
| OC-004 | store_memory Command: Store memory to appropriate tier | High |
| OC-005 | retrieve_memories Command: Retrieve relevant memories | High |
| OC-006 | Documentation and Examples: Provide OpenClaw integration documentation and usage examples | Medium |

#### 2.4.3 Framework Adapters Requirements

| Requirement ID | Requirement Description | Priority |
|---------------|-------------------------|----------|
| FA-001 | LangChain Adapter: Provide LangChain Tool encapsulation | Medium |
| FA-002 | CrewAI Adapter: Provide CrewAI Tool encapsulation | Medium |
| FA-003 | AutoGen Adapter: Provide AutoGen Agent encapsulation | Low |
| FA-004 | Adapter Documentation: Provide usage documentation for each framework adapter | Medium |

## 3. Technical Architecture

### 3.1 Architecture Overview

The Memory Classification Engine adopts a modular design, consisting of a core engine, multi-layered judgment pipeline, storage layer, and utilities layer. The system is designed with lightweight principles, prioritizing the use of existing local technologies to ensure normal operation in resource-constrained environments.

### 3.2 Technology Selection

| Component | Technical Solution | Selection Reason |
|-----------|-------------------|------------------|
| Core Language | Python 3 | Already installed locally, rich ecosystem, suitable for AI-related development |
| Rule Engine | YAML configuration + Regular expressions | Lightweight, easy to configure and extend |
| Dialogue State Tracking | In-memory state machine | Simple and efficient, suitable for initial development |
| Procedural Memory Storage | YAML/JSON files | Lightweight, easy to read/write and version control |
| Episodic Memory Storage | SQLite + Vector embeddings | Native support, no additional installation required, suitable for small to medium applications |
| Semantic Memory Storage | SQLite + Relational model | Native support, no additional installation required, suitable for structured data |
| Semantic Classification | Local small model (if available) or API call | Flexible adaptation to different environments |
| Interface Form | Python SDK + REST API | Easy to integrate into different systems |

### 3.3 System Architecture Diagram

```
┌─────────────────────┐
│     External Systems│
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│    API/SDK Interface│
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   Core Engine       │
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

### 3.4 Core Module Design

#### 3.4.1 Core Engine
- **Function**: Coordinate the work of various modules, handle external requests
- **Interfaces**:
  - `process_message(message)`: Process user message, return memory classification result
  - `retrieve_memories(query)`: Retrieve relevant memories based on query
  - `manage_memory(action, memory_id, data)`: Manage memory (view, edit, delete)

#### 3.4.2 Multi-layered Judgment Pipeline
- **Rule Matching Layer**: Based on regular expressions and keyword matching, identify clear user signals
- **Pattern Analysis Layer**: Analyze dialogue interaction patterns, identify repeated questions, plan acceptance/rejection patterns, etc.
- **Semantic Inference Layer**: Call models for semantic analysis, handle complex memory recognition

#### 3.4.3 Memory Management
- **Deduplication and Conflict Detection**: Avoid duplicate memories, handle memory conflicts
- **Forgetting Mechanism**: Weighted decay algorithm based on time, frequency, and importance
- **Memory Compression**: Compress detailed information into patterns, reduce storage footprint

#### 3.4.4 Storage Layer
- **Working Memory**: In-memory storage, cleared after session ends
- **Procedural Memory**: YAML/JSON file storage, suitable for user preferences, behavior rules
- **Episodic Memory**: SQLite storage, suitable for decision records, task patterns
- **Semantic Memory**: SQLite storage, suitable for fact declarations, relationship information

### 3.5 Data Model

#### 3.5.1 Memory Metadata
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

#### 3.5.2 Storage Structure
- **Procedural Memory**: YAML files, organized by type
- **Episodic Memory**: SQLite tables, containing memory metadata and vector embeddings
- **Semantic Memory**: SQLite tables, containing entity-relationship-attribute structure

### 3.6 Deployment and Integration

#### 3.6.1 Deployment Methods
- **Local Deployment**: Integrated as an independent module into existing systems
- **Container Deployment**: Packaged as Docker container for easy running in different environments

#### 3.6.2 Integration Methods

**Layer 1: Python SDK**
- **Python SDK**: Directly imported into Python projects
- **REST API**: Integration with other language systems through HTTP interface

**Layer 2: MCP Server** ⭐ Recent Focus
- **MCP Server**: Server compliant with Model Context Protocol standard
- **Claude Code Integration**: Direct integration through MCP configuration
- **Cursor Integration**: Direct integration through MCP configuration
- **OpenClaw Integration**: Integration through CLI adapter

**Layer 3: Framework Adapters**
- **LangChain**: Provide LangChain Tool encapsulation
- **CrewAI**: Provide CrewAI Tool encapsulation
- **AutoGen**: Provide AutoGen Agent encapsulation
- **Other Frameworks**: Extensible adapter architecture

### 3.7 Performance and Security

#### 3.7.1 Performance Optimization
- **Caching Mechanism**: Frequently accessed memories placed in memory cache
- **Asynchronous Processing**: Time-consuming operations like semantic inference handled asynchronously
- **Batch Operations**: Support for batch memory processing, reduce I/O operations

#### 3.7.2 Security Measures
- **Data Encryption**: Sensitive memory information encrypted for storage
- **Access Control**: Role-based access control
- **Audit Logs**: Record all memory operations for traceability

## 4. Implementation Plan

### 4.1 Phase Division

#### Phase 1: Minimum Viable Product (MVP)
- Implement rule matching layer
- Implement procedural memory read/write
- Provide basic memory retrieval functionality
- Support Python SDK integration

#### Phase 2: Feature Completion
- Implement pattern analysis layer
- Implement episodic memory storage and retrieval
- Implement basic forgetting mechanism
- Provide REST API interface

#### Phase 3: Advanced Features
- Implement semantic inference layer
- Implement semantic memory storage and retrieval
- Complete forgetting mechanism and memory management
- Support multi-language and multi-Agent integration

#### Phase 4: MCP Server and OpenClaw Integration ✅ Completed
- Implement MCP Server core functionality
- Implement 8 MCP Tools
- Ensure compatibility with Claude Code / Cursor
- Implement OpenClaw CLI adapter
- Provide OpenClaw configuration files and documentation

#### Phase 5: Framework Adapters
- Implement LangChain adapter
- Implement CrewAI adapter
- Implement AutoGen adapter
- Provide framework usage documentation

#### Phase 6: Optimization and Expansion
- Performance optimization and resource usage reduction
- Security enhancement and compliance improvement
- Support for more storage backends and model options
- Provide complete documentation and examples

### 4.2 Technical Risks and Countermeasures

| Risk | Countermeasure |
|------|----------------|
| Semantic inference layer performance issues | Prioritize lightweight models, set call frequency limits |
| Storage capacity growing too fast | Implement automatic forgetting mechanism, regularly clean up low-value memories |
| Complex memory conflict handling | Design clear conflict resolution strategies, provide user intervention mechanisms |
| Multi-language support difficulty | Prioritize support for mainstream languages, gradually expand |

## 5. Acceptance Criteria

### 5.1 Functional Acceptance
- Can correctly identify and classify at least 7 memory types
- Can store memories to corresponding tiers
- Can retrieve relevant memories based on queries
- Can automatically decay and eliminate low-value memories
- Can handle memory conflicts

### 5.2 Performance Acceptance
- Memory classification response time ≤ 100ms
- Memory retrieval response time ≤ 200ms
- System can handle at least 100 requests per minute

### 5.3 Reliability Acceptance
- Memory data not lost after system failure
- Can restore to pre-failure state
- Memory usage ≤ 500MB

## 6. Conclusion

The Memory Classification Engine is a lightweight, modular system that can intelligently identify, classify, and manage AI Agent memory information. Through tiered storage and forgetting mechanisms, the system can effectively control storage capacity and retrieval efficiency while ensuring important information is not lost.

This design fully considers the existing local technical environment, adopting lightweight storage solutions to ensure the system can run normally in resource-constrained environments. At the same time, the system has good scalability, and new features and support for more storage backends can be added in the future based on requirements.

Through the implementation of this plan, we will build a fully functional, reliable performance memory classification engine, providing more intelligent and personalized service capabilities for AI Agent.