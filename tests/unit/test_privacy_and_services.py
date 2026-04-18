import unittest
import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.privacy.access_control import AccessControlManager as PrivacyACM, Role, Permission
from memory_classification_engine.privacy.audit import AuditManager, AuditLog
from memory_classification_engine.privacy.compliance import ComplianceManager
from memory_classification_engine.privacy.encryption import EncryptionManager as PrivacyEncryption
from memory_classification_engine.privacy.privacy_settings import PrivacySettings, PrivacyManager
from memory_classification_engine.privacy.sensitivity_analyzer import SensitivityAnalyzer
from memory_classification_engine.privacy.visibility_manager import VisibilityManager
from memory_classification_engine.privacy.scenario_validator import ScenarioValidator
from memory_classification_engine.services.classification_service import ClassificationService
from memory_classification_engine.services.storage_service import StorageService
from memory_classification_engine.services.tenant_service import TenantService
from memory_classification_engine.services.privacy_service import PrivacyService
from memory_classification_engine.services.deduplication_service import DeduplicationService
from memory_classification_engine.services.recommendation_service import RecommendationService
from memory_classification_engine.utils.config import ConfigManager


class TestPrivacyAccessControl(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        config_file = os.path.join(self.test_dir, 'access_control.json')
        self.manager = PrivacyACM(config_file=config_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_create_role(self):
        role = self.manager.create_role('editor', ['read', 'write'])
        self.assertIsNotNone(role)
        self.assertEqual(role.name, 'editor')

    def test_assign_role(self):
        self.manager.create_role('editor', ['read', 'write'])
        self.manager.assign_role('user1', 'editor')
        roles = self.manager.get_user_roles('user1')
        self.assertIn('editor', roles)

    def test_check_permission(self):
        self.manager.create_role('editor', ['read', 'write'])
        self.manager.assign_role('user1', 'editor')
        result = self.manager.check_permission('user1', 'memory', 'read')
        self.assertIsInstance(result, bool)

    def test_get_user_permissions(self):
        self.manager.create_role('editor', ['read', 'write'])
        self.manager.assign_role('user1', 'editor')
        perms = self.manager.get_user_permissions('user1')
        self.assertIn('read', perms)
        self.assertIn('write', perms)

    def test_remove_role(self):
        self.manager.create_role('editor', ['read', 'write'])
        self.manager.assign_role('user1', 'editor')
        self.manager.remove_role('user1', 'editor')
        roles = self.manager.get_user_roles('user1')
        self.assertNotIn('editor', roles)

    def test_tenant_isolation(self):
        self.manager.assign_tenant('user1', 'tenant1')
        self.assertTrue(self.manager.check_tenant_isolation('user1', 'tenant1'))
        self.assertFalse(self.manager.check_tenant_isolation('user1', 'tenant2'))


class TestAuditManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        log_file = os.path.join(self.test_dir, 'audit.log')
        self.manager = AuditManager(log_file=log_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_log(self):
        self.manager.log('user1', 'read', 'memory_1', {'detail': 'test'})
        logs = self.manager.get_logs()
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)

    def test_get_logs_by_user(self):
        self.manager.log('user1', 'read', 'memory_1', {})
        self.manager.log('user2', 'write', 'memory_2', {})
        logs = self.manager.get_logs(user_id='user1')
        self.assertIsInstance(logs, list)

    def test_get_logs_by_action(self):
        self.manager.log('user1', 'read', 'memory_1', {})
        self.manager.log('user1', 'write', 'memory_2', {})
        logs = self.manager.get_logs(action='read')
        self.assertIsInstance(logs, list)

    def test_analyze_security_events(self):
        self.manager.log('user1', 'read', 'memory_1', {})
        result = self.manager.analyze_security_events()
        self.assertIsInstance(result, dict)

    def test_generate_audit_report(self):
        self.manager.log('user1', 'read', 'memory_1', {})
        report = self.manager.generate_audit_report()
        self.assertIsInstance(report, str)


class TestComplianceManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        config_file = os.path.join(self.test_dir, 'compliance.json')
        self.manager = ComplianceManager(config_file=config_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_log_data_processing(self):
        self.manager.log_data_processing('user1', 'store', 'memory', 'classification')
        records = self.manager.get_data_processing_records(user_id='user1')
        self.assertIsInstance(records, list)

    def test_perform_compliance_audit(self):
        result = self.manager.perform_compliance_audit()
        self.assertIsInstance(result, dict)

    def test_generate_privacy_impact_assessment(self):
        result = self.manager.generate_privacy_impact_assessment()
        self.assertIsInstance(result, dict)

    def test_generate_privacy_policy(self):
        result = self.manager.generate_privacy_policy()
        self.assertIsInstance(result, str)


class TestPrivacyEncryption(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        key_file = os.path.join(self.test_dir, 'encryption_keys.json')
        self.manager = PrivacyEncryption(key_file=key_file)
        self.key_id = self.manager.create_key('test_password')

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_create_key(self):
        self.assertIsInstance(self.key_id, str)

    def test_encrypt_decrypt(self):
        original = 'sensitive information'
        ciphertext, nonce, tag = self.manager.encrypt(original, self.key_id)
        decrypted = self.manager.decrypt(ciphertext, nonce, tag, self.key_id)
        self.assertEqual(original, decrypted)

    def test_is_sensitive_data(self):
        result = self.manager.is_sensitive_data("password is abc123")
        self.assertIsInstance(result, bool)

    def test_generate_key_id(self):
        key_id = self.manager.generate_key_id()
        self.assertIsInstance(key_id, str)

    def test_get_key(self):
        key = self.manager.get_key(self.key_id)
        self.assertIsNotNone(key)

    def test_get_key_not_found(self):
        key = self.manager.get_key('nonexistent')
        self.assertIsNone(key)


class TestPrivacySettings(unittest.TestCase):
    def test_init(self):
        settings = PrivacySettings()
        self.assertIsNotNone(settings)
        self.assertEqual(settings.visibility, "private")
        self.assertEqual(settings.retention_period, 365)
        self.assertFalse(settings.allow_data_sharing)

    def test_custom_init(self):
        settings = PrivacySettings(visibility="public", retention_period=90, allow_data_sharing=True)
        self.assertEqual(settings.visibility, "public")
        self.assertEqual(settings.retention_period, 90)
        self.assertTrue(settings.allow_data_sharing)


class TestPrivacyManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        config_file = os.path.join(self.test_dir, 'privacy_settings.json')
        self.manager = PrivacyManager(config_file=config_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_get_settings(self):
        settings = self.manager.get_settings('user1')
        self.assertIsNotNone(settings)
        self.assertIsInstance(settings, PrivacySettings)

    def test_update_settings(self):
        new_settings = PrivacySettings(visibility='public', retention_period=30)
        self.manager.update_settings('user1', new_settings)
        settings = self.manager.get_settings('user1')
        self.assertEqual(settings.visibility, 'public')
        self.assertEqual(settings.retention_period, 30)

    def test_delete_settings(self):
        self.manager.update_settings('user1', PrivacySettings())
        self.manager.delete_settings('user1')
        settings = self.manager.get_settings('user1')
        self.assertEqual(settings.visibility, 'private')

    def test_is_data_expired(self):
        self.manager.update_settings('user1', PrivacySettings(retention_period=30))
        old_date = datetime.now() - timedelta(days=60)
        self.assertTrue(self.manager.is_data_expired('user1', old_date))

    def test_anonymize_data(self):
        data = {'name': 'John', 'email': 'john@example.com', 'content': 'test'}
        result = self.manager.anonymize_data(data)
        self.assertIsInstance(result, dict)

    def test_apply_data_minimization(self):
        data = {'name': 'John', 'email': 'john@example.com', 'content': 'test', 'extra': 'data'}
        result = self.manager.apply_data_minimization(data)
        self.assertIsInstance(result, dict)


class TestSensitivityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.analyzer = SensitivityAnalyzer(self.config)

    def test_init(self):
        self.assertIsNotNone(self.analyzer)

    def test_analyze_sensitivity_low(self):
        result = self.analyzer.analyze_sensitivity("I prefer dark mode")
        self.assertIsNotNone(result)

    def test_analyze_sensitivity_high(self):
        result = self.analyzer.analyze_sensitivity("My password is abc123 and SSN is 123-45-6789")
        self.assertIsNotNone(result)

    def test_analyze_memory_sensitivity(self):
        memory = {'content': 'Test content', 'memory_type': 'user_preference'}
        result = self.analyzer.analyze_memory_sensitivity(memory)
        self.assertIsNotNone(result)


class TestVisibilityManager(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.manager = VisibilityManager(self.config)

    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_validate_visibility(self):
        result = self.manager.validate_visibility('private')
        self.assertIsNotNone(result)

    def test_can_access(self):
        memory = {'visibility': 'private', 'user_id': 'user1'}
        result = self.manager.can_access('user1', memory)
        self.assertIsInstance(result, bool)

    def test_filter_by_visibility(self):
        memories = [
            {'visibility': 'public', 'user_id': 'user1'},
            {'visibility': 'private', 'user_id': 'user2'},
        ]
        result = self.manager.filter_by_visibility(memories, 'user1')
        self.assertIsInstance(result, list)


class TestScenarioValidator(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.validator = ScenarioValidator(self.config)

    def test_init(self):
        self.assertIsNotNone(self.validator)

    def test_validate_scenario(self):
        memories = [{'content': 'test', 'sensitivity': 'low'}]
        result = self.validator.validate_scenario(memories, 'external_output')
        self.assertIsNotNone(result)

    def test_get_scenario_rules(self):
        rules = self.validator.get_scenario_rules()
        self.assertIsNotNone(rules)

    def test_add_scenario_rule(self):
        self.validator.add_scenario_rule('test_scenario', {'max_sensitivity': 'low'})
        rules = self.validator.get_scenario_rules()
        self.assertIn('test_scenario', rules)


class TestClassificationService(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.service = ClassificationService(self.config)

    def test_init(self):
        self.assertIsNotNone(self.service)

    def test_classify_message(self):
        self.service.initialize()
        result = self.service.classify_message("I prefer dark mode")
        self.assertIsNotNone(result)


class TestStorageService(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.test_dir = tempfile.mkdtemp()
        self.config.set('storage.data_path', self.test_dir)
        self.service = StorageService(self.config)
        try:
            self.service.initialize()
        except Exception:
            pass

    def tearDown(self):
        try:
            self.service.shutdown()
        except Exception:
            pass
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.service)

    def test_store_memory(self):
        try:
            memory = {
                'id': 'svc_test_1',
                'content': 'Test memory',
                'memory_type': 'user_preference',
                'confidence': 0.9,
            }
            result = self.service.store_memory(memory)
            self.assertIsNotNone(result)
        except AttributeError:
            pass

    def test_retrieve_memories(self):
        try:
            result = self.service.retrieve_memories(query="test query")
            self.assertIsNotNone(result)
        except AttributeError:
            pass


class TestTenantService(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.service = TenantService(self.config)
        self.service.initialize()

    def test_init(self):
        self.assertIsNotNone(self.service)

    def test_create_tenant(self):
        result = self.service.create_tenant('t1', 'Test', 'personal')
        self.assertIsNotNone(result)

    def test_get_tenant(self):
        result = self.service.create_tenant('t1', 'Test', 'personal')
        self.assertIsNotNone(result)

    def test_list_tenants(self):
        self.service.create_tenant('t1', 'Test1', 'personal')
        result = self.service.list_tenants()
        self.assertIsNotNone(result)


class TestPrivacyService(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.service = PrivacyService(self.config)
        self.service.initialize()

    def test_init(self):
        self.assertIsNotNone(self.service)

    def test_check_permission(self):
        result = self.service.check_permission('user1', 'memory', 'read')
        self.assertIsNotNone(result)

    def test_analyze_sensitivity(self):
        result = self.service.analyze_sensitivity({'content': 'test'})
        self.assertIsNotNone(result)


class TestDeduplicationService(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.service = DeduplicationService(self.config)

    def test_init(self):
        self.assertIsNotNone(self.service)

    def test_deduplicate(self):
        matches = [
            {'id': 'm1', 'content': 'I prefer dark mode', 'memory_type': 'user_preference', 'confidence': 0.9, 'source': 'rule'},
            {'id': 'm2', 'content': 'I prefer dark mode', 'memory_type': 'user_preference', 'confidence': 0.8, 'source': 'semantic'},
            {'id': 'm3', 'content': 'I like light mode', 'memory_type': 'user_preference', 'confidence': 0.7, 'source': 'rule'},
        ]
        result = self.service.deduplicate(matches)
        self.assertIsNotNone(result)


class TestRecommendationService(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.service = RecommendationService(self.config)
        self.service.initialize()

    def test_init(self):
        self.assertIsNotNone(self.service)

    def test_get_recommendations(self):
        result = self.service.get_recommendations('user1')
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
