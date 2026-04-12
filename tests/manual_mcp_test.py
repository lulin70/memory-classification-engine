#!/usr/bin/env python3
"""
MCP Server 手动测试脚本

不依赖 Claude Code/Cursor，直接测试 MCP 协议
使用方法:
    python tests/manual_mcp_test.py

环境要求:
    - Python 3.9+
    - 安装依赖: pip install -e .
    - 可选: 设置离线模式环境变量
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any, Optional


class MCPTester:
    """MCP Server 手动测试器"""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """发送 MCP 请求并获取响应"""
        try:
            # 启动 MCP Server 进程
            process = subprocess.Popen(
                [sys.executable, "-m", "memory_classification_engine", "mcp"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={
                    **dict(subprocess.os.environ),
                    "PYTHONPATH": "src",
                    "HF_DATASETS_OFFLINE": "1",
                    "TRANSFORMERS_OFFLINE": "1",
                }
            )
            
            # 发送请求
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # 读取响应
            response_line = process.stdout.readline()
            
            # 关闭进程
            process.terminate()
            process.wait(timeout=5)
            
            if response_line:
                return json.loads(response_line.strip())
            return None
            
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return None
    
    def test_initialize(self):
        """测试 initialize"""
        print("\n🧪 测试: initialize")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": "manual-test",
                    "version": "1.0.0"
                }
            }
        }
        
        response = self.send_request(request)
        
        if response and "result" in response:
            result = response["result"]
            if result.get("protocolVersion") == "2024-11-05":
                print("✅ initialize 测试通过")
                self.passed += 1
                return True
        
        print("❌ initialize 测试失败")
        print(f"响应: {json.dumps(response, indent=2)}")
        self.failed += 1
        return False
    
    def test_tools_list(self):
        """测试 tools/list"""
        print("\n🧪 测试: tools/list")
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = self.send_request(request)
        
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            if len(tools) == 8:
                print(f"✅ tools/list 测试通过 (发现 {len(tools)} 个 tools)")
                for tool in tools:
                    print(f"   - {tool['name']}")
                self.passed += 1
                return True
        
        print("❌ tools/list 测试失败")
        self.failed += 1
        return False
    
    def test_classify_memory(self):
        """测试 classify_memory tool"""
        print("\n🧪 测试: classify_memory")
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "classify_memory",
                "arguments": {
                    "message": "我喜欢使用双引号而不是单引号"
                }
            }
        }
        
        response = self.send_request(request)
        
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                try:
                    result = json.loads(content[0].get("text", "{}"))
                    if "matched" in result:
                        print("✅ classify_memory 测试通过")
                        print(f"   结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                        self.passed += 1
                        return True
                except:
                    pass
        
        print("❌ classify_memory 测试失败")
        print(f"响应: {json.dumps(response, indent=2)}")
        self.failed += 1
        return False
    
    def test_store_memory(self):
        """测试 store_memory tool"""
        print("\n🧪 测试: store_memory")
        
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "store_memory",
                "arguments": {
                    "content": "使用双引号",
                    "memory_type": "user_preference",
                    "tier": 2
                }
            }
        }
        
        response = self.send_request(request)
        
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                try:
                    result = json.loads(content[0].get("text", "{}"))
                    if result.get("success") and result.get("memory_id"):
                        print("✅ store_memory 测试通过")
                        print(f"   记忆ID: {result['memory_id']}")
                        self.passed += 1
                        return True
                except:
                    pass
        
        print("❌ store_memory 测试失败")
        self.failed += 1
        return False
    
    def test_retrieve_memories(self):
        """测试 retrieve_memories tool"""
        print("\n🧪 测试: retrieve_memories")
        
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "retrieve_memories",
                "arguments": {
                    "query": "代码风格",
                    "limit": 5
                }
            }
        }
        
        response = self.send_request(request)
        
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                try:
                    result = json.loads(content[0].get("text", "{}"))
                    if "memories" in result:
                        print("✅ retrieve_memories 测试通过")
                        print(f"   找到 {len(result['memories'])} 条记忆")
                        self.passed += 1
                        return True
                except:
                    pass
        
        print("❌ retrieve_memories 测试失败")
        self.failed += 1
        return False
    
    def test_get_memory_stats(self):
        """测试 get_memory_stats tool"""
        print("\n🧪 测试: get_memory_stats")
        
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "get_memory_stats",
                "arguments": {}
            }
        }
        
        response = self.send_request(request)
        
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                try:
                    result = json.loads(content[0].get("text", "{}"))
                    if "stats" in result:
                        print("✅ get_memory_stats 测试通过")
                        print(f"   统计: {json.dumps(result['stats'], indent=2)}")
                        self.passed += 1
                        return True
                except:
                    pass
        
        print("❌ get_memory_stats 测试失败")
        self.failed += 1
        return False
    
    def test_batch_classify(self):
        """测试 batch_classify tool"""
        print("\n🧪 测试: batch_classify")
        
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "batch_classify",
                "arguments": {
                    "messages": [
                        {"message": "我喜欢使用双引号"},
                        {"message": "每次部署前都要跑测试"}
                    ]
                }
            }
        }
        
        response = self.send_request(request)
        
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                try:
                    result = json.loads(content[0].get("text", "{}"))
                    if "results" in result and len(result["results"]) == 2:
                        print("✅ batch_classify 测试通过")
                        print(f"   分类了 {len(result['results'])} 条消息")
                        self.passed += 1
                        return True
                except:
                    pass
        
        print("❌ batch_classify 测试失败")
        self.failed += 1
        return False
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n🧪 测试: 错误处理 (未知 tool)")
        
        request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }
        
        response = self.send_request(request)
        
        if response and "error" in response:
            print("✅ 错误处理测试通过")
            print(f"   错误码: {response['error'].get('code')}")
            self.passed += 1
            return True
        
        print("❌ 错误处理测试失败")
        self.failed += 1
        return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("MCP Server 手动测试")
        print("=" * 60)
        print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # 运行测试
        self.test_initialize()
        self.test_tools_list()
        self.test_classify_memory()
        self.test_store_memory()
        self.test_retrieve_memories()
        self.test_get_memory_stats()
        self.test_batch_classify()
        self.test_error_handling()
        
        # 输出结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"总计: {self.passed + self.failed}")
        print(f"通过率: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print("=" * 60)
        
        return self.failed == 0


def main():
    """主函数"""
    tester = MCPTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！MCP Server 工作正常。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查日志。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
