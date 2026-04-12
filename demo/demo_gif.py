#!/usr/bin/env python3
"""
Demo script for recording GIF
"""

import time

def print_header():
    """打印标题"""
    print("=" * 60)
    print("    Memory Classification Engine - Demo    ")
    print("=" * 60)

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"{title:^60}")
    print("=" * 60)

def main():
    """主函数"""
    print_header()
    
    # 模拟初始化
    print("1. 安装 Memory Classification Engine...")
    time.sleep(1)
    print("   $ pip install memory-classification-engine")
    time.sleep(1)
    print("   ✅ 安装完成")
    time.sleep(1)
    
    print("\n2. 初始化引擎...")
    time.sleep(1)
    print("   >>> from memory_classification_engine import MemoryOrchestrator")
    time.sleep(1)
    print("   >>> memory = MemoryOrchestrator()")
    time.sleep(1)
    print("   ✅ 引擎初始化完成")
    time.sleep(1)
    
    # 模拟学习记忆
    print_section("3. 学习不同类型的记忆")
    
    test_messages = [
        ("我更喜欢使用双引号", "偏好类型"),
        ("张三是后端开发工程师", "关系类型"),
        ("不对，应该使用空格而不是制表符", "纠正类型")
    ]
    
    for message, msg_type in test_messages:
        print(f"\n3.{test_messages.index((message, msg_type))+1} 学习{msg_type}:")
        print(f"   >>> memory.learn('{message}')")
        time.sleep(1)
        print("   {success: True, stored: True}")
        time.sleep(1)
    
    # 模拟检索记忆
    print_section("4. 检索相关记忆")
    
    test_queries = ["双引号", "张三", "代码风格"]
    
    for query in test_queries:
        print(f"\n4.{test_queries.index(query)+1} 检索: '{query}'")
        print(f"   >>> memory.recall('{query}')")
        time.sleep(1)
        if query == "双引号":
            print("   [{'memory_type': 'user_preference', 'content': '我更喜欢使用双引号'}]")
        elif query == "张三":
            print("   [{'memory_type': 'relationship', 'content': '张三是后端开发工程师'}]")
        else:
            print("   [{'memory_type': 'user_preference', 'content': '我更喜欢使用双引号'},")
            print("    {'memory_type': 'correction', 'content': '不对，应该使用空格而不是制表符'}]")
        time.sleep(1)
    
    # 模拟高级功能
    print_section("5. 高级功能")
    
    print("\n5.1 生成质量报告:")
    print("   >>> report = memory.generate_quality_report()")
    time.sleep(1)
    print("   {'total_memories': 3, 'average_quality': 0.85, 'high_quality_memories': 3}")
    time.sleep(1)
    
    print("\n5.2 导出记忆:")
    print("   >>> export_data = memory.export_memories()")
    time.sleep(1)
    print("   ✅ 导出成功，可导入到其他 Agent")
    time.sleep(1)
    
    # 完成
    print_section("6. 演示完成")
    print("\n✅ Memory Classification Engine 核心功能演示完成！")
    print("\n主要特点:")
    print("  • 自动分类和存储有价值的信息")
    print("  • 快速检索相关记忆")
    print("  • 记忆质量评估")
    print("  • 跨会话记忆迁移")
    print("  • 60%+ 零 LLM 调用，低成本运行")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
