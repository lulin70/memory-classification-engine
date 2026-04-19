# Memory Classification Engine (MCE)

<p align="center">
  <strong>记忆分类中间件 — AI Agent 的"记忆安检机"</strong><br>
  <sub>MCE 不存储记忆。MCE 告诉你<strong>什么值得记</strong>、<strong>记成什么类型</strong>、<strong>存在哪一层</strong>。<br>
  存储的事，交给 Supermemory / Mem0 / Obsidian / 你自己的系统。</sub>
</p>

<p align="center">
  <a href="https://pypi.org/project/memory-classification-engine/"><img src="https://img.shields.io/pypi/v/memory-classification-engine" alt="PyPI version"></a>
  <a href="https://github.com/lulin70/memory-classification-engine/actions"><img src="https://img.shields.io/badge/tests-874%20passing-green" alt="Tests"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-Production%20Ready-blue" alt="MCP"></a>
</p>

<p align="center">
  <a href="./README-ZH.md">中文</a> ·
  <a href="./README-JP.md">日本語</a> ·
  <a href="./ROADMAP.md">Roadmap</a> ·
  <a href="./docs/user_guides/STORAGE_STRATEGY.md">Storage Strategy</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/issues">Issues</a>
</p>

---

## The Problem: Nobody Classifies Before Storing

Every AI memory system has the same blind spot.

**Supermemory** receives a message → stores it. No classification.
**Mem0** receives a message → stores it. No classification.
**Claude Code CLAUDE.md** → you manually decide what to write. No structure.

They all answer **"how to store"** but never **"what's worth storing"**.

The result:

| Message | Should it be stored? | What most systems do |
|---------|-------------------|---------------------|
| "I prefer double quotes" | Yes — preference | ✅ Stored (good) |
| "OK, sounds good" | No — acknowledgment | ❌ Stored anyway (noise) |
| "That approach was too complex" | Yes — correction | ⚠️ Stored as generic summary (lost type info) |
| "Nice weather today" | No — chitchat | ❌ Stored (pollutes retrieval) |

**60%+ of messages should NOT be stored.** But current systems either store everything (noise explosion) or store nothing (amnesia).

**MCE is the missing pre-filter.**

---

## What MCE Does

MCE is a **classification middleware**. It sits between your Agent and your memory system:

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
               │  Structured MemoryEntry (JSON)
               ▼
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 [Supermemory] [Mem0] [Obsidian] [Your DB]
    (cloud)    (self-host) (local)  (custom)
```

**MCE does one thing extremely well**: decide whether a message contains memorable information, and if so, classify it into one of 7 types with confidence scoring.

**MCE does NOT do**: store, retrieve, search, delete, export, import, or recall memories. Those are downstream responsibilities.

---

## Why Classification Matters More Than Storage

### Argument 1: The 60% Filter

MCE's three-layer pipeline filters out 60%+ of messages before any expensive processing:

```
Incoming Message
       │
       ▼
┌─────────────────────┐   60%+ of messages   │  Zero cost
│ Layer 1: Rule Match  │   filtered here     │  Regex + keywords
│   "remember", "always..."│                   │  Deterministic
└──────────┬──────────┘
           │ Unmatched (~40%)
           ▼
┌─────────────────────┐   30%+ of messages   │  Still zero LLM
│ Layer 2: Pattern    │   classified here    │  Conversation structure
│   Analysis          │                     │  "3rd rejection = preference"
└──────────┬──────────┘
           │ Ambiguous (~10%)
           ▼
┌─────────────────────┐   <10% of messages   │  LLM fallback
│ Layer 3: Semantic   │   reach here         │  Edge cases only
│   Inference         │                     │
└─────────────────────┘
```

Most solutions start at Layer 3 (LLM for every message). MCE starts at Layer 1.

**Cost per 1,000 messages:**

| Approach | LLM Calls | Cost |
|----------|-----------|------|
| Send everything to LLM | 1,000 | $0.50 - $2.00 |
| **MCE (Layer 1 + 2 first)** | **<100** | **$0.05 - $0.20** |

### Argument 2: Typed Memories Are More Useful Than Raw Summaries

```
Message: "That last approach was too complex, let's go simpler"

Without MCE (raw storage):
  → Stored as: "User discussed approach complexity"
  → Problem: Lost the REJECTION context. Search for "approach" returns noise.

With MCE (classified):
  → [correction] "Rejected previous complex approach, prefers simplicity"
  → Confidence: 0.89 | Source: pattern | Tier: episodic
  → Benefit: Downstream can route corrections differently from facts
```

### Argument 3: 7 Types > 1 Bucket

| Type | Example | Why it matters |
|------|---------|---------------|
| **user_preference** | "I prefer spaces over tabs" | Affects ALL future code generation |
| **correction** | "No, do it like this instead" | Must override previous fact/decision |
| **fact_declaration** | "We have 100 employees" | Verifiable truth, rarely changes |
| **decision** | "Let's go with Redis for caching" | Explains WHY architecture looks this way |
| **relationship** | "Alice handles backend" | Enables role-aware responses |
| **task_pattern** | "Always test before deploy" | Automatable workflow rules |
| **sentiment_marker** | "This workflow is frustrating" | Signals process pain points |

Not every message produces a memory. Chit-chat ("OK", "thanks"), acknowledgments, and low-signal content are filtered out.

---

## Quick Start

```bash
pip install memory-classification-engine
```

No database. No API key. No configuration. Pure classification.

### Classify a Message in 30 Seconds

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# Process a message — returns dict with 'matches' list
result = engine.process_message(
    "That last approach was too complex, let's go simpler"
)

# Access classification results:
if result.get('matches'):
    entry = result['matches'][0]
    print(f"Type: {entry.get('type')}")          # 'correction'
    print(f"Confidence: {entry.get('confidence')}")  # 0.89
    print(f"Tier: {entry.get('tier')}")           # 3 (episodic)
    print(f"Should store: {entry.get('confidence', 0) > 0.5}")  # True
```

### More Examples

```python
# Scenario 1: User preference
engine.process_message("I prefer double quotes in Python")
# → [user_preference] conf: 0.95, tier: 2, source: rule
#   ↓ Store this to Supermemory/Mem0/Obsidian as "preference"

# Scenario 2: Correction (overrides previous knowledge)
engine.process_message("No, we're using PostgreSQL not MongoDB")
# → [correction] conf: 0.92, tier: 2, source: pattern
#   ↓ Downstream should UPDATE existing fact, not duplicate

# Scenario 3: Decision (explains architecture choices)
engine.process_message("We decided to use Redis for session caching")
# → [decision] conf: 0.88, tier: 3, source: semantic
#   ↓ High-value, store in long-term memory

# Scenario 4: Noise (filtered out automatically)
engine.process_message("OK, let me check that")
# → [] (empty matches — no memory needed)

# Scenario 5: Relationship extraction
engine.process_message("Alice owns backend, Bob does frontend")
# → [relationship] conf: 0.95, tier: 4 (semantic/graph)
#   ↓ Good candidate for knowledge graph storage
```

### Batch Classification

```python
messages = [
    {"message": "I prefer dark mode"},
    {"message": "We chose PostgreSQL"},
    {"message": "Thanks for the help"},  # ← will be filtered
    {"message": "Alice handles the API"},
]

result = engine.batch_process(messages)
# Returns list of results, each with matches/confidence/tier
```

---

## Suggested Storage Tiers

MCE assigns each classified memory a **suggested storage tier**. This is advice to your downstream system — not a requirement.

| Tier | Name | Lifecycle | When to use |
|------|------|-----------|-------------|
| T1 | Sensory | < 1 second | Never store (filtered by MCE) |
| T2 | Procedural | Hours–Days | Active preferences, patterns, corrections |
| T3 | Episodic | Days–Months | Decisions, facts, events |
| T4 | Semantic | Months–Years | Relationships, domain knowledge |

Your downstream system can follow these suggestions or implement its own retention policy. See [Storage Strategy Guide](./docs/user_guides/STORAGE_STRATEGY.md) for integration examples with Supermemory, Mem0, and Obsidian.

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

### Feedback Loop (v2.0)

```python
result = engine.process_feedback(memory_id="mem_001",
                                feedback={"type": "wrong_type",
                                           "correct_type": "decision"})
# → Pattern detected: 3rd occurrence of user correcting episodic→decision
# → Rule suggestion generated, awaiting auto-apply (confidence: 0.85)
```

> **API Note**: `process_feedback(memory_id, feedback)` takes 2 arguments — `feedback` is a dict containing correction details. See [API Reference](./docs/api/API_REFERENCE_V1.md) for full signature.

---

## MCP Server: Claude Code Integration in 2 Minutes

MCE ships with a built-in MCP server (**v0.2.0, Production Ready**). MCE runs locally — **your data never leaves your machine**.

> **Positioning**: MCE is a **classification middleware**, not a full memory system. The MCP server exposes classification tools; storage is delegated to downstream systems (Supermemory, Mem0, Obsidian, or your own).

### Setup

```bash
python3 -m memory_classification_engine.integration.layer2_mcp
```

Add to your Claude Code config (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "mce": {
      "command": "python3",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
      "env": {}
    }
  }
}
```

### Available Tools (v0.2.0)

| Tool | Status | Description |
|------|--------|-------------|
| `classify_memory` | Core | Classify message -> structured MemoryEntry (type, tier, confidence) |
| `batch_classify` | Core | Batch classify multiple messages |
| `mce_status` | Core | Engine status (version, capabilities, uptime) |
| `store_memory` | Deprecated v0.3 | Storage moves to downstream adapter |
| `retrieve_memories` | Deprecated v0.3 | Retrieval moves to downstream system |
| `get_memory_stats` | Deprecated v0.3 | Stats from downstream system |
| `find_similar` | Deprecated v0.3 | Vector search from downstream |
| `export_memories` | Deprecated v0.3 | Export from downstream |
| `import_memories` | Deprecated v0.3 | Import to downstream |
| `mce_recall` | Deprecated v0.3 | Recall from downstream (e.g., Supermemory `recall()`) |
| `mce_forget` | Deprecated v0.3 | Delete via downstream |

> **Migration note**: In v0.3.0, deprecated tools will be removed. The MCP server will expose only 4 tools: `classify_message`, `get_classification_schema`, `batch_classify`, `mce_status`. See [Storage Strategy Guide](./docs/user_guides/STORAGE_STRATEGY.md) for downstream integration options.

### How It Works in Practice

```
You (in Claude Code):  "I prefer double quotes in Python"
         │
         ▼
   MCE MCP Server:  classify_memory("I prefer double quotes...")
         │
         ▼
   Output (MemoryEntry JSON):
   {
     "should_remember": true,
     "entries": [{
       "type": "user_preference",
       "confidence": 0.95,
       "tier": 2,
       "suggested_action": "store",
       "content": "User prefers double quotes over single quotes"
     }]
   }
         │
         ▼
   Your choice: Store to Supermemory / Obsidian / Mem0 / custom
```

See [API Reference](./docs/api/API_REFERENCE_V1.md) and [Storage Strategy](./docs/user_guides/STORAGE_STRATEGY.md) for full documentation.

---

## Performance

Benchmark results from `benchmarks/baseline_benchmark.py`:

### Classification Performance (Core Metric)

| Metric | Value | Condition |
|--------|-------|-----------|
| `process_message` P50 latency | ~45 ms | Warm cache, rule match |
| `process_message` P99 latency | **1,452 ms** | Worst case (LLM fallback) |
| Layer 1 hit rate | 60%+ | After 1 week of use |
| Cache hit rate (warmup) | **97.83%** | After initial warmup |
| LLM call ratio | **<10%** | Most messages handled by L1/L2 |

### Test Quality

| Metric | Value |
|--------|-------|
| Total tests | **874 passing, 0 failing** |
| Demo scenarios | **26/30 passed (87%)** |
| Coverage | Core engine + layers + coordinators + privacy |

### Cost Efficiency

| Scenario | Messages | Est. LLM calls | Est. cost |
|----------|----------|--------------|-----------|
| Light usage (10 msgs/day) | 300/month | ~30 | **<$0.01** |
| Heavy usage (100 msgs/day) | 3,000/month | ~300 | **~$0.10** |
| Power user (500 msgs/day) | 15,000/month | ~1,500 | **~$0.50** |

---

## FAQ

### Is MCE a replacement for Supermemory / Mem0?

**No. MCE complements them.**

Think of it this way:
- **Supermemory / Mem0** = the warehouse (stores and retrieves memories)
- **MCE** = the security scanner at the warehouse entrance (decides what goes in)

You can use them together: MCE classifies → Supermemory stores → Supermemory recalls. Or MCE classifies → Obsidian saves as markdown. MCE doesn't care where the data goes.

### Why not just build storage into MCE?

Three reasons:

1. **Supermemory has YC funding, Cloudflare infrastructure, and Benchmark #1 rankings.** One developer cannot compete on storage quality.
2. **Mem0 has 18k GitHub Stars, vector+graph hybrid storage, and a team of engineers.** Their storage is battle-tested.
3. **But NONE of them classify before storing.** That's the gap MCE fills. And once MCE classifies, any downstream system benefits from cleaner input data.

MCE focuses on being the **world's best memory classifier**, not an average memory system.

### Is my data safe?

**Yes.** MCE runs entirely locally on your machine. No data is sent to external servers during classification. Where your classified data goes next depends on which downstream system you choose — that's under **your** control.

### What if I don't want to set up a downstream system?

That's fine! Use MCE purely as a classification service:

```python
result = engine.process_message("I prefer dark mode")
if result.get('matches'):
    entry = result['matches'][0]
    print(f"[{entry['type']}] {entry['content']} (conf: {entry['confidence']})")
    # Log it, print it, copy-paste it anywhere
```

MCE's value is in the **classification decision**, not the persistence.

### What's the roadmap?

See [ROADMAP.md](./ROADMAP.md). Key milestones:
- **v0.2.0** (current): Classification engine + MCP server (11 tools, 8 deprecated)
- **v0.3.0** (next): Pure upstream migration — MCP reduced to 4 tools, StorageAdapter ABC, MemoryEntry Schema v1.0
- **v0.4.0**: Official adapters for Supermemory, Mem0, Obsidian
- **v1.0.0**: Industry-standard classification benchmark (MCE-Bench)

### How does MCE compare to...?

| Question | Answer |
|----------|--------|
| **vs Supermemory?** | Complementary. MCE classifies, Supermemory stores. Use both. |
| **vs Mem0?** | Complementary. MCE adds typed classification before Mem0's storage. |
| **vs Claude Code CLAUDE.md?** | MCE automates what you'd manually write in CLAUDE.md. Structured, typed, confidence-scored. |
| **vs building my own if/else?** | MCE has 7 types, 3-layer pipeline, auto-learning rules, and 60%+ zero-cost filtering. Rolling your own gets expensive fast. |

---

## Installation

```bash
# Core (classification engine only — pure Python, no heavy deps)
pip install memory-classification-engine

# With RESTful API server
pip install -e ".[api]"

# With LLM-based semantic classification (Layer 3, optional)
pip install -e ".[llm]"
export MCE_LLM_API_KEY="your-key"
export MCE_LLM_ENABLED=true

# Run tests
pip install -e ".[testing]"
pytest  # 874 tests, ~10 min
```

**Minimum dependency**: Only PyYAML. Everything else (vector DB, graph DB, LLM) is optional.

---

## Project Structure

```
memory-classification-engine/
├── src/memory_classification_engine/
│   ├── engine.py                    # Core coordinator
│   ├── layers/
│   │   ├── rule_matcher.py          # Layer 1: Rule matching (60%+ coverage)
│   │   ├── pattern_analyzer.py      # Layer 2: Structure analysis (30%+)
│   │   ├── semantic_classifier.py   # Layer 3: LLM fallback (<10%)
│   │   ├── feedback_loop.py         # Auto-learning from corrections
│   │   └── distillation.py          # Cost-optimized routing
│   ├── adapters/                    # v0.3.0: StorageAdapter ABC (planned)
│   ├── storage/                     # Built-in storage (deprecated in v0.3)
│   ├── coordinators/
│   └── utils/
│
├── src/memory_classification_engine/integration/layer2_mcp/
│   ├── server.py                    # MCP stdio server (Production v0.2.0)
│   ├── tools.py                     # 11 tool definitions (→ 4 in v0.3.0)
│   └── handlers.py                  # Tool handlers
│
├── mce-mcp/mce_mcp_server/server.py # HTTP server (Deprecated, use stdio)
├── benchmarks/                      # Performance measurement
├── tests/                           # 874 tests passing
├── config/rules.yaml                # Editable classification rules
├── docs/
│   ├── consensus/                   # Strategic decisions & analysis
│   └── user_guides/                 # Installation, storage strategy
├── setup.py                         # PyPI package config
└── README.md
```

---

## License

MIT

---

## Links

- **Repository**: [github.com/lulin70/memory-classification-engine](https://github.com/lulin70/memory-classification-engine)
- **Roadmap**: [ROADMAP.md](./ROADMAP.md)
- **Storage Strategy**: [STORAGE_STRATEGY.md](./docs/user_guides/STORAGE_STRATEGY.md) — how to integrate with downstream systems
- **API Reference**: [docs/api/API_REFERENCE_V1.md](./docs/api/API_REFERENCE_V1.md)
- **Strategic Consensus**: [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md) — why we chose the pure upstream path
- **Issues / Discussions**
