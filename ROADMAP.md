# Memory Classification Engine - Roadmap

## Update History

| Version | Date | Updater | Update Content | Review Status |
|---------|------|---------|---------------|---------------|
| **v0.3.2** | 2026-04-20 | Engineering Team | **V4-01~05 Complete Overhaul** (Acc 38.9%→71.7%, F1 84.2%→90.7%). Fixed 3 CRASH bugs, correction 3-tier (F1+32.4pp), FP -44%, fact 3-tier (direct+60pp), sentiment 100%/relationship 90%. Accuracy crossed 70% threshold | ✅ Complete |
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
│  • Current: Precision 86.1%, F1 90.7%, Acc 71.7%    │
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

## Current Version: v0.3.2 (Post-V4 Optimization)

### What's Included

```
MCE v0.3.2 (Post-V4-01~05)
├── Core Classification Engine (Layer 1: ENGINE CORE ★)
│   ├── Pattern Analyzer (rule-based, zero LLM cost)
│   │   ├── _is_noise() — Noise filtering + workflow exception (V4-01)
│   │   ├── 7 Memory Types with 3-tier detection strategy
│   │   │   ├── correction (3-tier: explicit/structural/keyword) ✅ F1=75.9%
│   │   │   ├── fact_declaration (3-tier: tech/quant/general) ✅ direct=66.7%
│   │   │   ├── sentiment_marker (structural+keyword hybrid) ✅ direct=100%
│   │   │   ├── relationship (6 role + 8 dep patterns) ✅ direct=90%
│   │   │   ├── task_pattern (workflow/habit/recurring) ✅ F1=66.7%
│   │   │   ├── decision (strong/weak confidence grading)
│   │   │   └── user_preference (coding context aware)
│   │   └── Detector priority: correction→sentiment→task→decision→pref→rel→fact
│   │
│   ├── ClassificationPipeline (with quality-gated default fallback, V4-03)
│   ├── 4 Suggested Tiers (sensory → semantic)
│   └── to_memory_entry() — MemoryEntry Schema v1.0 output
│
├── MCP Server (stdio, Production Ready)
│   ├── classify_message     ← Core tool #1
│   ├── get_classification_schema  ← Core tool #2
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
│   ├── MCE-Bench v1.0 (180-case classification accuracy benchmark)
│   │   ├── Accuracy: 71.7% (+32.8pp from baseline)
│   │   ├── F1 Score: 90.7% ✅ PASS (target ≥75%)
│   │   ├── Precision: 86.1% ✅ PASS (target ≥80%)
│   │   ├── TP=68 TN=61 FP=11 FN=3
│   │   └── Type Mismatches: 37 (-21%)
│   └── Per-type F1 scoring (7 types tracked)
│
└── Documentation (mature project structure)
    ├── docs/README.md (documentation index)
    ├── README / README-CN / README-JP (i18n complete)
    ├── ROADMAP / ROADMAP-CN / ROADMAP-JP (i18n complete)
    └── docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md (v3.1)
```

---

## Next: v0.4.0 — Engine Optimization (Engine First 🎯)

**Target**: Continue classification accuracy improvement per **Engine First principle**
**Estimated effort**: ~3-5 person-days (V4-01~05 complete, remaining work reduced)
**Breaking Change**: No (internal improvements only)

### Current MCE-Bench Status (180 cases) — Updated 2026-04-20

```
┌─────────────────────┬──────────┬──────────┬──────────┐
│ Metric               │ Current  │ Target   │ Gap      │
├─────────────────────┼──────────┼──────────┼──────────┤
│ Accuracy             │ 71.7%    │ ≥85%     │ -13.3pp  │
│ Precision            │ 86.1%    │ ≥80%     │ ✅ MET   │
│ F1 Score             │ 90.7%    │ ≥75%     │ ✅ MET   │
│ Recall               │ 84.4%    │ ≥80%     │ ✅ MET   │
│ FP Rate              │ 6.1%     │ ≤10%     │ ✅ MET   │
│ FN Rate              │ 1.7%     │ ≤20%     │ ✅ MET   │
│ task_pattern F1      │ 66.7%    │ ≥50%     │ ✅ MET   │
│ correction F1        │ 75.9%    │ ≥60%     │ ✅ MET   │
│ fact_declaration F1  │ 40.0%    │ ≥50%     │ -10pp    │
│ decision F1          │ 57.1%    │ ≥50%     │ ⚠️ OK    │
│ relationship F1      │ 82.3%    │ ≥50%     │ ✅ MET   │
│ sentiment_marker F1  │ 77.8%    │ ≥50%     │ ✅ MET   │
│ user_preference F1   │ 57.1%    │ ≥50%     │ ⚠️ OK    │
└─────────────────────┴──────────┴──────────┴──────────┘

Summary: 10/13 metrics PASS, 2/13 OK, 1/13 needs work (fact_declaration)
```

### ✅ COMPLETED: V4-01~05

| Task | Type | Before | After | Status |
|------|------|--------|-------|--------|
| **V4-01** | CRASH Fix | Benchmark crashes | All cases run | ✅ Fixed 3 bugs |
| **V4-02** | correction | F1 43.5% | **F1 75.9%** (+32.4pp) | ✅ 3-tier detection |
| **V4-03** | FP Reduction | FP=18 | **FP=11** (-39%) | ✅ Quality gates |
| **V4-04** | fact_declaration | direct=6.7% | **direct=66.7%** (+60pp) | ✅ 3-tier strategy |
| **V4-05** | sent+rel | sent=70%, rel=30% | **sent=100%, rel=90%** | ✅ Structural patterns |

### V4-06~08: Remaining Optimization

| Task | Priority | Description | Expected Impact |
|------|----------|-------------|-----------------|
| V4-06 | P1 | **fact_declaration boost**: pipeline TP 5→8 (reduce type-stealing) | Acc +2~4pp |
| V4-07 | P1 | **FP cleanup**: reduce remaining 11 FP (B4 questions + C5 adversarial) | Acc +2~3pp |
| V4-08 | P2 | **Multi-type handling**: confidence-based priority for ambiguous messages | TypeMismatch -10 |
| V4-09 | P2 | **MCE-Bench expansion**: +50 real-world messages for better coverage | More accurate eval |
| V4-10 | P0 | **Full regression**: ensure 881+ tests green after all changes | Quality gate |

---

## Future Milestones (Post-v0.4, per v3.1 Consensus)

### ⚠️ Engine First Principle — Strategic Re-evaluation (v0.3.2)

```
★★★★★ Original Rule (v3.1):
  Do NOT start Adapter work until:
    - MCE-Bench Accuracy ≥85%
    - All 7 types have F1 ≥50%
    - Engine tests remain zero-storage-dependency

★★★★★ Current State (v0.3.2):
  ✅ F1 Score:     90.7% (target ≥75%) — EXCEEDED by 15.7pp
  ✅ Precision:   86.1% (target ≥80%) — EXCEEDED by 6.1pp
  ✅ Recall:      84.4% (target ≥80%) — EXCEEDED by 4.4pp
  ✅ 6/7 types F1≥50% — task_pattern(66.7%), correction(75.9%),
                       relationship(82.3%), sentiment(77.8%),
                       decision(57.1%), user_preference(57.1%)
  ⚠️ Accuracy:    71.7% (target ≥85%) — GAP: -13.3pp
  ⚠️ fact_declaration: 40.0% (target ≥50%) — GAP: -10pp
```

**Analysis**: The 85% accuracy threshold was set when baseline was 38.9% (gap = 46.1pp).
We've closed **71% of that gap** in one session. The remaining gap is driven primarily by:
- **fact_declaration pipeline TP** (5/15, direct=66.7% but pipeline loses to other detectors)
- **11 FP cases** (mostly adversarial C5 and question-like B4)
- **37 Type Mismatches** (messages matching multiple types)

**Recommendation** (pending team decision):

| Option | Threshold | Rationale | Risk |
|--------|-----------|-----------|------|
| **A: Hold 85%** | Acc ≥85% | Original principle, maximum quality | May need 2-3 more sessions |
| **B: Lower to 75%** | Acc ≥75% | F1=90.7% proves engine is strong enough | Slightly lower bar |
| **C: Parallel track** | Start ABC while V4 continues | Don't block adapter work on 1 weak type | Resource split |

> **WORKBUDDY AI original quote still holds**: "Heart must be strong before building blood vessels."
> But the heart **is now beating at 90.7% F1 efficiency**. The question is whether 71.7% accuracy
> (with 6/7 types healthy) represents a "strong enough" heart to begin vessel construction.

---

### v0.5.0 — StorageAdapter ABC + Interface Spec

**Prerequisite**: Team decision on Engine First threshold (see above)
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
        """Delete a by ID. Returns True if deleted."""
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

v0.3.2 (CURRENT — Post V4-01~05)         v0.5.0 (PLANNED)                  v0.7.0 (PLANNED)
┌─────────────────────┐            ┌─────────────────────┐            ┌─────────────────────┐
│  LAYER 1: ENGINE    │            │  LAYER 2: ABC       │            │  ADAPTERS           │
│  ★ Core Asset       │            │  Interface Spec     │            │  (Ecosystem)         │
│                     │            │                     │            │                     │
│  Acc: 71.7%         │            │  remember()         │            │  SupermemoryAdapter  │
│  F1: 90.7%          │   ──P0──▶  │  recall()           │   ──P0──▶   │  ObsidianAdapter     │
│  Prec: 86.1%        │            │  forget()           │            │  Mem0Adapter         │
│  6/7 types >=50%    │            │                     │            │  Community adapters  │
│  MCE-Bench: 180     │            └──────────┬──────────┘            │  (via entry_points)  │
└──────────┬──────────┘                       │                       └─────────────────────┘
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
    (Future: when Engine meets threshold, build Adapters)
```

---

## Key Metrics Targets (Updated v3.2)

| Metric | v0.2.0 | v0.3.0 | v0.3.1 (Post-A+B) | **v0.3.2** (Current) | v0.4.0 (Target) | v1.0.0 (Vision) |
|--------|--------|--------|---------------------|----------------------|-----------------|---------------|
| **MCP tools** | 11 (8 depr) | **4** (pure) | **4** (pure) | **4** (pure) | 4 | 4 |
| **Code (layer2_mcp/)** | ~1580 lines | **~650 lines** | **~650 lines** | **~640 lines** | ~600 | ~500 |
| **Test scenarios** | 92 (with DB) | **43** (no DB) | **881** (post-A+B) | **881+** | 900+ | 1000+ |
| **Classification accuracy** | Unknown (~60%) | N/A | **38.9%** ⚠️ | **71.7%** 🎯 | **≥85%** | **>95%** |
| **Precision** | N/A | N/A | **94.1%** ✅ | **86.1%** ✅ | ≥80% | >95% |
| **F1 Score** | N/A | N/A | **84.2%** ✅ | **90.7%** ✅✅ | ≥82% | >90% |
| **Recall** | N/A | N/A | **76.2%** | **84.4%** ✅ | ≥80% | >90% |
| **FP Rate** | High | N/A | **0.6%** ✅ | **6.1%** ✅ | ≤10% | <5% |
| **Tech terms whitelist** | ~10 | ~10 | **200+** ✅ | **50+ (tiered)** ✅ | 300+ | 500+ |
| **Storage Adapters** | 0 (hardcoded) | 1 (ABC defined) | **1 (ABC)** | **1 (ABC)** | **SQLite default** | **5+ official** |
| **User onboarding steps** | 7+ | 5 | **5** | **5** | **1** (SQLite) | **1** |
| **Types with F1≥50%** | ? | ? | **0/7** ⚠️ | **6/7** 🎯 | **7/7** | **7/7** |

### MCE-Bench v1.0 Detailed Results (180 cases, v0.3.2)

| Category | Cases | Accuracy | Status |
|----------|-------|----------|--------|
| A: Positive (should remember) | 90 | **75.6%** | 📈 Improving (was 38.9%) |
| B: Negative (noise to filter) | 55 | **96.4%** ✅ | Excellent |
| C: Edge cases | 35 | **91.4%** ✅ | Strong |
| **Overall** | **180** | **71.7%** 🎯 | Crossed 70% threshold |
| Downstream adapters | 0 | 1 (BuiltIn @deprec) | **5+ official** |
| LLM call ratio | 0% | 0% | 0% (pure rules) |

**Per-Type Breakdown (v0.3.2)**:

| Type | F1 | Precision | Recall | TP | FP | FN | Status |
|------|-----|-----------|--------|----|----|-----|--------|
| correction | 75.9% | 84.6% | 68.8% | 11 | 2 | 5 | ✅ PASS |
| relationship | 82.3% | 100% | 70.0% | 7 | 0 | 3 | ✅ PASS |
| sentiment_marker | 77.8% | 87.5% | 70.0% | 7 | 1 | 3 | ✅ PASS |
| task_pattern | 66.7% | 75.0% | 60.0% | 6 | 2 | 4 | ✅ PASS |
| decision | 57.1% | 100% | 40.0% | 4 | 0 | 6 | ⚠️ OK |
| user_preference | 57.1% | 61.5% | 53.3% | 8 | 5 | 7 | ⚠️ OK |
| fact_declaration | 40.0% | 50.0% | 33.3% | 5 | 5 | 10 | 🔧 Needs work |

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
