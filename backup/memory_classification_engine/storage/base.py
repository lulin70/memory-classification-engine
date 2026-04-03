import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any

class BaseStorage(ABC):
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        os.makedirs(self.storage_path, exist_ok=True)
    
    @abstractmethod
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def retrieve_memories(self, query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        pass
    
    def _prepare_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        if 'id' not in memory:
            memory['id'] = self._generate_memory_id()
        
        current_time = self._get_current_time()
        if 'created_at' not in memory:
            memory['created_at'] = current_time
        if 'updated_at' not in memory:
            memory['updated_at'] = current_time
        if 'last_accessed' not in memory:
            memory['last_accessed'] = current_time
        if 'access_count' not in memory:
            memory['access_count'] = 0
        if 'status' not in memory:
            memory['status'] = 'active'
        
        return memory
    
    def _generate_memory_id(self) -> str:
        timestamp = int(datetime.now().timestamp() * 1000)
        return f"mem_{timestamp}"
    
    def _get_current_time(self) -> str:
        return datetime.now().isoformat()
    
    def _handle_error(self, error: Exception) -> bool:
        print(f"Error: {error}")
        return False
