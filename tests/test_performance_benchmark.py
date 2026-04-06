"""Benchmark performance test for Memory Classification Engine."""

import time
import random
from memory_classification_engine import MemoryClassificationEngine


def test_benchmark_message_processing():
    """Test benchmark for message processing."""
    engine = MemoryClassificationEngine()
    
    test_messages = [
        "我喜欢在代码中使用驼峰命名法",
        "记住，我不喜欢在代码中使用破折号",
        "我的生日是1990年1月1日",
        "我们公司有100名员工",
        "我负责管理产品开发团队"
    ]
    
    total_time = 0
    iterations = 20
    
    print(f"Running benchmark with {iterations} iterations...")
    
    for i in range(iterations):
        message = random.choice(test_messages)
        start_time = time.time()
        engine.process_message(message)
        end_time = time.time()
        iteration_time = end_time - start_time
        total_time += iteration_time
        print(f"Iteration {i+1}/{iterations}: {iteration_time:.4f} seconds")
    
    avg_time = total_time / iterations
    print(f"\nBenchmark Results:")
    print(f"Total time for {iterations} iterations: {total_time:.4f} seconds")
    print(f"Average time per message: {avg_time:.4f} seconds")
    print(f"Messages per second: {iterations / total_time:.2f}")
    
    # 检查性能是否在可接受范围内
    assert avg_time < 0.5, f"Average processing time too high: {avg_time:.4f} seconds"
    print("\n✅ Performance test passed!")


if __name__ == "__main__":
    test_benchmark_message_processing()
