# CarryMem Roadmap

**Current Version**: v0.3.0
**Last Updated**: 2026-04-22

**English** | [中文](ROADMAP-CN.md) | [日本語](ROADMAP-JP.md)

---

## Completed Milestones

### v0.1 — Classification Core
- Three-layer classification funnel (Rule → Pattern → Semantic)
- 7 memory types classification
- Basic rule matching engine

### v0.2 — Memory Types & Tiers
- 7 structured memory types
- 4-tier priority system with TTL
- Memory entry schema v1.0

### v0.3 — Tier System
- Sensory (24h) / Procedural (90d) / Episodic (365d) / Semantic (permanent)
- Tier-based storage and retrieval

### v0.4 — Confirmation Detection
- EN/CN/JP confirmation pattern detection
- Context-aware exception handling

### v0.5 — CarryMem Main Class
- `classify_message()` — pure classification
- `classify_and_remember()` — classify + store
- `recall_memories()` / `forget_memory()`
- Pure Upstream mode (no storage required)

### v0.6 — SQLite Adapter
- FTS5 full-text search
- Content deduplication
- Tier-based TTL auto-expiry
- `CarryMem(storage="sqlite")` default

### v0.7 — Obsidian Knowledge Base
- ObsidianAdapter (read-only)
- Markdown直读 + FTS5 + YAML frontmatter + wiki-links
- MCP 3+3+3 mode (Core + Storage + Knowledge)
- `recall_all()` unified retrieval

### v0.8 — Active Declaration & Memory Profile
- `declare()` — active declaration (confidence=1.0, source_layer="declaration")
- `get_memory_profile()` — structured memory aggregation
- MCP 3+3+3+2 mode (+ Profile tools)

### v0.9 — Namespace Isolation
- Project-level memory isolation via namespace
- Cross-namespace recall support
- SQLite namespace column + auto-migration

### v0.10 — Smart Scheduling & Plugin System & MCE-Bench
- `build_system_prompt()` — EN/CN/JP prompt templates with memory-first priority
- Plugin adapter loader via entry_points
- MCE-Bench: 180-case public benchmark dataset (EN/CN/JP × 60)
- MCP 3+3+3+2+1 mode (+ Prompt tool)

### v0.3.0 — Project Cleanup & Refactoring
- Engine slim refactoring (2263 → 182 lines)
- Removed enterprise features (tenants, access control, encryption, distributed)
- Deleted legacy directories and files
- Unified test suite (125/125 passing)
- README rewrite with comparison table

### v0.3.0+ — Multilingual Enhancement & Portability
- Full Chinese/Japanese classification rules (ZH 79.1%→91.0%, JA 76.1%→89.6%)
- Fixed Japanese language detection (hiragana/katakana check before CJK)
- Fixed CJK short message thresholds
- `export_memories()` — JSON + Markdown export
- `import_memories()` — JSON import with skip_existing merge strategy
- PyPI packaging (setup.py + pyproject.toml + MANIFEST.in)
- 125 tests passing (EN×7 + ZH×7 + JA×7 + noise×3 + integration + export/import + edge)

---

## Next Phase Priorities

### Priority 1: Memory Merge & Conflict Resolution
- Multi-agent memory consistency
- Conflict detection and resolution strategies
- Memory versioning

### Priority 2: MCP Remote Mode
- stdio → SSE/Streamable HTTP transport
- Remote CarryMem server deployment
- Multi-client support

### Priority 3: Additional Adapters
- Redis adapter (distributed storage)
- PostgreSQL adapter (enterprise storage)
- S3/R2 adapter (cloud storage)

---

## Long-term Vision

**CarryMem = The USB-C of AI Memory**

Just like USB-C standardized device connectivity, CarryMem aims to standardize AI memory:
- **One format**: MemoryEntry JSON Schema v1.0
- **Any storage**: SQLite, Obsidian, Redis, PostgreSQL, or your custom adapter
- **Any tool**: MCP protocol for universal Agent integration
- **Your data**: Memory belongs to the user, not the tool

> "Don't remember everything. Remember what matters."
