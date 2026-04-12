#!/usr/bin/env python3
"""
Memory Forgetting Management Tool

Tool for managing memory forgetting process
"""

import json
import logging
import time

from memory_classification_engine import MemoryClassificationEngine

logger = logging.getLogger('mce-mcp-forget')

class ForgetTool:
    """遗忘管理工具"""
    
    def __init__(self):
        """初始化遗忘管理工具"""
        self.engine = MemoryClassificationEngine()
    
    def manage_forgetting(self, memory_id, action='decrease_weight', weight_adjustment=0.1, reason=None):
        """管理记忆遗忘
        
        Args:
            memory_id (str): 记忆 ID
            action (str, optional): 操作类型
                - decrease_weight: 降低权重
                - mark_expired: 标记为过期
                - delete: 删除记忆
                - refresh: 刷新记忆（增加权重）
            weight_adjustment (float, optional): 权重调整值
            reason (str, optional): 操作原因
            
        Returns:
            dict: 操作结果
        """
        try:
            logger.info(f"Managing forgetting for memory {memory_id}: {action}")
            
            # 调用引擎的遗忘管理方法
            result = self.engine.manage_forgetting(
                memory_id=memory_id,
                action=action,
                weight_adjustment=weight_adjustment
            )
            
            # 记录操作
            operation_record = {
                'memory_id': memory_id,
                'action': action,
                'weight_adjustment': weight_adjustment,
                'reason': reason,
                'timestamp': time.time(),
                'success': result.get('success', False)
            }
            
            logger.info(f"Forgetting management completed: {result.get('message', 'Unknown result')}")
            
            return {
                'success': result.get('success', False),
                'message': result.get('message', ''),
                'operation': operation_record
            }
            
        except Exception as e:
            logger.error(f"Forgetting management failed: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def batch_manage_forgetting(self, memory_ids, action='decrease_weight', weight_adjustment=0.1, reason=None):
        """批量管理记忆遗忘
        
        Args:
            memory_ids (list): 记忆 ID 列表
            action (str, optional): 操作类型
            weight_adjustment (float, optional): 权重调整值
            reason (str, optional): 操作原因
            
        Returns:
            dict: 批量操作结果
        """
        results = []
        success_count = 0
        error_count = 0
        
        for memory_id in memory_ids:
            result = self.manage_forgetting(
                memory_id=memory_id,
                action=action,
                weight_adjustment=weight_adjustment,
                reason=reason
            )
            
            results.append({
                'memory_id': memory_id,
                'result': result
            })
            
            if result.get('success'):
                success_count += 1
            else:
                error_count += 1
        
        return {
            'results': results,
            'summary': {
                'total': len(memory_ids),
                'success': success_count,
                'error': error_count,
                'action': action
            }
        }
    
    def get_forgetting_candidates(self, min_days_since_access=30, max_weight=0.5, limit=20):
        """获取遗忘候选记忆
        
        Args:
            min_days_since_access (int, optional): 最小未访问天数
            max_weight (float, optional): 最大权重
            limit (int, optional): 返回数量限制
            
        Returns:
            dict: 遗忘候选记忆列表
        """
        try:
            logger.info(f"Getting forgetting candidates: min_days={min_days_since_access}, max_weight={max_weight}")
            
            # 这里需要在引擎中实现获取遗忘候选的方法
            # 暂时返回模拟数据
            candidates = []
            
            # 模拟获取候选记忆
            # 实际实现时应该从存储中查询符合条件的记忆
            
            return {
                'candidates': candidates,
                'total': len(candidates),
                'criteria': {
                    'min_days_since_access': min_days_since_access,
                    'max_weight': max_weight
                }
            }
            
        except Exception as e:
            logger.error(f"Getting forgetting candidates failed: {e}")
            return {
                'error': str(e),
                'candidates': [],
                'total': 0
            }
    
    def optimize_memory_weights(self, target_count=None, max_age_days=None):
        """优化记忆权重
        
        Args:
            target_count (int, optional): 目标记忆数量
            max_age_days (int, optional): 最大记忆年龄（天）
            
        Returns:
            dict: 优化结果
        """
        try:
            logger.info(f"Optimizing memory weights: target_count={target_count}, max_age_days={max_age_days}")
            
            # 这里需要在引擎中实现权重优化的方法
            # 暂时返回模拟结果
            
            optimized_count = 0
            removed_count = 0
            
            return {
                'success': True,
                'message': f"Memory weights optimized: {optimized_count} memories processed, {removed_count} memories removed",
                'stats': {
                    'optimized_count': optimized_count,
                    'removed_count': removed_count,
                    'target_count': target_count,
                    'max_age_days': max_age_days
                }
            }
            
        except Exception as e:
            logger.error(f"Optimizing memory weights failed: {e}")
            return {
                'error': str(e),
                'success': False
            }

# 全局工具实例
forget_tool = ForgetTool()

if __name__ == "__main__":
    # 测试遗忘管理工具
    test_memory_id = "test_memory_123"
    
    # 测试降低权重
    result = forget_tool.manage_forgetting(
        memory_id=test_memory_id,
        action='decrease_weight',
        reason='Test forgetting'
    )
    print(f"Decrease weight result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print("-" * 50)
    
    # 测试批量操作
    test_memory_ids = ["test_memory_123", "test_memory_456"]
    batch_result = forget_tool.batch_manage_forgetting(
        memory_ids=test_memory_ids,
        action='decrease_weight',
        reason='Batch test'
    )
    print(f"Batch operation result: {json.dumps(batch_result, indent=2, ensure_ascii=False)}")
