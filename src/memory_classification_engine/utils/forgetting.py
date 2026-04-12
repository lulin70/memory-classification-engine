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
        
        # 确保时间是浮点数类型
        try:
            created_at = float(created_at)
        except (ValueError, TypeError):
            created_at = current_time
        
        try:
            last_accessed = float(last_accessed)
        except (ValueError, TypeError):
            last_accessed = created_at
        
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
