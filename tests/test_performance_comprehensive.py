"""Comprehensive performance tests for Memory Classification Engine."""

import pytest
import time
import psutil
import random
import string
import concurrent.futures
from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.utils.performance import PerformanceMonitor


class TestPerformanceComprehensive:
    """Comprehensive performance tests."""
    
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
            "我负责管理产品开发团队",
            "我不喜欢加班",
            "我讨厌冗长的会议",
            "C++是一种高性能语言",
            "Python的语法很简洁",
            "Java是一种面向对象的语言"
        ]
        
        total_time = 0
        iterations = 100
        
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
    
    def test_load_test_with_large_memory(self, engine):
        """Test system performance with large memory load."""
        # Create a large number of memories
        memory_count = 1000
        
        print(f"\nLoad Test: Creating {memory_count} memories...")
        start_time = time.time()
        
        for i in range(memory_count):
            message = f"测试消息 {i}: 这是一条测试消息"
            engine.process_message(message)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Time to create {memory_count} memories: {total_time:.4f} seconds")
        print(f"Average time per memory: {total_time/memory_count:.4f} seconds")
        
        # Test retrieval performance after creating large memory
        print("\nTesting retrieval performance with large memory...")
        query = "测试消息"
        start_time = time.time()
        results = engine.retrieve_memories(query, limit=10)
        end_time = time.time()
        retrieval_time = end_time - start_time
        
        print(f"Retrieval time: {retrieval_time:.4f} seconds")
        print(f"Number of results: {len(results)}")
        
        assert retrieval_time < 1.0, f"Retrieval time too high: {retrieval_time:.4f} seconds"
    
    def test_memory_usage(self, engine):
        """Test memory usage under different loads."""
        process = psutil.Process()
        
        # Get initial memory usage
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"\nMemory Usage Test:")
        print(f"Initial memory usage: {initial_memory:.2f} MB")
        
        # Create memories
        memory_count = 500
        print(f"Creating {memory_count} memories...")
        
        for i in range(memory_count):
            message = f"测试记忆 {i}: {' '.join(random.choices(string.ascii_letters, k=10))}"
            engine.process_message(message)
        
        # Get memory usage after creating memories
        memory_after_creation = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory usage after creation: {memory_after_creation:.2f} MB")
        print(f"Memory increase: {memory_after_creation - initial_memory:.2f} MB")
        
        # Test retrieval and check memory usage
        print("Testing retrieval...")
        for i in range(100):
            query = f"测试记忆 {random.randint(0, memory_count-1)}"
            engine.retrieve_memories(query)
        
        memory_after_retrieval = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory usage after retrieval: {memory_after_retrieval:.2f} MB")
        print(f"Memory increase after retrieval: {memory_after_retrieval - memory_after_creation:.2f} MB")
        
        # Memory usage should not grow exponentially
        assert memory_after_retrieval < initial_memory * 3, "Memory usage growing too fast"
    
    def test_concurrent_performance(self, engine):
        """Test system performance under concurrent requests."""
        test_messages = [
            "我喜欢编程",
            "我喜欢狗",
            "我喜欢巧克力",
            "我不喜欢咖啡",
            "我很高兴",
            "情感: 我很生气",
            "决定: 我们决定下周一开始项目",
            "在代码中使用分号",
            "在代码中使用驼峰命名法",
            "函数名也要用驼峰命名法"
        ]
        
        def process_message():  # 移除 unused parameter
            message = random.choice(test_messages)
            start_time = time.time()
            engine.process_message(message)
            return time.time() - start_time
        
        def retrieve_memories():  # 移除 unused parameter
            query = random.choice(["编程", "狗", "巧克力", "代码风格", "决定"])
            start_time = time.time()
            engine.retrieve_memories(query)
            return time.time() - start_time
        
        # Test concurrent processing
        print("\nConcurrent Performance Test:")
        concurrent_count = 50
        
        # Test concurrent message processing
        print(f"Testing {concurrent_count} concurrent message processing...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_message) for _ in range(concurrent_count)]
            process_times = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        avg_time = total_time / concurrent_count
        print(f"Total time: {total_time:.4f} seconds")
        print(f"Average time per process: {avg_time:.4f} seconds")
        print(f"Throughput: {concurrent_count / total_time:.2f} messages/second")
        
        # Test concurrent memory retrieval
        print(f"\nTesting {concurrent_count} concurrent memory retrievals...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(retrieve_memories) for _ in range(concurrent_count)]
            retrieve_times = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        avg_time = total_time / concurrent_count
        print(f"Total time: {total_time:.4f} seconds")
        print(f"Average time per retrieval: {avg_time:.4f} seconds")
        print(f"Throughput: {concurrent_count / total_time:.2f} retrievals/second")
    
    def test_different_message_types_performance(self, engine):
        """Test performance for different message types."""
        message_types = {
            "user_preference": ["我喜欢在代码中使用驼峰命名法", "记住，我不喜欢在代码中使用破折号"],
            "fact_declaration": ["我的生日是1990年1月1日", "我们公司有100名员工"],
            "decision": ["决定: 我们决定下周一开始项目", "我们选择使用Python作为开发语言"],
            "relationship": ["我负责管理产品开发团队", "张三是我的同事"],
            "sentiment_marker": ["我很高兴", "情感: 我很生气"],
            "task_pattern": ["每周一我们有团队会议", "每天下午3点我需要检查邮件"],
            "correction": ["不对，应该是使用单引号而不是双引号", "我之前说的不对，应该是这样"]
        }
        
        print("\nDifferent Message Types Performance Test:")
        
        for message_type, messages in message_types.items():
            total_time = 0
            iterations = 20
            
            for i in range(iterations):
                message = random.choice(messages)
                start_time = time.time()
                result = engine.process_message(message)
                end_time = time.time()
                total_time += (end_time - start_time)
            
            avg_time = total_time / iterations
            print(f"{message_type}: {avg_time:.4f} seconds per message")
    
    def test_performance_monitor_integration(self, engine):
        """Test performance monitor integration."""
        print("\nPerformance Monitor Integration Test:")
        
        # Process some messages to generate metrics
        test_messages = ["我喜欢编程", "我喜欢狗", "我喜欢巧克力"]
        for message in test_messages:
            engine.process_message(message)
        
        # Retrieve memories to generate more metrics
        for query in ["编程", "狗", "巧克力"]:
            engine.retrieve_memories(query)
        
        # Get and print metrics
        metrics = engine.performance_monitor.get_metrics()
        print("Performance Metrics:")
        print(f"Memory usage: {metrics['memory']['usage']:.2f} MB")
        print(f"CPU usage: {metrics['cpu']['usage']:.2f}%")
        print(f"Disk usage: {metrics['disk']['usage']:.2f}%")
        print(f"Messages processed: {metrics['throughput'].get('messages_processed', 0)}")
        print(f"Queries processed: {metrics['throughput'].get('queries_processed', 0)}")
        
        # Check response times
        if 'process_message' in metrics['response_times']:
            process_times = metrics['response_times']['process_message']
            avg_process_time = sum(process_times) / len(process_times)
            print(f"Average process_message time: {avg_process_time:.4f} seconds")
        
        if 'retrieve_memories' in metrics['response_times']:
            retrieve_times = metrics['response_times']['retrieve_memories']
            avg_retrieve_time = sum(retrieve_times) / len(retrieve_times)
            print(f"Average retrieve_memories time: {avg_retrieve_time:.4f} seconds")
