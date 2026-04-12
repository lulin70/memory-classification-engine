"""完整的记忆分类引擎使用示例"""

from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.sdk import MemoryClassificationClient
import time


def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    # 初始化引擎
    engine = MemoryClassificationEngine()
    
    # 测试1: 处理用户偏好
    print("\n1. 测试用户偏好记忆:")
    user_message = "记住，我不喜欢在代码中使用破折号"
    result = engine.process_message(user_message)
    print(f"处理结果: {result}")
    
    # 测试2: 处理事实声明
    print("\n2. 测试事实声明记忆:")
    user_message = "我的生日是1990年1月1日"
    result = engine.process_message(user_message)
    print(f"处理结果: {result}")
    
    # 测试3: 处理决策记录
    print("\n3. 测试决策记录记忆:")
    user_message = "我们决定下周一开始项目"
    result = engine.process_message(user_message)
    print(f"处理结果: {result}")
    
    # 测试4: 检索记忆
    print("\n4. 测试记忆检索:")
    memories = engine.retrieve_memories("偏好")
    print(f"检索到的记忆: {memories}")
    
    # 测试5: 获取系统统计信息
    print("\n5. 测试系统统计:")
    stats = engine.get_stats()
    print(f"系统统计: {stats}")
    
    return engine


def test_sdk_functionality():
    """测试SDK功能"""
    print("\n=== 测试SDK功能 ===")
    
    # 初始化SDK客户端
    client = MemoryClassificationClient(base_url='http://localhost:5000')
    
    # 测试健康检查
    print("\n1. 测试健康检查:")
    try:
        health = client.health_check()
        print(f"健康检查结果: {health}")
    except Exception as e:
        print(f"健康检查失败 (服务器可能未运行): {e}")
    
    # 测试版本信息
    print("\n2. 测试版本信息:")
    try:
        version = client.get_version()
        print(f"版本信息: {version}")
    except Exception as e:
        print(f"获取版本失败 (服务器可能未运行): {e}")


def test_memory_evolution():
    """测试记忆进化功能"""
    print("\n=== 测试记忆进化功能 ===")
    
    engine = MemoryClassificationEngine()
    
    # 模拟用户反复提到的模式
    print("\n1. 模拟用户反复提到的模式:")
    
    # 第一次提到
    message1 = "我喜欢在代码中使用驼峰命名法"
    result1 = engine.process_message(message1)
    print(f"第一次处理结果: {result1}")
    
    # 第二次提到
    message2 = "在我们的项目中，变量名应该使用驼峰命名法"
    result2 = engine.process_message(message2)
    print(f"第二次处理结果: {result2}")
    
    # 第三次提到
    message3 = "记住，所有函数名都要用驼峰命名法"
    result3 = engine.process_message(message3)
    print(f"第三次处理结果: {result3}")
    
    # 检查是否生成了程序性记忆
    print("\n2. 检查程序性记忆:")
    procedural_memories = engine.manage_memory('view', 'tier2')
    print(f"程序性记忆: {procedural_memories}")
    
    return engine


def test_search_functionality():
    """测试搜索功能"""
    print("\n=== 测试搜索功能 ===")
    
    engine = MemoryClassificationEngine()
    
    # 添加一些测试数据
    test_messages = [
        "我喜欢Python编程语言",
        "Java是一种面向对象的语言",
        "JavaScript用于前端开发",
        "C++是一种高性能语言",
        "Python的语法很简洁"
    ]
    
    print("\n1. 添加测试数据:")
    for message in test_messages:
        engine.process_message(message)
        time.sleep(0.1)  # 避免太快
    
    # 测试搜索
    print("\n2. 测试搜索功能:")
    search_terms = ["Python", "语言", "前端"]
    
    for term in search_terms:
        results = engine.retrieve_memories(term)
        print(f"搜索 '{term}' 的结果: {results}")
    
    return engine


def main():
    """主函数"""
    print("Memory Classification Engine 完整示例")
    print("=" * 50)
    
    # 测试基本功能
    engine = test_basic_functionality()
    
    # 测试SDK功能
    test_sdk_functionality()
    
    # 测试记忆进化
    engine = test_memory_evolution()
    
    # 测试搜索功能
    engine = test_search_functionality()
    
    print("\n" + "=" * 50)
    print("示例测试完成！")
    print("您可以通过以下方式进一步使用系统:")
    print("1. 运行Web服务器: python -m memory_classification_engine.web.app")
    print("2. 使用SDK客户端与服务器交互")
    print("3. 查看API文档: docs/api/api.md")


if __name__ == "__main__":
    main()
