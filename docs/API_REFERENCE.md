# CarryMem API Reference

**Version**: v0.4.3
**Date**: 2026-04-25

---

## CarryMem Class

Main entry point for CarryMem.

### Constructor

```python
from memory_classification_engine import CarryMem

cm = CarryMem(
    storage="sqlite",           # "sqlite", "obsidian", StorageAdapter instance, or None
    db_path=None,               # Custom database path (default: ~/.carrymem/memories.db)
    knowledge_adapter=None,     # ObsidianAdapter for knowledge base
    namespace="default",        # Namespace for memory isolation
    config=None,                # Optional configuration dict
)
```

### Context Manager

```python
with CarryMem() as cm:
    cm.classify_and_remember("I prefer dark mode")
    # Connection automatically closed on exit
```

---

## Methods

### classify_and_remember()

Classify a message and store it if it's worth remembering.

```python
result = cm.classify_and_remember(
    message="I prefer dark mode",
    context=None,               # Optional context dict
    language=None,              # Optional language hint ("en", "zh", "ja")
)
```

**Returns**:
```python
{
    "should_remember": True,
    "entries": [...],
    "stored": True,
    "storage_keys": ["cm_20260425_..."],
    "summary": {
        "total_entries": 1,
        "by_type": {"user_preference": 1},
        "avg_confidence": 0.95,
    }
}
```

### classify_message()

Classify a message without storing it.

```python
result = cm.classify_message(
    message="I prefer dark mode",
    context=None,
    language=None,
)
```

**Returns**: Same structure as `classify_and_remember()` but without storage.

### recall_memories()

Recall memories matching a query.

```python
memories = cm.recall_memories(
    query="database",           # Search query (supports semantic recall)
    filters=None,               # {"type": "user_preference", "tier": 2}
    limit=20,                   # Max results (1-1000)
)
```

**Returns**: `List[Dict]` where each dict contains:
```python
{
    "id": "cm_...",
    "type": "user_preference",
    "content": "I prefer dark mode",
    "confidence": 0.95,
    "tier": 2,
    "created_at": "2026-04-25T...",
    "storage_key": "cm_...",
    ...
}
```

### forget_memory()

Delete a specific memory.

```python
deleted = cm.forget_memory(memory_id="cm_20260425_...")
```

**Returns**: `bool` — True if the memory was found and deleted.

### declare()

Actively declare a preference or fact (confidence=1.0).

```python
result = cm.declare(
    message="I prefer PostgreSQL over MySQL",
)
```

### get_memory_profile()

Get a summary of stored memories.

```python
profile = cm.get_memory_profile()
```

**Returns**:
```python
{
    "summary": "AI remembers 12 things about you: 5 preferences, 3 corrections, 2 decisions",
    "total_count": 12,
    "by_type": {"user_preference": 5, "correction": 3, ...},
    "highlights": {"user_preference": ["I prefer dark mode", ...], ...},
}
```

### get_stats()

Get storage statistics.

```python
stats = cm.get_stats()
```

**Returns**:
```python
{
    "total_count": 12,
    "by_type": {"user_preference": 5, ...},
    "by_tier": {"2": 8, "3": 4},
    "avg_confidence": 0.89,
}
```

### export_memories()

Export memories to a file.

```python
result = cm.export_memories(
    output_path="my_memories.json",   # Output file path
    format="json",                     # "json" or "markdown"
    namespace=None,                    # Export specific namespace
)
```

### import_memories()

Import memories from a file.

```python
result = cm.import_memories(
    input_path="my_memories.json",     # Input file path
    merge_strategy="skip",             # "skip" or "overwrite"
    namespace=None,                    # Import to specific namespace
)
```

### build_system_prompt()

Build a system prompt with relevant memories.

```python
prompt = cm.build_system_prompt(
    context=None,               # Optional context
    max_memories=10,            # Max memories to include
    max_knowledge=5,            # Max knowledge entries
    language="en",              # "en", "zh", "ja"
)
```

### index_knowledge()

Index Obsidian vault for knowledge base search.

```python
result = cm.index_knowledge()
```

### recall_from_knowledge()

Search knowledge base (Obsidian vault).

```python
results = cm.recall_from_knowledge(
    query="Python design patterns",
    filters=None,
    limit=20,
)
```

### recall_all()

Search both memories and knowledge base.

```python
result = cm.recall_all(
    query="database",
    filters=None,
    limit=20,
)
```

### close()

Close database connections. Called automatically when using `with` statement.

```python
cm = CarryMem()
cm.close()
```

---

## Exceptions

```python
from memory_classification_engine import CarryMem
from memory_classification_engine.carrymem import StorageNotConfiguredError, KnowledgeNotConfiguredError

try:
    cm = CarryMem(storage=None)
    cm.recall_memories(query="test")
except StorageNotConfiguredError:
    print("Storage not configured")
```

---

## Storage Adapters

### SQLiteAdapter (Default)

```python
from memory_classification_engine import SQLiteAdapter

adapter = SQLiteAdapter(
    db_path=None,               # Custom path (default: ~/.carrymem/memories.db)
    namespace="default",
    enable_semantic_recall=True,
)
```

### ObsidianAdapter

```python
from memory_classification_engine import ObsidianAdapter

adapter = ObsidianAdapter(
    vault_path="/path/to/vault",
    db_path=None,
)
```

---

## Memory Types

| Type | Description | Default Tier |
|------|-------------|-------------|
| `user_preference` | Stated preferences | 2 (90 days) |
| `correction` | Corrections to AI | 2 (90 days) |
| `fact_declaration` | Facts about user | 3 (365 days) |
| `decision` | Made decisions | 3 (365 days) |
| `relationship` | Social/context info | 2 (90 days) |
| `task_pattern` | Work patterns | 2 (90 days) |
| `sentiment_marker` | Emotional reactions | 1 (24 hours) |

## Storage Tiers

| Tier | Name | Default TTL |
|------|------|-------------|
| 1 | Sensory | 24 hours |
| 2 | Procedural | 90 days |
| 3 | Episodic | 365 days |
| 4 | Semantic | Permanent |
