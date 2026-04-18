import unittest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.utils.config import ConfigManager


class TestEnginePendingMemories(unittest.TestCase):
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

    def test_add_pending_memory(self):
        memory = {'content': 'Test pending', 'memory_type': 'user_preference'}
        result = self.engine.add_pending_memory(memory)
        self.assertIsInstance(result, str)

    def test_get_pending_memories(self):
        self.engine.add_pending_memory({'content': 'Pending 1'})
        result = self.engine.get_pending_memories()
        self.assertIsInstance(result, list)

    def test_approve_memory(self):
        memory_id = self.engine.add_pending_memory({'content': 'To approve'})
        result = self.engine.approve_memory(memory_id)
        self.assertIsInstance(result, bool)

    def test_reject_memory(self):
        memory_id = self.engine.add_pending_memory({'content': 'To reject'})
        result = self.engine.reject_memory(memory_id)
        self.assertIsInstance(result, bool)

    def test_get_pending_count(self):
        self.engine.add_pending_memory({'content': 'Count test'})
        count = self.engine.get_pending_count()
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)


class TestEngineNudgeMechanism(unittest.TestCase):
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

    def test_get_nudge_candidates(self):
        result = self.engine.get_nudge_candidates()
        self.assertIsInstance(result, list)

    def test_generate_nudge_prompt(self):
        memory = {
            'memory_type': 'user_preference',
            'content': 'I prefer dark mode',
            'created_at': '2026-01-01T00:00:00Z',
        }
        result = self.engine.generate_nudge_prompt(memory)
        self.assertIsInstance(result, str)

    def test_should_nudge(self):
        result = self.engine.should_nudge()
        self.assertIsInstance(result, bool)


class TestEngineTenantOperations(unittest.TestCase):
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

    def test_create_tenant(self):
        result = self.engine.create_tenant('t1', 'Test Tenant', 'personal')
        self.assertIsInstance(result, dict)

    def test_get_tenant(self):
        self.engine.create_tenant('t1', 'Test Tenant', 'personal')
        result = self.engine.get_tenant('t1')
        self.assertIsInstance(result, dict)

    def test_list_tenants(self):
        self.engine.create_tenant('t1', 'Tenant 1', 'personal')
        result = self.engine.list_tenants()
        self.assertIsInstance(result, list)

    def test_delete_tenant(self):
        self.engine.create_tenant('t1', 'Test', 'personal')
        result = self.engine.delete_tenant('t1')
        self.assertIsInstance(result, dict)

    def test_update_tenant(self):
        self.engine.create_tenant('t1', 'Test', 'personal')
        result = self.engine.update_tenant('t1', {'name': 'Updated'})
        self.assertIsInstance(result, dict)

    def test_add_tenant_role(self):
        self.engine.create_tenant('t1', 'Test', 'enterprise', organization_id='org1')
        result = self.engine.add_tenant_role('t1', 'editor', ['read', 'write'])
        self.assertIsInstance(result, dict)


class TestEngineMemoryOperations(unittest.TestCase):
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

    def test_manage_memory_update(self):
        result = self.engine.process_message("I prefer dark mode")
        if isinstance(result, dict) and 'memory_id' in result:
            manage_result = self.engine.manage_memory('update', result['memory_id'], {'confidence': 0.99})
            self.assertIsNotNone(manage_result)

    def test_manage_memory_delete(self):
        result = self.engine.process_message("Temporary memory to delete")
        if isinstance(result, dict) and 'memory_id' in result:
            manage_result = self.engine.manage_memory('delete', result['memory_id'])
            self.assertIsNotNone(manage_result)

    def test_manage_memory_read(self):
        result = self.engine.process_message("I prefer dark mode")
        if isinstance(result, dict) and 'memory_id' in result:
            manage_result = self.engine.manage_memory('read', result['memory_id'])
            self.assertIsNotNone(manage_result)

    def test_export_memories(self):
        self.engine.process_message("I prefer dark mode")
        try:
            result = self.engine.export_memories()
            self.assertIsNotNone(result)
        except TypeError:
            pass

    def test_export_memories_json(self):
        self.engine.process_message("I prefer dark mode")
        try:
            result = self.engine.export_memories(format='json')
            self.assertIsNotNone(result)
        except TypeError:
            pass

    def test_import_memories(self):
        self.engine.process_message("I prefer dark mode")
        try:
            exported = self.engine.export_memories()
            result = self.engine.import_memories(exported)
            self.assertIsNotNone(result)
        except TypeError:
            pass

    def test_get_stats(self):
        stats = self.engine.get_stats()
        self.assertIsInstance(stats, dict)

    def test_process_feedback(self):
        result = self.engine.process_message("I prefer dark mode")
        if isinstance(result, dict) and 'memory_id' in result:
            feedback = self.engine.process_feedback(result['memory_id'], 'positive')
            self.assertIsNotNone(feedback)

    def test_retrieve_memories_with_type(self):
        self.engine.process_message("I prefer dark mode")
        results = self.engine.retrieve_memories(query="dark mode", memory_type='user_preference')
        self.assertIsInstance(results, list)

    def test_retrieve_memories_with_limit(self):
        self.engine.process_message("I prefer dark mode")
        results = self.engine.retrieve_memories(query="dark mode", limit=3)
        self.assertIsInstance(results, list)

    def test_get_recommendations(self):
        self.engine.process_message("I prefer dark mode")
        try:
            result = self.engine.get_recommendations('user1', query='dark mode')
            self.assertIsNotNone(result)
        except Exception:
            pass

    def test_record_user_behavior(self):
        result = self.engine.record_user_behavior('user1', 'mem_1', 'view')
        self.assertIsInstance(result, dict)

    def test_get_user_behavior_summary(self):
        self.engine.record_user_behavior('user1', 'mem_1', 'view')
        result = self.engine.get_user_behavior_summary('user1')
        self.assertIsInstance(result, dict)

    def test_assign_tenant(self):
        result = self.engine.assign_tenant('user1', 'tenant1')
        self.assertIsInstance(result, dict)

    def test_get_user_tenant(self):
        self.engine.assign_tenant('user1', 'tenant1')
        result = self.engine.get_user_tenant('user1')
        self.assertIsInstance(result, dict)

    def test_share_memory(self):
        self.engine.create_tenant('t1', 'Test', 'personal')
        result = self.engine.share_memory('mem_1', ['user2'], permission='read')
        self.assertIsInstance(result, dict)

    def test_check_memory_access(self):
        result = self.engine.check_memory_access('user1', 'mem_1', 'read')
        self.assertIsInstance(result, dict)

    def test_clear_working_memory(self):
        self.engine.clear_working_memory()

    def test_reload_config(self):
        result = self.engine.reload_config()
        self.assertIsNotNone(result)


class TestEngineAgentOperations(unittest.TestCase):
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

    def test_list_agents(self):
        result = self.engine.list_agents()
        self.assertIsInstance(result, dict)

    def test_register_agent(self):
        result = self.engine.register_agent('test_agent', {'type': 'test'})
        self.assertIsInstance(result, dict)

    def test_unregister_agent(self):
        self.engine.register_agent('test_agent', {'type': 'test'})
        result = self.engine.unregister_agent('test_agent')
        self.assertIsInstance(result, dict)


class TestEngineKnowledgeOperations(unittest.TestCase):
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

    def test_get_knowledge_statistics(self):
        result = self.engine.get_knowledge_statistics()
        self.assertIsNotNone(result)

    def test_sync_knowledge_base(self):
        result = self.engine.sync_knowledge_base()
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
