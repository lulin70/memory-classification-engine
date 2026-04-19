"""
MCP Tool handlers for Memory Classification Engine.

Pure Upstream Mode (v0.3.0): Only classification handlers are present.
Storage, retrieval, and CRUD operations have been removed.
Output follows MemoryEntry JSON Schema v1.0 for downstream compatibility.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List

from .tools import CLASSIFICATION_SCHEMA, TOOL_NAMES


def _format_memory_entry(match: Dict[str, Any], original_message: str) -> Dict[str, Any]:
    """Convert a raw engine match dict to standardized MemoryEntry v1.0."""
    from uuid import uuid4

    mem_type = match.get("memory_type") or match.get("type", "unknown")
    confidence = match.get("confidence", 0.0)
    tier = match.get("tier", 2)

    return {
        "id": f"mce_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}",
        "type": mem_type,
        "content": match.get("content") or original_message[:200],
        "confidence": round(confidence, 4),
        "tier": tier,
        "source_layer": match.get("source", "unknown"),
        "reasoning": match.get("reasoning", ""),
        "suggested_action": "store" if confidence > 0.5 else ("defer" if confidence > 0.3 else "ignore"),
        "metadata": {
            "original_message": original_message,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z"
        }
    }


def _build_summary(entries: List[Dict[str, Any]], llm_calls: int = 0) -> Dict[str, Any]:
    """Build summary section of MemoryEntry output."""
    by_type: Dict[str, int] = {}
    by_tier: Dict[int, int] = {}
    total_confidence = 0.0

    for entry in entries:
        by_type[entry["type"]] = by_type.get(entry["type"], 0) + 1
        by_tier[entry["tier"]] = by_tier.get(entry["tier"], 0) + 1
        total_confidence += entry["confidence"]

    return {
        "total_entries": len(entries),
        "by_type": by_type,
        "by_tier": by_tier,
        "avg_confidence": round(total_confidence / max(len(entries), 1), 4),
        "filtered_count": 0,
        "llm_calls_used": llm_calls
    }


def handle_classify_message(engine, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify a single message and return MemoryEntry v1.0.

    This is the core MCE tool. It analyzes whether a message contains
    memorable information and returns structured classification results.
    The output is designed to be directly consumable by any downstream
    storage system.
    """
    message = arguments.get("message", "")
    context = arguments.get("context")

    if not message.strip():
        return {
            "schema_version": "1.0.0",
            "should_remember": False,
            "entries": [],
            "summary": {"total_entries": 0},
            "engine_info": {"mode": "classification_only"},
            "error": "Empty message provided"
        }

    try:
        result = engine.process_message(message, context)
        matches = result.get("matches", [])
        processing_time = result.get("processing_time", 0)

        entries = [_format_memory_entry(m, message) for m in matches]

        return {
            "schema_version": "1.0.0",
            "should_remember": len(entries) > 0,
            "entries": entries,
            "summary": _build_summary(entries),
            "engine_info": {
                "mode": "classification_only",
                "processing_time_ms": round(processing_time * 1000, 2) if processing_time else None
            }
        }
    except Exception as e:
        return {
            "schema_version": "1.0.0",
            "should_remember": False,
            "entries": [],
            "summary": {"total_entries": 0},
            "engine_info": {"mode": "classification_only"},
            "error": str(e)
        }


def handle_get_classification_schema(engine, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return MCE's complete classification schema definition.

    This includes all 7 memory types with examples and downstream mappings,
    4 storage tiers, confidence thresholds, and output format specification.
    Downstream systems use this to auto-map MCE output to their own data model.
    """
    fmt = arguments.get("format", "json")

    if fmt == "markdown":
        lines = [
            "# MCE Classification Schema v1.0",
            "",
            f"**Engine Version**: {CLASSIFICATION_SCHEMA['engine_version']}",
            f"**Mode**: {CLASSIFICATION_SCHEMA['mode']}",
            "",
            "## Memory Types (7)",
            ""
        ]
        for mt in CLASSIFICATION_SCHEMA["memory_types"]:
            lines.append(f"### {mt['id']} ({mt['label_en']} / {mt['label_zh']})")
            lines.append(f"- **Description**: {mt['description']}")
            lines.append(f"- **Examples**: {', '.join(mt['examples'])}")
            lines.append(f"- **Default Tier**: T{mt['default_tier']}")
            lines.append(f"- **Downstream Mapping**:")
            for ds, cat in mt["downstream_mapping"].items():
                lines.append(f"  - {ds}: `{cat}`")
            lines.append("")
        return {"schema": "\n".join(lines), "format": "markdown"}

    return {
        "schema": CLASSIFICATION_SCHEMA,
        "format": "json"
    }


def handle_batch_classify(engine, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Batch classify multiple messages, each returning independent MemoryEntry.

    Suitable for conversation history replay, log analysis, etc.
    Each message is classified independently; results are returned as an array.
    """
    messages_data = arguments.get("messages", [])

    if not messages_data:
        return {
            "results": [],
            "summary": {"total_messages": 0, "total_entries": 0},
            "error": "No messages provided"
        }

    results = []
    total_entries = 0

    for msg_item in messages_data:
        msg_text = msg_item.get("message", "")
        msg_context = msg_item.get("context")
        msg_result = handle_classify_message(engine, {"message": msg_text, "context": msg_context})
        results.append(msg_result)
        total_entries += len(msg_result.get("entries", []))

    return {
        "results": results,
        "summary": {
            "total_messages": len(messages_data),
            "total_entries": total_entries,
            "messages_with_memories": sum(1 for r in results if r.get("should_remember"))
        }
    }


def handle_mce_status(engine, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return MCE engine status (version, capabilities, uptime).

    Does NOT include storage statistics — those belong to downstream systems.
    """
    detail_level = arguments.get("detail_level", "summary")

    status = {
        "status": "active",
        "mode": "classification_only",
        "version": getattr(engine, 'ENGINE_VERSION', '0.3.0'),
        "schema_version": "1.0.0",
        "capabilities": {
            "memory_types": 7,
            "storage_tiers": 4,
            "supported_output_formats": ["json"],
            "available_tools": list(TOOL_NAMES)
        },
        "uptime_seconds": round(time.time() - getattr(engine, '_start_time', time.time()), 1)
    }

    if detail_level == "full":
        rules_config = getattr(engine, '_rules_config', None)
        if rules_config:
            status["configuration"] = {
                "llm_enabled": getattr(engine, '_llm_enabled', False),
                "rule_count": len(rules_config.get('rules', [])) if isinstance(rules_config, dict) else 0,
                "auto_learning_enabled": getattr(engine, '_auto_learn', True)
            }

    return status


handler_map = {
    "classify_message": handle_classify_message,
    "get_classification_schema": handle_get_classification_schema,
    "batch_classify": handle_batch_classify,
    "mce_status": handle_mce_status
}


class Handlers:
    """Backward-compatible wrapper for server.py integration.

    Server.py expects a Handlers class with __init__(config_path, data_path)
    and async handle_tool(tool_name, arguments) method.
    This class bridges that interface to the new function-based handlers.
    """

    def __init__(self, config_path: str = None, data_path: str = None):
        from memory_classification_engine import MemoryClassificationEngine
        self._engine = MemoryClassificationEngine(config_path=config_path)

    async def handle_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Route tool calls to the appropriate handler function."""
        if tool_name not in handler_map:
            return {
                "error": f"Unknown tool: {tool_name}. Available: {list(handler_map.keys())}",
                "available_tools": list(handler_map.keys())
            }

        handler_func = handler_map[tool_name]
        try:
            result = handler_func(self._engine, arguments or {})
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup(self):
        """Cleanup resources (no-op in pure classification mode)."""
        pass
