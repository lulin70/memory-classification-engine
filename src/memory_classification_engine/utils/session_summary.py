"""Session summary utility for Memory Classification Engine.

This module provides functionality to generate summaries of memories created during a session,
helping users understand what was learned and stored during their interaction.
"""

from typing import List, Dict, Any
from datetime import datetime


def generate_session_summary(memories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a summary of memories created during a session.
    
    Args:
        memories: List of memories created during the session
        
    Returns:
        Dictionary containing the session summary
    """
    if not memories:
        return {
            "success": True,
            "summary": "本次会话没有新的记忆记录。",
            "stats": {
                "total_memories": 0,
                "by_type": {},
                "by_tier": {}
            }
        }
    
    # Group memories by type
    by_type = {}
    by_tier = {}
    
    for memory in memories:
        # Group by type
        mem_type = memory.get('memory_type', 'unknown')
        if mem_type not in by_type:
            by_type[mem_type] = []
        by_type[mem_type].append(memory.get('content', ''))
        
        # Group by tier
        tier = memory.get('tier', 3)
        if tier not in by_tier:
            by_tier[tier] = 0
        by_tier[tier] += 1
    
    # Generate summary text
    summary_parts = ["本次会话新增记忆："]
    
    for mem_type, contents in by_type.items():
        summary_parts.append(f"\n{mem_type}:")
        for content in contents:
            summary_parts.append(f"- {content}")
    
    summary = "\n".join(summary_parts)
    
    # Calculate stats
    stats = {
        "total_memories": len(memories),
        "by_type": by_type,
        "by_tier": by_tier,
        "unique_types": len(by_type),
        "session_end_time": datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "summary": summary,
        "stats": stats
    }


def format_session_summary(summary_data: Dict[str, Any], format_type: str = "text") -> str:
    """Format the session summary in the specified format.
    
    Args:
        summary_data: Session summary data from generate_session_summary
        format_type: Output format ('text' or 'json')
        
    Returns:
        Formatted session summary
    """
    if format_type == "json":
        import json
        return json.dumps(summary_data, indent=2, ensure_ascii=False)
    
    # Text format
    if not summary_data.get("success"):
        return "生成会话摘要失败：" + summary_data.get("error", "未知错误")
    
    summary = summary_data.get("summary", "")
    stats = summary_data.get("stats", {})
    
    # Add stats to the summary
    stats_section = "\n\n## 统计信息"
    stats_section += f"\n- 总记忆数: {stats.get('total_memories', 0)}"
    stats_section += f"\n- 记忆类型: {stats.get('unique_types', 0)} 种"
    
    if stats.get('by_tier'):
        stats_section += "\n- 按层级分布:"
        for tier, count in stats.get('by_tier', {}).items():
            tier_name = {
                2: "程序性记忆",
                3: "情节记忆",
                4: "语义记忆"
            }.get(tier, f"层级 {tier}")
            stats_section += f"\n  - {tier_name}: {count} 条"
    
    return summary + stats_section


def get_session_memories(storage_service: Any, session_start_time: datetime) -> List[Dict[str, Any]]:
    """Get memories created during the current session.
    
    Args:
        storage_service: Storage service instance
        session_start_time: Session start time
        
    Returns:
        List of memories created during the session
    """
    # Get all memories
    all_memories = []
    
    # Try to get memories from all tiers
    try:
        # This is a placeholder - actual implementation depends on the storage service API
        # In a real implementation, you would query the storage service for memories
        # created after session_start_time
        all_memories = storage_service.retrieve_memories(query="", limit=100)
    except Exception as e:
        print(f"Error retrieving session memories: {e}")
    
    # Filter memories created during the session
    session_memories = []
    for memory in all_memories:
        created_at = memory.get('created_at')
        if created_at:
            # Convert to datetime if it's a string
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    continue
            
            # Check if memory was created during the session
            if created_at >= session_start_time:
                session_memories.append(memory)
    
    return session_memories
