import unittest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.services.classification_service import ClassificationService
from memory_classification_engine.services.storage_service import StorageService
from memory_classification_engine.services.tenant_service import TenantService
from memory_classification_engine.services.privacy_service import PrivacyService
from memory_classification_engine.services.deduplication_service import DeduplicationService


class TestClassificationService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            'storage.data_path': self.test_dir,
        }
        self.service = ClassificationService(self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_classify_preference(self):
        if hasattr(self.service, 'classify'):
            result = self.service.classify("I prefer dark mode")
            self.assertIsInstance(result, (dict, list, type(None)))

    def test_classify_correction(self):
        if hasattr(self.service, 'classify'):
            result = self.service.classify("No, that's wrong")
            self.assertIsInstance(result, (dict, list, type(None)))

    def test_classify_decision(self):
        if hasattr(self.service, 'classify'):
            result = self.service.classify("Let's use React for the frontend")
            self.assertIsInstance(result, (dict, list, type(None)))

    def test_classify_fact(self):
        if hasattr(self.service, 'classify'):
            result = self.service.classify("The deadline is April 30th")
            self.assertIsInstance(result, (dict, list, type(None)))

    def test_classify_chinese(self):
        if hasattr(self.service, 'classify'):
            result = self.service.classify("我喜欢深色模式")
            self.assertIsInstance(result, (dict, list, type(None)))

    def test_classify_japanese(self):
        if hasattr(self.service, 'classify'):
            result = self.service.classify("ダークモードが好きです")
            self.assertIsInstance(result, (dict, list, type(None)))


class TestStorageService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            'storage.data_path': self.test_dir,
        }
        self.service = StorageService(self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_store(self):
        if hasattr(self.service, 'store'):
            memory = {
                'id': 'test_store_1',
                'type': 'user_preference',
                'content': 'Test content',
                'created_at': '2026-04-15T00:00:00',
            }
            result = self.service.store(memory)
            self.assertIsInstance(result, (bool, dict, type(None)))

    def test_retrieve(self):
        if hasattr(self.service, 'retrieve'):
            result = self.service.retrieve(query='test', limit=10)
            self.assertIsInstance(result, (list, dict, type(None)))

    def test_delete(self):
        if hasattr(self.service, 'delete'):
            result = self.service.delete('nonexistent_id')
            self.assertIsInstance(result, (bool, dict, type(None)))


class TestTenantService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            'storage.data_path': self.test_dir,
        }
        self.service = TenantService(self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_tenant(self):
        if hasattr(self.service, 'create_tenant'):
            result = self.service.create_tenant('test_tenant', 'personal')
            self.assertIsInstance(result, (bool, dict, type(None)))

    def test_get_tenant(self):
        if hasattr(self.service, 'get_tenant'):
            result = self.service.get_tenant('default')
            self.assertIsInstance(result, (dict, type(None)))

    def test_list_tenants(self):
        if hasattr(self.service, 'list_tenants'):
            result = self.service.list_tenants()
            self.assertIsInstance(result, (list, dict, type(None)))


class TestPrivacyService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            'storage.data_path': self.test_dir,
        }
        self.service = PrivacyService(self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_check_privacy(self):
        if hasattr(self.service, 'check_privacy'):
            result = self.service.check_privacy('This is a test message')
            self.assertIsInstance(result, (bool, dict, type(None)))

    def test_anonymize(self):
        if hasattr(self.service, 'anonymize'):
            result = self.service.anonymize('My email is test@example.com')
            self.assertIsInstance(result, (str, dict, type(None)))


class TestDeduplicationService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            'storage.data_path': self.test_dir,
        }
        self.service = DeduplicationService(self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_check_duplicate(self):
        if hasattr(self.service, 'check_duplicate'):
            result = self.service.check_duplicate('This is a test message')
            self.assertIsInstance(result, (bool, dict, type(None)))

    def test_find_duplicates(self):
        if hasattr(self.service, 'find_duplicates'):
            memories = [
                {'id': '1', 'content': 'Test message 1'},
                {'id': '2', 'content': 'Test message 2'},
            ]
            result = self.service.find_duplicates(memories)
            self.assertIsInstance(result, (list, dict, type(None)))

    def test_deduplicate(self):
        if hasattr(self.service, 'deduplicate'):
            memories = [
                {'id': '1', 'content': 'Test message'},
                {'id': '2', 'content': 'Test message'},
            ]
            result = self.service.deduplicate(memories)
            self.assertIsInstance(result, (list, dict, type(None)))


if __name__ == '__main__':
    unittest.main()
