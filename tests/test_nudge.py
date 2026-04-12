#!/usr/bin/env python3
"""
测试 Nudge 主动复习机制
"""

from memory_classification_engine import MemoryClassificationEngine
import time
import sys
import os

# 重定向 stderr 到 /dev/null 以减少错误信息
sys.stderr = open(os.devnull, 'w')

def test_nudge_mechanism():
    print("Testing Nudge mechanism...")
    
    # 初始化引擎
    engine = MemoryClassificationEngine()
    
    # 添加一些测试记忆
    print("\n1. Adding test memories...")
    
    # 添加事实声明（容易过时）
    engine.process_message("Python 3.9 是最新版本")
    
    # 添加时间敏感内容
    engine.process_message("今天是 2026 年 4 月 12 日")
    
    # 添加任务模式
    engine.process_message("我们每周一上午 9 点开会")
    
    # 添加偏好（不容易过时）
    engine.process_message("我喜欢使用双引号")
    
    print("   ✅ Added 4 test memories")
    
    # 模拟时间流逝（将记忆标记为旧记忆）
    print("\n2. Simulating time passage...")
    
    # 手动修改消息历史，触发 nudge
    engine.message_history = [{'message': 'test'}] * 50  # 触发 50 消息阈值
    
    # 手动设置 last_nudge_time 为 2 天前
    engine.last_nudge_time = time.time() - 172800  # 2 days
    
    print("   ✅ Simulated time passage")
    
    # 触发 nudge
    print("\n3. Triggering Nudge mechanism...")
    engine._run_nudge()
    
    print("\n4. Checking nudge results...")
    
    # 检查是否有记忆被标记为需要审查
    recent_memories = engine.storage_coordinator.retrieve_memories(query="", limit=10)
    
    print(f"   Found {len(recent_memories)} memories in storage")
    
    for memory in recent_memories:
        content = memory.get('content', '')
        needs_review = memory.get('needs_review', False)
        weight = memory.get('weight', 1.0)
        
        print(f"   - {content[:50]}... (needs_review: {needs_review}, weight: {weight:.2f})")
    
    print("\n✅ Nudge mechanism test completed!")

if __name__ == "__main__":
    test_nudge_mechanism()
