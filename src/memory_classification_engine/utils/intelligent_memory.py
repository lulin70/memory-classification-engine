import time
from typing import Dict, Any, List
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.semantic import semantic_utility

class IntelligentMemoryManager:
    def __init__(self, config):
        self.config = config
        self.compression_threshold = self.config.get('memory.compression_threshold', 0.8)
        self.max_batch_size = self.config.get('memory.max_batch_size', 100)
    
    def compress_memories(self, memories):
        """压缩和合并记忆"""
        if len(memories) < 2:
            return memories
        
        # 按记忆类型分组
        memories_by_type = {}
        for memory in memories:
            memory_type = memory.get('memory_type', 'unknown')
            if memory_type not in memories_by_type:
                memories_by_type[memory_type] = []
            memories_by_type[memory_type].append(memory)
        
        compressed_memories = []
        
        # 对每个类型的记忆进行压缩
        for memory_type, type_memories in memories_by_type.items():
            compressed = self._compress_memory_group(type_memories)
            compressed_memories.extend(compressed)
        
        return compressed_memories
    
    def _compress_memory_group(self, memories):
        """压缩一组相似的记忆"""
        if len(memories) < 2:
            return memories
        
        # 计算记忆之间的相似度
        similarities = []
        for i, memory1 in enumerate(memories):
            for j, memory2 in enumerate(memories):
                if i < j:
                    similarity = semantic_utility.calculate_similarity(
                        memory1.get('content', ''),
                        memory2.get('content', '')
                    )
                    similarities.append((i, j, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        # 合并相似的记忆
        merged = set()
        compressed = []
        
        for i, j, similarity in similarities:
            if i not in merged and j not in merged and similarity >= self.compression_threshold:
                # 合并两个记忆
                merged_memory = self._merge_memories(memories[i], memories[j])
                compressed.append(merged_memory)
                merged.add(i)
                merged.add(j)
        
        # 添加未合并的记忆
        for i, memory in enumerate(memories):
            if i not in merged:
                compressed.append(memory)
        
        return compressed
    
    def _merge_memories(self, memory1, memory2):
        """合并两个记忆"""
        # 合并内容
        content1 = memory1.get('content', '')
        content2 = memory2.get('content', '')
        merged_content = f"{content1} {content2}"
        
        # 合并其他属性
        merged_memory = {
            'id': memory1.get('id'),
            'content': merged_content,
            'memory_type': memory1.get('memory_type'),
            'tier': memory1.get('tier'),
            'weight': (memory1.get('weight', 1.0) + memory2.get('weight', 1.0)) / 2,
            'created_at': min(memory1.get('created_at', float('inf')), memory2.get('created_at', float('inf'))),
            'last_accessed': max(memory1.get('last_accessed', 0), memory2.get('last_accessed', 0)),
            'merged_from': [memory1.get('id'), memory2.get('id')]
        }
        
        # 合并其他属性
        for key, value in memory1.items():
            if key not in merged_memory:
                merged_memory[key] = value
        
        return merged_memory
    
    def prioritize_memories(self, memories):
        """对记忆进行优先级排序"""
        # 按权重和最后访问时间排序
        memories.sort(key=lambda x: (x.get('weight', 1.0), x.get('last_accessed', 0)), reverse=True)
        return memories
    
    def batch_operate(self, memories, operation):
        """批量操作记忆"""
        if len(memories) > self.max_batch_size:
            logger.warning(f"Batch size exceeded, processing only {self.max_batch_size} memories")
            memories = memories[:self.max_batch_size]
        
        results = []
        for memory in memories:
            result = operation(memory)
            results.append(result)
        
        return results
    
    def get_memory_statistics(self, memories):
        """获取记忆统计信息"""
        if not memories:
            return {}
        
        # 按类型统计
        type_counts = {}
        for memory in memories:
            memory_type = memory.get('memory_type', 'unknown')
            type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
        
        # 计算平均权重
        avg_weight = sum(memory.get('weight', 1.0) for memory in memories) / len(memories)
        
        # 计算记忆的时间分布
        time_distribution = {}
        for memory in memories:
            created_at = memory.get('created_at', 0)
            hour = time.strftime('%H', time.localtime(created_at))
            time_distribution[hour] = time_distribution.get(hour, 0) + 1
        
        return {
            'total_memories': len(memories),
            'type_counts': type_counts,
            'average_weight': avg_weight,
            'time_distribution': time_distribution
        }
