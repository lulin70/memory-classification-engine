"""Tenant management module for personal and enterprise memory separation."""

from typing import Dict, Optional, List
from datetime import datetime
from memory_classification_engine.utils.helpers import get_current_time
from memory_classification_engine.utils.logger import logger


class Tenant:
    """Base tenant class."""
    
    def __init__(self, tenant_id: str, name: str, tenant_type: str):
        """Initialize a tenant.
        
        Args:
            tenant_id: Unique tenant identifier.
            name: Tenant name.
            tenant_type: Tenant type ('personal' or 'enterprise').
        """
        self.tenant_id = tenant_id
        self.name = name
        self.tenant_type = tenant_type
        self.created_at = get_current_time()
        self.updated_at = get_current_time()
        self.memories = []
    
    def add_memory(self, memory: Dict):
        """Add a memory to the tenant.
        
        Args:
            memory: Memory to add.
        """
        memory['tenant_id'] = self.tenant_id
        self.memories.append(memory)
    
    def get_memories(self) -> List[Dict]:
        """Get all memories for the tenant.
        
        Returns:
            List of memories.
        """
        return self.memories
    
    def update(self, updates: Dict):
        """Update tenant information.
        
        Args:
            updates: Dictionary of updates.
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = get_current_time()


class PersonalTenant(Tenant):
    """Personal tenant class."""
    
    def __init__(self, tenant_id: str, name: str, user_id: str):
        """Initialize a personal tenant.
        
        Args:
            tenant_id: Unique tenant identifier.
            name: Tenant name.
            user_id: User ID associated with the personal tenant.
        """
        super().__init__(tenant_id, name, 'personal')
        self.user_id = user_id
        self.decay_factor = 0.9  # Comment in Chinese removedr
    
    def decay_memories(self):
        """Decay personal memories based on time."""
        current_time = datetime.now()
        for memory in self.memories:
            if 'last_accessed' in memory:
                try:
                    last_accessed = datetime.fromisoformat(memory['last_accessed'].replace('Z', '+00:00'))
                    days_since_access = (current_time - last_accessed).days
                    if days_since_access > 30:
                        # Comment in Chinese removed
                        if 'weight' in memory:
                            memory['weight'] *= self.decay_factor
                except (ValueError, TypeError):
                    pass


class EnterpriseTenant(Tenant):
    """Enterprise tenant class."""
    
    def __init__(self, tenant_id: str, name: str, organization_id: str):
        """Initialize an enterprise tenant.
        
        Args:
            tenant_id: Unique tenant identifier.
            name: Tenant name.
            organization_id: Organization ID associated with the enterprise tenant.
        """
        super().__init__(tenant_id, name, 'enterprise')
        self.organization_id = organization_id
        self.roles = {}
    
    def add_role(self, role_name: str, permissions: List[str]):
        """Add a role to the enterprise tenant.
        
        Args:
            role_name: Role name.
            permissions: List of permissions.
        """
        self.roles[role_name] = permissions
    
    def has_permission(self, role_name: str, permission: str) -> bool:
        """Check if a role has a specific permission.
        
        Args:
            role_name: Role name.
            permission: Permission to check.
            
        Returns:
            True if the role has the permission, False otherwise.
        """
        if role_name not in self.roles:
            return False
        return permission in self.roles[role_name]


class TenantManager:
    """Tenant manager class."""
    
    def __init__(self):
        """Initialize the tenant manager."""
        self.tenants = {}
    
    def create_tenant(self, tenant_id: str, name: str, tenant_type: str, **kwargs) -> Tenant:
        """Create a new tenant.
        
        Args:
            tenant_id: Unique tenant identifier.
            name: Tenant name.
            tenant_type: Tenant type ('personal' or 'enterprise').
            **kwargs: Additional parameters.
            
        Returns:
            Created tenant.
        """
        if tenant_id in self.tenants:
            logger.warning(f"Tenant {tenant_id} already exists")
            return self.tenants[tenant_id]
        
        if tenant_type == 'personal':
            user_id = kwargs.get('user_id', tenant_id)
            tenant = PersonalTenant(tenant_id, name, user_id)
        elif tenant_type == 'enterprise':
            organization_id = kwargs.get('organization_id', tenant_id)
            tenant = EnterpriseTenant(tenant_id, name, organization_id)
        else:
            logger.error(f"Invalid tenant type: {tenant_type}")
            return None
        
        self.tenants[tenant_id] = tenant
        logger.info(f"Created tenant: {tenant_id} ({tenant_type})")
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            Tenant if found, None otherwise.
        """
        return self.tenants.get(tenant_id)
    
    def list_tenants(self) -> List[Tenant]:
        """List all tenants.
        
        Returns:
            List of tenants.
        """
        return list(self.tenants.values())
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant.
        
        Args:
            tenant_id: Tenant ID.
            
        Returns:
            True if the tenant was deleted, False otherwise.
        """
        if tenant_id in self.tenants:
            del self.tenants[tenant_id]
            logger.info(f"Deleted tenant: {tenant_id}")
            return True
        return False
    
    def update_tenant(self, tenant_id: str, updates: Dict) -> Optional[Tenant]:
        """Update a tenant.
        
        Args:
            tenant_id: Tenant ID.
            updates: Dictionary of updates.
            
        Returns:
            Updated tenant if found, None otherwise.
        """
        tenant = self.get_tenant(tenant_id)
        if tenant:
            tenant.update(updates)
            logger.info(f"Updated tenant: {tenant_id}")
        return tenant
