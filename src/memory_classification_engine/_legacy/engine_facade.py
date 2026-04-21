"""Memory Classification Engine - Facade Pattern Implementation.

This module provides a refactored version of the MemoryClassificationEngine
using the Facade pattern. It delegates all operations to specialized services
while maintaining backward compatibility.
"""

import os
from typing import Dict, List, Optional, Any

from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.helpers import get_current_time
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.services import (
    ClassificationService,
    StorageService,
    PrivacyService,
    RecommendationService,
    TenantService
)


class MemoryClassificationEngineFacade:
    """Facade for Memory Classification Engine.
    
    This class provides a simplified interface to the complex subsystem
    of services. It delegates all operations to specialized services.
    """
    
    def __init__(self, config_path: str = None):
        """Initialize the memory classification engine facade."""
        self.config = ConfigManager(config_path)
        self.logger = logger
        self._initialize_services()
        self.logger.info("MemoryClassificationEngineFacade initialized")
    
    def _initialize_services(self) -> None:
        """Initialize all services."""
        self.classification_service = ClassificationService(self.config)
        self.classification_service.initialize()
        
        self.storage_service = StorageService(self.config)
        self.storage_service.initialize()
        
        self.privacy_service = PrivacyService(self.config)
        self.privacy_service.initialize()
        
        self.recommendation_service = RecommendationService(self.config)
        self.recommendation_service.initialize()
        
        self.tenant_service = TenantService(self.config)
        self.tenant_service.initialize()
    
    def shutdown(self) -> None:
        """Shutdown all services."""
        self.classification_service.shutdown()
        self.storage_service.shutdown()
        self.privacy_service.shutdown()
        self.recommendation_service.shutdown()
        self.tenant_service.shutdown()
        self.logger.info("MemoryClassificationEngineFacade shutdown")
    
    # Comment in Chinese removedtions
    def classify_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.classification_service.classify_message(message, context)
    
    # Comment in Chinese removedtions
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        return self.storage_service.store_memory(memory)
    
    def store_memories_batch(self, memories: List[Dict[str, Any]]) -> int:
        return self.storage_service.store_memories_batch(memories)
    
    def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        return self.storage_service.retrieve_memory(memory_id)
    
    def retrieve_memories(self, query: Optional[str] = None, tier: Optional[int] = None, 
                         limit: int = 100, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.storage_service.retrieve_memories(query, tier, limit, memory_type)
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        return self.storage_service.update_memory(memory_id, updates)
    
    def delete_memory(self, memory_id: str) -> bool:
        return self.storage_service.delete_memory(memory_id)
    
    # Comment in Chinese removedtions
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        return self.privacy_service.check_permission(user_id, resource, action)
    
    def analyze_sensitivity(self, memory: Dict[str, Any]) -> str:
        return self.privacy_service.analyze_sensitivity(memory)
    
    # Comment in Chinese removedtions
    def get_recommendations(self, user_id: str, query: Optional[str] = None,
                           limit: int = 5, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return self.recommendation_service.get_recommendations(user_id, query, limit, context)
    
    def find_similar_memories(self, memory_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        return self.recommendation_service.find_similar_memories(memory_id, limit)
    
    # Comment in Chinese removedtions
    def create_tenant(self, tenant_id: str, name: str, tenant_type: str = 'personal',
                     user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return self.tenant_service.create_tenant(tenant_id, name, tenant_type, user_id)
    
    def get_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        return self.tenant_service.get_tenant(tenant_id)
    
    def list_tenants(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.tenant_service.list_tenants(user_id)
