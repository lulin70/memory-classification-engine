#!/usr/bin/env python3
"""
Memory Classification Tool

Tool for classifying messages into memory types
"""

import json
import logging

from memory_classification_engine import MemoryClassificationEngine

logger = logging.getLogger('mce-mcp-classify')

class ClassifyTool:
    """分类工具"""
    
    def __init__(self):
        """初始化分类工具"""
        self.engine = MemoryClassificationEngine()
    
    def classify_message(self, message, context=None, execution_context=None):
        """分类消息
        
        Args:
            message (str): 要分类的消息
            context (str, optional): 上下文信息
            execution_context (dict, optional): 执行上下文
            
        Returns:
            dict: 分类结果
        """
        try:
            logger.info(f"Classifying message: {message[:50]}...")
            
            result = self.engine.process_message(
                message,
                context=context,
                execution_context=execution_context
            )
            
            # 格式化结果
            formatted_result = {
                'matches': result.get('matches', []),
                'summary': result.get('summary', ''),
                'confidence': result.get('confidence', 0.0),
                'is_memory_worthy': len(result.get('matches', [])) > 0,
                'processing_time': result.get('processing_time', 0)
            }
            
            logger.info(f"Classification completed with {len(formatted_result['matches'])} matches")
            return formatted_result
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                'error': str(e),
                'matches': [],
                'is_memory_worthy': False
            }
    
    def batch_classify(self, messages, contexts=None, execution_contexts=None):
        """批量分类消息
        
        Args:
            messages (list): 消息列表
            contexts (list, optional): 上下文列表
            execution_contexts (list, optional): 执行上下文列表
            
        Returns:
            list: 分类结果列表
        """
        results = []
        
        for i, message in enumerate(messages):
            context = contexts[i] if contexts and i < len(contexts) else None
            execution_context = execution_contexts[i] if execution_contexts and i < len(execution_contexts) else None
            
            result = self.classify_message(message, context, execution_context)
            results.append(result)
        
        return results
    
    def get_supported_memory_types(self):
        """获取支持的记忆类型
        
        Returns:
            list: 支持的记忆类型列表
        """
        return [
            'user_preference',
            'correction',
            'relationship',
            'decision',
            'sentiment_marker',
            'task_pattern',
            'knowledge'
        ]

# 全局工具实例
classify_tool = ClassifyTool()

if __name__ == "__main__":
    # 测试分类工具
    test_messages = [
        "我更喜欢使用双引号",
        "不，应该使用单引号",
        "张三是后端开发工程师"
    ]
    
    for message in test_messages:
        result = classify_tool.classify_message(message)
        print(f"Message: {message}")
        print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        print("-" * 50)
