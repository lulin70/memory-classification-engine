"""Sentiment analyzer plugin."""

from typing import Dict, List, Optional, Any
from memory_classification_engine.plugins.base_plugin import BasePlugin


class SentimentAnalyzerPlugin(BasePlugin):
    """Sentiment analyzer plugin."""
    
    def __init__(self):
        """Initialize the sentiment analyzer plugin."""
        super().__init__("sentiment_analyzer", "1.0.0")
        self.positive_words = ['good', 'great', 'excellent', 'happy', 'love', '喜欢', '好', '棒', '开心']
        self.negative_words = ['bad', 'terrible', 'hate', 'sad', '讨厌', '差', '糟', '难过', '失望']
    
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the plugin.
        
        Args:
            config: Plugin configuration.
            
        Returns:
            True if initialization was successful, False otherwise.
        """
        if config:
            self.positive_words.extend(config.get('positive_words', []))
            self.negative_words.extend(config.get('negative_words', []))
        return True
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a message.
        
        Args:
            message: The message to process.
            context: Optional context information.
            
        Returns:
            Sentiment analysis result.
        """
        sentiment = self._analyze_sentiment(message)
        return {
            'sentiment': sentiment['sentiment'],
            'confidence': sentiment['confidence'],
            'positive_indicators': sentiment['positive_indicators'],
            'negative_indicators': sentiment['negative_indicators']
        }
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Process a memory.
        
        Args:
            memory: The memory to process.
            
        Returns:
            Memory with sentiment analysis.
        """
        if 'content' in memory:
            sentiment = self._analyze_sentiment(memory['content'])
            memory['sentiment'] = sentiment
        return memory
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Sentiment analysis result.
        """
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.5 + positive_count * 0.1, 0.9)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.5 + negative_count * 0.1, 0.9)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count
        }
