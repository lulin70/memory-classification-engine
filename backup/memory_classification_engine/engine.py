import os
from typing import Dict, List, Optional, Any
from memory_classification_engine.storage.tier2 import Tier2Storage
from memory_classification_engine.storage.tier3_fts import Tier3StorageFTS
from memory_classification_engine.utils.exceptions import MemoryNotFoundError

class MemoryClassificationEngine:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.working_memory = {}
        self.tier2_storage = Tier2Storage()
        self.tier3_storage = Tier3StorageFTS()
        self._load_config()
    
    def _load_config(self):
        pass
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        memory_type = self._classify_message(message)
        memory = {
            "type": memory_type,
            "memory_type": memory_type,
            "content": message,
            "confidence": 0.9,
            "source": "user",
            "tier": self._determine_tier(memory_type)
        }
        
        self._store_memory(memory)
        self._update_working_memory(memory)
        
        matches = self.retrieve_memories(message, memory_type)
        
        return {
            "message": message,
            "matches": matches,
            "working_memory_size": len(self.working_memory)
        }
    
    def _classify_message(self, message: str) -> str:
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ["like", "love", "prefer", "enjoy"]):
            return "user_preference"
        elif any(keyword in message_lower for keyword in ["correct", "wrong", "fix"]):
            return "correction"
        elif any(keyword in message_lower for keyword in ["is", "are", "was", "were", "will be"]):
            return "fact_declaration"
        elif any(keyword in message_lower for keyword in ["decide", "decision", "choose"]):
            return "decision"
        elif any(keyword in message_lower for keyword in ["friend", "family", "relationship"]):
            return "relationship"
        elif any(keyword in message_lower for keyword in ["task", "todo", "need to"]):
            return "task_pattern"
        elif any(keyword in message_lower for keyword in ["happy", "sad", "angry", "excited"]):
            return "sentiment_marker"
        else:
            return "general"
    
    def _determine_tier(self, memory_type: str) -> int:
        tier_map = {
            "user_preference": 2,
            "correction": 2,
            "fact_declaration": 3,
            "decision": 2,
            "relationship": 3,
            "task_pattern": 2,
            "sentiment_marker": 3,
            "general": 3
        }
        return tier_map.get(memory_type, 3)
    
    def _store_memory(self, memory: Dict[str, Any]):
        tier = memory.get("tier", 3)
        if tier == 2:
            self.tier2_storage.store_memory(memory)
        else:
            self.tier3_storage.store_memory(memory)
    
    def _update_working_memory(self, memory: Dict[str, Any]):
        memory_id = memory.get("id")
        if memory_id:
            self.working_memory[memory_id] = memory
            if len(self.working_memory) > 100:
                oldest_key = next(iter(self.working_memory))
                del self.working_memory[oldest_key]
    
    def retrieve_memories(self, query: str, memory_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        memories = []
        
        memories.extend(self._search_working_memory(query, memory_type))
        memories.extend(self.tier2_storage.retrieve_memories(query, limit // 2))
        memories.extend(self.tier3_storage.retrieve_memories(query, limit // 2))
        
        memories.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return memories[:limit]
    
    def _search_working_memory(self, query: str, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()
        
        for memory in self.working_memory.values():
            if memory_type and memory.get("type") != memory_type:
                continue
            if query_lower in memory.get("content", "").lower():
                results.append(memory)
        
        return results
    
    def manage_memory(self, action: str, memory_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if action == "view":
            memory = self._get_memory_by_id(memory_id)
            if not memory:
                raise MemoryNotFoundError(f"Memory with ID {memory_id} not found")
            return {"success": True, "memory": memory}
        
        elif action == "edit":
            if not data:
                return {"success": False, "error": "No data provided"}
            
            memory = self._get_memory_by_id(memory_id)
            if not memory:
                raise MemoryNotFoundError(f"Memory with ID {memory_id} not found")
            
            tier = memory.get("tier", 3)
            if tier == 2:
                success = self.tier2_storage.update_memory(memory_id, data)
            else:
                success = self.tier3_storage.update_memory(memory_id, data)
            
            if success:
                updated_memory = self._get_memory_by_id(memory_id)
                if memory_id in self.working_memory:
                    self.working_memory[memory_id] = updated_memory
                return {"success": True, "memory": updated_memory}
            else:
                return {"success": False, "error": "Failed to update memory"}
        
        elif action == "delete":
            memory = self._get_memory_by_id(memory_id)
            if not memory:
                raise MemoryNotFoundError(f"Memory with ID {memory_id} not found")
            
            tier = memory.get("tier", 3)
            if tier == 2:
                success = self.tier2_storage.delete_memory(memory_id)
            else:
                success = self.tier3_storage.delete_memory(memory_id)
            
            if success and memory_id in self.working_memory:
                del self.working_memory[memory_id]
            
            return {"success": success}
        
        else:
            return {"success": False, "error": "Invalid action"}
    
    def _get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        # 优先从存储中获取记忆，确保获取到最新的版本
        tier2_memories = self.tier2_storage.retrieve_memories()
        for memory in tier2_memories:
            if memory.get("id") == memory_id:
                return memory
        
        tier3_memories = self.tier3_storage.retrieve_memories()
        for memory in tier3_memories:
            if memory.get("id") == memory_id:
                return memory
        
        # 如果存储中没有，再从工作记忆中获取
        if memory_id in self.working_memory:
            return self.working_memory[memory_id]
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        tier2_stats = {
            "total_memories": len(self.tier2_storage.retrieve_memories(limit=10000)),
            "active_memories": len(self.tier2_storage.retrieve_memories(limit=10000))
        }
        
        tier3_stats = {
            "total_memories": len(self.tier3_storage.retrieve_memories(limit=10000)),
            "active_memories": len(self.tier3_storage.retrieve_memories(limit=10000))
        }
        
        return {
            "working_memory_size": len(self.working_memory),
            "tier2": tier2_stats,
            "tier3": tier3_stats,
            "tier4": {
                "total_memories": 0,
                "active_memories": 0
            },
            "total_memories": tier2_stats["total_memories"] + tier3_stats["total_memories"]
        }
