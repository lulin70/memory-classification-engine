"""命令行界面工具"""

import argparse
import json
import sys
from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.sdk import MemoryClassificationClient


def print_json(data):
    """打印JSON数据"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def handle_process_message(engine, args):
    """处理消息"""
    result = engine.process_message(args.message)
    print_json(result)


def handle_retrieve_memories(engine, args):
    """检索记忆"""
    memories = engine.retrieve_memories(args.query, limit=args.limit)
    print_json(memories)


def handle_get_stats(engine, args):
    """获取统计信息"""
    stats = engine.get_stats()
    print_json(stats)


def handle_manage_memory(engine, args):
    """管理记忆"""
    result = engine.manage_memory(args.action, args.memory_id, args.data)
    print_json(result)


def handle_clear_memory(engine, args):
    """清空工作记忆"""
    result = engine.clear_working_memory()
    print_json(result)


def handle_export_memories(engine, args):
    """导出记忆"""
    result = engine.export_memories(format=args.format)
    print_json(result)


def handle_import_memories(engine, args):
    """导入记忆"""
    with open(args.file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result = engine.import_memories(data, format=args.format)
    print_json(result)


def handle_sdk_process_message(client, args):
    """通过SDK处理消息"""
    result = client.process_message(args.message)
    print_json(result)


def handle_sdk_retrieve_memories(client, args):
    """通过SDK检索记忆"""
    memories = client.retrieve_memories(args.query, limit=args.limit)
    print_json(memories)


def handle_sdk_get_stats(client, args):
    """通过SDK获取统计信息"""
    stats = client.get_stats()
    print_json(stats)


def handle_sdk_health_check(client, args):
    """通过SDK进行健康检查"""
    health = client.health_check()
    print_json(health)


def handle_sdk_get_version(client, args):
    """通过SDK获取版本信息"""
    version = client.get_version()
    print_json(version)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Memory Classification Engine CLI')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 本地引擎命令
    local_parser = subparsers.add_parser('local', help='本地引擎操作')
    local_subparsers = local_parser.add_subparsers(dest='local_command', help='本地引擎子命令')
    
    # 处理消息
    process_parser = local_subparsers.add_parser('process', help='处理消息')
    process_parser.add_argument('message', type=str, help='消息内容')
    process_parser.set_defaults(func=handle_process_message)
    
    # 检索记忆
    retrieve_parser = local_subparsers.add_parser('retrieve', help='检索记忆')
    retrieve_parser.add_argument('query', type=str, help='搜索关键词')
    retrieve_parser.add_argument('--limit', type=int, default=20, help='返回结果数量')
    retrieve_parser.set_defaults(func=handle_retrieve_memories)
    
    # 获取统计信息
    stats_parser = local_subparsers.add_parser('stats', help='获取统计信息')
    stats_parser.set_defaults(func=handle_get_stats)
    
    # 管理记忆
    manage_parser = local_subparsers.add_parser('manage', help='管理记忆')
    manage_parser.add_argument('action', type=str, choices=['view', 'edit', 'delete'], help='操作类型')
    manage_parser.add_argument('memory_id', type=str, help='记忆ID')
    manage_parser.add_argument('--data', type=json.loads, default=None, help='数据（JSON格式）')
    manage_parser.set_defaults(func=handle_manage_memory)
    
    # 清空工作记忆
    clear_parser = local_subparsers.add_parser('clear', help='清空工作记忆')
    clear_parser.set_defaults(func=handle_clear_memory)
    
    # 导出记忆
    export_parser = local_subparsers.add_parser('export', help='导出记忆')
    export_parser.add_argument('--format', type=str, default='json', choices=['json'], help='导出格式')
    export_parser.set_defaults(func=handle_export_memories)
    
    # 导入记忆
    import_parser = local_subparsers.add_parser('import', help='导入记忆')
    import_parser.add_argument('file', type=str, help='导入文件路径')
    import_parser.add_argument('--format', type=str, default='json', choices=['json'], help='导入格式')
    import_parser.set_defaults(func=handle_import_memories)
    
    # Comment in Chinese removed命令
    sdk_parser = subparsers.add_parser('sdk', help='SDK操作')
    sdk_subparsers = sdk_parser.add_subparsers(dest='sdk_command', help='SDK子命令')
    
    # Comment in Chinese removed处理消息
    sdk_process_parser = sdk_subparsers.add_parser('process', help='通过SDK处理消息')
    sdk_process_parser.add_argument('message', type=str, help='消息内容')
    sdk_process_parser.set_defaults(func=handle_sdk_process_message)
    
    # Comment in Chinese removed检索记忆
    sdk_retrieve_parser = sdk_subparsers.add_parser('retrieve', help='通过SDK检索记忆')
    sdk_retrieve_parser.add_argument('query', type=str, help='搜索关键词')
    sdk_retrieve_parser.add_argument('--limit', type=int, default=20, help='返回结果数量')
    sdk_retrieve_parser.set_defaults(func=handle_sdk_retrieve_memories)
    
    # Comment in Chinese removed获取统计信息
    sdk_stats_parser = sdk_subparsers.add_parser('stats', help='通过SDK获取统计信息')
    sdk_stats_parser.set_defaults(func=handle_sdk_get_stats)
    
    # Comment in Chinese removed健康检查
    sdk_health_parser = sdk_subparsers.add_parser('health', help='通过SDK进行健康检查')
    sdk_health_parser.set_defaults(func=handle_sdk_health_check)
    
    # Comment in Chinese removed获取版本信息
    sdk_version_parser = sdk_subparsers.add_parser('version', help='通过SDK获取版本信息')
    sdk_version_parser.set_defaults(func=handle_sdk_get_version)
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'local':
            # 初始化本地引擎
            engine = MemoryClassificationEngine()
            args.func(engine, args)
        elif args.command == 'sdk':
            # Comment in Chinese removed客户端
            client = MemoryClassificationClient()
            args.func(client, args)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
