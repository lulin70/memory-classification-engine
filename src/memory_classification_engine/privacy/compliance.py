import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class ComplianceManager:
    def __init__(self, config_file: str = "./config/compliance.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.data_processing_records = self._load_data_processing_records()
    
    def _load_config(self) -> Dict:
        """加载合规性配置"""
        if not os.path.exists(self.config_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            return self._create_default_config()
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _create_default_config(self) -> Dict:
        """创建默认配置"""
        return {
            'company_name': 'Memory Classification Engine',
            'contact_email': 'privacy@memory-classification-engine.com',
            'data_retention_policy': '365 days',
            'cookie_policy': 'We use cookies to improve your experience',
            'gdpr_compliant': True,
            'ccpa_compliant': True
        }
    
    def _save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
    
    def _load_data_processing_records(self) -> List[Dict]:
        """加载数据处理记录"""
        records_file = "./config/data_processing_records.json"
        if not os.path.exists(records_file):
            return []
        
        with open(records_file, 'r') as f:
            return json.load(f)
    
    def _save_data_processing_records(self):
        """保存数据处理记录"""
        records_file = "./config/data_processing_records.json"
        os.makedirs(os.path.dirname(records_file), exist_ok=True)
        with open(records_file, 'w') as f:
            json.dump(self.data_processing_records, f)
    
    def update_config(self, config: Dict):
        """更新合规性配置"""
        self.config.update(config)
        self._save_config()
    
    def generate_privacy_policy(self) -> str:
        """生成隐私政策"""
        policy = f"""
# 隐私政策

## 1. 简介

本隐私政策描述了 {self.config.get('company_name', 'Memory Classification Engine')} 如何收集、使用、存储和保护您的个人数据。

## 2. 数据收集

我们收集以下类型的数据：
- 个人信息（如姓名、电子邮件地址）
- 使用数据（如访问时间、IP地址）
- 记忆数据（如您的对话内容、偏好设置）

## 3. 数据使用

我们使用收集的数据：
- 提供和改进我们的服务
- 个性化您的体验
- 分析使用情况
- 与您沟通

## 4. 数据存储

我们按照以下政策存储您的数据：
- 数据保留期限：{self.config.get('data_retention_policy', '365 days')}
- 数据加密：我们使用AES-256-GCM加密敏感数据
- 数据备份：我们定期备份数据以防止数据丢失

## 5. 数据共享

我们不会与第三方共享您的个人数据，除非：
- 获得您的明确许可
- 法律要求
- 保护我们的权利和财产

## 6. 您的权利

根据 GDPR 和 CCPA，您有权：
- 访问您的数据
- 修改您的数据
- 删除您的数据
- 限制数据处理
- 数据端口ability
- 反对数据处理

## 7. 联系我们

如果您对本隐私政策有任何疑问，请联系：
- 电子邮件：{self.config.get('contact_email', 'privacy@memory-classification-engine.com')}

## 8. 变更

本隐私政策可能会不时更新，更新后的政策将在我们的网站上发布。

最后更新：{datetime.now().strftime('%Y-%m-%d')}
"""
        return policy
    
    def log_data_processing(self, user_id: str, action: str, data_type: str, purpose: str):
        """记录数据处理操作"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'data_type': data_type,
            'purpose': purpose
        }
        self.data_processing_records.append(record)
        # 限制记录数量，只保留最近1000条
        if len(self.data_processing_records) > 1000:
            self.data_processing_records = self.data_processing_records[-1000:]
        self._save_data_processing_records()
    
    def get_data_processing_records(self, user_id: Optional[str] = None) -> List[Dict]:
        """获取数据处理记录"""
        if user_id:
            return [record for record in self.data_processing_records if record.get('user_id') == user_id]
        return self.data_processing_records
    
    def perform_compliance_audit(self) -> Dict:
        """执行合规性审计"""
        audit_result = {
            'audit_date': datetime.now().isoformat(),
            'gdpr_compliant': self.config.get('gdpr_compliant', True),
            'ccpa_compliant': self.config.get('ccpa_compliant', True),
            'data_processing_records_count': len(self.data_processing_records),
            'issues': []
        }
        
        # 检查数据处理记录
        if len(self.data_processing_records) == 0:
            audit_result['issues'].append('No data processing records found')
        
        # 检查隐私政策
        if not self.generate_privacy_policy():
            audit_result['issues'].append('Privacy policy generation failed')
        
        return audit_result
    
    def generate_privacy_impact_assessment(self) -> Dict:
        """生成隐私影响评估"""
        assessment = {
            'assessment_date': datetime.now().isoformat(),
            'system_description': 'Memory Classification Engine - A lightweight memory classification system',
            'data_types': ['Personal information', 'Usage data', 'Memory data'],
            'data_processing_activities': ['Data collection', 'Data storage', 'Data retrieval', 'Data deletion'],
            'risks': [
                {
                    'risk': 'Unauthorized access to sensitive data',
                    'severity': 'High',
                    'mitigation': 'Encryption, access control, audit logging'
                },
                {
                    'risk': 'Data breach',
                    'severity': 'High',
                    'mitigation': 'Encryption, regular backups, security monitoring'
                },
                {
                    'risk': 'Non-compliance with privacy regulations',
                    'severity': 'Medium',
                    'mitigation': 'Regular compliance audits, privacy policy updates'
                }
            ],
            'conclusion': 'The system has implemented appropriate measures to protect user privacy and comply with relevant regulations.'
        }
        return assessment

# 全局合规性管理器实例
compliance_manager = ComplianceManager()
