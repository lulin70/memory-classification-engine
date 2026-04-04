import pytest
import os
import shutil
from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.layers.pattern_analyzer import PatternAnalyzer
from memory_classification_engine.storage.tier3 import Tier3Storage, VECTOR_SEARCH_AVAILABLE

class TestLayer2Tier3:
    @pytest.fixture
    def pattern_analyzer(self):
        return PatternAnalyzer()
    
    @pytest.fixture
    def tier3_storage(self):
        # 清理测试数据
        if os.path.exists('./data'):
            shutil.rmtree('./data')
        
        storage = Tier3Storage()
        yield storage
        
        # 清理测试数据
        if os.path.exists('./data'):
            shutil.rmtree('./data')
    
    def test_pattern_analyzer_chinese(self, pattern_analyzer):
        """测试中文模式检测"""
        # 测试纠正模式
        result = pattern_analyzer.analyze("不对，Python是最好的语言")
        assert len(result) > 0
        assert any(match['memory_type'] == 'correction' for match in result)
        
        # 测试事实声明模式
        result = pattern_analyzer.analyze("Python是一种解释型语言")
        assert len(result) > 0
        assert any(match['memory_type'] == 'fact_declaration' for match in result)
        
        # 测试关系模式
        result = pattern_analyzer.analyze("Python属于编程语言")
        assert len(result) > 0
        assert any(match['memory_type'] == 'relationship' for match in result)
        
        # 测试任务模式
        result = pattern_analyzer.analyze("帮我写一个Python脚本")
        assert len(result) > 0
        assert any(match['memory_type'] == 'task_pattern' for match in result)
        
        # 测试决策模式
        # 先添加一个提议消息
        pattern_analyzer.analyze("我们应该使用Python")
        result = pattern_analyzer.analyze("好的，我们就用Python")
        assert len(result) > 0
        assert any(match['memory_type'] == 'decision' for match in result)
        
        # 测试情感模式
        result = pattern_analyzer.analyze("Python真的很棒")
        assert len(result) > 0
        assert any(match['memory_type'] == 'sentiment_marker' for match in result)
    
    def test_pattern_analyzer_english(self, pattern_analyzer):
        """测试英文模式检测"""
        # 测试纠正模式
        result = pattern_analyzer.analyze("No, Python is the best language")
        assert len(result) > 0
        assert any(match['memory_type'] == 'correction' for match in result)
        
        # 测试事实声明模式
        result = pattern_analyzer.analyze("Python is an interpreted language")
        assert len(result) > 0
        assert any(match['memory_type'] == 'fact_declaration' for match in result)
        
        # 测试关系模式
        result = pattern_analyzer.analyze("Python belongs to programming languages")
        assert len(result) > 0
        assert any(match['memory_type'] == 'relationship' for match in result)
        
        # 测试任务模式
        result = pattern_analyzer.analyze("Help me write a Python script")
        assert len(result) > 0
        assert any(match['memory_type'] == 'task_pattern' for match in result)
        
        # 测试决策模式
        # 先添加一个提议消息
        pattern_analyzer.analyze("We should use Python")
        result = pattern_analyzer.analyze("Okay, let's use Python")
        assert len(result) > 0
        assert any(match['memory_type'] == 'decision' for match in result)
        
        # 测试情感模式
        result = pattern_analyzer.analyze("Python is really great")
        assert len(result) > 0
        assert any(match['memory_type'] == 'sentiment_marker' for match in result)
    
    def test_pattern_analyzer_repeat_detection(self, pattern_analyzer):
        """测试重复模式检测"""
        # 测试重复偏好
        result1 = pattern_analyzer.analyze("我喜欢Python")
        result2 = pattern_analyzer.analyze("我喜欢Python")
        assert len(result2) > 0
        assert any('preference_repeat' in match['source'] for match in result2)
        
        # 测试重复任务
        result1 = pattern_analyzer.analyze("帮我写代码")
        result2 = pattern_analyzer.analyze("帮我写代码")
        assert len(result2) > 0
        assert any('task_repeat' in match['source'] for match in result2)
    
    def test_tier3_vector_search(self, tier3_storage):
        """测试Tier 3向量搜索功能"""
        # 存储一些记忆
        tier3_storage.store_memory({"content": "Python is a programming language", "confidence": 0.9, "id": "1", "type": "fact_declaration", "source": "user"})
        tier3_storage.store_memory({"content": "JavaScript is a programming language", "confidence": 0.8, "id": "2", "type": "fact_declaration", "source": "user"})
        tier3_storage.store_memory({"content": "Java is a programming language", "confidence": 0.7, "id": "3", "type": "fact_declaration", "source": "user"})
        
        # 测试常规搜索
        results = tier3_storage.retrieve_memories("Python")
        assert len(results) > 0
        assert any("Python" in result["content"] for result in results)
        
        # 测试向量搜索（如果可用）
        if VECTOR_SEARCH_AVAILABLE:
            vector_results = tier3_storage.retrieve_memories("programming language", use_vector_search=True)
            assert len(vector_results) > 0
            # 应该返回所有与编程语言相关的记忆
            assert any("programming language" in result["content"] for result in vector_results)
    
    def test_tier3_vector_index_update(self, tier3_storage):
        """测试Tier 3向量索引更新"""
        # 存储记忆
        tier3_storage.store_memory({"content": "Python is great", "confidence": 0.9, "id": "1", "type": "fact_declaration", "source": "user"})
        
        # 测试搜索
        results = tier3_storage.retrieve_memories("Python")
        assert len(results) > 0
        
        # 更新记忆
        tier3_storage.update_memory("1", {"content": "Python is very great"})
        
        # 测试更新后的搜索
        updated_results = tier3_storage.retrieve_memories("great")
        assert len(updated_results) > 0
        
        # 删除记忆
        tier3_storage.delete_memory("1")
        
        # 测试删除后的搜索
        deleted_results = tier3_storage.retrieve_memories("Python")
        assert len(deleted_results) == 0
    
    def test_tier3_cache_warmup(self, tier3_storage):
        """测试Tier 3缓存预热"""
        # 存储一些记忆
        for i in range(10):
            tier3_storage.store_memory({"content": f"Test memory {i}", "confidence": 0.9 - (i * 0.05), "id": str(i), "type": "general", "source": "user"})
        
        # 预热缓存
        warmup_count = tier3_storage.warmup_cache(limit=5)
        assert warmup_count > 0
        
        # 检查缓存统计
        stats = tier3_storage.get_cache_stats()
        assert stats["enabled"]
        assert stats["size"] > 0
