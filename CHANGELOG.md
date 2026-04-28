# Changelog

All notable changes to CarryMem will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.2] - 2026-04-28

### Added
- `carrymem whoami` — AI identity portrait showing preferences, decisions, corrections
- `carrymem profile export` — export identity as JSON for cross-AI portability
- `CarryMem.whoami()` — API method returning structured identity summary
- `CarryMem.export_profile()` — API method exporting full identity profile
- Competitive analysis document (COMPETITIVE_ANALYSIS.md)
- Product positioned as "AI Identity Layer" vs competitors' "Knowledge Layer"

### Fixed
- `conflict_detector._detect_outdated()`: offset-naive vs offset-aware datetime crash
- `conflict_detector._supersedes()`: same datetime comparison issue
- `carrymem.list_expired()`: `conn.close()` was closing thread-local connection
- Python 3.9 f-string backslash compatibility (6 fixes)
- `carrymem.py`: added missing `Path` import for `export_profile()`

## [0.8.1] - 2026-04-27

### Added
- `carrymem show <key>` — detailed memory card view with all metadata
- `carrymem edit <key> <content>` — update memory content with confirmation
- `carrymem clean` — remove expired/low-quality memories (--dry-run, --expired, --quality)
- `carrymem add --force` — bypass classification, always store the message
- Color output: green/red/yellow/cyan/dim/bold for better readability
- Unified memory card format (`_print_memory_card`)
- Command aliases: `ls`=list, `get`=show, `update`=edit
- Doctor now checks for `textual` dependency

### Fixed
- `update_memory()` called with dict instead of string in `cmd_edit()`
- Python 3.9 f-string backslash compatibility (4 fixes)

## [0.8.0] - 2026-04-27

### Added
- Complete CLI rewrite: 19 commands (add/list/search/show/edit/forget/clean/export/import/stats/check/doctor/setup-mcp/tui/serve/init/version/whoami/profile)
- `carrymem setup-mcp` — one-line MCP configuration for Cursor/Claude Code
- `carrymem doctor` — 11 diagnostic checks with `--fix` auto-repair
- `carrymem tui` — Textual terminal UI with sidebar filters, search, add mode
- `carrymem check` — quality & conflict check (--conflicts/--quality/--expired)
- `CarryMem.check_conflicts()` — detect contradictions, duplicates, superseded memories
- `CarryMem.check_quality()` — identify low-quality memories
- `CarryMem.list_expired()` — find expired memories
- CI/CD: GitHub Actions with quality lint, multi-Python testing, build validation
- `setup.py` extras: `pip install carrymem[tui]`, `pip install carrymem[encryption]`

### Fixed
- `ConflictDetector`: use `getattr` for namespace (StoredMemory compatibility)

## [0.7.0] - 2026-04-26

### Added
- MCP HTTP/SSE server (`MCPHTTPServer`) with API key auth
- JSON adapter (`JSONAdapter`) — zero-dependency file-based storage
- Async API (`AsyncCarryMem`) — `run_in_executor` wrapper
- Integration configs for Claude Code and Cursor
- `StoredMemory.from_dict()` — full deserialization including new fields

### Fixed
- AsyncCarryMem `:memory:` SQLite thread issue — use temp file instead
- JSONAdapter forget logic — proper key removal

## [0.6.0] - 2026-04-25

### Added
- Data encryption (`MemoryEncryption`) — Fernet/HMAC-CTR dual backend
- Automatic backup (`BackupManager`) — VACUUM INTO with FIFO cleanup
- Audit logging (`AuditLogger`) — append-only operation history

### Fixed
- `rollback_memory()` deadlock — split into `_update_memory_impl()` (no lock) and `update_memory()` (with lock)
- Schema migration index error — moved indexes to `_migrate_v050()`

## [0.5.0] - 2026-04-24

### Added
- Importance scoring (`scoring.py`) — confidence × type_weight × recency × access
- Query cache (`RecallCache`) — LRU + TTL with write-through invalidation
- Smart context injection (`context.py`) — token budget, relevance ranking
- Memory merge (`merge.py`) — conflict detection, 3 strategies
- Memory versioning — `memory_versions` table, `update_memory()`, `rollback_memory()`
- `build_context()` — structured dict with system_prompt, memories, knowledge

### Fixed
- Cache TTL test hanging — manipulate `expires_at` instead of `time.sleep()`
- `_update_memory_impl` indentation error after SearchReplace

## [0.4.1] - 2024-12-01

### Fixed
- Thread safety issues in SQLiteAdapter (ThreadLocal connections)
- Resource leaks from unclosed database connections
- Potential race conditions in multi-threaded environments
- Memory leak in MemoryClassificationEngine (`message_history` unbounded growth)

### Security
- Fixed potential SQL injection risks in dynamic query construction
- Improved input validation

## [0.4.0] - 2024-11-15

### Added
- Semantic recall with synonym expansion, spell correction, cross-language mapping
- FTS5 full-text search with trigram tokenizer for CJK support
- Content deduplication via `content_hash`

## [0.3.0] - 2024-10-01

### Added
- Obsidian knowledge base adapter
- Multi-namespace support
- Memory profile and statistics

## [0.2.0] - 2024-09-01

### Added
- Three-tier classification engine (Rule → Pattern → Semantic)
- Seven memory types with confidence scoring
- SQLite default storage adapter
- MCP protocol support (stdio)
