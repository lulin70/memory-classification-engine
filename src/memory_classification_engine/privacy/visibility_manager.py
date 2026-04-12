from typing import Dict, Any

class VisibilityManager:
    def __init__(self, config):
        self.config = config
    
    def validate_visibility(self, visibility):
        """验证可见性标签是否有效"""
        valid_visibilities = ["private", "team", "org"]
        return visibility in valid_visibilities
    
    def can_access(self, user_id, memory):
        """判断用户是否有权访问记忆"""
        if not memory:
            return False
        
        visibility = memory.get('visibility', 'private')
        created_by = memory.get('created_by', None)
        
        if visibility == "private":
            return user_id == created_by
        elif visibility == "team":
            # 这里需要实现团队成员判断逻辑
            # 简化处理，暂时允许所有用户访问
            return True
        elif visibility == "org":
            return True
        return False
    
    def upgrade_visibility(self, memory, new_visibility, user_id):
        """升级记忆的可见性"""
        if not self.validate_visibility(new_visibility):
            return False
        
        # 只有创建者可以升级可见性
        if user_id != memory.get('created_by'):
            return False
        
        # 只能升级，不能降级
        visibility_levels = {"private": 0, "team": 1, "org": 2}
        current_visibility = memory.get('visibility', 'private')
        if visibility_levels[new_visibility] <= visibility_levels[current_visibility]:
            return False
        
        memory['visibility'] = new_visibility
        return True
    
    def filter_by_visibility(self, memories, user_id):
        """根据用户ID过滤记忆"""
        if not memories:
            return []
        
        filtered_memories = []
        for memory in memories:
            if self.can_access(user_id, memory):
                filtered_memories.append(memory)
        
        return filtered_memories
