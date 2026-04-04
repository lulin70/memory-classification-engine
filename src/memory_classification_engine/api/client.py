"""API client for Memory Classification Engine."""

import json
import aiohttp
import socketio
from typing import Dict, Any, Optional, List


class APIClient:
    """API client for Memory Classification Engine."""
    
    def __init__(self, base_url: str = 'http://localhost:8000', api_key: str = None):
        """Initialize the API client.
        
        Args:
            base_url: Base URL of the API server.
            api_key: API key for authentication.
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
        self.sio = None
    
    async def __aenter__(self):
        """Enter async context."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        if self.session:
            await self.session.close()
        if self.sio:
            await self.sio.disconnect()
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint.
            data: Request data (for POST and PUT).
            params: Query parameters (for GET).
            
        Returns:
            Response data as a dictionary.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        if data:
            headers['Content-Type'] = 'application/json'
        
        async with getattr(self.session, method.lower())(url, json=data, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the API server."""
        return await self._request('GET', '/health')
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and classify memory."""
        data = {'message': message, 'context': context or {}}
        return await self._request('POST', '/api/memory/process', data)
    
    async def retrieve_memories(self, query: Optional[str] = None, limit: int = 5, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve memories based on query."""
        params = {'limit': limit}
        if query:
            params['query'] = query
        if tenant_id:
            params['tenant_id'] = tenant_id
        return await self._request('GET', '/api/memory/retrieve', params=params)
    
    async def manage_memory(self, action: str, memory_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage memory (view, edit, delete)."""
        request_data = {'action': action, 'memory_id': memory_id, 'data': data}
        return await self._request('POST', '/api/memory/manage', request_data)
    
    async def export_memories(self, format: str = 'json') -> Dict[str, Any]:
        """Export memories."""
        params = {'format': format}
        return await self._request('GET', '/api/memory/export', params=params)
    
    async def import_memories(self, data: Dict[str, Any], format: str = 'json') -> Dict[str, Any]:
        """Import memories."""
        request_data = {'data': data, 'format': format}
        return await self._request('POST', '/api/memory/import', request_data)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the engine."""
        return await self._request('GET', '/api/memory/stats')
    
    async def create_tenant(self, tenant_id: str, name: str, tenant_type: str, **kwargs) -> Dict[str, Any]:
        """Create a new tenant."""
        data = {'tenant_id': tenant_id, 'name': name, 'type': tenant_type, 'kwargs': kwargs}
        return await self._request('POST', '/api/tenant/create', data)
    
    async def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information."""
        return await self._request('GET', f'/api/tenant/{tenant_id}')
    
    async def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants."""
        return await self._request('GET', '/api/tenant')
    
    async def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Delete a tenant."""
        return await self._request('DELETE', f'/api/tenant/{tenant_id}')
    
    async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update tenant information."""
        return await self._request('PUT', f'/api/tenant/{tenant_id}', updates)
    
    async def add_tenant_role(self, tenant_id: str, role_name: str, permissions: List[str]) -> Dict[str, Any]:
        """Add a role to an enterprise tenant."""
        data = {'role_name': role_name, 'permissions': permissions}
        return await self._request('POST', f'/api/tenant/{tenant_id}/role', data)
    
    async def check_tenant_permission(self, tenant_id: str, role_name: str, permission: str) -> Dict[str, Any]:
        """Check if a role has a specific permission."""
        params = {'role_name': role_name, 'permission': permission}
        return await self._request('GET', f'/api/tenant/{tenant_id}/permission', params=params)
    
    async def get_tenant_memories(self, tenant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories for a specific tenant."""
        params = {'limit': limit}
        return await self._request('GET', f'/api/tenant/{tenant_id}/memories', params=params)
    
    async def generate_token(self, user_id: str) -> Dict[str, Any]:
        """Generate an authentication token."""
        data = {'user_id': user_id}
        return await self._request('POST', '/api/auth/token', data)
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify an authentication token."""
        data = {'token': token}
        return await self._request('POST', '/api/auth/verify', data)
    
    async def generate_api_key(self, user_id: str) -> Dict[str, Any]:
        """Generate an API key."""
        data = {'user_id': user_id}
        return await self._request('POST', '/api/auth/key', data)
    
    async def connect_websocket(self):
        """Connect to the WebSocket server."""
        if not self.sio:
            self.sio = socketio.AsyncClient()
            await self.sio.connect(self.base_url)
        return self.sio
    
    async def process_message_websocket(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message via WebSocket."""
        if not self.sio:
            await self.connect_websocket()
        
        # Create an event to wait for the response
        import asyncio
        event = asyncio.Event()
        response = None
        
        def on_response(data):
            nonlocal response, event
            response = data
            event.set()
        
        # Register the response handler
        self.sio.on('process_message_response', on_response)
        
        # Emit the message
        await self.sio.emit('process_message', {'message': message, 'context': context or {}})
        
        # Wait for the response
        await event.wait()
        return response
    
    async def retrieve_memories_websocket(self, query: Optional[str] = None, limit: int = 5, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve memories via WebSocket."""
        if not self.sio:
            await self.connect_websocket()
        
        # Create an event to wait for the response
        import asyncio
        event = asyncio.Event()
        response = None
        
        def on_response(data):
            nonlocal response, event
            response = data
            event.set()
        
        # Register the response handler
        self.sio.on('retrieve_memories_response', on_response)
        
        # Emit the request
        await self.sio.emit('retrieve_memories', {'query': query, 'limit': limit, 'tenant_id': tenant_id})
        
        # Wait for the response
        await event.wait()
        return response


class SyncAPIClient:
    """Synchronous API client for Memory Classification Engine."""
    
    def __init__(self, base_url: str = 'http://localhost:8000', api_key: str = None):
        """Initialize the synchronous API client.
        
        Args:
            base_url: Base URL of the API server.
            api_key: API key for authentication.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.client = APIClient(base_url, api_key)
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the API server."""
        import asyncio
        return asyncio.run(self.client.health_check())
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and classify memory."""
        import asyncio
        return asyncio.run(self.client.process_message(message, context))
    
    def retrieve_memories(self, query: Optional[str] = None, limit: int = 5, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve memories based on query."""
        import asyncio
        return asyncio.run(self.client.retrieve_memories(query, limit, tenant_id))
    
    def manage_memory(self, action: str, memory_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage memory (view, edit, delete)."""
        import asyncio
        return asyncio.run(self.client.manage_memory(action, memory_id, data))
    
    def export_memories(self, format: str = 'json') -> Dict[str, Any]:
        """Export memories."""
        import asyncio
        return asyncio.run(self.client.export_memories(format))
    
    def import_memories(self, data: Dict[str, Any], format: str = 'json') -> Dict[str, Any]:
        """Import memories."""
        import asyncio
        return asyncio.run(self.client.import_memories(data, format))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the engine."""
        import asyncio
        return asyncio.run(self.client.get_stats())
    
    def create_tenant(self, tenant_id: str, name: str, tenant_type: str, **kwargs) -> Dict[str, Any]:
        """Create a new tenant."""
        import asyncio
        return asyncio.run(self.client.create_tenant(tenant_id, name, tenant_type, **kwargs))
    
    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information."""
        import asyncio
        return asyncio.run(self.client.get_tenant(tenant_id))
    
    def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants."""
        import asyncio
        return asyncio.run(self.client.list_tenants())
    
    def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Delete a tenant."""
        import asyncio
        return asyncio.run(self.client.delete_tenant(tenant_id))
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update tenant information."""
        import asyncio
        return asyncio.run(self.client.update_tenant(tenant_id, updates))
    
    def add_tenant_role(self, tenant_id: str, role_name: str, permissions: List[str]) -> Dict[str, Any]:
        """Add a role to an enterprise tenant."""
        import asyncio
        return asyncio.run(self.client.add_tenant_role(tenant_id, role_name, permissions))
    
    def check_tenant_permission(self, tenant_id: str, role_name: str, permission: str) -> Dict[str, Any]:
        """Check if a role has a specific permission."""
        import asyncio
        return asyncio.run(self.client.check_tenant_permission(tenant_id, role_name, permission))
    
    def get_tenant_memories(self, tenant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories for a specific tenant."""
        import asyncio
        return asyncio.run(self.client.get_tenant_memories(tenant_id, limit))
    
    def generate_token(self, user_id: str) -> Dict[str, Any]:
        """Generate an authentication token."""
        import asyncio
        return asyncio.run(self.client.generate_token(user_id))
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify an authentication token."""
        import asyncio
        return asyncio.run(self.client.verify_token(token))
    
    def generate_api_key(self, user_id: str) -> Dict[str, Any]:
        """Generate an API key."""
        import asyncio
        return asyncio.run(self.client.generate_api_key(user_id))
