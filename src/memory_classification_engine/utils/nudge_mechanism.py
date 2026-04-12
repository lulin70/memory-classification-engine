"""Nudge mechanism for Memory Classification Engine.

This module provides functionality to actively nudge users to review and validate their memories,
ensuring memory accuracy and freshness over time.
"""

from typing import List, Dict, Any, Callable
from datetime import datetime, timedelta
import random


class NudgeManager:
    """Manager for the nudge mechanism to encourage memory review and validation."""
    
    def __init__(self, storage_service: Any):
        """Initialize the nudge manager.
        
        Args:
            storage_service: Storage service instance
        """
        self.storage_service = storage_service
        self.nudge_history = []
        self.nudge_threshold = 7  # Days since last review
    
    def get_nudge_candidates(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get memory candidates for nudge based on review frequency and importance.
        
        Args:
            limit: Maximum number of nudge candidates to return
            
        Returns:
            List of memory candidates for review
        """
        # Get all memories
        all_memories = self.storage_service.retrieve_memories(query="", limit=100)
        
        # Filter and score memories based on nudge criteria
        candidates = []
        for memory in all_memories:
            score = self._calculate_nudge_score(memory)
            if score > 0:
                memory['nudge_score'] = score
                candidates.append(memory)
        
        # Sort by nudge score (highest first)
        candidates.sort(key=lambda x: x.get('nudge_score', 0), reverse=True)
        
        return candidates[:limit]
    
    def _calculate_nudge_score(self, memory: Dict[str, Any]) -> float:
        """Calculate nudge score for a memory based on various factors.
        
        Args:
            memory: Memory data
            
        Returns:
            Nudge score (higher score means more urgent need for review)
        """
        score = 0.0
        
        # Factor 1: Time since last review (if available)
        last_reviewed = memory.get('last_reviewed')
        if last_reviewed:
            try:
                last_reviewed_date = datetime.fromisoformat(last_reviewed)
                days_since_review = (datetime.now() - last_reviewed_date).days
                if days_since_review > self.nudge_threshold:
                    score += days_since_review / self.nudge_threshold
            except ValueError:
                pass
        else:
            # Never reviewed, high priority
            score += 5.0
        
        # Factor 2: Memory type importance
        memory_type = memory.get('memory_type', 'unknown')
        type_importance = {
            'user_preference': 3.0,
            'correction': 2.5,
            'decision': 4.0,
            'relationship': 2.0,
            'task_pattern': 3.5,
            'sentiment_marker': 1.0,
            'fact_declaration': 2.0
        }
        score += type_importance.get(memory_type, 1.0)
        
        # Factor 3: Confidence score (lower confidence needs more review)
        confidence = memory.get('confidence', 0.0)
        score += (1.0 - confidence) * 2.0
        
        # Factor 4: Usage frequency (if available)
        usage_count = memory.get('usage_count', 0)
        if usage_count > 0:
            # Memories used more frequently need less review
            score -= min(usage_count / 10.0, 2.0)
        
        return max(score, 0.0)
    
    def generate_nudge_prompt(self, memory: Dict[str, Any]) -> str:
        """Generate a nudge prompt for a memory review.
        
        Args:
            memory: Memory data
            
        Returns:
            Formatted nudge prompt
        """
        memory_type = memory.get('memory_type', 'unknown')
        content = memory.get('content', '')
        created_at = memory.get('created_at', 'Unknown')
        
        # Get type-specific prompt
        type_prompts = {
            'user_preference': "Do you still prefer this?",
            'correction': "Is this correction still relevant?",
            'decision': "Is this decision still valid?",
            'relationship': "Is this relationship still accurate?",
            'task_pattern': "Do you still follow this pattern?",
            'sentiment_marker': "How do you feel about this now?",
            'fact_declaration': "Is this fact still accurate?"
        }
        
        prompt = f"🔔 Memory Review\n"
        prompt += f"\nMemory Type: {memory_type}"
        prompt += f"\nContent: {content}"
        prompt += f"\nCreated: {created_at}"
        prompt += f"\n\n{type_prompts.get(memory_type, 'Would you like to review this memory?')}"
        prompt += "\n\nOptions:"
        prompt += "\n1. Confirm - Keep as is"
        prompt += "\n2. Update - Modify the memory"
        prompt += "\n3. Archive - Move to archive"
        prompt += "\n4. Delete - Remove permanently"
        
        return prompt
    
    def record_nudge_interaction(self, memory_id: str, action: str) -> bool:
        """Record a nudge interaction.
        
        Args:
            memory_id: Memory ID
            action: User action (confirm, update, archive, delete)
            
        Returns:
            True if successful, False otherwise
        """
        interaction = {
            'memory_id': memory_id,
            'action': action,
            'timestamp': datetime.now().isoformat()
        }
        
        self.nudge_history.append(interaction)
        
        # Update memory with last reviewed timestamp
        memory = self.storage_service.get_memory(memory_id)
        if memory:
            memory['last_reviewed'] = datetime.now().isoformat()
            if action == 'confirm':
                memory['usage_count'] = memory.get('usage_count', 0) + 1
            
            return self.storage_service.update_memory(memory_id, memory)
        
        return False
    
    def get_nudge_stats(self) -> Dict[str, Any]:
        """Get statistics about nudge interactions.
        
        Returns:
            Nudge statistics
        """
        stats = {
            'total_nudges': len(self.nudge_history),
            'actions': {},
            'last_nudge': None
        }
        
        # Count actions
        for interaction in self.nudge_history:
            action = interaction.get('action')
            if action not in stats['actions']:
                stats['actions'][action] = 0
            stats['actions'][action] += 1
        
        # Get last nudge timestamp
        if self.nudge_history:
            last_interaction = sorted(self.nudge_history, key=lambda x: x.get('timestamp'), reverse=True)[0]
            stats['last_nudge'] = last_interaction.get('timestamp')
        
        return stats
    
    def should_nudge(self) -> bool:
        """Determine if a nudge should be sent based on time and conditions.
        
        Returns:
            True if a nudge should be sent, False otherwise
        """
        # Check if it's been at least 24 hours since last nudge
        if self.nudge_history:
            last_interaction = sorted(self.nudge_history, key=lambda x: x.get('timestamp'), reverse=True)[0]
            last_nudge_time = datetime.fromisoformat(last_interaction.get('timestamp'))
            time_since_last = datetime.now() - last_nudge_time
            if time_since_last < timedelta(hours=24):
                return False
        
        # Check if there are any high-priority candidates
        candidates = self.get_nudge_candidates(limit=3)
        if not candidates:
            return False
        
        # Random factor to avoid nudging every time
        return random.random() > 0.3


def generate_nudge_summary(nudges: List[Dict[str, Any]]) -> str:
    """Generate a summary of nudge candidates.
    
    Args:
        nudges: List of nudge candidates
        
    Returns:
        Formatted nudge summary
    """
    if not nudges:
        return "No memories need review at this time."
    
    summary = f"📋 Memory Review Reminder\n\n"
    summary += f"You have {len(nudges)} memories that could use a quick review:\n\n"
    
    for i, memory in enumerate(nudges, 1):
        memory_type = memory.get('memory_type', 'unknown')
        content = memory.get('content', '')
        score = memory.get('nudge_score', 0.0)
        
        summary += f"{i}. [{memory_type}] {content[:60]}{'...' if len(content) > 60 else ''}"
        summary += f" (Priority: {'High' if score > 5 else 'Medium' if score > 3 else 'Low'})\n"
    
    summary += "\nUse 'review <number>' to check details or 'skip' to dismiss."
    
    return summary
