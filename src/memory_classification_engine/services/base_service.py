"""Base service class for all services."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.logger import logger


class BaseService(ABC):
    """Abstract base class for all services.
    
    Provides common functionality for service initialization,
    configuration access, and logging.
    """
    
    def __init__(self, config: ConfigManager):
        """Initialize the service.
        
        Args:
            config: Configuration manager instance.
        """
        self.config = config
        self.logger = logger
        self._initialized = False
        
    @abstractmethod
    def initialize(self) -> None:
        """Initialize service-specific resources.
        
        This method should be implemented by concrete services
        to perform any necessary setup.
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Clean up service resources.
        
        This method should be called when the service is no longer needed
        to release any resources.
        """
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        return self.config.get(key, default)
    
    def log_info(self, message: str) -> None:
        """Log info message.
        
        Args:
            message: Log message.
        """
        self.logger.info(f"[{self.__class__.__name__}] {message}")
    
    def log_warning(self, message: str) -> None:
        """Log warning message.
        
        Args:
            message: Log message.
        """
        self.logger.warning(f"[{self.__class__.__name__}] {message}")
    
    def log_error(self, message: str) -> None:
        """Log error message.
        
        Args:
            message: Log message.
        """
        self.logger.error(f"[{self.__class__.__name__}] {message}")
