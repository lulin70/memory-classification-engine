from typing import Dict, List, Optional, Any
import re
from memory_classification_engine.utils.language import language_manager

class PatternAnalyzer:
    """Pattern-based memory analyzer."""
    
    def __init__(self):
        """Initialize the pattern analyzer."""
        # Comment in Chinese removedction
        self.message_history = []
        self.task_patterns = {}
        self.preference_patterns = {}
        self.correction_patterns = {}
        self.fact_patterns = {}
        self.relationship_patterns = {}
    
    def analyze(self, message: str, context: Optional[Dict[str, Any]] = None, execution_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Analyze a message for patterns.
        
        Args:
            message: The message to analyze.
            context: Optional context for the message.
            execution_context: Optional execution context containing feedback signals.
            
        Returns:
            A list of detected patterns.
        """
        patterns = []
        
        # Comment in Chinese removed to history
        self.message_history.append(message)
        
        # Comment in Chinese removed
        if len(self.message_history) > 10:
            self.message_history.pop(0)
        
        # Comment in Chinese removed
        language, _ = language_manager.detect_language(message)
        
        # Comment in Chinese removedls
        if execution_context:
            feedback_pattern = self._detect_execution_feedback_pattern(message, execution_context, language)
            if feedback_pattern:
                feedback_pattern['language'] = language
                patterns.append(feedback_pattern)
        
        # Comment in Chinese removedrns
        preference_pattern = self._detect_preference_pattern(message, language)
        if preference_pattern:
            preference_pattern['language'] = language
            patterns.append(preference_pattern)
        
        # Comment in Chinese removedrns
        correction_pattern = self._detect_correction_pattern(message, language)
        if correction_pattern:
            correction_pattern['language'] = language
            patterns.append(correction_pattern)
        
        # Comment in Chinese removedrns
        fact_pattern = self._detect_fact_pattern(message, language)
        if fact_pattern:
            fact_pattern['language'] = language
            patterns.append(fact_pattern)
        
        # Comment in Chinese removedrns
        relationship_pattern = self._detect_relationship_pattern(message, language)
        if relationship_pattern:
            relationship_pattern['language'] = language
            patterns.append(relationship_pattern)
        
        # Comment in Chinese removedrns
        task_pattern = self._detect_task_pattern(message, language)
        if task_pattern:
            task_pattern['language'] = language
            patterns.append(task_pattern)
        
        # Comment in Chinese removedrns
        decision_pattern = self._detect_decision_pattern(message, language)
        if decision_pattern:
            decision_pattern['language'] = language
            patterns.append(decision_pattern)
        
        # Comment in Chinese removedrns
        sentiment_pattern = self._detect_sentiment_pattern(message, language)
        if sentiment_pattern:
            sentiment_pattern['language'] = language
            patterns.append(sentiment_pattern)
        
        return patterns
    
    def _detect_execution_feedback_pattern(self, message: str, execution_context: Dict[str, Any], language: str) -> Optional[Dict[str, Any]]:
        """Detect execution feedback patterns.
        
        Args:
            message: The message to analyze.
            execution_context: Execution context containing feedback signals.
            language: The detected language code.
            
        Returns:
            A dictionary representing the detected feedback pattern, or None if no pattern found.
        """
        # Comment in Chinese removedck
        user_feedback = execution_context.get('user_feedback', '').lower()
        
        # Comment in Chinese removedtrics
        tool_error = execution_context.get('tool_error', False)
        retry_count = execution_context.get('retry_count', 0)
        execution_time = execution_context.get('execution_time', 0)
        
        # Comment in Chinese removedxt position
        context_position = execution_context.get('context_position', '')
        
        # Comment in Chinese removedck
        if any(phrase in user_feedback for phrase in ['对了', '正确', '好的', '成功', '完成', '不错', 'great', 'correct', 'good', 'success', 'done']):
            return {
                'memory_type': 'positive_feedback',
                'tier': 2,
                'content': f"Positive feedback: {message}",
                'confidence': 0.85,
                'source': 'pattern:execution_feedback',
                'feedback_type': 'positive',
                'execution_context': execution_context
            }
        
        # Comment in Chinese removedck
        if any(phrase in user_feedback for phrase in ['不对', '错误', '重做', '失败', '不行', '重新', 'wrong', 'error', 'redo', 'fail', 'no', 'again']):
            return {
                'memory_type': 'negative_feedback',
                'tier': 3,
                'content': f"Negative feedback: {message}",
                'confidence': 0.85,
                'source': 'pattern:execution_feedback',
                'feedback_type': 'negative',
                'execution_context': execution_context
            }
        
        # Comment in Chinese removedck
        if tool_error:
            return {
                'memory_type': 'tool_error',
                'tier': 3,
                'content': f"Tool error detected: {message}",
                'confidence': 0.90,
                'source': 'pattern:execution_feedback',
                'feedback_type': 'error',
                'execution_context': execution_context
            }
        
        # Comment in Chinese removedck
        if retry_count > 0:
            return {
                'memory_type': 'retry_needed',
                'tier': 3,
                'content': f"Retry needed: {message}",
                'confidence': 0.80,
                'source': 'pattern:execution_feedback',
                'feedback_type': 'retry',
                'execution_context': execution_context
            }
        
        # Comment in Chinese removedck
        if execution_time > 10:  # Comment in Chinese removedshold
            return {
                'memory_type': 'performance_issue',
                'tier': 3,
                'content': f"Performance issue: {message} (executed in {execution_time}s)",
                'confidence': 0.75,
                'source': 'pattern:execution_feedback',
                'feedback_type': 'performance',
                'execution_context': execution_context
            }
        
        # Comment in Chinese removedrns
        if context_position == 'correction_followup':
            return {
                'memory_type': 'correction_followup',
                'tier': 3,
                'content': f"Correction followup: {message}",
                'confidence': 0.80,
                'source': 'pattern:execution_feedback',
                'feedback_type': 'context',
                'execution_context': execution_context
            }
        
        if context_position == 'confirmation_pending':
            return {
                'memory_type': 'confirmation_pending',
                'tier': 2,
                'content': f"Confirmation pending: {message}",
                'confidence': 0.75,
                'source': 'pattern:execution_feedback',
                'feedback_type': 'context',
                'execution_context': execution_context
            }
        
        return None
    
    def _detect_preference_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect preference patterns.
        
        Args:
            message: The message to analyze.
            language: The detected language code.
            
        Returns:
            A preference pattern if detected, None otherwise.
        """
        # Comment in Chinese removedr
        preference_keywords = language_manager.get_keywords('user_preference', language)
        
        message_lower = message.lower()
        for keyword in preference_keywords:
            if keyword in message_lower:
                # Comment in Chinese removednt
                preference_content = message
                
                # Comment in Chinese removed
                preference_hash = hash(preference_content)
                if preference_hash in self.preference_patterns:
                    self.preference_patterns[preference_hash] += 1
                    if self.preference_patterns[preference_hash] >= 2:
                        # Comment in Chinese removed
                        return {
                            'memory_type': 'user_preference',
                            'tier': 2,
                            'content': preference_content,
                            'confidence': 0.8,
                            'source': 'pattern:preference_repeat',
                            'description': '重复偏好模式'
                        }
                else:
                    self.preference_patterns[preference_hash] = 1
                    # Comment in Chinese removed
                    return {
                        'memory_type': 'user_preference',
                        'tier': 2,
                        'content': preference_content,
                        'confidence': 0.6,
                        'source': 'pattern:preference',
                        'description': '偏好模式'
                    }
        
        return None
    
    def _detect_correction_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect correction patterns.
        
        Args:
            message: The message to analyze.
            language: The detected language code.
            
        Returns:
            A correction pattern if detected, None otherwise.
        """
        # Comment in Chinese removedr
        correction_keywords = language_manager.get_keywords('correction', language)
        
        # Comment in Chinese removedrs
        if language == 'en':
            correction_keywords.extend(['no', 'not', 'don\'t', 'doesn\'t', 'didn\'t'])
        elif language == 'zh-cn':
            correction_keywords.extend(['不', '没', '没有', '别', '不要'])
        
        message_lower = message.lower()
        for keyword in correction_keywords:
            if keyword in message_lower:
                # Comment in Chinese removednt
                correction_content = message
                
                # Comment in Chinese removedrs to
                if len(self.message_history) >= 2:
                    previous_message = self.message_history[-2]
                    if language.startswith('zh'):
                        correction_content = f"纠正: {message}. 针对: {previous_message}"
                    else:
                        correction_content = f"Correction: {message}. Referring to: {previous_message}"
                
                # Comment in Chinese removed
                correction_hash = hash(correction_content)
                if correction_hash in self.correction_patterns:
                    self.correction_patterns[correction_hash] += 1
                else:
                    self.correction_patterns[correction_hash] = 1
                
                return {
                    'memory_type': 'correction',
                    'tier': 3,
                    'content': correction_content,
                    'confidence': 0.7,
                    'source': 'pattern:correction',
                    'description': '纠正模式'
                }
        
        return None
    
    def _detect_fact_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect fact declaration patterns.
        
        Args:
            message: The message to analyze.
            language: The detected language code.
            
        Returns:
            A fact pattern if detected, None otherwise.
        """
        # Comment in Chinese removed
        if language.startswith('zh'):
            # Comment in Chinese removedrns
            fact_patterns = [
                r'(.+)是(.+)',
                r'(.+)有(.+)',
                r'(.+)在做(.+)',
                r'(.+)属于(.+)',
                r'(.+)位于(.+)'
            ]
            
            for pattern in fact_patterns:
                match = re.search(pattern, message)
                if match:
                    fact_content = message
                    
                    # Comment in Chinese removed
                    fact_hash = hash(fact_content)
                    if fact_hash in self.fact_patterns:
                        self.fact_patterns[fact_hash] += 1
                        if self.fact_patterns[fact_hash] >= 2:
                            # Comment in Chinese removedct
                            return {
                                'memory_type': 'fact_declaration',
                                'tier': 4,
                                'content': fact_content,
                                'confidence': 0.8,
                                'source': 'pattern:fact_repeat',
                                'description': '重复事实模式'
                            }
                    else:
                        self.fact_patterns[fact_hash] = 1
                    
                    return {
                        'memory_type': 'fact_declaration',
                        'tier': 4,
                        'content': fact_content,
                        'confidence': 0.7,
                        'source': 'pattern:fact',
                        'description': '事实声明模式'
                    }
        else:
            # Comment in Chinese removedrns
            fact_patterns = [
                r'(.+) is (.+)',
                r'(.+) has (.+)',
                r'(.+) are (.+)',
                r'(.+) was (.+)',
                r'(.+) were (.+)',
                r'(.+) will be (.+)'
            ]
            
            message_lower = message.lower()
            for pattern in fact_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    fact_content = message
                    
                    # Comment in Chinese removed
                    fact_hash = hash(fact_content)
                    if fact_hash in self.fact_patterns:
                        self.fact_patterns[fact_hash] += 1
                        if self.fact_patterns[fact_hash] >= 2:
                            # Comment in Chinese removedct
                            return {
                                'memory_type': 'fact_declaration',
                                'tier': 4,
                                'content': fact_content,
                                'confidence': 0.8,
                                'source': 'pattern:fact_repeat',
                                'description': '重复事实模式'
                            }
                    else:
                        self.fact_patterns[fact_hash] = 1
                    
                    return {
                        'memory_type': 'fact_declaration',
                        'tier': 4,
                        'content': fact_content,
                        'confidence': 0.7,
                        'source': 'pattern:fact',
                        'description': '事实声明模式'
                    }
        
        return None
    
    def _detect_relationship_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect relationship patterns.
        
        Args:
            message: The message to analyze.
            language: The detected language code.
            
        Returns:
            A relationship pattern if detected, None otherwise.
        """
        # Comment in Chinese removedr
        relationship_keywords = language_manager.get_keywords('relationship', language)
        
        message_lower = message.lower()
        for keyword in relationship_keywords:
            if keyword in message_lower:
                # Comment in Chinese removednt
                relationship_content = message
                
                # Comment in Chinese removed
                relationship_hash = hash(relationship_content)
                if relationship_hash in self.relationship_patterns:
                    self.relationship_patterns[relationship_hash] += 1
                    if self.relationship_patterns[relationship_hash] >= 2:
                        # Comment in Chinese removedtionship
                        return {
                            'memory_type': 'relationship',
                            'tier': 4,
                            'content': relationship_content,
                            'confidence': 0.8,
                            'source': 'pattern:relationship_repeat',
                            'description': '重复关系模式'
                        }
                else:
                    self.relationship_patterns[relationship_hash] = 1
                
                return {
                    'memory_type': 'relationship',
                    'tier': 4,
                    'content': relationship_content,
                    'confidence': 0.7,
                    'source': 'pattern:relationship',
                    'description': '关系信息模式'
                }
        
        return None
    
    def _detect_task_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect task patterns.
        
        Args:
            message: The message to analyze.
            language: The detected language code.
            
        Returns:
            A task pattern if detected, None otherwise.
        """
        # Comment in Chinese removedr
        task_keywords = language_manager.get_keywords('task_pattern', language)
        
        # Comment in Chinese removedrs
        if language == 'en':
            task_keywords.extend(['help', 'write', 'create', 'build', 'make', 'generate', 'develop', 'implement'])
        elif language == 'zh-cn':
            task_keywords.extend(['帮', '写', '创建', '构建', '制作', '生成', '开发', '实现'])
        
        message_lower = message.lower()
        for keyword in task_keywords:
            if keyword in message_lower:
                # Comment in Chinese removednt
                task_content = message
                
                # Comment in Chinese removed
                task_hash = hash(task_content)
                if task_hash in self.task_patterns:
                    self.task_patterns[task_hash] += 1
                    if self.task_patterns[task_hash] >= 2:
                        # Comment in Chinese removedsk
                        return {
                            'memory_type': 'task_pattern',
                            'tier': 3,
                            'content': task_content,
                            'confidence': 0.8,
                            'source': 'pattern:task_repeat',
                            'description': '重复任务模式'
                        }
                else:
                    self.task_patterns[task_hash] = 1
                    # Comment in Chinese removed
                    return {
                        'memory_type': 'task_pattern',
                        'tier': 3,
                        'content': task_content,
                        'confidence': 0.6,
                        'source': 'pattern:task',
                        'description': '任务模式'
                    }
        
        return None
    
    def _detect_decision_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect decision patterns.
        
        Args:
            message: The message to analyze.
            language: The detected language code.
            
        Returns:
            A decision pattern if detected, None otherwise.
        """
        # Comment in Chinese removedr
        decision_keywords = language_manager.get_keywords('decision', language)
        
        # Comment in Chinese removedrs
        if language == 'en':
            decision_keywords.extend(['okay', 'ok', 'yes', 'sure', 'let\'s', 'we\'ll', 'we will'])
        elif language == 'zh-cn':
            decision_keywords.extend(['好的', '行', '可以', '同意', '就', '我们', '决定'])
        
        message_lower = message.lower()
        for keyword in decision_keywords:
            if keyword in message_lower:
                # Comment in Chinese removedl
                if len(self.message_history) >= 2:
                    previous_message = self.message_history[-2]
                    if language.startswith('zh'):
                        return {
                            'memory_type': 'decision',
                            'tier': 3,
                            'content': f"决定: {message}. 基于: {previous_message}",
                            'confidence': 0.7,
                            'source': 'pattern:decision',
                            'description': '决策模式'
                        }
                    else:
                        return {
                            'memory_type': 'decision',
                            'tier': 3,
                            'content': f"Decision: {message}. Based on: {previous_message}",
                            'confidence': 0.7,
                            'source': 'pattern:decision',
                            'description': '决策模式'
                        }
                else:
                    # Comment in Chinese removed
                    if language.startswith('zh'):
                        return {
                            'memory_type': 'decision',
                            'tier': 3,
                            'content': f"决定: {message}",
                            'confidence': 0.6,
                            'source': 'pattern:decision',
                            'description': '决策模式'
                        }
                    else:
                        return {
                            'memory_type': 'decision',
                            'tier': 3,
                            'content': f"Decision: {message}",
                            'confidence': 0.6,
                            'source': 'pattern:decision',
                            'description': '决策模式'
                        }
        
        return None
    
    def _detect_sentiment_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect sentiment patterns.
        
        Args:
            message: The message to analyze.
            language: The detected language code.
            
        Returns:
            A sentiment pattern if detected, None otherwise.
        """
        # Comment in Chinese removedr
        sentiment_keywords = language_manager.get_keywords('sentiment_marker', language)
        
        # Comment in Chinese removedrs
        if language == 'en':
            sentiment_keywords.extend(['great', 'awesome', 'fantastic', 'wonderful', 'excellent', 'amazing', 'terrible', 'bad', 'horrible', 'awful'])
        elif language == 'zh-cn':
            sentiment_keywords.extend(['棒', '很棒', '真好', '太好了', '优秀', '惊人', '可怕', '糟糕', '恶心', '恐怖'])
        
        message_lower = message.lower()
        for keyword in sentiment_keywords:
            if keyword in message_lower:
                if language.startswith('zh'):
                    return {
                        'memory_type': 'sentiment_marker',
                        'tier': 3,
                        'content': f"情感: {message}",
                        'confidence': 0.6,
                        'source': 'pattern:sentiment',
                        'description': '情感模式'
                    }
                else:
                    return {
                        'memory_type': 'sentiment_marker',
                        'tier': 3,
                        'content': f"Sentiment: {message}",
                        'confidence': 0.6,
                        'source': 'pattern:sentiment',
                        'description': '情感模式'
                    }
        
        return None
    
    def clear_history(self):
        """Clear the message history."""
        self.message_history = []
        self.task_patterns = {}
        self.preference_patterns = {}
        self.correction_patterns = {}
        self.fact_patterns = {}
        self.relationship_patterns = {}
