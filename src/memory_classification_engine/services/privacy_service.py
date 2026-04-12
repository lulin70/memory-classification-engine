"""Privacy Service for Memory Classification Engine."""

from typing import Dict, List, Optional, Any

from memory_classification_engine.services.base_service import BaseService
from memory_classification_engine.privacy.encryption import encryption_manager
from memory_classification_engine.privacy.access_control import access_control_manager
from memory_classification_engine.privacy.sensitivity_analyzer import SensitivityAnalyzer
from memory_classification_engine.privacy.audit import audit_manager


class PrivacyService(BaseService):
    """Service for privacy and security operations.

    This service handles:
    - Data encryption/decryption
    - Access control
    - Sensitivity analysis
    - Audit logging
    """

    def __init__(self, config):
        """Initialize privacy service.

        Args:
            config: Configuration manager.
        """
        super().__init__(config)
        self.sensitivity_analyzer = None

    def initialize(self) -> None:
        """Initialize privacy resources."""
        self.sensitivity_analyzer = SensitivityAnalyzer(self.config)
        self._initialized = True
        self.log_info("Privacy service initialized")

    def shutdown(self) -> None:
        """Clean up privacy resources."""
        self._initialized = False
        self.log_info("Privacy service shutdown")

    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has permission for action on resource.

        Args:
            user_id: User identifier.
            resource: Resource name.
            action: Action to perform.

        Returns:
            True if permitted, False otherwise.
        """
        return access_control_manager.check_permission(user_id, resource, action)

    def analyze_sensitivity(self, memory: Dict[str, Any]) -> str:
        """Analyze memory sensitivity level.

        Args:
            memory: Memory data.

        Returns:
            Sensitivity level ('low', 'medium', 'high').
        """
        if not self._initialized:
            raise RuntimeError("Privacy service not initialized")
        return self.sensitivity_analyzer.analyze_memory_sensitivity(memory)

    def log_audit(self, user_id: str, action: str, resource: str, details: Dict[str, Any]) -> None:
        """Log audit event.

        Args:
            user_id: User identifier.
            action: Action performed.
            resource: Resource affected.
            details: Additional details.
        """
        audit_manager.log(user_id, action, resource, details)
