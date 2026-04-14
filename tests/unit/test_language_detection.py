import unittest
from memory_classification_engine.utils.semantic import SemanticUtility


class TestLanguageDetection(unittest.TestCase):
    """测试语言检测功能的单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.semantic_utility = SemanticUtility({})
    
    def test_english_detection(self):
        """测试英语检测"""
        english_text = "Hello, how are you?"
        self.assertEqual(self.semantic_utility.detect_language(english_text), "en")
        
        # 测试简短英语文本
        short_english = "Hi"
        self.assertEqual(self.semantic_utility.detect_language(short_english), "en")
    
    def test_chinese_detection(self):
        """测试中文检测"""
        chinese_text = "你好，你怎么样？"
        lang = self.semantic_utility.detect_language(chinese_text)
        self.assertIn(lang, ["zh-cn", "zh", "zh-tw"])
        
        # 测试简短中文文本
        short_chinese = "好"
        lang = self.semantic_utility.detect_language(short_chinese)
        self.assertIn(lang, ["zh-cn", "zh", "zh-tw"])
    
    def test_japanese_detection(self):
        """测试日语检测"""
        # 测试平假名
        hiragana_text = "こんにちは、元気ですか？"
        self.assertEqual(self.semantic_utility.detect_language(hiragana_text), "ja")
        
        # 测试片假名
        katakana_text = "カタカナで書かれたテキスト"
        self.assertEqual(self.semantic_utility.detect_language(katakana_text), "ja")
        
        # 测试汉字
        kanji_text = "漢字で書かれた文章"
        self.assertEqual(self.semantic_utility.detect_language(kanji_text), "ja")
        
        # 测试混合日语
        mixed_japanese = "こんにちは、漢字とカタカナの混ざったテキスト"
        self.assertEqual(self.semantic_utility.detect_language(mixed_japanese), "ja")
        
        # 测试简短日语文本
        short_japanese = "はい"
        self.assertEqual(self.semantic_utility.detect_language(short_japanese), "ja")
    
    def test_mixed_language_detection(self):
        """测试混合语言检测"""
        # 日语和英语混合
        mixed_japanese_english = "こんにちは Hello"
        self.assertEqual(self.semantic_utility.detect_language(mixed_japanese_english), "ja")
        
        # 中文和英语混合
        mixed_chinese_english = "你好 Hello"
        lang = self.semantic_utility.detect_language(mixed_chinese_english)
        self.assertIn(lang, ["zh-cn", "zh", "zh-tw"])
        
        # 三种语言混合
        mixed_all = "こんにちは 你好 Hello"
        # 应该检测为日语，因为日语字符集检测优先级更高
        self.assertEqual(self.semantic_utility.detect_language(mixed_all), "ja")
    
    def test_empty_text_detection(self):
        """测试空文本检测"""
        empty_text = ""
        self.assertEqual(self.semantic_utility.detect_language(empty_text), "en")
    
    def test_special_characters_detection(self):
        """测试特殊字符检测"""
        special_chars = "!@#$%^&*()"
        self.assertEqual(self.semantic_utility.detect_language(special_chars), "en")
    
    def test_numeric_text_detection(self):
        """测试数字文本检测"""
        numeric_text = "1234567890"
        self.assertEqual(self.semantic_utility.detect_language(numeric_text), "en")


if __name__ == '__main__':
    unittest.main()
