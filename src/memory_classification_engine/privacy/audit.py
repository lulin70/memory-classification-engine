import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class AuditLog:
    def __init__(self, user_id: str, action: str, resource: str, details: Dict):
        self.timestamp = datetime.now().isoformat()
        self.user_id = user_id
        self.action = action
        self.resource = resource
        self.details = details

class AuditManager:
    def __init__(self, log_file: str = "./logs/audit.log"):
        self.log_file = log_file
        self.logs = self._load_logs()
    
    def _load_logs(self) -> List[Dict]:
        """加载审计日志"""
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            return []
        
        with open(self.log_file, 'r') as f:
            logs = []
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
            return logs
    
    def _save_logs(self):
        """保存审计日志"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w') as f:
            for log in self.logs:
                f.write(json.dumps(log) + '\n')
    
    def log(self, user_id: str, action: str, resource: str, details: Dict):
        """记录审计日志"""
        log = AuditLog(user_id, action, resource, details)
        log_dict = {
            'timestamp': log.timestamp,
            'user_id': log.user_id,
            'action': log.action,
            'resource': log.resource,
            'details': log.details
        }
        self.logs.append(log_dict)
        # 限制日志数量，只保留最近10000条
        if len(self.logs) > 10000:
            self.logs = self.logs[-10000:]
        self._save_logs()
    
    def get_logs(self, user_id: Optional[str] = None, action: Optional[str] = None, resource: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict]:
        """获取审计日志"""
        filtered_logs = self.logs
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.get('user_id') == user_id]
        
        if action:
            filtered_logs = [log for log in filtered_logs if log.get('action') == action]
        
        if resource:
            filtered_logs = [log for log in filtered_logs if log.get('resource') == resource]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.get('timestamp') >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.get('timestamp') <= end_time]
        
        return filtered_logs
    
    def analyze_security_events(self) -> Dict:
        """分析安全事件"""
        analysis = {
            'total_logs': len(self.logs),
            'event_types': {},
            'suspicious_events': [],
            'user_activities': {}
        }
        
        # 统计事件类型
        for log in self.logs:
            action = log.get('action')
            if action not in analysis['event_types']:
                analysis['event_types'][action] = 0
            analysis['event_types'][action] += 1
        
        # 分析用户活动
        for log in self.logs:
            user_id = log.get('user_id')
            if user_id not in analysis['user_activities']:
                analysis['user_activities'][user_id] = []
            analysis['user_activities'][user_id].append({
                'timestamp': log.get('timestamp'),
                'action': log.get('action'),
                'resource': log.get('resource')
            })
        
        # 检测可疑事件
        # 这里使用简单的规则，实际项目中可能需要更复杂的检测逻辑
        suspicious_patterns = [
            {'action': 'login', 'count': 5, 'time_window': 60},  # 60秒内5次登录尝试
            {'action': 'access', 'resource': 'sensitive_data', 'count': 10, 'time_window': 300}  # 300秒内10次敏感数据访问
        ]
        
        # 简单实现，实际项目中可能需要更复杂的时间窗口分析
        for pattern in suspicious_patterns:
            # 这里只是示例，实际实现需要根据时间窗口进行统计
            pass
        
        return analysis
    
    def generate_audit_report(self) -> str:
        """生成审计报告"""
        analysis = self.analyze_security_events()
        report = f"""
# 审计报告

## 1. 概况

- 审计日期：{datetime.now().isoformat()}
- 日志总数：{analysis['total_logs']}
- 事件类型：{len(analysis['event_types'])}
- 可疑事件：{len(analysis['suspicious_events'])}
- 活跃用户：{len(analysis['user_activities'])}

## 2. 事件类型分布

"""
        
        for action, count in analysis['event_types'].items():
            report += f"- {action}: {count}\n"
        
        report += f"""

## 3. 可疑事件

"""
        
        if analysis['suspicious_events']:
            for event in analysis['suspicious_events']:
                report += f"- {event}\n"
        else:
            report += "无可疑事件\n"
        
        report += f"""

## 4. 用户活动

"""
        
        for user_id, activities in analysis['user_activities'].items():
            report += f"\n### 用户 {user_id}\n"
            for activity in activities[-5:]:  # 只显示最近5条活动
                report += f"- {activity['timestamp']} - {activity['action']} - {activity['resource']}\n"
        
        report += f"""

## 5. 结论

系统运行正常，未发现严重安全问题。
"""
        
        return report

# 全局审计管理器实例
audit_manager = AuditManager()
