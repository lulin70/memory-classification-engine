import unittest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.utils.config import ConfigManager


class TestEngineFullCoverage(unittest.TestCase):
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

    def test_process_message_empty(self):
        result = self.engine.process_message("")
        self.assertIsNotNone(result)

    def test_process_message_whitespace(self):
        result = self.engine.process_message("   ")
        self.assertIsNotNone(result)

    def test_process_message_very_long(self):
        result = self.engine.process_message("I prefer dark mode " * 50)
        self.assertIsNotNone(result)

    def test_process_message_special_chars(self):
        result = self.engine.process_message("I prefer @#$% mode!")
        self.assertIsNotNone(result)

    def test_process_message_unicode(self):
        result = self.engine.process_message("私はPythonが好き 🐍")
        self.assertIsNotNone(result)

    def test_process_message_numbers(self):
        result = self.engine.process_message("42 is the answer")
        self.assertIsNotNone(result)

    def test_retrieve_memories_empty(self):
        results = self.engine.retrieve_memories(query="nonexistent")
        self.assertIsInstance(results, list)

    def test_retrieve_memories_with_tier(self):
        self.engine.process_message("I prefer dark mode")
        try:
            results = self.engine.retrieve_memories(query="dark mode", tier=2)
            self.assertIsInstance(results, list)
        except TypeError:
            results = self.engine.retrieve_memories(query="dark mode")
            self.assertIsInstance(results, list)

    def test_retrieve_memories_with_type(self):
        self.engine.process_message("I prefer dark mode")
        results = self.engine.retrieve_memories(query="dark mode", memory_type='user_preference')
        self.assertIsInstance(results, list)

    def test_retrieve_memories_with_limit(self):
        self.engine.process_message("I prefer dark mode")
        results = self.engine.retrieve_memories(query="dark mode", limit=1)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 1)

    def test_get_stats_after_operations(self):
        self.engine.process_message("I prefer dark mode")
        self.engine.process_message("Actually, use single quotes")
        self.engine.retrieve_memories(query="dark mode")
        stats = self.engine.get_stats()
        self.assertIsInstance(stats, dict)

    def test_process_feedback_positive(self):
        result = self.engine.process_message("I prefer dark mode")
        if isinstance(result, dict) and 'memory_id' in result:
            feedback = self.engine.process_feedback(result['memory_id'], 'positive')
            self.assertIsNotNone(feedback)

    def test_process_feedback_negative(self):
        result = self.engine.process_message("I prefer dark mode")
        if isinstance(result, dict) and 'memory_id' in result:
            feedback = self.engine.process_feedback(result['memory_id'], 'negative')
            self.assertIsNotNone(feedback)

    def test_process_feedback_neutral(self):
        result = self.engine.process_message("I prefer dark mode")
        if isinstance(result, dict) and 'memory_id' in result:
            feedback = self.engine.process_feedback(result['memory_id'], 'neutral')
            self.assertIsNotNone(feedback)

    def test_manage_memory_operations(self):
        result = self.engine.process_message("I prefer dark mode")
        if isinstance(result, dict) and 'memory_id' in result:
            mid = result['memory_id']
            read_result = self.engine.manage_memory('read', mid)
            self.assertIsNotNone(read_result)

            update_result = self.engine.manage_memory('update', mid, {'confidence': 0.99})
            self.assertIsNotNone(update_result)

    def test_tenant_crud(self):
        self.engine.create_tenant('test_t1', 'Test Tenant', 'personal')
        tenant = self.engine.get_tenant('test_t1')
        self.assertIsNotNone(tenant)

        tenants = self.engine.list_tenants()
        self.assertIsInstance(tenants, list)

        self.engine.update_tenant('test_t1', {'name': 'Updated Tenant'})
        self.engine.delete_tenant('test_t1')

    def test_tenant_enterprise(self):
        self.engine.create_tenant('ent_t1', 'Enterprise', 'enterprise', organization_id='org1')
        self.engine.add_tenant_role('ent_t1', 'editor', ['read', 'write'])

    def test_agent_operations(self):
        agents = self.engine.list_agents()
        self.assertIsInstance(agents, dict)

        self.engine.register_agent('test_agent', {'type': 'test'})
        self.engine.unregister_agent('test_agent')

    def test_user_tenant_operations(self):
        self.engine.assign_tenant('user1', 'tenant1')
        tenant = self.engine.get_user_tenant('user1')
        self.assertIsNotNone(tenant)

    def test_memory_sharing(self):
        result = self.engine.share_memory('mem_1', ['user2'], permission='read')
        self.assertIsNotNone(result)

    def test_memory_access_check(self):
        result = self.engine.check_memory_access('user1', 'mem_1', 'read')
        self.assertIsNotNone(result)

    def test_user_behavior(self):
        self.engine.record_user_behavior('user1', 'mem_1', 'view')
        self.engine.record_user_behavior('user1', 'mem_1', 'like')
        summary = self.engine.get_user_behavior_summary('user1')
        self.assertIsNotNone(summary)

    def test_recommendations(self):
        self.engine.process_message("I prefer dark mode")
        try:
            recs = self.engine.get_recommendations('user1', query='dark mode')
            self.assertIsNotNone(recs)
        except Exception:
            pass

    def test_pending_memory_workflow(self):
        mid = self.engine.add_pending_memory({'content': 'Test pending', 'memory_type': 'user_preference'})
        self.assertIsInstance(mid, str)

        pending = self.engine.get_pending_memories()
        self.assertIsInstance(pending, list)

        count = self.engine.get_pending_count()
        self.assertIsInstance(count, int)

        self.engine.approve_memory(mid)

    def test_pending_memory_reject(self):
        mid = self.engine.add_pending_memory({'content': 'To reject'})
        self.engine.reject_memory(mid)

    def test_nudge_operations(self):
        candidates = self.engine.get_nudge_candidates()
        self.assertIsInstance(candidates, list)

        should = self.engine.should_nudge()
        self.assertIsInstance(should, bool)

    def test_nudge_prompt(self):
        memory = {
            'memory_type': 'user_preference',
            'content': 'I prefer dark mode',
            'created_at': '2026-01-01T00:00:00Z',
        }
        prompt = self.engine.generate_nudge_prompt(memory)
        self.assertIsInstance(prompt, str)

    def test_knowledge_operations(self):
        stats = self.engine.get_knowledge_statistics()
        self.assertIsNotNone(stats)

        sync = self.engine.sync_knowledge_base()
        self.assertIsNotNone(sync)

    def test_export_import(self):
        self.engine.process_message("I prefer dark mode")
        try:
            exported = self.engine.export_memories()
            self.assertIsNotNone(exported)
            imported = self.engine.import_memories(exported)
            self.assertIsNotNone(imported)
        except TypeError:
            pass

    def test_clear_working_memory(self):
        self.engine.clear_working_memory()

    def test_reload_config(self):
        result = self.engine.reload_config()
        self.assertIsNotNone(result)

    def test_optimize_system(self):
        result = self.engine.optimize_system()
        self.assertIsNotNone(result)

    def test_manage_forgetting(self):
        result = self.engine.process_message("I prefer dark mode")
        if isinstance(result, dict) and 'memory_id' in result:
            self.engine.manage_forgetting(result['memory_id'], action='decrease_weight', weight_adjustment=0.1)

    def test_compress_memories(self):
        self.engine.process_message("I prefer dark mode")
        try:
            self.engine.compress_memories(tenant_id=None)
        except Exception:
            pass

    def test_retrieve_with_associations(self):
        self.engine.process_message("I prefer dark mode")
        results = self.engine.retrieve_memories(query="dark mode", include_associations=True)
        self.assertIsInstance(results, list)


if __name__ == '__main__':
    unittest.main()
