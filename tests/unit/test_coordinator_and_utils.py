import unittest
import os
import sys
import tempfile
import shutil
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.coordinators.storage_coordinator import StorageCoordinator
from memory_classification_engine.utils.memory_quality import MemoryQualityManager
from memory_classification_engine.utils.nudge_mechanism import NudgeManager
from memory_classification_engine.utils.pending_memories import PendingMemoryManager
from memory_classification_engine.utils.memory_migration import MemoryMigrationManager
from memory_classification_engine.utils.memory_association import MemoryAssociationManager
from memory_classification_engine.utils.evolution import EvolutionManager
from memory_classification_engine.utils.encryption import EncryptionManager
from memory_classification_engine.utils.access_control import AccessControlManager
from memory_classification_engine.utils.agentskills import AgentSkillsIO


class TestStorageCoordinator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = ConfigManager()
        self.config.set('storage.data_path', self.test_dir)
        self.config.set('storage.tier2_path', os.path.join(self.test_dir, 'tier2'))
        self.config.set('storage.tier3_path', os.path.join(self.test_dir, 'tier3'))
        self.config.set('storage.tier4_path', os.path.join(self.test_dir, 'tier4'))
        self.config.set('memory.forgetting.min_weight', 0.1)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        coordinator = StorageCoordinator(self.config)
        self.assertIsNotNone(coordinator)

    def test_get_stats(self):
        coordinator = StorageCoordinator(self.config)
        stats = coordinator.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_memories', stats)

    def test_store_memory(self):
        coordinator = StorageCoordinator(self.config)
        memory = {
            'id': 'coord_test_1',
            'type': 'user_preference',
            'content': 'I prefer dark mode',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.95,
            'source': 'rule_matcher',
            'tier': 2,
        }
        result = coordinator.store_memory(memory)
        self.assertIsNotNone(result)

    def test_retrieve_memories(self):
        coordinator = StorageCoordinator(self.config)
        result = coordinator.retrieve_memories(query='test', limit=10)
        self.assertIsInstance(result, list)

    def test_retrieve_memories_by_tier(self):
        coordinator = StorageCoordinator(self.config)
        result = coordinator.retrieve_memories(query='test', limit=10, tier=2)
        self.assertIsInstance(result, list)
        result = coordinator.retrieve_memories(query='test', limit=10, tier=3)
        self.assertIsInstance(result, list)
        result = coordinator.retrieve_memories(query='test', limit=10, tier=4)
        self.assertIsInstance(result, list)

    def test_store_and_retrieve(self):
        coordinator = StorageCoordinator(self.config)
        memory = {
            'id': 'coord_sr_1',
            'type': 'user_preference',
            'content': 'I prefer dark mode for coding',
            'created_at': '2026-04-15T00:00:00',
            'updated_at': '2026-04-15T00:00:00',
            'confidence': 0.95,
            'source': 'rule_matcher',
            'tier': 2,
        }
        coordinator.store_memory(memory)
        results = coordinator.retrieve_memories(query='dark mode', limit=10)
        self.assertIsInstance(results, list)


class TestMemoryQualityManager(unittest.TestCase):
    def setUp(self):
        self.manager = MemoryQualityManager()

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertIsInstance(self.manager.usage_tracker, dict)
        self.assertIsInstance(self.manager.feedback_tracker, dict)
        self.assertIsInstance(self.manager.quality_metrics, dict)

    def test_track_memory_usage(self):
        self.manager.track_memory_usage('mem_1', 'test query', result=True)
        self.assertIn('mem_1', self.manager.usage_tracker)
        self.assertEqual(self.manager.usage_tracker['mem_1']['total_usage'], 1)
        self.assertEqual(self.manager.usage_tracker['mem_1']['successful_usage'], 1)

    def test_track_memory_usage_multiple(self):
        self.manager.track_memory_usage('mem_2', 'query1', result=True)
        self.manager.track_memory_usage('mem_2', 'query2', result=False)
        self.assertEqual(self.manager.usage_tracker['mem_2']['total_usage'], 2)
        self.assertEqual(self.manager.usage_tracker['mem_2']['successful_usage'], 1)

    def test_track_feedback(self):
        self.manager.track_feedback('mem_1', 'positive')
        self.assertIn('mem_1', self.manager.feedback_tracker)
        self.assertEqual(self.manager.feedback_tracker['mem_1']['positive'], 1)

    def test_track_feedback_types(self):
        self.manager.track_feedback('mem_3', 'positive')
        self.manager.track_feedback('mem_3', 'negative')
        self.manager.track_feedback('mem_3', 'neutral')
        self.assertEqual(self.manager.feedback_tracker['mem_3']['positive'], 1)
        self.assertEqual(self.manager.feedback_tracker['mem_3']['negative'], 1)
        self.assertEqual(self.manager.feedback_tracker['mem_3']['neutral'], 1)

    def test_calculate_memory_quality(self):
        self.manager.track_memory_usage('mem_4', 'query1', result=True)
        self.manager.track_memory_usage('mem_4', 'query2', result=True)
        self.manager.track_feedback('mem_4', 'positive')
        metrics = self.manager.calculate_memory_quality('mem_4', {'id': 'mem_4'})
        self.assertIsInstance(metrics, dict)
        self.assertIn('overall_quality', metrics)
        self.assertIn('usage_frequency', metrics)
        self.assertIn('success_rate', metrics)
        self.assertIn('feedback_score', metrics)
        self.assertGreater(metrics['overall_quality'], 0)

    def test_calculate_memory_quality_no_data(self):
        metrics = self.manager.calculate_memory_quality('nonexistent', {'id': 'nonexistent'})
        self.assertIsInstance(metrics, dict)
        self.assertEqual(metrics['overall_quality'], 0)

    def test_get_memory_quality(self):
        self.manager.track_memory_usage('mem_5', 'query', result=True)
        self.manager.calculate_memory_quality('mem_5', {'id': 'mem_5'})
        quality = self.manager.get_memory_quality('mem_5')
        self.assertIsNotNone(quality)
        self.assertIn('overall_quality', quality)

    def test_get_memory_quality_not_found(self):
        quality = self.manager.get_memory_quality('nonexistent')
        self.assertIsNone(quality)

    def test_generate_quality_report(self):
        self.manager.track_memory_usage('mem_6', 'query', result=True)
        self.manager.track_feedback('mem_6', 'positive')
        report = self.manager.generate_quality_report()
        self.assertIsInstance(report, dict)
        self.assertIn('total_memories', report)
        self.assertIn('average_quality', report)

    def test_generate_low_value_report(self):
        self.manager.track_memory_usage('mem_7', 'query', result=False)
        report = self.manager.generate_low_value_report(threshold=0.3)
        self.assertIsInstance(report, list)

    def test_reset_tracking_specific(self):
        self.manager.track_memory_usage('mem_8', 'query', result=True)
        self.manager.reset_tracking('mem_8')
        self.assertNotIn('mem_8', self.manager.usage_tracker)

    def test_reset_tracking_all(self):
        self.manager.track_memory_usage('mem_9', 'query', result=True)
        self.manager.track_memory_usage('mem_10', 'query', result=True)
        self.manager.reset_tracking()
        self.assertEqual(len(self.manager.usage_tracker), 0)
        self.assertEqual(len(self.manager.feedback_tracker), 0)


class TestNudgeManager(unittest.TestCase):
    def _create_mock_storage(self):
        class MockStorage:
            def __init__(self):
                self.memories = []
            def retrieve_memories(self, query="", limit=100):
                return self.memories
            def get_memory(self, memory_id):
                for m in self.memories:
                    if m.get('id') == memory_id:
                        return m
                return None
            def update_memory(self, memory_id, memory):
                return True
        return MockStorage()

    def setUp(self):
        self.storage = self._create_mock_storage()
        self.nudge = NudgeManager(self.storage)

    def test_init(self):
        self.assertIsNotNone(self.nudge)
        self.assertEqual(self.nudge.nudge_threshold, 7)
        self.assertIsInstance(self.nudge.nudge_history, list)

    def test_get_nudge_candidates_empty(self):
        candidates = self.nudge.get_nudge_candidates()
        self.assertIsInstance(candidates, list)
        self.assertEqual(len(candidates), 0)

    def test_get_nudge_candidates_with_memories(self):
        self.storage.memories = [
            {'id': 'm1', 'content': 'Test', 'memory_type': 'user_preference', 'confidence': 0.5},
            {'id': 'm2', 'content': 'Another', 'memory_type': 'decision', 'confidence': 0.9},
        ]
        candidates = self.nudge.get_nudge_candidates(limit=5)
        self.assertIsInstance(candidates, list)

    def test_calculate_nudge_score(self):
        memory = {'memory_type': 'user_preference', 'confidence': 0.5}
        score = self.nudge._calculate_nudge_score(memory)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)

    def test_calculate_nudge_score_never_reviewed(self):
        memory = {'memory_type': 'decision', 'confidence': 0.3}
        score = self.nudge._calculate_nudge_score(memory)
        self.assertGreater(score, 5.0)

    def test_generate_nudge_prompt(self):
        memory = {
            'memory_type': 'user_preference',
            'content': 'I prefer dark mode',
            'created_at': '2026-01-01',
        }
        prompt = self.nudge.generate_nudge_prompt(memory)
        self.assertIsInstance(prompt, str)
        self.assertIn('user_preference', prompt)
        self.assertIn('dark mode', prompt)

    def test_record_nudge_interaction(self):
        self.storage.memories = [
            {'id': 'm1', 'content': 'Test', 'memory_type': 'user_preference', 'confidence': 0.5, 'usage_count': 0},
        ]
        result = self.nudge.record_nudge_interaction('m1', 'confirm')
        self.assertTrue(result)
        self.assertEqual(len(self.nudge.nudge_history), 1)

    def test_record_nudge_interaction_not_found(self):
        result = self.nudge.record_nudge_interaction('nonexistent', 'confirm')
        self.assertFalse(result)

    def test_get_nudge_stats(self):
        stats = self.nudge.get_nudge_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_nudges', stats)
        self.assertIn('actions', stats)

    def test_should_nudge_no_candidates(self):
        result = self.nudge.should_nudge()
        self.assertFalse(result)


class TestPendingMemoryManager(unittest.TestCase):
    def _create_mock_storage(self):
        class MockStorage:
            def __init__(self):
                self.stored = []
            def store_memory(self, memory):
                self.stored.append(memory)
                return True
        return MockStorage()

    def setUp(self):
        self.storage = self._create_mock_storage()
        self.manager = PendingMemoryManager(self.storage)

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertIsInstance(self.manager.pending_memories, list)
        self.assertEqual(len(self.manager.pending_memories), 0)

    def test_add_pending_memory(self):
        memory = {'content': 'Test memory', 'memory_type': 'user_preference'}
        memory_id = self.manager.add_pending_memory(memory)
        self.assertIsInstance(memory_id, str)
        self.assertTrue(memory_id.startswith('pending_'))
        self.assertEqual(len(self.manager.pending_memories), 1)

    def test_get_pending_memories(self):
        self.manager.add_pending_memory({'content': 'Memory 1'})
        self.manager.add_pending_memory({'content': 'Memory 2'})
        pending = self.manager.get_pending_memories()
        self.assertIsInstance(pending, list)
        self.assertEqual(len(pending), 2)

    def test_get_pending_memories_with_limit(self):
        for i in range(5):
            self.manager.add_pending_memory({'content': f'Memory {i}'})
        pending = self.manager.get_pending_memories(limit=3)
        self.assertEqual(len(pending), 3)

    def test_approve_memory(self):
        self.manager.add_pending_memory({'content': 'Test', 'memory_type': 'fact_declaration'})
        pending = self.manager.get_pending_memories()
        memory_id = pending[0]['id']
        result = self.manager.approve_memory(memory_id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.pending_memories), 0)
        self.assertEqual(len(self.storage.stored), 1)

    def test_approve_memory_not_found(self):
        result = self.manager.approve_memory('nonexistent')
        self.assertFalse(result)

    def test_reject_memory(self):
        self.manager.add_pending_memory({'content': 'Test'})
        pending = self.manager.get_pending_memories()
        memory_id = pending[0]['id']
        result = self.manager.reject_memory(memory_id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.pending_memories), 0)

    def test_reject_memory_not_found(self):
        result = self.manager.reject_memory('nonexistent')
        self.assertFalse(result)

    def test_get_pending_count(self):
        self.manager.add_pending_memory({'content': 'Test 1'})
        self.manager.add_pending_memory({'content': 'Test 2'})
        self.assertEqual(self.manager.get_pending_count(), 2)

    def test_clear_all_pending(self):
        for i in range(3):
            self.manager.add_pending_memory({'content': f'Test {i}'})
        count = self.manager.clear_all_pending()
        self.assertEqual(count, 3)
        self.assertEqual(len(self.manager.pending_memories), 0)


class TestMemoryMigrationManager(unittest.TestCase):
    def setUp(self):
        self.manager = MemoryMigrationManager()

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.export_version, "1.0")

    def test_export_memories(self):
        memories = [
            {'id': 'mem_1', 'content': 'Test content 1', 'memory_type': 'user_preference', 'tier': 2, 'confidence': 0.9},
            {'id': 'mem_2', 'content': 'Test content 2', 'memory_type': 'fact_declaration', 'tier': 3, 'confidence': 0.8},
        ]
        json_str = self.manager.export_memories(memories)
        self.assertIsInstance(json_str, str)
        self.assertIn('mem_1', json_str)
        self.assertIn('mem_2', json_str)

    def test_import_memories(self):
        memories = [
            {'id': 'mem_1', 'content': 'Test', 'memory_type': 'user_preference', 'tier': 2, 'confidence': 0.9},
        ]
        json_str = self.manager.export_memories(memories)
        imported = self.manager.import_memories(json_str)
        self.assertIsInstance(imported, list)
        self.assertEqual(len(imported), 1)
        self.assertEqual(imported[0]['id'], 'mem_1')

    def test_export_import_roundtrip(self):
        memories = [
            {'id': 'mem_a', 'content': 'Content A', 'memory_type': 'correction', 'tier': 3, 'confidence': 0.85},
            {'id': 'mem_b', 'content': 'Content B', 'memory_type': 'decision', 'tier': 4, 'confidence': 0.75},
        ]
        json_str = self.manager.export_memories(memories)
        imported = self.manager.import_memories(json_str)
        self.assertEqual(len(imported), 2)
        for orig, imp in zip(memories, imported):
            self.assertEqual(orig['id'], imp['id'])
            self.assertEqual(orig['content'], imp['content'])

    def test_validate_export_data(self):
        memories = [{'id': 'm1', 'content': 'Test', 'memory_type': 'fact_declaration'}]
        json_str = self.manager.export_memories(memories)
        result = self.manager.validate_export_data(json_str)
        self.assertIsInstance(result, dict)
        self.assertTrue(result['valid'])

    def test_validate_export_data_invalid_json(self):
        result = self.manager.validate_export_data('not valid json')
        self.assertIsInstance(result, dict)
        self.assertFalse(result['valid'])

    def test_export_to_file(self):
        test_dir = tempfile.mkdtemp()
        try:
            file_path = os.path.join(test_dir, 'test_export.json')
            memories = [{'id': 'm1', 'content': 'Test', 'memory_type': 'user_preference'}]
            self.manager.export_to_file(memories, file_path)
            self.assertTrue(os.path.exists(file_path))
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_import_from_file(self):
        test_dir = tempfile.mkdtemp()
        try:
            file_path = os.path.join(test_dir, 'test_import.json')
            memories = [{'id': 'm1', 'content': 'File test', 'memory_type': 'decision'}]
            self.manager.export_to_file(memories, file_path)
            imported = self.manager.import_from_file(file_path)
            self.assertEqual(len(imported), 1)
            self.assertEqual(imported[0]['id'], 'm1')
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_import_from_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.manager.import_from_file('/nonexistent/path/file.json')


class TestMemoryAssociationManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manager = MemoryAssociationManager(
            storage_path=self.test_dir,
            cache_size=100,
            cache_ttl=60
        )

    def tearDown(self):
        self.manager.clear_all_associations()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertIsInstance(self.manager.associations, dict)

    def test_create_association(self):
        self.manager.create_association('mem_1', 'mem_2', 0.8)
        associations = self.manager.get_associations('mem_1')
        self.assertIsInstance(associations, list)
        self.assertGreater(len(associations), 0)
        self.assertEqual(associations[0]['target_id'], 'mem_2')

    def test_create_association_bidirectional(self):
        self.manager.create_association('mem_a', 'mem_b', 0.7)
        assoc_a = self.manager.get_associations('mem_a')
        assoc_b = self.manager.get_associations('mem_b')
        self.assertGreater(len(assoc_a), 0)
        self.assertGreater(len(assoc_b), 0)

    def test_create_association_with_metadata(self):
        self.manager.create_association('mem_1', 'mem_2', 0.9, metadata={'type': 'semantic'})
        associations = self.manager.get_associations('mem_1')
        self.assertEqual(associations[0]['metadata']['type'], 'semantic')

    def test_get_associations_empty(self):
        associations = self.manager.get_associations('nonexistent')
        self.assertIsInstance(associations, list)
        self.assertEqual(len(associations), 0)

    def test_get_associations_min_similarity(self):
        self.manager.create_association('mem_1', 'mem_2', 0.3)
        self.manager.create_association('mem_1', 'mem_3', 0.8)
        associations = self.manager.get_associations('mem_1', min_similarity=0.5)
        self.assertEqual(len(associations), 1)
        self.assertEqual(associations[0]['target_id'], 'mem_3')

    def test_remove_association(self):
        self.manager.create_association('mem_1', 'mem_2', 0.8)
        self.manager.remove_association('mem_1', 'mem_2')
        associations = self.manager.get_associations('mem_1')
        self.assertEqual(len(associations), 0)

    def test_remove_memory_associations(self):
        self.manager.create_association('mem_1', 'mem_2', 0.8)
        self.manager.create_association('mem_1', 'mem_3', 0.7)
        self.manager.remove_memory_associations('mem_1')
        associations = self.manager.get_associations('mem_1')
        self.assertEqual(len(associations), 0)

    def test_get_stats(self):
        self.manager.create_association('mem_1', 'mem_2', 0.8)
        stats = self.manager.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_associations', stats)
        self.assertIn('memory_count', stats)

    def test_clear_all_associations(self):
        self.manager.create_association('mem_1', 'mem_2', 0.8)
        self.manager.clear_all_associations()
        stats = self.manager.get_stats()
        self.assertEqual(stats['total_associations'], 0)


class TestEvolutionManager(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.config.set('evolution.feedback_threshold', 3)
        self.config.set('evolution.rule_adjustment_rate', 0.1)
        self.manager = EvolutionManager(self.config)

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.feedback_threshold, 3)
        self.assertEqual(self.manager.rule_adjustment_rate, 0.1)

    def test_process_feedback(self):
        memory = {'id': 'mem_1', 'content': 'Test'}
        result = self.manager.process_feedback(memory, 'positive')
        self.assertIn('feedback', result)
        self.assertEqual(len(result['feedback']), 1)

    def test_process_feedback_triggers_adjustment(self):
        memory = {'id': 'mem_1', 'content': 'Test'}
        for i in range(3):
            self.manager.process_feedback(memory, f'feedback_{i}')
        self.assertEqual(len(memory['feedback']), 0)

    def test_optimize_weight_calculation(self):
        memories = [{'id': 'm1'}, {'id': 'm2'}]
        result = self.manager.optimize_weight_calculation(memories)
        self.assertEqual(result, memories)

    def test_optimize_performance(self):
        result = self.manager.optimize_performance()
        self.assertTrue(result)

    def test_record_performance(self):
        self.manager.record_performance('classify', 0.5)
        self.manager.record_performance('classify', 0.3)
        self.assertEqual(len(self.manager.performance_history), 2)

    def test_get_performance_stats(self):
        self.manager.record_performance('classify', 0.5)
        self.manager.record_performance('classify', 0.3)
        stats = self.manager.get_performance_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('average_duration', stats)
        self.assertIn('operation_stats', stats)

    def test_get_performance_stats_empty(self):
        stats = self.manager.get_performance_stats()
        self.assertEqual(stats, {})

    def test_performance_history_limit(self):
        for i in range(150):
            self.manager.record_performance('op', 0.1)
        self.assertLessEqual(len(self.manager.performance_history), 100)


class TestEncryptionManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        key_path = os.path.join(self.test_dir, 'test_encryption.key')
        self.manager = EncryptionManager(key_path=key_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.fernet)

    def test_encrypt_decrypt(self):
        original = 'sensitive data'
        encrypted = self.manager.encrypt(original)
        decrypted = self.manager.decrypt(encrypted)
        self.assertEqual(original, decrypted)

    def test_encrypt_returns_string(self):
        result = self.manager.encrypt('test data')
        self.assertIsInstance(result, str)

    def test_decrypt_returns_string(self):
        encrypted = self.manager.encrypt('test data')
        result = self.manager.decrypt(encrypted)
        self.assertIsInstance(result, str)

    def test_encrypt_decrypt_unicode(self):
        original = '敏感数据 日本語テスト'
        encrypted = self.manager.encrypt(original)
        decrypted = self.manager.decrypt(encrypted)
        self.assertEqual(original, decrypted)

    def test_encrypt_dict(self):
        data = {'name': 'test', 'value': 42, 'secret': 'hidden'}
        encrypted = self.manager.encrypt_dict(data)
        self.assertIsInstance(encrypted, dict)
        self.assertEqual(encrypted['value'], 42)
        self.assertNotEqual(encrypted['name'], 'test')

    def test_decrypt_dict(self):
        data = {'name': 'test', 'value': 42}
        encrypted = self.manager.encrypt_dict(data)
        decrypted = self.manager.decrypt_dict(encrypted)
        self.assertEqual(decrypted['name'], 'test')
        self.assertEqual(decrypted['value'], 42)

    def test_key_persistence(self):
        key_path = os.path.join(self.test_dir, 'persist.key')
        manager1 = EncryptionManager(key_path=key_path)
        encrypted = manager1.encrypt('test')
        manager2 = EncryptionManager(key_path=key_path)
        decrypted = manager2.decrypt(encrypted)
        self.assertEqual('test', decrypted)


class TestAccessControlManager(unittest.TestCase):
    def setUp(self):
        self.manager = AccessControlManager()

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertIn('admin', self.manager.roles)
        self.assertIn('user', self.manager.roles)
        self.assertIn('guest', self.manager.roles)

    def test_add_user(self):
        self.manager.add_user('user1', 'user')
        self.assertIn('user1', self.manager.users)
        self.assertEqual(self.manager.users['user1'], 'user')

    def test_add_user_invalid_role(self):
        with self.assertRaises(ValueError):
            self.manager.add_user('user1', 'invalid_role')

    def test_has_permission(self):
        self.manager.add_user('admin1', 'admin')
        self.assertTrue(self.manager.has_permission('admin1', 'read'))
        self.assertTrue(self.manager.has_permission('admin1', 'write'))
        self.assertTrue(self.manager.has_permission('admin1', 'delete'))
        self.assertTrue(self.manager.has_permission('admin1', 'admin'))

    def test_has_permission_guest(self):
        self.manager.add_user('guest1', 'guest')
        self.assertTrue(self.manager.has_permission('guest1', 'read'))
        self.assertFalse(self.manager.has_permission('guest1', 'write'))
        self.assertFalse(self.manager.has_permission('guest1', 'delete'))

    def test_has_permission_unknown_user(self):
        self.assertFalse(self.manager.has_permission('unknown', 'read'))

    def test_get_user_role(self):
        self.manager.add_user('user1', 'user')
        self.assertEqual(self.manager.get_user_role('user1'), 'user')

    def test_get_user_role_not_found(self):
        self.assertIsNone(self.manager.get_user_role('unknown'))

    def test_update_user_role(self):
        self.manager.add_user('user1', 'user')
        self.manager.update_user_role('user1', 'admin')
        self.assertEqual(self.manager.users['user1'], 'admin')

    def test_update_user_role_invalid(self):
        self.manager.add_user('user1', 'user')
        with self.assertRaises(ValueError):
            self.manager.update_user_role('user1', 'invalid')

    def test_update_user_role_not_found(self):
        with self.assertRaises(ValueError):
            self.manager.update_user_role('unknown', 'admin')

    def test_remove_user(self):
        self.manager.add_user('user1', 'user')
        self.manager.remove_user('user1')
        self.assertNotIn('user1', self.manager.users)

    def test_get_all_users(self):
        self.manager.add_user('user1', 'user')
        self.manager.add_user('admin1', 'admin')
        users = self.manager.get_all_users()
        self.assertIsInstance(users, dict)
        self.assertEqual(len(users), 2)

    def test_get_all_roles(self):
        roles = self.manager.get_all_roles()
        self.assertIsInstance(roles, dict)
        self.assertIn('admin', roles)
        self.assertIn('user', roles)
        self.assertIn('guest', roles)


class TestAgentSkillsIO(unittest.TestCase):
    def test_mce_to_agentskills(self):
        mce_rule = {
            'name': 'test-rule',
            'description': 'Test rule',
            'memory_type': 'user_preference',
            'example': 'I prefer dark mode',
        }
        skill = AgentSkillsIO.mce_to_agentskills(mce_rule)
        self.assertIsInstance(skill, dict)
        self.assertEqual(skill['name'], 'test-rule')
        self.assertIn('inputSchema', skill)
        self.assertIn('outputSchema', skill)
        self.assertEqual(skill['category'], 'preference')

    def test_agentskills_to_mce(self):
        skill = {
            'name': 'test-skill',
            'description': 'Test skill',
            'category': 'preference',
            'version': '1.0.0',
            'examples': [{'input': {'message': 'I prefer dark mode'}}],
        }
        mce_rule = AgentSkillsIO.agentskills_to_mce(skill)
        self.assertIsInstance(mce_rule, dict)
        self.assertEqual(mce_rule['name'], 'test-skill')
        self.assertEqual(mce_rule['memory_type'], 'user_preference')
        self.assertEqual(mce_rule['tier'], 2)

    def test_roundtrip_conversion(self):
        mce_rule = {
            'name': 'round-trip',
            'description': 'Round trip test',
            'memory_type': 'correction',
            'example': 'Actually, use double quotes',
        }
        skill = AgentSkillsIO.mce_to_agentskills(mce_rule)
        back = AgentSkillsIO.agentskills_to_mce(skill)
        self.assertEqual(back['name'], 'round-trip')
        self.assertEqual(back['memory_type'], 'correction')

    def test_map_memory_type(self):
        self.assertEqual(AgentSkillsIO._map_memory_type('user_preference'), 'preference')
        self.assertEqual(AgentSkillsIO._map_memory_type('correction'), 'correction')
        self.assertEqual(AgentSkillsIO._map_memory_type('fact_declaration'), 'fact')
        self.assertEqual(AgentSkillsIO._map_memory_type('decision'), 'decision')
        self.assertEqual(AgentSkillsIO._map_memory_type('unknown_type'), 'general')

    def test_map_category(self):
        self.assertEqual(AgentSkillsIO._map_category('preference'), 'user_preference')
        self.assertEqual(AgentSkillsIO._map_category('fact'), 'fact_declaration')
        self.assertEqual(AgentSkillsIO._map_category('unknown'), 'general')

    def test_get_tier(self):
        self.assertEqual(AgentSkillsIO._get_tier('preference'), 2)
        self.assertEqual(AgentSkillsIO._get_tier('fact'), 4)
        self.assertEqual(AgentSkillsIO._get_tier('correction'), 3)
        self.assertEqual(AgentSkillsIO._get_tier('unknown'), 3)

    def test_save_and_load_skill(self):
        test_dir = tempfile.mkdtemp()
        try:
            skill = {
                'name': 'test-skill',
                'description': 'Test skill description',
                'category': 'preference',
                'content': 'This is the skill content',
            }
            file_path = os.path.join(test_dir, 'SKILL.md')
            AgentSkillsIO.save_skill(skill, file_path)
            self.assertTrue(os.path.exists(file_path))
            loaded = AgentSkillsIO.load_skill(file_path)
            self.assertEqual(loaded['name'], 'test-skill')
            self.assertEqual(loaded['content'], 'This is the skill content')
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
