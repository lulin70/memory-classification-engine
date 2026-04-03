import json
import os
from typing import Dict, List, Optional, Any
from memory_classification_engine.storage.base import BaseStorage

class Tier2Storage(BaseStorage):
    def __init__(self, storage_path: str = "./data/tier2"):
        super().__init__(storage_path)
        self.storage_file = os.path.join(storage_path, "procedural_memories.json")
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        try:
            memory = self._prepare_memory(memory)
            
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            memories.append(memory)
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(memories, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            return self._handle_error(e)
    
    def retrieve_memories(self, query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            if query:
                filtered_memories = [
                    mem for mem in memories 
                    if mem['status'] == 'active' and 
                    query.lower() in mem.get('content', '').lower()
                ]
            else:
                filtered_memories = [mem for mem in memories if mem['status'] == 'active']
            
            filtered_memories.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            return filtered_memories[:limit]
        except Exception as e:
            self._handle_error(e)
            return []
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            memory_found = False
            for i, memory in enumerate(memories):
                if memory['id'] == memory_id:
                    memory.update(updates)
                    memory['updated_at'] = self._get_current_time()
                    memory_found = True
                    break
            
            if memory_found:
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(memories, f, ensure_ascii=False, indent=2)
                return True
            return False
        except Exception as e:
            return self._handle_error(e)
    
    def delete_memory(self, memory_id: str) -> bool:
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            new_memories = [mem for mem in memories if mem['id'] != memory_id]
            
            if len(new_memories) != len(memories):
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(new_memories, f, ensure_ascii=False, indent=2)
                return True
            return False
        except Exception as e:
            return self._handle_error(e)
