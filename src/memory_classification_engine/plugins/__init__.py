"""Plugin system for Memory Classification Engine."""

from memory_classification_engine.plugins.plugin_manager import PluginManager
from memory_classification_engine.plugins.base_plugin import BasePlugin

__all__ = ['PluginManager', 'BasePlugin']
