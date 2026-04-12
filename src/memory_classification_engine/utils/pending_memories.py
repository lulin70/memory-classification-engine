"""Pending memories utility for Memory Classification Engine.

This module provides functionality to handle pending memories that require user confirmation,
allowing users to review and approve or reject memories before they are stored permanently.
"""

from typing import List, Dict, Any
from datetime import datetime


class PendingMemoryManager:
    """Manager for pending memories that require user confirmation."""
    
    def __init__(self, storage_service: Any):
        """Initialize the pending memory manager.
        
        Args:
            storage_service: Storage service instance
        """
        self.storage_service = storage_service
        self.pending_memories = []
    
    def add_pending_memory(self, memory: Dict[str, Any]) -> str:
        """Add a memory to the pending queue for user confirmation.
        
        Args:
            memory: Memory data to add to pending queue
            
        Returns:
            Memory ID
        """
        # Add pending status and timestamp
        pending_memory = memory.copy()
        pending_memory['status'] = 'pending'
        pending_memory['created_at'] = datetime.now().isoformat()
        pending_memory['id'] = f"pending_{datetime.now().timestamp()}"
        
        # Add to pending queue
        self.pending_memories.append(pending_memory)
        
        return pending_memory['id']
    
    def get_pending_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending memories for user review.
        
        Args:
            limit: Maximum number of pending memories to return
            
        Returns:
            List of pending memories
        """
        return self.pending_memories[:limit]
    
    def approve_memory(self, memory_id: str) -> bool:
        """Approve a pending memory and store it permanently.
        
        Args:
            memory_id: ID of the pending memory to approve
            
        Returns:
            True if successful, False otherwise
        """
        # Find the pending memory
        for i, memory in enumerate(self.pending_memories):
            if memory['id'] == memory_id:
                # Remove pending status
                approved_memory = memory.copy()
                del approved_memory['status']
                del approved_memory['id']  # Let storage service generate a new ID
                
                # Store the memory permanently
                success = self.storage_service.store_memory(approved_memory)
                
                if success:
                    # Remove from pending queue
                    self.pending_memories.pop(i)
                
                return success
        
        return False
    
    def reject_memory(self, memory_id: str) -> bool:
        """Reject a pending memory and remove it from the queue.
        
        Args:
            memory_id: ID of the pending memory to reject
            
        Returns:
            True if successful, False otherwise
        """
        # Find and remove the pending memory
        for i, memory in enumerate(self.pending_memories):
            if memory['id'] == memory_id:
                self.pending_memories.pop(i)
                return True
        
        return False
    
    def get_pending_count(self) -> int:
        """Get the number of pending memories.
        
        Returns:
            Number of pending memories
        """
        return len(self.pending_memories)
    
    def clear_all_pending(self) -> int:
        """Clear all pending memories.
        
        Returns:
            Number of pending memories cleared
        """
        count = len(self.pending_memories)
        self.pending_memories.clear()
        return count


def generate_pending_memory_prompt(memory: Dict[str, Any]) -> str:
    """Generate a prompt for user to review a pending memory.
    
    Args:
        memory: Pending memory data
        
    Returns:
        Formatted prompt string
    """
    memory_type = memory.get('memory_type', 'unknown')
    content = memory.get('content', '')
    confidence = memory.get('confidence', 0.0)
    source = memory.get('source', 'unknown')
    
    prompt = f"📝 Pending Memory Review\n"
    prompt += f"\nMemory Type: {memory_type}"
    prompt += f"\nContent: {content}"
    prompt += f"\nConfidence: {confidence:.2f}"
    prompt += f"\nSource: {source}"
    prompt += "\n\nDo you want to save this memory?"
    prompt += "\n1. Yes - Save this memory"
    prompt += "\n2. No - Reject this memory"
    prompt += "\n3. Edit - Modify the memory before saving"
    
    return prompt


def format_pending_memories_summary(pending_memories: List[Dict[str, Any]]) -> str:
    """Format a summary of pending memories.
    
    Args:
        pending_memories: List of pending memories
        
    Returns:
        Formatted summary string
    """
    if not pending_memories:
        return "No pending memories to review."
    
    summary = f"📋 You have {len(pending_memories)} pending memories to review:\n\n"
    
    for i, memory in enumerate(pending_memories, 1):
        memory_type = memory.get('memory_type', 'unknown')
        content = memory.get('content', '')
        confidence = memory.get('confidence', 0.0)
        
        summary += f"{i}. [{memory_type}] {content[:50]}{'...' if len(content) > 50 else ''}"
        summary += f" (Confidence: {confidence:.2f})\n"
    
    summary += "\nUse 'approve <number>' to save a memory, 'reject <number>' to discard it, or 'review <number>' to see details."
    
    return summary
