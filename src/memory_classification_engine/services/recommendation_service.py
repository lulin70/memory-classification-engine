"""Recommendation Service for Memory Classification Engine."""

from typing import Dict, List, Optional, Any

from memory_classification_engine.services.base_service import BaseService
from memory_classification_engine.utils.recommendation import recommendation_system


class RecommendationService(BaseService):
    """Service for memory recommendation operations.

    This service handles:
    - Personalized recommendations
    - Similar memory finding
    - Trending memories
    """

    def __init__(self, config):
        """Initialize recommendation service.

        Args:
            config: Configuration manager.
        """
        super().__init__(config)

    def initialize(self) -> None:
        """Initialize recommendation resources."""
        self._initialized = True
        self.log_info("Recommendation service initialized")

    def shutdown(self) -> None:
        """Clean up recommendation resources."""
        self._initialized = False
        self.log_info("Recommendation service shutdown")

    def get_recommendations(
        self,
        user_id: str,
        query: Optional[str] = None,
        limit: int = 5,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user.

        Args:
            user_id: User identifier.
            query: Optional search query.
            limit: Maximum number of recommendations.
            context: Optional context information.

        Returns:
            List of recommended memories.
        """
        if not self._initialized:
            raise RuntimeError("Recommendation service not initialized")

        try:
            return recommendation_system.get_recommendations(
                user_id=user_id,
                query=query,
                limit=limit,
                context=context
            )
        except Exception as e:
            self.log_error(f"Failed to get recommendations: {e}")
            return []

    def find_similar_memories(
        self,
        memory_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find memories similar to the given memory.

        Args:
            memory_id: Reference memory identifier.
            limit: Maximum number of similar memories.

        Returns:
            List of similar memories.
        """
        if not self._initialized:
            raise RuntimeError("Recommendation service not initialized")

        try:
            return recommendation_system.find_similar(memory_id, limit=limit)
        except Exception as e:
            self.log_error(f"Failed to find similar memories: {e}")
            return []
