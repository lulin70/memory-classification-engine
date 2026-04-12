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
        # Comment in Chinese removednt适配器
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
                # 转换为驼峰命名法
                class_name = ''.join(word.capitalize() for word in adapter_name.split('_')) + 'Adapter'
                adapter_class = getattr(module, class_name)
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
