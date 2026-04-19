"""
MCP Tools definitions for Memory Classification Engine.

This module defines all the tools exposed by the MCP server,
following the Model Context Protocol specification.
"""

from typing import Any, Dict, List

# Comment in Chinese removedtion
TOOLS: List[Dict[str, Any]] = [
    {
        "name": "classify_memory",
        "description": "分析消息并判断是否需要记忆，返回记忆类型、层级和置信度。MCE 是记忆分类中间件——不负责存储，输出可对接任意下游存储方案（Supermemory/Mem0/Obsidian/自定义）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "用户消息内容，需要分析是否包含值得记忆的信息"
                },
                "context": {
                    "type": "string",
                    "description": "对话上下文信息，帮助更准确地判断（可选）"
                }
            },
            "required": ["message"]
        }
    },
    {
        "name": "store_memory",
        "description": "[Deprecated v0.3] 将记忆内容存储到合适的层级，支持7种记忆类型 — 将移至 StorageAdapter 插件。请使用 classify_memory 获取分类结果后自行存储到下游系统。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "记忆的具体内容，简洁准确"
                },
                "memory_type": {
                    "type": "string",
                    "enum": [
                        "user_preference",
                        "correction",
                        "fact_declaration",
                        "decision",
                        "relationship",
                        "task_pattern",
                        "sentiment_marker"
                    ],
                    "description": "记忆类型：用户偏好、纠正信号、事实声明、决策记录、关系信息、任务模式、情感标记"
                },
                "tier": {
                    "type": "integer",
                    "enum": [2, 3, 4],
                    "description": "记忆层级（可选）：2=程序性记忆, 3=情节记忆, 4=语义记忆。如不指定，系统自动判断"
                },
                "context": {
                    "type": "string",
                    "description": "记忆产生的上下文信息（可选）"
                }
            },
            "required": ["content", "memory_type"]
        }
    },
    {
        "name": "retrieve_memories",
        "description": "[Deprecated v0.3] 根据查询内容检索相关记忆 — 将移至 StorageAdapter 插件。请使用下游存储系统（Supermemory/Mem0/Obsidian）的检索接口。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "查询内容，可以是关键词或自然语言描述"
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 50,
                    "description": "返回结果数量限制（默认5条，最大50条）"
                },
                "tier": {
                    "type": "integer",
                    "enum": [2, 3, 4],
                    "description": "指定搜索的记忆层级（可选，不指定则搜索所有层级）"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_memory_stats",
        "description": "[Deprecated v0.3] 获取记忆系统的统计信息 — 将移至 StorageAdapter 插件。请查询下游存储系统的 stats API。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tier": {
                    "type": "integer",
                    "enum": [2, 3, 4],
                    "description": "指定层级的统计信息（可选，不指定则返回所有层级）"
                }
            }
        }
    },
    {
        "name": "batch_classify",
        "description": "批量分类多条消息，每条返回独立分类结果。MCE 是记忆分类中间件——输出可对接任意下游存储方案。适用于对话历史回放、日志分析等批量场景。",
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
                                "description": "消息内容"
                            },
                            "context": {
                                "type": "string",
                                "description": "消息上下文（可选）"
                            }
                        },
                        "required": ["message"]
                    },
                    "description": "需要批量分类的消息列表"
                }
            },
            "required": ["messages"]
        }
    },
    {
        "name": "find_similar",
        "description": "[Deprecated v0.3] 查找与给定内容相似的记忆 — 将移至 StorageAdapter 插件。请使用下游存储系统（向量数据库原生支持）的相似搜索接口。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "用于相似度比较的参考内容"
                },
                "threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.8,
                    "description": "相似度阈值（0-1之间，默认0.8），只有相似度超过此值的记忆才会返回"
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20,
                    "description": "返回结果数量限制（默认5条）"
                }
            },
            "required": ["content"]
        }
    },
    {
        "name": "export_memories",
        "description": "[Deprecated v0.3] 导出记忆数据 — 将移至 StorageAdapter 插件。请使用下游存储系统的导出功能。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["json", "yaml", "csv"],
                    "default": "json",
                    "description": "导出格式（默认json）"
                },
                "tier": {
                    "type": "integer",
                    "enum": [2, 3, 4],
                    "description": "指定导出的记忆层级（可选，不指定则导出所有层级）"
                },
                "memory_type": {
                    "type": "string",
                    "enum": [
                        "user_preference",
                        "correction",
                        "fact_declaration",
                        "decision",
                        "relationship",
                        "task_pattern",
                        "sentiment_marker"
                    ],
                    "description": "指定导出的记忆类型（可选）"
                }
            }
        }
    },
    {
        "name": "import_memories",
        "description": "[Deprecated v0.3] 导入记忆数据 — 将移至 StorageAdapter 插件。请使用下游存储系统的导入功能。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "要导入的记忆数据（JSON/YAML/CSV格式的字符串）"
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "yaml", "csv"],
                    "default": "json",
                    "description": "数据格式（默认json）"
                },
                "merge_strategy": {
                    "type": "string",
                    "enum": ["skip_duplicates", "overwrite", "keep_both"],
                    "default": "skip_duplicates",
                    "description": "重复数据处理策略：skip_duplicates=跳过重复, overwrite=覆盖, keep_both=保留两者"
                }
            },
            "required": ["data"]
        }
    },
    {
        "name": "mce_recall",
        "description": "[Deprecated v0.3] Recall relevant memories — 将移除。记忆召回属于下游存储系统职责（Supermemory recall / Mem0 search）。MCE v0.3+ 只负责分类。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context": {
                    "type": "string",
                    "default": "general",
                    "description": "当前会话上下文 (coding / deployment / general)"
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "maximum": 20,
                    "description": "返回最大记忆数量"
                },
                "types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "user_preference",
                            "correction",
                            "fact_declaration",
                            "decision",
                            "relationship",
                            "task_pattern",
                            "sentiment_marker"
                        ]
                    },
                    "description": "按记忆类型过滤，空=全部"
                },
                "format": {
                    "type": "string",
                    "enum": ["text", "json"],
                    "default": "text",
                    "description": "输出格式"
                },
                "include_pending": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否包含低置信度待确认记忆"
                }
            }
        }
    },
    {
        "name": "mce_status",
        "description": "MCE 引擎状态查看（版本、能力、运行时间）。不包含存储统计——存储统计请查询下游系统。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "detail_level": {
                    "type": "string",
                    "enum": ["summary", "full"],
                    "default": "summary",
                    "description": "详细程度"
                }
            }
        }
    },
    {
        "name": "mce_forget",
        "description": "[Deprecated v0.3] 手动遗忘 — 将移除。记忆删除属于下游存储系统职责。MCE v0.3+ 只负责分类。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "记忆ID"
                },
                "reason": {
                    "type": "string",
                    "description": "遗忘原因（可选）"
                }
            },
            "required": ["memory_id"]
        }
    }
]


# Comment in Chinese removed
TOOL_NAMES = {tool["name"] for tool in TOOLS}


def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """
    Get the schema for a specific tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool schema dictionary
        
    Raises:
        ValueError: If tool not found
    """
    for tool in TOOLS:
        if tool["name"] == tool_name:
            return tool
    raise ValueError(f"Tool not found: {tool_name}")


def validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> List[str]:
    """
    Validate arguments for a tool.
    
    Args:
        tool_name: Name of the tool
        arguments: Arguments to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    try:
        schema = get_tool_schema(tool_name)
    except ValueError as e:
        return [str(e)]
    
    input_schema = schema.get("inputSchema", {})
    required = input_schema.get("required", [])
    properties = input_schema.get("properties", {})
    
    # Comment in Chinese removedlds
    for field in required:
        if field not in arguments:
            errors.append(f"Missing required field: {field}")
    
    # Comment in Chinese removeds
    for field, value in arguments.items():
        if field not in properties:
            errors.append(f"Unknown field: {field}")
            continue
        
        prop_schema = properties[field]
        
        # Comment in Chinese removedtion
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
        
        # Comment in Chinese removedtion
        enum_values = prop_schema.get("enum")
        if enum_values and value not in enum_values:
            errors.append(f"Field {field} must be one of: {enum_values}")
        
        # Comment in Chinese removedrs
        if isinstance(value, (int, float)):
            minimum = prop_schema.get("minimum")
            maximum = prop_schema.get("maximum")
            if minimum is not None and value < minimum:
                errors.append(f"Field {field} must be >= {minimum}")
            if maximum is not None and value > maximum:
                errors.append(f"Field {field} must be <= {maximum}")
    
    return errors
