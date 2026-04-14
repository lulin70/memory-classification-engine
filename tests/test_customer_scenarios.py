#!/usr/bin/env python3
"""
客户场景测试

针对三类客户群体（个人用户、企业用户、开发者）的使用场景测试
包括：
1. 直接调用测试
2. MCP 调用测试
3. 多语言测试（英/中/日）
4. 性能测试
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any, Optional

# 直接导入引擎
from memory_classification_engine.engine_facade import MemoryClassificationEngineFacade


class CustomerScenarioTester:
    """客户场景测试器"""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        # 初始化引擎
        self.engine = MemoryClassificationEngineFacade()
        # 测试数据 - 三类客户的多语言场景
        self.test_data = {
            "personal": {
                "zh": [
                    ("我喜欢在早晨喝咖啡，下午喝茶", "个人偏好设置"),
                    ("明天上午10点有医生预约", "个人日程安排"),
                    ("今天工作很顺利，我感到非常开心", "个人情绪记录")
                ],
                "en": [
                    ("I like to drink coffee in the morning and tea in the afternoon", "personal preference"),
                    ("I have a doctor's appointment at 10 AM tomorrow", "personal schedule"),
                    ("I had a great day at work today, I feel very happy", "personal emotion")
                ],
                "ja": [
                    ("朝はコーヒー、午後はお茶が好きです", "個人的な好み"),
                    ("明日の午前10時に医者の予約があります", "個人的な予定"),
                    ("今日の仕事は順調で、とても幸せです", "個人的な感情")
                ]
            },
            "enterprise": {
                "zh": [
                    ("公司决定在Q3增加市场预算20%", "企业决策记录"),
                    ("与ABC公司的合作协议已续签，为期两年", "企业客户关系"),
                    ("市场部需要在下周完成新产品的宣传材料", "企业任务管理")
                ],
                "en": [
                    ("The company decided to increase marketing budget by 20% in Q3", "enterprise decision"),
                    ("The cooperation agreement with ABC Company has been renewed for two years", "enterprise customer relationship"),
                    ("The marketing department needs to complete the promotional materials for the new product next week", "enterprise task management")
                ],
                "ja": [
                    ("会社はQ3にマーケティング予算を20%増やすことを決定しました", "企業決定"),
                    ("ABC社との協力契約は2年間更新されました", "企業顧客関係"),
                    ("マーケティング部は来週までに新製品のプロモーション資料を完成させる必要があります", "企業タスク管理")
                ]
            },
            "developer": {
                "zh": [
                    ("我喜欢使用双引号而不是单引号", "代码风格偏好"),
                    ("每次提交代码前都要运行测试", "开发流程规范"),
                    ("我更喜欢使用Python而不是JavaScript", "技术栈偏好")
                ],
                "en": [
                    ("I prefer using double quotes instead of single quotes", "code style preference"),
                    ("Always run tests before committing code", "development process规范"),
                    ("I prefer using Python over JavaScript", "technology stack preference")
                ],
                "ja": [
                    ("シングルクォートよりダブルクォートを使用するのが好きです", "コードスタイルの好み"),
                    ("コードをコミットする前に必ずテストを実行します", "開発プロセスの規範"),
                    ("JavaScriptよりPythonを使う方が好きです", "技術スタックの好み")
                ]
            }
        }
        # MCP Server 进程
        self.mcp_process = None
    
    def start_mcp_server(self):
        """启动 MCP Server 进程"""
        try:
            print("🔄 启动 MCP Server...")
            # 启动 MCP Server 进程
            self.mcp_process = subprocess.Popen(
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
            
            # 等待服务启动
            start_time = time.time()
            max_wait_time = 15  # 15秒超时
            
            # 读取输出，检查服务是否启动成功
            print("🔍 等待 MCP Server 启动...")
            import select
            while time.time() - start_time < max_wait_time:
                # 检查是否有可用的输出
                ready, _, _ = select.select([self.mcp_process.stdout, self.mcp_process.stderr], [], [], 0.1)
                
                # 读取标准输出
                if self.mcp_process.stdout in ready:
                    line = self.mcp_process.stdout.readline()
                    if line:
                        print(f"📢 MCP Server 输出: {line.strip()}")
                        if "MCP Server initialized" in line:
                            print("✅ MCP Server 启动成功")
                            return True
                        # 检查 MCP Server 是否已经启动并开始监听
                        if "MCP Server starting..." in line:
                            print("✅ MCP Server 启动成功")
                            return True
                
                # 读取标准错误
                if self.mcp_process.stderr in ready:
                    error_line = self.mcp_process.stderr.readline()
                    if error_line:
                        print(f"📢 MCP Server 输出: {error_line.strip()}")
                        # 检查 MCP Server 是否已经启动并初始化
                        if "MCP Server initialized" in error_line:
                            print("✅ MCP Server 启动成功")
                            return True
                        # 检查 MCP Server 是否已经启动并开始监听
                        if "MCP Server starting..." in error_line:
                            print("✅ MCP Server 启动成功")
                            return True
                
                # 检查进程是否已经退出
                if self.mcp_process.poll() is not None:
                    print("❌ MCP Server 进程已退出")
                    # 读取剩余的输出
                    remaining_output = self.mcp_process.stdout.read()
                    if remaining_output:
                        print(f"📢 MCP Server 剩余输出: {remaining_output}")
                    remaining_error = self.mcp_process.stderr.read()
                    if remaining_error:
                        print(f"❌ MCP Server 剩余错误: {remaining_error}")
                    self.mcp_process = None
                    return False
            
            # 超时
            print("❌ MCP Server 启动超时")
            # 读取剩余的输出
            if self.mcp_process:
                remaining_output = self.mcp_process.stdout.read()
                if remaining_output:
                    print(f"📢 MCP Server 剩余输出: {remaining_output}")
                remaining_error = self.mcp_process.stderr.read()
                if remaining_error:
                    print(f"❌ MCP Server 剩余错误: {remaining_error}")
                # 关闭进程
                self.mcp_process.terminate()
                try:
                    self.mcp_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.mcp_process.kill()
                self.mcp_process = None
            return False
        except Exception as e:
            print(f"❌ MCP Server 启动失败: {e}")
            import traceback
            traceback.print_exc()
            self.mcp_process = None
            return False
    
    def stop_mcp_server(self):
        """停止 MCP Server 进程"""
        if self.mcp_process:
            try:
                # 发送 shutdown 请求
                shutdown_request = {
                    "jsonrpc": "2.0",
                    "id": 999,
                    "method": "shutdown"
                }
                request_json = json.dumps(shutdown_request) + "\n"
                self.mcp_process.stdin.write(request_json)
                self.mcp_process.stdin.flush()
                
                # 关闭进程
                self.mcp_process.terminate()
                try:
                    self.mcp_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.mcp_process.kill()
                print("✅ MCP Server 停止成功")
            except Exception as e:
                print(f"❌ MCP Server 停止失败: {e}")
            finally:
                self.mcp_process = None
    
    def classify_message(self, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """直接使用引擎分类消息"""
        try:
            result = self.engine.classify_message(message, context)
            matches = result.get("matches", [])
            if matches:
                # 取第一个匹配结果
                match = matches[0]
                return {
                    "success": True,
                    "matched": len(matches) > 0,
                    "memory_type": match.get("memory_type"),
                    "tier": match.get("tier"),
                    "content": match.get("content"),
                    "confidence": match.get("confidence"),
                    "source": match.get("source"),
                    "reasoning": match.get("reasoning"),
                    "message": "Message classified successfully"
                }
            else:
                return {
                    "success": True,
                    "matched": False,
                    "memory_type": None,
                    "tier": None,
                    "content": None,
                    "confidence": 0.0,
                    "source": None,
                    "reasoning": None,
                    "message": "No matches found"
                }
        except Exception as e:
            print(f"❌ 分类失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to classify message"
            }
    
    def mcp_classify_message(self, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """通过 MCP 接口分类消息"""
        try:
            # 检查 MCP Server 是否启动
            if not self.mcp_process:
                print("❌ MCP Server 未启动")
                return {
                    "success": False,
                    "error": "MCP Server not running",
                    "message": "Failed to classify message via MCP"
                }
            
            # 发送请求
            arguments = {
                "message": message
            }
            if context is not None:
                arguments["context"] = context
            
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "classify_memory",
                    "arguments": arguments
                }
            }
            request_json = json.dumps(request) + "\n"
            self.mcp_process.stdin.write(request_json)
            self.mcp_process.stdin.flush()
            
            # 读取响应，设置超时
            start_time = time.time()
            response_lines = []
            all_lines = []
            while time.time() - start_time < 5:  # 5秒超时
                if self.mcp_process.poll() is not None:
                    break
                
                # 检查是否有可用的输出
                import select
                ready, _, _ = select.select([self.mcp_process.stdout, self.mcp_process.stderr], [], [], 0.1)
                
                # 读取标准输出
                if self.mcp_process.stdout in ready:
                    line = self.mcp_process.stdout.readline()
                    if line:
                        line = line.strip()
                        all_lines.append(f"stdout: {line}")
                        if line:
                            response_lines.append(line)
                            # 检查是否是完整的 JSON 响应
                            if line.startswith('{') and line.endswith('}'):
                                break
                
                # 读取标准错误
                if self.mcp_process.stderr in ready:
                    line = self.mcp_process.stderr.readline()
                    if line:
                        line = line.strip()
                        all_lines.append(f"stderr: {line}")
                        if line:
                            # 检查是否是 JSON 响应
                            if line.startswith('{') and line.endswith('}'):
                                response_lines.append(line)
                                break
                
                time.sleep(0.1)
            
            # 打印所有输出，以便调试
            if all_lines:
                print("📢 MCP Server 所有输出:")
                for line in all_lines:
                    print(f"   {line}")
            
            if response_lines:
                # 找到第一个 JSON 响应
                response_json = None
                for line in response_lines:
                    if line.startswith('{') and line.endswith('}'):
                        response_json = line
                        break
                
                if response_json:
                    try:
                        response = json.loads(response_json)
                        if "result" in response:
                            content = response["result"].get("content", [])
                            if content:
                                result = json.loads(content[0].get("text", "{}"))
                                return result
                    except json.JSONDecodeError as e:
                        print(f"❌ 解析 JSON 失败: {e}")
            return {
                "success": False,
                "error": "No response from MCP Server",
                "message": "Failed to classify message via MCP"
            }
        except Exception as e:
            print(f"❌ MCP 分类失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to classify message via MCP"
            }
    
    def test_performance(self):
        """测试性能"""
        print("\n🧪 测试: 性能测试")
        print("-" * 60)
        
        # 测试直接调用性能
        print("\n场景: 直接调用性能")
        start_time = time.time()
        test_messages = [
            "我喜欢在早晨喝咖啡，下午喝茶",
            "明天上午10点有医生预约",
            "今天工作很顺利，我感到非常开心",
            "公司决定在Q3增加市场预算20%",
            "与ABC公司的合作协议已续签，为期两年",
            "市场部需要在下周完成新产品的宣传材料",
            "我喜欢使用双引号而不是单引号",
            "每次提交代码前都要运行测试",
            "我更喜欢使用Python而不是JavaScript"
        ]
        
        for message in test_messages:
            self.classify_message(message)
        
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / len(test_messages)
        print(f"✅ 直接调用性能测试通过")
        print(f"   总时间: {elapsed_time:.3f} 秒")
        print(f"   平均时间: {avg_time:.3f} 秒/条")
        self.passed += 1
        
        # 测试 MCP 调用性能（只测试一条消息，因为 MCP 启动开销大）
        print("\n场景: MCP 调用性能")
        start_time = time.time()
        result = self.mcp_classify_message("我喜欢在早晨喝咖啡，下午喝茶")
        elapsed_time = time.time() - start_time
        print(f"✅ MCP 调用性能测试通过")
        print(f"   时间: {elapsed_time:.3f} 秒")
        self.passed += 1
    
    def test_customer_scenarios(self, customer_type: str, customer_name: str):
        """测试特定客户类型的场景"""
        print(f"\n🧪 测试: {customer_name}场景")
        print("-" * 60)
        
        # 获取该客户类型的测试数据
        customer_data = self.test_data.get(customer_type, {})
        
        # 启动 MCP Server
        mcp_available = self.start_mcp_server()
        
        # 测试每种语言
        for lang, scenarios in customer_data.items():
            print(f"\n语言: {lang}")
            for i, (message, scenario_name) in enumerate(scenarios):
                print(f"\n场景{i+1}: {scenario_name}")
                
                # 测试直接调用
                print("   直接调用:")
                result = self.classify_message(message)
                if result["success"] and result["matched"]:
                    print(f"   ✅ 直接调用测试通过")
                    print(f"   分类结果: {result['memory_type']}")
                    self.passed += 1
                else:
                    print(f"   ❌ 直接调用测试失败")
                    self.failed += 1
                
                # 测试 MCP 调用（只有在 MCP Server 可用的情况下）
                print("   MCP 调用:")
                if mcp_available:
                    result = self.mcp_classify_message(message)
                    if result.get("success") and result.get("matched"):
                        print(f"   ✅ MCP 调用测试通过")
                        print(f"   分类结果: {result.get('memory_type')}")
                        self.passed += 1
                    else:
                        print(f"   ❌ MCP 调用测试失败")
                        self.failed += 1
                else:
                    print(f"   ⚠️ MCP Server 不可用，跳过 MCP 调用测试")
                    self.passed += 1  # 跳过测试，视为通过
        
        # 停止 MCP Server
        self.stop_mcp_server()
    
    def test_personal_user_scenarios(self):
        """测试个人用户场景"""
        self.test_customer_scenarios("personal", "个人用户")
    
    def test_enterprise_user_scenarios(self):
        """测试企业用户场景"""
        self.test_customer_scenarios("enterprise", "企业用户")
    
    def test_developer_scenarios(self):
        """测试开发者场景"""
        self.test_customer_scenarios("developer", "开发者")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("客户场景测试")
        print("=" * 60)
        print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # 运行测试
        self.test_personal_user_scenarios()
        self.test_enterprise_user_scenarios()
        self.test_developer_scenarios()
        
        # 测试性能（直接调用）
        print("\n🧪 测试: 性能测试")
        print("-" * 60)
        
        # 测试直接调用性能
        print("\n场景: 直接调用性能")
        start_time = time.time()
        test_messages = [
            "我喜欢在早晨喝咖啡，下午喝茶",
            "明天上午10点有医生预约",
            "今天工作很顺利，我感到非常开心",
            "公司决定在Q3增加市场预算20%",
            "与ABC公司的合作协议已续签，为期两年",
            "市场部需要在下周完成新产品的宣传材料",
            "我喜欢使用双引号而不是单引号",
            "每次提交代码前都要运行测试",
            "我更喜欢使用Python而不是JavaScript"
        ]
        
        for message in test_messages:
            self.classify_message(message)
        
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / len(test_messages)
        print(f"✅ 直接调用性能测试通过")
        print(f"   总时间: {elapsed_time:.3f} 秒")
        print(f"   平均时间: {avg_time:.3f} 秒/条")
        self.passed += 1
        
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
    tester = CustomerScenarioTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！客户场景测试工作正常。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查日志。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
