import unittest
import os
import sys
import tempfile
import shutil
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.utils.security import SecurityManager, AuthorizationManager
from memory_classification_engine.utils.tenant import Tenant, PersonalTenant, EnterpriseTenant, TenantManager
from memory_classification_engine.utils.distributed import DistributedManager, DataSynchronizer
from memory_classification_engine.utils.recommendation import RecommendationSystem
from memory_classification_engine.utils.performance import PerformanceMonitor, PerformanceOptimizer
from memory_classification_engine.utils.helpers import (
    generate_memory_id, get_current_time, extract_content,
    calculate_memory_weight, format_memory, load_json_file, save_json_file,
    MEMORY_TYPES, MEMORY_TIERS
)
from memory_classification_engine.utils.constants import (
    DEFAULT_CACHE_TTL, DEFAULT_CACHE_SIZE, DEFAULT_CONFIDENCE,
    DEFAULT_MIN_WEIGHT, ENGINE_VERSION, DEFAULT_DATA_PATH,
    DEFAULT_RELEVANCE_WEIGHT, DEFAULT_DIVERSITY_WEIGHT, DEFAULT_NOVELTY_WEIGHT
)


class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.manager = SecurityManager(secret_key='test_secret_key_for_testing')

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.algorithm, 'HS256')

    def test_generate_and_verify_token(self):
        token = self.manager.generate_token('user1', 'user')
        self.assertIsInstance(token, str)
        payload = self.manager.verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['sub'], 'user1')
        self.assertEqual(payload['role'], 'user')

    def test_verify_invalid_token(self):
        result = self.manager.verify_token('invalid_token_string')
        self.assertIsNone(result)

    def test_hash_and_verify_password(self):
        password = 'my_secure_password_123'
        hashed = self.manager.hash_password(password)
        self.assertIsInstance(hashed, str)
        self.assertIn(':', hashed)
        self.assertTrue(self.manager.verify_password(password, hashed))

    def test_verify_wrong_password(self):
        hashed = self.manager.hash_password('correct_password')
        self.assertFalse(self.manager.verify_password('wrong_password', hashed))

    def test_generate_api_key(self):
        key = self.manager.generate_api_key()
        self.assertIsInstance(key, str)
        self.assertGreater(len(key), 10)

    def test_validate_api_key(self):
        valid_keys = ['key1', 'key2', 'key3']
        self.assertTrue(self.manager.validate_api_key('key1', valid_keys))
        self.assertFalse(self.manager.validate_api_key('key4', valid_keys))

    def test_sanitize_input(self):
        result = self.manager.sanitize_input("test'input\"value")
        self.assertIsInstance(result, str)
        self.assertIn("\\'", result)

    def test_validate_input(self):
        self.assertTrue(self.manager.validate_input('valid input'))
        self.assertFalse(self.manager.validate_input(''))
        self.assertFalse(self.manager.validate_input('x' * 1001))
        self.assertTrue(self.manager.validate_input('short', max_length=10))


class TestAuthorizationManager(unittest.TestCase):
    def setUp(self):
        self.manager = AuthorizationManager()

    def test_init(self):
        self.assertIsNotNone(self.manager)
        self.assertIn('admin', self.manager.permissions)
        self.assertIn('user', self.manager.permissions)
        self.assertIn('guest', self.manager.permissions)

    def test_has_permission(self):
        self.assertTrue(self.manager.has_permission('admin', 'read'))
        self.assertTrue(self.manager.has_permission('admin', 'write'))
        self.assertTrue(self.manager.has_permission('admin', 'delete'))
        self.assertTrue(self.manager.has_permission('user', 'read'))
        self.assertTrue(self.manager.has_permission('user', 'write'))
        self.assertFalse(self.manager.has_permission('user', 'delete'))
        self.assertTrue(self.manager.has_permission('guest', 'read'))
        self.assertFalse(self.manager.has_permission('guest', 'write'))

    def test_has_permission_unknown_role(self):
        self.assertFalse(self.manager.has_permission('unknown_role', 'read'))

    def test_get_permissions(self):
        admin_perms = self.manager.get_permissions('admin')
        self.assertIsInstance(admin_perms, list)
        self.assertIn('read', admin_perms)
        self.assertIn('write', admin_perms)
        self.assertIn('delete', admin_perms)

    def test_get_permissions_unknown_role(self):
        perms = self.manager.get_permissions('unknown')
        self.assertEqual(perms, [])

    def test_add_role(self):
        self.manager.add_role('moderator', ['read', 'write', 'moderate'])
        self.assertTrue(self.manager.has_permission('moderator', 'moderate'))
        self.assertFalse(self.manager.has_permission('moderator', 'delete'))

    def test_update_role(self):
        self.manager.update_role('guest', ['read', 'write'])
        self.assertTrue(self.manager.has_permission('guest', 'write'))

    def test_remove_role(self):
        self.manager.add_role('temp_role', ['read'])
        self.manager.remove_role('temp_role')
        self.assertFalse(self.manager.has_permission('temp_role', 'read'))


class TestTenant(unittest.TestCase):
    def test_tenant_init(self):
        tenant = Tenant('t1', 'Test Tenant', 'personal')
        self.assertEqual(tenant.tenant_id, 't1')
        self.assertEqual(tenant.name, 'Test Tenant')
        self.assertEqual(tenant.tenant_type, 'personal')
        self.assertIsInstance(tenant.memories, list)

    def test_tenant_add_memory(self):
        tenant = Tenant('t1', 'Test', 'personal')
        memory = {'content': 'Test memory'}
        tenant.add_memory(memory)
        self.assertEqual(len(tenant.memories), 1)
        self.assertEqual(tenant.memories[0]['tenant_id'], 't1')

    def test_tenant_get_memories(self):
        tenant = Tenant('t1', 'Test', 'personal')
        tenant.add_memory({'content': 'Memory 1'})
        tenant.add_memory({'content': 'Memory 2'})
        memories = tenant.get_memories()
        self.assertEqual(len(memories), 2)

    def test_tenant_update(self):
        tenant = Tenant('t1', 'Old Name', 'personal')
        tenant.update({'name': 'New Name'})
        self.assertEqual(tenant.name, 'New Name')


class TestPersonalTenant(unittest.TestCase):
    def test_init(self):
        tenant = PersonalTenant('p1', 'Personal', 'user1')
        self.assertEqual(tenant.tenant_type, 'personal')
        self.assertEqual(tenant.user_id, 'user1')
        self.assertEqual(tenant.decay_factor, 0.9)

    def test_decay_memories(self):
        tenant = PersonalTenant('p1', 'Personal', 'user1')
        tenant.memories = [
            {'content': 'Old', 'weight': 1.0, 'last_accessed': '2020-01-01T00:00:00Z'},
        ]
        tenant.decay_memories()
        self.assertLessEqual(tenant.memories[0]['weight'], 1.0)


class TestEnterpriseTenant(unittest.TestCase):
    def test_init(self):
        tenant = EnterpriseTenant('e1', 'Enterprise', 'org1')
        self.assertEqual(tenant.tenant_type, 'enterprise')
        self.assertEqual(tenant.organization_id, 'org1')
        self.assertIsInstance(tenant.roles, dict)

    def test_add_role(self):
        tenant = EnterpriseTenant('e1', 'Enterprise', 'org1')
        tenant.add_role('editor', ['read', 'write'])
        self.assertIn('editor', tenant.roles)

    def test_has_permission(self):
        tenant = EnterpriseTenant('e1', 'Enterprise', 'org1')
        tenant.add_role('editor', ['read', 'write'])
        self.assertTrue(tenant.has_permission('editor', 'read'))
        self.assertFalse(tenant.has_permission('editor', 'delete'))
        self.assertFalse(tenant.has_permission('unknown_role', 'read'))


class TestTenantManager(unittest.TestCase):
    def setUp(self):
        self.manager = TenantManager()

    def test_create_personal_tenant(self):
        tenant = self.manager.create_tenant('p1', 'Personal', 'personal', user_id='user1')
        self.assertIsNotNone(tenant)
        self.assertIsInstance(tenant, PersonalTenant)
        self.assertEqual(tenant.tenant_id, 'p1')

    def test_create_enterprise_tenant(self):
        tenant = self.manager.create_tenant('e1', 'Enterprise', 'enterprise', organization_id='org1')
        self.assertIsNotNone(tenant)
        self.assertIsInstance(tenant, EnterpriseTenant)

    def test_create_tenant_duplicate(self):
        self.manager.create_tenant('t1', 'Test', 'personal')
        tenant = self.manager.create_tenant('t1', 'Test2', 'personal')
        self.assertEqual(tenant.name, 'Test')

    def test_create_tenant_invalid_type(self):
        tenant = self.manager.create_tenant('t1', 'Test', 'invalid_type')
        self.assertIsNone(tenant)

    def test_get_tenant(self):
        self.manager.create_tenant('t1', 'Test', 'personal')
        tenant = self.manager.get_tenant('t1')
        self.assertIsNotNone(tenant)
        self.assertEqual(tenant.name, 'Test')

    def test_get_tenant_not_found(self):
        self.assertIsNone(self.manager.get_tenant('nonexistent'))

    def test_list_tenants(self):
        self.manager.create_tenant('t1', 'Tenant 1', 'personal')
        self.manager.create_tenant('t2', 'Tenant 2', 'enterprise', organization_id='org1')
        tenants = self.manager.list_tenants()
        self.assertEqual(len(tenants), 2)

    def test_delete_tenant(self):
        self.manager.create_tenant('t1', 'Test', 'personal')
        result = self.manager.delete_tenant('t1')
        self.assertTrue(result)
        self.assertIsNone(self.manager.get_tenant('t1'))

    def test_delete_tenant_not_found(self):
        result = self.manager.delete_tenant('nonexistent')
        self.assertFalse(result)

    def test_update_tenant(self):
        self.manager.create_tenant('t1', 'Old', 'personal')
        updated = self.manager.update_tenant('t1', {'name': 'New'})
        self.assertEqual(updated.name, 'New')

    def test_update_tenant_not_found(self):
        result = self.manager.update_tenant('nonexistent', {'name': 'New'})
        self.assertIsNone(result)


class TestDataSynchronizer(unittest.TestCase):
    def test_sync_data(self):
        source = {'key1': 'value1', 'key2': 'value2'}
        target = {'key3': 'value3'}
        result = DataSynchronizer.sync_data(source, target)
        self.assertIn('key1', result)
        self.assertIn('key2', result)
        self.assertIn('key3', result)

    def test_sync_data_nested(self):
        source = {'nested': {'a': 1, 'b': 2}}
        target = {'nested': {'a': 0, 'c': 3}}
        result = DataSynchronizer.sync_data(source, target)
        self.assertEqual(result['nested']['a'], 1)
        self.assertIn('c', result['nested'])

    def test_sync_data_list_merge(self):
        source = {'items': [1, 2, 3]}
        target = {'items': [3, 4, 5]}
        result = DataSynchronizer.sync_data(source, target)
        self.assertIn(1, result['items'])
        self.assertIn(3, result['items'])

    def test_calculate_hash(self):
        data = {'key': 'value'}
        hash1 = DataSynchronizer.calculate_hash(data)
        hash2 = DataSynchronizer.calculate_hash(data)
        self.assertEqual(hash1, hash2)

    def test_calculate_hash_different_data(self):
        hash1 = DataSynchronizer.calculate_hash({'a': 1})
        hash2 = DataSynchronizer.calculate_hash({'a': 2})
        self.assertNotEqual(hash1, hash2)

    def test_detect_changes(self):
        old_data = {'a': 1, 'b': 2}
        new_data = {'a': 1, 'b': 3, 'c': 4}
        changes = DataSynchronizer.detect_changes(old_data, new_data)
        self.assertIsInstance(changes, list)
        self.assertGreater(len(changes), 0)

    def test_incremental_sync(self):
        source = {'a': 1, 'b': 2}
        target = {'a': 0}
        merged, changes = DataSynchronizer.incremental_sync(source, target)
        self.assertIn('a', merged)
        self.assertIn('b', merged)
        self.assertIsInstance(changes, list)

    def test_resolve_conflicts_latest(self):
        conflicts = [
            {'path': 'a', 'old_value': 1, 'new_value': 2, 'value': 2},
        ]
        resolved = DataSynchronizer.resolve_conflicts(conflicts, 'latest')
        self.assertEqual(resolved['a'], 2)

    def test_resolve_conflicts_earliest(self):
        conflicts = [
            {'path': 'a', 'old_value': 1, 'new_value': 2, 'value': 2},
        ]
        resolved = DataSynchronizer.resolve_conflicts(conflicts, 'earliest')
        self.assertEqual(resolved['a'], 1)

    def test_calculate_merkle_tree(self):
        data = {'a': 1, 'b': {'c': 2, 'd': 3}}
        tree = DataSynchronizer.calculate_merkle_tree(data)
        self.assertIsInstance(tree, dict)
        self.assertIn('a', tree)
        self.assertIn('b.c', tree)
        self.assertIn('b.d', tree)

    def test_find_differences(self):
        tree1 = {'a': 'hash1', 'b': 'hash2', 'c': 'hash3'}
        tree2 = {'a': 'hash1', 'b': 'different', 'c': 'hash3'}
        diffs = DataSynchronizer.find_differences(tree1, tree2)
        self.assertIn('b', diffs)
        self.assertNotIn('a', diffs)


class TestDistributedManager(unittest.TestCase):
    def test_init(self):
        manager = DistributedManager(node_id='test_node', port=0)
        self.assertIsNotNone(manager)
        self.assertEqual(manager.node_id, 'test_node')
        self.assertEqual(manager.state, 'leader')

    def test_get_nodes(self):
        manager = DistributedManager(node_id='test_node', port=0)
        nodes = manager.get_nodes()
        self.assertIsInstance(nodes, dict)
        self.assertIn('test_node', nodes)

    def test_get_node_count(self):
        manager = DistributedManager(node_id='test_node', port=0)
        count = manager.get_node_count()
        self.assertEqual(count, 1)

    def test_is_leader(self):
        manager = DistributedManager(node_id='test_node', port=0)
        self.assertTrue(manager.is_leader())

    def test_get_leader(self):
        manager = DistributedManager(node_id='test_node', port=0)
        leader = manager.get_leader()
        self.assertEqual(leader, 'test_node')

    def test_update_node_metrics(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.update_node_metrics({'cpu_usage': 50.0, 'memory_usage': 60.0})
        metrics = manager.get_node_metrics('test_node')
        self.assertEqual(metrics['cpu_usage'], 50.0)
        self.assertEqual(metrics['memory_usage'], 60.0)

    def test_get_node_metrics_all(self):
        manager = DistributedManager(node_id='test_node', port=0)
        metrics = manager.get_node_metrics()
        self.assertIsInstance(metrics, dict)

    def test_get_node_health_healthy(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.update_node_metrics({'cpu_usage': 30.0, 'memory_usage': 40.0})
        health = manager.get_node_health('test_node')
        self.assertEqual(health, 'healthy')

    def test_get_node_health_warning(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.update_node_metrics({'cpu_usage': 65.0, 'memory_usage': 40.0})
        health = manager.get_node_health('test_node')
        self.assertEqual(health, 'warning')

    def test_get_node_health_critical(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.update_node_metrics({'cpu_usage': 85.0, 'memory_usage': 90.0})
        health = manager.get_node_health('test_node')
        self.assertEqual(health, 'critical')

    def test_get_cluster_status(self):
        manager = DistributedManager(node_id='test_node', port=0)
        status = manager.get_cluster_status()
        self.assertIsInstance(status, dict)
        self.assertIn('cluster_size', status)
        self.assertIn('nodes', status)

    def test_get_raft_status(self):
        manager = DistributedManager(node_id='test_node', port=0)
        raft = manager.get_raft_status()
        self.assertIsInstance(raft, dict)
        self.assertIn('current_term', raft)
        self.assertIn('state', raft)

    def test_compress_decompress_message(self):
        manager = DistributedManager(node_id='test_node', port=0)
        message = {'type': 'test', 'data': 'Hello World'}
        compressed = manager._compress_message(message)
        self.assertIsInstance(compressed, bytes)
        decompressed = manager._decompress_message(compressed)
        self.assertEqual(decompressed['type'], 'test')

    def test_add_sync_item(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.add_sync_item({'type': 'sync', 'data': 'test'})
        self.assertFalse(manager.sync_queue.empty())

    def test_recover_node(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.failed_nodes.add('failed_node')
        manager.recover_node('failed_node')
        self.assertNotIn('failed_node', manager.failed_nodes)

    def test_get_failed_nodes(self):
        manager = DistributedManager(node_id='test_node', port=0)
        failed = manager.get_failed_nodes()
        self.assertIsInstance(failed, set)

    def test_is_node_failed(self):
        manager = DistributedManager(node_id='test_node', port=0)
        manager.failed_nodes.add('failed_node')
        self.assertTrue(manager.is_node_failed('failed_node'))
        self.assertFalse(manager.is_node_failed('healthy_node'))

    def test_generate_cluster_report(self):
        manager = DistributedManager(node_id='test_node', port=0)
        report = manager.generate_cluster_report()
        self.assertIsInstance(report, str)
        self.assertIn('Cluster Report', report)


class TestRecommendationSystem(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.system = RecommendationSystem(storage_path=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.system)
        self.assertEqual(self.system.relevance_weight, 0.4)
        self.assertEqual(self.system.diversity_weight, 0.3)
        self.assertEqual(self.system.novelty_weight, 0.3)

    def test_record_user_behavior(self):
        self.system.record_user_behavior('user1', 'mem_1', 'view')
        self.assertIn('user1', self.system.user_behavior['users'])

    def test_record_user_behavior_multiple(self):
        self.system.record_user_behavior('user1', 'mem_1', 'view')
        self.system.record_user_behavior('user1', 'mem_1', 'like')
        self.system.record_user_behavior('user1', 'mem_2', 'interact')
        prefs = self.system.get_user_preferences('user1')
        self.assertIsInstance(prefs, dict)
        self.assertIn('mem_1', prefs)
        self.assertIn('mem_2', prefs)

    def test_get_user_preferences_empty(self):
        prefs = self.system.get_user_preferences('unknown_user')
        self.assertEqual(prefs, {})

    def test_calculate_relevance_score(self):
        self.system.record_user_behavior('user1', 'mem_1', 'like')
        memory = {'id': 'mem_1', 'content': 'Test content', 'confidence': 0.9}
        score = self.system.calculate_relevance_score(memory, 'user1')
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1.0)

    def test_calculate_diversity_score_empty(self):
        memory = {'content': 'Test content'}
        score = self.system.calculate_diversity_score(memory, [])
        self.assertEqual(score, 1.0)

    def test_calculate_novelty_score(self):
        memory = {'id': 'mem_new', 'created_at': '2026-04-15T00:00:00Z'}
        score = self.system.calculate_novelty_score(memory, 'user1')
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1.0)

    def test_generate_recommendations_empty(self):
        result = self.system.generate_recommendations('user1', all_memories=None)
        self.assertEqual(result, [])

    def test_generate_recommendations(self):
        self.system.record_user_behavior('user1', 'mem_1', 'like')
        memories = [
            {'id': 'mem_1', 'content': 'Known content', 'confidence': 0.9},
            {'id': 'mem_2', 'content': 'New content', 'confidence': 0.8},
        ]
        result = self.system.generate_recommendations('user1', limit=2, all_memories=memories)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 2)

    def test_get_user_behavior_summary(self):
        self.system.record_user_behavior('user1', 'mem_1', 'view')
        summary = self.system.get_user_behavior_summary('user1')
        self.assertIsInstance(summary, dict)
        self.assertIn('total_interactions', summary)

    def test_get_user_behavior_summary_unknown(self):
        summary = self.system.get_user_behavior_summary('unknown')
        self.assertEqual(summary['total_interactions'], 0)


class TestPerformanceMonitor(unittest.TestCase):
    def test_init(self):
        monitor = PerformanceMonitor(enabled=False)
        self.assertIsNotNone(monitor)
        self.assertFalse(monitor.enabled)

    def test_init_with_thresholds(self):
        thresholds = {'memory': 90, 'cpu': 95, 'disk': 95}
        monitor = PerformanceMonitor(enabled=False, alert_thresholds=thresholds)
        self.assertEqual(monitor.alert_thresholds['memory'], 90)

    def test_record_response_time(self):
        monitor = PerformanceMonitor(enabled=True)
        monitor.record_response_time('process_message', 0.5)
        monitor.record_response_time('process_message', 0.3)
        self.assertEqual(len(monitor.metrics['response_times']['process_message']), 2)

    def test_record_response_time_disabled(self):
        monitor = PerformanceMonitor(enabled=False)
        monitor.record_response_time('test', 0.5)
        self.assertNotIn('test', monitor.metrics['response_times'])

    def test_increment_throughput(self):
        monitor = PerformanceMonitor(enabled=True)
        monitor.increment_throughput('messages_processed')
        self.assertEqual(monitor.metrics['throughput']['messages_processed'], 1)

    def test_record_cache_metrics(self):
        monitor = PerformanceMonitor(enabled=True)
        cache_stats = {
            'hit_count': 100,
            'miss_count': 20,
            'hit_rate': 83.3,
            'size': 500,
            'expired_count': 5
        }
        monitor.record_cache_metrics(cache_stats)
        self.assertEqual(monitor.metrics['cache']['hit_count'], 100)
        self.assertEqual(monitor.metrics['cache']['hit_rate'], 83.3)

    def test_record_storage_operation(self):
        monitor = PerformanceMonitor(enabled=True)
        monitor.record_storage_operation('read', 0.01)
        monitor.record_storage_operation('write', 0.02)
        self.assertEqual(monitor.metrics['storage']['read_operations'], 1)
        self.assertEqual(monitor.metrics['storage']['write_operations'], 1)

    def test_get_metrics(self):
        monitor = PerformanceMonitor(enabled=False)
        metrics = monitor.get_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn('memory', metrics)
        self.assertIn('cpu', metrics)

    def test_get_summary(self):
        monitor = PerformanceMonitor(enabled=False)
        summary = monitor.get_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('memory', summary)
        self.assertIn('cpu', summary)
        self.assertIn('alerts', summary)

    def test_export_metrics(self):
        test_dir = tempfile.mkdtemp()
        try:
            monitor = PerformanceMonitor(enabled=True)
            file_path = os.path.join(test_dir, 'metrics.json')
            monitor.export_metrics(file_path)
            self.assertTrue(os.path.exists(file_path))
        finally:
            monitor.stop()
            shutil.rmtree(test_dir, ignore_errors=True)


class TestPerformanceOptimizer(unittest.TestCase):
    def test_optimize_query(self):
        query = "the quick brown fox jumps over the lazy dog"
        optimized = PerformanceOptimizer.optimize_query(query)
        self.assertIsInstance(optimized, str)
        self.assertNotIn('the', optimized.split())

    def test_optimize_query_preserves_meaningful(self):
        query = "memory classification engine"
        optimized = PerformanceOptimizer.optimize_query(query)
        self.assertIn('memory', optimized)
        self.assertIn('classification', optimized)

    def test_optimize_query_all_stop_words(self):
        query = "the a an"
        optimized = PerformanceOptimizer.optimize_query(query)
        self.assertEqual(optimized, query)

    def test_batch_process(self):
        def process_batch(items):
            return [item * 2 for item in items]
        items = list(range(10))
        results = PerformanceOptimizer.batch_process(process_batch, items, batch_size=3)
        self.assertEqual(results, [0, 2, 4, 6, 8, 10, 12, 14, 16, 18])

    def test_memory_efficient_iteration(self):
        items = list(range(10))
        batches = list(PerformanceOptimizer.memory_efficient_iteration(items, batch_size=3))
        self.assertEqual(len(batches), 4)
        self.assertEqual(len(batches[0]), 3)
        self.assertEqual(len(batches[-1]), 1)

    def test_cache_key_generator(self):
        key = PerformanceOptimizer.cache_key_generator('test', user='user1', query='search')
        self.assertIsInstance(key, str)
        self.assertTrue(key.startswith('test'))

    def test_cache_key_generator_deterministic(self):
        key1 = PerformanceOptimizer.cache_key_generator('test', a=1, b=2)
        key2 = PerformanceOptimizer.cache_key_generator('test', a=1, b=2)
        self.assertEqual(key1, key2)


class TestHelpers(unittest.TestCase):
    def test_generate_memory_id(self):
        mid = generate_memory_id()
        self.assertIsInstance(mid, str)
        self.assertTrue(mid.startswith('mem_'))

    def test_generate_memory_id_unique(self):
        id1 = generate_memory_id()
        time.sleep(0.01)
        id2 = generate_memory_id()
        self.assertNotEqual(id1, id2)

    def test_get_current_time(self):
        t = get_current_time()
        self.assertIsInstance(t, str)
        self.assertIn('T', t)
        self.assertTrue(t.endswith('Z'))

    def test_extract_content_extract(self):
        text = "Hello World"
        result = extract_content(text, r"Hello", "extract")
        self.assertEqual(result, "Hello")

    def test_extract_content_no_match(self):
        result = extract_content("Hello World", r"xyz", "extract")
        self.assertIsNone(result)

    def test_extract_content_following(self):
        text = "Name: John Smith lives here"
        result = extract_content(text, r"Name:", "extract_following_content")
        self.assertIsNotNone(result)
        self.assertIn("John", result)

    def test_extract_content_surrounding(self):
        text = "This is a long text with some content around a keyword and more text"
        result = extract_content(text, r"keyword", "extract_surrounding_context")
        self.assertIsNotNone(result)
        self.assertIn("keyword", result)

    def test_calculate_memory_weight(self):
        weight = calculate_memory_weight(0.9, 0, 10)
        self.assertIsInstance(weight, float)
        self.assertGreater(weight, 0)

    def test_calculate_memory_weight_decay(self):
        recent = calculate_memory_weight(0.9, 1, 5)
        old = calculate_memory_weight(0.9, 100, 5)
        self.assertGreater(recent, old)

    def test_calculate_memory_weight_frequency(self):
        frequent = calculate_memory_weight(0.9, 1, 100)
        rare = calculate_memory_weight(0.9, 1, 1)
        self.assertGreater(frequent, rare)

    def test_format_memory(self):
        memory = {'type': 'user_preference', 'tier': 2, 'content': 'Test', 'confidence': 0.9}
        formatted = format_memory(memory)
        self.assertIsInstance(formatted, str)
        self.assertIn('Test', formatted)

    def test_load_json_file(self):
        test_dir = tempfile.mkdtemp()
        try:
            file_path = os.path.join(test_dir, 'test.json')
            data = {'key': 'value'}
            with open(file_path, 'w') as f:
                json.dump(data, f)
            loaded = load_json_file(file_path)
            self.assertEqual(loaded['key'], 'value')
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_load_json_file_not_found(self):
        result = load_json_file('/nonexistent/path.json')
        self.assertEqual(result, {})

    def test_save_json_file(self):
        test_dir = tempfile.mkdtemp()
        try:
            file_path = os.path.join(test_dir, 'test.json')
            data = {'key': 'value', 'number': 42}
            save_json_file(file_path, data)
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, 'r') as f:
                loaded = json.load(f)
            self.assertEqual(loaded['key'], 'value')
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_memory_types(self):
        self.assertIsInstance(MEMORY_TYPES, dict)
        self.assertIn('user_preference', MEMORY_TYPES)
        self.assertIn('correction', MEMORY_TYPES)
        self.assertIn('fact_declaration', MEMORY_TYPES)

    def test_memory_tiers(self):
        self.assertIsInstance(MEMORY_TIERS, dict)
        self.assertIn(1, MEMORY_TIERS)
        self.assertIn(2, MEMORY_TIERS)
        self.assertIn(3, MEMORY_TIERS)
        self.assertIn(4, MEMORY_TIERS)


class TestConstants(unittest.TestCase):
    def test_cache_constants(self):
        self.assertEqual(DEFAULT_CACHE_TTL, 3600)
        self.assertEqual(DEFAULT_CACHE_SIZE, 1000)

    def test_confidence_constants(self):
        self.assertEqual(DEFAULT_CONFIDENCE, 1.0)
        self.assertEqual(DEFAULT_MIN_WEIGHT, 0.1)

    def test_engine_version(self):
        self.assertIsInstance(ENGINE_VERSION, str)
        self.assertRegex(ENGINE_VERSION, r'\d+\.\d+\.\d+')

    def test_data_path(self):
        self.assertIsInstance(DEFAULT_DATA_PATH, str)
        self.assertGreater(len(DEFAULT_DATA_PATH), 0)

    def test_weight_constants(self):
        self.assertEqual(DEFAULT_RELEVANCE_WEIGHT, 0.4)
        self.assertEqual(DEFAULT_DIVERSITY_WEIGHT, 0.3)
        self.assertEqual(DEFAULT_NOVELTY_WEIGHT, 0.3)
        self.assertAlmostEqual(DEFAULT_RELEVANCE_WEIGHT + DEFAULT_DIVERSITY_WEIGHT + DEFAULT_NOVELTY_WEIGHT, 1.0)


if __name__ == '__main__':
    unittest.main()
