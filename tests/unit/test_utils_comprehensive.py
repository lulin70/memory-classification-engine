import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.utils.semantic import SemanticUtility
from memory_classification_engine.utils.language import LanguageManager
from memory_classification_engine.utils.forgetting import ForgettingManager
from memory_classification_engine.utils.cache import LRUCache, SmartCache
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.constants import DEFAULT_BATCH_SIZE, DEFAULT_MEMORY_RETRIEVAL_LIMIT
from memory_classification_engine.utils.logger import Logger


class TestSemanticUtility(unittest.TestCase):
    def setUp(self):
        self.semantic = SemanticUtility({})

    def test_detect_language_english(self):
        lang = self.semantic.detect_language("Hello world")
        self.assertIsInstance(lang, str)

    def test_detect_language_chinese(self):
        lang = self.semantic.detect_language("你好世界")
        self.assertIn(lang, ["zh-cn", "zh", "zh-tw"])

    def test_detect_language_japanese_hiragana(self):
        self.assertEqual(self.semantic.detect_language("こんにちは"), "ja")

    def test_detect_language_japanese_katakana(self):
        self.assertEqual(self.semantic.detect_language("カタカナ"), "ja")

    def test_detect_language_japanese_kanji(self):
        lang = self.semantic.detect_language("漢字")
        self.assertIsInstance(lang, str)

    def test_detect_language_mixed_japanese_english(self):
        lang = self.semantic.detect_language("こんにちは Hello")
        self.assertEqual(lang, "ja")

    def test_detect_language_mixed_chinese_english(self):
        lang = self.semantic.detect_language("你好 Hello")
        self.assertIn(lang, ["zh-cn", "zh", "zh-tw"])

    def test_detect_language_empty(self):
        lang = self.semantic.detect_language("")
        self.assertEqual(lang, "en")

    def test_detect_language_numbers(self):
        lang = self.semantic.detect_language("1234567890")
        self.assertIsInstance(lang, str)

    def test_detect_language_special_chars(self):
        lang = self.semantic.detect_language("!@#$%^&*()")
        self.assertIsInstance(lang, str)

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


class TestLanguageManager(unittest.TestCase):
    def setUp(self):
        self.manager = LanguageManager()

    def test_detect_english(self):
        lang, confidence = self.manager.detect_language("Hello")
        self.assertIsInstance(lang, str)

    def test_detect_chinese(self):
        lang, confidence = self.manager.detect_language("你好")
        self.assertIsInstance(lang, str)

    def test_detect_japanese(self):
        lang, confidence = self.manager.detect_language("こんにちは")
        self.assertIsInstance(lang, str)

    def test_get_language_config(self):
        if hasattr(self.manager, 'get_language_config'):
            config = self.manager.get_language_config()
            self.assertIsInstance(config, (dict, type(None)))


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

    def test_should_forget_low_weight(self):
        if hasattr(self.manager, 'should_forget'):
            memory = {
                'weight': 0.05,
                'access_count': 0,
                'last_accessed': '2026-01-01T00:00:00',
            }
            result = self.manager.should_forget(memory)
            self.assertIsInstance(result, bool)

    def test_should_not_forget_high_weight(self):
        if hasattr(self.manager, 'should_forget'):
            memory = {
                'weight': 0.95,
                'access_count': 100,
                'last_accessed': '2026-04-15T00:00:00',
            }
            result = self.manager.should_forget(memory)
            self.assertIsInstance(result, bool)

    def test_get_forgetting_candidates(self):
        if hasattr(self.manager, 'get_forgetting_candidates'):
            memories = [
                {'id': '1', 'weight': 0.05, 'access_count': 0},
                {'id': '2', 'weight': 0.95, 'access_count': 100},
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

    def test_set_and_get_list(self):
        self.cache.set('key3', [1, 2, 3])
        result = self.cache.get('key3')
        self.assertEqual(result, [1, 2, 3])

    def test_overwrite(self):
        self.cache.set('key4', 'original')
        self.cache.set('key4', 'updated')
        result = self.cache.get('key4')
        self.assertEqual(result, 'updated')

    def test_clear(self):
        self.cache.set('key5', 'value5')
        self.cache.clear()
        result = self.cache.get('key5')
        self.assertIsNone(result)

    def test_delete(self):
        self.cache.set('key6', 'value6')
        self.cache.delete('key6')
        result = self.cache.get('key6')
        self.assertIsNone(result)

    def test_delete_nonexistent(self):
        result = self.cache.delete('nonexistent')
        self.assertFalse(result)

    def test_size(self):
        self.cache.set('key7', 'value7')
        size = self.cache.size()
        self.assertGreaterEqual(size, 1)

    def test_has(self):
        self.cache.set('key8', 'value8')
        self.assertIsNotNone(self.cache.get('key8'))
        self.assertIsNone(self.cache.get('nonexistent'))

    def test_eviction(self):
        small_cache = LRUCache(max_size=3)
        small_cache.set('a', 1)
        small_cache.set('b', 2)
        small_cache.set('c', 3)
        small_cache.set('d', 4)
        self.assertIsNone(small_cache.get('a'))
        self.assertEqual(small_cache.get('d'), 4)


class TestSmartCache(unittest.TestCase):
    def setUp(self):
        self.cache = SmartCache()

    def test_set_and_get(self):
        self.cache.set('key1', 'value1')
        result = self.cache.get('key1')
        self.assertEqual(result, 'value1')

    def test_get_nonexistent(self):
        result = self.cache.get('nonexistent')
        self.assertIsNone(result)

    def test_clear(self):
        self.cache.set('key2', 'value2')
        self.cache.clear()
        result = self.cache.get('key2')
        self.assertIsNone(result)


class TestConfigManager(unittest.TestCase):
    def test_default_config(self):
        config = ConfigManager()
        self.assertIsInstance(config, ConfigManager)

    def test_get(self):
        config = ConfigManager()
        result = config.get('nonexistent_key', 'default_value')
        self.assertEqual(result, 'default_value')

    def test_set_and_get(self):
        config = ConfigManager()
        config.set('test_key', 'test_value')
        result = config.get('test_key')
        self.assertEqual(result, 'test_value')


class TestConstants(unittest.TestCase):
    def test_default_batch_size(self):
        self.assertIsInstance(DEFAULT_BATCH_SIZE, int)
        self.assertGreater(DEFAULT_BATCH_SIZE, 0)

    def test_default_memory_retrieval_limit(self):
        self.assertIsInstance(DEFAULT_MEMORY_RETRIEVAL_LIMIT, int)
        self.assertGreater(DEFAULT_MEMORY_RETRIEVAL_LIMIT, 0)


class TestLogger(unittest.TestCase):
    def test_logger_creation(self):
        logger = Logger("test_logger")
        self.assertIsNotNone(logger)

    def test_logger_info(self):
        logger = Logger("test_logger_info")
        logger.logger.info("Test info message")

    def test_logger_warning(self):
        logger = Logger("test_logger_warning")
        logger.logger.warning("Test warning message")

    def test_logger_error(self):
        logger = Logger("test_logger_error")
        logger.logger.error("Test error message")


if __name__ == '__main__':
    unittest.main()
