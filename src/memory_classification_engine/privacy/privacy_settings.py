import os
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class PrivacySettings:
    def __init__(self, visibility: str = "private", retention_period: int = 365, allow_data_sharing: bool = False):
        self.visibility = visibility  # Comment in Chinese removedd
        self.retention_period = retention_period  # 保留期限（天）
        self.allow_data_sharing = allow_data_sharing  # 是否允许数据共享

class PrivacyManager:
    def __init__(self, config_file: str = "./config/privacy_settings.json"):
        self.config_file = config_file
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, PrivacySettings]:
        """加载隐私设置"""
        if not os.path.exists(self.config_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            return {}
        
        with open(self.config_file, 'r') as f:
            data = json.load(f)
            settings = {}
            for user_id, user_settings in data.items():
                settings[user_id] = PrivacySettings(
                    user_settings.get('visibility', 'private'),
                    user_settings.get('retention_period', 365),
                    user_settings.get('allow_data_sharing', False)
                )
            return settings
    
    def _save_settings(self):
        """保存隐私设置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        data = {
            user_id: {
                'visibility': settings.visibility,
                'retention_period': settings.retention_period,
                'allow_data_sharing': settings.allow_data_sharing
            }
            for user_id, settings in self.settings.items()
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f)
    
    def get_settings(self, user_id: str) -> PrivacySettings:
        """获取用户隐私设置"""
        if user_id not in self.settings:
            # 返回默认设置
            return PrivacySettings()
        return self.settings[user_id]
    
    def update_settings(self, user_id: str, settings: PrivacySettings):
        """更新用户隐私设置"""
        self.settings[user_id] = settings
        self._save_settings()
    
    def delete_settings(self, user_id: str):
        """删除用户隐私设置"""
        if user_id in self.settings:
            del self.settings[user_id]
            self._save_settings()
    
    def is_data_expired(self, user_id: str, created_at: datetime) -> bool:
        """检查数据是否过期"""
        settings = self.get_settings(user_id)
        retention_period = settings.retention_period
        expiration_date = created_at + timedelta(days=retention_period)
        return datetime.now() > expiration_date
    
    def should_delete_data(self, user_id: str, created_at: datetime) -> bool:
        """判断是否应该删除数据"""
        return self.is_data_expired(user_id, created_at)
    
    def export_data(self, user_id: str, data: List[Dict], format: str = "json") -> str:
        """导出数据"""
        if format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif format == "csv":
            if not data:
                return ""
            # 获取所有字段名
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = list(fieldnames)
            
            # Comment in Chinese removed
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def anonymize_data(self, data: Dict) -> Dict:
        """匿名化数据"""
        # 简单实现，实际项目中可能需要更复杂的匿名化逻辑
        sensitive_fields = ['email', 'phone', 'address', 'credit_card', 'ssn']
        anonymized_data = {}
        for key, value in data.items():
            if key.lower() in sensitive_fields:
                anonymized_data[key] = "[ANONYMIZED]"
            else:
                anonymized_data[key] = value
        return anonymized_data
    
    def apply_data_minimization(self, data: Dict) -> Dict:
        """应用数据最小化原则"""
        # 简单实现，实际项目中可能需要更复杂的数据最小化逻辑
        # 这里假设只保留必要的字段
        necessary_fields = ['id', 'content', 'memory_type', 'created_at', 'priority']
        minimized_data = {}
        for key, value in data.items():
            if key in necessary_fields:
                minimized_data[key] = value
        return minimized_data

# 全局隐私管理器实例
privacy_manager = PrivacyManager()
