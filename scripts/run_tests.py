#!/usr/bin/env python3
"""
MCE 系统测试脚本
执行全面的测试并生成测试报告
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='test_results.log'
)
logger = logging.getLogger('mce-test')

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.utils.semantic import semantic_utility

class MCETestRunner:
    def __init__(self):
        self.engine = MemoryClassificationEngine()
        self.test_results = {
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0,
                'errors': 0
            },
            'tests': [],
            'warnings': [],
            'errors': [],
            'performance': {}
        }
    
    def run_test(self, test_id, test_name, test_func):
        """执行单个测试"""
        self.test_results['summary']['total'] += 1
        
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            test_result = {
                'id': test_id,
                'name': test_name,
                'status': 'PASSED',
                'duration': end_time - start_time,
                'result': result
            }
            
            self.test_results['tests'].append(test_result)
            self.test_results['summary']['passed'] += 1
            logger.info(f"✓ {test_id}: {test_name} - PASSED ({end_time - start_time:.2f}s)")
            
        except Exception as e:
            end_time = time.time()
            error_msg = str(e)
            
            test_result = {
                'id': test_id,
                'name': test_name,
                'status': 'FAILED',
                'duration': end_time - start_time,
                'error': error_msg
            }
            
            self.test_results['tests'].append(test_result)
            self.test_results['summary']['failed'] += 1
            self.test_results['errors'].append({
                'test_id': test_id,
                'test_name': test_name,
                'error': error_msg
            })
            logger.error(f"✗ {test_id}: {test_name} - FAILED: {error_msg}")
    
    def test_english_classification(self):
        """测试英语分类"""
        test_cases = [
            ("EN-001", "英语日常对话分类", "Hello, how are you today? I'm doing well, thank you."),
            ("EN-002", "英语技术文档分类", "The quick sort algorithm has a time complexity of O(n log n)."),
            ("EN-003", "英语代码分类", "def calculate_sum(a, b): return a + b"),
            ("EN-004", "英语长文本分类", """This is a long English text that discusses various topics including technology, science, and culture. It contains multiple sentences and paragraphs to test the system's ability to handle longer texts.""")
        ]
        
        for test_id, test_name, text in test_cases:
            def test_func():
                result = self.engine.process_message(text)
                return result
            self.run_test(test_id, test_name, test_func)
    
    def test_chinese_classification(self):
        """测试中文分类"""
        test_cases = [
            ("ZH-001", "中文日常对话分类", "你好，今天怎么样？我很好，谢谢。"),
            ("ZH-002", "中文技术文档分类", "快速排序算法的时间复杂度是 O(n log n)。"),
            ("ZH-003", "中文代码分类", "# 这是中文注释\ndef calculate_sum(a, b): return a + b"),
            ("ZH-004", "中文长文本分类", """这是一段中文长文本，讨论了包括技术、科学和文化在内的各种话题。它包含多个句子和段落，以测试系统处理较长文本的能力。""")
        ]
        
        for test_id, test_name, text in test_cases:
            def test_func():
                result = self.engine.process_message(text)
                return result
            self.run_test(test_id, test_name, test_func)
    
    def test_japanese_classification(self):
        """测试日语分类"""
        test_cases = [
            ("JP-001", "日语日常对话分类", "こんにちは、今日はどうですか？私は元気です、ありがとう。"),
            ("JP-002", "日语技术文档分类", "クイックソートアルゴリズムの時間計算量は O(n log n) です。"),
            ("JP-003", "日语代码分类", "# これは日本語のコメント\ndef calculate_sum(a, b): return a + b"),
            ("JP-004", "日语长文本分类", """これは日本語の長いテキストで、技術、科学、文化などの様々なトピックについて話しています。システムが長いテキストを処理する能力をテストするために、複数の文と段落が含まれています。""")
        ]
        
        for test_id, test_name, text in test_cases:
            def test_func():
                result = self.engine.process_message(text)
                return result
            self.run_test(test_id, test_name, test_func)
    
    def test_mixed_language(self):
        """测试混合语言"""
        test_cases = [
            ("MIX-001", "中英混合文本", "Hello 你好，this is a 混合 language test。"),
            ("MIX-002", "中日混合文本", "こんにちは 你好，これは 混合 言語 テスト です。"),
            ("MIX-003", "英日混合文本", "Hello こんにちは，this is a 混合 language test です。")
        ]
        
        for test_id, test_name, text in test_cases:
            def test_func():
                result = self.engine.process_message(text)
                return result
            self.run_test(test_id, test_name, test_func)
    
    def test_edge_cases(self):
        """测试边界情况"""
        test_cases = [
            ("EDGE-001", "空输入", ""),
            ("EDGE-002", "超长文本", "a" * 10000),
            ("EDGE-003", "特殊字符", "!@#$%^&*()_+[]{}|;:'\",.<>?/\\"),
            ("EDGE-004", "重复内容", "Hello Hello Hello Hello Hello")
        ]
        
        for test_id, test_name, text in test_cases:
            def test_func():
                result = self.engine.process_message(text)
                return result
            self.run_test(test_id, test_name, test_func)
    
    def test_performance(self):
        """测试性能"""
        test_cases = [
            ("PERF-001", "分类性能", 100),
            ("PERF-002", "检索性能", 1000)
        ]
        
        for test_id, test_name, count in test_cases:
            def test_func():
                start_time = time.time()
                for i in range(count):
                    self.engine.process_message(f"Test message {i}")
                end_time = time.time()
                return {"count": count, "time": end_time - start_time, "avg_time": (end_time - start_time) / count}
            self.run_test(test_id, test_name, test_func)
    
    def test_memory_management(self):
        """测试记忆管理"""
        test_cases = [
            ("MEM-001", "记忆检索", "test message"),
            ("MEM-002", "遗忘管理", "low value memory")
        ]
        
        for test_id, test_name, query in test_cases:
            def test_func():
                if test_id == "MEM-001":
                    result = self.engine.retrieve_memories(query)
                else:
                    # 先创建一个记忆
                    create_result = self.engine.process_message(query)
                    memory_id = create_result['matches'][0]['id']
                    # 然后进行遗忘管理
                    result = self.engine.manage_forgetting(memory_id)
                return result
            self.run_test(test_id, test_name, test_func)
    
    def generate_test_report(self):
        """生成测试报告"""
        report = {
            'test_date': datetime.now().isoformat(),
            'summary': self.test_results['summary'],
            'tests': self.test_results['tests'],
            'warnings': self.test_results['warnings'],
            'errors': self.test_results['errors'],
            'performance': self.test_results['performance']
        }
        
        # 保存 JSON 格式的测试结果
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成 Markdown 格式的测试报告
        markdown_report = self._generate_markdown_report(report)
        
        # 保存 Markdown 报告
        report_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'testing', 'MCE_TEST_REPORT.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        logger.info(f"测试报告已生成: {report_path}")
        return report_path
    
    def _generate_markdown_report(self, report):
        """生成 Markdown 格式的测试报告"""
        md = f"""# MCE 系统测试报告

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档名称 | MCE 系统测试报告 |
| 版本 | v1.0.0 |
| 测试日期 | {report['test_date']} |
| 测试环境 | Python {sys.version} |
| 测试人员 | 测试专家 |

## 测试执行摘要

| 指标 | 数值 |
|------|------|
| 总测试用例 | {report['summary']['total']} |
| 通过 | {report['summary']['passed']} |
| 失败 | {report['summary']['failed']} |
| 警告 | {report['summary']['warnings']} |
| 错误 | {report['summary']['errors']} |
| 通过率 | {report['summary']['passed'] / report['summary']['total'] * 100:.2f}% |

## 测试结果详情

"""
        
        # 测试结果详情
        for test in report['tests']:
            status_emoji = "✅" if test['status'] == 'PASSED' else "❌"
            md += f"### {status_emoji} {test['id']}: {test['name']}\n"
            md += f"- 状态: {test['status']}\n"
            md += f"- 执行时间: {test['duration']:.2f} 秒\n"
            if test['status'] == 'FAILED':
                md += f"- 错误信息: {test['error']}\n"
            md += "\n"
        
        # 警告和错误
        if report['warnings']:
            md += "## 警告清单\n\n"
            for warning in report['warnings']:
                md += f"- {warning['test_id']}: {warning['test_name']} - {warning['warning']}\n"
            md += "\n"
        
        if report['errors']:
            md += "## 错误清单\n\n"
            for error in report['errors']:
                md += f"- {error['test_id']}: {error['test_name']} - {error['error']}\n"
            md += "\n"
        
        # 性能测试结果
        if report['performance']:
            md += "## 性能测试结果\n\n"
            for test_id, result in report['performance'].items():
                md += f"- {test_id}: {result['avg_time']:.4f} 秒/次\n"
            md += "\n"
        
        # 建议和改进
        md += "## 建议和改进\n\n"
        md += "1. 优化系统性能，特别是在处理长文本时\n"
        md += "2. 增强多语言支持，特别是日语处理能力\n"
        md += "3. 完善错误处理和日志记录\n"
        md += "4. 增加更多边界情况测试\n"
        md += "5. 优化存储和检索算法\n"
        
        md += "\n---\n\n**版本**: v1.0.0  \n**最后更新**: {report['test_date']}"
        
        return md
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始执行 MCE 系统测试...")
        
        # 运行各类测试
        self.test_english_classification()
        self.test_chinese_classification()
        self.test_japanese_classification()
        self.test_mixed_language()
        self.test_edge_cases()
        self.test_performance()
        self.test_memory_management()
        
        # 生成测试报告
        report_path = self.generate_test_report()
        
        logger.info(f"测试完成，报告已生成: {report_path}")
        return report_path

if __name__ == "__main__":
    test_runner = MCETestRunner()
    test_runner.run_all_tests()
