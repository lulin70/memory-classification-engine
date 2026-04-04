from typing import Dict, List, Optional, Any
import re

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
        
        # Detect preference patterns
        preference_pattern = self._detect_preference_pattern(message)
        if preference_pattern:
            patterns.append(preference_pattern)
        
        # Detect correction patterns
        correction_pattern = self._detect_correction_pattern(message)
        if correction_pattern:
            patterns.append(correction_pattern)
        
        # Detect fact declaration patterns
        fact_pattern = self._detect_fact_pattern(message)
        if fact_pattern:
            patterns.append(fact_pattern)
        
        # Detect relationship patterns
        relationship_pattern = self._detect_relationship_pattern(message)
        if relationship_pattern:
            patterns.append(relationship_pattern)
        
        # Detect task patterns
        task_pattern = self._detect_task_pattern(message)
        if task_pattern:
            patterns.append(task_pattern)
        
        # Detect decision patterns
        decision_pattern = self._detect_decision_pattern(message)
        if decision_pattern:
            patterns.append(decision_pattern)
        
        # Detect sentiment patterns
        sentiment_pattern = self._detect_sentiment_pattern(message)
        if sentiment_pattern:
            patterns.append(sentiment_pattern)
        
        return patterns
    
    def _detect_task_pattern(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect task patterns.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A task pattern if detected, None otherwise.
        """
        # Check for repeated task requests
        task_keywords = ['需要', '帮忙', '做', '写', '改', '查', '找', '创建', '生成']
        
        for keyword in task_keywords:
            if keyword in message:
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
        
        return None
    
    def _detect_decision_pattern(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect decision patterns.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A decision pattern if detected, None otherwise.
        """
        # Check for decision keywords
        decision_keywords = ['决定', '确认', '同意', '批准', '通过', '好的', '行', '可以', '没问题']
        
        for keyword in decision_keywords:
            if keyword in message:
                # Check if there's a previous message that contains a proposal
                if len(self.message_history) >= 2:
                    previous_message = self.message_history[-2]
                    return {
                        'memory_type': 'decision',
                        'tier': 3,
                        'content': f"决定: {message}. 基于: {previous_message}",
                        'confidence': 0.7,
                        'source': 'pattern:decision',
                        'description': '决策模式'
                    }
        
        return None
    
    def _detect_preference_pattern(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect preference patterns.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A preference pattern if detected, None otherwise.
        """
        # Check for preference keywords in Chinese
        chinese_preference_keywords = ['喜欢', '偏好', '希望', '想要', '偏爱', '倾向于', '更愿意', '喜欢用', '习惯']
        # Check for preference keywords in English
        english_preference_keywords = ['like', 'prefer', 'love', 'enjoy', 'favor', 'want', 'would like', 'tend to', 'habitually']
        
        # Check Chinese preferences
        for keyword in chinese_preference_keywords:
            if keyword in message:
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
        
        # Check English preferences
        message_lower = message.lower()
        for keyword in english_preference_keywords:
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
    
    def _detect_correction_pattern(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect correction patterns.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A correction pattern if detected, None otherwise.
        """
        # Check for correction keywords in Chinese
        chinese_correction_keywords = ['不对', '错了', '不是', '你搞错了', '我说的是', '应该是', '其实是', '实际上是']
        # Check for correction keywords in English
        english_correction_keywords = ['no', 'not', 'wrong', 'incorrect', 'actually', 'should be', 'I meant', 'I said']
        
        # Check Chinese corrections
        for keyword in chinese_correction_keywords:
            if keyword in message:
                # Extract correction content
                correction_content = message
                
                # Check if there's a previous message that this correction refers to
                if len(self.message_history) >= 2:
                    previous_message = self.message_history[-2]
                    correction_content = f"纠正: {message}. 针对: {previous_message}"
                
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
        
        # Check English corrections
        message_lower = message.lower()
        for keyword in english_correction_keywords:
            if keyword in message_lower:
                # Extract correction content
                correction_content = message
                
                # Check if there's a previous message that this correction refers to
                if len(self.message_history) >= 2:
                    previous_message = self.message_history[-2]
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
    
    def _detect_fact_pattern(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect fact declaration patterns.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A fact pattern if detected, None otherwise.
        """
        # Check for fact patterns in Chinese
        chinese_fact_patterns = [
            r'(.+)是(.+)',
            r'(.+)有(.+)',
            r'(.+)在做(.+)',
            r'(.+)属于(.+)',
            r'(.+)位于(.+)'
        ]
        
        # Check for fact patterns in English
        english_fact_patterns = [
            r'(.+) is (.+)',
            r'(.+) has (.+)',
            r'(.+) are (.+)',
            r'(.+) was (.+)',
            r'(.+) were (.+)',
            r'(.+) will be (.+)'
        ]
        
        # Check Chinese fact patterns
        for pattern in chinese_fact_patterns:
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
        
        # Check English fact patterns
        message_lower = message.lower()
        for pattern in english_fact_patterns:
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
    
    def _detect_relationship_pattern(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect relationship patterns.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A relationship pattern if detected, None otherwise.
        """
        # Check for relationship keywords in Chinese
        chinese_relationship_keywords = ['负责', '管理', '属于', '汇报给', '领导', '下属', '同事', '朋友', '家人', '亲戚']
        # Check for relationship keywords in English
        english_relationship_keywords = ['in charge of', 'responsible for', 'manage', 'report to', 'lead', 'subordinate', 'colleague', 'friend', 'family', 'relative', 'belongs to']
        
        # Check Chinese relationships
        for keyword in chinese_relationship_keywords:
            if keyword in message:
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
        
        # Check English relationships
        message_lower = message.lower()
        for keyword in english_relationship_keywords:
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
    
    def _detect_task_pattern(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect task patterns.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A task pattern if detected, None otherwise.
        """
        # Check for task keywords in Chinese
        chinese_task_keywords = ['需要', '帮忙', '做', '写', '改', '查', '找', '创建', '生成']
        # Check for task keywords in English
        english_task_keywords = ['need', 'help', 'do', 'write', 'modify', 'check', 'find', 'create', 'generate', 'build', 'make']
        
        # Check Chinese tasks
        for keyword in chinese_task_keywords:
            if keyword in message:
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
        
        # Check English tasks
        message_lower = message.lower()
        for keyword in english_task_keywords:
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
    
    def _detect_decision_pattern(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect decision patterns.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A decision pattern if detected, None otherwise.
        """
        # Check for decision keywords in Chinese
        chinese_decision_keywords = ['决定', '确认', '同意', '批准', '通过', '好的', '行', '可以', '没问题']
        # Check for decision keywords in English
        english_decision_keywords = ['decide', 'confirm', 'agree', 'approve', 'pass', 'okay', 'ok', 'yes', 'no problem']
        
        # Check Chinese decisions
        for keyword in chinese_decision_keywords:
            if keyword in message:
                # Check if there's a previous message that contains a proposal
                if len(self.message_history) >= 2:
                    previous_message = self.message_history[-2]
                    return {
                        'memory_type': 'decision',
                        'tier': 3,
                        'content': f"决定: {message}. 基于: {previous_message}",
                        'confidence': 0.7,
                        'source': 'pattern:decision',
                        'description': '决策模式'
                    }
        
        # Check English decisions
        message_lower = message.lower()
        for keyword in english_decision_keywords:
            if keyword in message_lower:
                # Check if there's a previous message that contains a proposal
                if len(self.message_history) >= 2:
                    previous_message = self.message_history[-2]
                    return {
                        'memory_type': 'decision',
                        'tier': 3,
                        'content': f"Decision: {message}. Based on: {previous_message}",
                        'confidence': 0.7,
                        'source': 'pattern:decision',
                        'description': '决策模式'
                    }
        
        return None
    
    def _detect_sentiment_pattern(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect sentiment patterns.
        
        Args:
            message: The message to analyze.
            
        Returns:
            A sentiment pattern if detected, None otherwise.
        """
        # Check for sentiment keywords in Chinese
        chinese_positive_keywords = ['喜欢', '爱', '好', '棒', '优秀', '满意', '推荐', '赞']
        chinese_negative_keywords = ['讨厌', '不喜欢', '差', '糟糕', '失望', '不满', '反感', '垃圾']
        
        # Check for sentiment keywords in English
        english_positive_keywords = ['like', 'love', 'good', 'great', 'excellent', 'satisfied', 'recommend', 'awesome']
        english_negative_keywords = ['hate', 'dislike', 'bad', 'terrible', 'disappointed', 'unsatisfied', 'disgust', 'awful']
        
        # Check Chinese sentiment
        for keyword in chinese_positive_keywords:
            if keyword in message:
                return {
                    'memory_type': 'sentiment_marker',
                    'tier': 3,
                    'content': f"正面情感: {message}",
                    'confidence': 0.6,
                    'source': 'pattern:positive_sentiment',
                    'description': '正面情感模式'
                }
        
        for keyword in chinese_negative_keywords:
            if keyword in message:
                return {
                    'memory_type': 'sentiment_marker',
                    'tier': 3,
                    'content': f"负面情感: {message}",
                    'confidence': 0.6,
                    'source': 'pattern:negative_sentiment',
                    'description': '负面情感模式'
                }
        
        # Check English sentiment
        message_lower = message.lower()
        for keyword in english_positive_keywords:
            if keyword in message_lower:
                return {
                    'memory_type': 'sentiment_marker',
                    'tier': 3,
                    'content': f"Positive sentiment: {message}",
                    'confidence': 0.6,
                    'source': 'pattern:positive_sentiment',
                    'description': '正面情感模式'
                }
        
        for keyword in english_negative_keywords:
            if keyword in message_lower:
                return {
                    'memory_type': 'sentiment_marker',
                    'tier': 3,
                    'content': f"Negative sentiment: {message}",
                    'confidence': 0.6,
                    'source': 'pattern:negative_sentiment',
                    'description': '负面情感模式'
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
