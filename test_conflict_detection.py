#!/usr/bin/env python3
"""Test script for conflict detection and resolution."""

from memory_classification_engine import MemoryClassificationEngine


def test_conflict_detection():
    """Test conflict detection functionality."""
    print("=== 测试冲突检测功能 ===")
    
    # Initialize engine
    engine = MemoryClassificationEngine()
    
    # Test case 1: Direct negation conflict
    print("\n1. 测试直接否定冲突:")
    message1 = "我喜欢巧克力"
    result1 = engine.process_message(message1)
    print(f"第一条消息处理结果: {result1['matches'][0]['content']}")
    
    message2 = "我不喜欢巧克力"
    result2 = engine.process_message(message2)
    print(f"第二条消息处理结果: {result2['matches'][0]['content']}")
    
    # Retrieve memories
    memories = engine.retrieve_memories("巧克力")
    print(f"\n检索到的记忆数量: {len(memories)}")
    for i, memory in enumerate(memories):
        print(f"记忆 {i+1}: {memory['content']}, 冲突状态: {memory.get('conflict_status', 'none')}")
    
    # Test case 2: Semantic conflict
    print("\n2. 测试语义冲突:")
    message3 = "Python是最好的编程语言"
    result3 = engine.process_message(message3)
    print(f"第三条消息处理结果: {result3['matches'][0]['content']}")
    
    message4 = "Python不是最好的编程语言"
    result4 = engine.process_message(message4)
    print(f"第四条消息处理结果: {result4['matches'][0]['content']}")
    
    # Retrieve memories
    memories2 = engine.retrieve_memories("Python")
    print(f"\n检索到的记忆数量: {len(memories2)}")
    for i, memory in enumerate(memories2):
        print(f"记忆 {i+1}: {memory['content']}, 冲突状态: {memory.get('conflict_status', 'none')}")
    
    # Test case 3: No conflict
    print("\n3. 测试无冲突情况:")
    message5 = "我喜欢编程"
    result5 = engine.process_message(message5)
    print(f"第五条消息处理结果: {result5['matches'][0]['content']}")
    
    message6 = "我喜欢阅读"
    result6 = engine.process_message(message6)
    print(f"第六条消息处理结果: {result6['matches'][0]['content']}")
    
    # Retrieve memories
    memories3 = engine.retrieve_memories("喜欢")
    print(f"\n检索到的记忆数量: {len(memories3)}")
    for i, memory in enumerate(memories3):
        print(f"记忆 {i+1}: {memory['content']}, 冲突状态: {memory.get('conflict_status', 'none')}")
    
    # Test case 4: Check memory weights
    print("\n4. 测试记忆权重:")
    for i, memory in enumerate(memories):
        print(f"记忆 {i+1}: {memory['content']}, 权重: {memory.get('weight', 0):.2f}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_conflict_detection()
