# Release v0.1.2 — Production-Ready First Release

## 🎯 What is CarryMem?

CarryMem is a **portable AI memory layer** — your AI's persistent identity that travels across tools and sessions. It automatically classifies, stores, and recalls your preferences, decisions, and corrections.

## ✨ Key Features

- **7-Type Automatic Classification** — user_preference, correction, fact_declaration, decision, relationship, task_pattern, sentiment_marker
- **Semantic Recall** — Cross-language search (EN/CN/JP) with synonym expansion and spell correction
- **AI Identity Layer** — `whoami` and `profile export` for personalized AI interactions
- **MCP Integration** — Works with Claude Code, Cursor, and Trae via Model Context Protocol
- **Obsidian Integration** — Index and search your Obsidian vault as knowledge base
- **Data Security** — AES encryption, auto-backup with rollback, audit logging, input validation
- **19 CLI Commands + TUI** — Full-featured terminal interface
- **490 Tests** — Comprehensive test coverage

## 🚀 Quick Start

```bash
pip install carrymem

# Add a memory
carrymem add "I prefer dark mode"

# Search memories
carrymem search "dark"

# Set up MCP integration
carrymem setup-mcp --tool cursor

# See your AI identity
carrymem whoami
```

## 🐛 Bug Fixes (from code review)

### CRITICAL (6)
- Cache invalidation logic was completely non-functional
- Double encryption during memory rollback
- Preference type name mismatch preventing conflict detection
- CLI update_memory success check always returned True
- No safety backup during restore
- Over-aggressive SQL injection detection blocking legitimate text

### HIGH (7)
- N+1 query pattern in recall (fixed with batch updates)
- Multi-thread connection leaks (fixed with connection registry)
- Async HTTP handlers blocking event loop (fixed with run_in_executor)
- InputValidator type mismatch with actual memory types
- API Key comparison vulnerable to timing attacks (fixed with hmac.compare_digest)
- CORS wildcard allowing any origin (fixed with configurable allowed_origins)
- ObsidianAdapter() crash without vault_path argument

### MEDIUM (4)
- StoredMemory missing namespace attribute
- validate_filters signature mismatch
- Conflict detection only checking 2 of 7 types
- PyYAML hard dependency causing import failure

## 🔒 Security Improvements
- `hmac.compare_digest()` for constant-time API key comparison
- Configurable CORS origins (default: localhost only)
- Input validator patterns tuned to reduce false positives
- Pre-restore safety backup with automatic rollback

## ⚡ Performance Improvements
- Batch SQL updates (executemany) instead of N+1 individual queries
- Connection registry for proper multi-thread cleanup
- Bucketed conflict detection (O(n²) → O(n·k))
- Direct key lookup via `_get_by_key()` instead of full table scan

## 📦 Installation

```bash
pip install -e .
# or
pip install carrymem
```

## 🔗 Integration

### Claude Code / Cursor
```bash
carrymem setup-mcp --tool all
```

### HTTP/SSE Server
```bash
carrymem serve --port 8765
```

### Obsidian Vault
```python
from carrymem import CarryMem
from carrymem.adapters.obsidian_adapter import ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()
results = cm.recall_from_knowledge("Python")
```
