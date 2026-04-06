"""Classification pipeline for coordinating classification layers."""

from typing import Dict, List, Optional, Any
from memory_classification_engine.layers.rule_matcher import RuleMatcher
from memory_classification_engine.layers.pattern_analyzer import PatternAnalyzer
from memory_classification_engine.layers.semantic_classifier import SemanticClassifier
from memory_classification_engine.utils.logger import logger


class ClassificationPipeline:
    """Coordinates the classification layers in order."""
    
    def __init__(self, config: Any):
        """Initialize classification pipeline.
        
        Args:
            config: Configuration manager instance.
        """
        self.config = config
        
        # Initialize layers
        rules = config.get_rules().get('rules', [])
        self.rule_matcher = RuleMatcher(rules)
        self.pattern_analyzer = PatternAnalyzer()
        
        llm_enabled = config.get('llm.enabled', False)
        api_key = config.get('llm.api_key', '')
        self.semantic_classifier = SemanticClassifier(llm_enabled, api_key)
    
    def classify(self, message: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Classify a message through the pipeline.
        
        Args:
            message: The message to classify.
            context: Optional context for the message.
            
        Returns:
            List of classification matches.
        """
        # Layer 1: Rule matching (fastest, execute first)
        rule_matches = self.rule_matcher.match(message, context)
        
        if rule_matches:
            logger.debug(f"Rule matching found {len(rule_matches)} matches")
            return rule_matches
        
        # Layer 2: Pattern analysis (second fastest)
        pattern_matches = self.pattern_analyzer.analyze(message, context)
        
        if pattern_matches:
            logger.debug(f"Pattern analysis found {len(pattern_matches)} matches")
            return pattern_matches
        
        # Layer 3: Semantic classification (slowest, execute last)
        semantic_matches = self.semantic_classifier.classify(message, context)
        
        if semantic_matches:
            logger.debug(f"Semantic classification found {len(semantic_matches)} matches")
            return semantic_matches
        
        logger.debug("No classification matches found")
        return []
    
    def classify_with_defaults(self, message: str, language: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Classify a message with default fallback.
        
        Args:
            message: The message to classify.
            language: The detected language code.
            context: Optional context for the message.
            
        Returns:
            List of classification matches, with default if no matches found.
        """
        matches = self.classify(message, context)
        
        if not matches:
            # Use default classifier
            default_match = self._get_default_classification(message, language)
            if default_match:
                matches = [default_match]
        
        return matches
    
    def _get_default_classification(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Get default classification for a message when no other matches are found.
        
        Args:
            message: The message to classify.
            language: The detected language code.
            
        Returns:
            A default classification match if found, None otherwise.
        """
        from memory_classification_engine.utils.language import language_manager
        
        message_lower = message.lower()
        
        # Get language-specific keywords from LanguageManager
        preference_keywords = language_manager.get_keywords('user_preference', language)
        correction_keywords = language_manager.get_keywords('correction', language)
        fact_keywords = language_manager.get_keywords('fact_declaration', language)
        decision_keywords = language_manager.get_keywords('decision', language)
        relationship_keywords = language_manager.get_keywords('relationship', language)
        task_keywords = language_manager.get_keywords('task_pattern', language)
        sentiment_keywords = language_manager.get_keywords('sentiment_marker', language)
        
        # Check for user preferences
        if any(keyword in message_lower for keyword in preference_keywords):
            return {
                'memory_type': 'user_preference',
                'tier': 2,
                'content': message,
                'confidence': 0.9,
                'source': 'default:preference',
                'description': 'User preference detected',
                'language': language
            }
        # Check for corrections
        elif any(keyword in message_lower for keyword in correction_keywords):
            return {
                'memory_type': 'correction',
                'tier': 3,
                'content': message,
                'confidence': 0.8,
                'source': 'default:correction',
                'description': 'Correction detected',
                'language': language
            }
        # Check for fact declarations
        elif any(keyword in message_lower for keyword in fact_keywords):
            return {
                'memory_type': 'fact_declaration',
                'tier': 3,
                'content': message,
                'confidence': 0.7,
                'source': 'default:fact',
                'description': 'Fact declaration detected',
                'language': language
            }
        # Check for decisions
        elif any(keyword in message_lower for keyword in decision_keywords):
            return {
                'memory_type': 'decision',
                'tier': 2,
                'content': message,
                'confidence': 0.8,
                'source': 'default:decision',
                'description': 'Decision detected',
                'language': language
            }
        # Check for relationships
        elif any(keyword in message_lower for keyword in relationship_keywords):
            return {
                'memory_type': 'relationship',
                'tier': 3,
                'content': message,
                'confidence': 0.7,
                'source': 'default:relationship',
                'description': 'Relationship information detected',
                'language': language
            }
        # Check for task patterns
        elif any(keyword in message_lower for keyword in task_keywords):
            return {
                'memory_type': 'task_pattern',
                'tier': 2,
                'content': message,
                'confidence': 0.8,
                'source': 'default:task',
                'description': 'Task pattern detected',
                'language': language
            }
        # Check for sentiment markers
        elif any(keyword in message_lower for keyword in sentiment_keywords):
            return {
                'memory_type': 'sentiment_marker',
                'tier': 3,
                'content': message,
                'confidence': 0.7,
                'source': 'default:sentiment',
                'description': 'Sentiment detected',
                'language': language
            }
        else:
            # Default to general fact declaration
            return {
                'memory_type': 'fact_declaration',
                'tier': 3,
                'content': message,
                'confidence': 0.5,
                'source': 'default:general',
                'description': 'General fact declaration',
                'language': language
            }
