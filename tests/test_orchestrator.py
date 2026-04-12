#!/usr/bin/env python3
"""
测试 MemoryOrchestrator 功能
"""

from memory_classification_engine import MemoryOrchestrator, get_orchestrator
import json

def test_memory_orchestrator():
    """测试记忆编排器功能"""
    print("=" * 60)
    print("Testing MemoryOrchestrator")
    print("=" * 60)
    
    # 初始化编排器
    print("1. Initializing MemoryOrchestrator...")
    orchestrator = MemoryOrchestrator()
    print("   ✅ MemoryOrchestrator initialized")
    
    # 测试学习功能
    print("\n2. Testing learn() function...")
    test_messages = [
        "我更喜欢使用双引号",
        "张三是后端开发工程师",
        "不，应该使用单引号而不是双引号"
    ]
    
    for i, message in enumerate(test_messages):
        result = orchestrator.learn(message)
        print(f"   Message {i+1}: '{message}'")
        print(f"   Success: {result['success']}")
        if result['stored']:
            print(f"   Stored: {len(result['classification']['matches'])} memory(ies)")
        else:
            print(f"   Stored: No memory stored")
    
    # 测试回忆功能
    print("\n3. Testing recall() function...")
    queries = ["双引号", "张三", "单引号"]
    
    for query in queries:
        memories = orchestrator.recall(query)
        print(f"   Query: '{query}'")
        print(f"   Found {len(memories)} memory(ies)")
        for j, memory in enumerate(memories):
            print(f"     {j+1}. [{memory.get('memory_type')}] {memory.get('content', '')}")
    
    # 测试搜索功能
    print("\n4. Testing search() function...")
    search_terms = ["引号", "开发"]
    
    for term in search_terms:
        results = orchestrator.search(term, min_confidence=0.5)
        print(f"   Search term: '{term}'")
        print(f"   Found {len(results)} result(s)")
        for k, result in enumerate(results):
            print(f"     {k+1}. [{result.get('memory_type')}] {result.get('content', '')} (confidence: {result.get('confidence', 0):.2f})")
    
    # 测试批量学习
    print("\n5. Testing batch_learn() function...")
    batch_messages = [
        "Python 是我最喜欢的编程语言",
        "我不喜欢使用分号",
        "代码应该保持简洁"
    ]
    
    batch_results = orchestrator.batch_learn(batch_messages)
    print(f"   Batch learned {len(batch_results)} messages")
    for l, result in enumerate(batch_results):
        print(f"     {l+1}. Success: {result['success']}, Stored: {result['stored']}")
    
    # 测试统计功能
    print("\n6. Testing get_stats() function...")
    stats = orchestrator.get_stats()
    print(f"   Stats: {json.dumps(stats, indent=2)}")
    
    # 测试全局编排器实例
    print("\n7. Testing get_orchestrator() function...")
    global_orchestrator = get_orchestrator()
    print("   ✅ Global orchestrator obtained")
    test_memory = global_orchestrator.recall("Python")
    print(f"   Found {len(test_memory)} memory(ies) for 'Python'")
    
    print("\n" + "=" * 60)
    print("MemoryOrchestrator tests completed!")
    print("=" * 60)

def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    orchestrator = MemoryOrchestrator()
    
    # 测试无效的记忆 ID
    print("\n1. Testing forget with invalid memory ID...")
    result = orchestrator.forget("invalid_memory_id")
    print(f"   Success: {result['success']}")
    print(f"   Message: {result.get('message', 'No message')}")
    
    # 测试空查询
    print("\n2. Testing recall with empty query...")
    memories = orchestrator.recall("")
    print(f"   Found {len(memories)} memory(ies)")
    
    print("\n" + "=" * 60)
    print("Error handling tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_memory_orchestrator()
    test_error_handling()
