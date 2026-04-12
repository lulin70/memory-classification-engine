"""Python SDK for Memory Classification Engine."""

from typing import Dict, Any, Optional, List
from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.api.client import SyncAPIClient


class MemorySDK:
    """Python SDK for Memory Classification Engine."""
    
    def __init__(self, config_path: str = None, api_url: str = None, api_key: str = None):
        """Initialize the SDK.
        
        Args:
            config_path: Path to configuration file for local engine.
            api_url: API URL for remote engine (if using API mode).
            api_key: API key for authentication (if using API mode).
        """
        self.config_path = config_path
        self.api_url = api_url
        self.api_key = api_key
        
        if api_url:
            # Comment in Chinese removed
            self.mode = 'api'
            self.client = SyncAPIClient(api_url, api_key)
        else:
            # Comment in Chinese removed
            self.mode = 'local'
            self.engine = MemoryClassificationEngine(config_path)
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and classify memory.
        
        Args:
            message: The message to process.
            context: Optional context for the message.
            
        Returns:
            A dictionary containing the classification results.
        """
        if self.mode == 'api':
            return self.client.process_message(message, context)
        else:
            return self.engine.process_message(message, context)
    
    def retrieve_memories(self, query: Optional[str] = None, limit: int = 5, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve memories based on query.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            tenant_id: Optional tenant ID to filter memories by tenant.
            
        Returns:
            A list of matching memories.
        """
        if self.mode == 'api':
            return self.client.retrieve_memories(query, limit, tenant_id)
        else:
            return self.engine.retrieve_memories(query, limit, tenant_id)
    
    def manage_memory(self, action: str, memory_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage memory (view, edit, delete).
        
        Args:
            action: The action to perform (view, edit, delete).
            memory_id: The ID of the memory to manage.
            data: Optional data for editing.
            
        Returns:
            A dictionary containing the result.
        """
        if self.mode == 'api':
            return self.client.manage_memory(action, memory_id, data)
        else:
            return self.engine.manage_memory(action, memory_id, data)
    
    def export_memories(self, format: str = "json") -> Dict[str, Any]:
        """Export memories.
        
        Args:
            format: Export format (json).
            
        Returns:
            A dictionary containing the exported memories.
        """
        if self.mode == 'api':
            return self.client.export_memories(format)
        else:
            return self.engine.export_memories(format)
    
    def import_memories(self, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        """Import memories.
        
        Args:
            data: The data to import.
            format: Import format (json).
            
        Returns:
            A dictionary containing the import result.
        """
        if self.mode == 'api':
            return self.client.import_memories(data, format)
        else:
            return self.engine.import_memories(data, format)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the engine.
        
        Returns:
            A dictionary with statistics.
        """
        if self.mode == 'api':
            return self.client.get_stats()
        else:
            return self.engine.get_stats()
    
    def create_tenant(self, tenant_id: str, name: str, tenant_type: str, **kwargs) -> Dict[str, Any]:
        """Create a new tenant.
        
        Args:
            tenant_id: Unique tenant identifier.
            name: Tenant name.
            tenant_type: Tenant type ('personal' or 'enterprise').
            **kwargs: Additional parameters.
            
        Returns:
            A dictionary containing the created tenant information.
        """
        if self.mode == 'api':
            return self.client.create_tenant(tenant_id, name, tenant_type, **kwargs)
        else:
            return self.engine.create_tenant(tenant_id, name, tenant_type, **kwargs)
    
    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            A dictionary containing the tenant information.
        """
        if self.mode == 'api':
            return self.client.get_tenant(tenant_id)
        else:
            return self.engine.get_tenant(tenant_id)
    
    def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants.
        
        Returns:
            A list of tenant information dictionaries.
        """
        if self.mode == 'api':
            return self.client.list_tenants()
        else:
            return self.engine.list_tenants()
    
    def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Delete a tenant.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            A dictionary containing the result.
        """
        if self.mode == 'api':
            return self.client.delete_tenant(tenant_id)
        else:
            return self.engine.delete_tenant(tenant_id)
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update tenant information.
        
        Args:
            tenant_id: Tenant ID.
            updates: Dictionary of updates.
            
        Returns:
            A dictionary containing the updated tenant information.
        """
        if self.mode == 'api':
            return self.client.update_tenant(tenant_id, updates)
        else:
            return self.engine.update_tenant(tenant_id, updates)
    
    def add_tenant_role(self, tenant_id: str, role_name: str, permissions: List[str]) -> Dict[str, Any]:
        """Add a role to an enterprise tenant.
        
        Args:
            tenant_id: Tenant ID.
            role_name: Role name.
            permissions: List of permissions.
            
        Returns:
            A dictionary containing the result.
        """
        if self.mode == 'api':
            return self.client.add_tenant_role(tenant_id, role_name, permissions)
        else:
            return self.engine.add_tenant_role(tenant_id, role_name, permissions)
    
    def check_tenant_permission(self, tenant_id: str, role_name: str, permission: str) -> Dict[str, Any]:
        """Check if a role has a specific permission.
        
        Args:
            tenant_id: Tenant ID.
            role_name: Role name.
            permission: Permission to check.
            
        Returns:
            A dictionary containing the result.
        """
        if self.mode == 'api':
            return self.client.check_tenant_permission(tenant_id, role_name, permission)
        else:
            return self.engine.check_tenant_permission(tenant_id, role_name, permission)
    
    def get_tenant_memories(self, tenant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories for a specific tenant.
        
        Args:
            tenant_id: Tenant ID.
            limit: Maximum number of memories to return.
            
        Returns:
            A list of memories for the tenant.
        """
        if self.mode == 'api':
            return self.client.get_tenant_memories(tenant_id, limit)
        else:
            return self.engine.get_tenant_memories(tenant_id, limit)
    
    def clear_working_memory(self):
        """Clear working memory (only available in local mode)."""
        if self.mode == 'local':
            self.engine.clear_working_memory()
    
    def reload_config(self):
        """Reload configuration (only available in local mode)."""
        if self.mode == 'local':
            self.engine.reload_config()


class MemoryClient:
    """Convenience client for Memory Classification Engine."""
    
    def __init__(self, config_path: str = None, api_url: str = None, api_key: str = None):
        """Initialize the client.
        
        Args:
            config_path: Path to configuration file for local engine.
            api_url: API URL for remote engine (if using API mode).
            api_key: API key for authentication (if using API mode).
        """
        self.sdk = MemorySDK(config_path, api_url, api_key)
    
    def remember(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Remember a message.
        
        Args:
            message: The message to remember.
            context: Optional context for the message.
            
        Returns:
            A dictionary containing the classification results.
        """
        return self.sdk.process_message(message, context)
    
    def recall(self, query: Optional[str] = None, limit: int = 5, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recall memories based on query.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            tenant_id: Optional tenant ID to filter memories by tenant.
            
        Returns:
            A list of matching memories.
        """
        return self.sdk.retrieve_memories(query, limit, tenant_id)
    
    def manage(self, action: str, memory_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage memory (view, edit, delete).
        
        Args:
            action: The action to perform (view, edit, delete).
            memory_id: The ID of the memory to manage.
            data: Optional data for editing.
            
        Returns:
            A dictionary containing the result.
        """
        return self.sdk.manage_memory(action, memory_id, data)
    
    def export(self, format: str = "json") -> Dict[str, Any]:
        """Export memories.
        
        Args:
            format: Export format (json).
            
        Returns:
            A dictionary containing the exported memories.
        """
        return self.sdk.export_memories(format)
    
    def import_(self, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        """Import memories.
        
        Args:
            data: The data to import.
            format: Import format (json).
            
        Returns:
            A dictionary containing the import result.
        """
        return self.sdk.import_memories(data, format)
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about the engine.
        
        Returns:
            A dictionary with statistics.
        """
        return self.sdk.get_stats()
    
    def create_tenant(self, tenant_id: str, name: str, tenant_type: str, **kwargs) -> Dict[str, Any]:
        """Create a new tenant.
        
        Args:
            tenant_id: Unique tenant identifier.
            name: Tenant name.
            tenant_type: Tenant type ('personal' or 'enterprise').
            **kwargs: Additional parameters.
            
        Returns:
            A dictionary containing the created tenant information.
        """
        return self.sdk.create_tenant(tenant_id, name, tenant_type, **kwargs)
    
    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            A dictionary containing the tenant information.
        """
        return self.sdk.get_tenant(tenant_id)
    
    def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants.
        
        Returns:
            A list of tenant information dictionaries.
        """
        return self.sdk.list_tenants()
    
    def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Delete a tenant.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            A dictionary containing the result.
        """
        return self.sdk.delete_tenant(tenant_id)
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update tenant information.
        
        Args:
            tenant_id: Tenant ID.
            updates: Dictionary of updates.
            
        Returns:
            A dictionary containing the updated tenant information.
        """
        return self.sdk.update_tenant(tenant_id, updates)
    
    def add_tenant_role(self, tenant_id: str, role_name: str, permissions: List[str]) -> Dict[str, Any]:
        """Add a role to an enterprise tenant.
        
        Args:
            tenant_id: Tenant ID.
            role_name: Role name.
            permissions: List of permissions.
            
        Returns:
            A dictionary containing the result.
        """
        return self.sdk.add_tenant_role(tenant_id, role_name, permissions)
    
    def check_tenant_permission(self, tenant_id: str, role_name: str, permission: str) -> Dict[str, Any]:
        """Check if a role has a specific permission.
        
        Args:
            tenant_id: Tenant ID.
            role_name: Role name.
            permission: Permission to check.
            
        Returns:
            A dictionary containing the result.
        """
        return self.sdk.check_tenant_permission(tenant_id, role_name, permission)
    
    def get_tenant_memories(self, tenant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories for a specific tenant.
        
        Args:
            tenant_id: Tenant ID.
            limit: Maximum number of memories to return.
            
        Returns:
            A list of memories for the tenant.
        """
        return self.sdk.get_tenant_memories(tenant_id, limit)
    
    def clear(self):
        """Clear working memory (only available in local mode)."""
        self.sdk.clear_working_memory()
    
    def reload(self):
        """Reload configuration (only available in local mode)."""
        self.sdk.reload_config()
