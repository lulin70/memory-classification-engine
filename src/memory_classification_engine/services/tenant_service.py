"""Tenant Service for Memory Classification Engine."""

from typing import Dict, List, Optional, Any

from memory_classification_engine.services.base_service import BaseService
from memory_classification_engine.utils.tenant import TenantManager


class TenantService(BaseService):
    """Service for tenant management operations.

    This service handles:
    - Tenant CRUD operations
    - Tenant isolation
    - Role-based access control
    """

    def __init__(self, config):
        """Initialize tenant service.

        Args:
            config: Configuration manager.
        """
        super().__init__(config)
        self.tenant_manager = None

    def initialize(self) -> None:
        """Initialize tenant resources."""
        self.tenant_manager = TenantManager()
        self._initialized = True
        self.log_info("Tenant service initialized")

    def shutdown(self) -> None:
        """Clean up tenant resources."""
        self._initialized = False
        self.log_info("Tenant service shutdown")

    def create_tenant(
        self,
        tenant_id: str,
        name: str,
        tenant_type: str = 'personal',
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new tenant.

        Args:
            tenant_id: Tenant identifier.
            name: Tenant name.
            tenant_type: Type of tenant ('personal' or 'enterprise').
            user_id: Optional owner user ID.

        Returns:
            Tenant data or None if creation failed.
        """
        if not self._initialized:
            raise RuntimeError("Tenant service not initialized")

        try:
            tenant = self.tenant_manager.create_tenant(
                tenant_id=tenant_id,
                name=name,
                tenant_type=tenant_type,
                user_id=user_id
            )
            return tenant.to_dict() if hasattr(tenant, 'to_dict') else {'tenant_id': tenant_id}
        except Exception as e:
            self.log_error(f"Failed to create tenant: {e}")
            return None

    def get_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant by ID.

        Args:
            tenant_id: Tenant identifier.

        Returns:
            Tenant data or None if not found.
        """
        if not self._initialized:
            raise RuntimeError("Tenant service not initialized")

        try:
            tenant = self.tenant_manager.get_tenant(tenant_id)
            return tenant.to_dict() if tenant and hasattr(tenant, 'to_dict') else None
        except Exception as e:
            self.log_error(f"Failed to get tenant: {e}")
            return None

    def list_tenants(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tenants.

        Args:
            user_id: Optional user filter.

        Returns:
            List of tenant data.
        """
        if not self._initialized:
            raise RuntimeError("Tenant service not initialized")

        try:
            tenants = self.tenant_manager.list_tenants(user_id)
            return [t.to_dict() if hasattr(t, 'to_dict') else {'tenant_id': str(t)} for t in tenants]
        except Exception as e:
            self.log_error(f"Failed to list tenants: {e}")
            return []

    def add_memory_to_tenant(self, tenant_id: str, memory: Dict[str, Any]) -> bool:
        """Add a memory to a tenant.

        Args:
            tenant_id: Tenant identifier.
            memory: Memory data.

        Returns:
            True if successful, False otherwise.
        """
        if not self._initialized:
            raise RuntimeError("Tenant service not initialized")

        try:
            tenant = self.tenant_manager.get_tenant(tenant_id)
            if tenant:
                tenant.add_memory(memory)
                return True
            return False
        except Exception as e:
            self.log_error(f"Failed to add memory to tenant: {e}")
            return False
