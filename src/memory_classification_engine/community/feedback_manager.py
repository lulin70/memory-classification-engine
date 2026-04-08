"""Community feedback management system."""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from memory_classification_engine.utils.logger import logger


class FeedbackManager:
    """Manager for handling community feedback."""
    
    def __init__(self, feedback_dir: str = "./data/feedback"):
        """Initialize the feedback manager.
        
        Args:
            feedback_dir: Directory to store feedback data.
        """
        self.feedback_dir = feedback_dir
        os.makedirs(self.feedback_dir, exist_ok=True)
        self.feedback_file = os.path.join(self.feedback_dir, "feedback.json")
        self.feedback = self._load_feedback()
    
    def _load_feedback(self) -> List[Dict[str, Any]]:
        """Load feedback from file."""
        if not os.path.exists(self.feedback_file):
            return []
        
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading feedback: {e}")
            return []
    
    def _save_feedback(self):
        """Save feedback to file."""
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
    
    def submit_feedback(self, user_id: str, feedback_type: str, content: str, 
                      severity: str = "medium", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Submit feedback.
        
        Args:
            user_id: User ID.
            feedback_type: Type of feedback (bug, feature, suggestion, question).
            content: Feedback content.
            severity: Severity level (low, medium, high, critical).
            metadata: Additional metadata.
            
        Returns:
            Feedback submission result.
        """
        feedback_id = f"feedback_{int(time.time())}_{user_id}"
        feedback = {
            "id": feedback_id,
            "user_id": user_id,
            "feedback_type": feedback_type,
            "content": content,
            "severity": severity,
            "metadata": metadata or {},
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "replies": []
        }
        
        self.feedback.append(feedback)
        self._save_feedback()
        
        logger.info(f"Feedback submitted: {feedback_id} by {user_id}")
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Feedback submitted successfully"
        }
    
    def get_feedback(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback by ID.
        
        Args:
            feedback_id: Feedback ID.
            
        Returns:
            Feedback data or None if not found.
        """
        for feedback in self.feedback:
            if feedback["id"] == feedback_id:
                return feedback
        return None
    
    def list_feedback(self, status: str = None, feedback_type: str = None, 
                     user_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List feedback with filters.
        
        Args:
            status: Filter by status (open, in_progress, resolved, closed).
            feedback_type: Filter by feedback type.
            user_id: Filter by user ID.
            limit: Maximum number of results.
            
        Returns:
            List of feedback.
        """
        filtered_feedback = self.feedback
        
        if status:
            filtered_feedback = [f for f in filtered_feedback if f.get("status") == status]
        
        if feedback_type:
            filtered_feedback = [f for f in filtered_feedback if f.get("feedback_type") == feedback_type]
        
        if user_id:
            filtered_feedback = [f for f in filtered_feedback if f.get("user_id") == user_id]
        
        # Sort by created_at descending
        filtered_feedback.sort(key=lambda x: x.get("created_at"), reverse=True)
        
        return filtered_feedback[:limit]
    
    def update_feedback_status(self, feedback_id: str, status: str, 
                             user_id: str, comment: str = None) -> Dict[str, Any]:
        """Update feedback status.
        
        Args:
            feedback_id: Feedback ID.
            status: New status (open, in_progress, resolved, closed).
            user_id: User ID making the update.
            comment: Optional comment.
            
        Returns:
            Update result.
        """
        feedback = self.get_feedback(feedback_id)
        if not feedback:
            return {"error": "Feedback not found"}
        
        feedback["status"] = status
        feedback["updated_at"] = datetime.now().isoformat()
        
        if comment:
            feedback["replies"].append({
                "user_id": user_id,
                "content": comment,
                "timestamp": datetime.now().isoformat(),
                "type": "status_update"
            })
        
        self._save_feedback()
        
        logger.info(f"Feedback {feedback_id} status updated to {status} by {user_id}")
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "status": status
        }
    
    def reply_to_feedback(self, feedback_id: str, user_id: str, content: str) -> Dict[str, Any]:
        """Reply to feedback.
        
        Args:
            feedback_id: Feedback ID.
            user_id: User ID making the reply.
            content: Reply content.
            
        Returns:
            Reply result.
        """
        feedback = self.get_feedback(feedback_id)
        if not feedback:
            return {"error": "Feedback not found"}
        
        feedback["replies"].append({
            "user_id": user_id,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "type": "reply"
        })
        feedback["updated_at"] = datetime.now().isoformat()
        
        self._save_feedback()
        
        logger.info(f"Reply added to feedback {feedback_id} by {user_id}")
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Reply added successfully"
        }
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics.
        
        Returns:
            Feedback statistics.
        """
        total = len(self.feedback)
        status_counts = {}
        type_counts = {}
        
        for feedback in self.feedback:
            status = feedback.get("status", "open")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            feedback_type = feedback.get("feedback_type", "other")
            type_counts[feedback_type] = type_counts.get(feedback_type, 0) + 1
        
        return {
            "total": total,
            "status_counts": status_counts,
            "type_counts": type_counts
        }
    
    def export_feedback(self, filename: str) -> Dict[str, Any]:
        """Export feedback to file.
        
        Args:
            filename: Export filename.
            
        Returns:
            Export result.
        """
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "total_feedback": len(self.feedback),
                "feedback": self.feedback
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Feedback exported to {filename}")
            
            return {
                "success": True,
                "filename": filename,
                "total_feedback": len(self.feedback)
            }
        except Exception as e:
            logger.error(f"Error exporting feedback: {e}")
            return {"error": str(e)}


# Global feedback manager instance
feedback_manager = FeedbackManager()