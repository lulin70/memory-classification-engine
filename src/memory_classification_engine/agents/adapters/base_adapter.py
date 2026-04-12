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
