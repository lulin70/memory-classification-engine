from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class Plugin(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def initialize(self) -> bool:
        pass
    
    @abstractmethod
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        pass
