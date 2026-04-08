# Memory Classification Engine

<p align="center">
  <strong>A lightweight Agent-side memory classification engine</strong><br>
  Real-time classification of what's worth remembering, how to store it, and which memory tier to use
</p>

<p align="center">
  <a href="./README.md">中文</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/issues">Issues</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/discussions">Discussions</a>
</p>

---

## Why?

Most AI Agent memory solutions use a "full summary" approach: after a conversation ends, they summarize the entire thing and store it. This fills your memory store with noise and destroys retrieval signal-to-noise ratio.

Memory Classification Engine takes a different approach:

- **Real-time classification**, not post-hoc summarization. Judges each message as the conversation flows
- **7 memory types** distinguished: preferences, corrections, facts, decisions, relationships, task patterns, sentiment markers
- **Three-layer judgment pipeline**: rule matching (zero cost) → structure analysis (lightweight) → semantic inference (LLM, only when needed)
- **Four-tier memory storage**: working memory → procedural memory → episodic memory → semantic memory
- **Active forgetting**: weighted decay based on time, frequency, and importance instead of passive overflow eviction

In short: **tell your Agent what's worth remembering instead of storing everything.**

## How It Compares

| | Mem0 | MemGPT | LangChain Memory | This Project |
|---|---|---|---|---|
| **Write Timing** | Full extraction after conversation | Context window management | Manual/Hooks | **Real-time classification** |
| **Memory Classification** | Basic | None | None | **7 types + 3-layer pipeline** |
| **Memory Tiers** | Single (vector DB) | Two (memory + disk) | Single (session) | **Four tiers** |
| **Forgetting** | None | Passive eviction | None | **Active weighted decay** |
| **Learning** | Basic | None | None | **Patterns auto-promote to rules** |
| **Agent-agnostic** | Yes | No | Yes | **Yes (standalone module + SDK)** |

## Quick Start

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd memory-classification-engine

# Install (core dependency is just PyYAML, works out of the box)
pip install -e .
```

No database required. No API key needed. Works immediately:

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# Process a message — the engine decides if it's worth remembering
result = engine.process_message("Remember, I prefer spaces over tabs")
print(result)
# {"matched": true, "memory_type": "user_preference", "tier": 2,
#  "content": "prefer spaces over tabs", "confidence": 1.0, "source": "rule:0"}

# Retrieve memories
memories = engine.retrieve_memories("coding preferences")
print(memories)
```

### Optional Extensions

```bash
# RESTful API server
pip install -e ".[api]"

# LLM semantic classification (Layer 3)
pip install -e ".[llm]"
export MCE_LLM_API_KEY="your_api_key"
export MCE_LLM_ENABLED=true

# Run tests
pip install -e ".[testing]"
pytest
```

## Memory Types

The engine classifies conversation content into 7 types in real time:

| Type | Key | Example |
|------|-----|---------|
| User Preference | `user_preference` | "I prefer spaces over tabs" |
| Correction | `correction` | "No, use 4 spaces not 2" |
| Fact Declaration | `fact_declaration` | "Our team has 5 people" |
| Decision | `decision` | "Let's go with Python" |
| Relationship | `relationship` | "Alice handles the backend" |
| Task Pattern | `task_pattern` | "Always run tests before deploying" |
| Sentiment Marker | `sentiment_marker` | "I really hate over-engineered architectures" |

## Three-Layer Pipeline

The core design principle: **use the cheapest method that works, LLM is the last resort.**

```
User message
  │
  ▼
┌──────────────────────────┐
│ Layer 1: Rule Matching    │  Regex + keywords, zero cost, covers 60%+ of common cases
└────────┬─────────────────┘
         │ Unmatched
         ▼
┌──────────────────────────┐
│ Layer 2: Structure Analysis│  Conversation interaction pattern recognition, no LLM needed
└────────┬─────────────────┘
         │ Unmatched
         ▼
┌──────────────────────────┐
│ Layer 3: Semantic Inference│  LLM-based semantic analysis, high coverage
└────────┬─────────────────┘
         │
         ▼
  Dedup → Conflict detection → Write to appropriate tier
```

## Four-Tier Storage

| Tier | Type | Storage | Lifecycle |
|------|------|---------|-----------|
| Tier 1 | Working Memory | Context window (LLM native) | Current session |
| Tier 2 | Procedural Memory | Config files / System prompts | Long-term, actively loaded |
| Tier 3 | Episodic Memory | Vector database (ChromaDB / SQLite) | Weighted decay |
| Tier 4 | Semantic Memory | Knowledge graph (Neo4j / in-memory) | Long-term, semantic links |

## Tech Stack

| Component | Default | Alternative |
|-----------|---------|-------------|
| Rule Engine | YAML + Regex | JSON Schema |
| Vector Store (Tier 3) | ChromaDB | Qdrant, Milvus |
| Knowledge Graph (Tier 4) | In-memory graph | Neo4j |
| Semantic Classification (Layer 3) | Small model API | Ollama (local) |
| Agent Adapters | Standalone module + SDK | Plugin extension |

The only core dependency is `PyYAML`. Vector databases, knowledge graphs, and LLMs are all optional extensions — install only what you need.

## Agent Framework Integration

Works as a standalone module with any Agent framework:

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# Register an agent (supports claude_code, work_buddy, trae, openclaw adapters)
engine.register_agent('my_agent', {
    'adapter': 'claude_code',
})

# Process messages through the agent
result = engine.process_message_with_agent('my_agent', "Hello, world!")
```

Also available via RESTful API and Python SDK. See [API docs](docs/api/api.md) and [User guide](docs/user_guides/user_guide.md) for details.

## Performance

| Metric | Result |
|--------|--------|
| Message processing (L1/L2) | ~10ms |
| Message processing (L3) | < 500ms |
| Retrieval latency | ~15ms |
| Concurrent throughput | 626 messages/s |
| Memory compression | 87-90% |
| Memory footprint | < 100MB (basic mode) |

## Project Structure

```
memory-classification-engine/
├── src/memory_classification_engine/
│   ├── engine.py              # Core engine (coordinator architecture)
│   ├── layers/                # Three-layer classification pipeline
│   │   ├── rule_matcher.py        # Layer 1: Rule matching
│   │   ├── pattern_analyzer.py    # Layer 2: Structure analysis
│   │   └── semantic_classifier.py # Layer 3: Semantic inference
│   ├── storage/               # Tiered storage
│   │   ├── tier2.py               # Procedural memory
│   │   ├── tier3.py               # Episodic memory (vector)
│   │   ├── tier4.py               # Semantic memory (graph)
│   │   └── neo4j_knowledge_graph.py
│   ├── privacy/               # Privacy & security
│   ├── plugins/               # Plugin system
│   ├── agents/                # Agent framework adapters
│   ├── sdk/                   # Python SDK
│   ├── api/                   # RESTful API
│   └── utils/                 # Utilities
├── config/rules.yaml          # Rule configuration
├── examples/                  # Usage examples
├── tests/                     # Tests
└── setup.py
```

## Contributing

Contributions of all forms are welcome: code, bug reports, documentation, discussions.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

[MIT License](LICENSE)

## Links

- Repository: [github.com/lulin70/memory-classification-engine](https://github.com/lulin70/memory-classification-engine)
- Issues: [Issues](https://github.com/lulin70/memory-classification-engine/issues)
- Discussions: [Discussions](https://github.com/lulin70/memory-classification-engine/discussions)
- Roadmap: [ROADMAP.md](ROADMAP.md)
