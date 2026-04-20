# Memory Classification Engine - Roadmap

## Update History

| Version | Date | Updater | Update Content | Review Status |
|---------|------|---------|---------------|---------------|
| **v0.3.2** | 2026-04-20 | Engineering Team | **V4-01~03 Accuracy Overhaul** (Acc 38.9%→66.7%, F1 84.2%→89.9%). Fixed 3 CRASH bugs, enhanced correction detection (F1 +32.4pp), reduced FP 44% (18→10). task_pattern revived (0%→52.2%) | In Progress |
| **v0.3.1** | 2026-04-19 | Engineering Team + Four-Role Review | **Phase A+B Classification Overhaul** (Precision 40%→94%, F1 57%→84%), **Layered Decoupling Architecture** (v3.1 consensus), Project structure cleanup, MCE-Bench 180-case benchmark, Tech terms whitelist 7→200+ | Reviewed |
| v0.2.1 | 2026-04-19 | Engineering Team | Pure Upstream Positioning: README rewritten, MCP tools deprecated, STORAGE_STRATEGY.md created, consensus v3 (Route B decision) | Reviewed |
| v0.2.0 | 2026-04-18 | Engineering Team | Phase 1 optimization complete (-74%), Phase 2 features delivered, MCP Server Production, **874 tests**, Demo 26/30 (87%) | Reviewed |

---

## Vision (Updated v3.1)

**MCE is the standard memory classification middleware for AI agents.**

Like how **ChromaDB** is synonymous with vector storage, MCE aims to become synonymous with **memory classification** — the "security scanner" that decides what enters any memory system.

**Product positioning (v3.1)**: *"Your Agent uses Supermemory/Mem0/Obsidian to STORE memories. MCE tells it WHAT to store. And by default, you can use our built-in SQLite adapter to get started immediately."*

**Core narrative (v3.1)**: **Classify First. Store Later. Default Works. Your Choice.**

**Architecture metaphor**: *"Engine is the heart, Adapters are the blood vessels, SQLite is the pacemaker."* — WORKBUDDY AI

---

## Strategic Decisions

### Decision #1: Pure Upstream Route (2026-04-19, v3.0)

**Document**: [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md)

| Before (v0.2.0) | After (v0.3.0+) |
|------------------|-------------------|
| MCP: 11 tools (classify + full CRUD) | MCP: 4 tools (classify only) |
| "Memory classification engine" | "Memory classification **middleware**" |
| Competes with Supermemory / Mem0 | **Complements** them (downstream customers) |
| Built-in SQLite storage required | Storage delegated via **StorageAdapter ABC** |

### Decision #2: Layered Decoupling Architecture (2026-04-19, v3.1) ⭐ NEW

**Document**: [MCP_POSITIONING_CONSENSUS_v3.md#7.5](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md#75--layered-decoupling-new-architecture-review-v31-)

**Four-role review result**: ✅ UNANIMOUS (5/5 approval including WORKBUDDY AI)

```
Three-Layer Architecture:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────┐
│ Layer 1: ENGINE CORE ★★★★★ (核心资产)              │
│                                                     │
│  • Only classifies: message → MemoryEntry JSON     │
│  • Zero external dependencies (pure rules + ML)     │
│  • Classification accuracy = ONLY KPI               │
│  • Current: Precision 94.1%, F1 84.2%              │
│  • Target: Accuracy ≥85%, F1 ≥82%                  │
└──────────────────────┬──────────────────────────────┘
                       │ MemoryEntry (JSON)
                       ▼
┌─────────────────────────────────────────────────────┐
│ Layer 2: STORAGE ADAPTERS (可插拔后端)             │
│                                                     │
│  Unified Interface (ABC):                           │
│    • remember(entry) — Store memory                │
│    • recall(query)   — Retrieve memories           │
│    • forget(id)      — Delete/expiry               │
│                                                     │
│  Official Adapters (planned):                       │
│    • SQLiteAdapter      ← Default implementation   │
│    • SupermemoryAdapter  ← Production recommended   │
│    • ObsidianAdapter     ← Note-taking users       │
│    • Mem0Adapter         ← Vector+graph users      │
│    • Custom Adapter      ← User-defined            │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Layer 3: SQLITE ADAPTER (默认实现，开箱即用)        │
│                                                     │
│  • One-file database (SQLite)                      │
│  • Basic CRUD operations                            │
│  • FTS5 full-text search                           │
│  • Forgetting mechanism (tier/time-based expiry)   │
│  • Development/Demo use (NOT production default)    │
└─────────────────────────────────────────────────────┘

Key Principle: "Default works out-of-the-box,
                replace if unsatisfied"
```

### Why This Architecture?

1. **Lower onboarding barrier**: From "configure storage yourself" → `pip install && mce run`
2. **Engine isolation**: Core code stays clean, tests don't import sqlite3
3. **Future-proof**: Any storage backend just implements 3 methods
4. **Express.js analogy**: Doesn't become DB framework because of built-in session store

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

### Phase 0: Pure Upstream Positioning ✅ (2026-04-19)

**Status**: Committed (`a8dc7b3e`), pushed

| Task | File | Change |
|------|------|--------|
| Tools deprecation | [tools.py](../src/memory_classification_engine/integration/layer2_mcp/tools.py) | 8 storage tools marked `[Deprecated v0.3]` |
| Version fix | [server.py](../src/memory_classification_engine/integration/layer2_mcp/server.py) | serverInfo 0.1.0 → 0.2.0 |
| README rewrite | [README.md](../README.md) | "Classification First" narrative, FAQ, architecture diagram |
| Storage strategy guide | [STORAGE_STRATEGY.md](../docs/user_guides/STORAGE_STRATEGY.md) | NEW — Supermemory/Mem0/Obsidian integration guide |
| Consensus docs | [MCP_POSITIONING_CONSENSUS_v3.md](../docs/consensus/) | Full strategic decision document (Route B) |

### Phase 1: Classification First Narrative ✅ (2026-04-19)

**Status**: Committed (`f050aa05`), pushed

- README.md FULL REWRITE (~553 lines)
- ROADMAP.md v3.0.0 rewrite
- i18n sync: -ZH→CN rename + 4 locale files (EN/CN/JP × README/Roadmap)

### Phase 2: Pure Upstream Code Migration ✅ (2026-04-19)

**Status**: Committed (`18c11d8b`), pushed

| Task | Change |
|------|--------|
| V3-MCP-01 | tools.py REWRITE (389→283 lines, -27%, 11→4 tools) |
| V3-MCP-02 | handlers.py REWRITE (674→259 lines, -62%) |
| V3-MCP-03 | engine.py: new `to_memory_entry()` method |
| V3-MCP-04 | adapters/base.py NEW (StorageAdapter ABC + MemoryEntry dataclass) |
| V3-MCP-05 | adapters/builtin.py NEW (BuiltInStorageAdapter @deprecated) |

### Phase A+B: Classification Accuracy Overhaul ✅ (2026-04-19) ⭐ MAJOR

**Status**: Committed (`f8bdf254`), pushed
**Benchmark**: MCE-Bench v1.0 (180 cases)

#### Phase A Fixes (Noise Filtering)

| Fix | Description | Impact |
|-----|-------------|--------|
| #1 | `_is_noise()` noise blacklist system | TN: 0→54, FP: 72→1 (-99%) |
| #2 | fact_declaration tightening (min length + tech terms) | Reduced false positives on short text |
| #3 | task_pattern initial enhancement (40+ action verbs) | Foundation for Phase B |

#### Phase B Fixes (Detection Rewrite)

| Fix | Description | Impact |
|-----|-------------|--------|
| #2b | Tech terms whitelist expansion: **7 → 200+ terms** | QA expert review complete coverage |
| B-1 | task_pattern COMPLETE REWRITE (workflow/habit/recurring patterns) | 15+ new regex patterns |
| B-2 | decision detection REWRITE (removed noise words, 15+ strong patterns) | Confidence grading Strong(0.75)/Weak(0.65) |
| B-3 | user_preference ENHANCEMENT (8 structured patterns, 40+ keywords) | Coding context awareness |
| B-4 | Detector priority REORDER (task/decision BEFORE fact) | Prevents fact from stealing matches |
| B-5 | Exception handling for language detection fallback | Prevents analyze() returning None |

#### CRITICAL BUG FIX

🔴 **`analyze()` method truncation bug resolved**
- Root cause: `_is_noise()` insertion broke method structure (orphan code outside method)
- Impact: All Phase B modifications were in non-executing code region
- Fix: Complete restructure of `analyze()` with proper detector loop

#### MCE-Bench v1.0 Results (180 cases)

```
┌─────────────────────┬──────────┬──────────┐
│ Metric               │ Before    │ After     │
├─────────────────────┼──────────┼──────────┤
│ Precision            │ 40.5%    │ 94.1%     │ (+53.6pp)│
│ F1 Score             │ 57.7%    │ 84.2%     │ (+26.5pp)│
│ FP Rate              │ 40%      │ 0.6%      │ (-99%)   │
│ TN (True Negatives)  │ 0        │ 54        │ (+54)    │
│ Type Mismatch        │ N/A      │ 27        │ Stable  │
└─────────────────────┴──────────┴──────────┘
```

### Project Structure Cleanup ✅ (2026-04-19)

**Status**: Included in `f8bdf254`

- Removed 16+ temporary debug files (debug_*, test_*, verify_*, monkey_*, ...)
- Reorganized docs/ directory (created planning/, config/, moved 17 files)
- Created [docs/README.md](./docs/README.md) documentation index
- Updated .gitignore with comprehensive rules

---

## Current Version: v0.3.1 (Post-Phase A+B)

### What's Included

```
MCE v0.3.1 (Post-Phase A+B)
├── Core Classification Engine (Layer 1: ENGINE CORE ★)
│   ├── Pattern Analyzer (rule-based, zero LLM cost)
│   │   ├── _is_noise() — Noise filtering system (NEW Phase A)
│   │   ├── 7 Memory Types with enhanced detection
│   │   │   ├── user_preference (8 patterns, 40+ keywords)
│   │   │   ├── correction (7 structural regex patterns)
│   │   │   ├── fact_declaration (200+ tech terms whitelist)
│   │   │   ├── decision (15+ strong decision patterns)
│   │   │   ├── task_pattern (workflow/habit/recurring, 15+ patterns)
│   │   │   ├── relationship & sentiment_marker
│   │   │   └── location
│   │   ├── Detector priority: task/decision BEFORE fact (Phase B-4)
│   │   └── Exception handling for robustness (Phase B-5)
│   ├── 4 Suggested Tiers (sensory → semantic)
│   ├── to_memory_entry() — MemoryEntry Schema v1.0 output
│   └── ClassificationPipeline (with noise filter at pipeline level)
│
├── MCP Server (stdio, Production Ready)
│   ├── classify_message     ← Core tool #1
│   ├── get_classification_schema  ← Core tool #2 (NEW in v0.3)
│   ├── batch_classify      ← Core tool #3
│   └── mce_status          ← Core tool #4
│
├── Storage Layer (Layer 2+3: PLANNED per v3.1 consensus)
│   ├── adapters/base.py    ← StorageAdapter ABC (EXISTS, interface defined)
│   ├── adapters/builtin.py ← BuiltInStorageAdapter (@deprecated wrapper)
│   └── [FUTURE] SQLite Adapter (v0.5 target)
│       ├── remember(entry) — Store memory
│       ├── recall(query)   — Retrieve with filters
│       └── forget(id)      — Delete / time-based expiry
│
├── Quality Assurance
│   ├── MCE-Bench v1.0 (180-case classification accuracy benchmark) ⭐ NEW
│   │   ├── 5 User Stories mapped to test categories
│   │   ├── 90 Positive cases (should remember)
│   │   ├── 55 Negative cases (noise to filter)
│   │   └── 35 Edge cases (boundary conditions)
│   ├── 881 tests passing (regression after Phase A+B)
│   └── Per-type F1 scoring system
│
└── Documentation (mature project structure)
    ├── docs/README.md (documentation index) ⭐ NEW
    ├── README / README-CN / README-JP (i18n complete)
    ├── ROADMAP / ROADMAP-CN / ROADMAP-JP (i18n complete)
    └── docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md (v3.1 updated)
```

---

## Next: v0.4.0 — Engine Optimization (Engine First 🎯)

**Target**: Continue classification accuracy improvement per **Engine First principle**
**Estimated effort**: ~5-7 person-days
**Breaking Change**: No (internal improvements only)

### Current MCE-Bench Status (180 cases)

```
┌─────────────────────┬──────────┬──────────┬──────────┐
│ Metric               │ Current  │ Target   │ Gap      │
├─────────────────────┼──────────┼──────────┼──────────┤
│ Accuracy             │ 38.9%    │ ≥85%     │ -46.1pp  │
│ Precision            │ 94.1%    │ ≥80%     │ ✅ MET   │
│ F1 Score             │ 84.2%    │ ≥82%     │ -3.8pp   │
│ Recall               │ 76.2%    │ ≥80%     │ -3.8pp   │
│ FP Rate              │ 0.6%     │ ≤10%     │ ✅ MET   │
│ FN Rate              │ 2.8%     │ ≤20%     │ ✅ MET   │
│ task_pattern F1      │ 0.0%     │ ≥50%     │ -50pp    │
│ correction F1        │ 0.0%     │ ≥60%     │ -60pp    │
│ fact_declaration F1  │ 0.0%     │ ≥50%     │ -50pp    │
└─────────────────────┴──────────┴──────────┴──────────┘
```

### V4-01~03: Weak Type Recovery (P0, Survival-Critical)

| Task | Type | Target | Approach |
|------|------|--------|---------|
| V4-01 | **task_pattern** | F1 0% → ≥50% | Investigate why direct test passes but benchmark fails; likely _is_noise over-filtering |
| V4-02 | **correction** | F1 0% → ≥60% | May be affected by priority reorder or noise filter |
| V4-03 | **fact_declaration** | F1 0% → ≥50% | Phase A tightening may be too aggressive; relax with tech-term requirement |

### V4-04~06: Overall Accuracy Push

| Task | Description |
|------|-------------|
| V4-04 | **Multi-type message handling**: When message matches multiple types, use confidence-based priority (reduce Type Mismatch from 27) |
| V4-05 | **Context-aware filtering**: Use message_history to distinguish acknowledgment-in-context from standalone acknowledgment |
| V4-06 | **MCE-Bench case expansion**: Add 50+ real-world messages from Claude Code / Cursor sessions |

### V4-07~08: Testing & Quality

| Task | Description |
|------|-------------|
| V4-07 | Full regression run (target: 881+ all green after changes) |
| V4-08 | MCE-Bench re-run (target: Accuracy ≥70%, F1 ≥85%) |

---

## Future Milestones (Post-v0.4, per v3.1 Consensus)

### ⚠️ IMPORTANT: Execution Order Principle

```
★★★★★ Engine First: Do NOT start Adapter work until:
  - MCE-Bench Accuracy ≥85%
  - All 7 types have F1 ≥50%
  - Engine tests remain zero-storage-dependency

Rationale from WORKBUDDY AI:
"Heart must be strong before building blood vessels."
```

### v0.5.0 — StorageAdapter ABC + Interface Spec

**Prerequisite**: v0.4.0 complete (Accuracy ≥85%)
**Effort**: ~1-2 person-days

| Task | Description |
|------|-------------|
| V5-01 | Finalize StorageAdapter ABC interface (`remember/recall/forget`) |
| V5-02 | Define `StoredMemory` dataclass (extends MemoryEntry with storage fields) |
| V5-03 | Write contract tests (`TestStorageAdapterContract`) for all future adapters |
| V5-04 | Document adapter development guide for community contributors |

```python
# Target Interface (v5-01)
class StorageAdapter(ABC):
    """Unified storage interface for MCE memory entries."""
    
    async def remember(self, entry: MemoryEntry) -> StoredMemory:
        """Store a memory entry. Returns stored version with metadata."""
        ...
    
    async def recall(self, query: str, filters: Dict = None, limit: int = 20) -> List[StoredMemory]:
        """Retrieve memories matching query and optional filters."""
        ...
    
    async def forget(self, memory_id: str) -> bool:
        """Delete a memory by ID. Returns True if deleted."""
        ...
    
    @property
    def name(self) -> str:
        """Human-readable adapter name (e.g., 'SQLite', 'Supermemory')."""
        ...
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """Supported features (e.g., {'vector_search': True, 'fts': False})."""
        ...
```

### v0.6.0 — SQLite Default Adapter

**Prerequisite**: v0.5.0 complete
**Effort**: ~3-5 person-days
**Positioning**: "Development/Demo default, NOT production recommendation"

| Task | Description | Priority |
|------|-------------|----------|
| V6-01 | SQLite database schema design (memories table + FTS5 index) | P0 |
| V6-02 | Basic CRUD implementation (remember/recall/forget) | P0 |
| V6-03 | FTS5 full-text search integration | P1 |
| V6-04 | Forgetting mechanism (tier-based expiry + time-based auto-cleanup) | P1 |
| V6-05 | CLI wrapper: `mce run` starts local server with SQLite backend | P2 |
| V6-06 | Adapter test suite (target ≥80% coverage, separate from Engine tests) | P0 |

**Quality Standard (per QA tiered approach)**:

| Component | Coverage Target | Key Metrics |
|----------|----------------|-------------|
| SQLiteAdapter | ≥80% | CRUD smoke test, FTS retrieval, forget verification |
| Contract Tests | 100% | All ABC methods tested with mock |
| Integration (Engine+SQLite) | ≥50% | End-to-end classify→store→recall flow |

### v0.7.0 — Official Downstream Adapters

**Prerequisite**: v0.6.0 stable
**Effort**: ~5-8 person-days (all adapters)

| Adapter | Priority | Effort | Use Case |
|---------|----------|--------|----------|
| **SupermemoryAdapter** | P0 | ~2d | Production users wanting cloud sync |
| **ObsidianAdapter** | P0 | ~1.5d | Note-taking / PKM users |
| **Mem0Adapter** | P1 | ~1.5d | Vector+graph hybrid users |
| **JSONFileAdapter** | P1 | ~0.5d | Simple local persistence |
| **PostgreSQLAdapter** | P2 | ~2d | Enterprise / team collaboration |

### v0.8.0 — Ecosystem & Polish

| Feature | Description |
|---------|-------------|
| Web Dashboard | Simple UI to browse classified memories (optional dependency) |
| Plugin System | Community adapter loading via entry_points |
| MCE-Bench Public | 180-case dataset + leaderboard format |
| i18n Expansion | FR/DE/KO locale support |

### v1.0.0 — Industry Standard Vision

- Classification accuracy >95% on clear messages
- Official adapters for 5+ downstream systems
- Community-contributed adapter ecosystem
- Academic paper potential: *"Why Classification Matters More Than Storage for AI Memory Systems"*

---

## Architecture Evolution

```
v0.2.0 (MONOLITHIC)               v0.3.0 (PURE UPSTREAM)          v0.4.0 (ENGINE OPTIMIZED)        v1.0.0 (VISION)
┌─────────────┐                   ┌─────────────┐                   ┌─────────────┐                   ┌─────────────┐
│  MCP Server  │                   │  MCP Server  │                   │  MCP Server  │                   │  MCP Server  │
│  11 tools    │                   │  4 tools     │                   │  4 tools     │                   │  4 tools     │
│  (8 deprec.) │ ──breaking─────▶  │  (pure class)│                   │  (pure class)│                   │  (pure class)│
└──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘
       │                                 │                                 │                                 │
┌──────▼──────┐                   ┌──────▼──────┐                   ┌──────▼──────┐                   ┌──────▼──────┐
│   Engine     │                   │   Engine     │                   │   Engine     │                   │   Engine     │
│  (monolithic)│                   │  (+to_memory  │                   │  (>95% acc.) │                   │  (>95% acc.) │
│             │                   │   _entry())   │                   │  (optimized)  │                   │  (industry)  │
└──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘
       │                                 │                                 │                                 │
┌──────▼──────┐                   ┌──────▼──────┐                   ┌──────▼──────┐                   ┌──────▼──────┐
│  SQLite     │                   │ Adapter ABC  │                   │ Adapter ABC  │                   │ Adapter Eco │
│  (hardcoded) │                   │  + BuiltIn   │                   │  + SQLite   │                   │ (5+ official)│
└─────────────┘                   │  (deprecated)│                   │  (default)   │                   │ + community │
                                 └─────────────┘                   └──────┬──────┘                   └─────────────┘
                                                                   │
                                                          ┌───────────┼───────────┐
                                                          ▼           ▼           ▼
                                                     [Supermem]   [Obsidian]   [Mem0]   [Custom]
                                                      (official)   (official)   (official)

━━━ v3.1 LAYERED DECOUPLING (NEW) ━━━━━━━━━━━━━━━━━━━━━

v0.3.1 (CURRENT — Post Phase A+B)      v0.5.0 (PLANNED)                  v0.7.0 (PLANNED)
┌─────────────────────┐            ┌─────────────────────┐            ┌─────────────────────┐
│  LAYER 1: ENGINE    │            │  LAYER 2: ABC       │            │  ADAPTERS           │
│  ★ Core Asset       │            │  Interface Spec     │            │  (Ecosystem)         │
│                     │            │                     │            │                     │
│  Precision: 94.1%   │            │  remember()         │            │  SupermemoryAdapter  │
│  F1: 84.2%          │   ──P0──▶  │  recall()           │   ──P0──▶   │  ObsidianAdapter     │
│  TN: 54 / FP: 1     │            │  forget()           │            │  Mem0Adapter         │
│  Tech terms: 200+   │            │                     │            │  Community adapters  │
│  MCE-Bench: 180     │            └──────────┬──────────┘            │  (via entry_points)  │
└──────────┬──────────┘                       │                       └─────────────────────┘
           │                                │
           │                    ┌───────────▼──────────┐
           │                    │  LAYER 3: DEFAULT     │
           │                    │  SQLite Adapter      │
           │                    │  (v0.6 target)        │
           │                    │                     │
           │                    │  • CRUD              │
           │                    │  • FTS5 search       │
           │                    │  • Forgetting        │
           │                    │  • Dev/Demo only     │
           │                    └─────────────────────┘
           │
           ▼
    (Future: when Engine ≥85%, build Adapters)
```

---

## Key Metrics Targets (Updated v3.1)

| Metric | v0.2.0 | v0.3.0 | **v0.3.1** (Current) | v0.4.0 (Target) | v1.0.0 (Vision) |
|--------|--------|--------|---------------------|-----------------|---------------|
| **MCP tools** | 11 (8 depr) | **4** (pure) | **4** (pure) | 4 | 4 |
| **Code (layer2_mcp/)** | ~1580 lines | **~650 lines** | **~650 lines** | ~600 | ~500 |
| **Test scenarios** | 92 (with DB) | **43** (no DB) | **881** (post-A+B) | 900+ | 1000+ |
| **Classification accuracy** | Unknown (~60%) | N/A | **38.9%** ⚠️ | **≥85%** | **>95%** |
| **Precision** | N/A | N/A | **94.1%** ✅ | ≥80% | >95% |
| **F1 Score** | N/A | N/A | **84.2%** ✅ | **≥82%** | >90% |
| **FP Rate** | High | N/A | **0.6%** ✅ | ≤10% | <5% |
| **Tech terms whitelist** | ~10 | ~10 | **200+** ✅ | 300+ | 500+ |
| **Storage Adapters** | 0 (hardcoded) | 1 (ABC defined) | **1 (ABC)** | **SQLite default** | **5+ official** |
| **User onboarding steps** | 7+ | 5 | **5** | **1** (SQLite) | **1** |

### MCE-Bench v1.0 Detailed Results (180 cases, Current)

| Category | Cases | Accuracy | Status |
|----------|-------|----------|--------|
| A: Positive (should remember) | 90 | TBD | Improving |
| B: Negative (noise to filter) | 55 | **98%** ✅ | Excellent |
| C: Edge cases | 35 | **100%** ✅ | Perfect |
| **Overall** | **180** | **38.9%** ⚠️ | In Progress |
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
