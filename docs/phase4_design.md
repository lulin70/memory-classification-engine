# Phase 4 设计文档

## 1. 设计概述

本设计文档描述了记忆分类引擎（Memory Classification Engine）Phase 4阶段的实现方案，主要包括基于衰减的遗忘机制、系统的进化能力和智能记忆管理增强。设计目标是在保持系统高性能和轻量级的前提下，提升系统的智能化水平和适应性。

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

#### 2.2.1 遗忘机制模块

- 实现基于时间、频率和重要性的加权衰减算法
- 支持记忆的自动遗忘和归档
- 实现记忆的重要性评估
- 支持用户手动调整记忆的重要性

#### 2.2.2 系统进化模块

- 实现基于用户反馈的分类模型优化
- 支持记忆分类规则的自动调整
- 实现记忆权重计算的自适应优化
- 支持系统性能的自动调优

#### 2.2.3 智能记忆管理模块

- 实现记忆的自动压缩和合并
- 支持记忆的分层存储和检索
- 实现记忆的优先级管理
- 支持记忆的批量操作

## 3. 详细设计

### 3.1 遗忘机制模块

创建`src/memory_classification_engine/utils/forgetting.py`：

```python
import time
from typing import Dict, Any, List
from memory_classification_engine.utils.logger import logger

class ForgettingManager:
    def __init__(self, config):
        self.config = config
        self.decay_rate = self.config.get('forgetting.decay_rate', 0.01)
        self.min_weight = self.config.get('forgetting.min_weight', 0.1)
        self.importance_weights = {
            'high': 1.0,
            'medium': 0.7,
            'low': 0.3
        }
    
    def calculate_decay(self, memory, current_time=None):
        """计算记忆的衰减值"""
        if current_time is None:
            current_time = time.time()
        
        # 获取记忆的创建时间和最后访问时间
        created_at = memory.get('created_at', current_time)
        last_accessed = memory.get('last_accessed', created_at)
        
        # 计算时间衰减
        time_since_creation = current_time - created_at
        time_since_access = current_time - last_accessed
        
        # 基础衰减率
        time_decay = 1.0 - (self.decay_rate * time_since_creation / 3600)  # 按小时衰减
        access_decay = 1.0 - (self.decay_rate * time_since_access / 3600)  # 按小时衰减
        
        # 结合时间衰减和访问衰减
        decay = (time_decay * 0.7) + (access_decay * 0.3)
        
        # 应用重要性权重
        importance = memory.get('importance', 'medium')
        importance_weight = self.importance_weights.get(importance, 0.7)
        decay *= importance_weight
        
        # 确保衰减值在合理范围内
        return max(self.min_weight, min(1.0, decay))
    
    def update_memory_weight(self, memory, current_time=None):
        """更新记忆的权重"""
        decay = self.calculate_decay(memory, current_time)
        memory['weight'] = decay
        memory['last_accessed'] = current_time or time.time()
        return memory
    
    def should_forget(self, memory):
        """判断是否应该遗忘记忆"""
        weight = memory.get('weight', 1.0)
        return weight <= self.min_weight
    
    def forget_memory(self, memory):
        """遗忘记忆"""
        # 这里可以实现记忆的归档或删除逻辑
        # 暂时只是标记为已遗忘
        memory['forgotten'] = True
        return memory
    
    def batch_update_weights(self, memories, current_time=None):
        """批量更新记忆的权重"""
        updated_memories = []
        forgotten_memories = []
        
        for memory in memories:
            updated_memory = self.update_memory_weight(memory, current_time)
            if self.should_forget(updated_memory):
                forgotten_memory = self.forget_memory(updated_memory)
                forgotten_memories.append(forgotten_memory)
            else:
                updated_memories.append(updated_memory)
        
        return updated_memories, forgotten_memories
    
    def set_importance(self, memory, importance):
        """设置记忆的重要性"""
        if importance in self.importance_weights:
            memory['importance'] = importance
            return True
        return False
    
    def get_importance_levels(self):
        """获取重要性级别"""
        return list(self.importance_weights.keys())
```

### 3.2 系统进化模块

创建`src/memory_classification_engine/utils/evolution.py`：

```python
from typing import Dict, Any, List
from memory_classification_engine.utils.logger import logger

class EvolutionManager:
    def __init__(self, config):
        self.config = config
        self.feedback_threshold = self.config.get('evolution.feedback_threshold', 5)
        self.rule_adjustment_rate = self.config.get('evolution.rule_adjustment_rate', 0.1)
        self.performance_history = []
    
    def process_feedback(self, memory, feedback):
        """处理用户反馈"""
        # 记录反馈
        if 'feedback' not in memory:
            memory['feedback'] = []
        memory['feedback'].append(feedback)
        
        # 如果反馈达到阈值，调整分类规则
        if len(memory['feedback']) >= self.feedback_threshold:
            self.adjust_classification_rules(memory)
        
        return memory
    
    def adjust_classification_rules(self, memory):
        """调整分类规则"""
        # 这里可以实现基于反馈的规则调整逻辑
        # 暂时只是记录调整
        logger.info(f"Adjusting classification rules for memory: {memory.get('id')}")
        
        # 重置反馈计数
        memory['feedback'] = []
        return memory
    
    def optimize_weight_calculation(self, memories):
        """优化记忆权重计算"""
        # 这里可以实现基于历史数据的权重计算优化
        # 暂时只是返回原始记忆
        return memories
    
    def optimize_performance(self):
        """优化系统性能"""
        # 这里可以实现基于性能指标的系统调优
        # 暂时只是记录性能
        logger.info("Optimizing system performance")
        return True
    
    def record_performance(self, operation, duration):
        """记录性能指标"""
        self.performance_history.append({
            'operation': operation,
            'duration': duration,
            'timestamp': time.time()
        })
        
        # 保持性能历史的大小
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
    
    def get_performance_stats(self):
        """获取性能统计信息"""
        if not self.performance_history:
            return {}
        
        # 计算平均响应时间
        avg_duration = sum(item['duration'] for item in self.performance_history) / len(self.performance_history)
        
        # 按操作类型分组计算
        operation_stats = {}
        for item in self.performance_history:
            operation = item['operation']
            if operation not in operation_stats:
                operation_stats[operation] = []
            operation_stats[operation].append(item['duration'])
        
        for operation, durations in operation_stats.items():
            operation_stats[operation] = {
                'avg': sum(durations) / len(durations),
                'min': min(durations),
                'max': max(durations)
            }
        
        return {
            'average_duration': avg_duration,
            'operation_stats': operation_stats
        }
```

### 3.3 智能记忆管理模块

创建`src/memory_classification_engine/utils/intelligent_memory.py`：

```python
from typing import Dict, Any, List
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.semantic import semantic_utility

class IntelligentMemoryManager:
    def __init__(self, config):
        self.config = config
        self.compression_threshold = self.config.get('memory.compression_threshold', 0.8)
        self.max_batch_size = self.config.get('memory.max_batch_size', 100)
    
    def compress_memories(self, memories):
        """压缩和合并记忆"""
        if len(memories) < 2:
            return memories
        
        # 按记忆类型分组
        memories_by_type = {}
        for memory in memories:
            memory_type = memory.get('memory_type', 'unknown')
            if memory_type not in memories_by_type:
                memories_by_type[memory_type] = []
            memories_by_type[memory_type].append(memory)
        
        compressed_memories = []
        
        # 对每个类型的记忆进行压缩
        for memory_type, type_memories in memories_by_type.items():
            compressed = self._compress_memory_group(type_memories)
            compressed_memories.extend(compressed)
        
        return compressed_memories
    
    def _compress_memory_group(self, memories):
        """压缩一组相似的记忆"""
        if len(memories) < 2:
            return memories
        
        # 计算记忆之间的相似度
        similarities = []
        for i, memory1 in enumerate(memories):
            for j, memory2 in enumerate(memories):
                if i < j:
                    similarity = semantic_utility.calculate_similarity(
                        memory1.get('content', ''),
                        memory2.get('content', '')
                    )
                    similarities.append((i, j, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        # 合并相似的记忆
        merged = set()
        compressed = []
        
        for i, j, similarity in similarities:
            if i not in merged and j not in merged and similarity >= self.compression_threshold:
                # 合并两个记忆
                merged_memory = self._merge_memories(memories[i], memories[j])
                compressed.append(merged_memory)
                merged.add(i)
                merged.add(j)
        
        # 添加未合并的记忆
        for i, memory in enumerate(memories):
            if i not in merged:
                compressed.append(memory)
        
        return compressed
    
    def _merge_memories(self, memory1, memory2):
        """合并两个记忆"""
        # 合并内容
        content1 = memory1.get('content', '')
        content2 = memory2.get('content', '')
        merged_content = f"{content1} {content2}"
        
        # 合并其他属性
        merged_memory = {
            'id': memory1.get('id'),
            'content': merged_content,
            'memory_type': memory1.get('memory_type'),
            'tier': memory1.get('tier'),
            'weight': (memory1.get('weight', 1.0) + memory2.get('weight', 1.0)) / 2,
            'created_at': min(memory1.get('created_at', float('inf')), memory2.get('created_at', float('inf'))),
            'last_accessed': max(memory1.get('last_accessed', 0), memory2.get('last_accessed', 0)),
            'merged_from': [memory1.get('id'), memory2.get('id')]
        }
        
        # 合并其他属性
        for key, value in memory1.items():
            if key not in merged_memory:
                merged_memory[key] = value
        
        return merged_memory
    
    def prioritize_memories(self, memories):
        """对记忆进行优先级排序"""
        # 按权重和最后访问时间排序
        memories.sort(key=lambda x: (x.get('weight', 1.0), x.get('last_accessed', 0)), reverse=True)
        return memories
    
    def batch_operate(self, memories, operation):
        """批量操作记忆"""
        if len(memories) > self.max_batch_size:
            logger.warning(f"Batch size exceeded, processing only {self.max_batch_size} memories")
            memories = memories[:self.max_batch_size]
        
        results = []
        for memory in memories:
            result = operation(memory)
            results.append(result)
        
        return results
    
    def get_memory_statistics(self, memories):
        """获取记忆统计信息"""
        if not memories:
            return {}
        
        # 按类型统计
        type_counts = {}
        for memory in memories:
            memory_type = memory.get('memory_type', 'unknown')
            type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
        
        # 计算平均权重
        avg_weight = sum(memory.get('weight', 1.0) for memory in memories) / len(memories)
        
        # 计算记忆的时间分布
        time_distribution = {}
        for memory in memories:
            created_at = memory.get('created_at', 0)
            hour = time.strftime('%H', time.localtime(created_at))
            time_distribution[hour] = time_distribution.get(hour, 0) + 1
        
        return {
            'total_memories': len(memories),
            'type_counts': type_counts,
            'average_weight': avg_weight,
            'time_distribution': time_distribution
        }
```

### 3.4 核心引擎集成

更新`src/memory_classification_engine/engine.py`，集成遗忘机制和系统进化功能：

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
    
    # 检查是否需要运行遗忘机制（异步以避免阻塞主流程）
    threading.Thread(target=self._run_forgetting).start()
    
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
        
        # 设置重要性（默认为medium）
        processed_match['importance'] = 'medium'
        
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
    
    # 记录性能到进化管理器
    self.evolution_manager.record_performance('process_message', duration)
    
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

# 新增方法

def _run_forgetting(self):
    """运行遗忘机制"""
    try:
        # 获取所有记忆
        all_memories = []
        for tenant in self.tenant_manager.tenants.values():
            all_memories.extend(tenant.memories)
        
        # 更新记忆权重并检查是否需要遗忘
        updated_memories, forgotten_memories = self.forgetting_manager.batch_update_weights(all_memories)
        
        # 处理遗忘的记忆
        for memory in forgotten_memories:
            logger.info(f"Forgetting memory: {memory.get('id')}")
            # 这里可以添加遗忘逻辑，如从存储中删除或归档
    except Exception as e:
        logger.error(f"Error running forgetting mechanism: {e}")

def process_feedback(self, memory_id, feedback):
    """处理用户反馈"""
    # 查找记忆
    memory = None
    for tenant in self.tenant_manager.tenants.values():
        for m in tenant.memories:
            if m.get('id') == memory_id:
                memory = m
                break
        if memory:
            break
    
    if not memory:
        return {'error': 'Memory not found'}
    
    # 处理反馈
    updated_memory = self.evolution_manager.process_feedback(memory, feedback)
    
    # 更新存储
    self.storage_coordinator.update_memory(updated_memory)
    
    return {'success': True, 'memory': updated_memory}

def optimize_system(self):
    """优化系统"""
    # 优化记忆权重计算
    all_memories = []
    for tenant in self.tenant_manager.tenants.values():
        all_memories.extend(tenant.memories)
    
    optimized_memories = self.evolution_manager.optimize_weight_calculation(all_memories)
    
    # 批量更新记忆
    for memory in optimized_memories:
        self.storage_coordinator.update_memory(memory)
    
    # 优化系统性能
    self.evolution_manager.optimize_performance()
    
    return {'success': True, 'optimized_count': len(optimized_memories)}

def compress_memories(self, tenant_id):
    """压缩记忆"""
    # 获取租户
    tenant = self.tenant_manager.get_tenant(tenant_id)
    if not tenant:
        return {'error': 'Tenant not found'}
    
    # 压缩记忆
    compressed_memories = self.intelligent_memory_manager.compress_memories(tenant.memories)
    
    # 更新存储
    for memory in compressed_memories:
        self.storage_coordinator.update_memory(memory)
    
    # 更新租户的记忆列表
    tenant.memories = compressed_memories
    
    return {'success': True, 'compressed_count': len(compressed_memories)}
```

### 3.5 初始化新模块

更新`src/memory_classification_engine/engine.py`的`__init__`方法，初始化新模块：

```python
def __init__(self, config_path: str = None):
    """Initialize the Memory Classification Engine."""
    # 初始化配置
    self.config = ConfigManager(config_path)
    
    # 初始化日志
    self.logger = logger
    
    # 初始化存储协调器
    self.storage_coordinator = StorageCoordinator(self.config)
    
    # 初始化租户管理
    self.tenant_manager = TenantManager(self.config)
    
    # 初始化工作记忆
    self.working_memory = []
    self.working_memory_size = self.config.get('working_memory.size', 50)
    
    # 初始化缓存
    cache_config = self.config.get('cache', {})
    self.cache = SmartCache(cache_config)
    
    # 初始化插件管理器
    self.plugin_manager = PluginManager(self.config)
    
    # 初始化分类管道
    self.classification_pipeline = ClassificationPipeline(self.config)
    
    # 初始化去重服务
    self.deduplication_service = DeduplicationService(self.config)
    
    # 初始化分布式管理器
    self.distributed_manager = None
    if self.config.get('distributed.enabled', False):
        try:
            from memory_classification_engine.coordinators.distributed_manager import DistributedManager
            self.distributed_manager = DistributedManager(self.config)
        except Exception as e:
            self.logger.warning(f"Failed to initialize distributed manager: {e}")
    
    # 初始化隐私保护模块
    self.encryption_manager = encryption_manager
    self.access_control_manager = access_control_manager
    self.privacy_manager = privacy_manager
    self.compliance_manager = compliance_manager
    self.audit_manager = audit_manager
    
    # 初始化隐私模块 for Phase 2
    self.sensitivity_analyzer = SensitivityAnalyzer(self.config)
    self.visibility_manager = VisibilityManager(self.config)
    self.scenario_validator = ScenarioValidator(self.config)
    
    # 初始化遗忘机制和系统进化模块 for Phase 4
    from memory_classification_engine.utils.forgetting import ForgettingManager
    from memory_classification_engine.utils.evolution import EvolutionManager
    from memory_classification_engine.utils.intelligent_memory import IntelligentMemoryManager
    
    self.forgetting_manager = ForgettingManager(self.config)
    self.evolution_manager = EvolutionManager(self.config)
    self.intelligent_memory_manager = IntelligentMemoryManager(self.config)
    
    # 初始化性能监控
    self.performance_monitor = PerformanceMonitor(self.config)
    
    # 启动后台进程
    self._start_background_processes()
    
    self.logger.info("Memory Classification Engine initialized")
```

## 4. 测试设计

### 4.1 单元测试

- 测试遗忘机制模块
- 测试系统进化模块
- 测试智能记忆管理模块
- 测试核心引擎集成

### 4.2 集成测试

- 测试遗忘机制与存储层的集成
- 测试系统进化与分类管道的集成
- 测试智能记忆管理与存储层的集成

### 4.3 性能测试

- 测试遗忘机制的性能
- 测试系统进化的性能
- 测试智能记忆管理的性能
- 测试整体系统的性能

## 5. 实施计划

1. 实现遗忘机制模块
2. 实现系统进化模块
3. 实现智能记忆管理模块
4. 更新核心引擎，集成新功能
5. 编写单元测试和集成测试
6. 运行性能测试
7. 更新文档和README
8. 提交到Git

## 6. 风险评估

- **性能风险**：遗忘机制和系统进化可能会增加系统响应时间
- **兼容性风险**：新功能可能会影响现有功能
- **实现风险**：系统进化的准确性可能难以保证

## 7. 缓解措施

- 优化遗忘机制和系统进化算法，确保性能
- 保持向后兼容性，确保现有功能不受影响
- 采用模块化设计，确保逻辑清晰可维护
- 优先使用本地计算，减少API调用成本
