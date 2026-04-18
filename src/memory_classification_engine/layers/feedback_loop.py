"""Automated feedback loop for self-improving memory classification.

Collects user feedback, identifies patterns, and auto-tunes Layer 1 rules.
This enables the system to learn from corrections without manual intervention.

Pipeline:
  provide_feedback() → FeedbackAnalyzer.record() → pattern detection → 
  RuleTuner.suggest_rules() → auto-apply (confidence > threshold)
"""

import re
import json
import os
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class FeedbackEvent:
    """Single feedback event with context."""
    
    def __init__(self, memory_id: str, original_type: str, feedback_type: str,
                 feedback_value: str, content: str = '', timestamp: float = None):
        self.memory_id = memory_id
        self.original_type = original_type
        self.feedback_type = feedback_type
        self.feedback_value = feedback_value
        self.content = content
        self.timestamp = timestamp or time.time()
        self.content_lower = content.lower() if content else ''
        self.keywords = self._extract_keywords()
    
    def _extract_keywords(self) -> List[str]:
        if not self.content_lower:
            return []
        words = re.findall(r'[a-zA-Z\u4e00-\u9fff]{2,}', self.content_lower)
        return [w for w in words if len(w) >= 2]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'memory_id': self.memory_id,
            'original_type': self.original_type,
            'feedback_type': self.feedback_type,
            'feedback_value': self.feedback_value,
            'content': self.content,
            'timestamp': self.timestamp,
        }


class FeedbackAnalyzer:
    """Analyzes collected feedback to identify patterns for rule generation."""
    
    def __init__(self, min_pattern_count: int = 3, confidence_threshold: float = 0.7):
        self.events: List[FeedbackEvent] = []
        self.min_pattern_count = min_pattern_count
        self.confidence_threshold = confidence_threshold
        self._pattern_cache: Optional[Dict[str, Any]] = None
        self._cache_dirty = True
    
    def record(self, event: FeedbackEvent):
        """Record a feedback event."""
        self.events.append(event)
        self._cache_dirty = True
        
        if len(self.events) % 50 == 0:
            logger.info(f"FeedbackAnalyzer: {len(self.events)} events recorded")
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze all recorded feedback to find recurring patterns."""
        if not self._cache_dirty and self._pattern_cache:
            return self._pattern_cache
        
        corrections_by_target = defaultdict(list)
        
        for event in self.events:
            if event.feedback_value == 'negative' or event.feedback_type == 'correction':
                target_type = self._infer_target_type(event)
                if target_type and target_type != event.original_type:
                    key = (event.original_type, target_type)
                    corrections_by_target[key].append(event)
        
        suggestions = []
        for (original_type, target_type), events in corrections_by_target.items():
            if len(events) < self.min_pattern_count:
                continue
            
            common_keywords = self._find_common_keywords(events)
            suggested_pattern = self._build_pattern(common_keywords, events)
            
            if not suggested_pattern:
                continue
            
            confidence = min(len(events) / max(len(self.events), 1), 1.0)
            
            suggestion = {
                'pattern': suggested_pattern,
                'source_type': original_type,
                'target_type': target_type,
                'event_count': len(events),
                'confidence': round(confidence, 4),
                'keywords': common_keywords[:5],
                'sample_contents': [e.content[:80] for e in events[:3]],
                'auto_apply': confidence >= self.confidence_threshold,
            }
            suggestions.append(suggestion)
        
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        
        result = {
            'total_events': len(self.events),
            'patterns_found': len(suggestions),
            'suggestions': suggestions,
            'analyzed_at': time.time(),
        }
        
        self._pattern_cache = result
        self._cache_dirty = False
        return result
    
    def _infer_target_type(self, event: FeedbackEvent) -> Optional[str]:
        known_types = {
            'user_preference', 'correction', 'fact_declaration', 'decision',
            'relationship', 'task_pattern', 'sentiment_marker',
        }
        content = event.content_lower
        comment = getattr(event, 'comment', '')
        
        for t in known_types:
            if t in content or t.replace('_', '') in content:
                return t
        
        pref_indicators = ['prefer', 'like', 'want', 'always', 'should', '偏好', '喜欢']
        corr_indicators = ['wrong', 'not', 'actually', 'correct', 'fix', '纠正', '错误']
        fact_indicators = ['fact', 'is', 'are', 'was', '事实', '是']
        decision_indicators = ['decide', 'chose', 'use', 'go with', '决定', '选择']
        task_indicators = ['do', 'implement', 'create', 'add', '做', '实现', '添加']
        
        indicators_map = {
            'user_preference': pref_indicators,
            'correction': corr_indicators,
            'fact_declaration': fact_indicators,
            'decision': decision_indicators,
            'task_pattern': task_indicators,
        }
        
        for type_name, indicators in indicators_map.items():
            if any(ind in content for ind in indicators):
                return type_name
        
        return event.original_type
    
    def _find_common_keywords(self, events: List[FeedbackEvent]) -> List[Tuple[str, int]]:
        keyword_counts: Counter = Counter()
        for event in events:
            for kw in event.keywords:
                stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were',
                              'this', 'that', 'for', 'with', 'and', 'but', 'not'}
                if kw.lower() not in stop_words and len(kw) >= 2:
                    keyword_counts[kw] += 1
        
        return keyword_counts.most_common(10)
    
    def _build_pattern(self, keywords: List[Tuple[str, int]], events: List[FeedbackEvent]) -> Optional[str]:
        if not keywords:
            return None
        
        top_keywords = [kw for kw, count in keywords if count >= 2]
        if not top_keywords:
            top_keywords = [keywords[0][0]] if keywords else []
        
        if len(top_keywords) == 1:
            return re.escape(top_keywords[0])
        
        pattern_parts = [re.escape(kw) for kw in top_keywords[:4]]
        return '|'.join(pattern_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feedback analysis statistics."""
        total = len(self.events)
        if total == 0:
            return {'total_events': 0, 'by_type': {}, 'by_value': {}}
        
        by_type = Counter(e.feedback_type for e in self.events)
        by_value = Counter(e.feedback_value for e in self.events)
        by_original = Counter(e.original_type for e in self.events)
        
        return {
            'total_events': total,
            'by_type': dict(by_type),
            'by_value': dict(by_value),
            'by_original_type': dict(by_original),
        }


class RuleTuner:
    """Converts feedback analysis results into actual rule changes."""
    
    def __init__(self, rule_matcher=None, auto_apply_threshold: float = 0.8):
        self.rule_matcher = rule_matcher
        self.auto_apply_threshold = auto_apply_threshold
        self.applied_rules: List[Dict[str, Any]] = []
        self.rejected_rules: List[Dict[str, Any]] = []
    
    def generate_rule_suggestions(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert analysis patterns into concrete rule suggestions."""
        suggestions = analysis_result.get('suggestions', [])
        rule_suggestions = []
        
        tier_map = {
            'user_preference': 2,
            'correction': 2,
            'task_pattern': 2,
            'fact_declaration': 3,
            'decision': 3,
            'relationship': 3,
            'sentiment_marker': 3,
        }
        
        for s in suggestions:
            rule = {
                'pattern': s['pattern'],
                'memory_type': s['target_type'],
                'tier': tier_map.get(s['target_type'], 3),
                'action': 'extract',
                'description': f"Auto-generated from {s['event_count']} feedback events",
                'priority': 6,
                'language': 'all',
                'source': 'feedback_loop_auto',
                'confidence': s['confidence'],
                'based_on_events': s['event_count'],
                'keywords': s.get('keywords', []),
            }
            rule_suggestions.append(rule)
        
        return rule_suggestions
    
    def apply_suggestion(self, rule: Dict[str, Any]) -> bool:
        """Apply a single rule suggestion to the rule matcher."""
        if not self.rule_matcher:
            logger.warning("RuleTuner: No rule_matcher configured, cannot apply rule")
            return False
        
        try:
            existing_patterns = {r.get('pattern') for r in self.rule_matcher.get_rules()}
            
            if rule['pattern'] in existing_patterns:
                logger.debug(f"RuleTuner: Pattern '{rule['pattern']}' already exists, skipping")
                self.rejected_rules.append({**rule, 'reason': 'duplicate'})
                return False
            
            if rule.get('confidence', 0) < self.auto_apply_threshold:
                logger.debug(f"RuleTuner: Rule confidence {rule['confidence']} below threshold {self.auto_apply_threshold}")
                self.rejected_rules.append({**rule, 'reason': 'low_confidence'})
                return False
            
            clean_rule = {
                'pattern': rule['pattern'],
                'memory_type': rule['memory_type'],
                'tier': rule['tier'],
                'action': rule.get('action', 'extract'),
                'description': rule.get('description', ''),
                'priority': rule.get('priority', 5),
                'language': rule.get('language', 'all'),
            }
            
            self.rule_matcher.add_rule(clean_rule)
            self.applied_rules.append(rule)
            logger.info(f"RuleTuner: Applied auto-rule '{rule['pattern']}' → {rule['memory_type']} (conf={rule['confidence']})")
            return True
            
        except Exception as e:
            logger.error(f"RuleTuner: Error applying rule: {e}")
            self.rejected_rules.append({**rule, 'reason': str(e)})
            return False
    
    def auto_tune(self, analyzer: FeedbackAnalyzer) -> Dict[str, Any]:
        """Run full auto-tune pipeline: analyze → suggest → apply."""
        analysis = analyzer.analyze_patterns()
        suggestions = self.generate_rule_suggestions(analysis)
        
        applied = 0
        rejected = 0
        for rule in suggestions:
            if self.apply_suggestion(rule):
                applied += 1
            else:
                rejected += 1
        
        return {
            'patterns_analyzed': analysis['patterns_found'],
            'suggestions_generated': len(suggestions),
            'rules_applied': applied,
            'rules_rejected': rejected,
            'total_active_rules': len(self.rule_matcher.get_rules()) if self.rule_matcher else 0,
        }


class FeedbackLoop:
    """Orchestrates the complete feedback loop: collect → analyze → tune."""
    
    def __init__(self, rule_matcher=None, state_path: str = None):
        self.analyzer = FeedbackAnalyzer()
        self.tuner = RuleTuner(rule_matcher=rule_matcher)
        self.state_path = state_path or './data/feedback_loop_state.json'
        self.enabled = True
        self._load_state()
    
    def record_feedback(self, memory_id: str, original_type: str, feedback_type: str,
                        feedback_value: str, content: str = '', comment: str = '') -> Dict[str, Any]:
        """Record feedback and optionally trigger auto-tuning."""
        event = FeedbackEvent(
            memory_id=memory_id,
            original_type=original_type,
            feedback_type=feedback_type,
            feedback_value=feedback_value,
            content=content,
        )
        event.comment = comment
        self.analyzer.record(event)
        
        result = {
            'recorded': True,
            'total_events': len(self.analyzer.events),
            'event': event.to_dict(),
        }
        
        if len(self.analyzer.events) % 20 == 0 and self.enabled:
            tune_result = self.tuner.auto_tune(self.analyzer)
            result['auto_tune'] = tune_result
            self._save_state()
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get full feedback loop status."""
        analysis = self.analyzer.analyze_patterns()
        return {
            'enabled': self.enabled,
            'total_feedback_events': len(self.analyzer.events),
            'stats': self.analyzer.get_stats(),
            'patterns': analysis.get('suggestions', []),
            'rules_applied': len(self.tuner.applied_rules),
            'rules_rejected': len(self.tuner.rejected_rules),
        }
    
    def force_tune(self) -> Dict[str, Any]:
        """Force-run the tuning pipeline regardless of event count."""
        return self.tuner.auto_tune(self.analyzer)
    
    def _load_state(self):
        """Load persisted state from disk."""
        try:
            if os.path.exists(self.state_path):
                with open(self.state_path, 'r') as f:
                    state = json.load(f)
                self.enabled = state.get('enabled', True)
                logger.debug(f"FeedbackLoop: Loaded state from {self.state_path}")
        except Exception as e:
            logger.debug(f"FeedbackLoop: Could not load state: {e}")
    
    def _save_state(self):
        """Persist state to disk."""
        try:
            os.makedirs(os.path.dirname(self.state_path) or '.', exist_ok=True)
            state = {
                'enabled': self.enabled,
                'total_events': len(self.analyzer.events),
                'rules_applied': len(self.tuner.applied_rules),
                'last_updated': time.time(),
            }
            with open(self.state_path, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.debug(f"FeedbackLoop: Could not save state: {e}")
