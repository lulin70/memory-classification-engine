import unittest
import os
import sys
import tempfile
import shutil
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.distributed import DistributedManager, DataSynchronizer
from memory_classification_engine.utils.cache import LRUCache, FileCache, SmartCache, MemoryCache
from memory_classification_engine.utils.semantic import SemanticUtility
from memory_classification_engine.utils.language import LanguageManager
from memory_classification_engine.utils.logger import Logger


class TestEngineProcessMessageVariants(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = ConfigManager()
        self.config.set('storage.data_path', self.test_dir)
        self.config.set('storage.tier2_path', os.path.join(self.test_dir, 'tier2'))
        self.config.set('storage.tier3_path', os.path.join(self.test_dir, 'tier3'))
        self.config.set('storage.tier4_path', os.path.join(self.test_dir, 'tier4'))
        self.config.set('memory.forgetting.min_weight', 0.1)
        self.engine = MemoryClassificationEngine(self.config)

    def tearDown(self):
        if hasattr(self.engine, 'cleanup'):
            self.engine.cleanup()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_process_message_with_context(self):
        result = self.engine.process_message("I prefer dark mode", context={'source': 'test'})
        self.assertIsInstance(result, dict)

    def test_process_message_with_execution_context(self):
        result = self.engine.process_message("I prefer dark mode", execution_context={'feedback_signal': 'positive'})
        self.assertIsInstance(result, dict)

    def test_process_message_negative_feedback(self):
        result = self.engine.process_message("This is wrong", execution_context={'feedback_signal': 'negative'})
        self.assertIsInstance(result, dict)

    def test_process_message_tool_error(self):
        result = self.engine.process_message("Test message", execution_context={'feedback_signal': 'tool_error'})
        self.assertIsInstance(result, dict)

    def test_process_multiple_messages(self):
        for msg in ["I prefer dark mode", "Actually, use single quotes", "The project uses Python 3.9"]:
            result = self.engine.process_message(msg)
            self.assertIsInstance(result, dict)

    def test_process_message_relationship(self):
        result = self.engine.process_message("John is my colleague")
        self.assertIsInstance(result, dict)

    def test_process_message_task(self):
        result = self.engine.process_message("Remember to review the PR")
        self.assertIsInstance(result, dict)

    def test_process_message_emotion(self):
        result = self.engine.process_message("I'm happy with the progress")
        self.assertIsInstance(result, dict)

    def test_process_message_contact(self):
        result = self.engine.process_message("My email is john@example.com")
        self.assertIsInstance(result, dict)

    def test_process_message_event(self):
        result = self.engine.process_message("Meeting at 3pm tomorrow")
        self.assertIsInstance(result, dict)

    def test_retrieve_with_associations(self):
        self.engine.process_message("I prefer dark mode")
        results = self.engine.retrieve_memories(query="dark mode", include_associations=True)
        self.assertIsInstance(results, list)

    def test_manage_forgetting(self):
        result = self.engine.process_message("I prefer dark mode")
        if isinstance(result, dict) and 'memory_id' in result:
            forget_result = self.engine.manage_forgetting(result['memory_id'], action='decrease_weight', weight_adjustment=0.1)
            self.assertIsNotNone(forget_result)

    def test_optimize_system(self):
        result = self.engine.optimize_system()
        self.assertIsNotNone(result)


class TestDistributedManagerExtended(unittest.TestCase):
    def test_init_custom(self):
        manager = DistributedManager(node_id='custom_node', port=0)
        self.assertEqual(manager.node_id, 'custom_node')

    def test_get_cluster_status(self):
        manager = DistributedManager(node_id='test_node', port=0)
        status = manager.get_cluster_status()
        self.assertIsInstance(status, dict)

    def test_get_raft_status(self):
        manager = DistributedManager(node_id='test_node', port=0)
        raft = manager.get_raft_status()
        self.assertIsInstance(raft, dict)

    def test_update_and_get_node_metrics(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.update_node_metrics({'cpu_usage': 50.0, 'memory_usage': 60.0})
        metrics = manager.get_node_metrics('test_node')
        self.assertEqual(metrics['cpu_usage'], 50.0)

    def test_node_health_states(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.update_node_metrics({'cpu_usage': 30.0, 'memory_usage': 40.0})
        self.assertEqual(manager.get_node_health('test_node'), 'healthy')
        manager.update_node_metrics({'cpu_usage': 65.0, 'memory_usage': 40.0})
        self.assertEqual(manager.get_node_health('test_node'), 'warning')
        manager.update_node_metrics({'cpu_usage': 85.0, 'memory_usage': 90.0})
        self.assertEqual(manager.get_node_health('test_node'), 'critical')

    def test_failed_nodes(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.failed_nodes.add('failed_node')
        self.assertTrue(manager.is_node_failed('failed_node'))
        manager.recover_node('failed_node')
        self.assertFalse(manager.is_node_failed('failed_node'))

    def test_compress_decompress_message(self):
        manager = DistributedManager(node_id='test_node', port=0)
        message = {'type': 'test', 'data': 'Hello World'}
        compressed = manager._compress_message(message)
        self.assertIsInstance(compressed, bytes)
        decompressed = manager._decompress_message(compressed)
        self.assertEqual(decompressed['type'], 'test')

    def test_generate_cluster_report(self):
        manager = DistributedManager(node_id='test_node', port=0)
        report = manager.generate_cluster_report()
        self.assertIsInstance(report, str)


class TestDataSynchronizerExtended(unittest.TestCase):
    def test_sync_data(self):
        source = {'key1': 'value1', 'key2': 'value2'}
        target = {'key3': 'value3'}
        result = DataSynchronizer.sync_data(source, target)
        self.assertIn('key1', result)
        self.assertIn('key3', result)

    def test_calculate_hash(self):
        hash1 = DataSynchronizer.calculate_hash({'a': 1})
        hash2 = DataSynchronizer.calculate_hash({'a': 1})
        self.assertEqual(hash1, hash2)

    def test_detect_changes(self):
        old_data = {'a': 1, 'b': 2}
        new_data = {'a': 1, 'b': 3, 'c': 4}
        changes = DataSynchronizer.detect_changes(old_data, new_data)
        self.assertIsInstance(changes, list)

    def test_incremental_sync(self):
        source = {'a': 1, 'b': 2}
        target = {'a': 0}
        merged, changes = DataSynchronizer.incremental_sync(source, target)
        self.assertIn('a', merged)

    def test_resolve_conflicts_latest(self):
        conflicts = [{'path': 'a', 'old_value': 1, 'new_value': 2, 'value': 2}]
        resolved = DataSynchronizer.resolve_conflicts(conflicts, 'latest')
        self.assertEqual(resolved['a'], 2)

    def test_merkle_tree(self):
        data = {'a': 1, 'b': {'c': 2, 'd': 3}}
        tree = DataSynchronizer.calculate_merkle_tree(data)
        self.assertIsInstance(tree, dict)

    def test_find_differences(self):
        tree1 = {'a': 'hash1', 'b': 'hash2'}
        tree2 = {'a': 'hash1', 'b': 'different'}
        diffs = DataSynchronizer.find_differences(tree1, tree2)
        self.assertIn('b', diffs)


class TestCacheModules(unittest.TestCase):
    def _get_smart_cache_config(self):
        return {
            'tier1': {'max_size': 100, 'ttl': 3600},
            'tier2': {'cache_dir': tempfile.mkdtemp(), 'ttl': 86400},
            'preload_keys': []
        }

    def test_lru_cache_basic(self):
        cache = LRUCache(max_size=3, ttl=3600)
        cache.set('a', 1)
        cache.set('b', 2)
        cache.set('c', 3)
        self.assertEqual(cache.get('a'), 1)

    def test_lru_cache_update(self):
        cache = LRUCache(max_size=3, ttl=3600)
        cache.set('a', 1)
        cache.set('a', 10)
        self.assertEqual(cache.get('a'), 10)

    def test_lru_cache_exists(self):
        cache = LRUCache(max_size=3, ttl=3600)
        cache.set('a', 1)
        self.assertTrue(cache.exists('a'))
        self.assertFalse(cache.exists('nonexistent'))

    def test_lru_cache_delete(self):
        cache = LRUCache(max_size=3, ttl=3600)
        cache.set('a', 1)
        cache.delete('a')
        self.assertIsNone(cache.get('a'))

    def test_lru_cache_clear(self):
        cache = LRUCache(max_size=3, ttl=3600)
        cache.set('a', 1)
        cache.set('b', 2)
        cache.clear()
        self.assertIsNone(cache.get('a'))

    def test_lru_cache_stats(self):
        cache = LRUCache(max_size=3, ttl=3600)
        cache.set('a', 1)
        cache.get('a')
        cache.get('nonexistent')
        stats = cache.get_stats()
        self.assertIsInstance(stats, dict)

    def test_lru_cache_size(self):
        cache = LRUCache(max_size=3, ttl=3600)
        cache.set('a', 1)
        cache.set('b', 2)
        self.assertEqual(cache.size(), 2)

    def test_smart_cache_basic(self):
        config = self._get_smart_cache_config()
        cache = SmartCache(config=config)
        cache.set('key1', 'value1')
        self.assertEqual(cache.get('key1'), 'value1')

    def test_smart_cache_stats(self):
        config = self._get_smart_cache_config()
        cache = SmartCache(config=config)
        cache.set('key1', 'value1')
        cache.get('key1')
        cache.get('nonexistent')
        stats = cache.get_stats()
        self.assertIsInstance(stats, dict)

    def test_smart_cache_delete(self):
        config = self._get_smart_cache_config()
        cache = SmartCache(config=config)
        cache.set('key1', 'value1')
        cache.delete('key1')
        self.assertIsNone(cache.get('key1'))

    def test_smart_cache_clear(self):
        config = self._get_smart_cache_config()
        cache = SmartCache(config=config)
        cache.set('key1', 'value1')
        cache.clear()
        self.assertIsNone(cache.get('key1'))

    def test_memory_cache(self):
        cache = MemoryCache(max_size=10, ttl=3600)
        cache.set('key1', 'value1')
        self.assertEqual(cache.get('key1'), 'value1')

    def test_file_cache(self):
        test_dir = tempfile.mkdtemp()
        try:
            cache = FileCache(cache_dir=test_dir, ttl=3600)
            cache.set('key1', {'data': 'value1'})
            result = cache.get('key1')
            self.assertIsNotNone(result)
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)


class TestSemanticUtilityExtended(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.semantic = SemanticUtility(self.config)

    def test_detect_language_english(self):
        result = self.semantic.detect_language("I prefer dark mode for coding")
        self.assertIsInstance(result, str)

    def test_detect_language_chinese(self):
        result = self.semantic.detect_language("我喜欢用Python编程")
        self.assertIsInstance(result, str)

    def test_detect_language_japanese(self):
        result = self.semantic.detect_language("ダークモードが好きです")
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'ja')

    def test_calculate_similarity(self):
        result = self.semantic.calculate_similarity("Hello", "Hi")
        self.assertIsInstance(result, float)

    def test_extract_keywords(self):
        result = self.semantic.extract_keywords("I prefer dark mode for coding")
        self.assertIsInstance(result, list)


class TestLanguageManagerExtended(unittest.TestCase):
    def setUp(self):
        self.manager = LanguageManager()

    def test_detect_language(self):
        lang, conf = self.manager.detect_language("Hello world")
        self.assertIsInstance(lang, str)
        self.assertIsInstance(conf, float)

    def test_detect_chinese(self):
        lang, conf = self.manager.detect_language("我喜欢编程")
        self.assertIsInstance(lang, str)

    def test_detect_japanese(self):
        lang, conf = self.manager.detect_language("こんにちは")
        self.assertIsInstance(lang, str)


class TestLoggerExtended(unittest.TestCase):
    def test_init(self):
        log = Logger(name='test_logger')
        self.assertIsNotNone(log)

    def test_log_levels(self):
        log = Logger(name='test_levels')
        log.info("Info message")
        log.warning("Warning message")
        log.error("Error message")
        log.debug("Debug message")

    def test_no_duplicate_handlers(self):
        log1 = Logger(name='dup_test')
        log2 = Logger(name='dup_test')
        handler_count = len(log2.logger.handlers)
        self.assertLessEqual(handler_count, 2)


if __name__ == '__main__':
    unittest.main()
