#!/usr/bin/env python3
"""
示例：使用个性化推荐系统

本示例展示如何：
1. 记录用户行为
2. 获取个性化推荐
3. 分析用户行为
"""

from memory_classification_engine import MemoryClassificationEngine

# 初始化引擎
engine = MemoryClassificationEngine()

# 示例用户ID
user_id = "user_123"

# 示例1: 处理一些用户消息，创建记忆
print("=== 示例1: 创建一些记忆 ===")

messages = [
    "我喜欢在代码中使用驼峰命名法",
    "我不喜欢在代码中使用分号",
    "我喜欢巧克力",
    "我喜欢狗",
    "我喜欢编程"
]

memory_ids = []
for message in messages:
    result = engine.process_message(message, context={"tenant_id": user_id})
    if result.get("matches"):
        for match in result["matches"]:
            memory_id = match.get("id")
            memory_ids.append(memory_id)
            print(f"创建记忆: {match.get('content')} (ID: {memory_id})")

print()

# 示例2: 记录用户行为
print("=== 示例2: 记录用户行为 ===")

# 模拟用户查看记忆
for i, memory_id in enumerate(memory_ids):
    # 记录不同类型的行为
    actions = ["view", "interact", "like", "share"]
    action = actions[i % len(actions)]
    result = engine.record_user_behavior(user_id, memory_id, action)
    print(f"记录行为: {action} 记忆 {memory_id} - {result.get('message')}")

print()

# 示例3: 获取个性化推荐
print("=== 示例3: 获取个性化推荐 ===")

# 基于用户历史行为的推荐
recommendations = engine.get_recommendations(user_id, limit=3)
print("基于用户行为的推荐:")
for i, rec in enumerate(recommendations):
    print(f"{i+1}. {rec.get('content')} (推荐分数: {rec.get('recommendation_score', 0):.4f})")

print()

# 基于查询的个性化推荐
query = "代码风格"
recommendations_with_query = engine.get_recommendations(user_id, query=query, limit=3)
print(f"基于查询 '{query}' 的个性化推荐:")
for i, rec in enumerate(recommendations_with_query):
    print(f"{i+1}. {rec.get('content')} (推荐分数: {rec.get('recommendation_score', 0):.4f}, 相关性: {rec.get('relevance_score', 0):.4f})")

print()

# 示例4: 获取用户行为摘要
print("=== 示例4: 用户行为摘要 ===")

behavior_summary = engine.get_user_behavior_summary(user_id)
print(f"用户ID: {behavior_summary.get('user_id')}")
print(f"总交互次数: {behavior_summary.get('total_interactions')}")
print(f"最后活动时间: {behavior_summary.get('last_activity')}")
print(f"偏好记忆类型: {behavior_summary.get('preferred_memory_types')}")

print()
print("=== 示例完成 ===")
print("推荐系统已经成功集成到记忆分类引擎中，可以基于用户行为提供个性化推荐。")
