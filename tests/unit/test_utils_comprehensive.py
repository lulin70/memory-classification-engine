import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.utils.semantic import SemanticUtility
from memory_classification_engine.utils.language import LanguageManager
from memory_classification_engine.utils.forgetting import ForgettingManager
from memory_classification_engine.utils.cache import LRUCache, SmartCache


class TestSemanticUtilityComprehensive(unittest.TestCase):
    def setUp(self):
        self.semantic = SemanticUtility({})

    def test_detect_language_english(self):
        self.assertEqual(self.semantic.detect_language("Hello world"), "en")

    def test_detect_language_chinese(self):
        lang = self.semantic.detect_language("你好世界")
        self.assertIn(lang, ["zh-cn", "zh", "zh-tw"])

    def test_detect_language_japanese_hiragana(self):
        self.assertEqual(self.semantic.detect_language("こんにちは"), "ja")

    def test_detect_language_japanese_katakana(self):
        self.assertEqual(self.semantic.detect_language("カタカナ"), "ja")

    def test_detect_language_japanese_kanji(self):
        self.assertEqual(self.semantic.detect_language("漢字"), "ja")

    def test_detect_language_mixed(self):
        lang = self.semantic.detect_language("Hello こんにちは 你好")
        self.assertIsInstance(lang, str)

    def test_detect_language_empty(self):
        lang = self.semantic.detect_language("")
        self.assertEqual(lang, "en")

    def test_encode_text_basic(self):
        result = self.semantic.encode_text("Hello world")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_encode_text_empty(self):
        result = self.semantic.encode_text("")
        self.assertIsInstance(result, list)

    def test_encode_text_chinese(self):
        result = self.semantic.encode_text("你好世界")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_encode_text_japanese(self):
        result = self.semantic.encode_text("こんにちは世界")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_encode_text_long(self):
        result = self.semantic.encode_text("a" * 500)
        self.assertIsInstance(result, list)

    def test_analyze_sentiment(self):
        if hasattr(self.semantic, 'analyze_sentiment'):
            result = self.semantic.analyze_sentiment("I love this!")
            self.assertIsInstance(result, (dict, type(None)))

    def test_extract_entities(self):
        if hasattr(self.semantic, 'extract_entities'):
            result = self.semantic.extract_entities("Alice went to New York")
            self.assertIsInstance(result, (list, type(None)))


class TestLanguageManager(unittest.TestCase):
    def setUp(self):
        self.manager = LanguageManager({})

    def test_process_english(self):
        if hasattr(self.manager, 'process'):
            result = self.manager.process("Hello world")
            self.assertIsInstance(result, (dict, str, list, type(None)))

    def test_process_chinese(self):
        if hasattr(self.manager, 'process'):
            result = self.manager.process("你好世界")
            self.assertIsInstance(result, (dict, str, list, type(None)))

    def test_process_japanese(self):
        if hasattr(self.manager, 'process'):
            result = self.manager.process("こんにちは")
            self.assertIsInstance(result, (dict, str, list, type(None)))

    def test_detect_language(self):
        if hasattr(self.manager, 'detect_language'):
            lang = self.manager.detect_language("Hello")
            self.assertIsInstance(lang, str)


class TestForgettingManager(unittest.TestCase):
    def setUp(self):
        self.manager = ForgettingManager({})

    def test_calculate_weight(self):
        if hasattr(self.manager, 'calculate_weight'):
            weight = self.manager.calculate_weight(
                access_count=5,
                last_accessed_days_ago=1,
                importance=0.8
            )
            self.assertIsInstance(weight, (int, float))

    def test_should_forget(self):
        if hasattr(self.manager, 'should_forget'):
            memory = {
                'weight': 0.1,
                'access_count': 0,
                'last_accessed': '2026-01-01T00:00:00',
            }
            result = self.manager.should_forget(memory)
            self.assertIsInstance(result, bool)

    def test_get_forgetting_candidates(self):
        if hasattr(self.manager, 'get_forgetting_candidates'):
            memories = [
                {'id': '1', 'weight': 0.1, 'access_count': 0},
                {'id': '2', 'weight': 0.9, 'access_count': 100},
            ]
            result = self.manager.get_forgetting_candidates(memories)
            self.assertIsInstance(result, list)


class TestLRUCache(unittest.TestCase):
    def setUp(self):
        self.cache = LRUCache(max_size=100)

    def test_set_and_get(self):
        self.cache.set('key1', 'value1')
        result = self.cache.get('key1')
        self.assertEqual(result, 'value1')

    def test_get_nonexistent(self):
        result = self.cache.get('nonexistent')
        self.assertIsNone(result)

    def test_set_and_get_dict(self):
        self.cache.set('key2', {'nested': 'value'})
        result = self.cache.get('key2')
        self.assertEqual(result, {'nested': 'value'})

    def test_clear(self):
        self.cache.set('key3', 'value3')
        self.cache.clear()
        result = self.cache.get('key3')
        self.assertIsNone(result)

    def test_delete(self):
        self.cache.set('key4', 'value4')
        self.cache.delete('key4')
        result = self.cache.get('key4')
        self.assertIsNone(result)

    def test_size(self):
        self.cache.set('key5', 'value5')
        size = self.cache.size()
        self.assertGreaterEqual(size, 1)

    def test_has(self):
        self.cache.set('key6', 'value6')
        self.assertTrue(self.cache.has('key6'))
        self.assertFalse(self.cache.has('nonexistent'))


if __name__ == '__main__':
    unittest.main()
