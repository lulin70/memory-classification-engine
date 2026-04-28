#!/usr/bin/env python3
"""CarryMem CLI - Your Portable AI Memory Layer.

Usage:
    carrymem add "I prefer dark mode"     Store a memory
    carrymem list                         List recent memories
    carrymem search "theme"               Search memories
    carrymem show <key>                   View memory details
    carrymem edit <key> "new content"     Edit a memory
    carrymem forget <key>                 Delete a memory
    carrymem clean                        Remove expired/low-quality
    carrymem export backup.json           Export memories
    carrymem import backup.json           Import memories
    carrymem stats                        Show statistics
    carrymem check                        Check quality & conflicts
    carrymem doctor                       Run diagnostics
    carrymem setup-mcp --tool cursor      Configure MCP integration
    carrymem tui                          Launch terminal UI
    carrymem serve                        Start MCP HTTP server
    carrymem version                      Show version
"""

import sys
import os
import json
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
    "user_preference": "\u2b50",
    "fact_declaration": "\U0001f4cc",
    "correction": "\U0001f527",
    "decision": "\U0001f3af",
    "task_pattern": "\U0001f504",
    "contextual_observation": "\U0001f441",
    "knowledge": "\U0001f4da",
    "unknown": "\u2753",
}

_TIER_LABELS = {1: "Core", 2: "Standard", 3: "Background", 4: "Archive"}

_HAS_COLOR = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    if not _HAS_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def _green(t): return _c("32", t)
def _red(t): return _c("31", t)
def _yellow(t): return _c("33", t)
def _cyan(t): return _c("36", t)
def _dim(t): return _c("2", t)
def _bold(t): return _c("1", t)


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


def _find_memory(cm: CarryMem, key: str) -> Optional[Dict[str, Any]]:
    if cm._adapter and hasattr(cm._adapter, '_get_by_key'):
        stored = cm._adapter._get_by_key(key)
        if stored:
            return stored.to_dict()
    memories = cm.recall_memories(query="", limit=200)
    for m in memories:
        if m.get("storage_key") == key:
            return m
    return None


def _print_memory_card(m: Dict[str, Any], index: Optional[int] = None):
    mtype = m.get("type", "unknown")
    icon = _TYPE_ICONS.get(mtype, "\u2753")
    content = m.get("content", "")
    confidence = m.get("confidence", 0)
    importance = m.get("importance_score", 0)
    key = m.get("storage_key", "")
    created = m.get("created_at", "")
    tier = m.get("tier", 2)
    tier_label = _TIER_LABELS.get(tier, f"T{tier}")
    access_count = m.get("access_count", 0)

    prefix = f"  {index}." if index else "  "
    print(f"{prefix} {icon} {_bold(_truncate(content, 65))}")
    print(f"     {_dim(f'Type: {mtype} | Conf: {confidence:.0%} | Importance: {importance:.2f} | {tier_label}')}")
    print(f"     {_dim(f'Key: {key} | {_format_time(created)}')}")


def cmd_add(args):
    parser = _make_parser("add")
    parser.add_argument("message", help="Message to remember")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--context", "-c", help="Additional context (JSON)")
    parser.add_argument("--force", "-f", action="store_true", help="Force store without classification")
    parser.add_argument("--type", "-t", help="Override memory type (with --force)")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    context = None
    if parsed.context:
        try:
            context = json.loads(parsed.context)
        except json.JSONDecodeError:
            print(f"  {_red('Error:')} Invalid JSON context: {parsed.context}")
            return 1

    if parsed.force:
        result = cm.declare(parsed.message, context=context)
        keys = result.get("storage_keys", [])
        entries = result.get("entries", [])
        if keys:
            print(f"  {_green('Stored')} (forced) {len(keys)} item(s)")
            for i, key in enumerate(keys):
                entry = entries[i] if i < len(entries) else {}
                mtype = entry.get("type", parsed.type or "unknown")
                icon = _TYPE_ICONS.get(mtype, "\u2753")
                content = entry.get("content", parsed.message)
                print(f"    {icon} [{mtype}] {_truncate(content, 70)}")
                print(f"       Key: {key}")
        else:
            print(f"  {_red('Failed to store memory')}")
            cm.close()
            return 1
    else:
        result = cm.classify_and_remember(parsed.message, context=context)

        if not result.get("should_remember"):
            print(f"  {_yellow('Not classified as memorable')} (noise or too vague)")
            print(f"  {_dim('Tip: Use --force to store anyway:')}")
            tip_msg = f'  carrymem add --force "{parsed.message}"'
            print(f"  {_dim(tip_msg)}")
            cm.close()
            return 0

        entries = result.get("entries", [])
        keys = result.get("storage_keys", [])

        for i, entry in enumerate(entries):
            mtype = entry.get("type", "unknown")
            icon = _TYPE_ICONS.get(mtype, "\u2753")
            confidence = entry.get("confidence", 0)
            content = entry.get("content", "")
            tier = entry.get("tier", 2)
            tier_label = _TIER_LABELS.get(tier, f"T{tier}")

            print(f"  {icon} [{mtype}] {_bold(_truncate(content, 70))}")
            key_display = keys[i] if i < len(keys) else "N/A"
            print(f"     {_dim(f'Confidence: {confidence:.0%} | Tier: {tier_label} | Key: {key_display}')}")

        print(f"\n  {_green(f'Remembered {len(entries)} item(s)')}")

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
        print(f"  {_dim('No memories found')}")
        tip = 'Tip: carrymem add "I prefer dark mode"'
        print(f"  {_dim(tip)}")
        cm.close()
        return 0

    if parsed.format == "json":
        print(json.dumps(memories, ensure_ascii=False, indent=2))
    elif parsed.format == "plain":
        for m in memories:
            print(f"{m.get('storage_key', '')}\t{m.get('type', '')}\t{m.get('content', '')}\t{m.get('confidence', 0):.2f}")
    else:
        print(f"\n  {_bold(f'Memories')} ({len(memories)} shown, namespace={parsed.namespace})\n")
        for i, m in enumerate(memories, 1):
            _print_memory_card(m, index=i)
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
        print(f"  {_dim(f'No memories matching')} {_bold(parsed.query)}")
        cm.close()
        return 0

    if parsed.format == "json":
        print(json.dumps(memories, ensure_ascii=False, indent=2))
    elif parsed.format == "plain":
        for m in memories:
            print(f"{m.get('storage_key', '')}\t{m.get('type', '')}\t{m.get('content', '')}\t{m.get('confidence', 0):.2f}")
    else:
        print(f"\n  {_bold('Search:')} {_cyan(parsed.query)} ({len(memories)} results)\n")
        for i, m in enumerate(memories, 1):
            _print_memory_card(m, index=i)
            print()

    cm.close()
    return 0


def cmd_show(args):
    parser = _make_parser("show")
    parser.add_argument("key", help="Storage key of the memory")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    target = _find_memory(cm, parsed.key)

    if not target:
        print(f"  {_red('Memory not found:')} {parsed.key}")
        cm.close()
        return 1

    if parsed.json:
        print(json.dumps(target, ensure_ascii=False, indent=2))
        cm.close()
        return 0

    mtype = target.get("type", "unknown")
    icon = _TYPE_ICONS.get(mtype, "\u2753")
    content = target.get("content", "")
    confidence = target.get("confidence", 0)
    importance = target.get("importance_score", 0)
    key = target.get("storage_key", "")
    created = target.get("created_at", "")
    tier = target.get("tier", 2)
    tier_label = _TIER_LABELS.get(tier, f"T{tier}")
    access_count = target.get("access_count", 0)
    original = target.get("original_message", "")
    version = target.get("version", 1)
    expires = target.get("expires_at", "")

    print(f"\n  {icon} {_bold(content)}")
    print(f"  {'=' * 50}")
    print(f"  Key:        {key}")
    print(f"  Type:       {mtype}")
    print(f"  Tier:       {tier_label} ({tier})")
    print(f"  Confidence: {confidence:.0%}")
    print(f"  Importance: {importance:.3f}")
    print(f"  Version:    {version}")
    print(f"  Accesses:   {access_count}")
    print(f"  Created:    {_format_time(created)}")
    if expires:
        print(f"  Expires:    {expires}")
    if original and original != content:
        print(f"\n  Original:   {_dim(original)}")

    print()
    cm.close()
    return 0


def cmd_edit(args):
    parser = _make_parser("edit")
    parser.add_argument("key", help="Storage key of the memory to edit")
    parser.add_argument("content", help="New content")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    target = _find_memory(cm, parsed.key)

    if not target:
        print(f"  {_red('Memory not found:')} {parsed.key}")
        cm.close()
        return 1

    old_content = target.get("content", "")
    print(f"  {_dim('Old:')} {_truncate(old_content, 60)}")
    print(f"  {_green('New:')} {_truncate(parsed.content, 60)}")

    try:
        answer = input("  Confirm edit? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        cm.close()
        return 0

    if answer != "y":
        print(f"  {_dim('Cancelled')}")
        cm.close()
        return 0

    result = cm.update_memory(parsed.key, parsed.content)
    success = result if isinstance(result, bool) else bool(result)
    if success:
        print(f"  {_green('Updated:')} {parsed.key}")
    else:
        print(f"  {_red('Failed to update:')} {parsed.key}")
        cm.close()
        return 1

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

    target = _find_memory(cm, parsed.key)

    if not target:
        print(f"  {_red('Memory not found:')} {parsed.key}")
        cm.close()
        return 1

    if not parsed.force:
        content = target.get("content", "")
        print(f"  {_red('Delete:')} {_truncate(content, 60)}")
        print(f"  Key: {parsed.key}")
        try:
            answer = input("  Confirm? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            cm.close()
            return 0
        if answer != "y":
            print(f"  {_dim('Cancelled')}")
            cm.close()
            return 0

    success = cm.forget_memory(parsed.key)
    if success:
        print(f"  {_green('Forgotten:')} {parsed.key}")
    else:
        print(f"  {_red('Failed to forget:')} {parsed.key}")
        cm.close()
        return 1

    cm.close()
    return 0


def cmd_clean(args):
    parser = _make_parser("clean")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")
    parser.add_argument("--expired", action="store_true", help="Remove expired memories")
    parser.add_argument("--quality", type=float, default=0, help="Remove memories below quality threshold")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed")
    parser.add_argument("--force", "-y", action="store_true", help="Skip confirmation")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    to_remove = []

    if parsed.expired:
        expired = cm.list_expired()
        for item in expired:
            to_remove.append(("expired", item))

    if parsed.quality > 0:
        low_quality = cm.check_quality(min_score=parsed.quality)
        for item in low_quality:
            already = any(r[1].get("storage_key") == item["storage_key"] for r in to_remove)
            if not already:
                to_remove.append(("low_quality", item))

    if not to_remove:
        print(f"  {_green('Nothing to clean')} — all memories are healthy")
        cm.close()
        return 0

    print(f"\n  {_bold('Memories to clean:')} {len(to_remove)}\n")
    for reason, item in to_remove:
        key = item.get("storage_key", "")
        content = item.get("content", "")
        if reason == "expired":
            print(f"    {_yellow('[EXPIRED]')} {_truncate(content, 50)}")
        else:
            score = item.get("score", 0)
            print(f"    {_yellow(f'[QUALITY:{score:.2f}]')} {_truncate(content, 50)}")
        print(f"      Key: {key}")

    if parsed.dry_run:
        print(f"\n  {_dim('Dry run — no changes made')}")
        cm.close()
        return 0

    if not parsed.force:
        try:
            answer = input(f"\n  Remove {len(to_remove)} memories? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            cm.close()
            return 0
        if answer != "y":
            print(f"  {_dim('Cancelled')}")
            cm.close()
            return 0

    removed = 0
    errors = 0
    for reason, item in to_remove:
        key = item.get("storage_key", "")
        if cm.forget_memory(key):
            removed += 1
        else:
            errors += 1

    print(f"\n  {_green(f'Cleaned:')} {removed} removed, {errors} errors")
    cm.close()
    return 0 if errors == 0 else 1


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
        print(f"  {_green('Exported')} {total} memories to {_cyan(parsed.output)} ({fmt})")
    else:
        print(f"  {_red('Export failed:')} {result}")
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

    print(f"  {_green('Import complete:')} {imported} imported, {skipped} skipped, {errors} errors ({total} total)")

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

    print(f"\n  {_bold('CarryMem Statistics')} (namespace: {parsed.namespace})")
    print(f"  {'=' * 45}")
    print(f"\n  Total Memories: {_bold(str(total))}")

    if by_type:
        print(f"\n  By Type:")
        max_type_len = max(len(t) for t in by_type) if by_type else 10
        for mtype, count in sorted(by_type.items(), key=lambda x: -x[1]):
            icon = _TYPE_ICONS.get(mtype, "  ")
            bar = "\u2588" * min(count, 30)
            pct = (count / total * 100) if total > 0 else 0
            print(f"    {icon} {mtype.ljust(max_type_len)}  {count:4d}  {_cyan(bar)}  ({pct:.0f}%)")

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
            print(f"  Database Path: {_dim(db_path)}")

    print()
    cm.close()
    return 0


def cmd_whoami(args):
    parser = _make_parser("whoami")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    identity = cm.whoami()

    if parsed.json:
        print(json.dumps(identity, ensure_ascii=False, indent=2))
        cm.close()
        return 0

    user_type = identity.get("identity", "unknown")
    summary = identity.get("summary", "")
    total = identity.get("total_memories", 0)

    if user_type == "new_user":
        dont_know = "I don't know you yet."
        print(f"\n  {_dim(dont_know)}")
        print(f"  {_dim('Start by telling me about yourself:')}")
        print(f'    carrymem add "I prefer dark mode"')
        print(f'    carrymem add "I use Python for data analysis"')
        print()
        cm.close()
        return 0

    print(f"\n  {_bold('Who You Are (according to your AI)')}")
    print(f"  {'=' * 50}")
    print(f"\n  {_cyan(summary)}")

    preferences = identity.get("preferences", [])
    if preferences:
        print(f"\n  {_bold('Your Preferences:')}")
        for p in preferences:
            pref_icon = _TYPE_ICONS.get("user_preference", "*")
            print(f"    {_green(pref_icon)} {p}")

    decisions = identity.get("decisions", [])
    if decisions:
        print(f"\n  {_bold('Your Decisions:')}")
        for d in decisions:
            dec_icon = _TYPE_ICONS.get("decision", "*")
            print(f"    {_cyan(dec_icon)} {d}")

    corrections = identity.get("corrections", [])
    if corrections:
        print(f"\n  {_bold('Your Corrections:')}")
        for c in corrections:
            cor_icon = _TYPE_ICONS.get("correction", "*")
            print(f"    {_yellow(cor_icon)} {c}")

    by_type = identity.get("by_type", {})
    if by_type:
        print(f"\n  {_bold('Memory Profile:')}")
        top = identity.get("top_type", "")
        conf = identity.get("confidence_avg", 0)
        print(f"    Total: {total} | Dominant: {top} | Avg Confidence: {conf:.0%}")

    print(f"\n  {_dim('Export your identity: carrymem profile export identity.json')}")
    print()
    cm.close()
    return 0


def cmd_profile(args):
    parser = _make_parser("profile")
    parser.add_argument("action", choices=["export", "show"], default="show", nargs="?", help="Profile action")
    parser.add_argument("--output", "-o", help="Output file path (for export)")
    parser.add_argument("--namespace", "-n", default="default", help="Namespace")
    parser.add_argument("--db", help="Database path")

    parsed = parser.parse_args(args)
    cm = _get_carrymem(parsed.db, parsed.namespace)

    if parsed.action == "export":
        output = parsed.output or "carrymem_profile.json"
        result = cm.export_profile(output_path=output)
        pref_count = len(result.get("preferences", []))
        dec_count = len(result.get("decisions", []))
        print(f"  {_green('Profile exported to')} {_cyan(output)}")
        print(f"  {_dim(f'{pref_count} preferences, {dec_count} decisions')}")
    else:
        identity = cm.whoami()
        print(json.dumps(identity, ensure_ascii=False, indent=2))

    cm.close()
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

    print(f"\n  {_bold('CarryMem Quality Check')} (namespace: {parsed.namespace})")
    print(f"  {'=' * 45}\n")

    if run_all or parsed.conflicts:
        print(f"  Conflicts:")
        try:
            conflicts = cm.check_conflicts()
            if not conflicts:
                print(f"    {_green('No conflicts detected')}")
            else:
                for c in conflicts:
                    ctype = c.get("conflict_type", "unknown")
                    severity = c.get("severity", "unknown")
                    reason = c.get("reason", "")
                    keys = c.get("memory_keys", [])
                    sev_color = _red if severity == "high" else _yellow
                    print(f"    {sev_color(f'[{severity.upper()}]')} {ctype}: {reason}")
                    for key in keys:
                        print(f"      {_dim(f'- {key}')}")
        except Exception as e:
            print(f"    {_red(f'Error: {e}')}")
        print()

    if run_all or parsed.quality:
        print(f"  Low Quality Memories:")
        try:
            low_quality = cm.check_quality(min_score=0.3)
            if not low_quality:
                print(f"    {_green('All memories have good quality')}")
            else:
                for item in low_quality:
                    key = item.get("storage_key", "")
                    score = item.get("score", 0)
                    reasons = item.get("reasons", [])
                    content = item.get("content", "")
                    print(f"    {_yellow(f'Score: {score:.3f}')} | {_truncate(content, 50)}")
                    reasons_str = ", ".join(reasons)
                    print(f"      {_dim(f'Key: {key} | Reasons: {reasons_str}')}")
        except Exception as e:
            print(f"    {_red(f'Error: {e}')}")
        print()

    if run_all or parsed.expired:
        print(f"  Expired Memories:")
        try:
            expired = cm.list_expired()
            if not expired:
                print(f"    {_green('No expired memories')}")
            else:
                for item in expired:
                    key = item.get("storage_key", "")
                    content = item.get("content", "")
                    expires = item.get("expires_at", "")
                    print(f"    {_yellow('[EXPIRED]')} {_truncate(content, 50)}")
                    print(f"      {_dim(f'Key: {key} | Expired: {expires}')}")
        except Exception as e:
            print(f"    {_red(f'Error: {e}')}")
        print()

    cm.close()
    return 0


def cmd_doctor(args):
    parser = _make_parser("doctor")
    parser.add_argument("--db", help="Database path")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues")

    parsed = parser.parse_args(args)
    db_path = parsed.db or str(_DEFAULT_DB)

    print(f"\n  {_bold('CarryMem Doctor')} - Diagnostics\n")
    print(f"  {'=' * 45}")

    checks_passed = 0
    checks_total = 0
    issues = []

    checks_total += 1
    py_ver = sys.version_info
    py_str = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    if py_ver >= (3, 9):
        print(f"  {_green('[OK]')} Python {py_str} (>= 3.9)")
        checks_passed += 1
    else:
        print(f"  {_red('[FAIL]')} Python {py_str} (need >= 3.9)")
        issues.append("Python version too old")

    checks_total += 1
    try:
        from memory_classification_engine import CarryMem
        print(f"  {_green('[OK]')} CarryMem v{__version__}")
        checks_passed += 1
    except ImportError as e:
        print(f"  {_red('[FAIL]')} CarryMem import: {e}")
        issues.append("CarryMem not importable")

    checks_total += 1
    if _DEFAULT_CONFIG_DIR.exists():
        print(f"  {_green('[OK]')} Config directory: {_DEFAULT_CONFIG_DIR}")
        checks_passed += 1
    else:
        print(f"  {_yellow('[WARN]')} Config directory missing: {_DEFAULT_CONFIG_DIR}")
        issues.append("Config directory missing")
        if parsed.fix:
            _DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            print(f"        Fixed: Created {_DEFAULT_CONFIG_DIR}")

    checks_total += 1
    db = Path(db_path)
    if db.exists():
        size_mb = db.stat().st_size / (1024 * 1024)
        print(f"  {_green('[OK]')} Database: {db} ({size_mb:.2f} MB)")
        checks_passed += 1
    else:
        print(f"  {_yellow('[WARN]')} Database not found: {db}")
        issues.append("Database not initialized")
        if parsed.fix:
            try:
                cm = CarryMem(db_path=db_path)
                cm.declare("CarryMem initialized by doctor")
                cm.close()
                print(f"        Fixed: Created database at {db}")
            except Exception as e:
                print(f"        Fix failed: {e}")

    checks_total += 1
    if db.exists():
        try:
            conn = sqlite3.connect(str(db))
            result = conn.execute("PRAGMA integrity_check").fetchone()
            conn.close()
            if result[0] == "ok":
                print(f"  {_green('[OK]')} Database integrity: OK")
                checks_passed += 1
            else:
                print(f"  {_red('[FAIL]')} Database integrity: {result[0]}")
                issues.append("Database integrity check failed")
        except Exception as e:
            print(f"  {_red('[FAIL]')} Database check error: {e}")
            issues.append(f"Database error: {e}")
    else:
        print(f"  {_dim('[SKIP]')} Database integrity (no database)")

    checks_total += 1
    try:
        test_file = _DEFAULT_CONFIG_DIR / ".doctor_test"
        test_file.touch()
        test_file.unlink()
        print(f"  {_green('[OK]')} Write permissions")
        checks_passed += 1
    except Exception as e:
        print(f"  {_red('[FAIL]')} Write permissions: {e}")
        issues.append("Cannot write to config directory")

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
    try:
        import textual
        optional_deps.append("textual")
    except ImportError:
        pass

    if optional_deps:
        print(f"  {_green('[OK]')} Optional deps: {', '.join(optional_deps)}")
        checks_passed += 1
    else:
        print(f"  {_dim('[INFO]')} No optional deps (pycld2, cryptography, langdetect, textual)")
        checks_passed += 1

    checks_total += 1
    try:
        test_conn = sqlite3.connect(":memory:")
        test_conn.execute("CREATE VIRTUAL TABLE t USING fts5(c)")
        test_conn.close()
        print(f"  {_green('[OK]')} SQLite FTS5 support")
        checks_passed += 1
    except Exception:
        print(f"  {_red('[FAIL]')} SQLite FTS5 not available")
        issues.append("FTS5 not supported (search will be limited)")

    checks_total += 1
    try:
        from memory_classification_engine.security import InputValidator
        validator = InputValidator()
        test_result = validator.validate_content("test content")
        if test_result:
            print(f"  {_green('[OK]')} Security module (InputValidator)")
            checks_passed += 1
        else:
            print(f"  {_yellow('[WARN]')} Security module: validation returned empty")
            issues.append("InputValidator not working correctly")
    except ImportError:
        print(f"  {_dim('[INFO]')} Security module not available")
        checks_passed += 1
    except Exception as e:
        print(f"  {_yellow('[WARN]')} Security module: {e}")
        issues.append(f"Security module issue: {e}")

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
        print(f"  {_green('[OK]')} MCP configs: {', '.join(mcp_configs)}")
        checks_passed += 1
    else:
        print(f"  {_dim('[INFO]')} No MCP configs in current directory")
        print(f"         Run 'carrymem setup-mcp' to configure")
        checks_passed += 1

    checks_total += 1
    if db.exists():
        try:
            cm = CarryMem(db_path=db_path)
            stats = cm.get_stats()
            total = stats.get("total_count", 0)
            print(f"  {_green('[OK]')} Memory count: {total}")
            checks_passed += 1
            cm.close()
        except Exception:
            print(f"  {_yellow('[WARN]')} Cannot read memory count")
            checks_passed += 1
    else:
        print(f"  {_dim('[SKIP]')} Memory count (no database)")
        checks_passed += 1

    print(f"\n  {'=' * 45}")
    if issues:
        print(f"  {_red(f'Issues found ({len(issues)}):')}")
        for issue in issues:
            print(f"    - {issue}")
        if not parsed.fix:
            print(f"\n  {_dim('Tip: Run')} carrymem doctor --fix {_dim('to auto-fix issues')}")
    else:
        print(f"  {_green(f'All checks passed ({checks_passed}/{checks_total})')}")

    print()
    return 0 if not issues else 1


def cmd_setup_mcp(args):
    parser = _make_parser("setup-mcp")
    parser.add_argument("--tool", "-t", choices=["claude-code", "cursor", "all"], default="all", help="Target tool")
    parser.add_argument("--project", "-p", default=".", help="Project directory (default: current)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing config")

    parsed = parser.parse_args(args)
    project_dir = Path(parsed.project).resolve()

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

        skip_claude = False
        if claude_file.exists() and not parsed.force:
            try:
                with open(claude_file) as f:
                    existing = json.load(f)
                if "carrymem" in existing.get("mcpServers", {}):
                    print(f"  {_dim('Claude Code: already configured')} ({claude_file})")
                    configured.append("claude-code")
                    skip_claude = True
            except Exception:
                pass

        if not skip_claude:
            claude_dir.mkdir(parents=True, exist_ok=True)
            if claude_file.exists():
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
            print(f"  {_green('Claude Code:')} configured ({claude_file})")
            configured.append("claude-code")

    if parsed.tool in ("cursor", "all"):
        cursor_dir = project_dir / ".cursor"
        cursor_file = cursor_dir / "mcp.json"

        skip_cursor = False
        if cursor_file.exists() and not parsed.force:
            try:
                with open(cursor_file) as f:
                    existing = json.load(f)
                if "carrymem" in existing.get("mcpServers", {}):
                    print(f"  {_dim('Cursor: already configured')} ({cursor_file})")
                    configured.append("cursor")
                    skip_cursor = True
            except Exception:
                pass

        if not skip_cursor:
            cursor_dir.mkdir(parents=True, exist_ok=True)
            if cursor_file.exists():
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
            print(f"  {_green('Cursor:')} configured ({cursor_file})")
            configured.append("cursor")

    if configured:
        print(f"\n  {_green('MCP integration ready for:')} {', '.join(configured)}")
        print(f"  {_dim(f'Command: {module_cmd}')}")
        print(f"\n  {_bold('Restart your AI tool to activate CarryMem')}")
    else:
        print(f"  {_dim('No tools configured')}")

    return 0


def cmd_serve(args):
    parser = _make_parser("serve")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", "-p", type=int, default=8765, help="Port to listen")
    parser.add_argument("--api-key", help="API key for authentication")

    parsed = parser.parse_args(args)

    from memory_classification_engine.integration.layer2_mcp.http_server import run_http_server
    print(f"\n  {_bold('CarryMem MCP HTTP Server')}")
    print(f"  Host:   {parsed.host}")
    print(f"  Port:   {parsed.port}")
    print(f"  SSE:    {_cyan(f'http://{parsed.host}:{parsed.port}/sse')}")
    print(f"  API:    {_cyan(f'http://{parsed.host}:{parsed.port}/message')}")
    print(f"  Health: {_cyan(f'http://{parsed.host}:{parsed.port}/health')}")
    print()
    run_http_server(host=parsed.host, port=parsed.port, api_key=parsed.api_key)
    return 0


def cmd_tui(args):
    from memory_classification_engine.tui import run_tui, HAS_TEXTUAL
    if not HAS_TEXTUAL:
        print(f"  {_yellow('Textual is not installed.')}")
        print(f"  Install with: {_cyan('pip install textual')}")
        print(f"  Then run: carrymem tui")
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

    print(f"\n  {_bold('Initializing CarryMem...')}\n")

    if not _DEFAULT_CONFIG_DIR.exists():
        _DEFAULT_CONFIG_DIR.mkdir(parents=True)
        print(f"  {_green('[OK]')} Created config directory: {_DEFAULT_CONFIG_DIR}")
    else:
        print(f"  {_green('[OK]')} Config directory exists: {_DEFAULT_CONFIG_DIR}")

    config_file = _DEFAULT_CONFIG_DIR / "config.json"
    if not config_file.exists():
        config = {
            "version": __version__,
            "db_path": db_path,
            "namespace": "default",
        }
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print(f"  {_green('[OK]')} Created config: {config_file}")
    else:
        print(f"  {_green('[OK]')} Config exists: {config_file}")

    try:
        cm = CarryMem(db_path=db_path)
        cm.declare("CarryMem initialized successfully!")
        print(f"  {_green('[OK]')} Database initialized: {db_path}")
        cm.close()
    except Exception as e:
        print(f"  {_red('[FAIL]')} Database init error: {e}")
        return 1

    print(f"\n  {_green(_bold('CarryMem is ready!'))}")
    print(f"\n  {_bold('Quick Start:')}")
    print(f'    carrymem add "I prefer dark mode"')
    print(f"    carrymem list")
    print(f'    carrymem search "theme"')
    print(f"    carrymem setup-mcp --tool cursor")
    print(f"    carrymem tui")
    print()
    return 0


def cmd_version(args):
    print(f"\n  {_bold(f'CarryMem v{__version__}')}")
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
  {_bold(f'CarryMem v{__version__}')} - Your Portable AI Memory Layer

  {_dim('AI remembers you. Not the other way around.')}

  {_bold('Commands:')}
    add <message>        Store a memory
    list                 List recent memories
    search <query>       Search memories
    show <key>           View memory details
    edit <key> <text>    Edit a memory
    forget <key>         Delete a memory
    clean                Remove expired/low-quality
    export <path>        Export memories to file
    import <path>        Import memories from file
    stats                Show memory statistics
    check                Check memory quality & conflicts
    whoami               Who your AI thinks you are
    profile              Export/view your AI identity
    doctor               Run diagnostics
    setup-mcp            Configure MCP integration
    tui                  Launch terminal UI
    serve                Start MCP HTTP server
    init                 Initialize CarryMem
    version              Show version

  {_bold('Examples:')}
    carrymem add "I prefer dark mode"
    carrymem add "test note" --force
    carrymem add "Using React" --namespace work
    carrymem search "theme"
    carrymem show cm_20260423_xxxx
    carrymem edit cm_20260423_xxxx "Updated content"
    carrymem clean --expired --dry-run
    carrymem list --type user_preference --limit 20
    carrymem export backup.json
    carrymem setup-mcp --tool cursor
    carrymem doctor --fix

  {_dim('Documentation: https://github.com/lulin70/memory-classification-engine')}
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
        "ls": cmd_list,
        "search": cmd_search,
        "find": cmd_search,
        "show": cmd_show,
        "get": cmd_show,
        "edit": cmd_edit,
        "update": cmd_edit,
        "forget": cmd_forget,
        "delete": cmd_forget,
        "rm": cmd_forget,
        "clean": cmd_clean,
        "export": cmd_export,
        "import": cmd_import,
        "stats": cmd_stats,
        "status": cmd_stats,
        "check": cmd_check,
        "whoami": cmd_whoami,
        "profile": cmd_profile,
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
        print(f"  {_red('Unknown command:')} {command}")
        help_tip = "Run 'carrymem help' for usage"
        print(f"  {_dim(help_tip)}")
        sys.exit(1)

    try:
        result = handler(remaining_args)
        sys.exit(result if isinstance(result, int) else 0)
    except KeyboardInterrupt:
        print()
        sys.exit(130)
    except Exception as e:
        print(f"  {_red(f'Error: {e}')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
