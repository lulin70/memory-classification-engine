# Comment in Chinese removed
"""
Memory Quality Assessment System

Tracks memory usage, effectiveness, and value over time
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger('memory-quality')

class MemoryQualityManager:
    """记忆质量管理器
    
    追踪记忆的使用情况、有效性和价值
    """
    
    def __init__(self):
        """初始化记忆质量管理器"""
        self.usage_tracker = {}
        self.feedback_tracker = {}
        self.quality_metrics = {}
        logger.info("MemoryQualityManager initialized")
    
    def track_memory_usage(self, memory_id: str, query: str, result: bool = True):
        """追踪记忆使用情况
        
        Args:
            memory_id: 记忆 ID
            query: 检索查询
            result: 是否成功检索到
        """
        try:
            if memory_id not in self.usage_tracker:
                self.usage_tracker[memory_id] = {
                    'total_usage': 0,
                    'successful_usage': 0,
                    'last_used': time.time(),
                    'usage_history': [],
                    'queries': set()
                }
            
            # 更新使用统计
            self.usage_tracker[memory_id]['total_usage'] += 1
            if result:
                self.usage_tracker[memory_id]['successful_usage'] += 1
            
            # 更新最后使用时间
            self.usage_tracker[memory_id]['last_used'] = time.time()
            
            # 记录使用历史
            usage_record = {
                'timestamp': time.time(),
                'query': query,
                'result': result
            }
            self.usage_tracker[memory_id]['usage_history'].append(usage_record)
            
            # 记录查询词
            self.usage_tracker[memory_id]['queries'].add(query)
            
            logger.debug(f"Tracked usage for memory {memory_id}: {result}")
            
        except Exception as e:
            logger.error(f"Error tracking memory usage: {e}")
    
    def track_feedback(self, memory_id: str, feedback: str, context: Optional[Dict[str, Any]] = None):
        """追踪用户反馈
        
        Args:
            memory_id: 记忆 ID
            feedback: 反馈类型 ('positive', 'negative', 'neutral')
            context: 反馈上下文
        """
        try:
            if memory_id not in self.feedback_tracker:
                self.feedback_tracker[memory_id] = {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'feedback_history': []
                }
            
            # 更新反馈统计
            if feedback in ['positive', 'negative', 'neutral']:
                self.feedback_tracker[memory_id][feedback] += 1
            
            # 记录反馈历史
            feedback_record = {
                'timestamp': time.time(),
                'feedback': feedback,
                'context': context
            }
            self.feedback_tracker[memory_id]['feedback_history'].append(feedback_record)
            
            logger.debug(f"Tracked feedback for memory {memory_id}: {feedback}")
            
        except Exception as e:
            logger.error(f"Error tracking feedback: {e}")
    
    def calculate_memory_quality(self, memory_id: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        """计算记忆质量
        
        Args:
            memory_id: 记忆 ID
            memory: 记忆对象
            
        Returns:
            记忆质量指标
        """
        try:
            quality_score = 0.0
            metrics = {
                'usage_frequency': 0,
                'success_rate': 0,
                'feedback_score': 0,
                'recency_score': 0,
                'diversity_score': 0,
                'overall_quality': 0
            }
            
            # 计算使用频率
            usage_data = self.usage_tracker.get(memory_id, {})
            total_usage = usage_data.get('total_usage', 0)
            metrics['usage_frequency'] = min(total_usage / 30, 1.0)  # Comment in Chinese removed天内的使用频率
            
            # 计算成功率
            if total_usage > 0:
                successful_usage = usage_data.get('successful_usage', 0)
                metrics['success_rate'] = successful_usage / total_usage
            
            # 计算反馈分数
            feedback_data = self.feedback_tracker.get(memory_id, {})
            total_feedback = sum(feedback_data.get(k, 0) for k in ['positive', 'negative', 'neutral'])
            if total_feedback > 0:
                positive = feedback_data.get('positive', 0)
                negative = feedback_data.get('negative', 0)
                metrics['feedback_score'] = (positive - negative) / total_feedback
            
            # 计算新鲜度分数
            last_used = usage_data.get('last_used', 0)
            days_since_used = (time.time() - last_used) / (24 * 3600)
            metrics['recency_score'] = max(0, 1 - (days_since_used / 30))  # Comment in Chinese removed天内的新鲜度
            
            # 计算多样性分数
            query_count = len(usage_data.get('queries', set()))
            metrics['diversity_score'] = min(query_count / 10, 1.0)  # 基于不同查询的数量
            
            # 计算总体质量分数
            weights = {
                'usage_frequency': 0.3,
                'success_rate': 0.25,
                'feedback_score': 0.25,
                'recency_score': 0.1,
                'diversity_score': 0.1
            }
            
            for metric, weight in weights.items():
                quality_score += metrics[metric] * weight
            
            metrics['overall_quality'] = quality_score
            
            # 保存质量指标
            self.quality_metrics[memory_id] = {
                'metrics': metrics,
                'calculated_at': time.time()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating memory quality: {e}")
            return {
                'usage_frequency': 0,
                'success_rate': 0,
                'feedback_score': 0,
                'recency_score': 0,
                'diversity_score': 0,
                'overall_quality': 0
            }
    
    def generate_low_value_report(self, threshold: float = 0.3, days: int = 30) -> List[Dict[str, Any]]:
        """生成低价值记忆报告
        
        Args:
            threshold: 质量分数阈值
            days: 统计天数
            
        Returns:
            低价值记忆列表
        """
        try:
            low_value_memories = []
            cutoff_time = time.time() - (days * 24 * 3600)
            
            for memory_id, usage_data in self.usage_tracker.items():
                # 计算质量分数
                mock_memory = {'id': memory_id}
                metrics = self.calculate_memory_quality(memory_id, mock_memory)
                
                # 检查是否低价值
                if metrics['overall_quality'] < threshold:
                    # 检查是否在指定时间范围内有使用
                    last_used = usage_data.get('last_used', 0)
                    if last_used > cutoff_time:
                        low_value_memory = {
                            'memory_id': memory_id,
                            'quality_metrics': metrics,
                            'last_used': last_used,
                            'total_usage': usage_data.get('total_usage', 0),
                            'feedback': self.feedback_tracker.get(memory_id, {})
                        }
                        low_value_memories.append(low_value_memory)
            
            # 按质量分数排序
            low_value_memories.sort(key=lambda x: x['quality_metrics']['overall_quality'])
            
            logger.info(f"Generated low value report: {len(low_value_memories)} memories")
            return low_value_memories
            
        except Exception as e:
            logger.error(f"Error generating low value report: {e}")
            return []
    
    def generate_quality_report(self, days: int = 30) -> Dict[str, Any]:
        """生成质量报告
        
        Args:
            days: 统计天数
            
        Returns:
            质量报告
        """
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            total_memories = len(self.usage_tracker)
            total_usage = 0
            total_feedback = 0
            quality_scores = []
            
            # 计算总体统计
            for memory_id, usage_data in self.usage_tracker.items():
                if usage_data.get('last_used', 0) > cutoff_time:
                    total_usage += usage_data.get('total_usage', 0)
                    quality = self.calculate_memory_quality(memory_id, {'id': memory_id})
                    quality_scores.append(quality['overall_quality'])
            
            for memory_id, feedback_data in self.feedback_tracker.items():
                total_feedback += sum(feedback_data.get(k, 0) for k in ['positive', 'negative', 'neutral'])
            
            # 计算平均质量分数
            average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # 生成报告
            report = {
                'period': f'Last {days} days',
                'total_memories': total_memories,
                'total_usage': total_usage,
                'total_feedback': total_feedback,
                'average_quality': average_quality,
                'high_quality_memories': sum(1 for score in quality_scores if score > 0.7),
                'medium_quality_memories': sum(1 for score in quality_scores if 0.3 <= score <= 0.7),
                'low_quality_memories': sum(1 for score in quality_scores if score < 0.3),
                'generated_at': time.time()
            }
            
            logger.info(f"Generated quality report: {total_memories} memories, avg quality: {average_quality:.2f}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return {
                'error': str(e)
            }
    
    def get_memory_quality(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取记忆质量
        
        Args:
            memory_id: 记忆 ID
            
        Returns:
            记忆质量指标
        """
        try:
            if memory_id in self.quality_metrics:
                return self.quality_metrics[memory_id]['metrics']
            return None
        except Exception as e:
            logger.error(f"Error getting memory quality: {e}")
            return None
    
    def reset_tracking(self, memory_id: Optional[str] = None):
        """重置追踪数据
        
        Args:
            memory_id: 记忆 ID，None 表示重置所有
        """
        try:
            if memory_id:
                if memory_id in self.usage_tracker:
                    del self.usage_tracker[memory_id]
                if memory_id in self.feedback_tracker:
                    del self.feedback_tracker[memory_id]
                if memory_id in self.quality_metrics:
                    del self.quality_metrics[memory_id]
                logger.info(f"Reset tracking for memory {memory_id}")
            else:
                self.usage_tracker.clear()
                self.feedback_tracker.clear()
                self.quality_metrics.clear()
                logger.info("Reset all tracking data")
        except Exception as e:
            logger.error(f"Error resetting tracking: {e}")

# 全局记忆质量管理器实例
memory_quality_manager = MemoryQualityManager()

def get_memory_quality_manager() -> MemoryQualityManager:
    """获取记忆质量管理器实例
    
    Returns:
        MemoryQualityManager 实例
    """
    return memory_quality_manager

if __name__ == "__main__":
    # 测试记忆质量管理器
    manager = MemoryQualityManager()
    
    # 模拟使用数据
    memory_ids = ["mem_1", "mem_2", "mem_3"]
    
    # 模拟记忆使用
    for i, memory_id in enumerate(memory_ids):
        for j in range(i + 1):  # 不同的使用频率
            manager.track_memory_usage(memory_id, f"query_{j}", result=True)
            
        # 模拟反馈
        if i == 0:
            manager.track_feedback(memory_id, "positive")
        elif i == 1:
            manager.track_feedback(memory_id, "neutral")
        else:
            manager.track_feedback(memory_id, "negative")
    
    # 计算质量
    for memory_id in memory_ids:
        quality = manager.calculate_memory_quality(memory_id, {'id': memory_id})
        print(f"Memory {memory_id} quality: {quality['overall_quality']:.2f}")
    
    # 生成低价值报告
    low_value = manager.generate_low_value_report()
    print(f"\nLow value memories: {len(low_value)}")
    for mem in low_value:
        print(f"  {mem['memory_id']}: {mem['quality_metrics']['overall_quality']:.2f}")
    
    # 生成质量报告
    report = manager.generate_quality_report()
    print("\nQuality report:")
    for key, value in report.items():
        if key != 'generated_at':
            print(f"  {key}: {value}")
