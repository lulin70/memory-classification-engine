# Memory Classification Engine - Roadmap

## Update History

| Version | Date | Updater | Update Content | Review Status |
|---------|------|---------|---------------|---------------|
| v0.2.1 | 2026-04-19 | Engineering Team | **Pure Upstream Positioning**: README rewritten with "Classification First" narrative, MCP tools marked deprecated (8 storage → removed in v0.3), STORAGE_STRATEGY.md created, consensus v3 (Route B decision) | Reviewed |
| v0.2.0 | 2026-04-18 | Engineering Team | Phase 1 optimization complete (-74% process_message), Phase 2 features delivered, MCP Server Production, **874 tests**, Demo 26/30 (87%) | Reviewed |

---

## Vision

**MCE is the standard memory classification middleware for AI agents.**

Like how **ChromaDB** is synonymous with vector storage, MCE aims to become synonymous with **memory classification** — the "security scanner" that decides what enters any memory system.

**Product positioning**: *"Your Agent uses Supermemory/Mem0/Obsidian to STORE memories. MCE tells it WHAT to store."*

**Core narrative**: Classification First. Store Later. Your Choice.

---

## Strategic Decision: Pure Upstream Route (2026-04-19)

**Decision document**: [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md)

### What Changed

| Before (v0.2.0) | After (v0.3.0+) |
|------------------|-------------------|
| MCP: 11 tools (classify + full CRUD) | MCP: 4 tools (classify only) |
| "Memory classification engine" | "Memory classification **middleware**" |
| Competes with Supermemory / Mem0 | **Complements** them (downstream customers) |
| Built-in SQLite storage required | Storage delegated via **StorageAdapter ABC** |
| Narrative: "Don't remember everything" | Narrative: "**Classify before you store**" |

### Why This Decision

1. **Supermemory has YC + Benchmark #1 + Cloudflare infra.** Cannot compete on storage.
2. **Mem0 has 18k Stars + vector+graph hybrid.** Their storage is battle-tested.
3. **But NONE of them classify before storing.** That's the gap — and MCE owns it.
4. **60%+ of messages don't need LLM processing.** That's independent value, no storage needed.

---

## Completed Milestones

### v0.2.0 Release ✅ (2026-04-18)

**Status**: Released, tagged, pushed to GitHub

| Component | Details |
|-----------|---------|
| Core Engine | Three-layer pipeline (rule → pattern → semantic), 7 types, 4 tiers |
| Performance | `process_message` P99: -74% (5669→1452ms), cache hit: 97.83% |
| Test Suite | **874 tests passing, 0 failing** |
| Demo | 26/30 scenarios passing (87%) |
| MCP Server | stdio transport, 11 tools (3 core + 8 deprecated) |
| Documentation | README + Installation Guide + API Reference + Consensus docs |

### Phase 0: Pure Upstream Positioning ✅ (2026-04-19)

**Status**: Committed (`a8dc7b3e`), pushed

| Task | File | Change |
|------|------|--------|
| Tools deprecation | [tools.py](../src/memory_classification_engine/integration/layer2_mcp/tools.py) | 8 storage tools marked `[Deprecated v0.3]` |
| Version fix | [server.py](../src/memory_classification_engine/integration/layer2_mcp/server.py) | serverInfo 0.1.0 → 0.2.0 |
| HTTP server deprecation | [mce-mcp/server.py](../mce-mcp/mce_mcp_server/server.py) | DEPRECATED block comment added |
| README rewrite | [README.md](../README.md) | "Classification First" narrative, FAQ, architecture diagram |
| Storage strategy guide | [STORAGE_STRATEGY.md](../docs/user_guides/STORAGE_STRATEGY.md) | NEW — Supermemory/Mem0/Obsidian integration guide |
| Install guide update | [installation_guide_v2.md](../docs/user_guides/installation_guide_v2.md) | MCP section aligned with pure upstream mode |
| Consensus docs | [MCP_POSITIONING_CONSENSUS_v3.md](../docs/consensus/) | Full strategic decision document (Route B) |

---

## Current Version: v0.2.0 (Stable)

### What's Included

```
MCE v0.2.0
├── Core Classification Engine
│   ├── Layer 1: Rule Matching (60%+ coverage, zero cost)
│   ├── Layer 2: Pattern Analysis (30%+, zero LLM)
│   ├── Layer 3: Semantic Inference (<10%, LLM fallback)
│   ├── 7 Memory Types (user_preference / correction / fact / decision / relationship / pattern / sentiment)
│   ├── 4 Suggested Tiers (sensory / procedural / episodic / semantic)
│   ├── Feedback Loop (auto-learning from corrections)
│   └── Distillation Router (cost-aware routing)
│
├── MCP Server (stdio, Production)
│   ├── classify_memory     ← Core (keep in v0.3)
│   ├── batch_classify      ← Core (keep in v0.3)
│   ├── mce_status          ← Core (keep in v0.3)
│   ├── store_memory        ← ⚠️ Deprecated v0.3
│   ├── retrieve_memories   ← ⚠️ Deprecated v0.3
│   ├── get_memory_stats    ← ⚠️ Deprecated v0.3
│   ├── find_similar        ← ⚠️ Deprecated v0.3
│   ├── export_memories     ← ⚠️ Deprecated v0.3
│   ├── import_memories     ← ⚠️ Deprecated v0.3
│   ├── mce_recall          ← ⚠️ Deprecated v0.3
│   └── mce_forget          ← ⚠️ Deprecated v0.3
│
└── Built-in Storage (SQLite)
    └── Will be wrapped as BuiltInStorageAdapter @deprecated in v0.3
```

---

## Next: v0.3.0 — Pure Upstream Migration

**Target**: ~6 person-days | **Breaking Change**: Yes (8 MCP tools removed)

### V3-MCP-01: tools.py Rewrite (11 → 4 tools)

Remove 8 deprecated storage tools. Keep only:

| Tool | Purpose |
|------|---------|
| `classify_message` | Classify single message → MemoryEntry JSON |
| `get_classification_schema` | Return 7-type + 4-tier definition for downstream mapping |
| `batch_classify` | Batch classify → MemoryEntry[] |
| `mce_status` | Engine status (version, capabilities, uptime) |

### V3-MCP-02: handlers.py Rewrite (-422 lines)

Delete 8 storage handler methods. Modify `handle_classify_memory` to output MemoryEntry Schema v1.0 format. Add `handle_get_classification_schema`.

### V3-MCP-03: engine.py — New `to_memory_entry()` Method

Convert `process_message()` result into standardized MemoryEntry JSON:

```json
{
  "schema_version": "1.0.0",
  "should_remember": true,
  "entries": [{
    "id": "mce_20260419_001",
    "type": "user_preference",
    "confidence": 0.95,
    "tier": 2,
    "source_layer": "rule",
    "reasoning": "...",
    "suggested_action": "store",
    "metadata": {...}
  }],
  "summary": {...},
  "engine_info": {"mode": "classification_only"}
}
```

### V3-MCP-04: StorageAdapter ABC (New Abstract Layer)

```python
class StorageAdapter(ABC):
    def store(self, entry: MemoryEntry) -> str: ...
    def store_batch(self, entries: List[MemoryEntry]) -> List[str]: ...
    def retrieve(self, query: str, limit: int) -> List[Dict]: ...
    def delete(self, storage_id: str) -> bool: ...
    def get_stats(self) -> Dict: ...
    @property
    def name(self) -> str: ...       # e.g. "supermemory", "obsidian"
    @property
    def capabilities(self) -> Dict: ...  # {"vector_search": True, ...}
```

### V3-MCP-05: BuiltInStorageAdapter (@deprecated)

Wrap current SQLite logic as adapter. Mark `@deprecated`. For transition compatibility only.

### V3-06~08: Classification Accuracy Fixes

- A3.2: correction type accuracy improvement
- A3.5: sentiment_marker accuracy improvement
- Goal: classification accuracy >85% on clear messages

### V3-09~14: Testing Overhaul

| Task | Description |
|------|-------------|
| V3-09 | **MCE-Bench 180-case** — classification accuracy benchmark (P0, survival-critical) |
| V3-10 | Fuzz testing (1000 random inputs, verify no crashes) |
| V3-11 | MCP integration tests (4 tools only, no DB dependency) |
| V3-12 | Full regression (target: 874+ all green) |

### V3-15~17: Documentation & Case Study

| Task | Description |
|------|-------------|
| V3-15 | Migration guide (v0.2 → v0.3: data export script) |
| V3-16 | Case study: "MCE + Supermemory = Complete Memory Pipeline" |
| V3-17 | Updated installation guide (pure classification mode default) |

---

## Future Milestones (Post-v0.3)

### v0.4.0 — Official Downstream Adapters

| Adapter | Priority | Effort |
|---------|----------|--------|
| **SupermemoryAdapter** | P0 | ~2d |
| **ObsidianAdapter** | P0 | ~1.5d |
| **Mem0Adapter** | P1 | ~1.5d |
| **JSONFileAdapter** (default fallback) | P0 | ~0.5d |

### v0.5.0 — `get_classification_schema` Enhancement

- Downstream auto-mapping tables (MCE type → Supermemory tag → Mem0 category → Obsidian folder)
- Schema versioning (v1.0 → v1.1 backward compatible)
- Web UI for schema browser

### v0.6.0 — MCE-Bench Public Release

- 180-case standard benchmark dataset
- Leaderboard format (accuracy / latency / cost per 1k msgs)
- Open for community submissions
- Target: >90% accuracy on clear messages

### v1.0.0 — Industry Standard

- Classification accuracy >95%
- Official adapters for 5+ downstream systems
- Community-contributed adapters ecosystem
- Academic paper: "Why Classification Matters More Than Storage for AI Memory"

---

## Architecture Evolution

```
v0.2.0 (CURRENT)                    v0.3.0 (NEXT)                     v1.0.0 (VISION)
┌─────────────┐                   ┌─────────────┐                   ┌─────────────┐
│  MCP Server  │                   │  MCP Server  │                   │  MCP Server  │
│  11 tools    │                   │  4 tools     │                   │  4 tools     │
│  (8 deprec.) │ ──breaking─────▶  │  (pure class)│                   │  (pure class)│
└──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘
       │                                 │                                 │
┌──────▼──────┐                   ┌──────▼──────┐                   ┌──────▼──────┐
│   Engine     │                   │   Engine     │                   │   Engine     │
│  (monolithic)│                   │  (+to_memory  │                   │  (optimized)  │
│             │                   │   _entry())   │                   │  (>95% acc.)  │
└──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘
       │                                 │                                 │
┌──────▼──────┐                   ┌──────▼──────┐                   ┌──────▼──────┐
│  SQLite     │                   │ Adapter ABC  │                   │ Adapter Eco │
│  (hardcoded) │                   │  + BuiltIn   │                   │ (5+ official)│
└─────────────┘                   │  (deprecated)│                   │ + community │
                                 └──────┬──────┘                   └─────────────┘
                                        │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                         [Supermem]   [Obsidian]   [Mem0]   ...more
```

---

## Key Metrics Targets

| Metric | v0.2.0 (current) | v0.3.0 (target) | v1.0.0 (vision) |
|--------|------------------|-----------------|---------------|
| MCP tools | 11 (8 deprecated) | **4** (pure) | 4 |
| Code (layer2_mcp/) | ~1580 lines | **~650 lines** (-59%) | ~500 lines |
| Test scenarios | 92 (with DB deps) | **43** (no DB deps) (-53%) | 50+ |
| Classification accuracy | Unknown (~60% demo) | **>85%** (MCE-Bench) | **>95%** |
| Downstream adapters | 0 | 1 (BuiltIn @deprec) | **5+ official** |
| LLM call ratio | <10% | <10% | <5% |

---

## Decision Records

### DR-001: Why Pure Upstream Instead of Full Stack? (2026-04-19)

**Options considered**:
- A: Full stack (compete with Supermemory/Mem0 on storage) ❌
- B: Pure upstream (classification only, storage to downstream) ✅
- C: Dual mode (two packages) ❌

**Decision**: Route B — Pure Upstream

**Key reasons**:
1. Cannot compete on storage (Supermemory YC-funded, Mem0 18k stars)
2. But nobody does classification well — 7 competitor articles ALL ignore this dimension
3. "Warehouse vs Security Scanner" metaphor is compelling and differentiating
4. Reduces code by 59%, tests by 53%, maintenance burden dramatically

**Full analysis**: [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md)

### DR-002: Why MCP Over Framework Adapters First? (2026-04-11)

**Decision**: MCP priority over LangChain/CrewAI/AutoGen adapters

**Reasons still valid**:
- MCP is the trend (Anthropic heavily promoting)
- Claude Code / Cursor users = exact target audience
- Low packaging cost, high conversion rate
- Framework adapters can come later as Layer 3

### DR-003: Why Not a Skill Framework? (2026-04-10)

**Decision**: Engine, not framework

**Reasons still valid**:
- Framework competition fierce (LangChain, LlamaIndex)
- Engine positioning clearer, more differentiated
- Easier to integrate BY other frameworks
- Lower maintenance cost

---

## Promotion Plan

### Phase 1: Launch (Now — v0.2.0)

- [x] GitHub release v0.2.0
- [x] README rewrite (Classification First narrative)
- [ ] PyPI publish (pending user confirmation)
- [ ] "Classification First" blog post (drafting)

### Phase 2: Content Marketing (Parallel with v0.3 dev)

| Channel | Content | Status |
|---------|---------|--------|
| Hacker News | "I built a pre-filter for your AI memory system" | ⏳ Planned |
| Reddit r/ClaudeAI | "MCE + Supermemory: complete memory pipeline tutorial" | ⏳ Planned |
| GitHub Discussions | Show HN post + architecture walkthrough | ⏳ Planned |
| MCP Community | Submit to official MCP tools registry | ⏳ Planned |
| Blog (English) | "Why Classification Matters More Than Storage for AI Memory" | ⏳ Planned |
| Demo Video | 30s Claude Code + MCE operation GIF | ⏳ Planned |

### Phase 3: Ecosystem Growth (Post-v0.3)

- Official adapter releases (Supermemory, Obsidian, Mem0)
- MCE-Bench public leaderboard
- Community adapter contributions
- Integration tutorials with popular Agent frameworks

---

## Appendix

### Related Documents

| Document | Description |
|----------|-------------|
| [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md) | Strategic decision: why pure upstream |
| [COMPETITOR_ANALYSIS_CONSENSUS_v2.md](./docs/consensus/COMPETITOR_ANALYSIS_CONSENSUS_v2.md) | 7 competitor articles deep analysis |
| [STRATEGIC_REVIEW_CONSENSUS_20260419.md](./docs/consensus/STRATEGIC_REVIEW_CONSENSUS_20260419.md) | Strategic review meeting notes |
| [STORAGE_STRATEGY.md](./docs/user_guides/STORAGE_STRATEGY.md) | Downstream integration guide |
| [API Reference](./docs/api/API_REFERENCE_V1.md) | Complete SDK/MCP/REST documentation |
| [Installation Guide](./docs/user_guides/installation_guide_v2.md) | Setup, config, troubleshooting |

### Related Links

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Supermemory](https://supermemory.ai) — Recommended downstream (cloud)
- [Mem0](https://mem0.ai) — Recommended downstream (self-hosted)

---

**Document Version**: v3.0.0
**Last Updated**: 2026-04-19
**Next Update**: After v0.3.0 release
