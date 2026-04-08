"""Memory Classification Engine SDK client."""

import requests
import json
from typing import Dict, List, Optional, Any


class MemoryClassificationSDK:
    """Memory Classification Engine SDK client."""
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000/api/v1"):
        """Initialize the SDK client.
        
        Args:
            api_key: API key for authentication.
            base_url: Base URL of the API.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                     params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint.
            data: Request body data.
            params: Query parameters.
            
        Returns:
            Response data as dictionary.
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, params=params)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data, params=params)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and classify it into memories.
        
        Args:
            message: The message to process.
            context: Optional context information.
            
        Returns:
            Processing result.
        """
        data = {
            "message": message,
            "context": context or {}
        }
        return self._make_request("POST", "process", data)
    
    def retrieve_memories(self, query: Optional[str] = None, limit: int = 5, 
                        tenant_id: Optional[str] = None, memory_type: Optional[str] = None, 
                        tier: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve memories based on query parameters.
        
        Args:
            query: Search query string.
            limit: Maximum number of results.
            tenant_id: Filter by tenant ID.
            memory_type: Filter by memory type.
            tier: Filter by storage tier.
            
        Returns:
            Retrieved memories.
        """
        params = {
            "limit": limit
        }
        if query:
            params["query"] = query
        if tenant_id:
            params["tenant_id"] = tenant_id
        if memory_type:
            params["memory_type"] = memory_type
        if tier:
            params["tier"] = tier
        
        return self._make_request("GET", "memories", params=params)
    
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get a specific memory by ID.
        
        Args:
            memory_id: Memory ID.
            
        Returns:
            Memory data.
        """
        return self._make_request("GET", f"memories/{memory_id}")
    
    def update_memory(self, memory_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a memory.
        
        Args:
            memory_id: Memory ID.
            data: Update data.
            
        Returns:
            Updated memory.
        """
        return self._make_request("PUT", f"memories/{memory_id}", data)
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a memory.
        
        Args:
            memory_id: Memory ID.
            
        Returns:
            Deletion result.
        """
        return self._make_request("DELETE", f"memories/{memory_id}")
    
    def export_memories(self, format: str = "json", tenant_id: Optional[str] = None, 
                       memory_types: Optional[List[str]] = None) -> bytes:
        """Export memories in various formats.
        
        Args:
            format: Export format (json, csv, jsonl).
            tenant_id: Filter by tenant ID.
            memory_types: List of memory types to export.
            
        Returns:
            Exported data as bytes.
        """
        params = {
            "format": format
        }
        if tenant_id:
            params["tenant_id"] = tenant_id
        if memory_types:
            params["memory_types"] = ",".join(memory_types)
        
        url = f"{self.base_url}/export"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.content
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics.
        
        Returns:
            System statistics.
        """
        return self._make_request("GET", "stats")
    
    def manage_memory(self, action: str, memory_id: str, data: Optional[Dict[str, Any]] = None, 
                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """Manage memory operations (view, edit, delete).
        
        Args:
            action: Action to perform (view, edit, delete).
            memory_id: Memory ID.
            data: Optional data for editing.
            user_id: Optional user ID.
            
        Returns:
            Management result.
        """
        request_data = {
            "action": action,
            "memory_id": memory_id
        }
        if data:
            request_data["data"] = data
        if user_id:
            request_data["user_id"] = user_id
        
        return self._make_request("POST", "memories/manage", request_data)
    
    def process_with_agent(self, agent_name: str, message: str, 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message with a specific agent.
        
        Args:
            agent_name: Agent name.
            message: Message to process.
            context: Optional context information.
            
        Returns:
            Agent processing result.
        """
        data = {
            "agent_name": agent_name,
            "message": message,
            "context": context or {}
        }
        return self._make_request("POST", "process/agent", data)
    
    def create_tenant(self, tenant_id: str, name: str, tenant_type: str, 
                     user_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Create a new tenant.
        
        Args:
            tenant_id: Tenant ID.
            name: Tenant name.
            tenant_type: Tenant type.
            user_id: Optional user ID.
            **kwargs: Additional tenant properties.
            
        Returns:
            Creation result.
        """
        data = {
            "tenant_id": tenant_id,
            "name": name,
            "tenant_type": tenant_type
        }
        if user_id:
            data["user_id"] = user_id
        data.update(kwargs)
        
        return self._make_request("POST", "tenants", data)
    
    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Get a tenant by ID.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            Tenant data.
        """
        return self._make_request("GET", f"tenants/{tenant_id}")
    
    def update_tenant(self, tenant_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a tenant.
        
        Args:
            tenant_id: Tenant ID.
            data: Update data.
            
        Returns:
            Updated tenant.
        """
        return self._make_request("PUT", f"tenants/{tenant_id}", data)
    
    def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Delete a tenant.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            Deletion result.
        """
        return self._make_request("DELETE", f"tenants/{tenant_id}")
    
    def list_tenants(self) -> Dict[str, Any]:
        """List all tenants.
        
        Returns:
            List of tenants.
        """
        return self._make_request("GET", "tenants")