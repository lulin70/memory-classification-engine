"""
MCP Tool handlers for CarryMem.

3+3+3+2 Optional Mode (v0.8.0):
  Core handlers: classify_message, get_classification_schema, batch_classify
  Storage handlers: classify_and_remember, recall_memories, forget_memory
  Knowledge handlers: index_knowledge, recall_from_knowledge, recall_all
  Profile handlers: declare_preference, get_memory_profile
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List

from .tools import CLASSIFICATION_SCHEMA, TOOL_NAMES, CORE_TOOL_NAMES, OPTIONAL_TOOL_NAMES, KNOWLEDGE_TOOL_NAMES, PROFILE_TOOL_NAMES


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
    status = {
        "status": "active",
        "mode": "3+3_optional",
        "version": "0.6.0",
        "schema_version": "1.0.0",
        "capabilities": {
            "memory_types": 7,
            "storage_tiers": 4,
            "available_tools": list(TOOL_NAMES),
            "core_tools": list(CORE_TOOL_NAMES),
            "optional_tools": list(OPTIONAL_TOOL_NAMES),
        },
        "uptime_seconds": round(time.time() - getattr(engine, '_start_time', time.time()), 1)
    }
    return status


def handle_classify_and_remember(carrymem, arguments: Dict[str, Any]) -> Dict[str, Any]:
    message = arguments.get("message", "")
    context = arguments.get("context")

    if not message.strip():
        return {"error": "Empty message provided"}

    try:
        ctx = None
        if context:
            ctx = {"ai_reply": context}

        result = carrymem.classify_and_remember(message, context=ctx)
        return result
    except Exception as e:
        if "StorageNotConfiguredError" in type(e).__name__:
            return {
                "error": "storage_not_configured",
                "message": "Storage adapter not configured. Use CarryMem(storage='sqlite') to enable storage features.",
                "available_tools": list(CORE_TOOL_NAMES)
            }
        return {"error": str(e)}


def handle_recall_memories(carrymem, arguments: Dict[str, Any]) -> Dict[str, Any]:
    query = arguments.get("query")
    filters = arguments.get("filters")
    limit = arguments.get("limit", 20)

    try:
        results = carrymem.recall_memories(query=query, filters=filters, limit=limit)
        return {"memories": results, "total": len(results)}
    except Exception as e:
        if "StorageNotConfiguredError" in type(e).__name__:
            return {
                "error": "storage_not_configured",
                "message": "Storage adapter not configured. Use CarryMem(storage='sqlite') to enable storage features.",
                "available_tools": list(CORE_TOOL_NAMES)
            }
        return {"error": str(e)}


def handle_forget_memory(carrymem, arguments: Dict[str, Any]) -> Dict[str, Any]:
    memory_id = arguments.get("memory_id", "")

    if not memory_id:
        return {"error": "Missing required field: memory_id"}

    try:
        deleted = carrymem.forget_memory(memory_id)
        return {"deleted": deleted, "memory_id": memory_id}
    except Exception as e:
        if "StorageNotConfiguredError" in type(e).__name__:
            return {
                "error": "storage_not_configured",
                "message": "Storage adapter not configured. Use CarryMem(storage='sqlite') to enable storage features.",
                "available_tools": list(CORE_TOOL_NAMES)
            }
        return {"error": str(e)}


def handle_index_knowledge(carrymem, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        result = carrymem.index_knowledge()
        return {"indexed": True, "stats": result}
    except Exception as e:
        if "KnowledgeNotConfiguredError" in type(e).__name__:
            return {
                "error": "knowledge_not_configured",
                "message": "Knowledge adapter not configured. Use CarryMem(knowledge_adapter=ObsidianAdapter('/path/to/vault')) to enable knowledge features.",
                "available_tools": list(CORE_TOOL_NAMES) + list(OPTIONAL_TOOL_NAMES)
            }
        return {"error": str(e)}


def handle_recall_from_knowledge(carrymem, arguments: Dict[str, Any]) -> Dict[str, Any]:
    query = arguments.get("query", "")
    filters = arguments.get("filters")
    limit = arguments.get("limit", 20)

    if not query.strip():
        return {"error": "Missing required field: query"}

    try:
        results = carrymem.recall_from_knowledge(query=query, filters=filters, limit=limit)
        return {"notes": results, "total": len(results), "source": "knowledge"}
    except Exception as e:
        if "KnowledgeNotConfiguredError" in type(e).__name__:
            return {
                "error": "knowledge_not_configured",
                "message": "Knowledge adapter not configured. Use CarryMem(knowledge_adapter=ObsidianAdapter('/path/to/vault')) to enable knowledge features.",
                "available_tools": list(CORE_TOOL_NAMES) + list(OPTIONAL_TOOL_NAMES)
            }
        return {"error": str(e)}


def handle_recall_all(carrymem, arguments: Dict[str, Any]) -> Dict[str, Any]:
    query = arguments.get("query", "")
    filters = arguments.get("filters")
    limit = arguments.get("limit", 20)

    if not query.strip():
        return {"error": "Missing required field: query"}

    try:
        result = carrymem.recall_all(query=query, filters=filters, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


def handle_declare_preference(carrymem, arguments: Dict[str, Any]) -> Dict[str, Any]:
    message = arguments.get("message", "")

    if not message.strip():
        return {"error": "Missing required field: message"}

    try:
        result = carrymem.declare(message)
        return result
    except Exception as e:
        if "StorageNotConfiguredError" in type(e).__name__:
            return {
                "error": "storage_not_configured",
                "message": "Storage adapter not configured. Use CarryMem(storage='sqlite') to enable storage features.",
                "available_tools": list(CORE_TOOL_NAMES) + list(KNOWLEDGE_TOOL_NAMES)
            }
        return {"error": str(e)}


def handle_get_memory_profile(carrymem, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        profile = carrymem.get_memory_profile()
        return profile
    except Exception as e:
        return {"error": str(e)}


handler_map = {
    "classify_message": handle_classify_message,
    "get_classification_schema": handle_get_classification_schema,
    "batch_classify": handle_batch_classify,
    "mce_status": handle_mce_status,
    "classify_and_remember": handle_classify_and_remember,
    "recall_memories": handle_recall_memories,
    "forget_memory": handle_forget_memory,
    "index_knowledge": handle_index_knowledge,
    "recall_from_knowledge": handle_recall_from_knowledge,
    "recall_all": handle_recall_all,
    "declare_preference": handle_declare_preference,
    "get_memory_profile": handle_get_memory_profile,
}


class Handlers:
    """CarryMem MCP Handlers — 3+3+3+2 optional mode.

    Core tools use engine directly.
    Storage tools use CarryMem instance (with storage adapter).
    Knowledge tools use CarryMem instance (with knowledge adapter).
    Profile tools use CarryMem instance (with storage adapter).
    """

    def __init__(
        self,
        config_path: str = None,
        data_path: str = None,
        storage: str = "sqlite",
        vault_path: str = None,
        namespace: str = "default",
    ):
        from memory_classification_engine.carrymem import CarryMem
        from memory_classification_engine.adapters.obsidian_adapter import ObsidianAdapter

        knowledge_adapter = None
        if vault_path:
            knowledge_adapter = ObsidianAdapter(vault_path)

        self._carrymem = CarryMem(
            storage=storage,
            knowledge_adapter=knowledge_adapter,
            namespace=namespace,
        )
        self._engine = self._carrymem.engine

    async def handle_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name not in handler_map:
            return {
                "error": f"Unknown tool: {tool_name}. Available: {list(handler_map.keys())}",
                "available_tools": list(handler_map.keys())
            }

        handler_func = handler_map[tool_name]
        try:
            if tool_name in OPTIONAL_TOOL_NAMES or tool_name in KNOWLEDGE_TOOL_NAMES or tool_name in PROFILE_TOOL_NAMES:
                result = handler_func(self._carrymem, arguments or {})
            else:
                result = handler_func(self._engine, arguments or {})
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup(self):
        pass
