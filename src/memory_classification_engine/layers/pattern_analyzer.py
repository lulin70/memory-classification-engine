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
        self.location_patterns = {}
    
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

        if message is None:
            return patterns

        from memory_classification_engine.utils.confirmation import is_confirmation, has_confirmation_context
        confirmation_with_context = has_confirmation_context(context) and is_confirmation(message)

        if self._is_noise(message) and not confirmation_with_context:
            return patterns

        # Append to message history
        self.message_history.append(message)
        if len(self.message_history) > 10:
            self.message_history.pop(0)

        # Detect language (with fallback)
        try:
            language, _ = language_manager.detect_language(message)
        except Exception:
            language = 'en'

        # Run all detectors (Phase B Fix #4: task/decision BEFORE fact)
        if execution_context:
            feedback = self._detect_execution_feedback_pattern(message, execution_context, language)
            if feedback:
                feedback['language'] = language
                patterns.append(feedback)

        from memory_classification_engine.utils.confirmation import is_confirmation, has_confirmation_context
        if has_confirmation_context(context) and is_confirmation(message):
            ai_reply = context.get('ai_reply', '')
            from memory_classification_engine.utils.confirmation import summarize_context
            ai_summary = summarize_context(ai_reply)
            patterns.append({
                'memory_type': 'decision',
                'type': 'decision',
                'content': f'确认: {ai_summary}',
                'confidence': 0.85,
                'tier': 3,
                'source_layer': 'pattern_analyzer',
                'reasoning': 'User confirmation of AI suggestion',
                'suggested_action': 'store',
                'context_source': 'ai_reply',
                'original_user_message': message,
                'language': language,
            })
            return patterns

        for detector_name, detector_func in [
            ('correction', self._detect_correction_pattern),  # V4-02: correction first
            ('sentiment', self._detect_sentiment_pattern),    # V4-05: sentiment before task
            ('task', self._detect_task_pattern),           # Phase B: before fact
            ('decision', self._detect_decision_pattern),     # Phase B: before fact
            ('preference', self._detect_preference_pattern),
            ('relationship', self._detect_relationship_pattern),
            ('fact', self._detect_fact_pattern),              # V4-08: fact BEFORE location
            ('location', self._detect_location_pattern),      # Location is weak signal, last
        ]:
            result = detector_func(message, language)
            if result:
                result['language'] = language
                patterns.append(result)

        return patterns

    def _is_noise(self, message: str) -> bool:
        """Detect if message is noise (acknowledgment, chitchat, log, command, question).

        Phase A Fix #1: Critical filtering to achieve TN > 0.
        Covers B1 (acknowledgment), B2 (chitchat), B3 (noise), B4 (question), B5 (instruction).

        Args:
            message: The raw message string.

        Returns:
            True if message should be filtered out (not stored), False otherwise.
        """
        if not message or not message.strip():
            return True

        msg = message.strip()
        msg_lower = msg.lower()

        # --- B1: Acknowledgment patterns (19 cases) ---
        acknowledgment_patterns = [
            r'^ok\.?$', r'^okay\.?$', r'^o\.k\.?$', r'^oki\.?$',
            r'^sure\.?$', r'^yes\.?$', r'^yeah\.?$', r'^yep\.?$', r'^ya$',
            r"^got\s+it\.?$", r'^gotcha\.?$', r'^alright\.?$', r'^alrighty\.?$',
            r'^understood\.?$', r'^noted\.?$', r'^roger\s+that\.?$', r'^copy\s+that\.?$',
            r'^thanks?\.?$', r'^thank\s+you\.?$', r'^thx\.?$', r'^ty\.?$',
            r'^appreciate\s+it\.?$', r'^sounds?\s+(good|great)\.?$',
            r'^alright,?\s+makes?\s+sense\.?$',
            r'^noted,?\s+thanks?.*$', r'^got\s+it,?.*\s+handle',
        ]
        for pattern in acknowledgment_patterns:
            if re.match(pattern, msg_lower, re.IGNORECASE):
                return True

        # Extended acknowledgment with context (e.g., "OK, let me check that")
        if re.match(r'^(ok|okay|sure|alright|got\s+it)[,\s]+', msg_lower) and len(msg) < 40:
            return True

        # --- B2: Chitchat/Social patterns (15 cases) ---
        chitchat_patterns = [
            r'^hi$', r'^hello$', r'^hey$', r'^howdy$',
            r'^nice\s+(weather|day|to\s+meet\s+you)\.?',
            r"^(it'?s\s+)?(raining|sunny|cloudy|hot|cold|warm|snowing).*$",
            r'^(too\s+)?(hot|cold|warm|humid)\s+today\.?',
            r'^(how\s+was\s+your\s+(weekend|day|night))\??$',
            r'^(did\s+you\s+(watch|see|try).*)\??$',
            r'^(happy\s+birthday|congrats|congratulations)',
            r'^(have\s+you\s+tried|seen)\s+(that|this|the)\s+.*\??$',
            r'^(see\s+you|talk\s+later|goodbye|bye|take\s+care)\.?$',
            r'^(interesting|\.\.\.|hmm|oh\s+really|is\s+that\s+so|cool)[\s!]*$',
            r'^what\s+a\s+(beautiful|lovely|nice|great)\s+(day|morning|evening)',
            r'^hmm[,\.]?\s+let\s+me\s+think',
            r'^let\s+me\s+think\s*(about\s+it)?$',
        ]
        for pattern in chitchat_patterns:
            if re.match(pattern, msg_lower, re.IGNORECASE):
                return True

        # --- B3: Technical noise (10 cases) ---
        # Log lines (with or without brackets)
        if re.match(r'^\[(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL)\]', msg):
            return True
        if re.match(r'^(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL)[:\s]', msg):
            return True
        # Timestamp-only messages
        if re.match(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}', msg) and len(msg.split()) <= 4:
            return True

        # Common commands (should be executed, not remembered)
        command_patterns = [
            r'^(npm|pip|conda|cargo|go|gradle|maven|docker|kubectl|git|make|cmake)\s+',
            r'^(cd |ls |cat |echo |rm |cp |mv |mkdir |touch |chmod |chown |grep |find |wget |curl )',
            r'^(python|node|java|ruby|php|bash|sh|zsh|fish)\s+',
        ]
        for pattern in command_patterns:
            if re.match(pattern, msg_lower):
                # EXCEPTION: Messages about language versions or facts are NOT commands
                # e.g., "Python 3.9 is the minimum required version" is a fact, not a command
                fact_indicators = [
                    r'\d+(\.\d+)+',  # Version numbers (3.9, 2.0.0)
                    r'\b(is|are|was|were|has|have)\s+',  # Fact declaration verbs
                    r'\b(supports?|requires?|provides?|includes?)\s+',  # Technical facts
                ]
                if any(re.search(ind, msg_lower) for ind in fact_indicators):
                    continue  # Skip noise filtering - this is a fact about the language
                return True

        # --- B4: Question/Query patterns (10 cases) ---
        # V4-07: Enhanced to cover contractions like "what's", "who's"
        question_starters = [
            r'^(how|what|when|where|why|who|which|can|could|would|is|are|do|does|did)\s+',
            r'^what\'?s\s+',  # "what's the..."
            r'^who\'?s\s+',   # "who's the..."
            r'^where\'?s\s+', # "where's the..."
            r'^how\'?s\s+',   # "how's it..."
        ]
        if any(re.match(p, msg_lower) for p in question_starters):
            # Filter short questions (likely one-off queries, not memory-worthy)
            if len(msg) < 60:
                return True

        # --- B5: Instruction patterns (5 cases) ---
        # Phase C Fix #1 (V4-01): Distinguish immediate commands from workflow rules
        # Commands like "run tests" should be filtered, but workflow rules like
        # "Test after every deployment" contain temporal/frequency context and
        # should be classified as task_pattern, NOT filtered as noise.
        instruction_patterns = [
            r'^(please\s+)?(run|execute|start|launch|deploy|build|test|check|verify)\s+',
            r'^(create|open|send|write|generate|download|install|update|delete|remove)\s+',
            r'^(can\s+you\s+)?(help\s+me\s+)?(show|tell|give|explain|find|search)\s+',
        ]
        for pattern in instruction_patterns:
            if re.match(pattern, msg_lower) and len(msg) < 60:
                # EXCEPTION: Messages with workflow/temporal context are task_pattern, not noise
                workflow_indicators = [
                    r'\bevery\b', r'\balways\b', r'\bbefore\b', r'\bafter\b',
                    r'\bweekly\b', r'\bmonthly\b', r'\bdaily\b', r'\beach\b',
                ]
                if any(re.search(indicator, msg_lower) for indicator in workflow_indicators):
                    continue  # Skip noise filtering - this is a workflow rule
                return True

        # --- C5: Adversarial/anti-memory patterns ---
        # Messages explicitly stating they should NOT be remembered
        adversarial_indicators = [
            r'\bdon\'?t\s+remember\s+(this|it|me)\b',
            r'\bnot\s+(a\s+)?memory\b',
            r'\bjust\s+a\s+test\b',
            r'\bpretend\s+this\s+is\b',
            r'\bignore\s+(this|the\s+above)\b',
            r'\bdefinitely\s+not\s+worth\b',
            r'\bdo\s+not\s+(store|save|remember)\b',
            r'\bthis\s+is\s+(just\s+)?(a\s+)?(test|fake|random)\b',
        ]
        if any(re.search(ind, msg_lower) for ind in adversarial_indicators):
            return True

        # --- Ultra-short messages (< 5 chars likely noise) ---
        if len(msg) < 5 and not re.search(r'[a-z]{3,}', msg_lower):
            return True

        return False

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

        Phase B-3 Fix: Enhanced preference detection.
        Target: Recall from 33% to ≥60%.

        Args:
            message: The message to analyze.
            language: The detected language code.

        Returns:
            A preference pattern if detected, None otherwise.
        """
        # Phase B-3: Strong preference patterns (structured)
        strong_pref_patterns = [
            # Explicit preference statements
            r'\b(i\s+)?(prefer|preference|favor|favour|rather)\b.*\b(over|instead of|to|than|rather than)\b',
            r'\b(use|using|utilizing|adopting|choosing|picking|going with)\b.*\b(over|instead of|rather than|not)\b',

            # Personal style/habit preferences
            r'^(i\s+)?(always|never|generally|typically|usually|normally|consistently)\s+(use|prefer|like|love|hate|avoid|stick to|go for)\b',
            r'\b(my\s+)?(default|standard|convention|practice|habit|rule|policy|preference|style|choice|approach|way)\s+(is|are|will be|has been|should be)\b',

            # Coding/style preferences (context-aware)
            r'\b(when|while|whenever|if)\s+(writing|coding|developing|building|working)\s+\w+,\s*i\s+(always|usually|prefer|like|tend to)\b',
            r'\b(for|in|on|during)\s+\w+.*(i\s+)?(prefer|use|choose|pick|like|stick to|go with)\b',

            # Emotional preference indicators
            r'\b(i\s+)?(really\s+)?(like|love|enjoy|appreciate|admire|adore|hate|dislike|can\'t stand|despise|loathe)\b',
            r'\b(big\s+)?(fan\s+of|supporter of|advocate for|pro-|anti-)\b',
        ]

        message_lower = message.lower()

        for pattern in strong_pref_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return {
                    'memory_type': 'user_preference',
                    'tier': 2,
                    'content': message,
                    'confidence': 0.75,
                    'source': 'pattern:preference_strong',
                    'description': '明确偏好模式'
                }

        # Comment in Chinese removedr
        preference_keywords = language_manager.get_keywords('user_preference', language)

        # 添加更多偏好关键词 (Phase B-3 expansion)
        if language == 'en':
            preference_keywords.extend([
                # Core preference words
                'prefer', 'preference', 'favorite', 'favourite', 'preferred',
                'like', 'love', 'hate', 'dislike', 'enjoy', 'adore',
                # Style/choice words
                'default', 'standard', 'convention', 'style', 'approach', 'choice',
                'habit', 'practice', 'routine', 'ritual', 'rule', 'policy',
                # Frequency-based preference markers
                'always', 'never', 'usually', 'typically', 'normally', 'consistently',
                # Comparative preference
                'over', 'instead of', 'rather than', 'better than', 'worse than',
                # Opinion markers
                'think', 'believe', 'feel', 'find', 'consider', 'opinion', 'view',
            ])
        elif language == 'zh-cn':
            preference_keywords.extend([
                '爱好', '喜好', '偏爱', '最爱的', '喜欢的', '偏好',
                '喜欢', '爱', '讨厌', '不喜欢', '习惯', '通常',
                '总是', '从不', '默认', '标准', '风格', '选择',
                '觉得', '认为', '看法', '观点', '意见',
            ])
        
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

        V4-02 Enhanced: Comprehensive correction detection with 3-tier strategy.
        Tier 1: Explicit correction markers (highest confidence)
        Tier 2: Structural patterns (grammar-based)
        Tier 3: Keyword-based (broadest coverage)

        Args:
            message: The message to analyze.
            language: The detected language code.

        Returns:
            A correction pattern if detected, None otherwise.
        """
        message_lower = message.lower()
        import re

        # === TIER 1: Explicit correction markers (confidence 0.85) ===
        explicit_markers = [
            r'^correction\s*:',                    # "Correction: ..."
            r'^correction$',                        # Just "Correction"
            r'\bscratch\s+that\b',                  # "Scratch that..."
            r'\bforget\s+(about|what|i)\s+(i\s+)?(said|told you)\b',  # "Forget what I said"
            r'\bignore\s+(what|i)\s+(said|told|mentioned)\b',  # "Ignore what I said"
            r'\bnever\s+mind\b',                     # "Never mind..."
            r'\blet\s+me\s+(rephrase|redo|refine|correct|clarify)\b',
            r'\bi\s+(take\s+that\s+back|didn\'t\s+mean\s+that)\b',
            r'\bforget\s+about\b.*\b(instead|rather|better|use|go\s+with)\b',  # "Forget about X, Y instead"
        ]
        for pat in explicit_markers:
            if re.search(pat, message_lower):
                return self._build_correction_result(message, language, 'pattern:correction_explicit', 0.85)

        # === TIER 2: Structural patterns (confidence 0.75) ===
        structural_patterns = [
            # Strong negation + alternative
            r'^(?:no[,\.]?|not\s+|wait[,\.]?\s+|hold\s+on)',
            # Explicit wrong/incorrect statements
            r'(?:that\'s|it\'s|this\s+is)\s+(?:all\s+wrong|wrong|incorrect|not\s+right|not\s+correct|mistaken)',
            # Clarification patterns
            r'^(?:actually|in\s+fact|let\s+me\s+clarify|to\s+be\s+clear|let\s+me\s+be\s+clear)[,\s:]',
            # "Actually is/was" correction pattern
            r'\bactually\s+(is|was)\b',
            # "X is actually Y" correction pattern
            r'\bis\s+actually\b',
            # Replacement patterns
            r'(?:use|try|go\s+with|switch\s+to|change\s+to)\s+(?:this|that|the)\s+(?:one|instead|approach|way|method)',
            # Revert/undo patterns
            r'(?:undo|revert|rollback|cancel|discard|scrap|remove)\s+(?:that|this|the|it)\s',
            # Comparison with preference for other option
            r'(?:\w+\s+is\s+better|prefer\s+\w+\s+instead|rather\s+(?:have|use|go)\s+with)\b.*\b(?:than|over|instead\s+of)\b',
            # Error acknowledgment + fix intent
            r'(?:there\'?s?\s+an?\s+|(?:i\s+)?made\s+a\s+)(?:error|mistake|bug|issue|problem|typo).*\bfix\b',
            # "Not X, Y instead" pattern
            r'\bnot\s+.+,\s*(?:but\s+)?(instead|rather|use|try)\b',
            # "Nope/No" + negation
            r'^(?:nope|no)[,.\s]+(that|it|this)\s+(?:\'?s\s+)?(not\s+)?(right|correct|wrong|what\s+i\s+meant)',
        ]
        for pat in structural_patterns:
            if re.search(pat, message_lower):
                return self._build_correction_result(message, language, 'pattern:correction_structural', 0.75)

        # === TIER 3: Keyword-based detection (confidence 0.65) ===
        strong_correction_keywords = [
            'wrong', 'incorrect', 'mistake', 'error', 'fix it', 'bug in',
            'change our', 'change strategy', 'different approach',
            'should be', 'needs to be', 'actually is', 'supposed to be',
        ]
        if any(kw in message_lower for kw in strong_correction_keywords):
            return self._build_correction_result(message, language, 'pattern:correction_keyword', 0.65)

        return None

    def _build_correction_result(self, message: str, language: str, source: str, confidence: float) -> Dict[str, Any]:
        """Build a standardized correction result."""
        correction_content = message

        if len(self.message_history) >= 2:
            previous_message = self.message_history[-2]
            if language.startswith('zh'):
                correction_content = f"纠正: {message}. 针对: {previous_message}"
            else:
                correction_content = f"Correction: {message}. Referring to: {previous_message}"

        correction_hash = hash(correction_content)
        if correction_hash in self.correction_patterns:
            self.correction_patterns[correction_hash] += 1
        else:
            self.correction_patterns[correction_hash] = 1

        return {
            'memory_type': 'correction',
            'tier': 3,
            'content': correction_content,
            'confidence': confidence,
            'source': source,
            'description': '纠正模式'
        }
    
    def _detect_fact_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect fact declaration patterns.

        V4-04 Enhanced: Balanced 3-tier fact detection.
        Tier 1: Tech terms + structural patterns → conf 0.8
        Tier 2: Quantifiable facts (numbers/dates/locations) → conf 0.7
        Tier 3: General declarative statements → conf 0.6
        """
        if len(message.strip()) < 10:
            return None

        msg_lower = message.lower().strip()

        noise_indicators = ['ok', 'yeah', 'sure', 'thanks', 'nice', 'cool', 'great',
                           'got it', 'sounds good', 'alright', 'understood', 'noted',
                           'interesting', 'hmm', 'oh really', 'pretty']
        if any(indicator in msg_lower for indicator in noise_indicators):
            return None

        import re

        if language.startswith('zh'):
            fact_patterns = [r'(.+)是(.+)', r'(.+)有(.+)', r'(.+)在做(.+)', r'(.+)属于(.+)', r'(.+)位于(.+)']
            for pattern in fact_patterns:
                if re.search(pattern, message):
                    return self._build_fact_result(message)
        else:
            # === TIER 1: Strong technical facts (conf 0.8) ===
            tech_terms = [
                r'\b(api|sdk|http|https|tcp|udp|ip|dns|sql|nosql|graphql|rest|grpc|json|xml|csv)\b',
                r'\b(python|javascript|typescript|java|kotlin|go|rust|c\+\+|ruby|php|bash|shell)\b',
                r'\b(postgresql|mysql|mongodb|redis|elasticsearch|dynamodb|sqlite|supabase|firebase)\b',
                r'\b(docker|kubernetes|aws|gcp|azure|linux|nginx|git|github|ci|cd)\b',
                r'\b(llm|gpt|claude|gemini|llama|rag|vector|embedding|pytorch|tensorflow|mcp)\b',
                r'\b(oauth|jwt|encryption|2fa|mfa|rbac|sso|ssl|tls|api\s+key)\b',
                r'\d+(\.\d+)+', r'\d{4}[-/]\d{2}', r'\b(v?\d+\.\d+)\b',
            ]
            has_tech = any(re.search(t, msg_lower) for t in tech_terms)

            if has_tech:
                tech_patterns = [
                    r'(.+)\s+(?:is|are|was|were|runs?|operates?)\s+(?:the\s+)?(?:minimum|required|default|located|hosted|running|deployed|based)',
                    r'(.+)\s+(?:runs?|operates?|works?)\s+(?:on|in|at|with|using|via)\s+(.+)',
                    r'(.+)\s+(?:supports?|provides?|includes?|contains?|features?)\s+(.+)',
                    r'(.+)\s+(?:requires?|needs?|uses?|utilizes?)\s+(.+)',
                    r'(?:the|our|my|this)\s+(?:api|database|server|system|service|app|endpoint|port|limit|version|config)\s+.+(?:is|are|=)',
                    r'\b\d+\s*(?:employees?|users?|members?|people|teams?|instances?|pods?)\b',
                    r'(.+)\s+(?:is|are|has|was|were)\s+(.+)',
                    r'(.+)\s+(?:status)\s+\d+\s+(?:is|means|for)\s+(.+)',
                    r'(.+)\s+(?:handshake)\s+(?:requires?|needs?|involves?)\s+(.+)',
                    r'(.+)\s+(?:share[s]?\s+a)\s+(.+)',
                    r'(.+)\s+(?:by\s+default)\b',
                ]
                for pat in tech_patterns:
                    if re.search(pat, msg_lower):
                        return self._build_fact_result(message, 0.8, 'pattern:fact_tech')

                if has_tech:
                    return self._build_fact_result(message, 0.75, 'pattern:fact_tech_fallback')

            # === TIER 2: Quantifiable facts (conf 0.7) ===
            quant_indicators = [
                r'\b\d+\s*(?:%|percent|mb|gb|tb|ms|sec|min|hour|day|week|month|year|am|pm|jst|utc)\b',
                r'\b\d+[.,]?\d*\s*(?:employees?|users?|members?|people|teams?|servers?|nodes?|pods?)\b',
                r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?\b',
                r'\b\d{1,2}(?:am|pm|:)\b',
                r'\b(?:shanghai|beijing|tokyo|london|singapore|seoul|bangalore|berlin)\b',
                r'\bus-east-\d|us-west-\d|ap-southeast-\d|eu-west-\d\b',
                r'\$[\d,]+|\d+\s*k\s*\$|\$\d+k\b',
                r'\bv\d+[\.\w]*\b',
            ]
            has_quant = any(re.search(q, msg_lower) for q in quant_indicators)

            if has_quant:
                quant_patterns = [
                    r'(.+)\s+(?:is|are|has|have|was|were)\s+(.+)',
                    r'(.+)\s+(?:ends?|starts?|runs?|lasts?)\s+(?:on|at|in|by|every|each)\s*(.+)?',
                    r'(?:my|our|the|this)\s+(?:office|work|team|standup|sync|meeting|budget|approval)\s+.+',
                    r'.*\b(?:hours?|schedule|time|deadline|budget|limit|rate|cost|price|version)\b.*',
                ]
                for pat in quant_patterns:
                    if re.search(pat, msg_lower):
                        return self._build_fact_result(message, 0.7, 'pattern:fact_quant')

            # === TIER 3: General declarative (conf 0.6), only longer messages ===
            if len(msg_lower) > 25:
                general_patterns = [
                    r'^(?:we|i|our|my|the|this)\s+.+\s+(?:is|are|has|have|supports?|uses?|runs?|requires?)\s+.+',
                    r'.+\s+(?:live[s]?\s+in|work[s]?\s+(?:for|at|on|with)|based?\s+(?:in|on|at)|located?\s+(?:in|at))\s+.+',
                ]
                for pat in general_patterns:
                    if re.search(pat, msg_lower):
                        return self._build_fact_result(message, 0.6, 'pattern:fact_general')

        return None

    def _build_fact_result(self, message: str, confidence: float = 0.7, source: str = 'pattern:fact') -> Dict[str, Any]:
        """Build a standardized fact result."""
        fact_content = message
        fact_hash = hash(fact_content)
        if fact_hash in self.fact_patterns:
            self.fact_patterns[fact_hash] += 1
            if self.fact_patterns[fact_hash] >= 2:
                return {'memory_type': 'fact_declaration', 'tier': 4, 'content': fact_content,
                        'confidence': 0.8, 'source': 'pattern:fact_repeat', 'description': '重复事实模式'}
        else:
            self.fact_patterns[fact_hash] = 1
        return {'memory_type': 'fact_declaration', 'tier': 4, 'content': fact_content,
                'confidence': confidence, 'source': source, 'description': '事实声明模式'}
    
    def _detect_relationship_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect relationship patterns.

        V4-05 Enhanced: 3-tier relationship detection.
        Tier 1: Structural role/dependency patterns (conf 0.8)
        Tier 2: Keyword-based (original, conf 0.7)
        """
        import re
        msg_lower = message.lower().strip()

        if len(msg_lower) < 12:
            return None

        # === TIER 1: Structural patterns ===
        if not language.startswith('zh'):
            # Role patterns (who does what / who is what)
            role_patterns = [
                r'^(\w+)\s+(?:owns?|leads?|manages?|heads?|runs?)\s+(?:the\s+)?(.+)',
                r'(\w+)\s+(?:is|was)\s+(?:our|the|my)\s+(dba|pm|lead|architect|owner|maintainer|contact|expert|specialist)',
                r'(\w+)\s+(?:does|handles?|takes?\s+care\s+of|works?\s+on)\s+(.+)',
                r'(\w+)\s+(?:reports?\s+to|answers?\s+to)\s+(\w+)',
                r'(\w+)\s+(?:is\s+(?:on|in)|belongs?\s+to)\s+(?:the\s+)?(.+)\s+team',
                r'(?:ask|contact|reach(?:\s+out)?\s+to)\s+(\w+)\s+(?:about|for|regarding)',
            ]
            for pat in role_patterns:
                if re.search(pat, msg_lower):
                    return self._build_rel_result(message)

            # Dependency/architecture patterns
            dep_patterns = [
                r'(.+)\s+(?:depends?\s+on|relies?\s+on|uses?|imports?|calls?|invokes?)\s+(.+)',
                r'(.+)\s+(?:which|that)\s+(?:routes?\s+to|calls?|triggers?|publishes?\s+events?\s+(?:to|that))\s+(.+)',
                r'(.+)\s+(?:subscribes?\s+to|listens?\s+to|consumes?|reads?\s+from)\s+(.+)',
                r'(.+)\s+(?:sits?\s+between|connects?\s+|bridges?|links?)\s+(.+)',
                r'(.+)\s+(?:triggers?\s+after|runs?\s+after|starts?\s+when|fires?\s+on)\s+(.+)',
                r'(.+)\s+(?:pushes?\s+to|deploys?\s+to|merges?\s+into|integrates?\s+with)\s+(.+)',
                r'(.+)→(.+)',  # Arrow notation
                r'(.+)\s+->\s*(.+)',  # ASCII arrow
            ]
            for pat in dep_patterns:
                if re.search(pat, msg_lower):
                    return self._build_rel_result(message)

        # === TIER 2: Keyword-based (original) ===
        relationship_keywords = language_manager.get_keywords('relationship', language)
        for keyword in relationship_keywords:
            if keyword in msg_lower:
                return self._build_rel_result(message)

        return None

    def _build_rel_result(self, message: str) -> Dict[str, Any]:
        """Build a standardized relationship result."""
        rel_hash = hash(message)
        if rel_hash in self.relationship_patterns:
            self.relationship_patterns[rel_hash] += 1
            if self.relationship_patterns[rel_hash] >= 2:
                return {'memory_type': 'relationship', 'tier': 4, 'content': message,
                        'confidence': 0.8, 'source': 'pattern:relationship_repeat', 'description': '重复关系模式'}
        else:
            self.relationship_patterns[rel_hash] = 1
        return {'memory_type': 'relationship', 'tier': 4, 'content': message,
                'confidence': 0.75, 'source': 'pattern:relationship', 'description': '关系信息模式'}
    
    def _detect_task_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect task patterns.

        Phase A Fix #3: Enhanced with technical action verbs and structured patterns.
        Target: F1 from 0% to ≥50%.

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
            # Phase A Fix #3: Expanded technical action verbs
            task_keywords.extend([
                # Core development actions
                'implement', 'refactor', 'optimize', 'fix', 'debug', 'resolve',
                'add', 'create', 'build', 'make', 'generate', 'develop', 'write',
                'update', 'upgrade', 'migrate', 'integrate', 'deploy', 'release',
                # Planning & management
                'plan', 'design', 'architect', 'research', 'investigate', 'analyze',
                'review', 'test', 'validate', 'verify', 'check', 'monitor',
                # Need/should (but only in task context - handled by patterns below)
                'need to', 'should', 'must', 'have to', 'require', 'going to',
                # Common task markers
                'todo', 'task', 'action item', 'follow up', 'next step',
            ])
        elif language == 'zh-cn':
            task_keywords.extend([
                '实现', '重构', '优化', '修复', '调试', '解决',
                '添加', '创建', '构建', '制作', '生成', '开发', '编写',
                '更新', '升级', '迁移', '集成', '部署', '发布',
                '计划', '设计', '研究', '调查', '分析',
                '审查', '测试', '验证', '检查', '监控',
                '需要', '应该', '必须', '要', '待办', '下一步',
            ])

        message_lower = message.lower()

        # Phase B-1 Fix: Comprehensive task pattern detection
        # Covers: workflow rules, recurring tasks, personal habits, procedures

        # 1. Structured task patterns (command/planning style)
        structured_task_patterns = [
            r'^(i\s+|we\s+|let\'s\s+)?(need|should|must|have|got)\s+to\s+',
            r'^(todo|task):\s*',
            r'^(please\s+)?(can\s+you\s+)?(help\s+me\s+)?(implement|refactor|fix|add|create|build|write|update)\s+',
            r'^(don(\'t)?\s+)?forget\s+to\s+',
            r'^(remember\s+to\s+|make sure to\s+)',
            r'^(we\'re|we are|i\'m|i am)\s+(going to|planning to|working on)\s+',
        ]

        for pattern in structured_task_patterns:
            if re.match(pattern, message_lower, re.IGNORECASE):
                return {
                    'memory_type': 'task_pattern',
                    'tier': 3,
                    'content': message,
                    'confidence': 0.75,
                    'source': 'pattern:task_structured',
                    'description': '结构化任务模式'
                }

        # 2. Workflow rules & recurring patterns (NEW - Phase B-1)
        # Matches: "Always run linting", "Test after every deploy", "Update dependencies weekly"
        workflow_patterns = [
            # Frequency prefixes: Always, Every time, Each time
            r'^(always|every\s+time|each\s+time|generally|typically|normally|usually)\s+'
            r'(run|test|review|check|verify|update|backup|deploy|build|lint|format|document|validate)\b',

            # Frequency suffixes: ...every [period], ...on [day], ...before/after [event]
            r'\b(run|test|review|check|verify|update|backup|deploy|build|lint|format|document|validate|monitor|analyze|debug|refactor|optimize|migrate|integrate)\b'
            r'\s+(always|every\s+\w+|weekly|monthly|daily|before\s+\w+|after\s+\w+|each\s+\w+|on\s+\w+days?|at\s+\w+)\b',

            # Recurring schedule patterns
            r'^(weekly|monthly|daily|quarterly|annually|yearly)\s+.*\b(retro|meeting|report|sync|standup|review|check|update|deploy|release|backup)\b',
            r'\b(every\s+(morning|afternoon|evening|night|monday|tuesday|wednesday|thursday|friday|saturday|sunday|week|month|quarter|year))\b'
            r'.*\b(i\s+|we\s+)?(check|review|run|test|update|verify|monitor|analyze|send|generate|create|build|deploy)\b',

            # Before/After conditionals (workflow triggers)
            r'^(before|after|when|whenever|once)\s+\w+.*,?\s*(please\s+)?(make sure to|remember to|don\'t forget to|ensure to|verify|check|test|update|run|review)\b',
            r'\b(before|after)\s+(every|each|any|all)\s+\w+.*(run|test|check|review|update|verify|deploy|backup|build)\b',
        ]

        for pattern in workflow_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return {
                    'memory_type': 'task_pattern',
                    'tier': 3,
                    'content': message,
                    'confidence': 0.72,
                    'source': 'pattern:task_workflow',
                    'description': '工作流/重复任务模式'
                }

        # 3. Personal habit patterns (NEW - Phase B-1)
        # Matches: "I check the dashboard every morning", "We do code review on Fridays"
        habit_patterns = [
            r'^(i|we)\s+(always|usually|typically|normally|generally|tend to|like to|try to)\s+'
            r'(check|review|run|test|update|verify|monitor|read|write|build|deploy|start|begin|finish|complete|do)\b',
            r'^(my|our)\s+(routine|habit|practice|workflow|process|schedule|ritual|rule|policy|guideline|standard|procedure)\s+(is|includes|requires|involves|has)\b',
        ]

        for pattern in habit_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return {
                    'memory_type': 'task_pattern',
                    'tier': 3,
                    'content': message,
                    'confidence': 0.70,
                    'source': 'pattern:task_habit',
                    'description': '个人习惯/例行任务模式'
                }

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

        Phase B-2 Fix: Complete rewrite of decision detection.
        Target: Recall from 10% to ≥50%.

        Args:
            message: The message to analyze.
            language: The detected language code.

        Returns:
            A decision pattern if detected, None otherwise.
        """
        # Phase B-2: Strong decision indicators (NOT noise words!)
        strong_decision_patterns = [
            # Explicit decision markers
            r'\b(decision|decided?|choose|chose|chosen|choice|select|selected|selection|pick|picked)\b',
            r'\b(going\s+with|settled?\s+on|opted?\s+for|landed?\s+on|went\s+with)\b',
            r'\b(adopt|adopting|adopted|embrace|embraced|integrate|integrated)\b',

            # Commitment/Agreement markers
            r'\b(agreed?|consensus|unanimous|commit(ted|ting)?|pledge(d|ing)?)\b',
            r'\b(final(ize|ized|ization)|confirm(ed|ation)|approve(d|val)?|sign(ed|ing|off)?)\b',

            # Architecture/Approach decisions
            r'\b(architecture|approach|strategy|plan|pattern|design|solution|stack|framework|library|tool|tech|technology)\s+(is|will be|should be|has been|we(\'re| are))\b',
            r'\b(use|using|utilizing|leveraging|based\s+on|built\s+(with|on|around))\s+\w+\s+(for|as|instead of|over|rather than)\b',

            # Process/Policy decisions
            r'\b(will\s+move|moving|shift(ing)?|chang(e|ing)?)\s+to\b.*\b(monday|tuesday|friday|weekly|monthly|agile|scrum|kanban)\b',
            r'\b(are|is|will be)\s+(mandatory|required|standard|policy|rule|practice|norm|convention|default)\b',
        ]

        message_lower = message.lower()

        for pattern in strong_decision_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return {
                    'memory_type': 'decision',
                    'tier': 2,
                    'content': message,
                    'confidence': 0.75,
                    'source': 'pattern:decision_strong',
                    'description': '明确决策模式'
                }

        # Weaker decision indicators (require context length > 15)
        weak_decision_keywords = [
            'let\'s use', 'let\'s go with', 'let\'s adopt', 'let\'s choose',
            'we should use', 'we could use', 'we might use',
            'i think we should', 'i propose we', 'i suggest we',
            'best option is', 'better to go', 'makes sense to',
            'our approach', 'the plan is', 'the strategy is',
        ]

        if len(message.strip()) > 15:
            for keyword in weak_decision_keywords:
                if keyword in message_lower:
                    return {
                        'memory_type': 'decision',
                        'tier': 3,
                        'content': message,
                        'confidence': 0.65,
                        'source': 'pattern:decision_weak',
                        'description': '弱决策模式'
                    }

        # Legacy support (language-specific keywords - filtered for noise)
        decision_keywords = language_manager.get_keywords('decision', language)

        if language == 'en':
            # Phase B-2: Removed noise words (okay, ok, yes, sure), kept only meaningful ones
            decision_keywords.extend([
                'decide', 'determine', 'conclude', 'resolve', 'finalize',
                'preference', 'verdict', 'ruling', 'judgment',
            ])
        elif language == 'zh-cn':
            decision_keywords.extend([
                '决定', '选定', '确定', '采用', '选用', '敲定',
                '方案', '策略', '架构', '共识', '一致同意',
            ])
        
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

        V4-05 Enhanced: Structural + keyword hybrid detection.
        Tier 1: Strong emotion patterns with intensifiers (conf 0.8)
        Tier 2: Keyword-based (original, conf 0.65)
        """
        import re
        msg_lower = message.lower().strip()

        if len(msg_lower) < 10:
            return None

        # === TIER 1: Structural patterns ===
        if not language.startswith('zh'):
            # Emotion + subject patterns (strong signal)
            strong_emotion_patterns = [
                r'^(?:i\s+)?(?:\'?m|am|was|feel|feeling|get|getting)\s+(?:so\s+|really\s+|very\s+|super\s+)?'
                r'(?:happy|excited|proud|grateful|thrilled|delighted|relieved|impressed'
                r'|sad|angry|upset|frustrated|annoyed|worried|scared|exhausted|tired|bored'
                r'|disappointed|confused|overwhelmed|stressed)\b',
                r'\b(?:i\s+)?(?:love|hate|loathe|detest|enjoy|appreciate|dislike|dread)\s+(?:it|this|that|the\s+\w+)',
                r'^(?:this|the)\s+.+\s+is\s+(?:so\s+|really\s+|absolutely\s+|incredibly\s+)?'
                r'(?:great|awesome|amazing|fantastic|wonderful|terrible|awful|horrible|frustrating|annoying|beautiful)',
                r'\b(amazing|brilliant|outstanding|superb|marvelous|incredible|fantastic)\s+(work|job|effort|team|result|achievement)!',
                r'^\w+\s+work\b.*\b(?:on|for|with)\b',
            ]
            for pat in strong_emotion_patterns:
                if re.search(pat, msg_lower):
                    return self._build_sent_result(message, 0.8)

            # Intensifier + adjective patterns
            if any(intensifier in msg_lower for intensifier in ['so ', 'really ', 'very ', 'super ', 'absolutely ', 'extremely ']):
                adj_indicators = [
                    r'\b(happy|sad|angry|frustrated|annoyed|excited|tired|exhausted|bored|worried|proud|glad|upset)\b',
                    r'\b(great|good|bad|terrible|awful|nice|cool|lovely|horrible|amazing|fantastic|beautiful)\b',
                ]
                if any(re.search(adj, msg_lower) for adj in adj_indicators):
                    return self._build_sent_result(message, 0.75)

        # === TIER 2: Keyword-based (original) ===
        sentiment_keywords = language_manager.get_keywords('sentiment_marker', language)
        if language == 'en':
            sentiment_keywords.extend([
                'great', 'awesome', 'fantastic', 'wonderful', 'excellent', 'amazing',
                'terrible', 'bad', 'horrible', 'awful',
                'love', 'hate', 'dislike', 'enjoy',
                'happy', 'sad', 'angry', 'excited', 'frustrated', 'upset',
                'annoyed', 'bored', 'tired', 'exhausted', 'inspired',
                'proud', 'confident', 'worried', 'scared', 'relaxed',
                'brilliant', 'superb', 'outstanding', 'marvelous',
                'loathe', 'detest', 'disappoint', 'delighted', 'thrilled',
                'depressed', 'irritated', 'panic', 'frighten', 'motivated',
                'beautiful', 'bureaucratic',
            ])
        elif language == 'zh-cn':
            sentiment_keywords.extend([
                '棒', '很棒', '真好', '太好了', '优秀', '惊人',
                '可怕', '糟糕', '恶心', '恐怖',
                '喜欢', '讨厌', '烦', '崩溃', '心碎',
                '开心', '难过', '生气', '激动', '不满', '超赞',
                '无语', '无语了', '太赞了', '绝了', '牛', '牛逼',
                '累', '疲惫', '无聊', '焦虑', '担心', '害怕',
                '自豪', '自信', '放松', '失望', '郁闷', '不爽'
            ])

        for keyword in sentiment_keywords:
            if keyword in msg_lower:
                return self._build_sent_result(message, 0.65)

        return None

    def _build_sent_result(self, message: str, confidence: float = 0.7) -> Dict[str, Any]:
        """Build a standardized sentiment result."""
        content = f"Sentiment: {message}" if not any(c in message for c in '好棒爱喜欢') else f"情感: {message}"
        return {
            'memory_type': 'sentiment_marker',
            'tier': 3,
            'content': content,
            'confidence': confidence,
            'source': 'pattern:sentiment',
            'description': '情感模式'
        }
    
    def _detect_location_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect location patterns.

        V4-08: Restricted to pure location info, not facts containing locations.

        Args:
            message: The message to analyze.
            language: The detected language code.

        Returns:
            A location pattern if detected, None otherwise.
        """
        import re
        msg_lower = message.lower()

        # V4-08: Skip if this looks like a fact/decision/task (those take priority)
        # Location should only match pure location statements like "I'm at the office"
        fact_indicators = [
            r'\b(is|are|was|were|has|have)\s+',  # Fact verbs
            r'\b(supports?|requires?|provides?|includes?)\s+',  # Technical facts
            r'\b(every|always|weekly|monthly|daily)\b',  # Recurring patterns
            r'\b(approval|budget|deadline|schedule|sprint)\b',  # Business facts
            r'\d+(\.\d+)+',  # Version numbers
            r'\b(employees?|users?|members?|teams?)\s+\d+',  # Team facts
            r'\b(we\s+have|our\s+\w+)\s+',  # Organizational facts
            r'\b(runs?|operates?|works?)\s+(on|in|at)\s+',  # Infrastructure facts
            r'\b(latency|throughput|performance|uptime)\b',  # Performance metrics
            r'\b(live[s]?\s+in|work[s]?\s+(for|at|remotely))\b',  # Personal location facts
            r'\b(stands?|meets?|sync)\s+',  # Meeting patterns
            r'\b(ends?|starts?|begins?)\s+(on|at)\s+',  # Schedule facts
            r'\b\d+\s*(employees?|users?|ms|sec|min|hour)\b',  # Quantifiable facts
        ]
        if any(re.search(ind, msg_lower) for ind in fact_indicators):
            return None

        # Location keywords
        location_keywords = {
            'en': ['at', 'in', 'on', 'located', 'place', 'location', 'address'],
            'zh-cn': ['在', '位于', '地址', '地方', '位置']
        }

        keywords = location_keywords.get(language, location_keywords.get('en', []))

        for keyword in keywords:
            if keyword in msg_lower:
                # Check for common location names
                common_locations = {
                    'en': ['park', 'station', 'airport', 'hotel', 'restaurant', 'office', 'building', 'street', 'avenue', 'road'],
                    'zh-cn': ['公园', '车站', '机场', '酒店', '餐厅', '办公室', '大楼', '街道', '大道', '路']
                }
                
                location_terms = common_locations.get(language, common_locations.get('en', []))
                for term in location_terms:
                    if term in msg_lower:
                        location_content = message
                        location_hash = hash(location_content)
                        if location_hash in self.location_patterns:
                            self.location_patterns[location_hash] += 1
                        else:
                            self.location_patterns[location_hash] = 1
                        
                        return {
                            'memory_type': 'location',
                            'tier': 3,
                            'content': location_content,
                            'confidence': 0.7,
                            'source': 'pattern:location',
                            'description': '位置模式'
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
        self.location_patterns = {}
