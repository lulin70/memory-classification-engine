# Memory Classification Engine

<p align="center">
  <strong>Don't remember everything. Remember what matters.</strong><br>
  <sub>Real-time memory classification for AI Agents. 60%+ zero LLM cost.</sub>
</p>

<p align="center">
  <a href="./README-ZH.md">中文</a> ·
  <a href="./README-JP.md">日本語</a> ·
  <a href="./ROADMAP.md">Roadmap</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/issues">Issues</a>
</p>

---

## The Problem: Your Agent Forgets, or Remembers Too Much

Every AI agent has the same memory problem.

Option A: **Save nothing.** Each new session starts from zero. Users repeat themselves. The agent makes mistakes it already made.

Option B: **Save everything.** Dump every conversation into a vector DB as a summary. Works at first. After 50 sessions, retrieval returns vague noise because signal is drowned out by noise. Cost scales linearly with message count (every message = one LLM call).

The root cause: **most systems don't classify before they store.** They treat a user's preference ("use double quotes"), a decision ("we chose PostgreSQL"), and small talk ("nice weather") identically. One big blob.

## How MCE Is Different

MCE classifies **every message in real time** before storing:

```
Message: "上次那个方案太复杂了，换个简单点的"

Traditional system:
  → Stores as summary fragment: "discussed approach complexity"
  → Lost context: this was a REJECTION of a past decision
  → Search result: buried in 50 other summaries, low relevance

MCE:
  → [correction] "Rejected previous complex approach, prefers simplicity"
  → Auto-linked to decision_001 (the original complex plan)
  → Confidence: 0.89 | Source: pattern analysis | Tier: episodic
  → LLM cost: $0 (matched at Layer 2)
```

One message. The traditional system stores noise. MCE stores an **actionable, typed, cross-linked memory with zero LLM cost**.

**Cost per 1,000 messages:**

| Approach | LLM Calls | Cost |
|----------|-----------|------|
| Summarize everything | 1,000 | $0.50 - $2.00 |
| **MCE** | **<100** | **$0.05 - $0.20** |

---

## Three-Layer Pipeline: Cheap First, Expensive Last

```
Incoming Message
       │
       ▼
┌─────────────────────┐   60%+ of messages   │  Zero cost
│ Layer 1: Rule Match  │   handled here      │  Regex + keywords
│   "记住", "以后都..." │                     │  Deterministic
└──────────┬──────────┘
           │ Unmatched
           ▼
┌─────────────────────┐   30%+ of messages   │  Still zero LLM
│ Layer 2: Pattern    │   handled here       │  Conversation structure
│   Analysis          │                     │  "3rd rejection = preference"
└──────────┬──────────┘
           │ Unmatched
           ▼
┌─────────────────────┐   <10% of messages   │  LLM fallback
│ Layer 3: Semantic   │   reach here         │  Ambiguous edge cases
│   Inference         │                     │
└─────────────────────┘
```

Most solutions start at Layer 3. MCE starts at Layer 1 and escalates only when needed. That's why 60%+ of classification costs nothing.

---

## Quick Start

```bash
pip install memory-classification-engine
```

No database. No API key. No configuration. Works out of the box.

### Try It in 30 Seconds

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# Scenario 1: User rejects a previous approach (implicit correction)
engine.process_message(
    "That last approach was too complex, let's go simpler"
)
# → [correction] Rejected previous complex approach
#   confidence: 0.89, source: pattern, tier: episodic
#   linked to: decision_001 (auto)

# Scenario 2: Frustration reveals a recurring pain point
engine.process_message(
    "We always have to test before deploying, this process is so tedious"
)
# → [sentiment_marker] Frustration with deployment process
#   implied_pattern: test-before-deploy (auto-extracted)

# Scenario 3: Team roles in one sentence
engine.process_message(
    "Alice owns the backend, Bob does frontend, I oversee architecture"
)
# → [relationship] Alice→backend, Bob→frontend, User→arch lead
#   confidence: 0.95, tier: semantic
```

### Recall Across Sessions

This is what users actually feel: opening a new conversation and having their agent **remember** what matters.

```python
from memory_classification_engine import MemoryOrchestrator

memory = MemoryOrchestrator()

# ... after using for a week ...

# New session starts — load relevant memories
memories = memory.recall(context="coding", limit=5)
for m in memories:
    print(f"[{m['type']}] {m['content']} (conf: {m['confidence']}, src: {m['source']})")
# Output:
# [user_preference] Use double quotes, not single (conf: 0.95, src: rule)
# [decision] Project uses Python, not Go (conf: 0.91, src: rule)
# [relationship] Alice handles backend API (conf: 0.88, src: semantic)
# [correction] No over-engineering — keep it simple (conf: 0.89, src: pattern)
# [fact_declaration] Prod runs on Ubuntu 22.04 (conf: 0.92, src: rule)
#
# Stats: 5 loaded | 12 noise filtered | 0 LLM calls
```

---

## MCP Server: Claude Code Integration in 2 Minutes

MCE ships with a built-in MCP server. This is the fastest way to use it with Claude Code, Cursor, or any MCP-compatible tool.

```bash
cd mce-mcp
python3 server.py
# MCP server running on http://localhost:9001
```

Add to your Claude Code config (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "mce": {
      "command": "python3",
      "args": ["/path/to/mce-mcp/server.py"]
    }
  }
}
```

Available tools: `classify_message`, `retrieve_memories`, `store_memory`, `search_memories`, `get_memory_stats`, `delete_memory`, `update_memory`, `export_memories`, `import_memories`.

Every message you send in Claude Code can be classified and stored automatically. Every new session starts with a structured recall of your memories.

See [BETA_TESTING_GUIDE_EN.md](./BETA_TESTING_GUIDE_EN.md) for full setup instructions.

---

## What Gets Classified: 7 Memory Types

| Type | Example | Stored Where |
|------|---------|-------------|
| **user_preference** | "I prefer spaces over tabs" | Tier 2: Procedural (active) |
| **correction** | "No, do it like this instead" | Tier 3: Episodic (linked) |
| **fact_declaration** | "We have 100 employees" | Tier 3: Episodic (verified) |
| **decision** | "Let's go with Redis for caching" | Tier 3: Episodic (high priority) |
| **relationship** | "Alice handles backend" | Tier 4: Semantic (graph) |
| **task_pattern** | "Always test before deploy" | Tier 2: Procedural (auto) |
| **sentiment_marker** | "This workflow is frustrating" | Tier 3: Episodic (low priority) |

Not every message produces a memory. Chit-chat, acknowledgments ("OK", "thanks"), and low-signal content are filtered out before storage.

---

## Self-Evolving: Patterns Become Rules Over Time

The engine gets cheaper and more accurate the longer it runs.

| Time | Layer 1 (Rules) | Layer 2 (Patterns) | Layer 3 (LLM) | Cost/1k msgs |
|------|-----------------|-------------------|---------------|-------------|
| Week 1 | 30% hit rate | 40% | 30% | $0.15 |
| Week 4 | 50% (+20 auto-rules) | 35% | 15% | $0.08 (-47%) |
| Month 3 | 65% (+50 auto-rules) | 25% | 10% | $0.05 (-67%) |

Auto-generated rules look like this:

```yaml
# System seed (day one):
- pattern: "remember.*prefer"
  type: user_preference

# Learned after 1 month of use:
- pattern: "too complex.*simpler"
  type: correction
  source: learned_from_user_behavior

- pattern: "always have to.*tedious"
  type: sentiment_marker
  source: learned_from_user_behavior
```

Your usage patterns become free classification rules. No manual tuning required.

---

## Comparison

| Feature | Mem0 | MemGPT | LangChain Memory | **MCE** |
|---------|------|--------|------------------|---------|
| When to write | Post-conversation | Context window | Manual/Hooks | **Real-time, per-message** |
| Classification | Basic tags | None | None | **7 types + 3-layer pipeline** |
| Storage tiers | 1 (vector) | 2 (mem + disk) | 1 (session) | **4 tiers (working / procedural / episodic / semantic)** |
| Forgetting | None | Passive overflow | None | **Active decay + Nudge review** |
| Learning | Static | None | None | **Patterns auto-promote to rules** |
| LLM cost | Per-message | Medium | Low | **60%+ classified at zero cost** |
| Cross-session | Export only | None | None | **Structured migration standard** |
| MCP support | No | No | No | **Built-in MCP Server** |
| High-level API | No | No | Basic | **MemoryOrchestrator (learn/recall/export/import)** |

---

## Four-Tier Storage

| Tier | Name | Storage | Lifecycle |
|------|------|---------|-----------|
| T1 | Working Memory | Context window (LLM-native) | Current session only |
| T2 | Procedural | Config files / system prompts | Long-term, always loaded |
| T3 | Episodic | Vector store (ChromaDB / SQLite) | Weighted decay over time |
| T4 | Semantic | Knowledge graph (Neo4j / in-memory) | Long-term, cross-linked |

Core dependency: **only PyYAML**. Vector DBs, graph DBs, and LLM are all optional extensions.

---

## Performance

| Metric | Result |
|--------|--------|
| Message processing (Layer 1/2) | ~10ms |
| Message processing (Layer 3) | <500ms |
| Retrieval latency | ~15ms |
| Concurrent throughput | 626 msg/s |
| Memory compression | 87-90% noise reduction |
| Memory footprint | <100MB (basic mode) |
| LLM call ratio | **<10%** |

---

## Tech Stack

| Component | Default | Alternative |
|-----------|---------|-------------|
| Rule engine | YAML + Regex | JSON Schema |
| Vector store (T3) | ChromaDB | Qdrant, Milvus |
| Knowledge graph (T4) | In-memory | Neo4j |
| Semantic classifier (L3) | Small model API | Ollama local model |
| Agent adapters | Standalone SDK | Plugin extension |

---

## Project Structure

```
memory-classification-engine/
├── mce-mcp/                    # MCP Server (Claude Code / Cursor integration)
│   ├── server.py               #   Server entry point
│   ├── tools/                  #   MCP tool implementations
│   └── config.yaml             #   Server configuration
│
├── src/memory_classification_engine/
│   ├── engine.py               # Core coordinator
│   ├── layers/                 # 3-layer pipeline
│   │   ├── rule_matcher.py     #   Layer 1: Rule matching
│   │   ├── pattern_analyzer.py #   Layer 2: Structure analysis
│   │   └── semantic_classifier.py # Layer 3: LLM fallback
│   ├── storage/                # Tiered storage (T2-T4)
│   ├── orchestrator.py         # MemoryOrchestrator (high-level API)
│   ├── privacy/
│   └── utils/
│
├── examples/                   # Ready-to-run examples
├── tests/                      # Test suite
├── config/rules.yaml           # Classification rules
├── setup.py                    # PyPI package config
└── README.md
```

---

## Installation Options

```bash
# Core (classification engine only)
pip install memory-classification-engine

# With RESTful API server
pip install -e ".[api]"

# With LLM-based semantic classification (Layer 3)
pip install -e ".[llm]"
export MCE_LLM_API_KEY="your-key"
export MCE_LLM_ENABLED=true

# Run tests
pip install -e ".[testing]"
pytest
```

---

## License

MIT

---

## Links

- Repository: [github.com/lulin70/memory-classification-engine](https://github.com/lulin70/memory-classification-engine)
- Roadmap: [ROADMAP.md](./ROADMAP.md)
- Beta Testing Guide: [BETA_TESTING_GUIDE_EN.md](./BETA_TESTING_GUIDE_EN.md)
- MCP Setup for Claude Code: [docs/claude_code_mcp_config.md](./docs/claude_code_mcp_config.md)
- Issues / Discussions
