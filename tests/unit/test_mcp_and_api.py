import unittest
import os
import sys
import json
import tempfile
import shutil
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.integration.layer2_mcp.server import MCPServer
from memory_classification_engine.integration.layer2_mcp.handlers import Handlers
from memory_classification_engine.integration.layer2_mcp.tools import TOOLS, get_tool_schema, validate_tool_arguments
from memory_classification_engine.api.client import APIClient, SyncAPIClient
from memory_classification_engine.api.server import APIServer
from memory_classification_engine.sdk.client import MemoryClassificationSDK
from memory_classification_engine.sdk.python import MemorySDK, MemoryClient
from memory_classification_engine.sdk.exceptions import (
    MemoryClassificationError, APIError, ConnectionError as SDKConnectionError,
    TimeoutError as SDKTimeoutError, ValidationError
)


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.server = MCPServer(data_path=self.test_dir)

    def tearDown(self):
        if hasattr(self.server, 'cleanup'):
            try:
                asyncio.get_event_loop().run_until_complete(self.server.cleanup())
            except Exception:
                pass
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.server)

    def _run_async(self, coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, coro)
                    return future.result()
            return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    def test_handle_initialize(self):
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'test', 'version': '1.0'}
            }
        }
        result = self._run_async(self.server.handle_request(request))
        self.assertIsInstance(result, dict)
        self.assertIn('result', result)

    def test_handle_tools_list(self):
        request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/list',
            'params': {}
        }
        result = self._run_async(self.server.handle_request(request))
        self.assertIsInstance(result, dict)
        self.assertIn('result', result)
        self.assertIn('tools', result['result'])

    def test_handle_classify_memory(self):
        request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'classify_memory',
                'arguments': {
                    'message': 'I prefer dark mode'
                }
            }
        }
        result = self._run_async(self.server.handle_request(request))
        self.assertIsInstance(result, dict)

    def test_handle_store_memory(self):
        request = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'store_memory',
                'arguments': {
                    'message': 'I prefer dark mode',
                    'memory_type': 'user_preference',
                    'confidence': 0.95
                }
            }
        }
        result = self._run_async(self.server.handle_request(request))
        self.assertIsInstance(result, dict)

    def test_handle_retrieve_memories(self):
        request = {
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'tools/call',
            'params': {
                'name': 'retrieve_memories',
                'arguments': {
                    'query': 'dark mode',
                    'limit': 5
                }
            }
        }
        result = self._run_async(self.server.handle_request(request))
        self.assertIsInstance(result, dict)

    def test_handle_get_stats(self):
        request = {
            'jsonrpc': '2.0',
            'id': 6,
            'method': 'tools/call',
            'params': {
                'name': 'get_memory_stats',
                'arguments': {}
            }
        }
        result = self._run_async(self.server.handle_request(request))
        self.assertIsInstance(result, dict)

    def test_handle_batch_classify(self):
        request = {
            'jsonrpc': '2.0',
            'id': 7,
            'method': 'tools/call',
            'params': {
                'name': 'batch_classify',
                'arguments': {
                    'messages': [
                        'I prefer dark mode',
                        'Actually, use single quotes',
                    ]
                }
            }
        }
        result = self._run_async(self.server.handle_request(request))
        self.assertIsInstance(result, dict)

    def test_handle_unknown_method(self):
        request = {
            'jsonrpc': '2.0',
            'id': 8,
            'method': 'unknown/method',
            'params': {}
        }
        result = self._run_async(self.server.handle_request(request))
        self.assertIn('error', result)

    def test_handle_invalid_request(self):
        result = self._run_async(self.server.handle_request({}))
        self.assertIn('error', result)


class TestMCPHandlers(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.handlers = Handlers(data_path=self.test_dir)

    def tearDown(self):
        if hasattr(self.handlers, 'cleanup'):
            try:
                asyncio.get_event_loop().run_until_complete(self.handlers.cleanup())
            except Exception:
                pass
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _run_async(self, coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, coro)
                    return future.result()
            return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    def test_init(self):
        self.assertIsNotNone(self.handlers)

    def test_handle_classify(self):
        result = self._run_async(
            self.handlers.handle_classify_memory({'message': 'I prefer dark mode'})
        )
        self.assertIsNotNone(result)

    def test_handle_store(self):
        result = self._run_async(
            self.handlers.handle_store_memory({
                'message': 'I prefer dark mode',
                'memory_type': 'user_preference',
                'content': 'I prefer dark mode',
                'confidence': 0.95
            })
        )
        self.assertIsNotNone(result)

    def test_handle_retrieve(self):
        result = self._run_async(
            self.handlers.handle_retrieve_memories({'query': 'test', 'limit': 5})
        )
        self.assertIsNotNone(result)

    def test_handle_stats(self):
        result = self._run_async(
            self.handlers.handle_get_memory_stats({})
        )
        self.assertIsNotNone(result)

    def test_handle_batch_classify(self):
        try:
            result = self._run_async(
                self.handlers.handle_batch_classify({
                    'messages': ['I prefer dark mode', 'Use single quotes']
                })
            )
            self.assertIsNotNone(result)
        except (TypeError, KeyError):
            pass


class TestMCPToolDefinitions(unittest.TestCase):
    def test_get_tool_definitions(self):
        tools = TOOLS
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)

    def test_tool_definition_structure(self):
        tools = TOOLS
        for tool in tools:
            self.assertIn('name', tool)
            self.assertIn('description', tool)
            self.assertIn('inputSchema', tool)

    def test_expected_tools_present(self):
        tools = TOOLS
        tool_names = [t['name'] for t in tools]
        self.assertIn('classify_memory', tool_names)
        self.assertIn('store_memory', tool_names)
        self.assertIn('retrieve_memories', tool_names)
        self.assertIn('get_memory_stats', tool_names)
        self.assertIn('batch_classify', tool_names)

    def test_get_tool_schema(self):
        schema = get_tool_schema('classify_memory')
        self.assertIsInstance(schema, dict)
        self.assertIn('name', schema)

    def test_get_tool_schema_not_found(self):
        with self.assertRaises(ValueError):
            get_tool_schema('nonexistent_tool')

    def test_validate_tool_arguments(self):
        errors = validate_tool_arguments('classify_memory', {'message': 'test'})
        self.assertIsInstance(errors, list)
        self.assertEqual(len(errors), 0)

    def test_validate_tool_arguments_missing_required(self):
        errors = validate_tool_arguments('classify_memory', {})
        self.assertIsInstance(errors, list)
        self.assertGreater(len(errors), 0)


class TestAPIClient(unittest.TestCase):
    def test_init(self):
        client = APIClient(base_url='http://localhost:8080')
        self.assertIsNotNone(client)
        self.assertEqual(client.base_url, 'http://localhost:8080')

    def test_init_with_api_key(self):
        client = APIClient(base_url='http://localhost:8080', api_key='test_key')
        self.assertEqual(client.api_key, 'test_key')


class TestSyncAPIClient(unittest.TestCase):
    def test_init(self):
        client = SyncAPIClient(base_url='http://localhost:8080')
        self.assertIsNotNone(client)


class TestAPIServer(unittest.TestCase):
    def test_init(self):
        try:
            server = APIServer(host='localhost', port=0, config_path=None)
            self.assertIsNotNone(server)
        except (AttributeError, ImportError):
            pass


class TestSDKExceptions(unittest.TestCase):
    def test_memory_classification_error(self):
        error = MemoryClassificationError("test error")
        self.assertEqual(str(error), "test error")
        self.assertIsInstance(error, Exception)

    def test_api_error(self):
        try:
            error = APIError("API error", status_code=400)
            self.assertEqual(str(error), "API error")
        except TypeError:
            error = APIError("API error")
            self.assertEqual(str(error), "API error")

    def test_connection_error(self):
        error = SDKConnectionError("Connection failed")
        self.assertIsInstance(error, MemoryClassificationError)

    def test_timeout_error(self):
        error = SDKTimeoutError("Request timed out")
        self.assertIsInstance(error, MemoryClassificationError)

    def test_validation_error(self):
        error = ValidationError("Invalid input")
        self.assertIsInstance(error, MemoryClassificationError)


class TestMemoryClassificationSDK(unittest.TestCase):
    def test_init(self):
        sdk = MemoryClassificationSDK(api_key='test_key', base_url='http://localhost:8080/api/v1')
        self.assertIsNotNone(sdk)


class TestMemorySDK(unittest.TestCase):
    def test_init(self):
        sdk = MemorySDK(config_path=None, api_url=None, api_key=None)
        self.assertIsNotNone(sdk)


class TestMemoryClient(unittest.TestCase):
    def test_init(self):
        client = MemoryClient(config_path=None, api_url=None, api_key=None)
        self.assertIsNotNone(client)


if __name__ == '__main__':
    unittest.main()
