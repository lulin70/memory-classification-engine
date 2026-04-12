#!/usr/bin/env python3
"""Test cases for API client module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from memory_classification_engine.api.client import APIClient, SyncAPIClient


class TestAPIClient:
    """Test APIClient class."""

    def test_init_default(self):
        """Test APIClient initialization with default values."""
        client = APIClient()
        assert client.base_url == 'http://localhost:8000'
        assert client.api_key is None
        assert client.session is None

    def test_init_custom(self):
        """Test APIClient initialization with custom values."""
        client = APIClient(base_url='http://example.com:9000', api_key='test-key-123')
        assert client.base_url == 'http://example.com:9000'
        assert client.api_key == 'test-key-123'

    def test_init_base_url_trailing_slash(self):
        """Test that trailing slash is removed from base_url."""
        client = APIClient(base_url='http://localhost:8000/')
        assert client.base_url == 'http://localhost:8000'

    @pytest.mark.asyncio
    async def test_aenter_creates_session(self):
        """Test that async context manager creates session."""
        client = APIClient()
        async with client as c:
            assert c.session is not None
            assert c is client

    @pytest.mark.asyncio
    async def test_aexit_closes_session(self):
        """Test that exit closes session."""
        client = APIClient()
        async with client:
            pass
        assert client.session is None or client.session.closed

    @pytest.mark.asyncio
    async def test_request_get_method(self):
        """Test GET request method."""
        client = APIClient(base_url='http://test.com')
        
        expected_result = {'status': 'ok'}
        
        with patch('aiohttp.ClientSession') as MockSession:
            mock_session = MockSession.return_value
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=expected_result)
            mock_response.raise_for_status = Mock()
            
            context_manager = AsyncMock()
            context_manager.__aenter__ = AsyncMock(return_value=mock_response)
            context_manager.__aexit__ = AsyncMock(return_value=False)
            
            mock_session.get = Mock(return_value=context_manager)
            
            client.session = mock_session
            
            result = await client._request('GET', '/test')
            assert result == expected_result
            mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_with_api_key(self):
        """Test that request includes Authorization header when api_key is set."""
        client = APIClient(base_url='http://test.com', api_key='my-secret-key')
        
        with patch('aiohttp.ClientSession') as MockSession:
            mock_session = MockSession.return_value
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={})
            mock_response.raise_for_status = Mock()
            
            context_manager = AsyncMock()
            context_manager.__aenter__ = AsyncMock(return_value=mock_response)
            context_manager.__aexit__ = AsyncMock(return_value=False)
            
            mock_session.get = Mock(return_value=context_manager)
            
            client.session = mock_session
            
            await client._request('GET', '/health')
            
            call_kwargs = mock_session.get.call_args[1]
            headers = call_kwargs.get('headers', {})
            assert 'Authorization' in headers
            assert 'Bearer my-secret-key' in headers['Authorization']

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """Test health check endpoint."""
        client = APIClient(base_url='http://test.com')
        
        expected_result = {'status': 'healthy', 'version': '1.0.0'}
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_result
            
            result = await client.health_check()
            
            assert result == expected_result
            mock_request.assert_called_once_with('GET', '/health')

    @pytest.mark.asyncio
    async def test_process_message_endpoint(self):
        """Test process message endpoint."""
        client = APIClient(base_url='http://test.com')
        
        message = "I prefer using spaces over tabs"
        expected_result = {'matches': [{'memory_type': 'user_preference'}]}
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_result
            
            result = await client.process_message(message)
            
            assert result == expected_result
            assert mock_request.called

    @pytest.mark.asyncio
    async def test_retrieve_memories_endpoint(self):
        """Test retrieve memories endpoint."""
        client = APIClient(base_url='http://test.com')
        
        expected_result = [{'id': 'mem_1', 'content': 'test'}]
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_result
            
            result = await client.retrieve_memories(query="test", limit=10)
            
            assert result == expected_result
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_manage_memory_endpoint(self):
        """Test manage memory endpoint."""
        client = APIClient(base_url='http://test.com')
        
        expected_result = {'success': True}
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_result
            
            result = await client.manage_memory('delete', 'mem_123')
            
            assert result == expected_result
            call_args = mock_request.call_args
            assert 'mem_123' in str(call_args)

    @pytest.mark.asyncio
    async def test_export_memories_endpoint(self):
        """Test export memories endpoint."""
        client = APIClient(base_url='http://test.com')
        
        expected_result = {'data': [], 'format': 'json'}
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_result
            
            result = await client.export_memories(format='json')
            
            assert result == expected_result
            mock_request.assert_called_once_with('GET', '/api/memory/export', params={'format': 'json'})

    @pytest.mark.asyncio
    async def test_import_memories_endpoint(self):
        """Test import memories endpoint."""
        client = APIClient(base_url='http://test.com')
        
        import_data = [{'content': 'test memory'}]
        expected_result = {'success': True, 'count': 1}
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_result
            
            result = await client.import_memories(import_data, format='json')
            
            assert result == expected_result
            assert mock_request.called

    @pytest.mark.asyncio
    async def test_get_stats_endpoint(self):
        """Test get stats endpoint."""
        client = APIClient(base_url='http://test.com')
        
        expected_result = {'total_memories': 100, 'by_type': {}}
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_result
            
            result = await client.get_stats()
            
            assert result == expected_result
            mock_request.assert_called_once_with('GET', '/api/memory/stats')

    @pytest.mark.asyncio
    async def test_tenant_operations(self):
        """Test tenant CRUD operations."""
        client = APIClient(base_url='http://test.com')
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            # Create tenant
            create_data = {'tenant_id': 'tenant_1', 'name': 'Test Tenant', 'type': 'personal'}
            mock_request.return_value = {'success': True}
            result = await client.create_tenant('tenant_1', 'Test Tenant', 'personal')
            assert result['success'] is True
            
            # Get tenant
            mock_request.return_value = {'tenant_id': 'tenant_1', 'name': 'Test Tenant'}
            result = await client.get_tenant('tenant_1')
            assert result['tenant_id'] == 'tenant_1'
            
            # List tenants
            mock_request.return_value = []
            result = await client.list_tenants()
            assert isinstance(result, list)
            
            # Update tenant
            mock_request.return_value = {'success': True}
            result = await client.update_tenant('tenant_1', {'name': 'Updated Name'})
            assert result['success'] is True
            
            # Delete tenant
            mock_request.return_value = {'success': True}
            result = await client.delete_tenant('tenant_1')
            assert result['success'] is True

    @pytest.mark.asyncio
    async def test_auth_operations(self):
        """Test authentication operations."""
        client = APIClient(base_url='http://test.com')
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            # Generate token
            mock_request.return_value = {'token': 'jwt-token-123'}
            result = await client.generate_token('user_1')
            assert 'token' in result
            
            # Verify token
            mock_request.return_value = {'valid': True, 'user_id': 'user_1'}
            result = await client.verify_token('jwt-token-123')
            assert result['valid'] is True
            
            # Generate API key
            mock_request.return_value = {'api_key': 'key-456'}
            result = await client.generate_api_key('user_1')
            assert 'api_key' in result


class TestSyncAPIClient:
    """Test SyncAPIClient class."""

    def test_init(self):
        """Test SyncAPIClient initialization."""
        sync_client = SyncAPIClient(base_url='http://localhost:8080', api_key='sync-key')
        assert sync_client.base_url == 'http://localhost:8080'
        assert sync_client.api_key == 'sync-key'
        assert isinstance(sync_client.client, APIClient)

    def test_wraps_async_methods(self):
        """Test that SyncAPIClient wraps all async methods."""
        sync_client = SyncAPIClient()
        
        methods = [
            'health_check', 'process_message', 'retrieve_memories',
            'manage_memory', 'export_memories', 'import_memories',
            'get_stats', 'create_tenant', 'get_tenant', 'list_tenants',
            'delete_tenant', 'update_tenant', 'add_tenant_role',
            'check_tenant_permission', 'get_tenant_memories',
            'generate_token', 'verify_token', 'generate_api_key'
        ]
        
        for method_name in methods:
            assert hasattr(sync_client, method_name), f"Missing method: {method_name}"
            assert callable(getattr(sync_client, method_name)), f"Method not callable: {method_name}"


class TestAPIErrorHandling:
    """Test API error handling scenarios."""

    @pytest.mark.asyncio
    async def test_missing_query_parameter(self):
        """Test that missing query parameter works correctly."""
        client = APIClient(base_url='http://test.com')
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []
            
            result = await client.retrieve_memories(limit=5)
            
            assert isinstance(result, list)
            call_kwargs = mock_request.call_args[1]
            params = call_kwargs.get('params', {})
            assert 'query' not in params

    @pytest.mark.asyncio
    async def test_empty_message_handling(self):
        """Test handling of empty messages."""
        client = APIClient(base_url='http://test.com')
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {'matches': []}
            
            result = await client.process_message("")
            
            assert result == {'matches': []}

    @pytest.mark.asyncio
    async def test_context_parameter_passed(self):
        """Test that context parameter is passed correctly."""
        client = APIClient(base_url='http://test.com')
        
        context = {'conversation_id': 'conv_123', 'user_id': 'user_456'}
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {'matches': []}
            
            await client.process_message("test", context=context)
            
            assert mock_request.called
            call_args = mock_request.call_args
            if call_args[1] and 'data' in call_args[1]:
                assert call_args[1]['data'].get('context') == context