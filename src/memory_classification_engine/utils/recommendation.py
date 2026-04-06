import os
import json
import time
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.helpers import get_current_time
from memory_classification_engine.utils.semantic import semantic_utility

class RecommendationSystem:
    """Personalized recommendation system based on user behavior."""
    
    def __init__(self, storage_path: str = "./data/recommendations"):
        """Initialize recommendation system.
        
        Args:
            storage_path: Path to store user behavior data.
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # User behavior data file
        self.behavior_file = os.path.join(self.storage_path, "user_behavior.json")
        
        # Load existing user behavior data
        self.user_behavior = self._load_behavior_data()
        
        # Memory embedding cache
        self.embedding_cache = {}
        
        # Hyperparameters for recommendation
        self.relevance_weight = 0.4  # Weight for relevance score
        self.diversity_weight = 0.3   # Weight for diversity score
        self.novelty_weight = 0.3     # Weight for novelty score
        self.behavior_decay = 0.9     # Decay factor for past behavior
        
    def _load_behavior_data(self) -> Dict[str, Any]:
        """Load user behavior data from file.
        
        Returns:
            User behavior data as a dictionary.
        """
        try:
            if os.path.exists(self.behavior_file):
                with open(self.behavior_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading behavior data: {e}", exc_info=True)
        return {"users": {}}
    
    def _save_behavior_data(self):
        """Save user behavior data to file."""
        try:
            with open(self.behavior_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_behavior, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving behavior data: {e}", exc_info=True)
    
    def record_user_behavior(self, user_id: str, memory_id: str, action: str, context: Optional[Dict[str, Any]] = None):
        """Record user behavior for recommendation.
        
        Args:
            user_id: User ID.
            memory_id: Memory ID.
            action: Action type (view, interact, etc.).
            context: Optional context information.
        """
        if user_id not in self.user_behavior["users"]:
            self.user_behavior["users"][user_id] = {
                "interactions": [],
                "preferences": {},
                "last_updated": get_current_time()
            }
        
        user_data = self.user_behavior["users"][user_id]
        
        # Record interaction
        interaction = {
            "memory_id": memory_id,
            "action": action,
            "timestamp": get_current_time(),
            "context": context or {}
        }
        
        user_data["interactions"].append(interaction)
        
        # Limit interactions to last 1000
        if len(user_data["interactions"]) > 1000:
            user_data["interactions"] = user_data["interactions"][-1000:]
        
        # Update preference weights based on interaction
        if memory_id not in user_data["preferences"]:
            user_data["preferences"][memory_id] = 0.0
        
        # Increase preference weight based on action type
        action_weights = {
            "view": 0.1,
            "interact": 0.3,
            "like": 0.5,
            "share": 0.8
        }
        
        weight = action_weights.get(action, 0.1)
        user_data["preferences"][memory_id] += weight
        
        # Apply decay to all preferences
        for mem_id in user_data["preferences"]:
            user_data["preferences"][mem_id] *= self.behavior_decay
        
        user_data["last_updated"] = get_current_time()
        
        # Save behavior data
        self._save_behavior_data()
    
    def get_user_preferences(self, user_id: str) -> Dict[str, float]:
        """Get user preferences based on past behavior.
        
        Args:
            user_id: User ID.
            
        Returns:
            Dictionary of memory IDs to preference scores.
        """
        if user_id not in self.user_behavior["users"]:
            return {}
        
        return self.user_behavior["users"][user_id].get("preferences", {})
    
    def calculate_relevance_score(self, memory: Dict[str, Any], user_id: str, query: Optional[str] = None) -> float:
        """Calculate relevance score for a memory.
        
        Args:
            memory: Memory object.
            user_id: User ID.
            query: Optional query string.
            
        Returns:
            Relevance score between 0 and 1.
        """
        relevance_score = 0.0
        
        # 1. User preference score
        user_preferences = self.get_user_preferences(user_id)
        memory_id = memory.get("id")
        if memory_id in user_preferences:
            preference_score = user_preferences[memory_id]
            # Normalize preference score
            max_preference = max(user_preferences.values()) if user_preferences else 1.0
            relevance_score += preference_score / max_preference * 0.4
        
        # 2. Query relevance (if query provided)
        if query:
            content = memory.get("content", "")
            if content:
                query_similarity = semantic_utility.calculate_similarity(query, content)
                relevance_score += query_similarity * 0.4
        
        # 3. Memory properties
        confidence = memory.get("confidence", 1.0)
        relevance_score += confidence * 0.2
        
        # Normalize score
        return min(relevance_score, 1.0)
    
    def calculate_diversity_score(self, memory: Dict[str, Any], selected_memories: List[Dict[str, Any]]) -> float:
        """Calculate diversity score for a memory.
        
        Args:
            memory: Memory object.
            selected_memories: List of already selected memories.
            
        Returns:
            Diversity score between 0 and 1.
        """
        if not selected_memories:
            return 1.0
        
        memory_content = memory.get("content", "")
        if not memory_content:
            return 0.0
        
        # Calculate average similarity to selected memories
        similarities = []
        for selected_memory in selected_memories:
            selected_content = selected_memory.get("content", "")
            if selected_content:
                similarity = semantic_utility.calculate_similarity(memory_content, selected_content)
                similarities.append(similarity)
        
        if similarities:
            avg_similarity = sum(similarities) / len(similarities)
            # Diversity is inverse of similarity
            return 1.0 - avg_similarity
        
        return 1.0
    
    def calculate_novelty_score(self, memory: Dict[str, Any], user_id: str) -> float:
        """Calculate novelty score for a memory.
        
        Args:
            memory: Memory object.
            user_id: User ID.
            
        Returns:
            Novelty score between 0 and 1.
        """
        # 1. Time-based novelty
        created_at = memory.get("created_at", "")
        if created_at:
            try:
                from datetime import datetime, timezone
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                current_dt = datetime.now(timezone.utc)
                days_since_creation = (current_dt - created_dt).days
                
                # Exponential decay for novelty over time
                time_novelty = 2 ** (-0.05 * days_since_creation)
            except:
                time_novelty = 0.5
        else:
            time_novelty = 0.5
        
        # 2. User interaction novelty
        user_preferences = self.get_user_preferences(user_id)
        memory_id = memory.get("id")
        interaction_novelty = 1.0
        
        if memory_id in user_preferences:
            # Less novelty if user has interacted with this memory before
            interaction_novelty = 1.0 - min(user_preferences[memory_id], 1.0)
        
        # Combine novelty scores
        return (time_novelty * 0.6 + interaction_novelty * 0.4)
    
    def generate_recommendations(self, user_id: str, query: Optional[str] = None, limit: int = 5, all_memories: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate personalized recommendations for a user.
        
        Args:
            user_id: User ID.
            query: Optional query string.
            limit: Maximum number of recommendations to return.
            all_memories: List of all available memories.
            
        Returns:
            List of recommended memories sorted by recommendation score.
        """
        if not all_memories:
            return []
        
        # Calculate scores for all memories
        scored_memories = []
        for memory in all_memories:
            # Calculate relevance score
            relevance_score = self.calculate_relevance_score(memory, user_id, query)
            
            # Calculate novelty score
            novelty_score = self.calculate_novelty_score(memory, user_id)
            
            # Store scores
            memory_copy = memory.copy()
            memory_copy["relevance_score"] = relevance_score
            memory_copy["novelty_score"] = novelty_score
            
            scored_memories.append(memory_copy)
        
        # Apply diversity-aware selection
        selected_memories = []
        remaining_memories = scored_memories.copy()
        
        while remaining_memories and len(selected_memories) < limit:
            # Calculate combined scores with diversity consideration
            for memory in remaining_memories:
                diversity_score = self.calculate_diversity_score(memory, selected_memories)
                memory["diversity_score"] = diversity_score
                
                # Calculate final score
                memory["recommendation_score"] = (
                    memory["relevance_score"] * self.relevance_weight +
                    memory["diversity_score"] * self.diversity_weight +
                    memory["novelty_score"] * self.novelty_weight
                )
            
            # Sort by recommendation score
            remaining_memories.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
            
            # Select top memory
            if remaining_memories:
                selected_memory = remaining_memories.pop(0)
                selected_memories.append(selected_memory)
        
        # Sort final recommendations by recommendation score
        selected_memories.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
        
        return selected_memories
    
    def get_user_behavior_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user behavior summary.
        
        Args:
            user_id: User ID.
            
        Returns:
            User behavior summary.
        """
        if user_id not in self.user_behavior["users"]:
            return {
                "user_id": user_id,
                "total_interactions": 0,
                "preferred_memory_types": {},
                "last_activity": None
            }
        
        user_data = self.user_behavior["users"][user_id]
        interactions = user_data.get("interactions", [])
        
        # Analyze preferred memory types
        type_counts = {}
        for interaction in interactions:
            # We would need memory type information here
            # For now, just return basic stats
            pass
        
        return {
            "user_id": user_id,
            "total_interactions": len(interactions),
            "preferred_memory_types": type_counts,
            "last_activity": user_data.get("last_updated")
        }

# Global recommendation system instance
recommendation_system = RecommendationSystem()
