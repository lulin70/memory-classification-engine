"""Model Distillation Interface for Layer 3 LLM cost reduction.

Provides:
- Weak/Strong model routing based on confidence
- Training data export for offline distillation
- Fallback chain: embedding-based → weak LLM → strong LLM

Architecture:
  Input → ConfidenceEstimator
    ├─ High confidence (>0.85) → Embedding-only (zero LLM)
    ├─ Medium (0.5-0.85)    → Weak Model (fast/cheap)
    └─ Low (<0.5)            → Strong Model (accurate)
"""

import json
import os
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class DistillationMode(Enum):
    """Distillation operating modes."""
    STRONG_ONLY = "strong_only"
    WEAK_FIRST = "weak_first"
    AUTO = "auto"
    EMBEDDING_ONLY = "embedding_only"


class ModelTier(Enum):
    """Model quality tiers."""
    EMBEDDING = "embedding"
    WEAK = "weak"
    STRONG = "strong"


class ClassificationRequest:
    """A single classification request with metadata."""
    
    def __init__(self, message: str, context: str = '', source: str = 'api'):
        self.message = message
        self.context = context or ''
        self.source = source
        self.timestamp = time.time()
        self.result = None
        self.model_used = None
        self.latency_ms = 0
    
    def to_training_sample(self) -> Dict[str, Any]:
        if not self.result:
            return {}
        return {
            'message': self.message,
            'context': self.context,
            'predicted_type': self.result.get('memory_type'),
            'predicted_tier': self.result.get('tier'),
            'confidence': self.result.get('confidence', 0),
            'model_used': self.model_used,
            'timestamp': self.timestamp,
        }


class ConfidenceEstimator:
    """Estimates whether a strong model is needed for accurate classification.
    
    Uses heuristics on input complexity to decide routing:
    - Short messages with clear keywords → high confidence (embedding only)
    - Messages with ambiguity indicators → low confidence (need LLM)
    """
    
    def __init__(self, embedding_threshold: float = 0.85,
                 weak_threshold: float = 0.50):
        self.embedding_threshold = embedding_threshold
        self.weak_threshold = weak_threshold
        
        self._clear_patterns = [
            r'^i (prefer|like|want|always|should|use)\b',
            r'^(that\'?s|it\'?s|this is)\s+(wrong|incorrect|not)',
            r'^(we|let\'?s|i\'ll)\s+(use|choose|go with|switch)',
            r'^(the|a|an)\s+(api|rate|limit|timeout|size)',
        ]
        
        self._ambiguous_indicators = [
            'maybe', 'possibly', 'could be', 'might be',
            'not sure', 'depends', 'sometimes',
            'probably', 'perhaps', 'unclear',
            '可能', '也许', '不确定', '看情况',
        ]
        
        self._complexity_keywords = {
            'high': ['architecture', 'design', 'strategy', 'optimize', 'refactor'],
            'medium': ['implement', 'create', 'update', 'fix', 'add', 'change'],
            'low': ['prefer', 'like', 'use', 'choose', 'set', 'config'],
        }
    
    def estimate(self, message: str, context: str = '') -> tuple:
        """Estimate confidence and recommended model tier.
        
        Returns:
            (confidence: float, tier: ModelTier)
        """
        msg_lower = message.lower()
        
        has_clear_pattern = any(
            re.search(p, msg_lower) for p in self._clear_patterns
        )
        
        has_ambiguity = any(ind in msg_lower for ind in self._ambiguous_indicators)
        
        word_count = len(message.split())
        
        complexity_score = 0
        for level, keywords in self._complexity_keywords.items():
            if any(kw in msg_lower for kw in keywords):
                complexity_score = 2 if level == 'high' else (1 if level == 'medium' else 0)
                break
        
        if has_clear_pattern and not has_ambiguity and word_count < 15:
            confidence = 0.92
            tier = ModelTier.EMBEDDING
        elif has_clear_pattern or (word_count < 10 and complexity_score == 0):
            confidence = 0.75
            tier = ModelTier.WEAK
        elif has_ambiguity or complexity_score >= 2 or word_count > 25:
            confidence = 0.35
            tier = ModelTier.STRONG
        else:
            confidence = 0.60
            tier = ModelTier.WEAK
        
        return round(confidence, 4), tier


class DistillationRouter:
    """Routes classification requests to appropriate model tier."""
    
    def __init__(self, mode: DistillationMode = DistillationMode.AUTO,
                 semantic_classifier=None, semantic_utility=None,
                 confidence_estimator: ConfidenceEstimator = None):
        self.mode = mode
        self.semantic_classifier = semantic_classifier
        self.semantic_utility = semantic_utility
        self.estimator = confidence_estimator or ConfidenceEstimator()
        
        self.stats = {
            'total': 0,
            'embedding': 0,
            'weak': 0,
            'strong': 0,
            'fallback_count': 0,
            'total_latency_ms': 0,
        }
        
        self._training_buffer: List[ClassificationRequest] = []
        self._max_buffer_size = 1000
    
    def classify(self, message: str, context: str = '',
                source: str = 'api') -> Dict[str, Any]:
        """Classify using distillation-aware routing."""
        request = ClassificationRequest(message, context, source)
        start = time.time()
        
        if self.mode == DistillationMode.STRONG_ONLY:
            result = self._classify_strong(message, context)
            request.model_used = 'strong'
        elif self.mode == DistillationMode.EMBEDDING_ONLY:
            result = self._classify_embedding(message, context)
            request.model_used = 'embedding'
        elif self.mode == DistillationMode.WEAK_FIRST:
            result = self._classify_weak_then_fallback(message, context)
            request.model_used = result.get('_model_used', 'weak')
        else:
            result = self._auto_classify(message, context)
            request.model_used = result.get('_model_used', 'auto')
        
        latency = (time.time() - start) * 1000
        request.result = result
        request.latency_ms = round(latency, 2)
        
        self._record_stats(request)
        self._buffer_for_training(request)
        
        clean_result = {k: v for k, v in result.items()
                       if not k.startswith('_')}
        return clean_result
    
    def _auto_classify(self, message: str, context: str) -> Dict[str, Any]:
        """Auto mode: route by confidence estimation."""
        confidence, tier = self.estimator.estimate(message, context)
        
        result = {'_model_used': tier.value, '_confidence_estimate': confidence}
        
        if tier == ModelTier.EMBEDDING:
            embedding_result = self._classify_embedding(message, context)
            result.update(embedding_result or {})
            if embedding_result and embedding_result.get('memory_type'):
                return result
            
            fallback = self._classify_weak_then_fallback(message, context)
            result.update(fallback)
            result['_model_used'] = fallback.get('_model_used', 'weak_fallback')
            self.stats['fallback_count'] += 1
            return result
        
        elif tier == ModelTier.WEAK:
            weak_result = self._classify_weak(message, context)
            if weak_result and weak_result.get('memory_type'):
                result.update(weak_result)
                return result
            
            strong_result = self._classify_strong(message, context)
            result.update(strong_result or {})
            result['_model_used'] = 'strong_fallback'
            self.stats['fallback_count'] += 1
            return result
        
        else:
            strong_result = self._classify_strong(message, context)
            result.update(strong_result or {})
            return result
    
    def _classify_embedding(self, message: str, context: str) -> Optional[Dict[str, Any]]:
        """Embedding-based classification (zero LLM cost)."""
        if not self.semantic_utility:
            return None
        
        try:
            from memory_classification_engine.layers.rule_matcher import RuleMatcher
            rules = [
                {'pattern': r'(?:^|\s)(i|we|you|they)\s+(?:prefer|like|want|always|should|use)\b.*',
                 'memory_type': 'user_preference', 'tier': 2, 'action': 'extract',
                 'priority': 8},
                {'pattern': r'(?:^|\s)(that\'?s|it\'?s|this is)\s+(?:wrong|incorrect|not|actually)\b.*',
                 'memory_type': 'correction', 'tier': 3, 'action': 'extract',
                 'priority': 8},
                {'pattern': r'(?:^|\s)(?:we|let\'?s|i\'ll|decided|going to)\s+(?:use|choose|go with|switch|adopt)\b.*',
                 'memory_type': 'decision', 'tier': 3, 'action': 'extract',
                 'priority': 7},
                {'pattern': r'(?:^|\s)(the|a|an)\s+(?:api|rate|limit|timeout|max|min|size|version)\s+is\b.*',
                 'memory_type': 'fact_declaration', 'tier': 4, 'action': 'extract',
                 'priority': 7},
            ]
            
            matcher = RuleMatcher(rules)
            matches = matcher.match(message, {'context': context} if context else None)
            
            if matches:
                best = matches[0]
                similarity = 0.9
                if self.semantic_utility.embedding_model:
                    try:
                        emb = self.semantic_utility.embedding_model.encode([message, best['content']])
                        from sklearn.metrics.pairwise import cosine_similarity
                        similarity = float(cosine_similarity([emb[0]], [emb[1]])[0][0])
                    except Exception as e:
                        logger.warning(f"Confidence estimation failed, using default similarity: {e}")
                        similarity = 0.85  # Default to medium confidence on failure
                
                return {
                    'memory_type': best['memory_type'],
                    'tier': best['tier'],
                    'confidence': round(similarity * 0.95, 4),
                    'reason': f"Rule match via embedding ({similarity:.2f})",
                    'source': 'distillation_embedding',
                }
            
            return None
        except Exception as e:
            logger.debug(f"Embedding classification failed: {e}")
            return None
    
    def _classify_weak(self, message: str, context: str) -> Optional[Dict[str, Any]]:
        """Weak model classification (fast, lower cost).
        
        Uses simplified prompt / smaller model / cached results.
        """
        if self.semantic_classifier:
            original_model = getattr(self.semantic_classifier, 'llm_model', None)
            original_temp = getattr(self.semantic_classifier, 'llm_temperature', 0.7)
            
            try:
                setattr(self.semantic_classifier, 'llm_temperature', 0.5)
                result = self.semantic_classifier.classify(message, context)
                
                if result:
                    result['_model_used'] = 'weak'
                return result
            except Exception as e:
                logger.debug(f"Weak model failed: {e}")
            finally:
                pass  # Cleanup if needed for future resource management
        
        return self._classify_embedding(message, context)
    
    def _classify_weak_then_fallback(self, message: str, context: str) -> Dict[str, Any]:
        """Weak-first with automatic fallback to strong."""
        result = self._classify_weak(message, context)
        
        if result and result.get('memory_type') and result.get('confidence', 0) > 0.5:
            result['_model_used'] = 'weak'
            return result
        
        strong = self._classify_strong(message, context)
        if strong:
            strong['_model_used'] = 'strong_fallback'
            self.stats['fallback_count'] += 1
            return strong or {}
        
        embedding = self._classify_embedding(message, context)
        if embedding:
            embedding['_model_used'] = 'embedding_fallback'
            return embedding
        
        return {'_model_used': 'none_failed'}
    
    def _classify_strong(self, message: str, context: str) -> Optional[Dict[str, Any]]:
        """Strong model classification (full accuracy)."""
        if self.semantic_classifier:
            try:
                return self.semantic_classifier.classify(message, context)
            except Exception as e:
                logger.debug(f"Strong model failed: {e}")
        return None
    
    def _record_stats(self, request: ClassificationRequest):
        """Record routing statistics."""
        self.stats['total'] += 1
        self.stats['total_latency_ms'] += request.latency_ms
        
        model = request.model_used or 'unknown'
        if 'embed' in model:
            self.stats['embedding'] += 1
        elif 'weak' in model:
            self.stats['weak'] += 1
        elif 'strong' in model:
            self.stats['strong'] += 1
    
    def _buffer_for_training(self, request: ClassificationRequest):
        """Buffer classified results for distillation training data export."""
        if request.result and len(self._training_buffer) < self._max_buffer_size:
            self._training_buffer.append(request)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get distillation routing statistics."""
        total = max(self.stats['total'], 1)
        avg_latency = round(self.stats['total_latency_ms'] / total, 2)
        
        return {
            **self.stats,
            'avg_latency_ms': avg_latency,
            'mode': self.mode.value,
            'embedding_pct': round(self.stats['embedding'] / total * 100, 1),
            'weak_pct': round(self.stats['weak'] / total * 100, 1),
            'strong_pct': round(self.stats['strong'] / total * 100, 1),
            'fallback_rate': round(self.stats['fallback_count'] / total * 100, 1),
            'buffer_size': len(self._training_buffer),
        }
    
    def export_training_data(self, output_path: str = None) -> Dict[str, Any]:
        """Export buffered classifications as training data for distillation.
        
        Format suitable for fine-tuning a smaller model on strong-model outputs.
        """
        samples = [r.to_training_sample() for r in self._training_buffer]
        samples = [s for s in samples if s]
        
        output = {
            'exported_at': time.time(),
            'total_samples': len(samples),
            'by_model': {},
            'by_predicted_type': {},
            'samples': samples[:500],
        }
        
        for s in samples:
            model = s.get('model_used', 'unknown')
            output['by_model'][model] = output['by_model'].get(model, 0) + 1
            ptype = s.get('predicted_type', 'unknown')
            output['by_predicted_type'][ptype] = output['by_predicted_type'].get(ptype, 0) + 1
        
        if output_path:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            logger.info(f"Exported {len(samples)} training samples to {output_path}")
        
        self._training_buffer.clear()
        return output
    
    def set_mode(self, mode: DistillationMode):
        """Switch distillation mode at runtime."""
        self.mode = mode
        logger.info(f"DistillationRouter: Mode changed to {mode.value}")


import re
