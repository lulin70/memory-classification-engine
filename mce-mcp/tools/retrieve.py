#!/usr/bin/env python3
"""
Memory Retrieval Tool

Tool for retrieving relevant memories
"""

import json
import logging

from memory_classification_engine import MemoryClassificationEngine

logger = logging.getLogger('mce-mcp-retrieve')

class RetrieveTool:
    """检索工具"""
    
    def __init__(self):
        """初始化检索工具"""
        self.engine = MemoryClassificationEngine()
    
    def retrieve_memories(self, query, memory_type=None, limit=10, filters=None):
        """检索相关记忆
        
        Args:
            query (str): 检索查询
            memory_type (str, optional): 记忆类型过滤
            limit (int, optional): 返回结果数量限制
            filters (dict, optional): 其他过滤条件
            
        Returns:
            dict: 检索结果
        """
        try:
            logger.info(f"Retrieving memories for query: {query}")
            
            results = self.engine.retrieve_memories(
                query=query,
                memory_type=memory_type,
                limit=limit
            )
            
            # 应用额外过滤条件
            if filters:
                filtered_memories = []
                for memory in results.get('memories', []):
                    match = True
                    for key, value in filters.items():
                        if key in memory and memory[key] != value:
                            match = False
                            break
                    if match:
                        filtered_memories.append(memory)
                results['memories'] = filtered_memories
            
            # 格式化结果
            formatted_result = {
                'memories': results.get('memories', []),
                'total': len(results.get('memories', [])),
                'query': query,
                'memory_type': memory_type,
                'limit': limit,
                'processing_time': results.get('processing_time', 0)
            }
            
            logger.info(f"Retrieved {formatted_result['total']} memories")
            return formatted_result
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {
                'error': str(e),
                'memories': [],
                'total': 0
            }
    
    def get_memory_by_id(self, memory_id):
        """根据 ID 获取特定记忆
        
        Args:
            memory_id (str): 记忆 ID
            
        Returns:
            dict: 记忆详情
        """
        try:
            logger.info(f"Getting memory by ID: {memory_id}")
            
            # 这里需要在引擎中实现根据 ID 获取记忆的方法
            # 暂时使用检索方式模拟
            results = self.engine.retrieve_memories(
                query=memory_id,
                limit=1
            )
            
            if results.get('memories'):
                return {
                    'memory': results['memories'][0],
                    'found': True
                }
            else:
                return {
                    'memory': None,
                    'found': False,
                    'message': f"Memory with ID {memory_id} not found"
                }
                
        except Exception as e:
            logger.error(f"Get memory by ID failed: {e}")
            return {
                'error': str(e),
                'found': False
            }
    
    def search_memories(self, search_term, memory_types=None, min_confidence=0.5, limit=20):
        """高级搜索记忆
        
        Args:
            search_term (str): 搜索词
            memory_types (list, optional): 记忆类型列表
            min_confidence (float, optional): 最小置信度
            limit (int, optional): 返回结果数量限制
            
        Returns:
            dict: 搜索结果
        """
        try:
            logger.info(f"Searching memories for: {search_term}")
            
            all_memories = []
            
            # 如果指定了记忆类型，分别搜索每种类型
            if memory_types:
                for memory_type in memory_types:
                    results = self.engine.retrieve_memories(
                        query=search_term,
                        memory_type=memory_type,
                        limit=limit
                    )
                    all_memories.extend(results.get('memories', []))
            else:
                # 搜索所有类型
                results = self.engine.retrieve_memories(
                    query=search_term,
                    limit=limit
                )
                all_memories = results.get('memories', [])
            
            # 过滤低置信度的结果
            filtered_memories = [
                memory for memory in all_memories 
                if memory.get('confidence', 0) >= min_confidence
            ]
            
            # 按置信度排序
            filtered_memories.sort(
                key=lambda x: x.get('confidence', 0),
                reverse=True
            )
            
            # 限制返回数量
            filtered_memories = filtered_memories[:limit]
            
            return {
                'memories': filtered_memories,
                'total': len(filtered_memories),
                'search_term': search_term,
                'memory_types': memory_types,
                'min_confidence': min_confidence
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                'error': str(e),
                'memories': [],
                'total': 0
            }

# 全局工具实例
retrieve_tool = RetrieveTool()

if __name__ == "__main__":
    # 测试检索工具
    test_queries = [
        "代码风格",
        "团队成员",
        "技术选择"
    ]
    
    for query in test_queries:
        result = retrieve_tool.retrieve_memories(query)
        print(f"Query: {query}")
        print(f"Found {result['total']} memories")
        for i, memory in enumerate(result['memories'][:3]):
            print(f"  {i+1}. [{memory.get('memory_type')}] {memory.get('content', '')[:50]}...")
        print("-" * 50)
