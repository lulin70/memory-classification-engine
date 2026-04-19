# MCE Storage Strategy Guide

**Version**: 1.0.0
**Last Updated**: 2026-04-19
**Status**: v0.2.0 companion document (will be expanded in v0.3.0)

---

## Core Principle: MCE Classifies, Doesn't Store

MCE is a **memory classification middleware**, not a memory storage system.

```
Your AI Agent / Claude Code
        │  (raw conversation messages)
        ▼
┌───────────────────────────────┐
│     MCE (Classification)      │
│                               │
│   Input:  "I prefer double    │
│           quotes in Python"   │
│                               │
│   Output: {                   │
│     should_remember: true,    │
│     type: "user_preference", │
│     confidence: 0.95,         │
│     tier: 2,                  │
│     suggested_action: "store" │
│   }                          │
└──────────────┬────────────────┘
               │  MemoryEntry (JSON)
               ▼
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 [Choose your  [Choose your  [Or build
  downstream]   downstream]   your own]
```

**Why this architecture?**
- Supermemory has YC backing + Cloudflare infrastructure + Benchmark #1 rankings — you can't beat their storage
- Mem0 has 18k GitHub Stars + vector+graph hybrid storage — they've optimized storage for years
- MCE's strength is **classification quality** (7 types, 3-layer pipeline, 60%+ zero LLM cost)
- Focus on what you're best at; let specialists handle storage

---

## Recommended Downstream Options

### Option A: Supermemory (Cloud)

**Best for**: Users who want the best retrieval quality with zero infrastructure management

| Attribute | Value |
|-----------|-------|
| Type | Cloud SaaS |
| Strengths | LongMemEval #1, auto-forgetting, user profiling |
| Data location | Their servers (not local) |
| MCP support | Yes (`npx install-mcp ...`) |
| Free tier | Available |

**Integration pattern**:

```python
# Step 1: MCE classifies
from memory_classification_engine import MemoryClassificationEngine

mce = MemoryClassificationEngine()
result = mce.process_message("I prefer double quotes")
entry = result['matches'][0]  # {type, confidence, tier, content}

# Step 2: Store to Supermemory
# (using Supermemory SDK or their MCP `memory` tool)
supermemory.store({
    "content": entry['content'],
    "tags": [entry['type']],           # user_preference
    "metadata": {"mce_confidence": entry['confidence'], "mce_tier": entry['tier']}
})
```

**MCE type → Supermemory mapping**:

| MCE Type | Supermemory Tag/Category |
|----------|-------------------------|
| `user_preference` | `preference` |
| `correction` | `correction` |
| `fact_declaration` | `fact` |
| `decision` | `decision` |
| `relationship` | `relation` |
| `task_pattern` | `pattern` |
| `sentiment_marker` | `sentiment` |

---

### Option B: Mem0 (Self-hosted)

**Best for**: Users who want self-hosted storage with vector + graph hybrid retrieval

| Attribute | Value |
|-----------|-------|
| Type | Self-hosted (or cloud) |
| Strengths | Graph memory, conversation summarization, 43.6k Stars |
| Data location | Your server (self-hosted) |
| MCP support | No (SDK only) |
| License | Apache 2.0 |

**Integration pattern**:

```python
from mem0 import Memory

mce = MemoryClassificationEngine()
mem0 = Memory()

result = mce.process_message("We decided to use Redis for caching")
entry = result['matches'][0]

mem0.add(
    f"[{entry['type']}] {entry['content']}",
    user_id="default",
    metadata={"mce_type": entry['type'], "mce_tier": entry['tier']}
)
```

**MCE type → Mem0 mapping**:

| MCE Type | Mem0 Category |
|----------|--------------|
| `user_preference` | `user_profile` |
| `correction` | `correction` |
| `fact_declaration` | `fact` |
| `decision` | `decision` |
| `relationship` | `relationship` |
| `task_pattern` | `workflow` |
| `sentiment_marker` | `emotion` |

---

### Option C: Obsidian (Local Markdown)

**Best for**: Knowledge workers who want human-readable, git-trackable memory files

| Attribute | Value |
|-----------|-------|
| Type | Local Markdown files |
| Strengths | Human-readable, version-controlled, plugin ecosystem |
| Data location | Your disk (Obsidian vault) |
| MCP support | Via community plugins |
| Cost | Free |

**Integration pattern**:

```python
import os
from datetime import datetime

mce = MemoryClassificationEngine()
vault_path = "~/my-obsidian-vault"

result = mce.process_message("Alice owns backend, Bob does frontend")
entry = result['matches'][0]

# Map MCE type to Obsidian folder/tag
folder_map = {
    "user_preferences": "10-Preferences",
    "corrections": "20-Corrections",
    "facts": "30-Facts",
    "decisions": "40-Decisions",
    "relationships": "50-Relationships",
    "patterns": "60-Patterns",
    "sentiments": "70-Sentiments"
}

folder = folder_map.get(entry['type'] + 's', '00-Inbox')
os.makedirs(os.path.join(vault_path, folder), exist_ok=True)

timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
filename = os.path.join(vault_path, folder, f"{timestamp}_{entry['type']}.md")

with open(filename, 'w') as f:
    f.write(f"# {entry['type'].replace('_', ' ').title()}\n\n")
    f.write(f"{entry['content']}\n\n")
    f.write(f"---\n")
    f.write(f"- **Source**: MCE classify\n")
    f.write(f"- **Confidence**: {entry.get('confidence', 0):.2f}\n")
    f.write(f"- **Tier**: {entry.get('tier', '?')}\n")
    f.write(f"- **Date**: {timestamp}\n")
    f.write(f"- **Tags**: #{entry['type']}\n")
```

**Resulting file structure**:
```
my-obsidian-vault/
├── 10-Preferences/
│   └── 20260419103000_user_preference.md
├── 40-Decisions/
│   └── 20260419104500_decision.md
└── 50-Relationships/
    └── 20260419110000_relationship.md
```

---

### Option D: Custom StorageAdapter (Advanced)

**Best for**: Users with specialized storage needs (proprietary DB, internal systems, etc.)

In v0.3.0, MCE will provide a `StorageAdapter` abstract base class:

```python
from memory_classification_engine.adapters.base import StorageAdapter, MemoryEntry

class MyCustomAdapter(StorageAdapter):
    """Example: Store to a custom PostgreSQL database."""
    
    @property
    def name(self) -> str:
        return "my_postgres"
    
    @property
    def capabilities(self) -> dict:
        return {"vector_search": True, "graph": False, "ttl": True}
    
    def store(self, entry: MemoryEntry) -> str:
        # Insert into your database
        sql = """
            INSERT INTO memories (type, content, confidence, tier, source_layer)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        cursor.execute(sql, (
            entry.type, entry.content, entry.confidence,
            entry.tier, entry.source_layer
        ))
        return cursor.fetchone()[0]
    
    def retrieve(self, query: str, limit: int = 20) -> list:
        # Query your database
        ...
    
    def delete(self, storage_id: str) -> bool:
        ...
    
    def get_stats(self) -> dict:
        ...
```

> **Note**: StorageAdapter ABC will be available in v0.3.0. For v0.2.0, process MCE output manually as shown in Options A-C.

---

## Quick Start: Which Option Should I Choose?

| Your Situation | Recommended Option |
|---------------|-------------------|
| "I want it to just work, no infra" | **A: Supermemory** (cloud, 30s setup) |
| "I need self-hosted, good search" | **B: Mem0** (vector+graph, pip install) |
| "I'm a knowledge worker, want readable notes" | **C: Obsidian** (markdown, git-friendly) |
| "I have my own database/system" | **D: Custom Adapter** (v0.3.0) |
| "I just want to try MCE first" | **None needed** — use `classify_memory` output directly |

---

## Migration Guide: From Built-in Storage to Downstream

If you have been using MCE's built-in storage (v0.2.0 or earlier):

1. **Export your data** (before v0.3.0):
   ```python
   # Use the deprecated export_memories tool while it still exists
   data = engine.export_memories(format="json")
   ```

2. **Choose a downstream** from Options A-D above

3. **Import to downstream** using the exported JSON

4. **Update your pipeline** to use MCE for classification only

> A migration script (`scripts/mce_migrate.py`) will be provided in v0.3.0.

---

## FAQ

**Q: Does this mean MCE can't store anything at all?**

A: In v0.2.0, MCE still includes built-in SQLite storage (via the deprecated MCP tools). Starting from v0.3.0, storage tools will be removed from the MCP interface. You can still use the Python API's `process_message()` which internally uses working memory — but persistent storage should go through a downstream system.

**Q: What if I don't want to set up any downstream?**

A: That's fine! You can use MCE purely as a classification service. Call `classify_message`, get the JSON result, and decide what to do with it (log it, print it, store it in a text file, or ignore it). MCE's value is in the *classification decision*, not the persistence.

**Q: Is my data safe with MCE?**

A: MCE runs entirely locally on your machine. No data is sent to external servers during classification. Where your classified data goes next depends on which downstream you choose — that's under *your* control.

**Q: Will there be official adapters for Supermemory/Mem0/Obsidian?**

A: Yes. The roadmap (v0.3.1 - v0.3.3) includes official adapter implementations for these three systems. Community contributions for other backends are welcome.
