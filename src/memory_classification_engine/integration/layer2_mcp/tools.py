"""
MCP Tools definitions for Memory Classification Engine.

Pure Upstream Mode (v0.3.0): Only classification tools are exposed.
Storage, retrieval, and CRUD operations are delegated to downstream systems
(Supermemory / Mem0 / Obsidian / custom) via StorageAdapter interface.
"""

from typing import Any, Dict, List

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "classify_message",
        "description": "Analyze a message and determine if it contains memorable information. Returns a standardized MemoryEntry JSON with type, tier, confidence, and suggested_action. MCE is a memory classification middleware — it does NOT store memories. Output can be sent to any downstream storage system (Supermemory/Mem0/Obsidian/custom).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message content to analyze for memorable information"
                },
                "context": {
                    "type": "string",
                    "description": "Conversation context for more accurate classification (optional)"
                }
            },
            "required": ["message"]
        }
    },
    {
        "name": "get_classification_schema",
        "description": "Return MCE's complete classification schema definition including 7 memory types, 4 storage tiers, confidence thresholds, and downstream mapping tables. Use this to understand the MemoryEntry output format and map MCE types to your storage system's categories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "json",
                    "description": "Output format"
                }
            }
        }
    },
    {
        "name": "batch_classify",
        "description": "Batch classify multiple messages, each returning an independent MemoryEntry. MCE is a memory classification middleware — output can be sent to any downstream storage system. Suitable for conversation history replay, log analysis, and batch processing scenarios.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message content"
                            },
                            "context": {
                                "type": "string",
                                "description": "Message context (optional)"
                            }
                        },
                        "required": ["message"]
                    },
                    "description": "List of messages to batch classify"
                }
            },
            "required": ["messages"]
        }
    },
    {
        "name": "mce_status",
        "description": "MCE engine status information (version, capabilities, uptime). Does NOT include storage statistics — query your downstream system for those.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "detail_level": {
                    "type": "string",
                    "enum": ["summary", "full"],
                    "default": "summary",
                    "description": "Detail level of status output"
                }
            }
        }
    }
]

TOOL_NAMES = {tool["name"] for tool in TOOLS}

CLASSIFICATION_SCHEMA = {
    "schema_version": "1.0.0",
    "engine_version": "0.3.0",
    "mode": "classification_only",
    "memory_types": [
        {
            "id": "user_preference",
            "label_en": "User Preference",
            "label_zh": "用户偏好",
            "description": "User habits, preferences, style choices that affect future behavior",
            "examples": ["I prefer double quotes", "Use camelCase naming", "Dark mode please"],
            "default_tier": 2,
            "persistence_hint": "short_term_to_long_term",
            "downstream_mapping": {
                "supermemory": "preference",
                "mem0": "user_profile",
                "obsidian": "# Preferences",
                "custom_field": "category"
            }
        },
        {
            "id": "correction",
            "label_en": "Correction",
            "label_zh": "纠正信号",
            "description": "Corrections, clarifications, or negations of previous information",
            "examples": ["No, that's wrong", "Actually use X not Y", "Let me correct that"],
            "default_tier": 2,
            "persistence_hint": "immediate",
            "downstream_mapping": {
                "supermemory": "correction",
                "mem0": "correction",
                "obsidian": "# Corrections",
                "custom_field": "category"
            }
        },
        {
            "id": "fact_declaration",
            "label_en": "Fact Declaration",
            "label_zh": "事实声明",
            "description": "Factual statements, verifiable truths about the world or project",
            "examples": ["We have 100 employees", "Python 3.9 required", "Deployed on AWS"],
            "default_tier": 3,
            "persistence_hint": "long_term",
            "downstream_mapping": {
                "supermemory": "fact",
                "mem0": "fact",
                "obsidian": "# Facts",
                "custom_field": "category"
            }
        },
        {
            "id": "decision",
            "label_en": "Decision Record",
            "label_zh": "决策记录",
            "description": "Decisions made, choices selected, with reasoning context",
            "examples": ["We chose Redis for caching", "Go with PostgreSQL", "Use REST not GraphQL"],
            "default_tier": 3,
            "persistence_hint": "long_term",
            "downstream_mapping": {
                "supermemory": "decision",
                "mem0": "decision",
                "obsidian": "# Decisions",
                "custom_field": "category"
            }
        },
        {
            "id": "relationship",
            "label_en": "Relationship Mapping",
            "label_zh": "关系映射",
            "description": "Relationships between entities, roles, ownerships, or connections",
            "examples": ["Alice owns backend", "Bob reports to Carol", "Module X depends on Y"],
            "default_tier": 4,
            "persistence_hint": "archive",
            "downstream_mapping": {
                "supermemory": "relation",
                "mem0": "relationship",
                "obsidian": "# Relationships",
                "custom_field": "category"
            }
        },
        {
            "id": "task_pattern",
            "label_en": "Task Pattern",
            "label_zh": "任务模式",
            "description": "Recurring workflows, automation rules, procedural patterns",
            "examples": ["Always test before deploy", "Run lint on every PR", "Review on Fridays"],
            "default_tier": 2,
            "persistence_hint": "short_term_to_long_term",
            "downstream_mapping": {
                "supermemory": "pattern",
                "mem0": "workflow",
                "obsidian": "# Patterns",
                "custom_field": "category"
            }
        },
        {
            "id": "sentiment_marker",
            "label_en": "Sentiment Marker",
            "label_zh": "情感标记",
            "description": "Emotional signals, pain points, satisfaction indicators",
            "examples": ["This workflow is frustrating", "Love this approach", "Too many meetings"],
            "default_tier": 3,
            "persistence_hint": "medium_term",
            "downstream_mapping": {
                "supermemory": "sentiment",
                "mem0": "emotion",
                "obsidian": "# Sentiments",
                "custom_field": "category"
            }
        }
    ],
    "storage_tiers": [
        {"id": 1, "name": "Sensory", "zh_name": "感觉记忆", "duration": "<1s", "action": "ignore"},
        {"id": 2, "name": "Procedural/Working", "zh_name": "程序性记忆", "duration": "hours-days", "action": "cache"},
        {"id": 3, "name": "Episodic", "zh_name": "情节记忆", "duration": "days-months", "action": "persist"},
        {"id": 4, "name": "Semantic", "zh_name": "语义记忆", "duration": "months-years", "action": "archive"}
    ],
    "confidence_thresholds": {
        "high": 0.85,
        "medium": 0.60,
        "low": 0.30
    },
    "suggested_actions": {
        "store": "High-confidence memory, should be persisted to downstream storage",
        "defer": "Medium-confidence, may be worth storing after more context accumulates",
        "ignore": "Low-confidence or no memorable content, safe to discard"
    },
    "output_format": {
        "root_keys": ["schema_version", "should_remember", "entries", "summary", "engine_info"],
        "entry_keys": ["id", "type", "content", "confidence", "tier", "source_layer", "reasoning", "suggested_action", "metadata"]
    }
}


def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """Get the schema for a specific tool."""
    for tool in TOOLS:
        if tool["name"] == tool_name:
            return tool
    raise ValueError(f"Tool not found: {tool_name}. Available: {TOOL_NAMES}")


def validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> List[str]:
    """Validate arguments for a tool."""
    errors = []
    
    try:
        schema = get_tool_schema(tool_name)
    except ValueError as e:
        return [str(e)]
    
    input_schema = schema.get("inputSchema", {})
    required = input_schema.get("required", [])
    properties = input_schema.get("properties", {})
    
    for field in required:
        if field not in arguments:
            errors.append(f"Missing required field: {field}")
    
    for field, value in arguments.items():
        if field not in properties:
            errors.append(f"Unknown field: {field}")
            continue
        
        prop_schema = properties[field]
        
        expected_type = prop_schema.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"Field {field} must be a string")
        elif expected_type == "integer" and not isinstance(value, int):
            errors.append(f"Field {field} must be an integer")
        elif expected_type == "number" and not isinstance(value, (int, float)):
            errors.append(f"Field {field} must be a number")
        elif expected_type == "array" and not isinstance(value, list):
            errors.append(f"Field {field} must be an array")
        elif expected_type == "object" and not isinstance(value, dict):
            errors.append(f"Field {field} must be an object")
        
        enum_values = prop_schema.get("enum")
        if enum_values and value not in enum_values:
            errors.append(f"Field {field} must be one of: {enum_values}")
        
        if isinstance(value, (int, float)):
            minimum = prop_schema.get("minimum")
            maximum = prop_schema.get("maximum")
            if minimum is not None and value < minimum:
                errors.append(f"Field {field} must be >= {minimum}")
            if maximum is not None and value > maximum:
                errors.append(f"Field {field} must be <= {maximum}")
    
    return errors
