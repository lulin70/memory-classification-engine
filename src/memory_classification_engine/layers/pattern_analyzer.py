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

        # Handle None message
        if message is None:
            return patterns

        # Phase A Fix #1: Noise filtering (P0-3d) - Early rejection
        if self._is_noise(message):
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

        for detector_name, detector_func in [
            ('preference', self._detect_preference_pattern),
            ('correction', self._detect_correction_pattern),
            ('task', self._detect_task_pattern),           # Phase B: before fact
            ('decision', self._detect_decision_pattern),     # Phase B: before fact
            ('relationship', self._detect_relationship_pattern),
            ('fact', self._detect_fact_pattern),              # Phase B: last (fallback)
            ('sentiment', self._detect_sentiment_pattern),
            ('location', self._detect_location_pattern),
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
        ]
        for pattern in chitchat_patterns:
            if re.match(pattern, msg_lower, re.IGNORECASE):
                return True

        # --- B3: Technical noise (10 cases) ---
        # Log lines
        if re.match(r'^\[(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL)\]', msg):
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
                return True

        # --- B4: Question/Query patterns (10 cases) ---
        if re.match(r'^(how|what|when|where|why|who|which|can|could|would|is|are|do|does|did)\s+', msg_lower):
            # Exclude decision-like questions ("Why did we choose X?" could be context)
            # Only filter pure information-seeking questions < 50 chars
            if len(msg) < 50 and '?' in msg or msg.endswith('?'):
                return True

        # --- B5: Instruction patterns (5 cases) ---
        instruction_patterns = [
            r'^(please\s+)?(run|execute|start|launch|deploy|build|test|check|verify)\s+',
            r'^(create|open|send|write|generate|download|install|update|delete|remove)\s+',
            r'^(can\s+you\s+)?(help\s+me\s+)?(show|tell|give|explain|find|search)\s+',
        ]
        for pattern in instruction_patterns:
            if re.match(pattern, msg_lower) and len(msg) < 60:
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
            # 避免误匹配普通否定词，只添加明确的纠正词
            correction_keywords.extend(['wrong', 'incorrect', 'mistake', 'error', 'fix', 'bug', 'issue', 'problem'])
        elif language == 'zh-cn':
            correction_keywords.extend(['错', '误', '修', '改', '问题', 'bug'])
        
        message_lower = message.lower()

        import re

        found_correction = False
        if not found_correction:
            structural_patterns = [
                r'^(?:no|not|wait|hold on|stop)[,\s]+',
                r'(?:that\'s|it\'s|this is)\s+(?:not\s+)?(?:right|correct|what\s+(?:i|we)\s+(?:want|meant)|what\s+i\s+said)',
                r'(?:actually|in\s+fact|let\s+me\s+clarify|to\s+be\s+clear)[,\s]',
                r'(?:instead|rather|use|try|go\s+with)\s+(?:this|that|the)\s+(?:one|approach|way)',
                r'(?:change|switch|replace|update|modify)\s+(?:to|with|from)',
                r'(?:undo|revert|rollback|cancel|discard|scrap)\s+',
            ]
            for pat in structural_patterns:
                if re.search(pat, message_lower):
                    found_correction = True
                    break

        if found_correction:
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

        Phase A Fix #2: Tightened conditions to reduce FP from 68 to <20.
        Now requires: minimum length, substantive content, factual keywords.

        Args:
            message: The message to analyze.
            language: The detected language code.

        Returns:
            A fact pattern if detected, None otherwise.
        """
        # Phase A Fix #2: Pre-filter to avoid false positives on short/noise messages
        if len(message.strip()) < 15:
            return None

        msg_lower = message.lower().strip()

        # Exclude common non-fact patterns (acknowledgment, chitchat residue)
        noise_indicators = ['ok', 'yeah', 'sure', 'thanks', 'nice', 'cool', 'great',
                           'got it', 'sounds good', 'alright', 'understood', 'noted']
        if any(indicator in msg_lower for indicator in noise_indicators):
            return None

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
            # Phase A Fix #2: Tightened English fact patterns
            # Require factual indicators: numbers, versions, dates, technical terms
            # Phase B Fix #2b: Expanded tech terminology whitelist (QA expert review)
            factual_indicators = [
                # Version/Release patterns
                r'\d+(\.\d+)+',                    # Version numbers (3.9, 2.0.0, 1.23.4)
                r'\d{4}[-/]\d{2}',                # Dates (2024-01, 2026/04)
                r'\b(v?\d+\.\d+)\b',              # Versions (v1.0, 0.2.0)
                r'\b\d+\.\d+\.(x|X|\*)\b',        # Semver ranges (1.2.x)

                # Protocols & Standards
                r'\b(API|SDK|URL|URI|HTTP|HTTPS|FTP|SSH|SSL|TLS|TCP|UDP|IP|DNS|VPN)\b',
                r'\b(SQL|NoSQL|GraphQL|REST|SOAP|RPC|gRPC|WebSocket|MQTT)\b',
                r'\b(JSON|XML|CSV|YAML|TOML|INI|HTML|CSS|SCSS|SASS|LESS)\b',
                r'\b(UTF-8|UTF-16|ASCII|Unicode|Base64|MD5|SHA256|JWT|OAuth|OIDC)\b',

                # Programming Languages (comprehensive)
                r'\b(Python|JavaScript|TypeScript|Java|Kotlin|Scala|Go|Rust|C\+\+|C#|Swift|Objective-C|Ruby|PHP|Perl|R|MATLAB|Lua|Shell|Bash|PowerShell|Zig|Nim|Elixir|Haskell|Clojure|F#|Dart|Julia)\b',
                r'\b(JS|TS|py|rb|go|rs|java|kt|swift|vue|jsx|tsx)\b',  # File extensions as language hints

                # Frontend Frameworks & Libraries
                r'\b(React|Vue|Angular|Svelte|Solid|Qwik|Next\.js|Nuxt|Remix|Astro|Gatsby|Vite|Webpack|Parcel|esbuild|Rollup|Turbopack)\b',
                r'\b(jQuery|Backbone|Ember|Alpine|HTMX|Tailwind|Bootstrap|Bulma|Foundation|Material-UI|Ant Design|Element Plus|Chakra|Shadcn)\b',
                r'\b(Three\.js|Babylon|D3|Chart\.js|ECharts|Plotly|Mapbox|Leaflet|Canvas|WebGL|SVG)\b',

                # Backend Frameworks & Runtimes
                r'\b(Node|Express|Koa|Fastify|Hapi|NestJS|Django|Flask|FastAPI|Spring|SpringBoot|Quarkus|Micronaut|Rails|Sinatra|Laravel|Symfony|Gin|Echo|Fiber|Actix|Axum)\b',
                r'\b(Deno|Bun|Worker|Edge|Cloudflare|Vercel|Netlify|Railway|Render|Fly|Heroku)\b',

                # Data & Databases
                r'\b(PostgreSQL|MySQL|MariaDB|SQLite|MongoDB|Redis|Elasticsearch|Cassandra|DynamoDB|CouchDB|Neo4j|TimescaleDB|CockroachDB|PlanetScale|Supabase|Firebase|Firestore|Realm|RealmDB)\b',
                r'\b(ORM|Prisma|TypeORM|Sequelize|Hibernate|MyBatis|SQLAlchemy|Drizzle|Knex)\b',
                r'\b(Kafka|RabbitMQ|NATS|ZeroMQ|ActiveMQ|SQS|SNS|PubSub|gRPC|Protobuf|Avro|Thrift)\b',

                # DevOps & Infrastructure
                r'\b(Docker|Kubernetes|K8s|Helm|Terraform|Pulumi|Ansible|Chef|Puppet|Jenkins|GitHub Actions|GitLab CI|CircleCI|Travis|ArgoCD|Flux)\b',
                r'\b(AWS|GCP|Azure|OCI|DigitalOcean|Linode|Vultr|Hetzner|Cloudflare|Railway|Vercel|Netlify|Heroku)\b',
                r'\b(EC2|S3|Lambda|ECS|EKS|RDS|DynamoDB|CloudFront|Route53|IAM|VPC|ALB|NLB|SNS|SQS|CloudWatch| Athena|Redshift|EMR|SageMaker|Bedrock)\b',
                r'\b(GCE|GKE|Cloud Run|BigQuery|Dataflow|PubSub|Cloud Storage|Firestore|Vertex AI|AI Platform)\b',
                r'\b(Azure Functions|App Service|AKS|Cosmos DB|Blob Storage|DevOps|AD|Entra ID|Key Vault)\b',
                r'\b(Linux|Ubuntu|Debian|CentOS|Fedora|RHEL|Alpine|Arch|macOS|Windows|WSL|NixOS|FreeBSD|OpenBSD)\b',
                r'\b(Nginx|Apache|Caddy|Traefik|Envoy|HAProxy| Kong|Ambassador|Istio|Linkerd)\b',
                r'\b(Git|GitHub|GitLab|Bitbucket|Gitea|Gitee|SVN|Mercurial|Perforce)\b',
                r'\b(Poetry|pipenv|conda|npm|yarn|pnpm|bun|cargo|composer|maven|gradle|sbt|leiningen|mix|go mod|NuGet)\b',

                # Testing & Quality
                r'\b(Jest|Mocha|Vitest|Pytest|unittest|pytest|RSpec|TestNG|JUnit|PHPUnit|Cypress|Playwright|Puppeteer|Selenium|WebDriver|Detox|Maestro)\b',
                r'\b(CI|CD|TDD|BDD|DDD|SOLID|DRY|KISS|YAGNI|ACID|BASE|CAP|PACELC)\b',
                r'\b(SonarQube|CodeClimate|Coveralls|Codecov|ESLint|Prettier|Stylelint|PMD|Checkstyle|Rubocop|Black|Ruff|Clippy)\b',

                # Architecture Patterns
                r'\b(Microservice|Monolith|Serverless|Event-Driven|CQRS|Event Sourcing|Saga|Outbox|Pattern|Anti-Pattern)\b',
                r'\b(MVC|MVVM|MVP|Clean Architecture|Hexagonal|Onion|Layered|Feature-Sliced|DCI)\b',
                r'\b(Restful|GraphQL|gRPC|WebSocket|SSE|Webhook|Callback|Promise|Async/Await|Observable|Stream|Reactive)\b',
                r'\b(Singleton|Factory|Builder|Adapter|Decorator|Facade|Proxy|Strategy|Observer|Command|Chain of Responsibility|Repository|Unit of Work|Service Locator|Dependency Injection|Inversion of Control)\b',

                # Config & Environment
                r'\b(minimum|maximum|required|limit|threshold|config|default|port|endpoint|host|domain|subnet|CIDR|firewall|load balancer|reverse proxy|CDN|cache)\b',
                r'\b(\.env|dotenv|environment variable|feature flag|A/B test|canary|blue-green|rolling|zero-downtime)\b',

                # AI/ML Terms
                r'\b(LLM|GPT|Claude|Gemini|Llama|Mistral|BERT|Transformer|Attention|RAG|Vector|Embedding|Fine-tuning|LoRA|QLoRA|Prompt|Token|Context Window|Temperature|Top-P|Top-K)\b',
                r'\b(PyTorch|TensorFlow|JAX|ONNX|OpenVINO|TensorRT|vLLM|llama-cpp|Ollama|LangChain|LlamaIndex|Haystack|CrewAI|AutoGen|Semantic Kernel|MCP|Agent|Workflow|Tool|Function Calling)\b',
                r'\b(Pinecone|Weaviate|Qdrant|Milvus|Chroma|Faiss|pgvector|pgembedding|LanceDB|DocArray|Usearch|Hnswlib|Annoy|ScaNN|Vald)\b',

                # Security
                r'\b(OAuth|OIDC|SAML|LDAP|2FA|MFA|RBAC|ABAC|JWT|API Key|Secret|Credential|Encryption|Hashing|Salt|Pepper|AES|RSA|ECDSA|XSS|CSRF|SQLi|XXE|SSRF|IDOR|Rate Limit|WAF|DDoS)\b',
            ]

            has_factual_content = any(re.search(ind, msg_lower) for ind in factual_indicators)

            if not has_factual_content:
                return None

            fact_patterns = [
                r'(.+) is (.+)',
                r'(.+) has (.+)',
                r'(.+) are (.+)',
                r'(.+) was (.+)',
                r'(.+) were (.+)',
                r'(.+) will be (.+)'
            ]

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
            r'\b(will\s+move|moving|shift(ing)?|chang(e|ing)?)\s+to)\b.*\b(monday|tuesday|friday|weekly|monthly|agile|scrum|kanban)\b',
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
            sentiment_keywords.extend([
                'great', 'awesome', 'fantastic', 'wonderful', 'excellent', 'amazing',
                'terrible', 'bad', 'horrible', 'awful',
                'love', 'hate', 'dislike', 'enjoy',
                'happy', 'sad', 'angry', 'excited', 'frustrated', 'upset',
                'annoyed', 'bored', 'tired', 'exhausted', 'inspired',
                'proud', 'confident', 'worried', 'scared', 'relaxed',
                'brilliant', 'superb', 'outstanding', 'marvelous',
                'loathe', 'detest', 'disappoint', 'delighted', 'thrilled',
                'depressed', 'irritated', 'panic', 'frighten', 'motivated'
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
    
    def _detect_location_pattern(self, message: str, language: str) -> Optional[Dict[str, Any]]:
        """Detect location patterns.
        
        Args:
            message: The message to analyze.
            language: The detected language code.
            
        Returns:
            A location pattern if detected, None otherwise.
        """
        # 位置关键词
        location_keywords = {
            'en': ['at', 'in', 'on', 'located', 'place', 'location', 'address'],
            'zh-cn': ['在', '位于', '地址', '地方', '位置']
        }
        
        # 检查语言对应的关键词
        keywords = location_keywords.get(language, location_keywords.get('en', []))
        
        message_lower = message.lower()
        for keyword in keywords:
            if keyword in message_lower:
                # 位置内容
                location_content = message
                
                # 检查是否包含常见地点名称
                common_locations = {
                    'en': ['park', 'station', 'airport', 'hotel', 'restaurant', 'office', 'building', 'street', 'avenue', 'road'],
                    'zh-cn': ['公园', '车站', '机场', '酒店', '餐厅', '办公室', '大楼', '街道', '大道', '路']
                }
                
                location_terms = common_locations.get(language, common_locations.get('en', []))
                for term in location_terms:
                    if term in message_lower:
                        # 生成位置模式
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
