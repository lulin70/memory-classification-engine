import unittest
from memory_classification_engine.utils.semantic import SemanticUtility


class TestSemanticUtility(unittest.TestCase):
    """测试SemanticUtility类的单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.semantic_utility = SemanticUtility({})
    
    def test_encode_text(self):
        """测试encode_text方法"""
        # 测试基本文本编码
        text = "Hello, world!"
        encoded = self.semantic_utility.encode_text(text)
        self.assertIsInstance(encoded, list)
        self.assertGreater(len(encoded), 0)
        
        # 测试空文本
        empty_text = ""
        encoded_empty = self.semantic_utility.encode_text(empty_text)
        self.assertIsInstance(encoded_empty, list)
        
        # 测试长文本
        long_text = "a" * 200
        encoded_long = self.semantic_utility.encode_text(long_text)
        self.assertIsInstance(encoded_long, list)
    
    def test_detect_language(self):
        """测试detect_language方法"""
        # 测试英语检测
        english_text = "Hello, how are you?"
        self.assertEqual(self.semantic_utility.detect_language(english_text), "en")
        
        # 测试中文检测
        chinese_text = "你好，你怎么样？"
        lang = self.semantic_utility.detect_language(chinese_text)
        self.assertIn(lang, ["zh-cn", "zh", "zh-tw"])
        
        # 测试日语检测
        japanese_text = "こんにちは、元気ですか？"
        self.assertEqual(self.semantic_utility.detect_language(japanese_text), "ja")
        
        # 测试混合语言
        mixed_text = "Hello 你好 こんにちは"
        lang = self.semantic_utility.detect_language(mixed_text)
        self.assertIsInstance(lang, str)


if __name__ == '__main__':
    unittest.main()
