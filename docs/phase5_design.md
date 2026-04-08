# Phase 5 设计文档

## 1. 设计概述

本设计文档描述了记忆分类引擎（Memory Classification Engine）Phase 5阶段的实现方案，主要包括多种Agent框架支持、与Obsidian的集成以及产品定位的明确。设计目标是在保持系统高性能和轻量级的前提下，扩展系统的生态系统，提高系统的可用性和实用性。

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

#### 2.2.1 Agent框架集成模块

- 实现Agent框架的抽象接口
- 实现ClaudeCode、WorkBuddy、TRAE、openclaw等Agent框架的适配器
- 实现Agent框架的自动发现和注册机制
- 实现Agent框架的动态加载和卸载

#### 2.2.2 知识库集成模块

- 实现与Obsidian的集成接口
- 实现记忆写回知识库的机制
- 实现从知识库获取上下文增强的功能
- 实现知识库的自动同步和更新

#### 2.2.3 产品定位模块

- 明确记忆分类引擎的服务用户和场景
- 确定核心功能和非核心功能
- 制定产品路线图和发展计划
- 设计用户界面和用户体验

## 3. 详细设计

### 3.1 Agent框架集成模块

创建`src/memory_classification_engine/agents/agent_manager.py`：

```python
from typing import Dict, Any, List, Optional
from memory_classification_engine.utils.logger import logger
import importlib
import os

class AgentManager:
    def __init__(self, config):
        self.config = config
        self.agents = {}
        self.agent_adapters = {}
        self._load_agent_adapters()
    
    def _load_agent_adapters(self):
        """加载Agent适配器"""
        # 内置Agent适配器
        builtin_adapters = [
            'claude_code',
            'work_buddy',
            'trae',
            'openclaw'
        ]
        
        for adapter_name in builtin_adapters:
            try:
                module_name = f'memory_classification_engine.agents.adapters.{adapter_name}'
                module = importlib.import_module(module_name)
                adapter_class = getattr(module, f'{adapter_name.capitalize()}Adapter')
                self.agent_adapters[adapter_name] = adapter_class
                logger.info(f'Loaded agent adapter: {adapter_name}')
            except Exception as e:
                logger.warning(f'Failed to load agent adapter {adapter_name}: {e}')
    
    def register_agent(self, agent_name: str, agent_config: Dict[str, Any]):
        """注册Agent"""
        adapter_name = agent_config.get('adapter', agent_name)
        if adapter_name not in self.agent_adapters:
            logger.error(f'Agent adapter {adapter_name} not found')
            return False
        
        try:
            adapter_class = self.agent_adapters[adapter_name]
            agent = adapter_class(agent_config)
            self.agents[agent_name] = agent
            logger.info(f'Registered agent: {agent_name}')
            return True
        except Exception as e:
            logger.error(f'Failed to register agent {agent_name}: {e}')
            return False
    
    def unregister_agent(self, agent_name: str):
        """注销Agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f'Unregistered agent: {agent_name}')
            return True
        return False
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """获取Agent"""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[str]:
        """列出所有Agent"""
        return list(self.agents.keys())
    
    def process_message(self, agent_name: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用Agent处理消息"""
        agent = self.get_agent(agent_name)
        if not agent:
            return {'error': f'Agent {agent_name} not found'}
        
        try:
            return agent.process_message(message, context)
        except Exception as e:
            logger.error(f'Failed to process message with agent {agent_name}: {e}')
            return {'error': str(e)}
    
    def process_memory(self, agent_name: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        """使用Agent处理记忆"""
        agent = self.get_agent(agent_name)
        if not agent:
            return {'error': f'Agent {agent_name} not found'}
        
        try:
            return agent.process_memory(memory)
        except Exception as e:
            logger.error(f'Failed to process memory with agent {agent_name}: {e}')
            return {'error': str(e)}
```

创建`src/memory_classification_engine/agents/adapters/base_adapter.py`：

```python
from typing import Dict, Any

class BaseAdapter:
    def __init__(self, config):
        self.config = config
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理消息"""
        raise NotImplementedError
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """处理记忆"""
        raise NotImplementedError
```

创建`src/memory_classification_engine/agents/adapters/claude_code.py`：

```python
from memory_classification_engine.agents.adapters.base_adapter import BaseAdapter
from typing import Dict, Any

class ClaudeCodeAdapter(BaseAdapter):
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理消息"""
        # 实现ClaudeCode的消息处理逻辑
        return {
            'processed_message': message,
            'agent': 'claude_code',
            'status': 'success'
        }
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """处理记忆"""
        # 实现ClaudeCode的记忆处理逻辑
        return {
            'processed_memory': memory,
            'agent': 'claude_code',
            'status': 'success'
        }
```

创建`src/memory_classification_engine/agents/adapters/work_buddy.py`：

```python
from memory_classification_engine.agents.adapters.base_adapter import BaseAdapter
from typing import Dict, Any

class WorkBuddyAdapter(BaseAdapter):
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理消息"""
        # 实现WorkBuddy的消息处理逻辑
        return {
            'processed_message': message,
            'agent': 'work_buddy',
            'status': 'success'
        }
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """处理记忆"""
        # 实现WorkBuddy的记忆处理逻辑
        return {
            'processed_memory': memory,
            'agent': 'work_buddy',
            'status': 'success'
        }
```

创建`src/memory_classification_engine/agents/adapters/trae.py`：

```python
from memory_classification_engine.agents.adapters.base_adapter import BaseAdapter
from typing import Dict, Any

class TraeAdapter(BaseAdapter):
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理消息"""
        # 实现TRAE的消息处理逻辑
        return {
            'processed_message': message,
            'agent': 'trae',
            'status': 'success'
        }
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """处理记忆"""
        # 实现TRAE的记忆处理逻辑
        return {
            'processed_memory': memory,
            'agent': 'trae',
            'status': 'success'
        }
```

创建`src/memory_classification_engine/agents/adapters/openclaw.py`：

```python
from memory_classification_engine.agents.adapters.base_adapter import BaseAdapter
from typing import Dict, Any

class OpenclawAdapter(BaseAdapter):
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理消息"""
        # 实现openclaw的消息处理逻辑
        return {
            'processed_message': message,
            'agent': 'openclaw',
            'status': 'success'
        }
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """处理记忆"""
        # 实现openclaw的记忆处理逻辑
        return {
            'processed_memory': memory,
            'agent': 'openclaw',
            'status': 'success'
        }
```

### 3.2 知识库集成模块

创建`src/memory_classification_engine/knowledge/knowledge_manager.py`：

```python
from typing import Dict, Any, List, Optional
from memory_classification_engine.utils.logger import logger
import os
import json

class KnowledgeManager:
    def __init__(self, config):
        self.config = config
        self.obsidian_vault_path = self.config.get('knowledge.obsidian_vault_path', '')
        self.knowledge_base = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """加载知识库"""
        if self.obsidian_vault_path and os.path.exists(self.obsidian_vault_path):
            self._load_obsidian_vault()
        else:
            logger.warning('Obsidian vault path not set or does not exist')
    
    def _load_obsidian_vault(self):
        """加载Obsidian vault"""
        try:
            # 遍历Obsidian vault目录
            for root, dirs, files in os.walk(self.obsidian_vault_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, self.obsidian_vault_path)
                        
                        # 读取文件内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 存储到知识库
                        self.knowledge_base[relative_path] = {
                            'content': content,
                            'path': file_path,
                            'last_modified': os.path.getmtime(file_path)
                        }
            
            logger.info(f'Loaded {len(self.knowledge_base)} files from Obsidian vault')
        except Exception as e:
            logger.error(f'Failed to load Obsidian vault: {e}')
    
    def get_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """获取知识库中的相关知识"""
        results = []
        
        # 简单的字符串匹配
        for path, knowledge in self.knowledge_base.items():
            if query in knowledge['content']:
                results.append({
                    'path': path,
                    'content': knowledge['content'],
                    'score': 1.0  # 简单的匹配得分
                })
        
        # 按得分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def write_memory_to_knowledge(self, memory: Dict[str, Any]) -> bool:
        """将记忆写回知识库"""
        if not self.obsidian_vault_path or not os.path.exists(self.obsidian_vault_path):
            logger.error('Obsidian vault path not set or does not exist')
            return False
        
        try:
            # 生成文件名
            memory_id = memory.get('id', '')
            memory_type = memory.get('memory_type', 'unknown')
            filename = f'{memory_id}_{memory_type}.md'
            file_path = os.path.join(self.obsidian_vault_path, filename)
            
            # 生成文件内容
            content = f"# {memory_type}\n\n"
            content += f"**ID**: {memory_id}\n"
            content += f"**Created At**: {memory.get('created_at', '')}\n"
            content += f"**Last Accessed**: {memory.get('last_accessed', '')}\n"
            content += f"**Weight**: {memory.get('weight', 1.0)}\n"
            content += f"**Importance**: {memory.get('importance', 'medium')}\n"
            content += f"**Sensitivity Level**: {memory.get('sensitivity_level', 'low')}\n"
            content += f"**Visibility**: {memory.get('visibility', 'private')}\n\n"
            content += f"## Content\n\n{memory.get('content', '')}\n"
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新知识库
            self.knowledge_base[filename] = {
                'content': content,
                'path': file_path,
                'last_modified': os.path.getmtime(file_path)
            }
            
            logger.info(f'Wrote memory {memory_id} to knowledge base')
            return True
        except Exception as e:
            logger.error(f'Failed to write memory to knowledge base: {e}')
            return False
    
    def sync_knowledge_base(self):
        """同步知识库"""
        self._load_knowledge_base()
        logger.info('Synced knowledge base')
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return {
            'total_files': len(self.knowledge_base),
            'vault_path': self.obsidian_vault_path
        }
```

### 3.3 核心引擎集成

更新`src/memory_classification_engine/engine.py`，集成Agent框架和知识库功能：

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
    
    # 初始化Agent管理器和知识库管理器 for Phase 5
    from memory_classification_engine.agents.agent_manager import AgentManager
    from memory_classification_engine.knowledge.knowledge_manager import KnowledgeManager
    
    self.agent_manager = AgentManager(self.config)
    self.knowledge_manager = KnowledgeManager(self.config)
    
    # 初始化性能监控
    self.performance_monitor = PerformanceMonitor(self.config)
    
    # 启动后台进程
    self._start_background_processes()
    
    self.logger.info("Memory Classification Engine initialized")

# 新增方法

def process_message_with_agent(self, agent_name: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """使用Agent处理消息"""
    # 先使用Agent处理消息
    agent_result = self.agent_manager.process_message(agent_name, message, context)
    
    # 然后使用引擎处理消息
    engine_result = self.process_message(message, context)
    
    # 合并结果
    result = {
        'agent_result': agent_result,
        'engine_result': engine_result
    }
    
    return result

def write_memory_to_knowledge(self, memory_id: str) -> Dict[str, Any]:
    """将记忆写回知识库"""
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
    
    # 写回知识库
    success = self.knowledge_manager.write_memory_to_knowledge(memory)
    
    if success:
        return {'success': True, 'memory_id': memory_id}
    else:
        return {'error': 'Failed to write memory to knowledge base'}

def get_knowledge(self, query: str) -> Dict[str, Any]:
    """获取知识库中的相关知识"""
    knowledge = self.knowledge_manager.get_knowledge(query)
    return {'knowledge': knowledge}

def sync_knowledge_base(self) -> Dict[str, Any]:
    """同步知识库"""
    self.knowledge_manager.sync_knowledge_base()
    return {'success': True}

def get_knowledge_statistics(self) -> Dict[str, Any]:
    """获取知识库统计信息"""
    return self.knowledge_manager.get_knowledge_statistics()

def register_agent(self, agent_name: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
    """注册Agent"""
    success = self.agent_manager.register_agent(agent_name, agent_config)
    if success:
        return {'success': True, 'agent_name': agent_name}
    else:
        return {'error': 'Failed to register agent'}

def unregister_agent(self, agent_name: str) -> Dict[str, Any]:
    """注销Agent"""
    success = self.agent_manager.unregister_agent(agent_name)
    if success:
        return {'success': True, 'agent_name': agent_name}
    else:
        return {'error': 'Failed to unregister agent'}

def list_agents(self) -> Dict[str, Any]:
    """列出所有Agent"""
    agents = self.agent_manager.list_agents()
    return {'agents': agents}
```

## 4. 测试设计

### 4.1 单元测试

- 测试Agent框架集成模块
- 测试知识库集成模块
- 测试核心引擎集成

### 4.2 集成测试

- 测试Agent框架与核心引擎的集成
- 测试知识库与核心引擎的集成
- 测试Agent框架与知识库的集成

### 4.3 性能测试

- 测试Agent框架的性能
- 测试知识库集成的性能
- 测试整体系统的性能

## 5. 实施计划

1. 实现Agent框架集成模块
2. 实现知识库集成模块
3. 更新核心引擎，集成新功能
4. 下载并安装Obsidian
5. 编写单元测试和集成测试
6. 运行性能测试
7. 更新文档和README
8. 提交到Git

## 6. 风险评估

- **兼容性风险**：不同Agent框架的集成可能会带来兼容性问题
- **性能风险**：知识库集成可能会增加系统响应时间
- **实现风险**：Obsidian集成的复杂性可能会导致实现困难

## 7. 缓解措施

- 采用模块化设计，确保Agent框架的集成不会影响现有功能
- 优化知识库访问，使用缓存减少响应时间
- 提供详细的文档和示例，帮助用户理解和使用新功能
- 优先使用本地计算，减少API调用成本
