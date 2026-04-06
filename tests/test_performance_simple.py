"""Simplified performance tests for Memory Classification Engine."""

import pytest
import time
import psutil
import random
from memory_classification_engine import MemoryClassificationEngine


class TestPerformanceSimple:
    """Simplified performance tests."""
    
    @pytest.fixture
    def engine(self):
        """Create a memory classification engine for testing."""
        return MemoryClassificationEngine()
    
    def test_benchmark_message_processing(self, engine):
        """Test benchmark for message processing."""
        test_messages = [
            "我喜欢在代码中使用驼峰命名法",
            "记住，我不喜欢在代码中使用破折号",
            "我的生日是1990年1月1日",
            "我们公司有100名员工",
            "我负责管理产品开发团队"
        ]
        
        total_time = 0
        iterations = 50
        
        for i in range(iterations):
            message = random.choice(test_messages)
            start_time = time.time()
            engine.process_message(message)
            end_time = time.time()
            total_time += (end_time - start_time)
        
        avg_time = total_time / iterations
        print(f"\nBenchmark Message Processing:")
        print(f"Total time for {iterations} iterations: {total_time:.4f} seconds")
        print(f"Average time per message: {avg_time:.4f} seconds")
        
        # Assert that average processing time is within acceptable limits
        assert avg_time < 0.5, f"Average processing time too high: {avg_time:.4f} seconds"
    
    def test_load_test(self, engine):
        """Test system performance with moderate memory load."""
        # Create a moderate number of memories
        memory_count = 200
        
        print(f"\nLoad Test: Creating {memory_count} memories...")
        start_time = time.time()
        
        for i in range(memory_count):
            message = f"测试消息 {i}: 这是一条测试消息"
            engine.process_message(message)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Time to create {memory_count} memories: {total_time:.4f} seconds")
        print(f"Average time per memory: {total_time/memory_count:.4f} seconds")
        
        # Test retrieval performance after creating memory
        print("\nTesting retrieval performance...")
        query = "测试消息"
        start_time = time.time()
        results = engine.retrieve_memories(query, limit=5)
        end_time = time.time()
        retrieval_time = end_time - start_time
        
        print(f"Retrieval time: {retrieval_time:.4f} seconds")
        print(f"Number of results: {len(results)}")
        
        assert retrieval_time < 0.5, f"Retrieval time too high: {retrieval_time:.4f} seconds"
    
    def test_memory_usage(self, engine):
        """Test memory usage."""
        process = psutil.Process()
        
        # Get initial memory usage
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"\nMemory Usage Test:")
        print(f"Initial memory usage: {initial_memory:.2f} MB")
        
        # Create memories
        memory_count = 100
        print(f"Creating {memory_count} memories...")
        
        for i in range(memory_count):
            message = f"测试记忆 {i}: 这是一条测试消息"
            engine.process_message(message)
        
        # Get memory usage after creating memories
        memory_after_creation = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory usage after creation: {memory_after_creation:.2f} MB")
        print(f"Memory increase: {memory_after_creation - initial_memory:.2f} MB")
        
        # Memory usage should not grow exponentially
        assert memory_after_creation < initial_memory * 3, "Memory usage growing too fast"
    
    def test_performance_summary(self, engine):
        """Test performance summary."""
        print("\nPerformance Summary Test:")
        
        # Process some messages
        test_messages = ["我喜欢编程", "我喜欢狗", "我喜欢巧克力"]
        for message in test_messages:
            engine.process_message(message)
        
        # Retrieve memories
        for query in ["编程", "狗", "巧克力"]:
            engine.retrieve_memories(query)
        
        # Get stats
        stats = engine.get_stats()
        print("System Stats:")
        print(f"Working memory size: {stats['working_memory_size']}")
        print(f"Tier 2 memories: {stats['tier2'].get('total_memories', 0)}")
        print(f"Tier 3 memories: {stats['tier3'].get('total_memories', 0)}")
        print(f"Tier 4 relationships: {stats['tier4'].get('total_relationships', 0)}")
        print(f"Total memories: {stats['total_memories']}")
        print(f"Cache hits: {stats['cache'].get('hits', 0)}")
        print(f"Cache misses: {stats['cache'].get('misses', 0)}")
