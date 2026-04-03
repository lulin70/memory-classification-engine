from typing import Dict, Optional, Any
from memory_classification_engine.plugins.base import Plugin

class SentimentAnalyzerPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(name)
        self.positive_words = ["happy", "joy", "love", "excited", "great", "good", "wonderful", "excellent"]
        self.negative_words = ["sad", "angry", "hate", "disappointed", "bad", "terrible", "awful", "horrible"]
    
    def initialize(self) -> bool:
        print(f"Initializing {self.name} plugin")
        return True
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        sentiment = self._analyze_sentiment(message)
        return {
            "sentiment": sentiment,
            "score": self._calculate_score(message)
        }
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        content = memory.get("content", "")
        sentiment = self._analyze_sentiment(content)
        memory["sentiment"] = sentiment
        memory["sentiment_score"] = self._calculate_score(content)
        return memory
    
    def cleanup(self) -> bool:
        print(f"Cleaning up {self.name} plugin")
        return True
    
    def _analyze_sentiment(self, text: str) -> str:
        text_lower = text.lower()
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_score(self, text: str) -> float:
        text_lower = text.lower()
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
