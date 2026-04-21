# CarryMem — 随身记忆库

<p align="center">
  <strong>带着你的记忆走 — 让 AI Agent 记住用户</strong><br>
  <sub>CarryMem = <strong>MCE 分类引擎</strong>（核心壁垒）+ <strong>SQLite 默认存储</strong>（开箱即用）+ <strong>Obsidian 知识库</strong>（只读检索）+ <strong>可替换适配器</strong>（你的选择）</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.3.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-75%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/MCP-3%2B3%2B3%2B2-blue" alt="MCP">
  <img src="https://img.shields.io/badge/Accuracy-90.6%25-green" alt="Accuracy">
</p>

<p align="center">
  <a href="./ROADMAP.md">Roadmap</a> ·
  <a href="./docs/architecture/CARRYMEM_ARCHITECTURE_v4.md">Architecture</a> ·
  <a href="./docs/architecture/CARRYMEM_DESIGN_v4.md">Design</a> ·
  <a href="./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md">Consensus</a>
</p>

---

## The Problem: Nobody Classifies Before Storing

Every AI memory system has the same blind spot.

**Supermemory** receives a message → stores it. No classification.
**Mem0** receives a message → stores it. No classification.
**Claude Code CLAUDE.md** → you manually decide what to write. No structure.

They all answer **"how to store"** but never **"what's worth storing"**.

**60%+ of messages should NOT be stored.** But current systems either store everything (noise explosion) or store nothing (amnesia).

**MCE is the missing pre-filter.** Now with CarryMem, it also provides default storage, knowledge base retrieval, and user declaration — so your Agent can remember users out of the box.

---

## Quick Start

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

### Declare Preferences (v0.8)

```python
# User proactively tells the AI about themselves
result = cm.declare("I prefer dark mode")
# → confidence=1.0, source_layer="declaration", always stored
```

### See What AI Remembers (v0.8)

```python
profile = cm.get_memory_profile()
# → {
#     "summary": "AI 记住了关于你的 12 条信息：5个偏好、3个纠正、2个决策",
#     "highlights": {"user_preference": ["dark mode", "PostgreSQL"], ...},
#     "stats": {"by_type": {...}, "confidence_avg": 0.92}
#   }
```

### Obsidian Knowledge Base (v0.7)

```python
from carrymem import CarryMem
from carrymem.adapters import ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()
results = cm.recall_from_knowledge("Python design patterns")
```

### Project-Level Isolation (v0.9)

```python
cm_alpha = CarryMem(namespace="project-alpha")
cm_beta = CarryMem(namespace="project-beta")

cm_alpha.declare("I prefer dark mode")   # Isolated in project-alpha
cm_beta.declare("I prefer light mode")    # Isolated in project-beta

# Cross-project search
result = cm_alpha.recall_all("PostgreSQL", namespaces=["project-alpha", "global"])
```

---

## Why Classification Matters

### The 60% Filter

MCE's three-layer pipeline filters out 60%+ of messages before any expensive processing:

```
Layer 1: Rule Match     → 60%+ filtered, zero cost (regex + keywords)
Layer 2: Pattern Analysis → 30%+ classified, still zero LLM
Layer 3: Semantic (LLM)  → <10% reach here, LLM fallback only
```

**Cost per 1,000 messages:**

| Approach | LLM Calls | Cost |
|----------|-----------|------|
| Send everything to LLM | 1,000 | $0.50 - $2.00 |
| **MCE (Layer 1 + 2 first)** | **<100** | **$0.05 - $0.20** |

### 7 Types > 1 Bucket

| Type | Example | Why it matters |
|------|---------|---------------|
| **user_preference** | "I prefer spaces over tabs" | Affects ALL future code generation |
| **correction** | "No, do it like this instead" | Must override previous fact/decision |
| **fact_declaration** | "We have 100 employees" | Verifiable truth, rarely changes |
| **decision** | "Let's go with Redis for caching" | Explains WHY architecture looks this way |
| **relationship** | "Alice handles backend" | Enables role-aware responses |
| **task_pattern** | "Always test before deploy" | Automatable workflow rules |
| **sentiment_marker** | "This workflow is frustrating" | Signals process pain points |

---

## MCP Server: 3+3+3+2 Optional Mode

| Group | Tools | Requirement |
|-------|-------|-------------|
| **Core (3)** | classify_message, get_classification_schema, batch_classify | Always available |
| **Storage (3)** | classify_and_remember, recall_memories, forget_memory | Storage adapter |
| **Knowledge (3)** | index_knowledge, recall_from_knowledge, recall_all | Knowledge adapter |
| **Profile (2)** | declare_preference, get_memory_profile | Storage adapter |

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

## Retrieval Priority

```
recall_all(query, namespaces=[...])
  │
  ├─ Layer 1a: Current namespace memories (project-specific)
  ├─ Layer 1b: Global namespace memories (user-level preferences)
  ├─ Layer 2:  Knowledge base (Obsidian vault)
  └─ Layer 3:  External LLM (Agent decides)
```

---

## Performance

| Metric | Value |
|--------|-------|
| Classification Accuracy | **90.6%** |
| F1 Score | **97.9%** |
| Integration Tests | **75/75 passing** |
| LLM Call Ratio | **<10%** |
| P50 Latency (rule match) | ~45ms |

---

## Architecture

```
CarryMem (Main Class)
  ├── MCE Engine (3-layer classification funnel)
  ├── StorageAdapter (SQLite default, replaceable)
  │   ├── SQLiteAdapter: FTS5 + Dedup + TTL + Namespace
  │   └── ObsidianAdapter: Markdown + Frontmatter + Wiki-links (read-only)
  ├── declare(): Active declaration (confidence=1.0)
  ├── get_memory_profile(): Structured memory profile
  └── MCP Server: 3+3+3+2 tools
```

---

## Project Structure

```
carrymem/
├── src/memory_classification_engine/
│   ├── carrymem.py              # CarryMem main class
│   ├── engine.py                # MCE core engine
│   ├── adapters/
│   │   ├── base.py              # StorageAdapter ABC + MemoryEntry + StoredMemory
│   │   ├── sqlite_adapter.py    # SQLite + FTS5 + Namespace
│   │   └── obsidian_adapter.py  # Obsidian (read-only)
│   ├── layers/                  # 3-layer classification funnel
│   ├── coordinators/            # Classification pipeline
│   ├── utils/
│   │   ├── confirmation.py      # Confirmation detection (EN/CN/JP)
│   │   └── ...
│   └── integration/layer2_mcp/  # MCP Server
├── tests/                       # 75 tests passing
├── benchmarks/                  # Accuracy benchmark
├── docs/
│   ├── consensus/               # Strategic decisions
│   ├── architecture/            # Architecture + Design docs
│   ├── planning/                # User stories + Migration plan
│   └── testing/                 # Test plan
└── setup.py                     # carrymem v0.3.0
```

---

## License

MIT
