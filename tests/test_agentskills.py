#!/usr/bin/env python3
"""
测试 agentskills.io 格式兼容性
"""

from memory_classification_engine.utils.agentskills import AgentSkillsIO
import os

# 测试 MCE 规则转换为 agentskills.io 格式
def test_mce_to_agentskills():
    print("Testing MCE to agentskills.io conversion...")
    
    # 示例 MCE 规则
    mce_rule = {
        'name': 'preference-double-quotes',
        'description': 'Detect preference for double quotes',
        'pattern': '我更喜欢使用双引号',
        'memory_type': 'user_preference',
        'tier': 2,
        'action': 'extract',
        'author': 'MCE Team',
        'version': '1.0.0',
        'example': '我更喜欢使用双引号而不是单引号'
    }
    
    # 转换为 agentskills.io 格式
    skill = AgentSkillsIO.mce_to_agentskills(mce_rule)
    
    print("  Converted skill:")
    print(f"    Name: {skill['name']}")
    print(f"    Description: {skill['description']}")
    print(f"    Category: {skill['category']}")
    print(f"    InputSchema: {skill['inputSchema']}")
    print(f"    OutputSchema: {skill['outputSchema']}")
    print(f"    Examples: {skill['examples']}")
    
    # 保存为 SKILL.md
    output_path = 'test_skill.md'
    AgentSkillsIO.save_skill(skill, output_path)
    print(f"  ✅ Saved to {output_path}")
    
    # 读取回来
    loaded_skill = AgentSkillsIO.load_skill(output_path)
    print(f"  ✅ Loaded skill: {loaded_skill['name']}")
    
    # 清理测试文件
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"  ✅ Cleaned up {output_path}")

# 测试 agentskills.io 格式转换为 MCE 规则
def test_agentskills_to_mce():
    print("\nTesting agentskills.io to MCE conversion...")
    
    # 示例 agentskills.io 技能
    skill = {
        'name': 'feedback-handler',
        'description': 'Handle user feedback',
        'author': 'AgentSkills Team',
        'version': '1.0.0',
        'category': 'feedback',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'description': 'User message'
                }
            },
            'required': ['message']
        },
        'outputSchema': {
            'type': 'object',
            'properties': {
                'memory_type': {
                    'type': 'string'
                }
            }
        },
        'examples': [
            {
                'input': {
                    'message': '对了，这个方案很好'
                },
                'output': {
                    'memory_type': 'positive_feedback'
                }
            }
        ]
    }
    
    # 转换为 MCE 规则
    mce_rule = AgentSkillsIO.agentskills_to_mce(skill)
    
    print("  Converted MCE rule:")
    print(f"    Name: {mce_rule['name']}")
    print(f"    Description: {mce_rule['description']}")
    print(f"    Memory Type: {mce_rule['memory_type']}")
    print(f"    Tier: {mce_rule['tier']}")
    print(f"    Pattern: {mce_rule['pattern']}")
    print(f"    Example: {mce_rule['example']}")

if __name__ == "__main__":
    test_mce_to_agentskills()
    test_agentskills_to_mce()
    print("\n✅ agentskills.io compatibility tests completed!")
