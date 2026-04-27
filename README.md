# CarryMem

**AI remembers you. Not the other way around.**

> Your portable AI memory layer — across models, tools, and devices

CarryMem is a portable AI memory system that lets AI assistants remember your preferences, corrections, and decisions. Switch tools without losing memories, switch devices and take them with you.

**English** | [中文](docs/i18n/README-CN.md) | [日本語](docs/i18n/README-JP.md)

<p align="center">
  <img src="https://img.shields.io/badge/version-0.7.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-332%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/accuracy-90.6%25-green" alt="Accuracy">
  <img src="https://img.shields.io/badge/zero--cost-60%25%2B-brightgreen" alt="Zero Cost">
</p>

---

## 🎯 Why CarryMem?

### The Problem: AI Always Forgets You

Every new conversation, AI acts like it's meeting you for the first time:
- ❌ Your preferences? Forgotten
- ❌ Your corrections? Forgotten
- ❌ Your decisions? Forgotten

Switch tools (Cursor → Windsurf), switch models (Claude → GPT), start from scratch every time.

### The Solution: CarryMem

✅ **AI Remembers You Automatically** — Preferences, corrections, decisions auto-classified and stored
✅ **Memories Are Portable** — Export/import, switch tools without losing data
✅ **60%+ Zero Cost** — Smart classification, no token waste
✅ **5-Minute Setup** — Zero config, works out of the box

---

## ⚡ Quick Start

### Install

```bash
pip install carrymem
```

### First Memory (1 minute)

```python
from memory_classification_engine import CarryMem

with CarryMem() as cm:
    # AI automatically classifies and stores your preferences
    cm.classify_and_remember("I prefer dark mode")
    cm.classify_and_remember("I use PostgreSQL for databases")
    cm.classify_and_remember("I work at a startup in Tokyo")

    # Recall memories
    memories = cm.recall_memories(query="database")
    for mem in memories:
        print(f"{mem['type']}: {mem['content']}")
```

That's it! 🎉 CarryMem auto-creates the database at `~/.carrymem/memories.db`.

---

## 💡 Core Features

### 1. Auto-Classification (7 Memory Types)

CarryMem automatically identifies message types, storing only valuable information:

```python
cm.classify_and_remember("I prefer dark mode")
# → type: user_preference, confidence: 0.95

cm.classify_and_remember("No, I meant Python 3.11, not 3.10")
# → type: correction, confidence: 0.98

cm.classify_and_remember("Let's use React for the frontend")
# → type: decision, confidence: 0.92
```

**7 Memory Types**: `user_preference` · `correction` · `fact_declaration` · `decision` · `relationship` · `task_pattern` · `sentiment_marker`

### 2. Semantic Recall (v0.4.0+)

```python
# Store in Chinese, query in English — works cross-language!
cm.classify_and_remember("我偏好使用PostgreSQL")

# All of these find the memory:
memories = cm.recall_memories(query="PostgreSQL")      # ✅ Exact match
memories = cm.recall_memories(query="数据库")            # ✅ Synonym expansion
memories = cm.recall_memories(query="Postgres")          # ✅ Spell correction
memories = cm.recall_memories(query="データベース")      # ✅ Cross-language (Japanese)
```

**Features**: Synonym expansion · Spell correction · Cross-language mapping (CN/EN/JP) · Zero external dependencies

### 3. Active Declaration

```python
cm.declare("I prefer PostgreSQL over MySQL")
# → confidence=1.0, guaranteed to be remembered
```

### 4. Memory Profile

```python
profile = cm.get_memory_profile()
print(profile['summary'])
# → "AI remembers 12 things about you: 5 preferences, 3 corrections, 2 decisions"
```

### 5. Export & Import (Portability)

```python
# Export memories — they belong to you
cm.export_memories(output_path="my_memories.json")

# Import on new device
with CarryMem() as cm2:
    cm2.import_memories(input_path="my_memories.json")
    # All memories restored!
```

---

## 🎨 Real-World Use Cases

### Use Case 1: Code Assistant Remembers Your Style

```python
with CarryMem() as cm:
    cm.classify_and_remember("I prefer using type hints in Python")
    cm.classify_and_remember("I like to use dataclasses instead of dicts")

    # Next conversation, AI automatically knows your preferences
    memories = cm.recall_memories(query="Python coding style")
```

### Use Case 2: Cross-Tool Usage

```python
# In Cursor
with CarryMem(namespace="cursor") as cm_cursor:
    cm_cursor.classify_and_remember("I prefer dark mode")

# In Windsurf, use same memories
with CarryMem(namespace="cursor") as cm_windsurf:
    memories = cm_windsurf.recall_memories(query="theme")  # Found!
```

### Use Case 3: Project Isolation

```python
# Project A
with CarryMem(namespace="project-a") as cm_a:
    cm_a.classify_and_remember("Use React for frontend")

# Project B — no interference
with CarryMem(namespace="project-b") as cm_b:
    cm_b.classify_and_remember("Use Vue for frontend")
```

---

## 🔥 Why CarryMem Is Better

|  | CarryMem | Mem0 | LangMem | Zep |
|--|----------|------|---------|-----|
| **Auto-Classification** | ✅ 7 types | ❌ Store all | ⚠️ Needs LLM | ⚠️ Post-summary |
| **Portability** | ✅ Your files | ❌ Locked in cloud | ❌ Locked in tool | ❌ Locked in service |
| **Cost** | ✅ 60%+ zero cost | ❌ Always calls | ❌ Always calls | ❌ Always calls |
| **Project Isolation** | ✅ Namespace | ❌ No | ❌ No | ❌ No |
| **Knowledge Base** | ✅ Obsidian | ❌ No | ❌ No | ❌ No |
| **Open Source** | ✅ Fully open | ⚠️ Partial | ✅ Fully open | ⚠️ Partial |

**Key Difference**: CarryMem's memories belong to you. Switch models, tools, devices — memories follow you.

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Classification Accuracy | **90.6%** |
| F1 Score | **97.9%** |
| Zero-Cost Classification | **60%+** |
| Recall Latency (P50) | **~45ms** |
| Tests Passing | **332/332** |

---

## 🏗️ How It Works

### Three-Tier Classification Strategy

```
User Input → Rule Engine (60%+) → Pattern Analysis (30%) → Semantic (10%)
               ↓                        ↓                         ↓
          Zero cost              Near-zero cost             Token cost
          High speed             Medium speed               Low speed
```

**60%+ classifications don't need LLM calls!**

### Data Flow

```
1. User Input
   ↓
2. Auto-Classification (7 types)
   ↓
3. Smart Storage (dedup + TTL)
   ↓
4. Semantic Recall (FTS5 + synonyms)
   ↓
5. Return Relevant Memories
```

---

## 🌟 Advanced Features

### Obsidian Knowledge Base Integration

```python
from memory_classification_engine import CarryMem, ObsidianAdapter

with CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault")) as cm:
    cm.index_knowledge()
    results = cm.recall_from_knowledge("Python design patterns")
```

### MCP Server

Add to your MCP client config (e.g. Claude Code, Cursor):

```json
{
  "mcpServers": {
    "carrymem": {
      "command": "python3",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
      "env": {}
    }
  }
}
```

**12 Tools**: Core (3) · Storage (3) · Knowledge (3) · Profile (2) · Prompt (1)

---

## 📚 Documentation

- 📖 [Quick Start Guide](docs/QUICK_START_GUIDE.md)
- 🏗️ [Architecture](docs/ARCHITECTURE.md)
- 📋 [API Reference](docs/API_REFERENCE.md)
- 🎯 [User Stories](docs/USER_STORIES.md)
- 🗺️ [Roadmap](docs/guides/ROADMAP.md)
- 🤝 [Contributing](CONTRIBUTING.md)

---

## 🎯 Who Is This For?

**Developers** — Building AI Agents that need to remember users

**Product Teams** — Need persistent memory without building classification logic from scratch

**Power Users** — Want AI tools to remember them, not the other way around

---

## 🚦 Project Status

**Current Version**: v0.7.0
**Tests**: 332/332 passing
**Accuracy**: 90.6%

---

## 🤝 Contributing

We welcome contributions! See [Contributing Guide](CONTRIBUTING.md).

### Development Setup

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd carrymem
pip install -e ".[dev]"
pytest
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

**Start using CarryMem and let AI remember you!** 🚀

```bash
pip install carrymem
```
