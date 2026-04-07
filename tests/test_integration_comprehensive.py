"""综合集成测试"""

import pytest
import time
from memory_classification_engine import MemoryClassificationEngine


class TestIntegrationComprehensive:
    """综合集成测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        return MemoryClassificationEngine()
    
    def test_conversation_flow(self, engine):
        """测试完整的对话流程"""
        # 模拟一段完整的对话
        conversation = [
            "你好，我是张三",
            "我喜欢在代码中使用驼峰命名法",
            "我的生日是1990年1月1日",
            "我们决定下周一开始项目",
            "我不喜欢在代码中使用分号"
        ]
        
        for message in conversation:
            result = engine.process_message(message)
            assert result['message'] == message
            assert 'matches' in result
            assert isinstance(result['matches'], list)
    
    def test_memory_evolution(self, engine):
        """测试记忆进化功能"""
        # 反复提到相同的模式
        pattern_messages = [
            "我喜欢在代码中使用驼峰命名法",
            "变量名应该使用驼峰命名法",
            "函数名也要用驼峰命名法"
        ]
        
        for message in pattern_messages:
            result = engine.process_message(message)
            assert result['message'] == message
        
        # 检查是否生成了程序性记忆
        stats = engine.get_stats()
        assert stats['storage']['tier2']['total_memories'] > 0
    
    def test_search_relevance(self, engine):
        """测试搜索相关性"""
        # 添加一些测试数据
        test_data = [
            "Python是一种流行的编程语言",
            "Java是一种面向对象的语言",
            "JavaScript用于前端开发",
            "C++是一种高性能语言",
            "Python的语法很简洁"
        ]
        
        for data in test_data:
            engine.process_message(data)
        
        # 测试搜索
        results = engine.retrieve_memories("Python")
        assert len(results) > 0
        
        # 验证搜索结果包含相关内容
        python_related = any("Python" in str(result) for result in results)
        assert python_related
    
    def test_performance(self, engine):
        """测试系统性能"""
        start_time = time.time()
        
        # 处理3条消息
        for i in range(3):
            message = f"测试消息 {i}: 这是一条测试消息"
            result = engine.process_message(message)
            assert result['message'] == message
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 确保处理3条消息的时间不超过30秒（考虑到数据库锁定问题）
        assert total_time < 30.0, f"处理3条消息耗时 {total_time} 秒，超过预期"
    
    def test_error_handling(self, engine):
        """测试错误处理"""
        # 测试空消息
        result = engine.process_message("")
        assert 'matches' in result
        
        # 测试非常长的消息
        long_message = "a" * 10000
        result = engine.process_message(long_message)
        assert result['message'] == long_message
    
    def test_memory_management(self, engine):
        """测试记忆管理功能"""
        # 添加一些记忆
        test_messages = [
            "我喜欢巧克力",
            "我不喜欢咖啡",
            "我喜欢狗"
        ]
        
        for message in test_messages:
            engine.process_message(message)
        
        # 获取统计信息
        stats = engine.get_stats()
        assert stats['storage']['total_memories'] >= 3
        
        # 检索记忆
        memories = engine.retrieve_memories("喜欢")
        assert len(memories) >= 2
    
    def test_plugin_integration(self, engine):
        """测试插件集成"""
        # 测试情感分析插件
        test_messages = [
            "我很高兴",
            "我很生气",
            "我感觉一般"
        ]
        
        for message in test_messages:
            result = engine.process_message(message)
            assert 'plugin_results' in result
            assert 'sentiment_analyzer' in result['plugin_results']
    
    def test_cross_language(self, engine):
        """测试跨语言支持"""
        # 测试中文消息
        chinese_messages = [
            "我喜欢编程",
            "今天天气很好",
            "我不喜欢加班"
        ]
        
        for message in chinese_messages:
            result = engine.process_message(message)
            assert result['message'] == message
            assert 'matches' in result
    
    def test_context_handling(self, engine):
        """测试上下文处理"""
        # 测试带上下文的消息处理
        context = {
            "conversation_id": "test_conv_123",
            "user_id": "user_456",
            "timestamp": time.time()
        }
        
        message = "我喜欢编程"
        result = engine.process_message(message, context=context)
        assert result['message'] == message
        assert 'matches' in result
    
    def test_memory_persistence(self, engine):
        """测试记忆持久化"""
        # 添加一些记忆
        test_message = "测试记忆持久化"
        engine.process_message(test_message)
        
        # 创建新的引擎实例
        new_engine = MemoryClassificationEngine()
        
        # 检索记忆
        memories = new_engine.retrieve_memories("持久化")
        assert len(memories) > 0
