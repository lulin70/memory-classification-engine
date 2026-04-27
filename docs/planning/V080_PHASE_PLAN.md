# CarryMem v0.8.0 Implementation Plan — User Experience Leap

**Version**: v0.8.0  
**Date**: 2026-04-27  
**Status**: COMPLETED  
**Based on**: SEVEN_MEMBER_VOTE_CONSENSUS.md

---

## Goal

**"Let users fall in love with CarryMem in 5 minutes"**

Evolve from "technical prototype (8/10)" to "usable tool (8/10)".

---

## Sprint 1: Core Experience (P0) — COMPLETED

### 8.1 Enhanced CLI
- **Status**: ✅ Completed
- **Changes**: Complete rewrite of cli.py with add/list/search/forget/export/import/stats commands
- **Features**:
  - `carrymem add "message"` — classify and store
  - `carrymem list` — list memories with type icons, confidence, importance
  - `carrymem search "query"` — search with filters
  - `carrymem forget <key>` — delete with confirmation
  - `carrymem export <path>` — JSON/Markdown export
  - `carrymem import <path>` — import with merge strategy
  - `carrymem stats` — visual statistics with type bars
  - Multiple output formats: table, json, plain
  - Alias support: find=search, delete/rm=forget
- **Tests**: 45 new tests in test_v080_cli.py

### 8.2 Simplified MCP Configuration
- **Status**: ✅ Completed
- **Changes**: `carrymem setup-mcp` command
- **Features**:
  - `--tool cursor/claude-code/all` selection
  - Auto-detect Python path for MCP command
  - Merge with existing MCP configs (preserve other tools)
  - Idempotent: skip if already configured
  - `--force` to overwrite
- **Tests**: 6 tests in test_v080_cli.py (TestCmdSetupMcp)

### 8.3 carrymem doctor
- **Status**: ✅ Completed
- **Changes**: `carrymem doctor` command with 11 checks
- **Features**:
  - Python version check (>= 3.9)
  - CarryMem import check
  - Config directory check
  - Database file check
  - Database integrity check (PRAGMA integrity_check)
  - Write permissions check
  - Optional dependencies check (pycld2, cryptography, langdetect)
  - FTS5 support check
  - Security module check
  - MCP integration status check
  - Memory count check
  - `--fix` flag for auto-fix
- **Tests**: 4 tests in test_v080_cli.py (TestCmdDoctor)

---

## Sprint 2: Visual Experience (P1) — COMPLETED

### 8.4 Simple TUI
- **Status**: ✅ Completed
- **Changes**: New tui.py module with Textual framework
- **Features**:
  - `carrymem tui` command
  - Sidebar with filters (All/Preferences/Facts/Corrections)
  - Search bar with add mode toggle
  - Memory list with type icons, confidence, importance
  - Keyboard shortcuts: s=search, a=add, r=refresh, q=quit
  - Graceful fallback if textual not installed
- **Dependency**: textual>=0.40 (optional, `pip install carrymem[tui]`)

### 8.5 Memory Quality Management
- **Status**: ✅ Completed
- **Changes**: Integrated ConflictDetector and MemoryQualityScorer into CarryMem API
- **New API methods**:
  - `check_conflicts()` — detect contradictions, duplicates, superseded memories
  - `check_quality(min_score)` — identify low-quality memories
  - `list_expired()` — find expired memories
- **New CLI command**: `carrymem check [--conflicts] [--quality] [--expired] [--all]`
- **Bug fix**: ConflictDetector now uses `getattr` for namespace (StoredMemory doesn't have namespace attribute)
- **Tests**: 12 new tests in test_v080_quality.py

### 8.6 CI/CD Basics
- **Status**: ✅ Completed
- **Changes**: Enhanced .github/workflows/ci.yml
- **Features**:
  - Quality job: flake8, black, isort, mypy
  - Test job: Python 3.9/3.10/3.11/3.12 × ubuntu/macos
  - Build job: python -m build + twine check
  - Coverage upload to codecov
  - Dependency caching

---

## Sprint 3: Ecosystem Preparation (P1) — COMPLETED

### 8.7 Cursor Integration Optimization
- **Status**: ✅ Completed (via setup-mcp)
- **The setup-mcp command handles Cursor configuration automatically**

### 8.8 PyPI Publish Preparation
- **Status**: ✅ Completed
- **Changes**:
  - setup.py updated with version 0.8.0
  - extras_require: encryption, tui
  - CI build job validates package with twine check
  - Package structure verified

---

## Test Results

| Category | Count |
|----------|-------|
| Original tests (v0.4-v0.7) | 332 |
| CLI tests (test_v080_cli.py) | 45 |
| Quality tests (test_v080_quality.py) | 12 |
| **Total** | **389** |

All 389 tests passing.

---

## Files Changed/Created

### New Files
- `src/memory_classification_engine/tui.py` — Textual TUI
- `tests/test_v080_cli.py` — CLI tests
- `tests/test_v080_quality.py` — Quality management tests

### Major Changes
- `src/memory_classification_engine/cli.py` — Complete rewrite (enhanced CLI)
- `src/memory_classification_engine/carrymem.py` — Added check_conflicts, check_quality, list_expired
- `src/memory_classification_engine/conflict_detector.py` — Fixed namespace attribute access
- `.github/workflows/ci.yml` — Enhanced CI/CD pipeline

### Version Updates
- `__version__.py` — 0.7.0 → 0.8.0
- `setup.py` — 0.7.0 → 0.8.0, added tui extras
- `__init__.py` — Updated docstring
- `README.md` — Version badge updated
