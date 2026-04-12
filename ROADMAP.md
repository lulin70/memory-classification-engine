# Memory Classification Engine - Roadmap

## Update History

| Version | Date | Updater | Update Content | Review Status |
|---------|------|---------|---------------|---------------|
| v1.2.0 | 2026-04-12 | Product Team | Added VS Code extension, memory quality dashboard, pending memory mechanism, and Nudge mechanism | Reviewed |
| v1.1.0 | 2026-04-11 | Product Team | MCP Server completed, Beta testing started | Reviewed |
| v1.0.0 | 2026-04-10 | Product Team | Initial version - Three-layer integration strategy planning | Reviewed |

---

## 🎯 Vision

To become the standard component in the field of Agent memory classification, just like ChromaDB is for vector storage, to become synonymous with memory classification.

---

## Three-Layer Integration Strategy

### Layer 1: Python SDK ✅ (Completed)

**Status**: Available

**Goal**: Provide the most basic Python library that anyone can pip install and integrate

**Core Features**:
- [x] Real-time message classification
- [x] 7 memory type identification
- [x] Three-layer judgment pipeline
- [x] Four-tier memory storage
- [x] Active forgetting mechanism
- [x] VS Code extension
- [x] Memory quality dashboard
- [x] Pending memory mechanism
- [x] Nudge active review mechanism

**Next Optimizations**:
- [ ] Improve API documentation
- [ ] Add more usage examples
- [ ] Performance optimization

---

### Layer 2: MCP Server ⭐ (Beta Testing)

**Status**: ✅ Core functionality completed, Beta testing in progress

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
- [x] `retrieve_memories` - Retrieve related memories
- [x] `get_memory_stats` - Get memory statistics
- [x] `batch_classify` - Batch classification
- [x] `find_similar` - Find similar memories
- [x] `export_memories` - Export memories
- [x] `import_memories` - Import memories

#### Phase 2: OpenClaw Integration ✅ (Completed)

- [x] OpenClaw adapter
- [x] OpenClaw configuration file
- [x] Usage examples and documentation

**Technical Solution**:

```python
# MCP Server architecture
mcp-server/
├── src/
│   └── mce_mcp_server/
│       ├── server.py      # MCP Server main entry
│       ├── tools.py       # Tool definitions
│       └── config.py      # Configuration management
├── pyproject.toml
└── README.md
```

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

### Code Quality Optimization (Ongoing)

**Completed**:
- [x] Fix P0/P1 code quality issues
- [x] Engine class split refactoring (Facade pattern)
- [x] Service layer architecture implementation
- [x] Code review checklist
- [x] Static code analysis tool configuration

**In Progress**:
- [ ] Improve unit test coverage
- [ ] Performance benchmarking
- [ ] Documentation improvement

**Planned**:
- [ ] Introduce dependency injection framework
- [ ] Improve error handling mechanism
- [ ] Optimize storage layer performance

---

## Promotion and Operation Plan

### Phase 1: MCP Server Launch ✅ (In Progress)

**Technical Work**:
- [x] Implement MCP Server core functionality (8 tools)
- [x] Write MCP configuration documentation
- [x] Create Claude Code usage examples
- [x] Complete 27 unit tests
- [ ] OpenClaw integration
- [ ] Release to PyPI

**Promotion Work**:
- [x] Create Beta testing guide (English and Chinese)
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
- [API Documentation](docs/api/api.md)
- [User Guide](docs/user_guides/user_guide.md)
- [Code Quality Fixes](docs/code_quality_fixes.md)

### Related Links

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [OpenClaw Project](https://github.com/openclaw)

---

**Document Version**: v1.2.0  
**Last Updated**: 2026-04-12  
**Review Status**: Reviewed