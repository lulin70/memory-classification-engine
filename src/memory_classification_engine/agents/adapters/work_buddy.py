from memory_classification_engine.agents.adapters.base_adapter import BaseAdapter
from typing import Dict, Any

class WorkBuddyAdapter(BaseAdapter):
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理消息"""
        try:
            # Comment in Chinese removedddy的消息处理逻辑
            # Comment in Chinese removed调用
            processed_message = f"[WorkBuddy] {message}"
            
            # 分析消息内容，提取任务相关信息
            task_info = self._extract_task_info(message)
            
            return {
                'processed_message': processed_message,
                'task_info': task_info,
                'agent': 'work_buddy',
                'status': 'success'
            }
        except Exception as e:
            return {
                'error': str(e),
                'agent': 'work_buddy',
                'status': 'error'
            }
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """处理记忆"""
        try:
            # Comment in Chinese removedddy的记忆处理逻辑
            # Comment in Chinese removed调用
            processed_memory = memory.copy()
            processed_memory['processed_by'] = 'work_buddy'
            
            # 分析记忆内容，提取任务相关信息
            task_analysis = self._analyze_task_memory(memory)
            processed_memory['task_analysis'] = task_analysis
            
            return {
                'processed_memory': processed_memory,
                'agent': 'work_buddy',
                'status': 'success'
            }
        except Exception as e:
            return {
                'error': str(e),
                'agent': 'work_buddy',
                'status': 'error'
            }
    
    def _extract_task_info(self, message: str) -> Dict[str, Any]:
        """提取任务相关信息"""
        # 简单的任务提取逻辑
        task_keywords = ['任务', '工作', '项目', 'todo', '任务', '作业', '工作']
        contains_task = any(keyword in message.lower() for keyword in task_keywords)
        
        return {
            'contains_task': contains_task,
            'priority': 'high' if '紧急' in message or '重要' in message else 'normal',
            'deadline_mentioned': '截止' in message or '期限' in message or 'deadline' in message.lower(),
            'message_length': len(message)
        }
    
    def _analyze_task_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """分析任务相关记忆"""
        # 简单的任务记忆分析逻辑
        content = memory.get('content', '')
        task_keywords = ['任务', '工作', '项目', 'todo', '任务', '作业', '工作']
        contains_task = any(keyword in content.lower() for keyword in task_keywords)
        
        return {
            'contains_task': contains_task,
            'memory_type': memory.get('type', 'unknown'),
            'confidence': memory.get('confidence', 0.0),
            'content_length': len(content)
        }
