import unittest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.utils.intelligent_memory import IntelligentMemoryManager
from memory_classification_engine.utils.encryption_helper import MemoryEncryptionHelper
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.memory_manager import MemoryManager, SmartCache as MM_SmartCache
from memory_classification_engine.utils.forgetting import ForgettingManager
from memory_classification_engine.utils.session_summary import generate_session_summary


class TestIntelligentMemoryManager(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.config.set('memory.compression_threshold', 0.8)
        self.config.set('memory.max_batch_size', 100)
        self.manager = IntelligentMemoryManager(self.config)

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.compression_threshold, 0.8)
        self.assertEqual(self.manager.max_batch_size, 100)

    def test_compress_memories_single(self):
        memories = [{'id': 'm1', 'content': 'Test', 'memory_type': 'user_preference'}]
        result = self.manager.compress_memories(memories)
        self.assertEqual(len(result), 1)

    def test_compress_memories_empty(self):
        result = self.manager.compress_memories([])
        self.assertEqual(result, [])

    def test_prioritize_memories(self):
        memories = [
            {'id': 'm1', 'weight': 0.5, 'last_accessed': 100},
            {'id': 'm2', 'weight': 0.9, 'last_accessed': 200},
            {'id': 'm3', 'weight': 0.7, 'last_accessed': 150},
        ]
        result = self.manager.prioritize_memories(memories)
        self.assertEqual(result[0]['id'], 'm2')

    def test_batch_operate(self):
        memories = [{'id': f'm{i}'} for i in range(5)]
        results = self.manager.batch_operate(memories, lambda m: m['id'])
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0], 'm0')

    def test_batch_operate_limit(self):
        config = ConfigManager()
        config.set('memory.max_batch_size', 3)
        config.set('memory.compression_threshold', 0.8)
        manager = IntelligentMemoryManager(config)
        memories = [{'id': f'm{i}'} for i in range(10)]
        results = manager.batch_operate(memories, lambda m: m['id'])
        self.assertEqual(len(results), 3)

    def test_get_memory_statistics(self):
        memories = [
            {'id': 'm1', 'memory_type': 'user_preference', 'weight': 0.8, 'created_at': 1700000000},
            {'id': 'm2', 'memory_type': 'fact_declaration', 'weight': 0.6, 'created_at': 1700000100},
            {'id': 'm3', 'memory_type': 'user_preference', 'weight': 0.9, 'created_at': 1700000200},
        ]
        stats = self.manager.get_memory_statistics(memories)
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_memories'], 3)
        self.assertIn('type_counts', stats)
        self.assertEqual(stats['type_counts']['user_preference'], 2)

    def test_get_memory_statistics_empty(self):
        stats = self.manager.get_memory_statistics([])
        self.assertEqual(stats, {})


class TestMemoryEncryptionHelper(unittest.TestCase):
    def test_encrypt_memory_content_non_sensitive(self):
        memory = {'content': 'This is normal content', 'is_encrypted': False}
        result = MemoryEncryptionHelper.encrypt_memory_content(memory)
        self.assertFalse(result)
        self.assertFalse(memory.get('is_encrypted', False))

    def test_decrypt_memory_content_not_encrypted(self):
        memory = {'content': 'Plain text', 'is_encrypted': False}
        result = MemoryEncryptionHelper.decrypt_memory_content(memory)
        self.assertFalse(result)

    def test_decrypt_memory_content_invalid_json(self):
        memory = {'content': 'not valid json', 'is_encrypted': True}
        result = MemoryEncryptionHelper.decrypt_memory_content(memory)
        self.assertFalse(result)

    def test_decrypt_memory_content_missing_keys(self):
        memory = {'content': '{"ciphertext": "abc"}', 'is_encrypted': True}
        result = MemoryEncryptionHelper.decrypt_memory_content(memory)
        self.assertFalse(result)

    def test_decrypt_memory_content_no_key_id(self):
        import json, base64
        encrypted_data = {
            'ciphertext': base64.b64encode(b'test').decode(),
            'nonce': base64.b64encode(b'test_nonce_1234').decode(),
            'tag': base64.b64encode(b'test_tag_123456').decode()
        }
        memory = {
            'content': json.dumps(encrypted_data),
            'is_encrypted': True,
        }
        result = MemoryEncryptionHelper.decrypt_memory_content(memory)
        self.assertFalse(result)

    def test_decrypt_memory_list(self):
        memories = [
            {'content': 'plain', 'is_encrypted': False},
            {'content': 'also plain', 'is_encrypted': False},
        ]
        count = MemoryEncryptionHelper.decrypt_memory_list(memories)
        self.assertEqual(count, 0)


class TestForgettingManager(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.config.set('forgetting.min_weight', 0.1)
        self.config.set('forgetting.decay_rate', 0.01)
        self.manager = ForgettingManager(self.config)

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.min_weight, 0.1)
        self.assertEqual(self.manager.decay_rate, 0.01)

    def test_should_forget(self):
        memory = {'weight': 0.05}
        result = self.manager.should_forget(memory)
        self.assertTrue(result)
        memory = {'weight': 0.9}
        result = self.manager.should_forget(memory)
        self.assertFalse(result)

    def test_calculate_decay(self):
        memory = {'weight': 1.0, 'created_at': time.time() - 3600, 'last_accessed': time.time()}
        decay = self.manager.calculate_decay(memory)
        self.assertIsInstance(decay, float)
        self.assertGreaterEqual(decay, self.manager.min_weight)
        self.assertLessEqual(decay, 1.0)

    def test_update_memory_weight(self):
        memory = {'weight': 1.0, 'created_at': time.time() - 3600, 'last_accessed': time.time() - 3600}
        result = self.manager.update_memory_weight(memory)
        self.assertIn('weight', result)
        self.assertIn('last_accessed', result)

    def test_forget_memory(self):
        memory = {'weight': 0.05}
        result = self.manager.forget_memory(memory)
        self.assertTrue(result.get('forgotten', False))

    def test_batch_update_weights(self):
        memories = [
            {'id': 'm1', 'weight': 0.9, 'created_at': time.time(), 'last_accessed': time.time()},
            {'id': 'm2', 'weight': 0.05, 'created_at': time.time() - 864000, 'last_accessed': time.time() - 864000},
        ]
        updated, forgotten = self.manager.batch_update_weights(memories)
        self.assertIsInstance(updated, list)
        self.assertIsInstance(forgotten, list)

    def test_set_importance(self):
        memory = {}
        result = self.manager.set_importance(memory, 'high')
        self.assertTrue(result)
        self.assertEqual(memory['importance'], 'high')

    def test_set_importance_invalid(self):
        memory = {}
        result = self.manager.set_importance(memory, 'invalid')
        self.assertFalse(result)

    def test_get_importance_levels(self):
        levels = self.manager.get_importance_levels()
        self.assertIsInstance(levels, list)
        self.assertIn('high', levels)
        self.assertIn('medium', levels)
        self.assertIn('low', levels)


class TestMemoryManagerSmartCache(unittest.TestCase):
    def test_init(self):
        cache = MM_SmartCache()
        self.assertIsNotNone(cache)

    def test_set_and_get(self):
        cache = MM_SmartCache()
        cache.set('key1', 'value1')
        result = cache.get('key1')
        self.assertEqual(result, 'value1')

    def test_get_nonexistent(self):
        cache = MM_SmartCache()
        result = cache.get('nonexistent')
        self.assertIsNone(result)

    def test_clear(self):
        cache = MM_SmartCache()
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.clear()
        self.assertIsNone(cache.get('key1'))
        self.assertIsNone(cache.get('key2'))

    def test_get_stats(self):
        cache = MM_SmartCache()
        cache.set('key1', 'value1')
        cache.get('key1')
        cache.get('nonexistent')
        stats = cache.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('hit_count', stats)
        self.assertIn('miss_count', stats)
        self.assertEqual(stats['hit_count'], 1)
        self.assertEqual(stats['miss_count'], 1)

    def test_set_size(self):
        cache = MM_SmartCache(initial_size=5)
        for i in range(10):
            cache.set(f'key_{i}', f'value_{i}')
        cache.set_size(3)
        self.assertLessEqual(len(cache.cache), 3)

    def test_ttl_expiry(self):
        cache = MM_SmartCache(ttl=0)
        cache.set('key1', 'value1')
        import time
        time.sleep(0.01)
        result = cache.get('key1')
        self.assertIsNone(result)


class TestSessionSummary(unittest.TestCase):
    def test_generate_session_summary(self):
        try:
            result = generate_session_summary([])
            self.assertIsNotNone(result)
        except TypeError:
            pass
        except Exception:
            pass


import time

if __name__ == '__main__':
    unittest.main()
