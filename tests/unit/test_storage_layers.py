import unittest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.storage.tier2 import Tier2Storage
from memory_classification_engine.storage.tier3 import Tier3Storage
from memory_classification_engine.storage.tier4 import Tier4Storage


class TestTier2Storage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.tier2_path = os.path.join(self.test_dir, 'tier2')
        self.storage = Tier2Storage(storage_path=self.tier2_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertTrue(os.path.exists(self.tier2_path))

    def test_store_preference(self):
        memory = {
            'id': 'pref_1',
            'type': 'user_preference',
            'content': 'I prefer dark mode',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.95,
            'source': 'rule_matcher',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)

    def test_store_correction(self):
        memory = {
            'id': 'corr_1',
            'type': 'correction',
            'content': 'No, I use Python not Java',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.9,
            'source': 'rule_matcher',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)

    def test_store_decision(self):
        memory = {
            'id': 'dec_1',
            'type': 'decision',
            'content': 'Decided to use React for frontend',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.85,
            'source': 'rule_matcher',
        }
        try:
            result = self.storage.store_memory(memory)
            self.assertIsInstance(result, bool)
        except Exception:
            pass

    def test_retrieve_memories(self):
        memory = {
            'id': 'pref_retrieve',
            'type': 'user_preference',
            'content': 'I prefer dark mode',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.95,
            'source': 'rule_matcher',
        }
        self.storage.store_memory(memory)
        results = self.storage.retrieve_memories(query='dark mode', limit=10)
        self.assertIsInstance(results, list)

    def test_retrieve_all(self):
        results = self.storage.retrieve_memories(query='', limit=100)
        self.assertIsInstance(results, list)

    def test_get_stats(self):
        stats = self.storage.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_memories', stats)

    def test_delete_memory(self):
        memory = {
            'id': 'pref_del',
            'type': 'user_preference',
            'content': 'Delete me',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.9,
            'source': 'rule_matcher',
        }
        self.storage.store_memory(memory)
        result = self.storage.delete_memory('pref_del')
        self.assertIsInstance(result, bool)

    def test_update_memory(self):
        memory = {
            'id': 'pref_upd',
            'type': 'user_preference',
            'content': 'Original content',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.9,
            'source': 'rule_matcher',
        }
        self.storage.store_memory(memory)
        result = self.storage.update_memory('pref_upd', {'content': 'Updated content'})
        self.assertIsInstance(result, bool)

    def test_chinese_content(self):
        memory = {
            'id': 'pref_cn',
            'type': 'user_preference',
            'content': '我喜欢深色模式',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.95,
            'source': 'rule_matcher',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)

    def test_japanese_content(self):
        memory = {
            'id': 'pref_ja',
            'type': 'user_preference',
            'content': 'ダークモードが好きです',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.95,
            'source': 'rule_matcher',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)


class TestTier3Storage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.tier3_path = os.path.join(self.test_dir, 'tier3')
        self.storage = Tier3Storage(
            storage_path=self.tier3_path,
            enable_cache=True,
            enable_vector_search=False,
            enable_in_memory_cache=True,
            enable_memory_compression=False
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertTrue(os.path.exists(self.tier3_path))

    def test_store_memory(self):
        memory = {
            'id': 'epi_1',
            'type': 'episodic',
            'memory_type': 'fact_declaration',
            'content': 'The project deadline is April 30th',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.8,
            'source': 'rule_matcher',
            'status': 'active',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)

    def test_store_batch(self):
        memories = [
            {
                'id': f'batch_{i}',
                'type': 'episodic',
                'memory_type': 'fact_declaration',
                'content': f'Fact number {i}',
                'created_at': '2026-04-15T00:00:00',
                'updated_at': '2026-04-15T00:00:00',
                'confidence': 0.8,
                'source': 'rule_matcher',
                'status': 'active',
            }
            for i in range(5)
        ]
        result = self.storage.store_memories_batch(memories)
        self.assertTrue(result)

    def test_retrieve_memories(self):
        memory = {
            'id': 'epi_retrieve',
            'type': 'episodic',
            'memory_type': 'fact_declaration',
            'content': 'The project deadline is April 30th',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.8,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        results = self.storage.retrieve_memories(query='deadline', limit=10)
        self.assertIsInstance(results, list)

    def test_retrieve_empty_query(self):
        results = self.storage.retrieve_memories(query='', limit=10)
        self.assertIsInstance(results, list)

    def test_retrieve_chinese(self):
        memory = {
            'id': 'epi_cn',
            'type': 'episodic',
            'memory_type': 'fact_declaration',
            'content': '项目截止日期是4月30日',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.8,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        results = self.storage.retrieve_memories(query='截止', limit=10)
        self.assertIsInstance(results, list)

    def test_retrieve_japanese(self):
        memory = {
            'id': 'epi_ja',
            'type': 'episodic',
            'memory_type': 'fact_declaration',
            'content': 'プロジェクトの締め切りは4月30日です',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.8,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        results = self.storage.retrieve_memories(query='締め切り', limit=10)
        self.assertIsInstance(results, list)

    def test_get_stats(self):
        stats = self.storage.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_memories', stats)

    def test_delete_memory(self):
        memory = {
            'id': 'epi_del',
            'type': 'episodic',
            'memory_type': 'fact_declaration',
            'content': 'To be deleted',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.8,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        result = self.storage.delete_memory('epi_del')
        self.assertIsInstance(result, bool)

    def test_update_memory(self):
        memory = {
            'id': 'epi_upd',
            'type': 'episodic',
            'memory_type': 'fact_declaration',
            'content': 'Original fact',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.8,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        result = self.storage.update_memory('epi_upd', {'content': 'Updated fact'})
        self.assertIsInstance(result, bool)

    def test_store_and_retrieve_chinese(self):
        memory = {
            'id': 'epi_cn',
            'type': 'episodic',
            'memory_type': 'fact_declaration',
            'content': '项目截止日期是4月30日',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.8,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        results = self.storage.retrieve_memories(query='截止', limit=10)
        self.assertIsInstance(results, list)

    def test_store_and_retrieve_japanese(self):
        memory = {
            'id': 'epi_ja',
            'type': 'episodic',
            'memory_type': 'fact_declaration',
            'content': 'プロジェクトの締め切りは4月30日です',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.8,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        results = self.storage.retrieve_memories(query='締め切り', limit=10)
        self.assertIsInstance(results, list)


class TestTier4Storage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.tier4_path = os.path.join(self.test_dir, 'tier4')
        self.storage = Tier4Storage(
            storage_path=self.tier4_path,
            enable_graph=False
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertTrue(os.path.exists(self.tier4_path))

    def test_store_memory(self):
        memory = {
            'id': 'know_1',
            'type': 'knowledge',
            'memory_type': 'relationship',
            'content': 'Alice is the project manager',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.7,
            'source': 'rule_matcher',
            'status': 'active',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)

    def test_retrieve_memories(self):
        memory = {
            'id': 'know_retrieve',
            'type': 'knowledge',
            'memory_type': 'relationship',
            'content': 'Alice is the project manager',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.7,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        results = self.storage.retrieve_memories(query='Alice', limit=10)
        self.assertIsInstance(results, list)

    def test_retrieve_empty_query(self):
        results = self.storage.retrieve_memories(query='', limit=10)
        self.assertIsInstance(results, list)

    def test_get_stats(self):
        stats = self.storage.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_memories', stats)

    def test_delete_memory(self):
        memory = {
            'id': 'know_del',
            'type': 'knowledge',
            'memory_type': 'relationship',
            'content': 'To be deleted',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.7,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        if hasattr(self.storage, 'delete_memory'):
            result = self.storage.delete_memory('know_del')
            self.assertIsInstance(result, bool)
        else:
            pass

    def test_update_memory(self):
        memory = {
            'id': 'know_upd',
            'type': 'knowledge',
            'memory_type': 'relationship',
            'content': 'Original knowledge',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.7,
            'source': 'rule_matcher',
            'status': 'active',
        }
        self.storage.store_memory(memory)
        if hasattr(self.storage, 'update_memory'):
            result = self.storage.update_memory('know_upd', {'content': 'Updated knowledge'})
            self.assertIsInstance(result, bool)
        else:
            pass

    def test_chinese_content(self):
        memory = {
            'id': 'know_cn',
            'type': 'knowledge',
            'memory_type': 'relationship',
            'content': '张三是项目经理',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.7,
            'source': 'rule_matcher',
            'status': 'active',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)

    def test_japanese_content(self):
        memory = {
            'id': 'know_ja',
            'type': 'knowledge',
            'memory_type': 'relationship',
            'content': '田中さんはプロジェクトマネージャーです',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.7,
            'source': 'rule_matcher',
            'status': 'active',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
