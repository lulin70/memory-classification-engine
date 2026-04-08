import re
from typing import Dict, Any

class SensitivityAnalyzer:
    def __init__(self, config):
        self.config = config
        self.sensitive_patterns = {
            "high": [
                r"credit card", r"social security", r"password",
                r"bank account", r"medical", r"health",
                r"ssn", r"social security number", r"credit card number",
                r"bank account number", r"financial information", r"personal health information"
            ],
            "medium": [
                r"address", r"phone number", r"email",
                r"birthday", r"salary", r"income",
                r"phone", r"email address", r"home address",
                r"work address", r"contact information", r"personal information"
            ]
        }
    
    def analyze_sensitivity(self, content):
        """分析内容的敏感度"""
        if not content:
            return "low"
        
        content_lower = content.lower()
        
        # 检查高敏感度模式
        for pattern in self.sensitive_patterns["high"]:
            if re.search(pattern, content_lower):
                return "high"
        
        # 检查中敏感度模式
        for pattern in self.sensitive_patterns["medium"]:
            if re.search(pattern, content_lower):
                return "medium"
        
        # 默认为低敏感度
        return "low"
    
    def analyze_memory_sensitivity(self, memory):
        """分析记忆的敏感度"""
        content = memory.get('content', '')
        return self.analyze_sensitivity(content)
