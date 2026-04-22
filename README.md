# CarryMem

**Your portable AI memory layer.**

> Don't remember everything. Remember what matters.

CarryMem gives AI Agents a persistent, portable memory layer. It classifies conversations in real-time, stores what's worth remembering, and lets users take their memory anywhere — across models, across tools, across devices.

**AI remembers you. Not the other way around.**

<p align="center">
  <img src="https://img.shields.io/badge/version-0.3.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-114%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/MCP-3%2B3%2B3%2B2%2B1-blue" alt="MCP">
  <img src="https://img.shields.io/badge/Accuracy-90.6%25-green" alt="Accuracy">
</p>

---

## The Problem

Every time you start a new conversation with an AI Agent, it forgets you.

Your preferences, your corrections, your decisions — gone. You repeat yourself. The Agent recommends things you already rejected. Switch from Claude to GPT, from Cursor to Windsurf, from one MCP server to another, and it's like meeting a stranger again.

Existing solutions have three problems:

1. **Memory is locked in.** Most memory tools store your data in their own system. Change the tool, lose the memory.
2. **Everything is stored.** They dump entire conversations into vector databases and hope semantic search will figure it out. Expensive, noisy, and slow.
3. **No classification.** Without understanding what a message *is* (a preference? a correction? a casual remark?), retrieval is blind.

**60%+ of messages should NOT be stored.** But current systems either store everything (noise explosion) or store nothing (amnesia).

CarryMem solves all three.

---

## How It Works

```
User message → MCE Engine (classify) → Storage Layer (store) → Agent Context (retrieve)
```

### Step 1: Classify (MCE Engine)

Every user message flows through a three-layer classification funnel:

| Layer | Method | Cost | Coverage |
|-------|--------|------|----------|
| Rule matching | Regex + keywords | Zero | ~60% |
| Pattern analysis | NLP patterns | Near-zero | ~30% |
| Semantic inference | LLM (only when needed) | Token cost | <10% |

**60%+ of classifications happen with zero LLM cost.**

### Step 2: Classify into 7 Memory Types

| Type | Description | Example |
|------|-------------|---------|
| `user_preference` | Stated likes/dislikes | "I prefer dark mode" |
| `correction` | Explicit correction to AI | "No, I meant the Python version" |
| `fact_declaration` | Stated facts about the user | "I work at a startup in Tokyo" |
| `decision` | Made a choice | "Let's go with React" |
| `relationship` | Social/contextual info | "My teammate handles the backend" |
| `task_pattern` | Recurring workflow | "I always start with a README" |
| `sentiment_marker` | Emotional response to output | "This is exactly what I needed" |

### Step 3: Store with Priority Tiers

Not all memories are equal. CarryMem assigns a tier to every classified memory:

| Tier | Name | Default TTL | Description |
|------|------|-------------|-------------|
| **Tier 1** | Sensory | 24 hours | Temporary info, fast decay |
| **Tier 2** | Procedural | 90 days | Habits/preferences, medium retention |
| **Tier 3** | Episodic | 365 days | Important events, long retention |
| **Tier 4** | Semantic | Permanent | Core knowledge, never expires |

### Step 4: Retrieve When Needed

When a new conversation starts, CarryMem injects relevant memories into the Agent's context window. The Agent doesn't just respond — it *remembers*.

Retrieval priority: **Memories > Knowledge Base > External LLM**

---

## Quick Start

### Install

```bash
pip install carrymem
```

### Classify + Remember (3 lines)

```python
from carrymem import CarryMem

cm = CarryMem()  # Auto SQLite storage at ~/.carrymem/memories.db
result = cm.classify_and_remember("I prefer dark mode in my editor")
# → {"type": "user_preference", "confidence": 0.95, "stored": True}
```

### Declare Preferences

```python
# User proactively tells the AI about themselves
result = cm.declare("I prefer dark mode")
# → confidence=1.0, source_layer="declaration", always stored
```

### See What AI Remembers

```python
profile = cm.get_memory_profile()
# → {
#     "summary": "AI 记住了关于你的 12 条信息：5个偏好、3个纠正、2个决策",
#     "highlights": {"user_preference": ["dark mode", "PostgreSQL"], ...},
#     "stats": {"by_type": {...}, "confidence_avg": 0.92}
#   }
```

### Obsidian Knowledge Base

```python
from carrymem import CarryMem
from carrymem.adapters import ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()
results = cm.recall_from_knowledge("Python design patterns")
```

### Project-Level Isolation

```python
cm_alpha = CarryMem(namespace="project-alpha")
cm_beta = CarryMem(namespace="project-beta")

cm_alpha.declare("I prefer dark mode")   # Isolated in project-alpha
cm_beta.declare("I prefer light mode")    # Isolated in project-beta

# Cross-project search
result = cm_alpha.recall_all("PostgreSQL", namespaces=["project-alpha", "global"])
```

### Smart System Prompt

```python
# Generate context-aware system prompts for your Agent
prompt = cm.build_system_prompt(context="dark mode", language="en")
# → Includes relevant memories and knowledge with priority ordering
```

### Plugin Adapters

```python
# Load third-party adapters via entry_points
from carrymem.adapters import load_adapter, list_available_adapters

CustomAdapter = load_adapter("my_custom_adapter")
adapters = list_available_adapters()
# → {"sqlite": "...", "obsidian": "...", "my_custom_adapter": "... (plugin)"}
```

---

## MCP Server: 3+3+3+2+1 Optional Mode

| Group | Tools | Requirement |
|-------|-------|-------------|
| **Core (3)** | `classify_message`, `get_classification_schema`, `batch_classify` | Always available |
| **Storage (3)** | `classify_and_remember`, `recall_memories`, `forget_memory` | Storage adapter |
| **Knowledge (3)** | `index_knowledge`, `recall_from_knowledge`, `recall_all` | Knowledge adapter |
| **Profile (2)** | `declare_preference`, `get_memory_profile` | Storage adapter |
| **Prompt (1)** | `get_system_prompt` | Storage adapter |

### Setup

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

---

## Comparison

|  | CarryMem | Mem0 | LangMem | Zep |
|--|----------|------|---------|-----|
| **Classification** | Real-time, 7 types | None (full dump) | Via LLM chain | Post-hoc summary |
| **Storage** | Portable (SQLite/your DB) | Locked in Mem0 Cloud | Locked in LangChain | Locked in Zep |
| **LLM Cost** | 60%+ zero cost | Always-on embedding | Always-on LLM | Always-on LLM |
| **Memory Types** | 7 structured types | Unstructured | 3 types | 2 types |
| **Forgetting** | Active (4-tier TTL) | TTL only | Manual | TTL only |
| **Knowledge Base** | Obsidian (read-only) | No | No | No |
| **Active Declaration** | Yes (confidence=1.0) | No | No | No |
| **Project Isolation** | Namespace-based | No | No | No |
| **Open Source** | Full | Partial | Full | Partial |
| **Portability** | Your files, take anywhere | No | No | No |

**The key difference:** CarryMem's memory is yours. Not ours, not anyone else's. Switch models, switch tools, switch devices — your memory follows you.

---

## Performance

| Metric | Value |
|--------|-------|
| Classification Accuracy | **90.6%** |
| F1 Score | **97.9%** |
| Integration Tests | **32/32 passing** |
| LLM Call Ratio | **<10%** |
| P50 Latency (rule match) | ~45ms |

---

## Architecture

```
CarryMem (Main Class)
  ├── MCE Engine (3-layer classification funnel)
  │   ├── Rule Matcher (60%+ hit, zero cost)
  │   ├── Pattern Analyzer (30%+ hit, near-zero cost)
  │   └── Semantic Classifier (<10% hit, LLM fallback)
  ├── StorageAdapter (SQLite default, replaceable)
  │   ├── SQLiteAdapter: FTS5 + Dedup + TTL + Namespace
  │   ├── ObsidianAdapter: Markdown + Frontmatter + Wiki-links (read-only)
  │   └── Plugin Adapters: via entry_points
  ├── declare(): Active declaration (confidence=1.0)
  ├── get_memory_profile(): Structured memory profile
  ├── build_system_prompt(): Smart prompt generation (EN/CN/JP)
  └── MCP Server: 3+3+3+2+1 tools
```

---

## Project Structure

```
carrymem/
├── src/memory_classification_engine/
│   ├── carrymem.py              # CarryMem main class
│   ├── engine.py                # MCE core engine (slim)
│   ├── adapters/
│   │   ├── base.py              # StorageAdapter ABC + MemoryEntry + StoredMemory
│   │   ├── sqlite_adapter.py    # SQLite + FTS5 + Namespace
│   │   ├── obsidian_adapter.py  # Obsidian (read-only)
│   │   └── loader.py            # Plugin adapter loader
│   ├── layers/                  # 3-layer classification funnel
│   ├── coordinators/            # Classification pipeline
│   ├── utils/
│   │   ├── confirmation.py      # Confirmation detection (EN/CN/JP)
│   │   └── ...
│   └── integration/layer2_mcp/  # MCP Server
├── tests/                       # 32 tests passing
├── benchmarks/                  # MCE-Bench 180-case dataset
├── docs/
│   ├── consensus/               # Strategic decisions
│   ├── architecture/            # Architecture + Design docs
│   ├── planning/                # User stories + Status
│   └── testing/                 # Test plan
└── setup.py                     # carrymem v0.3.0
```

---

## Who Is This For?

**Developers** building AI Agents that need to remember users across sessions.

**Agent product teams** who want persistent memory without building classification logic from scratch.

**Power users** who want their AI tools to remember them, not the other way around.

---

## License

MIT
