#!/usr/bin/env python3
"""CarryMem CLI - Your Portable AI Memory Layer.

Usage:
    carrymem add "I prefer dark mode"     Store a memory
    carrymem list                         List recent memories
    carrymem search "theme"               Search memories
    carrymem forget <id>                  Delete a memory
    carrymem export backup.json           Export memories
    carrymem import backup.json           Import memories
    carrymem stats                        Show statistics
    carrymem doctor                       Run diagnostics
    carrymem setup-mcp --tool cursor      Configure MCP integration
    carrymem tui                          Launch terminal UI
    carrymem serve                        Start MCP HTTP server
    carrymem version                      Show version
"""

import sys
import os
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from memory_classification_engine import CarryMem
    from memory_classification_engine.__version__ import __version__
    from memory_classification_engine.adapters.sqlite_adapter import SQLiteAdapter
except ImportError:
    print("Error: CarryMem not properly installed")
    print("Try: pip install -e .")
    sys.exit(1)


_DEFAULT_DB = Path.home() / ".carrymem" / "memories.db"
_DEFAULT_CONFIG_DIR = Path.home() / ".carrymem"

_TYPE_ICONS = {
    "user_preference": "⭐",
    "fact_declaration": "📌",
    "correction": "🔧",
    "decision": "🎯",
    "task_pattern": "🔄",
    "contextual_observation": "👁",
    "knowledge": "📚",
    "unknown": "❓",
}

_TIER_LABELS = {1: "Core", 2: "Standard", 3: "Background", 4: "Archive"}


def _get_carrymem(db_path: Optional[str] = None, namespace: str = "default") -> CarryMem:
    path = db_path or str(_DEFAULT_DB)
    return CarryMem(db_path=path, namespace=namespace)


def _format_time(iso_str: Optional[str]) -> str:
    if not iso_str:
        return "N/A"
    try:
        from datetime import datetime
        if isinstance(iso_str, str):
            dt = datetime.fromisoformat(iso_str)
            now = datetime.now(dt.tzinfo)
            delta = now - dt
            if delta.days == 0:
                hours = delta.seconds // 3600
                if hours == 0:
                    minutes = delta.seconds // 60
                    return f"{minutes}m ago"
                return f"{hours}h ago"
            elif delta.days == 1:
                return "yesterday"
            elif delta.days < 30:
                return f"{delta.days}d ago"
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return str(iso_str)[:16]


def _truncate(text: str, max_len: int = 60) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def _print_table(headers: List[str], rows: List[List[str]], col_widths: Optional[List[int]] = None):
    if not col_widths:
        col_widths = []
        for i, h in enumerate(headers):
            max_w = len(h)
            for row in rows:
                if i < len(row):
                    max_w = max(max_w, len(str(row[i])))
            col_widths.append(min(max_w + 2, 50))

    header_line = ""
    for i, h in enumerate(headers):
        header_line += str(h).ljust(col_widths[i])
    print(header_line)
    print("-" * sum(col_widths))

    for row in rows:
        line = ""
        for i, cell in enumerate(row):
            if i < len(col_widths):
                line += str(cell).ljust(col_widths[i])
        print(line)


def cmd_add(args):
    parser = _make_parser("add")
    parser.add_argument("message", help="Message to remember")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--context", "-c", help="Additional context (JSON)")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    context = None
    if parsed.context:
        try:
            context = json.loads(parsed.context)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON context: {parsed.context}")
            return 1

    result = cm.classify_and_remember(parsed.message, context=context)

    if not result.get("should_remember"):
        print("  Not worth remembering (noise or too vague)")
        return 0

    entries = result.get("entries", [])
    keys = result.get("storage_keys", [])

    for i, entry in enumerate(entries):
        mtype = entry.get("type", "unknown")
        icon = _TYPE_ICONS.get(mtype, "❓")
        confidence = entry.get("confidence", 0)
        content = entry.get("content", "")
        tier = entry.get("tier", 2)
        tier_label = _TIER_LABELS.get(tier, f"T{tier}")

        print(f"  {icon} [{mtype}] {_truncate(content, 70)}")
        print(f"     Confidence: {confidence:.0%} | Tier: {tier_label} | Key: {keys[i] if i < len(keys) else 'N/A'}")

    print(f"\n  Remembered {len(entries)} item(s)")
    cm.close()
    return 0


def cmd_list(args):
    parser = _make_parser("list")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Number of memories to show")
    parser.add_argument("--type", "-t", help="Filter by memory type")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--format", "-f", choices=["table", "json", "plain"], default="table", help="Output format")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    filters = {}
    if parsed.type:
        filters["type"] = parsed.type

    memories = cm.recall_memories(query="", filters=filters, limit=parsed.limit)

    if not memories:
        print("  No memories found")
        print('  Tip: carrymem add "I prefer dark mode"')
        cm.close()
        return 0

    if parsed.format == "json":
        print(json.dumps(memories, ensure_ascii=False, indent=2))
    elif parsed.format == "plain":
        for m in memories:
            print(f"{m.get('storage_key', '')}\t{m.get('type', '')}\t{m.get('content', '')}\t{m.get('confidence', 0):.2f}")
    else:
        print(f"\n  Memories ({len(memories)} shown, namespace={parsed.namespace})\n")
        for i, m in enumerate(memories, 1):
            mtype = m.get("type", "unknown")
            icon = _TYPE_ICONS.get(mtype, "❓")
            content = m.get("content", "")
            confidence = m.get("confidence", 0)
            importance = m.get("importance_score", 0)
            key = m.get("storage_key", "")
            created = m.get("created_at", "")
            tier = m.get("tier", 2)
            tier_label = _TIER_LABELS.get(tier, f"T{tier}")

            print(f"  {i}. {icon} {_truncate(content, 65)}")
            print(f"     Type: {mtype} | Conf: {confidence:.0%} | Importance: {importance:.2f} | {tier_label}")
            print(f"     Key: {key} | {_format_time(created)}")
            print()

    cm.close()
    return 0


def cmd_search(args):
    parser = _make_parser("search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    parser.add_argument("--type", "-t", help="Filter by memory type")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--format", "-f", choices=["table", "json", "plain"], default="table", help="Output format")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    filters = {}
    if parsed.type:
        filters["type"] = parsed.type

    memories = cm.recall_memories(query=parsed.query, filters=filters, limit=parsed.limit)

    if not memories:
        print(f"  No memories matching '{parsed.query}'")
        cm.close()
        return 0

    if parsed.format == "json":
        print(json.dumps(memories, ensure_ascii=False, indent=2))
    elif parsed.format == "plain":
        for m in memories:
            print(f"{m.get('storage_key', '')}\t{m.get('type', '')}\t{m.get('content', '')}\t{m.get('confidence', 0):.2f}")
    else:
        print(f"\n  Search: '{parsed.query}' ({len(memories)} results)\n")
        for i, m in enumerate(memories, 1):
            mtype = m.get("type", "unknown")
            icon = _TYPE_ICONS.get(mtype, "❓")
            content = m.get("content", "")
            confidence = m.get("confidence", 0)
            key = m.get("storage_key", "")
            created = m.get("created_at", "")

            print(f"  {i}. {icon} {_truncate(content, 65)}")
            print(f"     Type: {mtype} | Conf: {confidence:.0%} | Key: {key} | {_format_time(created)}")
            print()

    cm.close()
    return 0


def cmd_forget(args):
    parser = _make_parser("forget")
    parser.add_argument("key", help="Storage key of the memory to delete")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")
    parser.add_argument("--force", "-y", action="store_true", help="Skip confirmation")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    memories = cm.recall_memories(query="", limit=100)
    target = None
    for m in memories:
        if m.get("storage_key") == parsed.key:
            target = m
            break

    if not target:
        print(f"  Memory not found: {parsed.key}")
        cm.close()
        return 1

    if not parsed.force:
        content = target.get("content", "")
        print(f"  Delete: {_truncate(content, 60)}")
        print(f"  Key: {parsed.key}")
        try:
            answer = input("  Confirm? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            cm.close()
            return 0
        if answer != "y":
            print("  Cancelled")
            cm.close()
            return 0

    success = cm.forget_memory(parsed.key)
    if success:
        print(f"  Forgotten: {parsed.key}")
    else:
        print(f"  Failed to forget: {parsed.key}")
        cm.close()
        return 1

    cm.close()
    return 0


def cmd_export(args):
    parser = _make_parser("export")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="json", help="Export format")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    result = cm.export_memories(output_path=parsed.output, format=parsed.format, namespace=parsed.namespace)

    if result.get("exported"):
        total = result.get("total_memories", 0)
        fmt = result.get("format", "json")
        print(f"  Exported {total} memories to {parsed.output} ({fmt})")
    else:
        print(f"  Export failed: {result}")
        cm.close()
        return 1

    cm.close()
    return 0


def cmd_import(args):
    parser = _make_parser("import")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("--namespace", "-n", default="default", help="Target namespace")
    parser.add_argument("--merge", choices=["skip_existing", "overwrite"], default="skip_existing", help="Merge strategy")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    result = cm.import_memories(
        input_path=parsed.input,
        namespace=parsed.namespace,
        merge_strategy=parsed.merge,
    )

    imported = result.get("imported", 0)
    skipped = result.get("skipped", 0)
    errors = result.get("errors", 0)
    total = result.get("total_processed", 0)

    print(f"  Import complete: {imported} imported, {skipped} skipped, {errors} errors ({total} total)")

    if errors > 0:
        cm.close()
        return 1

    cm.close()
    return 0


def cmd_stats(args):
    parser = _make_parser("stats")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    stats = cm.get_stats()
    profile = cm.get_memory_profile()

    if parsed.format == "json":
        combined = {"stats": stats, "profile": profile}
        print(json.dumps(combined, ensure_ascii=False, indent=2))
        cm.close()
        return 0

    total = stats.get("total_count", 0)
    by_type = stats.get("by_type", {})

    print(f"\n  CarryMem Statistics (namespace: {parsed.namespace})")
    print(f"  {'=' * 45}")
    print(f"\n  Total Memories: {total}")

    if by_type:
        print(f"\n  By Type:")
        max_type_len = max(len(t) for t in by_type) if by_type else 10
        for mtype, count in sorted(by_type.items(), key=lambda x: -x[1]):
            icon = _TYPE_ICONS.get(mtype, "  ")
            bar = "█" * min(count, 30)
            pct = (count / total * 100) if total > 0 else 0
            print(f"    {icon} {mtype.ljust(max_type_len)}  {count:4d}  {bar}  ({pct:.0f}%)")

    profile_stats = profile.get("stats", {})
    by_tier = profile_stats.get("by_tier", {})
    if by_tier:
        print(f"\n  By Tier:")
        for tier_num in sorted(by_tier.keys()):
            count = by_tier[tier_num]
            label = _TIER_LABELS.get(tier_num, f"T{tier_num}")
            print(f"    Tier {tier_num} ({label}): {count}")

    conf_avg = profile_stats.get("confidence_avg", 0)
    if conf_avg:
        print(f"\n  Avg Confidence: {conf_avg:.2f}")

    db_path = stats.get("db_path", "")
    if db_path and db_path != ":memory:":
        p = Path(db_path)
        if p.exists():
            size_mb = p.stat().st_size / (1024 * 1024)
            print(f"  Database Size: {size_mb:.2f} MB")
            print(f"  Database Path: {db_path}")

    print()
    cm.close()
    return 0


def cmd_doctor(args):
    parser = _make_parser("doctor")
    parser.add_argument("--db", help="Database path")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues")

    parsed = parser.parse_args(args)
    db_path = parsed.db or str(_DEFAULT_DB)

    print("\n  CarryMem Doctor - Diagnostics\n")
    print(f"  {'=' * 45}")

    checks_passed = 0
    checks_total = 0
    issues = []

    # Check 1: Python version
    checks_total += 1
    py_ver = sys.version_info
    py_str = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    if py_ver >= (3, 9):
        print(f"  [OK] Python {py_str} (>= 3.9)")
        checks_passed += 1
    else:
        print(f"  [FAIL] Python {py_str} (need >= 3.9)")
        issues.append("Python version too old")

    # Check 2: CarryMem import
    checks_total += 1
    try:
        from memory_classification_engine import CarryMem
        print(f"  [OK] CarryMem v{__version__}")
        checks_passed += 1
    except ImportError as e:
        print(f"  [FAIL] CarryMem import: {e}")
        issues.append("CarryMem not importable")

    # Check 3: Config directory
    checks_total += 1
    if _DEFAULT_CONFIG_DIR.exists():
        print(f"  [OK] Config directory: {_DEFAULT_CONFIG_DIR}")
        checks_passed += 1
    else:
        print(f"  [WARN] Config directory missing: {_DEFAULT_CONFIG_DIR}")
        issues.append("Config directory missing")
        if parsed.fix:
            _DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            print(f"        Fixed: Created {_DEFAULT_CONFIG_DIR}")

    # Check 4: Database file
    checks_total += 1
    db = Path(db_path)
    if db.exists():
        size_mb = db.stat().st_size / (1024 * 1024)
        print(f"  [OK] Database: {db} ({size_mb:.2f} MB)")
        checks_passed += 1
    else:
        print(f"  [WARN] Database not found: {db}")
        issues.append("Database not initialized")
        if parsed.fix:
            try:
                cm = CarryMem(db_path=db_path)
                cm.classify_and_remember("CarryMem initialized by doctor")
                cm.close()
                print(f"        Fixed: Created database at {db}")
            except Exception as e:
                print(f"        Fix failed: {e}")

    # Check 5: Database integrity
    checks_total += 1
    if db.exists():
        try:
            conn = sqlite3.connect(str(db))
            result = conn.execute("PRAGMA integrity_check").fetchone()
            conn.close()
            if result[0] == "ok":
                print(f"  [OK] Database integrity: OK")
                checks_passed += 1
            else:
                print(f"  [FAIL] Database integrity: {result[0]}")
                issues.append("Database integrity check failed")
        except Exception as e:
            print(f"  [FAIL] Database check error: {e}")
            issues.append(f"Database error: {e}")
    else:
        print(f"  [SKIP] Database integrity (no database)")

    # Check 6: Write permissions
    checks_total += 1
    try:
        test_file = _DEFAULT_CONFIG_DIR / ".doctor_test"
        test_file.touch()
        test_file.unlink()
        print(f"  [OK] Write permissions")
        checks_passed += 1
    except Exception as e:
        print(f"  [FAIL] Write permissions: {e}")
        issues.append("Cannot write to config directory")

    # Check 7: Optional dependencies
    checks_total += 1
    optional_deps = []
    try:
        import pycld2
        optional_deps.append("pycld2")
    except ImportError:
        pass
    try:
        from cryptography.fernet import Fernet
        optional_deps.append("cryptography")
    except ImportError:
        pass
    try:
        import langdetect
        optional_deps.append("langdetect")
    except ImportError:
        pass

    if optional_deps:
        print(f"  [OK] Optional deps: {', '.join(optional_deps)}")
        checks_passed += 1
    else:
        print(f"  [INFO] No optional deps (pycld2, cryptography, langdetect)")
        checks_passed += 1

    # Check 8: FTS5 support
    checks_total += 1
    try:
        test_conn = sqlite3.connect(":memory:")
        test_conn.execute("CREATE VIRTUAL TABLE t USING fts5(c)")
        test_conn.close()
        print(f"  [OK] SQLite FTS5 support")
        checks_passed += 1
    except Exception:
        print(f"  [FAIL] SQLite FTS5 not available")
        issues.append("FTS5 not supported (search will be limited)")

    # Check 9: Security module
    checks_total += 1
    try:
        from memory_classification_engine.security import InputValidator
        validator = InputValidator()
        test_result = validator.validate_content("test content")
        if test_result:
            print(f"  [OK] Security module (InputValidator)")
            checks_passed += 1
        else:
            print(f"  [WARN] Security module: validation returned empty")
            issues.append("InputValidator not working correctly")
    except ImportError:
        print(f"  [INFO] Security module not available")
        checks_passed += 1
    except Exception as e:
        print(f"  [WARN] Security module: {e}")
        issues.append(f"Security module issue: {e}")

    # Check 10: MCP integration status
    checks_total += 1
    mcp_configs = []
    cwd = Path.cwd()
    claude_mcp = cwd / ".claude" / "mcp.json"
    cursor_mcp = cwd / ".cursor" / "mcp.json"
    if claude_mcp.exists():
        mcp_configs.append(f"claude-code ({claude_mcp})")
    if cursor_mcp.exists():
        mcp_configs.append(f"cursor ({cursor_mcp})")

    if mcp_configs:
        print(f"  [OK] MCP configs: {', '.join(mcp_configs)}")
        checks_passed += 1
    else:
        print(f"  [INFO] No MCP configs in current directory")
        print(f"         Run 'carrymem setup-mcp' to configure")
        checks_passed += 1

    # Check 11: Memory count
    checks_total += 1
    if db.exists():
        try:
            cm = CarryMem(db_path=db_path)
            stats = cm.get_stats()
            total = stats.get("total_count", 0)
            print(f"  [OK] Memory count: {total}")
            checks_passed += 1
            cm.close()
        except Exception:
            print(f"  [WARN] Cannot read memory count")
            checks_passed += 1
    else:
        print(f"  [SKIP] Memory count (no database)")
        checks_passed += 1

    # Summary
    print(f"\n  {'=' * 45}")
    if issues:
        print(f"  Issues found ({len(issues)}):")
        for issue in issues:
            print(f"    - {issue}")
        if not parsed.fix:
            print(f"\n  Tip: Run 'carrymem doctor --fix' to auto-fix issues")
    else:
        print(f"  All checks passed ({checks_passed}/{checks_total})")

    print()
    return 0 if not issues else 1


def cmd_setup_mcp(args):
    parser = _make_parser("setup-mcp")
    parser.add_argument("--tool", "-t", choices=["claude-code", "cursor", "all"], default="all", help="Target tool")
    parser.add_argument("--project", "-p", default=".", help="Project directory (default: current)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing config")

    parsed = parser.parse_args(args)
    project_dir = Path(parsed.project).resolve()

    import sys
    python_path = sys.executable

    module_cmd = f"{python_path} -m memory_classification_engine.integration.layer2_mcp"

    mcp_config = {
        "mcpServers": {
            "carrymem": {
                "command": python_path,
                "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
            }
        }
    }

    configured = []

    if parsed.tool in ("claude-code", "all"):
        claude_dir = project_dir / ".claude"
        claude_file = claude_dir / "mcp.json"

        if claude_file.exists() and not parsed.force:
            try:
                with open(claude_file) as f:
                    existing = json.load(f)
                if "carrymem" in existing.get("mcpServers", {}):
                    print(f"  Claude Code: already configured ({claude_file})")
                    configured.append("claude-code")
                    skip_claude = True
                else:
                    skip_claude = False
            except Exception:
                skip_claude = False
        else:
            skip_claude = False

        if not skip_claude:
            claude_dir.mkdir(parents=True, exist_ok=True)
            if claude_file.exists() and not parsed.force:
                try:
                    with open(claude_file) as f:
                        existing = json.load(f)
                    existing.setdefault("mcpServers", {})["carrymem"] = mcp_config["mcpServers"]["carrymem"]
                    with open(claude_file, "w") as f:
                        json.dump(existing, f, indent=2)
                except Exception:
                    with open(claude_file, "w") as f:
                        json.dump(mcp_config, f, indent=2)
            else:
                with open(claude_file, "w") as f:
                    json.dump(mcp_config, f, indent=2)
            print(f"  Claude Code: configured ({claude_file})")
            configured.append("claude-code")

    if parsed.tool in ("cursor", "all"):
        cursor_dir = project_dir / ".cursor"
        cursor_file = cursor_dir / "mcp.json"

        if cursor_file.exists() and not parsed.force:
            try:
                with open(cursor_file) as f:
                    existing = json.load(f)
                if "carrymem" in existing.get("mcpServers", {}):
                    print(f"  Cursor: already configured ({cursor_file})")
                    configured.append("cursor")
                    skip_cursor = True
                else:
                    skip_cursor = False
            except Exception:
                skip_cursor = False
        else:
            skip_cursor = False

        if not skip_cursor:
            cursor_dir.mkdir(parents=True, exist_ok=True)
            if cursor_file.exists() and not parsed.force:
                try:
                    with open(cursor_file) as f:
                        existing = json.load(f)
                    existing.setdefault("mcpServers", {})["carrymem"] = mcp_config["mcpServers"]["carrymem"]
                    with open(cursor_file, "w") as f:
                        json.dump(existing, f, indent=2)
                except Exception:
                    with open(cursor_file, "w") as f:
                        json.dump(mcp_config, f, indent=2)
            else:
                with open(cursor_file, "w") as f:
                    json.dump(mcp_config, f, indent=2)
            print(f"  Cursor: configured ({cursor_file})")
            configured.append("cursor")

    if configured:
        print(f"\n  MCP integration ready for: {', '.join(configured)}")
        print(f"  Command: {module_cmd}")
        print(f"\n  Restart your AI tool to activate CarryMem")
    else:
        print(f"  No tools configured")

    return 0


def cmd_serve(args):
    parser = _make_parser("serve")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", "-p", type=int, default=8765, help="Port to listen")
    parser.add_argument("--api-key", help="API key for authentication")

    parsed = parser.parse_args(args)

    from memory_classification_engine.integration.layer2_mcp.http_server import run_http_server
    print(f"\n  CarryMem MCP HTTP Server")
    print(f"  Host: {parsed.host}")
    print(f"  Port: {parsed.port}")
    print(f"  SSE:  http://{parsed.host}:{parsed.port}/sse")
    print(f"  API:  http://{parsed.host}:{parsed.port}/message")
    print(f"  Health: http://{parsed.host}:{parsed.port}/health")
    print()
    run_http_server(host=parsed.host, port=parsed.port, api_key=parsed.api_key)
    return 0


def cmd_check(args):
    parser = _make_parser("check")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")
    parser.add_argument("--conflicts", action="store_true", help="Check for conflicts")
    parser.add_argument("--quality", action="store_true", help="Check for low quality memories")
    parser.add_argument("--expired", action="store_true", help="Check for expired memories")
    parser.add_argument("--all", action="store_true", help="Run all checks")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    run_all = parsed.all or (not parsed.conflicts and not parsed.quality and not parsed.expired)

    print(f"\n  CarryMem Quality Check (namespace: {parsed.namespace})")
    print(f"  {'=' * 45}\n")

    if run_all or parsed.conflicts:
        print(f"  Conflicts:")
        try:
            conflicts = cm.check_conflicts()
            if not conflicts:
                print(f"    No conflicts detected")
            else:
                for c in conflicts:
                    ctype = c.get("conflict_type", "unknown")
                    severity = c.get("severity", "unknown")
                    reason = c.get("reason", "")
                    keys = c.get("memory_keys", [])
                    print(f"    [{severity.upper()}] {ctype}: {reason}")
                    for key in keys:
                        print(f"      - {key}")
        except Exception as e:
            print(f"    Error: {e}")
        print()

    if run_all or parsed.quality:
        print(f"  Low Quality Memories:")
        try:
            low_quality = cm.check_quality(min_score=0.3)
            if not low_quality:
                print(f"    All memories have good quality")
            else:
                for item in low_quality:
                    key = item.get("storage_key", "")
                    score = item.get("score", 0)
                    reasons = item.get("reasons", [])
                    content = item.get("content", "")
                    print(f"    Score: {score:.3f} | {_truncate(content, 50)}")
                    print(f"      Key: {key} | Reasons: {', '.join(reasons)}")
        except Exception as e:
            print(f"    Error: {e}")
        print()

    if run_all or parsed.expired:
        print(f"  Expired Memories:")
        try:
            expired = cm.list_expired()
            if not expired:
                print(f"    No expired memories")
            else:
                for item in expired:
                    key = item.get("storage_key", "")
                    content = item.get("content", "")
                    expires = item.get("expires_at", "")
                    print(f"    {_truncate(content, 50)}")
                    print(f"      Key: {key} | Expired: {expires}")
        except Exception as e:
            print(f"    Error: {e}")
        print()

    cm.close()
    return 0


def cmd_tui(args):
    from memory_classification_engine.tui import run_tui, HAS_TEXTUAL
    if not HAS_TEXTUAL:
        print("  Textual is not installed.")
        print("  Install with: pip install textual")
        print("  Then run: carrymem tui")
        return 1

    parser = _make_parser("tui")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    run_tui(db_path=parsed.db, namespace=parsed.namespace)
    return 0


def cmd_init(args):
    parser = _make_parser("init")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    db_path = parsed.db or str(_DEFAULT_DB)

    print("\n  Initializing CarryMem...\n")

    if not _DEFAULT_CONFIG_DIR.exists():
        _DEFAULT_CONFIG_DIR.mkdir(parents=True)
        print(f"  [OK] Created config directory: {_DEFAULT_CONFIG_DIR}")
    else:
        print(f"  [OK] Config directory exists: {_DEFAULT_CONFIG_DIR}")

    config_file = _DEFAULT_CONFIG_DIR / "config.json"
    if not config_file.exists():
        config = {
            "version": __version__,
            "db_path": db_path,
            "namespace": "default",
        }
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print(f"  [OK] Created config: {config_file}")
    else:
        print(f"  [OK] Config exists: {config_file}")

    try:
        cm = CarryMem(db_path=db_path)
        cm.classify_and_remember("CarryMem initialized successfully!")
        print(f"  [OK] Database initialized: {db_path}")
        cm.close()
    except Exception as e:
        print(f"  [FAIL] Database init error: {e}")
        return 1

    print(f"\n  CarryMem is ready!")
    print(f"\n  Quick Start:")
    print(f'    carrymem add "I prefer dark mode"')
    print(f"    carrymem list")
    print(f'    carrymem search "theme"')
    print(f"    carrymem setup-mcp --tool cursor")
    print()
    return 0


def cmd_version(args):
    print(f"\n  CarryMem v{__version__}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Config: {_DEFAULT_CONFIG_DIR}")
    print(f"  Database: {_DEFAULT_DB}")
    print()
    return 0


def _make_parser(cmd_name: str):
    import argparse
    return argparse.ArgumentParser(
        prog=f"carrymem {cmd_name}",
        description=f"CarryMem {cmd_name} command",
    )


def show_help():
    print(f"""
  CarryMem v{__version__} - Your Portable AI Memory Layer

  AI remembers you. Not the other way around.

  Commands:
    add <message>        Store a memory
    list                 List recent memories
    search <query>       Search memories
    forget <key>         Delete a memory
    export <path>        Export memories to file
    import <path>        Import memories from file
    stats                Show memory statistics
    check                Check memory quality & conflicts
    doctor               Run diagnostics
    setup-mcp            Configure MCP integration
    tui                  Launch terminal UI
    serve                Start MCP HTTP server
    init                 Initialize CarryMem
    version              Show version

  Examples:
    carrymem add "I prefer dark mode"
    carrymem add "Using React for frontend" --namespace work
    carrymem search "theme"
    carrymem list --type user_preference --limit 20
    carrymem export backup.json
    carrymem import backup.json
    carrymem setup-mcp --tool cursor
    carrymem doctor --fix

  Documentation: https://github.com/lulin70/memory-classification-engine
""")


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1]
    remaining_args = sys.argv[2:]

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "search": cmd_search,
        "find": cmd_search,
        "forget": cmd_forget,
        "delete": cmd_forget,
        "rm": cmd_forget,
        "export": cmd_export,
        "import": cmd_import,
        "stats": cmd_stats,
        "check": cmd_check,
        "doctor": cmd_doctor,
        "setup-mcp": cmd_setup_mcp,
        "init-integration": cmd_setup_mcp,
        "tui": cmd_tui,
        "serve": cmd_serve,
        "init": cmd_init,
        "version": cmd_version,
        "--version": cmd_version,
        "-v": cmd_version,
        "help": lambda _: show_help(),
    }

    handler = commands.get(command)
    if handler is None:
        print(f"  Unknown command: {command}")
        print(f"  Run 'carrymem help' for usage")
        sys.exit(1)

    try:
        result = handler(remaining_args)
        sys.exit(result if isinstance(result, int) else 0)
    except KeyboardInterrupt:
        print()
        sys.exit(130)
    except Exception as e:
        print(f"  Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
