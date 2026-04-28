# CarryMem Architecture

**Version**: v0.1.2
**Date**: 2026-04-28
**Status**: Stable

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Architecture](#core-architecture)
3. [Layer Design](#layer-design)
4. [Data Flow](#data-flow)
5. [Key Components](#key-components)
6. [Extension Mechanisms](#extension-mechanisms)
7. [Performance Optimization](#performance-optimization)
8. [Security Design](#security-design)

---

## System Overview

### Design Philosophy

CarryMem uses a **layered architecture + plugin design**:

1. **Zero-config**: Works out of the box, auto-initializes
2. **High performance**: 60%+ zero-cost classification, FTS5 full-text search
3. **Extensible**: Adapter pattern supports multiple storage backends
4. **Cross-platform**: Pure Python, minimal external dependencies

### Core Value

```
User Input → Auto-Classify → Smart Store → Semantic Recall
   ↓              ↓              ↓             ↓
 Simple       90%+ accuracy   Dedup+TTL    <100ms
```

---

## Core Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Python   │  │   CLI    │  │   MCP    │              │
│  │   API    │  │  Tool    │  │  Server  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   API Layer                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │              CarryMem (Main Entry)                │  │
│  │  - classify_and_remember()  - recall_memories()   │  │
│  │  - declare()  - forget_memory()                   │  │
│  │  - export_memories()  - import_memories()         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Classification Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Rule Engine │  │   Pattern    │  │   Semantic   │ │
│  │ (Zero-cost)  │  │  Analyzer    │  │  Classifier  │ │
│  │    60%+      │  │    ~30%      │  │    <10%      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│               Storage Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   SQLite     │  │   Obsidian   │  │   Custom     │ │
│  │  (Default)   │  │   (Plugin)   │  │  (Adapter)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│               Recall Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  FTS5 Search │  │   Semantic   │  │    Result    │ │
│  │  (Exact)     │  │   Expander   │  │    Merger    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Layer Design

### 1. User Layer

**Responsibility**: Provide multiple interaction methods

#### 1.1 Python API
```python
from memory_classification_engine import CarryMem

with CarryMem() as cm:
    cm.classify_and_remember("I prefer dark mode")
    memories = cm.recall_memories(query="theme")
```

#### 1.2 CLI Tool
```bash
carrymem init
carrymem list
carrymem stats
```

#### 1.3 MCP Server
```json
{
  "mcpServers": {
    "carrymem": {
      "command": "python3",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"]
    }
  }
}
```

### 2. API Layer

**Responsibility**: Unified business logic entry point

#### Core Class: CarryMem

```python
class CarryMem:
    def __init__(
        self,
        storage: Optional[Any] = "sqlite",
        db_path: Optional[str] = None,
        knowledge_adapter: Optional[StorageAdapter] = None,
        namespace: str = "default",
        config: Optional[Dict] = None,
    ): ...

    def classify_and_remember(self, message, context=None, language=None) -> Dict: ...
    def recall_memories(self, query=None, filters=None, limit=20) -> List[Dict]: ...
    def forget_memory(self, memory_id: str) -> bool: ...
    def declare(self, message: str) -> Dict: ...
    def get_memory_profile(self) -> Dict: ...
    def export_memories(self, output_path=None, format="json", namespace=None) -> Dict: ...
    def import_memories(self, input_path=None, merge_strategy="skip", namespace=None) -> Dict: ...
    def build_system_prompt(self, context=None, max_memories=10, max_knowledge=5, language="en") -> str: ...
```

### 3. Classification Layer

**Responsibility**: Auto-identify memory types

#### Three-Tier Classification Strategy

```
Input → Rule Engine (60%+) → Pattern Analyzer (~30%) → Semantic Classifier (<10%)
          ↓                       ↓                         ↓
      Zero cost             Near-zero cost             Token cost
      High speed            Medium speed               Low speed
```

#### 3.1 Rule Engine (RuleMatcher)

Pattern-based classification using regex and keywords. Zero cost, covers ~60% of inputs.

#### 3.2 Pattern Analyzer (PatternAnalyzer)

NLP-based pattern analysis. Near-zero cost, covers ~30% of inputs.

#### 3.3 Semantic Classifier (SemanticClassifier)

LLM-based classification for ambiguous cases. Token cost, covers <10% of inputs.

### 4. Storage Layer

**Responsibility**: Persistence and retrieval

#### 4.1 Adapter Interface

```python
class StorageAdapter(ABC):
    @abstractmethod
    def remember(self, entry: MemoryEntry) -> StoredMemory: ...

    @abstractmethod
    def recall(self, query: str, filters=None, limit=20, namespaces=None) -> List[StoredMemory]: ...

    @abstractmethod
    def forget(self, storage_key: str) -> bool: ...
```

#### 4.2 SQLite Adapter

**Features**:
- FTS5 full-text search with trigram tokenizer
- Content deduplication (content_hash)
- TTL auto-expiry
- Transaction support (BEGIN/COMMIT/ROLLBACK)
- Thread safety (threading.Lock + threading.local)

**Database Schema**:
```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    original_message TEXT,
    confidence REAL NOT NULL,
    tier INTEGER NOT NULL,
    namespace TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    access_count INTEGER,
    content_hash TEXT NOT NULL,
    metadata TEXT
);

CREATE VIRTUAL TABLE memories_fts USING fts5(
    content,
    original_message,
    tokenize='trigram'
);
```

### 5. Recall Layer

**Responsibility**: Smart retrieval and result optimization

#### 5.1 Recall Pipeline

```
Query → FTS5 Search → Semantic Expansion → Result Fusion → Sort → Return
  ↓         ↓              ↓                 ↓           ↓       ↓
Validate  Exact match  Synonym expand    Dedup     Relevance  Top-K
```

#### 5.2 Semantic Expansion (v0.4.0)

Zero-dependency semantic expansion:
- **Synonym expansion**: YAML-based synonym graph (470+ terms, CN/EN/JP)
- **Spell correction**: Levenshtein edit distance
- **Cross-language mapping**: CN↔EN↔JP term mapping

#### 5.3 Result Fusion

```python
class ResultMerger:
    def merge(self, original_results, expanded_results, query, limit=20, source="synonym"):
        # 1. Deduplicate by storage_key
        # 2. Calculate relevance score
        # 3. Sort by relevance
        # 4. Return top-K
```

---

## Data Flow

### Store Flow

```
1. User Input
   ↓
2. Input Validation
   ↓
3. Classification (Rule → Pattern → Semantic)
   ↓
4. Create MemoryEntry
   ↓
5. Calculate content_hash
   ↓
6. Check duplicate
   ↓
7. Store to database
   ↓
8. Update FTS5 index
   ↓
9. Return result
```

### Recall Flow

```
1. User Query
   ↓
2. Query Validation
   ↓
3. FTS5 Search
   ↓
4. Results insufficient? → Semantic Expansion
   ↓
5. Result Fusion
   ↓
6. Dedup + Sort
   ↓
7. Update access_count
   ↓
8. Return Top-K
```

---

## Key Components

### 1. Configuration

```python
# Default config
CarryMem(storage="sqlite", db_path=None, namespace="default")

# Custom storage
CarryMem(storage=SQLiteAdapter(db_path="/custom/path.db"))

# With knowledge base
CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
```

### 2. Exception Hierarchy

```python
class CarryMemError(Exception):
    """Base exception"""

class StorageError(CarryMemError):
    """Storage error"""

class DatabaseError(StorageError):
    """Database error"""

class ValidationError(CarryMemError):
    """Validation error"""
```

### 3. Logging

```python
from memory_classification_engine.utils.logger import logger

# Log levels: DEBUG, INFO, WARNING, ERROR
# File: ~/.carrymem/logs/carrymem.log (if configured)
```

---

## Extension Mechanisms

### 1. Custom Storage Adapter

```python
from memory_classification_engine.adapters import StorageAdapter

class PostgreSQLAdapter(StorageAdapter):
    def remember(self, entry: MemoryEntry) -> StoredMemory: ...
    def recall(self, query: str, **kwargs) -> List[StoredMemory]: ...
    def forget(self, storage_key: str) -> bool: ...

# Usage
cm = CarryMem(storage=PostgreSQLAdapter("postgresql://..."))
```

### 2. Plugin System

```python
# setup.py
entry_points={
    "carrymem.adapters": [
        "postgresql=my_plugin:PostgreSQLAdapter",
    ],
}

# Dynamic loading
cm = CarryMem(storage="postgresql")
```

---

## Performance Optimization

### 1. Query Optimization

**Index Strategy**:
- Single column: type, namespace, content_hash
- Composite: (namespace, type), (namespace, tier)
- FTS5: trigram tokenizer

### 2. Batch Operations

```python
# Atomic batch with transaction
adapter.remember_batch(entries)
# → BEGIN → INSERT... → COMMIT (or ROLLBACK on error)
```

### 3. Thread Safety

```python
# ThreadLocal connections + Lock
adapter = SQLiteAdapter()  # Thread-safe by default
```

---

## Security Design

### 1. Input Validation

All inputs validated via `validators.py`:
- Message length limits
- Namespace character whitelist
- Storage key format validation
- Query length limits

### 2. SQL Injection Prevention

All queries use parameterized statements (`?` placeholders).

### 3. Path Safety

```python
# Path traversal prevention
def _validate_file_path(path: str) -> str:
    if ".." in path:
        raise ValueError("Path traversal not allowed")
    return os.path.realpath(os.path.expanduser(path))
```

### 4. MCP Handler Safety

- Exception sanitization: internal errors never exposed to clients
- Parameter clamping: limit, max_memories, max_knowledge all bounded
- Language whitelist: only "en", "zh", "ja" accepted

---

## Summary

CarryMem uses a **layered architecture + plugin design**, achieving:

✅ **High Performance**: FTS5 + indexing + caching
✅ **Extensible**: Adapter pattern + plugin system
✅ **Easy to Use**: Zero config + CLI tools
✅ **Secure**: Input validation + parameterized queries + path safety
