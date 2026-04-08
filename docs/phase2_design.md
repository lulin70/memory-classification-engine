# Phase 2 设计文档

## 1. 设计概述

本设计文档描述了记忆分类引擎（Memory Classification Engine）Phase 2阶段的实现方案，主要包括记忆的可见性标签、敏感度分级和引用场景校验功能。设计目标是在保持系统高性能和轻量级的前提下，增强系统的隐私保护能力。

## 2. 架构设计

### 2.1 系统架构

系统架构保持不变，仍然采用4层存储架构：
- Tier 1: 工作记忆（Working Memory）
- Tier 2: 短期记忆（Short-term Memory）
- Tier 3: 情景记忆（Episodic Memory）
- Tier 4: 语义记忆（Semantic Memory）

### 2.2 模块设计

#### 2.2.1 记忆元数据扩展

在记忆元数据中添加以下字段：
- `visibility`: 可见性标签，取值为private、team、org
- `sensitivity_level`: 敏感度级别，取值为low、medium、high
- `owner`: 记忆所有者
- `created_by`: 创建者
- `updated_at`: 更新时间

#### 2.2.2 敏感度分析模块

- 实现基于内容的敏感度分析
- 使用规则引擎和简单的NLP技术判断内容敏感度
- 支持自定义敏感度规则

#### 2.2.3 可见性管理模块

- 实现可见性标签的管理和验证
- 支持可见性升级的授权流程
- 确保检索时的可见性过滤

#### 2.2.4 引用场景校验模块

- 实现场景识别和记忆适用性判断
- 基于规则的场景校验
- 支持自定义场景规则

## 3. 详细设计

### 3.1 记忆元数据扩展

在`src/memory_classification_engine/storage/base.py`中扩展记忆元数据结构：

```python
class Memory:
    def __init__(self, content, memory_type, tier, visibility="private", sensitivity_level="low", owner=None, created_by=None):
        self.id = str(uuid.uuid4())
        self.content = content
        self.memory_type = memory_type
        self.tier = tier
        self.visibility = visibility
        self.sensitivity_level = sensitivity_level
        self.owner = owner
        self.created_by = created_by
        self.created_at = time.time()
        self.updated_at = time.time()
        self.weight = 1.0
        self.associations = []
```

### 3.2 敏感度分析模块

创建`src/memory_classification_engine/privacy/sensitivity_analyzer.py`：

```python
class SensitivityAnalyzer:
    def __init__(self, config):
        self.config = config
        self.sensitive_patterns = {
            "high": [
                r"credit card", r"social security", r"password",
                r"bank account", r"medical", r"health"
            ],
            "medium": [
                r"address", r"phone number", r"email",
                r"birthday", r"salary", r"income"
            ]
        }
    
    def analyze_sensitivity(self, content):
        """分析内容的敏感度"""
        content_lower = content.lower()
        
        # 检查高敏感度模式
        for pattern in self.sensitive_patterns["high"]:
            if re.search(pattern, content_lower):
                return "high"
        
        # 检查中敏感度模式
        for pattern in self.sensitive_patterns["medium"]:
            if re.search(pattern, content_lower):
                return "medium"
        
        # 默认为低敏感度
        return "low"
```

### 3.3 可见性管理模块

创建`src/memory_classification_engine/privacy/visibility_manager.py`：

```python
class VisibilityManager:
    def __init__(self, config):
        self.config = config
    
    def validate_visibility(self, visibility):
        """验证可见性标签是否有效"""
        valid_visibilities = ["private", "team", "org"]
        return visibility in valid_visibilities
    
    def can_access(self, user_id, memory):
        """判断用户是否有权访问记忆"""
        if memory.visibility == "private":
            return user_id == memory.created_by
        elif memory.visibility == "team":
            # 这里需要实现团队成员判断逻辑
            return True  # 简化处理
        elif memory.visibility == "org":
            return True
        return False
    
    def upgrade_visibility(self, memory, new_visibility, user_id):
        """升级记忆的可见性"""
        if not self.validate_visibility(new_visibility):
            return False
        
        # 只有创建者可以升级可见性
        if user_id != memory.created_by:
            return False
        
        # 只能升级，不能降级
        visibility_levels = {"private": 0, "team": 1, "org": 2}
        if visibility_levels[new_visibility] <= visibility_levels[memory.visibility]:
            return False
        
        memory.visibility = new_visibility
        memory.updated_at = time.time()
        return True
```

### 3.4 引用场景校验模块

创建`src/memory_classification_engine/privacy/scenario_validator.py`：

```python
class ScenarioValidator:
    def __init__(self, config):
        self.config = config
        self.scenario_rules = {
            "external_output": {
                "max_sensitivity": "medium"
            },
            "internal_analysis": {
                "max_sensitivity": "high"
            },
            "personal_assistant": {
                "max_sensitivity": "high"
            }
        }
    
    def validate_scenario(self, memories, scenario):
        """校验记忆是否适合当前场景"""
        if scenario not in self.scenario_rules:
            return memories
        
        rule = self.scenario_rules[scenario]
        max_sensitivity = rule.get("max_sensitivity", "high")
        
        sensitivity_levels = {"low": 0, "medium": 1, "high": 2}
        max_level = sensitivity_levels[max_sensitivity]
        
        # 过滤掉超出敏感度限制的记忆
        filtered_memories = []
        for memory in memories:
            memory_level = sensitivity_levels.get(memory.sensitivity_level, 0)
            if memory_level <= max_level:
                filtered_memories.append(memory)
        
        return filtered_memories
```

### 3.5 存储层更新

更新存储层，支持新的元数据字段：

1. 在`src/memory_classification_engine/storage/tier2.py`中更新存储和检索逻辑
2. 在`src/memory_classification_engine/storage/tier3.py`中更新存储和检索逻辑
3. 在`src/memory_classification_engine/storage/tier4.py`中更新存储和检索逻辑

### 3.6 核心引擎集成

更新核心引擎，集成新的隐私保护功能：

1. 在`src/memory_classification_engine/engine.py`中添加敏感度分析和可见性管理
2. 在记忆创建时自动分析敏感度
3. 在记忆检索时进行可见性过滤和场景校验

## 4. 测试设计

### 4.1 单元测试

- 测试敏感度分析模块
- 测试可见性管理模块
- 测试引用场景校验模块
- 测试存储层的元数据处理

### 4.2 集成测试

- 测试记忆创建和敏感度分析的集成
- 测试记忆检索和可见性过滤的集成
- 测试记忆检索和场景校验的集成

### 4.3 性能测试

- 测试敏感度分析的性能
- 测试可见性过滤的性能
- 测试场景校验的性能
- 测试整体系统的性能

## 5. 实施计划

1. 扩展记忆元数据结构
2. 实现敏感度分析模块
3. 实现可见性管理模块
4. 实现引用场景校验模块
5. 更新存储层，支持新的元数据字段
6. 更新核心引擎，集成新的隐私保护功能
7. 编写单元测试和集成测试
8. 运行性能测试
9. 更新文档和README
10. 提交到Git

## 6. 风险评估

- **性能风险**：敏感度分析可能会增加系统响应时间
- **兼容性风险**：新的元数据字段可能会影响现有功能
- **实现风险**：可见性管理和场景校验的逻辑可能会比较复杂

## 7. 缓解措施

- 优化敏感度分析算法，确保性能
- 保持向后兼容性，确保现有功能不受影响
- 采用模块化设计，确保逻辑清晰可维护
