# Phase 3 设计文档

## 1. 设计概述

本设计文档描述了记忆分类引擎（Memory Classification Engine）Phase 3阶段的实现方案，主要包括语义推断层的实现、语义理解增强和智能记忆管理。设计目标是在保持系统高性能和轻量级的前提下，提升系统的智能性和准确性。

## 2. 架构设计

### 2.1 系统架构

系统架构保持不变，仍然采用4层存储架构和3层判断管道：
- **存储架构**：
  - Tier 1: 工作记忆（Working Memory）
  - Tier 2: 短期记忆（Short-term Memory）
  - Tier 3: 情景记忆（Episodic Memory）
  - Tier 4: 语义记忆（Semantic Memory）

- **判断管道**：
  - Layer 1: 规则匹配层（Rule Matching Layer）
  - Layer 2: 结构分析层（Structure Analysis Layer）
  - Layer 3: 语义推断层（Semantic Inference Layer）

### 2.2 模块设计

#### 2.2.1 语义推断层

- 实现基于LLM的语义分析
- 支持多种LLM模型，包括本地模型和API模型
- 实现成本控制机制，避免过度使用LLM
- 设计并优化分类Prompt，提高分类准确率

#### 2.2.2 语义理解增强

- 实现基于语义的记忆分类
- 支持上下文理解，考虑对话历史进行分类
- 实现多语言支持，处理不同语言的输入
- 支持复杂意图识别，理解用户的深层需求

#### 2.2.3 智能记忆管理

- 实现基于语义的记忆关联
- 实现记忆权重的语义调整
- 实现记忆压缩的语义优化
- 实现基于语义的记忆检索

## 3. 详细设计

### 3.1 语义推断层实现

创建`src/memory_classification_engine/layers/semantic_classifier.py`：

```python
class SemanticClassifier:
    def __init__(self, config):
        self.config = config
        self.llm_enabled = self.config.get('llm.enabled', False)
        self.llm_api_key = self.config.get('llm.api_key', '')
        self.llm_model = self.config.get('llm.model', 'glm-4-plus')
        self.llm_temperature = self.config.get('llm.temperature', 0.3)
        self.llm_max_tokens = self.config.get('llm.max_tokens', 500)
        self.llm_timeout = self.config.get('llm.timeout', 30)
        
        # 初始化LLM客户端
        self.llm_client = self._init_llm_client()
        
        # 分类Prompt模板
        self.classification_prompt = """
        You are a memory classification assistant. Your task is to classify the given message into one of the following memory types:
        
        1. user_preference: User's explicitly expressed preferences, habits, and style requirements
        2. correction: User's correction of AI's judgment or output
        3. fact_declaration: User's statements about themselves or business facts
        4. decision: Clear conclusions or choices reached in the conversation
        5. relationship: Information about relationships between people, teams, and organizations
        6. task_pattern: Repeated task types and their processing methods
        7. sentiment_marker: User's explicit emotional tendency towards a topic
        
        Please also determine the appropriate memory tier for storage:
        - Tier 2: Procedural Memory (user_preference, task_pattern)
        - Tier 3: Episodic Memory (correction, decision, sentiment_marker)
        - Tier 4: Semantic Memory (fact_declaration, relationship)
        
        Message: {message}
        Context: {context}
        
        Please return your classification in JSON format with the following fields:
        - memory_type: The classified memory type
        - tier: The appropriate memory tier
        - confidence: A float between 0 and 1 indicating your confidence in the classification
        - reason: A brief explanation of your classification
        """
    
    def _init_llm_client(self):
        """初始化LLM客户端"""
        if not self.llm_enabled:
            return None
        
        # 这里可以根据配置初始化不同的LLM客户端
        # 例如：OpenAI, GLM, Ollama等
        try:
            # 尝试导入并初始化GLM客户端
            from zhipuai import ZhipuAI
            if self.llm_api_key:
                return ZhipuAI(api_key=self.llm_api_key)
        except ImportError:
            pass
        
        return None
    
    def classify(self, message, context=None):
        """使用LLM进行语义分类"""
        if not self.llm_enabled or not self.llm_client:
            return None
        
        try:
            # 构建Prompt
            prompt = self.classification_prompt.format(
                message=message,
                context=context or ""
            )
            
            # 调用LLM
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens,
                timeout=self.llm_timeout
            )
            
            # 解析响应
            content = response.choices[0].message.content
            import json
            result = json.loads(content)
            
            return result
        except Exception as e:
            logger.error(f"Semantic classification failed: {e}")
            return None
    
    def should_use_llm(self, message, context=None):
        """判断是否应该使用LLM进行分类"""
        # 这里可以实现成本控制逻辑
        # 例如：只有当规则匹配和结构分析都失败时才使用LLM
        return True
```

### 3.2 语义理解增强

创建`src/memory_classification_engine/utils/semantic.py`：

```python
class SemanticUtility:
    def __init__(self, config):
        self.config = config
        self.embedding_model = self._init_embedding_model()
    
    def _init_embedding_model(self):
        """初始化嵌入模型"""
        try:
            # 尝试使用sentence-transformers
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback semantic analysis")
            return None
    
    def calculate_similarity(self, text1, text2):
        """计算两个文本的语义相似度"""
        if not self.embedding_model:
            # 回退到简单的字符串相似度
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1, text2).ratio()
        
        try:
            # 使用嵌入模型计算相似度
            embeddings = self.embedding_model.encode([text1, text2])
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return similarity
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            # 回退到简单的字符串相似度
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1, text2).ratio()
    
    def extract_keywords(self, text):
        """提取文本的关键词"""
        try:
            # 使用NLTK或spaCy提取关键词
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from collections import Counter
            
            # 下载必要的资源
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # 分词
            tokens = word_tokenize(text.lower())
            
            # 过滤停用词
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
            
            # 计算词频
            word_counts = Counter(filtered_tokens)
            
            # 返回前5个关键词
            return [word for word, _ in word_counts.most_common(5)]
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def detect_language(self, text):
        """检测文本的语言"""
        try:
            import langdetect
            return langdetect.detect(text)
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'
```

### 3.3 智能记忆管理

更新`src/memory_classification_engine/utils/memory_association.py`：

```python
class MemoryAssociationManager:
    def __init__(self, config):
        self.config = config
        self.associations = {}
        from memory_classification_engine.utils.semantic import semantic_utility
        self.semantic_utility = semantic_utility
    
    def update_memory_associations(self, memory, all_memories):
        """更新记忆的关联关系"""
        memory_id = memory.get('id')
        if not memory_id:
            return
        
        memory_content = memory.get('content', '')
        if not memory_content:
            return
        
        # 计算与其他记忆的语义相似度
        associations = []
        for other_memory in all_memories:
            other_id = other_memory.get('id')
            if other_id == memory_id:
                continue
            
            other_content = other_memory.get('content', '')
            if not other_content:
                continue
            
            # 计算语义相似度
            similarity = self.semantic_utility.calculate_similarity(memory_content, other_content)
            
            # 只保留相似度大于0.6的关联
            if similarity > 0.6:
                associations.append({
                    'target_id': other_id,
                    'similarity': similarity,
                    'created_at': get_current_time()
                })
        
        # 按相似度排序
        associations.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 限制关联数量
        associations = associations[:10]
        
        # 存储关联关系
        self.associations[memory_id] = associations
    
    def get_associations(self, memory_id, min_similarity=0.6, limit=5):
        """获取记忆的关联关系"""
        associations = self.associations.get(memory_id, [])
        
        # 过滤相似度低于阈值的关联
        filtered_associations = [assoc for assoc in associations if assoc['similarity'] >= min_similarity]
        
        # 限制返回数量
        return filtered_associations[:limit]
```

### 3.4 核心引擎集成

更新`src/memory_classification_engine/engine.py`，集成语义推断层：

```python
def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process a message and classify memory."""
    start_time = time.time()
    
    # 快速路径：如果消息为空，直接返回
    if not message or not message.strip():
        duration = time.time() - start_time
        return {
            'message': message,
            'matches': [],
            'plugin_results': {},
            'working_memory_size': len(self.working_memory),
            'processing_time': duration,
            'tenant_id': 'default',
            'language': 'unknown',
            'language_confidence': 0.0
        }
    
    # 检查是否需要运行归档（异步以避免阻塞主流程）
    threading.Thread(target=self._check_archive_time).start()
    
    # 步骤1：将消息添加到工作记忆
    self._add_to_working_memory(message)
    
    # 步骤2：获取或创建租户
    tenant_id = context.get('tenant_id') if context else None
    tenant = None
    
    if tenant_id:
        tenant = self.tenant_manager.get_tenant(tenant_id)
    
    if not tenant:
        tenant_id = tenant_id or 'default'
        tenant = self.tenant_manager.create_tenant(
            tenant_id,
            f"Default Tenant {tenant_id}",
            'personal',
            user_id=tenant_id
        )
    
    # 步骤3：检测语言
    language, lang_confidence = language_manager.detect_language(message)
    
    # 步骤4：检查访问控制
    user_id = context.get('user_id') if context else tenant_id
    if not self.access_control_manager.check_permission(user_id, 'memory', 'write'):
        self.audit_manager.log(user_id, 'access_denied', 'process_message', {'message': 'Access denied'})
        return {
            'message': message,
            'matches': [],
            'plugin_results': {},
            'working_memory_size': len(self.working_memory),
            'processing_time': time.time() - start_time,
            'tenant_id': tenant.tenant_id,
            'language': language,
            'language_confidence': lang_confidence,
            'error': 'Access denied'
        }
    
    # 步骤5：通过插件处理消息
    plugin_results = self.plugin_manager.process_message(message, context)
    
    # 步骤6：通过管道分类（委托给ClassificationPipeline）
    matches = self.classification_pipeline.classify_with_defaults(message, language, context)
    
    # 步骤7：去重匹配（委托给DeduplicationService）
    unique_matches = self.deduplication_service.deduplicate(matches)
    
    # 步骤8：批量存储记忆以减少I/O操作
    stored_memories = []
    batch_memories = []
    
    for match in unique_matches:
        # 生成记忆ID
        memory_id = generate_memory_id()
        match['id'] = memory_id
        
        # 添加上下文（如果提供）
        if context:
            match['context'] = context.get('conversation_id', '')
            # 限制对话历史以减少内存使用
            conversation_history = context.get('conversation_history', [])
            if len(conversation_history) > 10:
                match['conversation_history'] = conversation_history[-10:]
            else:
                match['conversation_history'] = conversation_history
        
        # 添加租户信息
        match['tenant_id'] = tenant.tenant_id
        
        # 添加语言信息
        match['language'] = language
        match['language_confidence'] = lang_confidence
        
        # 规范化memory_type字段
        if 'memory_type' in match:
            match['type'] = match['memory_type']
        if 'type' in match and 'memory_type' not in match:
            match['memory_type'] = match['type']
        
        # 通过插件处理记忆
        processed_match = self.plugin_manager.process_memory(match)
        
        # 添加创建者信息
        processed_match['created_by'] = user_id
        
        # 分析敏感度
        sensitivity_level = self.sensitivity_analyzer.analyze_memory_sensitivity(processed_match)
        processed_match['sensitivity_level'] = sensitivity_level
        
        # 设置可见性（默认为private）
        processed_match['visibility'] = 'private'
        
        # 加密敏感数据（如果需要）
        if self.encryption_manager.is_sensitive_data(str(processed_match)):
            # 简化处理，暂时不加密，因为需要密钥
            stored_memories.append(processed_match)
            batch_memories.append(processed_match)
        else:
            stored_memories.append(processed_match)
            batch_memories.append(processed_match)
    
    # 批量存储记忆（委托给StorageCoordinator）
    if batch_memories:
        self.storage_coordinator.store_memories_batch(batch_memories)
        
        # 添加到租户的记忆列表
        for memory in batch_memories:
            tenant.add_memory(memory)
        
        # 添加到分布式同步队列
        if self.distributed_manager:
            for memory in batch_memories:
                sync_item = {
                    'type': 'memory_add',
                    'memory': memory,
                    'timestamp': get_current_time()
                }
                self.distributed_manager.add_sync_item(sync_item)
    
    # 构建关联（异步）
    if stored_memories:
        self._build_associations_async(stored_memories, context)
    
    # 选择性清除缓存而不是完全清除
    if stored_memories:
        # 通过清除整个缓存来使相关缓存键失效
        # SmartCache没有删除方法，所以我们将清除缓存
        self.cache.clear()
    
    # 记录性能指标
    duration = time.time() - start_time
    self.performance_monitor.record_response_time('process_message', duration)
    self.performance_monitor.increment_throughput('messages_processed')
    self.performance_monitor.log_metrics()
    
    # 记录操作
    self.audit_manager.log(user_id, 'success', 'process_message', {
        'message_length': len(message),
        'matches_count': len(stored_memories),
        'processing_time': duration,
        'tenant_id': tenant.tenant_id
    })
    
    return {
        'message': message,
        'matches': stored_memories,
        'plugin_results': plugin_results,
        'working_memory_size': len(self.working_memory),
        'processing_time': duration,
        'tenant_id': tenant.tenant_id,
        'language': language,
        'language_confidence': lang_confidence
    }
```

### 3.5 分类管道集成

更新`src/memory_classification_engine/coordinators/classification_pipeline.py`，集成语义推断层：

```python
def classify_with_defaults(self, message, language='en', context=None):
    """使用默认设置进行分类"""
    # 步骤1：规则匹配层
    rule_matches = self.rule_matcher.match(message, context)
    if rule_matches:
        return rule_matches
    
    # 步骤2：结构分析层
    pattern_matches = self.pattern_analyzer.analyze(message, context)
    if pattern_matches:
        return pattern_matches
    
    # 步骤3：语义推断层
    semantic_matches = self.semantic_classifier.classify(message, context)
    if semantic_matches:
        # 转换为匹配格式
        return [{
            'memory_type': semantic_matches['memory_type'],
            'tier': semantic_matches['tier'],
            'content': message,
            'confidence': semantic_matches['confidence'],
            'source': 'semantic'
        }]
    
    # 如果所有层都失败，返回空列表
    return []
```

## 4. 测试设计

### 4.1 单元测试

- 测试语义推断层
- 测试语义理解增强
- 测试智能记忆管理
- 测试核心引擎集成

### 4.2 集成测试

- 测试语义推断层与规则匹配层的集成
- 测试语义推断层与结构分析层的集成
- 测试语义推断层与存储层的集成

### 4.3 性能测试

- 测试语义推断的性能
- 测试语义理解的性能
- 测试智能记忆管理的性能
- 测试整体系统的性能

## 5. 实施计划

1. 实现语义推断层
2. 实现语义理解增强
3. 实现智能记忆管理
4. 更新核心引擎，集成新功能
5. 编写单元测试和集成测试
6. 运行性能测试
7. 更新文档和README
8. 提交到Git

## 6. 风险评估

- **性能风险**：语义推断可能会增加系统响应时间
- **成本风险**：使用LLM API可能会产生额外成本
- **兼容性风险**：新功能可能会影响现有功能
- **实现风险**：语义理解的准确性可能难以保证

## 7. 缓解措施

- 优化语义推断算法，确保性能
- 实现成本控制机制，避免过度使用LLM
- 保持向后兼容性，确保现有功能不受影响
- 采用模块化设计，确保逻辑清晰可维护
- 优先使用本地模型，减少API调用成本
