from typing import Dict, List, Optional, Any
import re
from memory_classification_engine.utils.language import language_manager

class PatternAnalyzer:
    """Pattern-based memory analyzer."""
    
    def __init__(self):
        """Initialize the pattern analyzer."""
        # Initialize counters for pattern detection
        self.message_history = []
        self.task_patterns = {}
        self.preference_patterns = {}
        self.correction_patterns = {}
        self.fact_patterns = {}
        self.relationship_patterns = {}
    
    def analyze(self, message: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Analyze a message for patterns.
        
        Args:
            message: The message to analyze.
            context: Optional context for the message.
            
        Returns:
            A list of detected patterns.
        """
        patterns = []
        
        # Add current message to history
        self.message_history.append(message)
        
        # Limit history size
        if len(self.message_history) > 10:
            self.message_history.pop(0)
        
        # Detect language
        language, _ = language_manager.detect_language(message)
        
        # Detect preference patterns
        preference_pattern = self._detect_preference_pattern(message, language)
        if preference_pattern:
            preference_pattern['language'] = language
            patterns.append(preference_pattern)
        
        # Detect correction patterns
        correction_pattern = self._detect_correction_pattern(message, language)
        if correction_pattern:
            correction_pattern['language'] = language
            patterns.append(correction_pattern)
        
        # Detect fact declaration patterns
        fact_pattern = self._detect_fact_pattern(message, language)
        if fact_pattern:
            fact_pattern['language'] = language
            patterns.append(fact_pattern)
        
        # Detect relationship patterns
        relationship_pattern = self._detect_relationship_pattern(message, language)
        if relationship_pattern:
            relationship_pattern['language'] = language
            patterns.append(relationship_pattern)
        
        # Detect task patterns
        task_pattern = self._detect_task_pattern(message, language)
        if task_pattern:
            task_pattern['language'] = language
            patterns.append(task_pattern)
        
        # Detect decision patterns
        decision_pattern = self._detect_decision_pattern(message, language)
        if decision_pattern:
            decision_pattern['language'] = language
            patterns.append(decision_pattern)
        
        # Detect sentiment patterns
        sentiment_pattern = self._detect_sentiment_pattern(message, language)
        if sentiment_pattern:
            sentiment_pattern['language'] = language
            patterns.append(sentiment_pattern)
        
        return patterns
    
    def _detect_preference_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect preference patterns.
        
        Args:
            message: The message to analyze.
            language: The detected language code.
            
        Returns:
            A preference pattern if detected, None otherwise.
        """
        # Get language-specific preference keywords from LanguageManager
        preference_keywords = language_manager.get_keywords('user_preference', language)
        
        message_lower = message.lower()
        for keyword in preference_keywords:
            if keyword in message_lower:
                # Extract preference content
                preference_content = message
                
                # Check if this preference has been expressed before
                preference_hash = hash(preference_content)
                if preference_hash in self.preference_patterns:
                    self.preference_patterns[preference_hash] += 1
                    if self.preference_patterns[preference_hash] >= 2:
                        # This is a repeated preference
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
                    # Return first occurrence with lower confidence
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
        # Get language-specific correction keywords from LanguageManager
        correction_keywords = language_manager.get_keywords('correction', language)
        
        # Add additional common correction markers
        if language == 'en':
            correction_keywords.extend(['no', 'not', 'don\'t', 'doesn\'t', 'didn\'t'])
        elif language == 'zh-cn':
            correction_keywords.extend(['不', '没', '没有', '别', '不要'])
        
        message_lower = message.lower()
        for keyword in correction_keywords:
            if keyword in message_lower:
                # Extract correction content
                correction_content = message
                
                # Check if there's a previous message that this correction refers to
                if len(self.message_history) >= 2:
                    previous_message = self.message_history[-2]
                    if language.startswith('zh'):
                        correction_content = f"纠正: {message}. 针对: {previous_message}"
                    else:
                        correction_content = f"Correction: {message}. Referring to: {previous_message}"
                
                # Check if this correction pattern has been seen before
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
        # Check for fact patterns based on language
        if language.startswith('zh'):
            # Chinese fact patterns
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
                    
                    # Check if this fact has been stated before
                    fact_hash = hash(fact_content)
                    if fact_hash in self.fact_patterns:
                        self.fact_patterns[fact_hash] += 1
                        if self.fact_patterns[fact_hash] >= 2:
                            # This is a repeated fact
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
            # English fact patterns
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
                    
                    # Check if this fact has been stated before
                    fact_hash = hash(fact_content)
                    if fact_hash in self.fact_patterns:
                        self.fact_patterns[fact_hash] += 1
                        if self.fact_patterns[fact_hash] >= 2:
                            # This is a repeated fact
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
        # Get language-specific relationship keywords from LanguageManager
        relationship_keywords = language_manager.get_keywords('relationship', language)
        
        message_lower = message.lower()
        for keyword in relationship_keywords:
            if keyword in message_lower:
                # Extract relationship content
                relationship_content = message
                
                # Check if this relationship has been mentioned before
                relationship_hash = hash(relationship_content)
                if relationship_hash in self.relationship_patterns:
                    self.relationship_patterns[relationship_hash] += 1
                    if self.relationship_patterns[relationship_hash] >= 2:
                        # This is a repeated relationship
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
        # Get language-specific task keywords from LanguageManager
        task_keywords = language_manager.get_keywords('task_pattern', language)
        
        # Add additional common task markers
        if language == 'en':
            task_keywords.extend(['help', 'write', 'create', 'build', 'make', 'generate', 'develop', 'implement'])
        elif language == 'zh-cn':
            task_keywords.extend(['帮', '写', '创建', '构建', '制作', '生成', '开发', '实现'])
        
        message_lower = message.lower()
        for keyword in task_keywords:
            if keyword in message_lower:
                # Extract task content
                task_content = message
                
                # Check if this task has been requested before
                task_hash = hash(task_content)
                if task_hash in self.task_patterns:
                    self.task_patterns[task_hash] += 1
                    if self.task_patterns[task_hash] >= 2:
                        # This is a repeated task
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
                    # Return first occurrence with lower confidence
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
        # Get language-specific decision keywords from LanguageManager
        decision_keywords = language_manager.get_keywords('decision', language)
        
        # Add additional common decision markers
        if language == 'en':
            decision_keywords.extend(['okay', 'ok', 'yes', 'sure', 'let\'s', 'we\'ll', 'we will'])
        elif language == 'zh-cn':
            decision_keywords.extend(['好的', '行', '可以', '同意', '就', '我们', '决定'])
        
        message_lower = message.lower()
        for keyword in decision_keywords:
            if keyword in message_lower:
                # Check if there's a previous message that contains a proposal
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
                    # Return decision pattern even without previous message
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
        # Get language-specific sentiment keywords from LanguageManager
        sentiment_keywords = language_manager.get_keywords('sentiment_marker', language)
        
        # Add additional common sentiment markers
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
