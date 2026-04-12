#!/usr/bin/env python3
"""
Quick demo script for Memory Classification Engine
"""

from memory_classification_engine import MemoryOrchestrator
import time

def print_header():
    """打印标题"""
    print("=" * 60)
    print("    Memory Classification Engine - Quick Demo    ")
    print("=" * 60)

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"{title:^60}")
    print("=" * 60)

def main():
    """主函数"""
    print_header()
    
    # 初始化引擎
    print("1. 初始化 MemoryOrchestrator...")
    memory = MemoryOrchestrator()
    print("   ✅ 引擎初始化完成")
    time.sleep(1)
    
    # 学习记忆
    print_section("2. 学习不同类型的记忆")
    
    test_messages = [
        ("我更喜欢使用双引号", "偏好类型"),
        ("张三是后端开发工程师", "关系类型"),
        ("不对，应该使用空格而不是制表符", "纠正类型"),
        ("Python 是我最喜欢的编程语言", "偏好类型"),
        ("代码应该保持简洁", "事实声明")
    ]
    
    for message, msg_type in test_messages:
        print(f"\n2.{test_messages.index((message, msg_type))+1} 学习{msg_type}:")
        print(f"   输入: '{message}'")
        result = memory.learn(message)
        print(f"   成功: {result['success']}")
        print(f"   存储: {result['stored']}")
        time.sleep(0.5)
    
    # 检索记忆
    print_section("3. 检索相关记忆")
    
    test_queries = ["双引号", "张三", "Python", "代码"]
    
    for query in test_queries:
        print(f"\n3.{test_queries.index(query)+1} 检索: '{query}'")
        memories = memory.recall(query, limit=3)
        print(f"   找到 {len(memories)} 条相关记忆:")
        for i, mem in enumerate(memories):
            print(f"   {i+1}. [{mem.get('memory_type')}] {mem.get('content')}")
        time.sleep(0.5)
    
    # 高级搜索
    print_section("4. 高级搜索")
    
    print("\n4.1 搜索代码风格相关记忆:")
    results = memory.search("代码风格", memory_types=["user_preference"], min_confidence=0.5)
    print(f"   找到 {len(results)} 条相关记忆:")
    for i, result in enumerate(results):
        print(f"   {i+1}. [{result.get('memory_type')}] {result.get('content')}")
    time.sleep(0.5)
    
    # 质量报告
    print_section("5. 生成质量报告")
    
    print("\n5.1 生成记忆质量报告:")
    report = memory.generate_quality_report(days=7)
    print(f"   总记忆数: {report.get('total_memories')}")
    print(f"   平均质量: {report.get('average_quality', 0):.2f}")
    print(f"   高质量记忆: {report.get('high_quality_memories', 0)}")
    print(f"   中等质量记忆: {report.get('medium_quality_memories', 0)}")
    print(f"   低质量记忆: {report.get('low_quality_memories', 0)}")
    time.sleep(0.5)
    
    # 导出导入
    print_section("6. 记忆导出导入")
    
    print("\n6.1 导出记忆:")
    export_data = memory.export_memories()
    print(f"   导出成功，数据长度: {len(export_data)} 字符")
    time.sleep(0.5)
    
    print("\n6.2 导入记忆:")
    import_result = memory.import_memories(export_data)
    print(f"   导入成功，导入 {import_result.get('imported_count', 0)} 条记忆")
    time.sleep(0.5)
    
    # 完成
    print_section("7. 演示完成")
    print("\n✅ Memory Classification Engine 核心功能演示完成！")
    print("\n主要功能:")
    print("  • 自动分类和存储有价值的信息")
    print("  • 快速检索相关记忆")
    print("  • 高级搜索和过滤")
    print("  • 记忆质量评估")
    print("  • 跨会话记忆迁移")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
