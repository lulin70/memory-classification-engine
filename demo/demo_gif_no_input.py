#!/usr/bin/env python3
"""
GIF-ready demo script for memory recall functionality (no input required).

This script generates clean output suitable for GIF recording,
demonstrating the memory recall functionality in two scenarios:
1. First time use (empty memory state)
2. After one week of use (rich memory state)
"""

import os
import sys
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def demo_empty_state():
    """Demonstrate memory recall with empty state."""
    print("=" * 60)
    print("MCE Memory Recall - First Time Use")
    print("=" * 60)
    print()
    print("📝 MCE Memory Recall")
    print()
    print("## 已加载的记忆 (0/5)")
    print("- 还没有任何记忆记录。")
    print("- 随着我们对话，我会记住你的偏好、决策和重要信息。")
    print()
    print("## 统计信息")
    print("- 过滤噪音: 0条")
    print("- LLM调用: 0次")
    print("- 处理消息: 0条")
    print("- 本周新增: 0条记忆")
    print()
    print("💡 这些记忆将影响我的回复，确保一致性体验")
    print()


def demo_rich_state():
    """Demonstrate memory recall with rich state after one week of use."""
    print("=" * 60)
    print("MCE Memory Recall - After One Week of Use")
    print("=" * 60)
    print()
    print("📝 MCE Memory Recall")
    print()
    print("## 已加载的记忆 (7/7)")
    print("- [偏好] 使用双引号而非单引号          置信度0.95 规则层   引用8次")
    print("- [偏好] 不喜欢过度设计的架构            置信度0.92 语义层   引用5次")
    print("- [决策] 项目采用Python技术栈             置信度0.89 模式层   +3关联")
    print("- [纠正] 否决复杂方案->倾向简化           置信度0.89 模式层")
    print("- [关系] 张三负责后端，李四做前端         置信度0.95 规则层")
    print("- [任务模式] 每次部署前跑测试套件         置信度0.91 自动晋升规则")
    print()
    print("## 统计信息")
    print("- 过滤噪音: 23条")
    print("- LLM调用: 28次(8.2%)")
    print("- 处理消息: 342条")
    print("- 本周新增: 7条记忆")
    print()
    print("💡 这些记忆将影响我的回复，确保一致性体验")
    print()


def main():
    """Main function."""
    print("Memory Classification Engine - Recall Demo")
    print()
    
    # Demo empty state
    demo_empty_state()
    print("Loading rich state demo...")
    time.sleep(2)
    
    # Clear screen (works on most terminals)
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Demo rich state
    demo_rich_state()
    print()
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
