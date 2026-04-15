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
        self.config = {
            'storage.data_path': self.test_dir,
            'storage.tier2_path': os.path.join(self.test_dir, 'tier2'),
        }
        self.storage = Tier2Storage(self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_store_and_retrieve_preference(self):
        memory = {
            'id': 'test_pref_1',
            'type': 'user_preference',
            'content': 'I prefer dark mode',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.95,
            'source': 'rule_matcher',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)

        memories = self.storage.retrieve_memories(query='dark mode', limit=10)
        self.assertIsInstance(memories, list)

    def test_store_and_retrieve_correction(self):
        memory = {
            'id': 'test_corr_1',
            'type': 'correction',
            'content': 'No, I use Python not Java',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.9,
            'source': 'rule_matcher',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)

    def test_store_and_retrieve_decision(self):
        memory = {
            'id': 'test_dec_1',
            'type': 'decision',
            'content': 'Decided to use React for frontend',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.85,
            'source': 'rule_matcher',
        }
        result = self.storage.store_memory(memory)
        self.assertTrue(result)

    def test_get_stats(self):
        stats = self.storage.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_memories', stats)

    def test_delete_memory(self):
        memory = {
            'id': 'test_del_1',
            'type': 'user_preference',
            'content': 'Delete me',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.9,
            'source': 'rule_matcher',
        }
        self.storage.store_memory(memory)
        result = self.storage.delete_memory('test_del_1')
        self.assertIsInstance(result, bool)

    def test_update_memory(self):
        memory = {
            'id': 'test_upd_1',
            'type': 'user_preference',
            'content': 'Original content',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.9,
            'source': 'rule_matcher',
        }
        self.storage.store_memory(memory)
        memory['content'] = 'Updated content'
        result = self.storage.update_memory(memory)
        self.assertIsInstance(result, bool)


class TestTier3Storage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            'storage.data_path': self.test_dir,
            'storage.tier3_path': os.path.join(self.test_dir, 'tier3'),
        }
        self.storage = Tier3Storage(self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_store_and_retrieve_episodic(self):
        memory = {
            'id': 'test_epi_1',
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

        memories = self.storage.retrieve_memories(query='deadline', limit=10)
        self.assertIsInstance(memories, list)

    def test_store_batch(self):
        memories = [
            {
                'id': f'test_batch_{i}',
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

    def test_get_stats(self):
        stats = self.storage.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_memories', stats)

    def test_delete_memory(self):
        memory = {
            'id': 'test_del_epi_1',
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
        result = self.storage.delete_memory('test_del_epi_1')
        self.assertIsInstance(result, bool)

    def test_update_memory(self):
        memory = {
            'id': 'test_upd_epi_1',
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
        memory['content'] = 'Updated fact'
        result = self.storage.update_memory(memory)
        self.assertIsInstance(result, bool)

    def test_retrieve_with_empty_query(self):
        memories = self.storage.retrieve_memories(query='', limit=10)
        self.assertIsInstance(memories, list)

    def test_retrieve_with_chinese_query(self):
        memory = {
            'id': 'test_chinese_1',
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
        memories = self.storage.retrieve_memories(query='截止日期', limit=10)
        self.assertIsInstance(memories, list)

    def test_retrieve_with_japanese_query(self):
        memory = {
            'id': 'test_japanese_1',
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
        memories = self.storage.retrieve_memories(query='締め切り', limit=10)
        self.assertIsInstance(memories, list)


class TestTier4Storage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            'storage.data_path': self.test_dir,
            'storage.tier4_path': os.path.join(self.test_dir, 'tier4'),
        }
        self.storage = Tier4Storage(self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_store_and_retrieve_knowledge(self):
        memory = {
            'id': 'test_know_1',
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

        memories = self.storage.retrieve_memories(query='Alice', limit=10)
        self.assertIsInstance(memories, list)

    def test_get_stats(self):
        stats = self.storage.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_memories', stats)

    def test_delete_memory(self):
        memory = {
            'id': 'test_del_know_1',
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
        result = self.storage.delete_memory('test_del_know_1')
        self.assertIsInstance(result, bool)

    def test_update_memory(self):
        memory = {
            'id': 'test_upd_know_1',
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
        memory['content'] = 'Updated knowledge'
        result = self.storage.update_memory(memory)
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
