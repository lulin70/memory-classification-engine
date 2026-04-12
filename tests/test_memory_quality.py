#!/usr/bin/env python3
"""
测试记忆质量自评估系统
"""

from memory_classification_engine import MemoryOrchestrator
from memory_classification_engine.utils.memory_quality import MemoryQualityManager, get_memory_quality_manager
import json

def test_memory_quality_system():
    """测试记忆质量自评估系统"""
    print("=" * 60)
    print("Testing Memory Quality Assessment System")
    print("=" * 60)
    
    # 初始化编排器和质量管理器
    print("1. Initializing MemoryOrchestrator and MemoryQualityManager...")
    orchestrator = MemoryOrchestrator()
    quality_manager = get_memory_quality_manager()
    print("   ✅ MemoryOrchestrator and MemoryQualityManager initialized")
    
    # 测试学习和检索，生成使用数据
    print("\n2. Testing learn and recall to generate usage data...")
    test_messages = [
        "我更喜欢使用双引号",
        "张三是后端开发工程师",
        "Python 是我最喜欢的编程语言",
        "代码应该保持简洁"
    ]
    
    memory_ids = []
    for i, message in enumerate(test_messages):
        result = orchestrator.learn(message)
        print(f"   Message {i+1}: '{message}' - Stored: {result['stored']}")
        if result['stored'] and result['classification'].get('matches'):
            for match in result['classification']['matches']:
                memory_ids.append(match.get('id'))
    
    # 模拟检索，生成使用数据
    print("\n3. Testing recall to track memory usage...")
    queries = ["双引号", "张三", "Python", "代码"]
    
    for query in queries:
        memories = orchestrator.recall(query)
        print(f"   Query: '{query}' - Found {len(memories)} memory(ies)")
        for j, memory in enumerate(memories[:2]):
            print(f"     {j+1}. [{memory.get('memory_type')}] {memory.get('content', '')[:50]}...")
    
    # 测试反馈追踪
    print("\n4. Testing feedback tracking...")
    if memory_ids:
        # 为第一个记忆添加正面反馈
        feedback_result = orchestrator.track_feedback(memory_ids[0], "positive", {"context": "User liked this memory"})
        print(f"   Tracked positive feedback for memory {memory_ids[0]}: {feedback_result['success']}")
        
        # 为第二个记忆添加负面反馈
        if len(memory_ids) > 1:
            feedback_result = orchestrator.track_feedback(memory_ids[1], "negative", {"context": "User disliked this memory"})
            print(f"   Tracked negative feedback for memory {memory_ids[1]}: {feedback_result['success']}")
    
    # 测试记忆质量计算
    print("\n5. Testing memory quality calculation...")
    if memory_ids:
        for memory_id in memory_ids[:3]:
            quality = orchestrator.get_memory_quality(memory_id)
            if quality:
                print(f"   Memory {memory_id} quality:")
                print(f"     Overall: {quality['overall_quality']:.2f}")
                print(f"     Usage frequency: {quality['usage_frequency']:.2f}")
                print(f"     Success rate: {quality['success_rate']:.2f}")
                print(f"     Feedback score: {quality['feedback_score']:.2f}")
                print(f"     Recency score: {quality['recency_score']:.2f}")
                print(f"     Diversity score: {quality['diversity_score']:.2f}")
            else:
                print(f"   Memory {memory_id} quality: No data")
    
    # 测试质量报告生成
    print("\n6. Testing quality report generation...")
    report = orchestrator.generate_quality_report(days=7)
    print(f"   Quality report for last 7 days:")
    for key, value in report.items():
        if key not in ['generated_at', 'error']:
            print(f"     {key}: {value}")
    
    # 测试低价值记忆报告
    print("\n7. Testing low value memory report...")
    low_value = orchestrator.generate_low_value_report(threshold=0.5)
    print(f"   Low value memories (threshold: 0.5): {len(low_value)}")
    for mem in low_value[:3]:
        print(f"     {mem['memory_id']}: {mem['quality_metrics']['overall_quality']:.2f}")
    
    # 测试重置追踪
    print("\n8. Testing reset tracking...")
    if memory_ids:
        quality_manager.reset_tracking(memory_ids[0])
        print(f"   Reset tracking for memory {memory_ids[0]}")
        quality = orchestrator.get_memory_quality(memory_ids[0])
        print(f"   Memory {memory_ids[0]} quality after reset: {quality}")
    
    print("\n" + "=" * 60)
    print("Memory Quality Assessment System tests completed!")
    print("=" * 60)

def test_quality_manager_directly():
    """直接测试 MemoryQualityManager"""
    print("\n" + "=" * 60)
    print("Testing MemoryQualityManager Directly")
    print("=" * 60)
    
    manager = MemoryQualityManager()
    
    # 模拟使用数据
    memory_ids = ["mem_1", "mem_2", "mem_3"]
    
    # 模拟记忆使用
    print("1. Simulating memory usage...")
    for i, memory_id in enumerate(memory_ids):
        for j in range(i + 1):  # 不同的使用频率
            manager.track_memory_usage(memory_id, f"query_{j}", result=True)
            
        # 模拟反馈
        if i == 0:
            manager.track_feedback(memory_id, "positive")
        elif i == 1:
            manager.track_feedback(memory_id, "neutral")
        else:
            manager.track_feedback(memory_id, "negative")
    
    # 计算质量
    print("\n2. Calculating memory quality...")
    for memory_id in memory_ids:
        quality = manager.calculate_memory_quality(memory_id, {'id': memory_id})
        print(f"   Memory {memory_id} quality: {quality['overall_quality']:.2f}")
    
    # 生成低价值报告
    print("\n3. Generating low value report...")
    low_value = manager.generate_low_value_report()
    print(f"   Low value memories: {len(low_value)}")
    for mem in low_value:
        print(f"     {mem['memory_id']}: {mem['quality_metrics']['overall_quality']:.2f}")
    
    # 生成质量报告
    print("\n4. Generating quality report...")
    report = manager.generate_quality_report()
    print("   Quality report:")
    for key, value in report.items():
        if key != 'generated_at':
            print(f"     {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Direct MemoryQualityManager tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_memory_quality_system()
    test_quality_manager_directly()
