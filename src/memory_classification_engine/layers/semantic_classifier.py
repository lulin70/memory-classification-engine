"""Semantic classifier for Layer 3."""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from memory_classification_engine.utils.logger import logger

# Try to import AI/ML dependencies
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using fallback semantic analysis")


class SemanticClassifier:
    """Layer 3 semantic classifier for deep understanding of memories."""
    
    # Memory type definitions with semantic understanding
    MEMORY_TYPES = {
        'user_preference': {
            'description': 'User preferences and likes/dislikes',
            'keywords': ['喜欢', 'prefer', 'love', 'hate', '讨厌', '想要', 'want'],
            'confidence_threshold': 0.7
        },
        'correction': {
            'description': 'Corrections to previous information',
            'keywords': ['纠正', 'correction', '错了', 'wrong', '不对', 'incorrect'],
            'confidence_threshold': 0.8
        },
        'fact_declaration': {
            'description': 'Factual statements and declarations',
            'keywords': ['是', 'is', 'are', '有', 'have', '位于', 'located'],
            'confidence_threshold': 0.6
        },
        'decision': {
            'description': 'Decisions and choices made',
            'keywords': ['决定', 'decide', '选择', 'choose', '确定', 'confirm'],
            'confidence_threshold': 0.75
        },
        'relationship': {
            'description': 'Relationship information',
            'keywords': ['负责', 'responsible', '管理', 'manage', '属于', 'belong'],
            'confidence_threshold': 0.7
        },
        'task_pattern': {
            'description': 'Task and workflow patterns',
            'keywords': ['任务', 'task', '工作', 'work', '流程', 'process'],
            'confidence_threshold': 0.65
        },
        'sentiment_marker': {
            'description': 'Emotional and sentiment markers',
            'keywords': ['开心', 'happy', '难过', 'sad', '兴奋', 'excited'],
            'confidence_threshold': 0.6
        }
    }
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', use_local_model: bool = True):
        """Initialize the semantic classifier.
        
        Args:
            model_name: Name of the sentence transformer model to use.
            use_local_model: Whether to use local model or API-based analysis.
        """
        self.model_name = model_name
        self.use_local_model = use_local_model
        self.model = None
        
        # Initialize embedding model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE and use_local_model:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Loaded sentence transformer model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load model {model_name}: {e}")
                self.use_local_model = False
        
        # Semantic context storage
        self.semantic_context = {}
        
        logger.info("SemanticClassifier initialized")
    
    def classify(self, message: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Classify a message using semantic understanding.
        
        Args:
            message: The message to classify.
            context: Optional context information.
            
        Returns:
            A list of classification results with confidence scores.
        """
        results = []
        
        # 1. Keyword-based classification (fast fallback)
        keyword_results = self._keyword_classification(message)
        results.extend(keyword_results)
        
        # 2. Semantic embedding analysis (if available)
        if self.model is not None:
            semantic_results = self._semantic_classification(message)
            results.extend(semantic_results)
        
        # 3. Context-aware analysis
        if context:
            context_results = self._context_analysis(message, context)
            results.extend(context_results)
        
        # 4. Intent analysis
        intent_results = self._intent_analysis(message)
        results.extend(intent_results)
        
        # Deduplicate and sort by confidence
        results = self._deduplicate_and_sort(results)
        
        return results
    
    def _keyword_classification(self, message: str) -> List[Dict[str, Any]]:
        """Classify based on keywords.
        
        Args:
            message: The message to classify.
            
        Returns:
            A list of classification results.
        """
        results = []
        message_lower = message.lower()
        
        for memory_type, config in self.MEMORY_TYPES.items():
            # Check for keywords
            matched_keywords = []
            for keyword in config['keywords']:
                if keyword.lower() in message_lower:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # Calculate confidence based on keyword matches
                confidence = min(0.6 + len(matched_keywords) * 0.1, 0.85)
                
                if confidence >= config['confidence_threshold']:
                    results.append({
                        'memory_type': memory_type,
                        'confidence': confidence,
                        'source': 'semantic:keyword',
                        'description': config['description'],
                        'matched_keywords': matched_keywords,
                        'tier': self._get_tier_for_type(memory_type)
                    })
        
        return results
    
    def _semantic_classification(self, message: str) -> List[Dict[str, Any]]:
        """Classify using semantic embeddings.
        
        Args:
            message: The message to classify.
            
        Returns:
            A list of classification results.
        """
        results = []
        
        try:
            # Encode the message
            message_embedding = self.model.encode(message)
            
            # Compare with type descriptions
            for memory_type, config in self.MEMORY_TYPES.items():
                # Encode description
                description_embedding = self.model.encode(config['description'])
                
                # Calculate similarity
                similarity = self._cosine_similarity(message_embedding, description_embedding)
                
                if similarity >= config['confidence_threshold']:
                    results.append({
                        'memory_type': memory_type,
                        'confidence': float(similarity),
                        'source': 'semantic:embedding',
                        'description': config['description'],
                        'tier': self._get_tier_for_type(memory_type)
                    })
        
        except Exception as e:
            logger.error(f"Error in semantic classification: {e}")
        
        return results
    
    def _context_analysis(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze message in context.
        
        Args:
            message: The message to analyze.
            context: Context information.
            
        Returns:
            A list of classification results.
        """
        results = []
        
        # Check for conversation continuity
        conversation_history = context.get('conversation_history', [])
        if conversation_history:
            last_message = conversation_history[-1] if conversation_history else None
            if last_message:
                # Check if current message is a response or continuation
                if self._is_continuation(message, last_message):
                    results.append({
                        'memory_type': 'conversation_context',
                        'confidence': 0.7,
                        'source': 'semantic:context',
                        'description': 'Conversation continuation',
                        'tier': 3
                    })
        
        # Check for user preferences in context
        user_preferences = context.get('user_preferences', {})
        if user_preferences:
            # Check if message relates to known preferences
            for pref_type, pref_value in user_preferences.items():
                if pref_type.lower() in message.lower() or pref_value.lower() in message.lower():
                    results.append({
                        'memory_type': 'user_preference',
                        'confidence': 0.75,
                        'source': 'semantic:context_preference',
                        'description': f'Related to user preference: {pref_type}',
                        'tier': 2
                    })
        
        return results
    
    def _intent_analysis(self, message: str) -> List[Dict[str, Any]]:
        """Analyze the intent of the message.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A list of intent analysis results.
        """
        results = []
        
        # Define intent patterns
        intents = {
            'question': {
                'patterns': ['?', '什么', 'what', '怎么', 'how', '为什么', 'why', '哪里', 'where'],
                'memory_type': 'information_request'
            },
            'command': {
                'patterns': ['请', 'please', '帮我', 'help me', '需要', 'need', '做', 'do'],
                'memory_type': 'task_pattern'
            },
            'statement': {
                'patterns': ['是', 'is', '有', 'have', '我觉得', 'i think', '我认为', 'i believe'],
                'memory_type': 'fact_declaration'
            },
            'feedback': {
                'patterns': ['好的', 'ok', '不错', 'good', '谢谢', 'thanks', '很好', 'great'],
                'memory_type': 'sentiment_marker'
            }
        }
        
        message_lower = message.lower()
        
        for intent_name, intent_config in intents.items():
            for pattern in intent_config['patterns']:
                if pattern.lower() in message_lower:
                    results.append({
                        'memory_type': intent_config['memory_type'],
                        'confidence': 0.6,
                        'source': f'semantic:intent:{intent_name}',
                        'description': f'Detected intent: {intent_name}',
                        'tier': 3,
                        'intent': intent_name
                    })
                    break  # Only add once per intent
        
        return results
    
    def _is_continuation(self, current: str, previous: str) -> bool:
        """Check if current message is a continuation of previous.
        
        Args:
            current: Current message.
            previous: Previous message.
            
        Returns:
            True if continuation, False otherwise.
        """
        # Simple heuristic: check for pronouns or short responses
        continuation_markers = ['它', '这个', 'that', 'it', 'this', '是的', 'yes', '对', 'right']
        
        current_lower = current.lower()
        for marker in continuation_markers:
            if marker.lower() in current_lower:
                return True
        
        # Check if current message is short (likely a response)
        if len(current) < 20:
            return True
        
        return False
    
    def _cosine_similarity(self, a, b) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector.
            b: Second vector.
            
        Returns:
            Cosine similarity score.
        """
        import numpy as np
        
        a = np.array(a)
        b = np.array(b)
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _get_tier_for_type(self, memory_type: str) -> int:
        """Get storage tier for a memory type.
        
        Args:
            memory_type: The type of memory.
            
        Returns:
            The tier number (1-4).
        """
        tier_mapping = {
            'user_preference': 2,
            'correction': 2,
            'fact_declaration': 4,
            'decision': 3,
            'relationship': 4,
            'task_pattern': 3,
            'sentiment_marker': 3,
            'information_request': 3,
            'conversation_context': 3
        }
        
        return tier_mapping.get(memory_type, 3)
    
    def _deduplicate_and_sort(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate results and sort by confidence.
        
        Args:
            results: List of classification results.
            
        Returns:
            Deduplicated and sorted results.
        """
        # Deduplicate by memory_type, keeping highest confidence
        seen_types = {}
        for result in results:
            memory_type = result['memory_type']
            if memory_type not in seen_types or result['confidence'] > seen_types[memory_type]['confidence']:
                seen_types[memory_type] = result
        
        # Sort by confidence (descending)
        sorted_results = sorted(seen_types.values(), key=lambda x: x['confidence'], reverse=True)
        
        return sorted_results
    
    def extract_entities(self, message: str) -> List[Dict[str, Any]]:
        """Extract named entities from message.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A list of extracted entities.
        """
        entities = []
        
        # Simple entity extraction based on patterns
        # In a full implementation, this would use NER (Named Entity Recognition)
        
        # Extract potential names (capitalized words in English)
        import re
        
        # English names (capitalized words that are not common words)
        name_pattern = r'\b[A-Z][a-z]+\b'
        potential_names = re.findall(name_pattern, message)
        
        # Common words to exclude from person names
        common_words = {'The', 'And', 'But', 'For', 'Are', 'Use', 'Works', 'Uses', 'At'}
        
        for name in potential_names:
            if len(name) > 2 and name not in common_words:  # Filter out short words and common words
                entities.append({
                    'text': name,
                    'type': 'person',
                    'confidence': 0.6
                })
        
        # Extract potential organizations (all caps or capitalized words after "at", "in", "from")
        # First, try to find organizations mentioned with prepositions
        org_pattern_with_prep = r'\b(at|in|from|for)\s+([A-Z][a-zA-Z]+)\b'
        org_matches = re.findall(org_pattern_with_prep, message, re.IGNORECASE)
        
        for prep, org in org_matches:
            if len(org) > 2:
                entities.append({
                    'text': org,
                    'type': 'organization',
                    'confidence': 0.7
                })
        
        # Also extract all caps as organizations
        org_pattern_caps = r'\b[A-Z]{2,}\b'
        potential_orgs = re.findall(org_pattern_caps, message)
        
        for org in potential_orgs:
            # Check if not already added
            if not any(e['text'] == org for e in entities):
                entities.append({
                    'text': org,
                    'type': 'organization',
                    'confidence': 0.5
                })
        
        return entities
    
    def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze sentiment of a message.
        
        Args:
            message: The message to analyze.
            
        Returns:
            Sentiment analysis result.
        """
        # Simple sentiment analysis based on keywords
        positive_words = ['good', 'great', 'excellent', 'happy', 'love', '喜欢', '好', '棒', '开心']
        negative_words = ['bad', 'terrible', 'hate', 'sad', '讨厌', '差', '糟', '难过', '失望']
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
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
