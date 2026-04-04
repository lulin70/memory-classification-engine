"""Base plugin class for Memory Classification Engine."""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """Initialize the plugin.
        
        Args:
            name: Plugin name.
            version: Plugin version.
        """
        self.name = name
        self.version = version
        self.enabled = True
        self.config = {}
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the plugin.
        
        Args:
            config: Plugin configuration.
            
        Returns:
            True if initialization was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a message.
        
        Args:
            message: The message to process.
            context: Optional context information.
            
        Returns:
            Processed result.
        """
        pass
    
    @abstractmethod
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Process a memory.
        
        Args:
            memory: The memory to process.
            
        Returns:
            Processed memory.
        """
        pass
    
    def cleanup(self) -> bool:
        """Clean up resources.
        
        Returns:
            True if cleanup was successful, False otherwise.
        """
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information.
        
        Returns:
            Plugin information.
        """
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'type': self.__class__.__name__
        }
    
    def set_config(self, config: Dict[str, Any]):
        """Set plugin configuration.
        
        Args:
            config: Plugin configuration.
        """
        self.config.update(config)
    
    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration.
        
        Returns:
            Plugin configuration.
        """
        return self.config
