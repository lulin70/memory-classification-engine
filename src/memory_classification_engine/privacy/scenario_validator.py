from typing import Dict, Any, List

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
        if not memories:
            return []
        
        if scenario not in self.scenario_rules:
            return memories
        
        rule = self.scenario_rules[scenario]
        max_sensitivity = rule.get("max_sensitivity", "high")
        
        sensitivity_levels = {"low": 0, "medium": 1, "high": 2}
        max_level = sensitivity_levels[max_sensitivity]
        
        # 过滤掉超出敏感度限制的记忆
        filtered_memories = []
        for memory in memories:
            memory_level = sensitivity_levels.get(memory.get('sensitivity_level', 'low'), 0)
            if memory_level <= max_level:
                filtered_memories.append(memory)
        
        return filtered_memories
    
    def get_scenario_rules(self):
        """获取场景规则"""
        return self.scenario_rules
    
    def add_scenario_rule(self, scenario, rule):
        """添加场景规则"""
        self.scenario_rules[scenario] = rule
