import pytest
import os
import shutil
from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.storage.tier3 import Tier3Storage

class TestIntegration:
    @pytest.fixture
    def engine(self):
        # 清理测试数据
        if os.path.exists('./data'):
            shutil.rmtree('./data')
        
        engine = MemoryClassificationEngine()
        yield engine
        
        # 清理测试数据
        if os.path.exists('./data'):
            shutil.rmtree('./data')
    
    def test_process_message(self, engine):
        result = engine.process_message("I like using Python for web development")
        assert "message" in result
        assert "matches" in result
        assert len(result["matches"]) > 0
        assert result["working_memory_size"] > 0
    
    def test_retrieve_memories(self, engine):
        # 存储一些记忆
        engine.process_message("I like Python")
        engine.process_message("I love JavaScript")
        engine.process_message("I prefer React")
        
        # 检索记忆
        memories = engine.retrieve_memories("Python")
        assert len(memories) > 0
        assert any("Python" in memory["content"] for memory in memories)
    
    def test_manage_memory(self, engine):
        # 存储记忆
        result = engine.process_message("Test memory")
        memory_id = result["matches"][0]["id"]
        
        # 查看记忆
        view_result = engine.manage_memory("view", memory_id)
        assert view_result["success"]
        assert view_result["memory"]["id"] == memory_id
        
        # 编辑记忆
        edit_result = engine.manage_memory("edit", memory_id, {"content": "Updated test memory"})
        assert edit_result["success"]
        assert edit_result["memory"]["content"] == "Updated test memory"
        
        # 删除记忆
        delete_result = engine.manage_memory("delete", memory_id)
        assert delete_result["success"]
    
    def test_get_stats(self, engine):
        # 存储一些记忆
        engine.process_message("Test 1")
        engine.process_message("Test 2")
        
        stats = engine.get_stats()
        assert "working_memory_size" in stats
        assert "tier2" in stats
        assert "tier3" in stats
        assert "total_memories" in stats
    
    def test_fts_search(self):
        # 清理测试数据
        if os.path.exists('./data'):
            shutil.rmtree('./data')
        
        storage = Tier3Storage()
        
        # 存储一些英文记忆
        storage.store_memory({"content": "I like Python programming", "confidence": 0.9, "id": "1", "type": "user_preference", "source": "user"})
        storage.store_memory({"content": "Python is a great language", "confidence": 0.8, "id": "2", "type": "fact_declaration", "source": "user"})
        storage.store_memory({"content": "I love JavaScript", "confidence": 0.7, "id": "3", "type": "user_preference", "source": "user"})
        
        # 测试FTS搜索
        results = storage.retrieve_memories("Python")
        assert len(results) >= 2
        assert any("Python" in result["content"] for result in results)
        
        # 清理测试数据
        if os.path.exists('./data'):
            shutil.rmtree('./data')
    
    def test_cache_warmup(self):
        # 清理测试数据
        if os.path.exists('./data'):
            shutil.rmtree('./data')
        
        storage = Tier3Storage()
        
        # 存储一些记忆
        for i in range(10):
            storage.store_memory({"content": f"Test memory {i}", "confidence": 0.9 - (i * 0.05), "id": str(i), "type": "general", "source": "user"})
        
        # 预热缓存
        warmup_count = storage.warmup_cache(limit=5)
        assert warmup_count > 0
        
        # 检查缓存统计
        stats = storage.get_cache_stats()
        assert stats["enabled"]
        assert stats["size"] > 0
        
        # 清理测试数据
        if os.path.exists('./data'):
            shutil.rmtree('./data')
