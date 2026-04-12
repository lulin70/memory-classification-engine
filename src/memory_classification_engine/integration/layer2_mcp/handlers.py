"""
MCP Tool Handlers for Memory Classification Engine.

This module implements the business logic for each MCP tool,
connecting the MCP protocol to the Memory Classification Engine core.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ...engine_facade import MemoryClassificationEngineFacade
from .tools import validate_tool_arguments, TOOL_NAMES


logger = logging.getLogger(__name__)


class Handlers:
    """
    Handlers for MCP tools.
    
    Each method corresponds to a tool defined in tools.py.
    """
    
    def __init__(self, config_path: Optional[str] = None, data_path: Optional[str] = None):
        """
        Initialize handlers with engine facade.
        
        Args:
            config_path: Path to configuration file
            data_path: Path to data directory
        """
        self.engine = MemoryClassificationEngineFacade(config_path)
        self.data_path = data_path
        logger.info("Handlers initialized with engine facade")
    
    async def handle_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route tool calls to appropriate handler.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found or invalid arguments
        """
        # Comment in Chinese removedxists
        if tool_name not in TOOL_NAMES:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Comment in Chinese removednts
        errors = validate_tool_arguments(tool_name, arguments)
        if errors:
            raise ValueError(f"Invalid arguments: {'; '.join(errors)}")
        
        # Comment in Chinese removedr
        handler_map = {
            "classify_memory": self.handle_classify_memory,
            "store_memory": self.handle_store_memory,
            "retrieve_memories": self.handle_retrieve_memories,
            "get_memory_stats": self.handle_get_memory_stats,
            "batch_classify": self.handle_batch_classify,
            "find_similar": self.handle_find_similar,
            "export_memories": self.handle_export_memories,
            "import_memories": self.handle_import_memories,
            "mce_recall": self.handle_mce_recall,
            "mce_status": self.handle_mce_status,
            "mce_forget": self.handle_mce_forget,
        }
        
        handler = handler_map.get(tool_name)
        if not handler:
            raise ValueError(f"Handler not implemented for tool: {tool_name}")
        
        logger.info(f"Executing handler for: {tool_name}")
        return await handler(arguments)
    
    async def handle_classify_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle classify_memory tool.
        
        Args:
            arguments: Tool arguments containing 'message' and optional 'context'
            
        Returns:
            Classification result
        """
        message = arguments["message"]
        context = arguments.get("context")
        
        logger.debug(f"Classifying message: {message[:100]}...")
        
        try:
            result = self.engine.process_message(message, context)
            
            # Comment in Chinese removed
            return {
                "success": True,
                "matched": result.get("matched", False),
                "memory_type": result.get("memory_type"),
                "tier": result.get("tier"),
                "content": result.get("content"),
                "confidence": result.get("confidence"),
                "source": result.get("source"),
                "reasoning": result.get("reasoning"),
                "message": "Message classified successfully"
            }
        except Exception as e:
            logger.error(f"Error classifying message: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to classify message"
            }
    
    async def handle_store_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle store_memory tool.
        
        Args:
            arguments: Tool arguments containing 'content', 'memory_type', etc.
            
        Returns:
            Storage result with memory_id
        """
        content = arguments["content"]
        memory_type = arguments["memory_type"]
        tier = arguments.get("tier")
        context = arguments.get("context")
        
        logger.debug(f"Storing memory: {content[:100]}...")
        
        try:
            # Comment in Chinese removedmory
            storage_service = self.engine.storage_service
            
            memory_data = {
                "type": memory_type,
                "content": content,
                "context": context,
                "confidence": 1.0,  # Comment in Chinese removed
            }
            
            if tier:
                memory_data["tier"] = tier
            
            memory_id = storage_service.store_memory(memory_data)
            
            return {
                "success": True,
                "memory_id": memory_id,
                "stored": True,
                "tier": tier or "auto-determined",
                "message": "Memory stored successfully"
            }
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return {
                "success": False,
                "error": str(e),
                "stored": False,
                "message": "Failed to store memory"
            }
    
    async def handle_retrieve_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle retrieve_memories tool.
        
        Args:
            arguments: Tool arguments containing 'query', 'limit', etc.
            
        Returns:
            List of matching memories
        """
        query = arguments["query"]
        limit = arguments.get("limit", 5)
        tier = arguments.get("tier")
        
        logger.debug(f"Retrieving memories for query: {query}")
        
        try:
            # Comment in Chinese removeds
            storage_service = self.engine.storage_service
            
            memories = storage_service.retrieve_memories(
                query=query,
                limit=limit,
                tier=tier
            )
            
            # Comment in Chinese removed
            formatted_memories = []
            for mem in memories:
                formatted_memories.append({
                    "id": mem.get("id"),
                    "type": mem.get("type"),
                    "tier": mem.get("tier"),
                    "content": mem.get("content"),
                    "confidence": mem.get("confidence"),
                    "created_at": mem.get("created_at"),
                    "relevance_score": mem.get("relevance_score", 0.0)
                })
            
            return {
                "success": True,
                "memories": formatted_memories,
                "count": len(formatted_memories),
                "message": f"Retrieved {len(formatted_memories)} memories"
            }
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return {
                "success": False,
                "error": str(e),
                "memories": [],
                "message": "Failed to retrieve memories"
            }
    
    async def handle_get_memory_stats(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle get_memory_stats tool.
        
        Args:
            arguments: Tool arguments containing optional 'tier'
            
        Returns:
            Memory statistics
        """
        tier = arguments.get("tier")
        
        logger.debug(f"Getting memory stats for tier: {tier or 'all'}")
        
        try:
            # Comment in Chinese removedts
            storage_service = self.engine.storage_service
            
            stats = storage_service.get_stats(tier=tier)
            
            return {
                "success": True,
                "stats": stats,
                "message": "Statistics retrieved successfully"
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get statistics"
            }
    
    async def handle_batch_classify(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle batch_classify tool.
        
        Args:
            arguments: Tool arguments containing 'messages' list
            
        Returns:
            List of classification results
        """
        messages = arguments["messages"]
        
        logger.debug(f"Batch classifying {len(messages)} messages")
        
        results = []
        for msg_data in messages:
            message = msg_data["message"]
            context = msg_data.get("context")
            
            try:
                result = self.engine.process_message(message, context)
                results.append({
                    "message": message[:100] + "..." if len(message) > 100 else message,
                    "matched": result.get("matched", False),
                    "memory_type": result.get("memory_type"),
                    "tier": result.get("tier"),
                    "confidence": result.get("confidence"),
                    "success": True
                })
            except Exception as e:
                logger.error(f"Error in batch classification: {e}")
                results.append({
                    "message": message[:100] + "..." if len(message) > 100 else message,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "results": results,
            "total": len(messages),
            "matched": sum(1 for r in results if r.get("matched")),
            "message": f"Classified {len(messages)} messages"
        }
    
    async def handle_find_similar(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle find_similar tool.
        
        Args:
            arguments: Tool arguments containing 'content', 'threshold', etc.
            
        Returns:
            List of similar memories
        """
        content = arguments["content"]
        threshold = arguments.get("threshold", 0.8)
        limit = arguments.get("limit", 5)
        
        logger.debug(f"Finding similar memories for: {content[:100]}...")
        
        try:
            # Comment in Chinese removeds
            storage_service = self.engine.storage_service
            
            similar_memories = storage_service.find_similar(
                content=content,
                threshold=threshold,
                limit=limit
            )
            
            # Comment in Chinese removed
            formatted_memories = []
            for mem in similar_memories:
                formatted_memories.append({
                    "id": mem.get("id"),
                    "type": mem.get("type"),
                    "tier": mem.get("tier"),
                    "content": mem.get("content"),
                    "similarity_score": mem.get("similarity_score", 0.0),
                    "confidence": mem.get("confidence")
                })
            
            return {
                "success": True,
                "similar_memories": formatted_memories,
                "count": len(formatted_memories),
                "threshold": threshold,
                "message": f"Found {len(formatted_memories)} similar memories"
            }
        except Exception as e:
            logger.error(f"Error finding similar memories: {e}")
            return {
                "success": False,
                "error": str(e),
                "similar_memories": [],
                "message": "Failed to find similar memories"
            }
    
    async def handle_export_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle export_memories tool.
        
        Args:
            arguments: Tool arguments containing 'format', 'tier', etc.
            
        Returns:
            Exported data
        """
        format_type = arguments.get("format", "json")
        tier = arguments.get("tier")
        memory_type = arguments.get("memory_type")
        
        logger.debug(f"Exporting memories in {format_type} format")
        
        try:
            # Comment in Chinese removeds
            storage_service = self.engine.storage_service
            
            data = storage_service.export_memories(
                format=format_type,
                tier=tier,
                memory_type=memory_type
            )
            
            return {
                "success": True,
                "format": format_type,
                "data": data,
                "message": f"Memories exported in {format_type} format"
            }
        except Exception as e:
            logger.error(f"Error exporting memories: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to export memories"
            }
    
    async def handle_import_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle import_memories tool.
        
        Args:
            arguments: Tool arguments containing 'data', 'format', etc.
            
        Returns:
            Import result
        """
        data = arguments["data"]
        format_type = arguments.get("format", "json")
        merge_strategy = arguments.get("merge_strategy", "skip_duplicates")
        
        logger.debug(f"Importing memories from {format_type} data")
        
        try:
            # Comment in Chinese removeds
            storage_service = self.engine.storage_service
            
            result = storage_service.import_memories(
                data=data,
                format=format_type,
                merge_strategy=merge_strategy
            )
            
            return {
                "success": True,
                "imported_count": result.get("imported_count", 0),
                "skipped_count": result.get("skipped_count", 0),
                "error_count": result.get("error_count", 0),
                "message": f"Imported {result.get('imported_count', 0)} memories"
            }
        except Exception as e:
            logger.error(f"Error importing memories: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to import memories"
            }
    
    async def handle_mce_recall(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle mce_recall tool.
        
        Args:
            arguments: Tool arguments containing 'context', 'limit', etc.
            
        Returns:
            Formatted memory recall result
        """
        context = arguments.get("context", "general")
        limit = arguments.get("limit", 5)
        memory_types = arguments.get("types")
        format_type = arguments.get("format", "text")
        include_pending = arguments.get("include_pending", True)
        
        logger.debug(f"Recalling memories for context: {context}")
        
        try:
            # Get storage service
            storage_service = self.engine.storage_service
            
            # Retrieve memories based on context
            memories = storage_service.retrieve_memories(
                query=context,
                limit=limit,
                memory_type=memory_types[0] if memory_types else None
            )
            
            # Get stats for the recall
            stats = storage_service.get_stats()
            total_memories = stats.get("total_memories", 0)
            
            if format_type == "text":
                # Generate text format response
                text_response = "📝 MCE Memory Recall\n\n"
                text_response += f"## 已加载的记忆 ({len(memories)}/{limit})\n"
                
                for mem in memories:
                    memory_type = mem.get("type", "unknown")
                    content = mem.get("content", "")
                    confidence = mem.get("confidence", 0.0)
                    source = mem.get("source", "unknown")
                    
                    # Map memory type to Chinese label
                    type_label_map = {
                        "user_preference": "偏好",
                        "correction": "纠正",
                        "fact_declaration": "事实",
                        "decision": "决策",
                        "relationship": "关系",
                        "task_pattern": "任务模式",
                        "sentiment_marker": "情感标记"
                    }
                    type_label = type_label_map.get(memory_type, memory_type)
                    
                    text_response += f"- [{type_label}] {content}          置信度{confidence:.2f} {source}\n"
                
                text_response += "\n## 统计信息\n"
                text_response += f"- 过滤噪音: {total_memories - len(memories)}条\n"
                text_response += f"- LLM调用: 0次\n"
                text_response += f"- 处理消息: {stats.get('total_processed', 0)}条\n"
                text_response += f"- 本周新增: {stats.get('weekly_additions', 0)}条记忆\n"
                text_response += "\n💡 这些记忆将影响我的回复，确保一致性体验\n"
                
                return {
                    "success": True,
                    "content": text_response,
                    "format": "text",
                    "memories_count": len(memories),
                    "message": "Memory recall completed"
                }
            else:
                # Generate JSON format response
                formatted_memories = []
                for mem in memories:
                    formatted_memories.append({
                        "id": mem.get("id"),
                        "type": mem.get("type"),
                        "content": mem.get("content"),
                        "confidence": mem.get("confidence"),
                        "source": mem.get("source"),
                        "tier": mem.get("tier"),
                        "created_at": mem.get("created_at")
                    })
                
                return {
                    "success": True,
                    "memories": formatted_memories,
                    "stats": {
                        "total_memories": total_memories,
                        "recalled_count": len(memories),
                        "noise_filtered": total_memories - len(memories),
                        "llm_calls": 0,
                        "total_processed": stats.get('total_processed', 0),
                        "weekly_additions": stats.get('weekly_additions', 0)
                    },
                    "format": "json",
                    "message": "Memory recall completed"
                }
        except Exception as e:
            logger.error(f"Error in mce_recall: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to recall memories"
            }
    
    async def handle_mce_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle mce_status tool.
        
        Args:
            arguments: Tool arguments containing 'detail_level'
            
        Returns:
            Memory status information
        """
        detail_level = arguments.get("detail_level", "summary")
        
        logger.debug(f"Getting memory status with detail level: {detail_level}")
        
        try:
            # Get storage service
            storage_service = self.engine.storage_service
            
            # Get stats
            stats = storage_service.get_stats()
            
            if detail_level == "full":
                return {
                    "success": True,
                    "status": "active",
                    "detail_level": "full",
                    "stats": stats,
                    "message": "Full memory status retrieved"
                }
            else:
                # Summary level
                summary_stats = {
                    "total_memories": stats.get("total_memories", 0),
                    "by_type": stats.get("type_stats", {}),
                    "by_tier": stats.get("tier_stats", {}),
                    "total_processed": stats.get("total_processed", 0),
                    "weekly_additions": stats.get("weekly_additions", 0)
                }
                
                return {
                    "success": True,
                    "status": "active",
                    "detail_level": "summary",
                    "stats": summary_stats,
                    "message": "Summary memory status retrieved"
                }
        except Exception as e:
            logger.error(f"Error in mce_status: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get memory status"
            }
    
    async def handle_mce_forget(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle mce_forget tool.
        
        Args:
            arguments: Tool arguments containing 'memory_id' and optional 'reason'
            
        Returns:
            Forgetting result
        """
        memory_id = arguments["memory_id"]
        reason = arguments.get("reason", "user_request")
        
        logger.debug(f"Forgetting memory with ID: {memory_id}")
        
        try:
            # Get storage service
            storage_service = self.engine.storage_service
            
            # Remove the memory
            success = storage_service.delete_memory(memory_id)
            
            if success:
                return {
                    "success": True,
                    "memory_id": memory_id,
                    "forgotten": True,
                    "reason": reason,
                    "message": "Memory forgotten successfully"
                }
            else:
                return {
                    "success": False,
                    "memory_id": memory_id,
                    "forgotten": False,
                    "message": "Memory not found or could not be forgotten"
                }
        except Exception as e:
            logger.error(f"Error in mce_forget: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to forget memory"
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up handlers...")
        # Comment in Chinese removed
