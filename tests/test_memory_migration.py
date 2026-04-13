#!/usr/bin/env python3
"""
测试记忆迁移功能
"""

from memory_classification_engine import MemoryOrchestrator
from memory_classification_engine.utils.memory_migration import MemoryMigrationManager, get_memory_migration_manager
import json
import os

def test_memory_migration():
    """测试记忆迁移功能"""
    print("=" * 60)
    print("Testing Memory Migration System")
    print("=" * 60)
    
    # 初始化编排器和迁移管理器
    print("1. Initializing MemoryOrchestrator and MemoryMigrationManager...")
    print("   Step 1: Creating orchestrator1...")
    orchestrator1 = MemoryOrchestrator()
    print("   Step 2: Creating orchestrator2...")
    orchestrator2 = MemoryOrchestrator()  # 模拟另一个 Agent 实例
    print("   Step 3: Creating migration_manager...")
    migration_manager = get_memory_migration_manager()
    print("   ✅ MemoryOrchestrator and MemoryMigrationManager initialized")
    
    # 在第一个编排器中创建一些记忆
    print("\n2. Creating memories in first orchestrator...")
    test_messages = [
        "我更喜欢使用双引号",
        "张三是后端开发工程师",
        "Python 是我最喜欢的编程语言",
        "代码应该保持简洁"
    ]
    
    for i, message in enumerate(test_messages):
        result = orchestrator1.learn(message)
        print(f"   Message {i+1}: '{message}' - Stored: {result['stored']}")
    
    # 测试导出功能
    print("\n3. Testing export functionality...")
    export_json = orchestrator1.export_memories()
    print(f"   Exported JSON length: {len(export_json)} characters")
    print(f"   Exported data preview: {export_json[:200]}...")
    
    # 测试验证功能
    print("\n4. Testing validation functionality...")
    validation = orchestrator1.validate_export_data(export_json)
    print(f"   Validation result: {validation['valid']}")
    if validation['valid']:
        print(f"   Memory count: {validation['memory_count']}")
        print(f"   Export version: {validation['version']}")
    else:
        print(f"   Validation errors: {validation['errors']}")
    
    # 测试导入功能到第二个编排器
    print("\n5. Testing import functionality...")
    import_result = orchestrator2.import_memories(export_json)
    print(f"   Import result: {import_result['success']}")
    print(f"   Imported memories: {import_result['imported_count']}")
    
    # 验证第二个编排器中是否有导入的记忆
    print("\n6. Verifying imported memories in second orchestrator...")
    for query in ["双引号", "张三", "Python", "代码"]:
        memories = orchestrator2.recall(query)
        print(f"   Query: '{query}' - Found {len(memories)} memory(ies)")
        for j, memory in enumerate(memories[:2]):
            print(f"     {j+1}. [{memory.get('memory_type')}] {memory.get('content', '')[:50]}...")
    
    # 测试文件导出导入
    print("\n7. Testing file export/import...")
    test_file = "test_migration.json"
    
    # 导出到文件
    orchestrator1.export_to_file(test_file)
    print(f"   Exported memories to {test_file}")
    
    # 从文件导入
    import_from_file_result = orchestrator2.import_from_file(test_file)
    print(f"   Import from file result: {import_from_file_result['success']}")
    print(f"   Imported from file: {import_from_file_result['imported_count']} memories")
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"   Cleaned up test file: {test_file}")
    
    # 测试直接使用迁移管理器
    print("\n8. Testing migration manager directly...")
    # 示例记忆数据
    sample_memories = [
        {
            "id": "mem_1",
            "content": "测试记忆 1",
            "memory_type": "user_preference",
            "tier": 2,
            "confidence": 0.9
        },
        {
            "id": "mem_2",
            "content": "测试记忆 2",
            "memory_type": "relationship",
            "tier": 4,
            "confidence": 0.85
        }
    ]
    
    # 直接导出
    direct_export = migration_manager.export_memories(sample_memories)
    print(f"   Direct export successful: {len(direct_export)} characters")
    
    # 直接导入
    direct_import = migration_manager.import_memories(direct_export)
    print(f"   Direct import successful: {len(direct_import)} memories")
    
    print("\n" + "=" * 60)
    print("Memory Migration System tests completed!")
    print("=" * 60)

def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    orchestrator = MemoryOrchestrator()
    migration_manager = get_memory_migration_manager()
    
    # 测试无效的 JSON
    print("\n1. Testing invalid JSON...")
    invalid_json = "invalid json"
    validation = orchestrator.validate_export_data(invalid_json)
    print(f"   Validation result: {validation['valid']}")
    print(f"   Error: {validation['errors'][0]}")
    
    # 测试缺少字段的 JSON
    print("\n2. Testing JSON with missing fields...")
    incomplete_json = '{"version": "1.0"}'  # 缺少 memories 字段
    validation = orchestrator.validate_export_data(incomplete_json)
    print(f"   Validation result: {validation['valid']}")
    print(f"   Errors: {validation['errors']}")
    
    # 测试不存在的文件
    print("\n3. Testing non-existent file...")
    non_existent_file = "non_existent.json"
    try:
        result = orchestrator.import_from_file(non_existent_file)
        print(f"   Import result: {result['success']}")
    except Exception as e:
        print(f"   Expected error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Error handling tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_memory_migration()
    test_error_handling()
