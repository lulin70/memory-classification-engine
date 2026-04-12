"""Classification Service for Memory Classification Engine."""

import time
from typing import Dict, List, Optional, Any, Tuple

from memory_classification_engine.services.base_service import BaseService
from memory_classification_engine.coordinators.classification_pipeline import ClassificationPipeline
from memory_classification_engine.services.deduplication_service import DeduplicationService
from memory_classification_engine.utils.language import language_manager
from memory_classification_engine.utils.helpers import generate_memory_id, get_current_time
from memory_classification_engine.utils.logger import logger


class ClassificationService(BaseService):
    """Service for memory classification operations.
    
    This service handles:
    - Message classification
    - Memory type detection
    - Language detection
    - Duplicate detection
    """
    
    def __init__(self, config, plugin_manager=None):
        """Initialize classification service.
        
        Args:
            config: Configuration manager.
            plugin_manager: Optional plugin manager for extensibility.
        """
        super().__init__(config)
        self.plugin_manager = plugin_manager
        self.classification_pipeline = None
        self.deduplication_service = None
        
    def initialize(self) -> None:
        """Initialize classification resources."""
        self.classification_pipeline = ClassificationPipeline(self.config)
        self.deduplication_service = DeduplicationService(self.config)
        self._initialized = True
        self.log_info("Classification service initialized")
        
    def shutdown(self) -> None:
        """Clean up classification resources."""
        self._initialized = False
        self.log_info("Classification service shutdown")
        
    def classify_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Classify a message and return classification results.
        
        Args:
            message: The message to classify.
            context: Optional context information.
            
        Returns:
            Dictionary containing classification results.
        """
        if not self._initialized:
            raise RuntimeError("Classification service not initialized")
            
        start_time = time.time()
        
        # Comment in Chinese removed
        if not message or not message.strip():
            return {
                'message': message,
                'matches': [],
                'processing_time': time.time() - start_time,
                'language': 'unknown',
                'language_confidence': 0.0
            }
        
        # Comment in Chinese removed
        language, lang_confidence = language_manager.detect_language(message)
        
        # Comment in Chinese removed
        plugin_results = {}
        if self.plugin_manager:
            plugin_results = self.plugin_manager.process_message(message, context)
        
        # Comment in Chinese removed
        matches = self.classification_pipeline.classify_with_defaults(
            message, language, context
        )
        
        # Comment in Chinese removeds
        unique_matches = self.deduplication_service.deduplicate(matches)
        
        # Comment in Chinese removed
        enriched_matches = self._enrich_matches(
            unique_matches, context, language, lang_confidence
        )
        
        return {
            'message': message,
            'matches': enriched_matches,
            'plugin_results': plugin_results,
            'processing_time': time.time() - start_time,
            'language': language,
            'language_confidence': lang_confidence
        }
    
    def _enrich_matches(
        self,
        matches: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
        language: str,
        lang_confidence: float
    ) -> List[Dict[str, Any]]:
        """Enrich matches with additional metadata.
        
        Args:
            matches: List of classification matches.
            context: Optional context.
            language: Detected language.
            lang_confidence: Language confidence score.
            
        Returns:
            Enriched matches.
        """
        enriched = []
        
        for match in matches:
            # Comment in Chinese removed
            memory_id = generate_memory_id()
            match['id'] = memory_id
            
            # Comment in Chinese removedtion
            if context:
                match['context'] = context.get('conversation_id', '')
                conversation_history = context.get('conversation_history', [])
                if len(conversation_history) > 10:
                    match['conversation_history'] = conversation_history[-10:]
                else:
                    match['conversation_history'] = conversation_history
            
            # Comment in Chinese removedtion
            match['language'] = language
            match['language_confidence'] = lang_confidence
            
            # Comment in Chinese removedld
            if 'memory_type' in match:
                match['type'] = match['memory_type']
            if 'type' in match and 'memory_type' not in match:
                match['memory_type'] = match['type']
            
            # Comment in Chinese removedgins
            if self.plugin_manager:
                match = self.plugin_manager.process_memory(match)
            
            enriched.append(match)
        
        return enriched
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language of text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Tuple of (language_code, confidence).
        """
        return language_manager.detect_language(text)
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics.
        
        Returns:
            Dictionary with classification statistics.
        """
        return {
            'service': 'ClassificationService',
            'initialized': self._initialized,
            'pipeline_type': type(self.classification_pipeline).__name__ if self.classification_pipeline else None
        }
