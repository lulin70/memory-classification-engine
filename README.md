# CarryMem — The Identity Layer for AI

**AI remembers who you are. Not just what you said.**

> Your portable AI identity layer — preferences, decisions, and corrections that follow you across models, tools, and devices.

CarryMem is a lightweight, zero-dependency AI memory system that stores **who you are** — your preferences, decisions, corrections — and makes that identity available to any AI tool. Switch from Cursor to Claude Code, from GPT to Claude, your AI always knows you.

**English** | [中文](docs/i18n/README-CN.md) | [日本語](docs/i18n/README-JP.md)

<p align="center">
  <img src="https://img.shields.io/badge/version-0.8.2-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-507%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-62.54%25-yellow" alt="Coverage">
  <img src="https://img.shields.io/badge/accuracy-90.6%25-green" alt="Accuracy">
  <img src="https://img.shields.io/badge/zero--dependencies-core-brightgreen" alt="Zero Deps">
</p>

---

## Why CarryMem?

### The Problem: AI Always Forgets Who You Are

Every new conversation, AI starts from zero:
- You prefer dark mode? **Forgotten.**
- You corrected it last time? **Forgotten.**
- You decided to use React? **Forgotten.**

Switch tools (Cursor → Windsurf), switch models (Claude → GPT) — start from scratch every time.

### The Solution: CarryMem Identity Layer

CarryMem doesn't just store text — it understands **who you are**:

```bash
$ carrymem whoami

  Who You Are (according to your AI)
  ==================================================

  Your Preferences:
    ⭐ I prefer dark mode for all editors
    ⭐ I use PostgreSQL for databases
    ⭐ I always use Python for data analysis

  Your Decisions:
    🎯 Let's use React for the frontend

  Your Corrections:
    🔧 The port should be 5432, not 3306

  Memory Profile:
    Total: 19 | Dominant: user_preference | Avg Confidence: 73%
```

---

## Quick Start

### Install

```bash
pip install -e .
```

### 5 Lines of Code

```python
from memory_classification_engine import CarryMem

cm = CarryMem()
cm.classify_and_remember("I prefer dark mode")        # Auto-classified as preference
cm.classify_and_remember("Use PostgreSQL not MySQL")   # Auto-classified as correction
memories = cm.recall_memories("database")              # Semantic recall
print(cm.build_system_prompt())                        # Inject into any AI
cm.close()
```

### CLI (19 commands)

```bash
carrymem init                           # Initialize
carrymem add "I prefer dark mode"       # Store a memory
carrymem add "test note" --force        # Force store (bypass classification)
carrymem list                           # List memories
carrymem search "theme"                 # Search memories
carrymem show <key>                     # View memory details
carrymem edit <key> "new content"       # Edit a memory
carrymem forget <key>                   # Delete a memory
carrymem whoami                         # Who your AI thinks you are
carrymem profile export identity.json   # Export your AI identity
carrymem stats                          # Memory statistics
carrymem check                          # Quality & conflict check
carrymem clean --expired --dry-run      # Preview cleanup
carrymem doctor                         # Diagnose installation
carrymem setup-mcp --tool cursor        # One-line MCP config
carrymem tui                            # Terminal UI
carrymem export backup.json             # Export all memories
carrymem import backup.json             # Import memories
carrymem version                        # Show version
```

---

## Core Features

### 1. Auto-Classification (7 Memory Types)

CarryMem automatically identifies what kind of information you're sharing:

| Type | Icon | Example |
|------|------|---------|
| `user_preference` | ⭐ | "I prefer dark mode" |
| `correction` | 🔧 | "No, I meant Python 3.11 not 3.10" |
| `decision` | 🎯 | "Let's use React for the frontend" |
| `fact_declaration` | 📌 | "I work at a startup in Tokyo" |
| `task_pattern` | 🔄 | "I always write tests first" |
| `contextual_observation` | 👁 | "The user seems frustrated" |
| `knowledge` | 📚 | "PostgreSQL uses MVCC" |

### 2. Semantic Recall (Cross-Language)

```python
cm.classify_and_remember("我偏好使用PostgreSQL")

# All of these find it:
cm.recall_memories("PostgreSQL")     # Exact match
cm.recall_memories("数据库")          # Synonym expansion
cm.recall_memories("Postgres")       # Spell correction
cm.recall_memories("データベース")    # Cross-language (Japanese)
```

### 3. Identity Layer (whoami)

```python
identity = cm.whoami()
print(identity["preferences"])   # ["I prefer dark mode", ...]
print(identity["decisions"])     # ["Let's use React", ...]
print(identity["corrections"])   # ["The port should be 5432", ...]
```

### 4. Importance Scoring & Lifecycle

Every memory has an importance score that evolves over time:

```
importance = confidence × type_weight × recency_factor × access_factor
```

- **30-day half-life decay** — old memories fade unless accessed
- **Access reinforcement** — frequently recalled memories stay fresh
- **Type weighting** — corrections (1.3x) > decisions (1.2x) > preferences (1.1x)

### 5. Quality Management

```bash
carrymem check                    # Check all
carrymem check --conflicts        # Detect contradictions
carrymem check --quality          # Find low-quality memories
carrymem check --expired          # Find expired memories
carrymem clean --expired --dry-run # Preview cleanup
```

### 6. Security & Reliability

| Feature | Description |
|---------|-------------|
| **Encryption** | AES-128 (Fernet) or HMAC-CTR fallback, zero-dep |
| **Backup** | Zero-downtime SQLite VACUUM INTO |
| **Audit Log** | Append-only operation history |
| **Version History** | Every edit tracked, rollback supported |
| **Input Validation** | SQL injection, XSS, path traversal protection |

### 7. MCP Integration (One-Line Setup)

```bash
# Configure for Cursor
carrymem setup-mcp --tool cursor

# Configure for Claude Code
carrymem setup-mcp --tool claude-code

# Configure for all
carrymem setup-mcp --tool all
```

12 MCP tools available: Core (3) · Storage (3) · Knowledge (3) · Profile (2) · Prompt (1)

### 8. Terminal UI

```bash
pip install textual
carrymem tui
```

Interactive terminal interface with sidebar filters, search, and add mode.

---

## Comparison

|  | CarryMem | Mem0 | OpenChronicle | ima |
|--|----------|------|---------------|-----|
| **Zero Dependencies** | ✅ SQLite only | ❌ Milvus needed | ✅ | ❌ Cloud |
| **Auto-Classification** | ✅ 7 types | ❌ | ❌ Manual | ❌ |
| **Identity Portrait** | ✅ whoami | ❌ | ❌ | ❌ |
| **CLI** | ✅ 19 commands | ❌ | ❌ | ❌ |
| **TUI** | ✅ textual | ❌ | ❌ | ✅ App |
| **Encryption** | ✅ Built-in | ❌ | ❌ | ❌ |
| **Version History** | ✅ Rollback | ❌ | ❌ | ❌ |
| **Conflict Detection** | ✅ Built-in | ❌ | ❌ | ❌ |
| **Data Ownership** | ✅ Local files | ⚠️ Cloud | ✅ Local | ❌ Cloud |
| **5-Line Integration** | ✅ | ❌ | ❌ | ❌ |
| **Cross-Language Recall** | ✅ EN/CN/JP | ❌ | ❌ | ❌ |

**Key Difference**: Other products store *what you read*. CarryMem stores *who you are*.

---

## Performance

| Metric | Value |
|--------|-------|
| Classification Accuracy | **90.6%** |
| F1 Score | **97.9%** |
| Zero-Cost Classification | **60%+** |
| Recall Latency (P50) | **~45ms** |
| Tests Passing | **507/507** |
| Test Coverage | **62.54%** |

---

## Architecture

```
User Input
    ↓
Auto-Classification (7 types, 4 tiers)
    ↓
Importance Scoring (confidence × type × recency × access)
    ↓
Smart Storage (SQLite + FTS5, dedup, TTL, encryption)
    ↓
Semantic Recall (FTS5 + synonyms + spell fix + cross-language)
    ↓
Context Injection (token budget, relevance ranking)
    ↓
AI Tool (Cursor / Claude Code / any MCP client)
```

**Three-Tier Classification**:
```
Rule Engine (60%+) → Pattern Analysis (30%) → Semantic (10%)
     ↓                      ↓                      ↓
 Zero cost            Near-zero cost          Token cost
```

---

## Advanced Usage

### Obsidian Knowledge Base

```python
from memory_classification_engine import CarryMem, ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()
results = cm.recall_from_knowledge("Python design patterns")
```

### Async API

```python
from memory_classification_engine import AsyncCarryMem

async with AsyncCarryMem() as cm:
    await cm.classify_and_remember("I prefer dark mode")
    memories = await cm.recall_memories("theme")
```

### JSON Adapter (No SQLite)

```python
from memory_classification_engine import CarryMem, JSONAdapter

cm = CarryMem(adapter=JSONAdapter("/path/to/memories.json"))
```

### Encryption

```python
cm = CarryMem(encryption_key="my-secret-key")
# All content encrypted at rest, decrypted on read
```

### Memory Versioning

```python
cm.update_memory(key, "Updated content")     # Creates version 2
history = cm.get_memory_history(key)          # [v1, v2]
cm.rollback_memory(key, version=1)            # Restore v1
```

### Export Identity for Other AIs

```python
# Export your AI identity
cm.export_profile(output_path="my_identity.json")

# On another device or AI tool
cm.import_memories(input_path="backup.json")
```

---

## Documentation

- [Quick Start Guide](docs/QUICK_START_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [User Stories](docs/USER_STORIES.md)
- [Roadmap](docs/ROADMAP.md)
- [Contributing](CONTRIBUTING.md)

---

## Who Is This For?

**Developers** — Building AI agents that need to remember users across sessions

**Power Users** — Want AI tools (Cursor, Claude Code, Windsurf) to remember them

**Teams** — Share organizational knowledge through shared memory namespaces

---

## Project Status

**Current Version**: v0.8.2
**Tests**: 507/507 passing
**Coverage**: 62.54%
**Accuracy**: 90.6%

**v0.8.x Changelog**:
- v0.8.2: Identity layer (whoami, profile export), competitive differentiation
- v0.8.1: User-perspective CLI improvements (show/edit/clean, color output, --force)
- v0.8.0: Enhanced CLI (19 commands), TUI, MCP setup, doctor, quality management
- v0.7.0: MCP HTTP/SSE, JSON adapter, async API
- v0.6.0: Encryption, backup, audit logging
- v0.5.0: Smart context injection, importance scoring, cache, merge, versioning

---

## Contributing

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd carrymem
pip install -e ".[dev]"
pytest
```

See [Contributing Guide](CONTRIBUTING.md) for details.

---

## License

MIT License — see [LICENSE](LICENSE)

---

**CarryMem — AI remembers who you are. Only you own the data.** 🚀
