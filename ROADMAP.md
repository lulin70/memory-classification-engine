# Memory Classification Engine - Roadmap

## Update History

| Version | Date | Updater | Update Content | Review Status |
|---------|------|---------|---------------|---------------|
| v0.2.0 | 2026-04-18 | Engineering Team | Phase 1 optimization complete (-74% process_message), Phase 2 features delivered (adaptive retrieval, feedback loop, distillation), MCP Server promoted to Production v1.0.0, test suite expanded to **874 tests**, documentation updated across EN/ZH/JP, Demo test 26/30 (87%) passing | Reviewed |
| v1.2.0 | 2026-04-12 | Product Team | Added VS Code extension, memory quality dashboard, pending memory mechanism, and Nudge mechanism | Reviewed |
| v1.1.0 | 2026-04-11 | Product Team | MCP Server completed, Beta testing started | Reviewed |
| v1.0.0 | 2026-04-10 | Product Team | Initial version - Three-layer integration strategy planning | Reviewed |

---

## Vision

To become the standard component in the field of Agent memory classification, just like ChromaDB is for vector storage, to become synonymous with memory classification.

**Product positioning**: "Don't remember everything. Remember what matters." — A lightweight, high-efficiency professional AI Agent memory classification engine.

---

## Completed Milestones

### Phase 1: Performance Optimization ✅ (Completed 2026-04-17)

**Status**: All tasks complete, verified by benchmark

**Deliverables**:

| Task | Description | Result |
|------|-------------|--------|
| T1.1 | Performance baseline established | `benchmarks/baseline_benchmark.py` created |
| T1.2 | FAISS dimension mismatch fix | Eliminated AssertionError on every `process_message` call |
| T1.3 | SmartCache rewrite (OrderedDict + LRU) | O(1) eviction vs old O(n) scan |
| T1.4 | Cache warmup at engine startup | Cache hit rate: 0% → **97.83%** |
| T1.5 | Parallel query (ThreadPoolExecutor) | Concurrent tier2/tier3/tier4 retrieval |
| T1.6 | Hash index for get_memory | O(1) lookup via `_id_index` dict |
| T1.7 | Archive fix (selective invalidation) | `_run_archive` no longer clears entire cache |
| T1.8 | Semantic sort deep optimization | Batch encoding + pre-computed keys: P99 **-41%** |
| T1.9 | Final benchmark verification | `process_message` P99: **-74%** overall |

**Key metrics before/after**:
- `process_message` P99: 5,669ms → 1,452ms (**-74%**)
- `retrieve_memories` long-sentence P99: 85ms → 50ms (**-41%**)
- Cache hit rate: 0% → **97.83%**
- Test count: 661 → **696**

### Phase 2: v2.0 Features ✅ (Completed 2026-04-17)

**Status**: All features delivered

#### P0: Adaptive Retrieval Modes ✅

Three retrieval modes for different scenarios:

| Mode | Latency Target | Strategy |
|------|---------------|----------|
| `compact` | <10ms | Keyword match only, skip semantic sort |
| `balanced` | ~15-50ms | Default mode with optimized semantic pipeline |
| `comprehensive` | 50-200ms | Full analysis with associations + composite scoring |

Implementation: `engine.py` `retrieve_memories()` now accepts `retrieval_mode` parameter, dispatches to `_retrieve_compact()`, `_retrieve_balanced()`, or `_retrieve_comprehensive()`.

#### P1: Feedback Loop Automation ✅

Automated pattern detection and rule tuning from user corrections:

- **FeedbackEvent / FeedbackAnalyzer**: Detects patterns (min 3 occurrences)
- **RuleTuner**: Generates rule suggestions from patterns
- **FeedbackLoop**: Auto-applies rules when confidence > threshold (default 0.8)

File: [feedback_loop.py](../src/memory_classification_engine/layers/feedback_loop.py)

#### P2: Model Distillation Interface ✅

Cost-aware routing for production deployments:

- **ConfidenceEstimator**: Estimates classification difficulty
- **DistillationRouter**: Routes to embedding-only (>0.85), weak model (0.5-0.85), or strong model (<0.5)
- Supports offline training data export for model distillation

File: [distillation.py](../src/memory_classification_engine/layers/distillation.py)

### MCP Server Production Release ✅ (v1.0.0)

**Status**: Promoted from Beta to Production

- VERSION = "1.0.0" set in MCPServer class
- PROTOCOL_VERSION = "2024-11-05"
- Full API reference documented: [API_REFERENCE_V1.md](./docs/api/API_REFERENCE_V1.md)
- 11 MCP tools available

---

## Three-Layer Integration Strategy

### Layer 1: Python SDK ✅ (Completed & Optimized)

**Status**: Available, performance optimized in Phase 1

**Goal**: Provide the most basic Python library that anyone can pip install and integrate

**Core Features**:
- [x] Real-time message classification
- [x] 7 memory type identification
- [x] Three-layer judgment pipeline
- [x] Four-tier memory storage
- [x] Active forgetting mechanism
- [x] Adaptive retrieval modes (compact/balanced/comprehensive)
- [x] Feedback loop automation
- [x] Model distillation interface
- [x] SmartCache with warmup (97.83% hit rate)
- [x] Parallel query across storage tiers
- [x] Hash index for O(1) lookups
- [x] VS Code extension
- [x] Memory quality dashboard
- [x] Pending memory mechanism
- [x] Nudge active review mechanism

---

### Layer 2: MCP Server ✅ (Production v1.0.0)

**Status**: Production release complete

**Goal**: Allow Claude Code, Cursor, OpenClaw and other MCP-supported tools to call directly

**Why prioritize MCP?**

| Advantage | Description |
|-----------|-------------|
| Trend | Anthropic is heavily promoting MCP, related repositories are growing fast |
| Targeted users | Claude Code / Cursor users are exactly the target audience |
| Low investment | Low packaging cost (JSON-RPC interface layer) |
| High conversion | Zero-friction usage, high Topic traffic conversion rate |

**Feature Planning**:

#### Phase 1: Core MCP Tools ✅ (Completed)

- [x] `classify_memory` - Analyze messages and determine if memory is needed
- [x] `store_memory` - Store memory to the appropriate tier
- [x] `retrieve_memories` - Retrieve related memories (supports adaptive modes)
- [x] `get_memory_stats` - Get memory statistics
- [x] `batch_classify` - Batch classification
- [x] `find_similar` - Find similar memories
- [x] `export_memories` - Export memories
- [x] `import_memories` - Import memories

#### Phase 2: OpenClaw Integration ✅ (Completed)

- [x] OpenClaw adapter
- [x] OpenClaw configuration file
- [x] Usage examples and documentation

**Release Plan**:
- PyPI package name: `mce-mcp-server`
- Submit to MCP community repository
- Share in Claude Code / Cursor community

---

### Layer 3: Framework Adapters (Long-term)

**Status**: Planning

**Goal**: Provide out-of-the-box Skill packaging for mainstream Agent frameworks

**Framework Adaptation Plan**:

#### LangChain (Priority: High)

```python
from memory_classification_engine.adapters.langchain import MemoryClassifierTool

tool = MemoryClassifierTool()
```

**Features**:
- [ ] MemoryClassifierTool class
- [ ] Integration with LangChain Memory
- [ ] Usage documentation and examples

#### CrewAI (Priority: Medium)

```python
from memory_classification_engine.adapters.crewai import MemoryTool

tool = MemoryTool()
```

**Features**:
- [ ] MemoryTool class
- [ ] Integration with CrewAI Agent
- [ ] Usage documentation and examples

#### AutoGen (Priority: Medium)

```python
from memory_classification_engine.adapters.autogen import MemoryAgent

agent = MemoryAgent()
```

**Features**:
- [ ] MemoryAgent component
- [ ] Integration with AutoGen conversations
- [ ] Usage documentation and examples

---

## Technical Debt Cleanup

### Code Quality Optimization ✅ (Completed)

**Completed**:
- [x] Fix P0/P1 code quality issues
- [x] Engine class split refactoring (Facade pattern)
- [x] Service layer architecture implementation
- [x] Code review checklist
- [x] Static code analysis tool configuration
- [x] Phase 1 performance optimization (9 tasks)
- [x] Phase 2 v2.0 feature delivery (3 major features)
- [x] English code comments added (394 placeholders fixed)
- [x] Documentation updated across EN/ZH/JP (README, ROADMAP, design, architecture, testing, API, installation)

**Planned**:
- [ ] Introduce dependency injection framework
- [ ] Improve error handling mechanism
- [ ] Further storage layer performance tuning

---

## Promotion and Operation Plan

### Phase 1: MCP Server Launch ✅ (Complete)

**Technical Work**:
- [x] Implement MCP Server core functionality (11 tools)
- [x] Write MCP configuration documentation
- [x] Create Claude Code usage examples
- [x] Complete 27 unit tests → expanded to 696 total tests
- [x] OpenClaw integration
- [x] Promote to Production v1.0.0
- [ ] Release to PyPI

**Promotion Work**:
- [x] Create Beta testing guide (English and Chinese)
- [x] Create comprehensive API reference (API_REFERENCE_V1.md)
- [x] Create multi-role consensus optimization roadmap
- [ ] Submit to MCP community repository
- [ ] Share in Claude Code Discord
- [ ] Write technical blog

### Phase 2: Community Building (Month 2-3)

**Content Marketing**:
- Blog post: "Why Your Agent Needs Professional Memory Classification"
- Demo video: Claude Code + MCE demonstration
- User cases: Real usage scenarios

**Community Operations**:
- Reddit r/ClaudeAI
- Hacker News Show
- Twitter/X tech circle
- GitHub Discussions

### Phase 3: Framework Integration (Month 3-6)

**Technical Work**:
- LangChain adapter
- CrewAI adapter
- AutoGen adapter

**Promotion Work**:
- Submit PRs to each framework community
- Write integration tutorials
- Provide comparison benchmarks

---

## Key Milestones

| Time | Milestone | Key Metrics | Status |
|------|-----------|-------------|--------|
| 2026-04-11 | MCP Server Beta testing launch | Beta testing guide published | ✅ Completed |
| 2026-04-17 | Phase 1 Optimization complete | process_message -74%, cache 97.83% | ✅ Completed |
| 2026-04-17 | Phase 2 v2.0 Features delivered | Adaptive retrieval, feedback loop, distillation | ✅ Completed |
| 2026-04-17 | MCP Server Production v1.0.0 | VERSION=1.0.0, PROTOCOL_VERSION set | ✅ Completed |
| 2026-04-17 | Documentation update cycle | README/ROADMAP EN/ZH/JP, design/arch/test/API docs | ✅ In Progress |
| Month 1 | MCP Server official release | GitHub Stars: 200+ | 🔄 In Progress |
| Month 2 | Initial community establishment | Stars: 500+, community members: 50+ | ⏳ To Start |
| Month 3 | LangChain adaptation | Stars: 800+, downloads: 1000/month | ⏳ To Start |
| Month 6 | Complete ecosystem | Stars: 1500+, downloads: 5000/month | ⏳ To Start |

---

## Decision Records

### Why not make a Skill framework?

**Discussion**: Should we make it a framework like LangChain?

**Decision**: Not a framework, focus on engine

**Reasons**:
1. Framework competition is fierce (LangChain, LlamaIndex, etc.)
2. Engine positioning is clearer, with obvious differentiation
3. Easier to be integrated by other frameworks
4. Lower maintenance cost

### Why MCP Server priority over Framework Adapters?

**Discussion**: Should we do LangChain adaptation first?

**Decision**: MCP Server priority

**Reasons**:
1. MCP is a trend, Anthropic is heavily promoting it
2. Higher investment return ratio (low packaging cost, targeted users)
3. LangChain adaptation can be done as Layer 3 later
4. MCP users are more willing to try new tools

---

## Appendix

### Related Documents

- [Architecture Design](docs/architecture/architecture.md)
- [Architecture Design (ZH)](docs/architecture/architecture-zh.md)
- [Design Document](docs/design.md)
- [Design Document (ZH)](docs/design-zh.md)
- [Design Document (JP)](docs/design-jp.md)
- [API Reference](docs/api/API_REFERENCE_V1.md)
- [Optimization Roadmap](docs/OPTIMIZATION_ROADMAP_V1.md)
- [User Guide](docs/user_guides/user_guide.md)
- [User Guide (ZH)](docs/user_guides/user_guide-zh.md)
- [User Guide (JP)](docs/user_guides/user_guide-jp.md)
- [Installation Guide](docs/user_guides/installation_guide.md)
- [Test Plan V2](docs/testing/MCE_TEST_PLAN_V2.md)

### Related Links

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [OpenClaw Project](https://github.com/openclaw)

---

**Document Version**: v2.0.0
**Last Updated**: 2026-04-17
**Review Status**: Reviewed
