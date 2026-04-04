"""Plugin manager for Memory Classification Engine."""

import os
import importlib.util
import json
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.plugins.base_plugin import BasePlugin


class PluginManager:
    """Manages plugins for Memory Classification Engine."""
    
    def __init__(self, plugins_dir: str = None):
        """Initialize the plugin manager.
        
        Args:
            plugins_dir: Directory where plugins are stored.
        """
        self.plugins_dir = plugins_dir or os.path.join(os.path.dirname(__file__), 'plugins')
        self.plugins = {}
        self.enabled_plugins = set()
        self.plugin_manifest = {}
        
        # Create plugins directory if it doesn't exist
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # Load built-in plugins
        self._load_builtin_plugins()
    
    def _load_builtin_plugins(self):
        """Load built-in plugins."""
        # Import built-in plugins
        try:
            from memory_classification_engine.plugins.builtin.sentiment_analyzer import SentimentAnalyzerPlugin
            from memory_classification_engine.plugins.builtin.entity_extractor import EntityExtractorPlugin
            
            # Add built-in plugins
            self.add_plugin(SentimentAnalyzerPlugin())
            self.add_plugin(EntityExtractorPlugin())
            
            logger.info("Loaded built-in plugins")
        except ImportError as e:
            logger.warning(f"Error loading built-in plugins: {e}")
    
    def load_plugins(self):
        """Load plugins from directory."""
        if not os.path.exists(self.plugins_dir):
            logger.warning(f"Plugins directory {self.plugins_dir} does not exist")
            return
        
        # Load plugin manifests
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.json'):
                manifest_path = os.path.join(self.plugins_dir, filename)
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                        self.plugin_manifest[manifest['name']] = manifest
                        logger.info(f"Loaded plugin manifest: {manifest['name']}")
                except Exception as e:
                    logger.error(f"Error loading plugin manifest {filename}: {e}")
        
        # Load plugin modules
        for plugin_name, manifest in self.plugin_manifest.items():
            if 'module' in manifest:
                try:
                    self._load_plugin_module(plugin_name, manifest)
                except Exception as e:
                    logger.error(f"Error loading plugin {plugin_name}: {e}")
    
    def _load_plugin_module(self, plugin_name: str, manifest: Dict[str, Any]):
        """Load a plugin module.
        
        Args:
            plugin_name: Plugin name.
            manifest: Plugin manifest.
        """
        module_path = os.path.join(self.plugins_dir, manifest['module'])
        if not os.path.exists(module_path):
            logger.error(f"Plugin module {module_path} not found")
            return
        
        # Load the module
        spec = importlib.util.spec_from_file_location(plugin_name, module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, BasePlugin) and obj != BasePlugin:
                    plugin = obj(plugin_name, manifest.get('version', '1.0.0'))
                    self.add_plugin(plugin)
                    break
    
    def add_plugin(self, plugin: BasePlugin):
        """Add a plugin.
        
        Args:
            plugin: Plugin instance.
        """
        self.plugins[plugin.name] = plugin
        if plugin.enabled:
            self.enabled_plugins.add(plugin.name)
        logger.info(f"Added plugin: {plugin.name} v{plugin.version}")
    
    def remove_plugin(self, plugin_name: str):
        """Remove a plugin.
        
        Args:
            plugin_name: Plugin name.
        """
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.cleanup()
            del self.plugins[plugin_name]
            self.enabled_plugins.discard(plugin_name)
            logger.info(f"Removed plugin: {plugin_name}")
    
    def enable_plugin(self, plugin_name: str):
        """Enable a plugin.
        
        Args:
            plugin_name: Plugin name.
        """
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            self.enabled_plugins.add(plugin_name)
            logger.info(f"Enabled plugin: {plugin_name}")
    
    def disable_plugin(self, plugin_name: str):
        """Disable a plugin.
        
        Args:
            plugin_name: Plugin name.
        """
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            self.enabled_plugins.discard(plugin_name)
            logger.info(f"Disabled plugin: {plugin_name}")
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a message through all enabled plugins.
        
        Args:
            message: The message to process.
            context: Optional context information.
            
        Returns:
            Combined results from all plugins.
        """
        results = {}
        
        for plugin_name in self.enabled_plugins:
            plugin = self.plugins[plugin_name]
            try:
                result = plugin.process_message(message, context)
                results[plugin_name] = result
            except Exception as e:
                logger.error(f"Error processing message with plugin {plugin_name}: {e}")
        
        return results
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Process a memory through all enabled plugins.
        
        Args:
            memory: The memory to process.
            
        Returns:
            Processed memory.
        """
        processed_memory = memory.copy()
        
        for plugin_name in self.enabled_plugins:
            plugin = self.plugins[plugin_name]
            try:
                processed_memory = plugin.process_memory(processed_memory)
            except Exception as e:
                logger.error(f"Error processing memory with plugin {plugin_name}: {e}")
        
        return processed_memory
    
    def get_plugins(self) -> Dict[str, BasePlugin]:
        """Get all plugins.
        
        Returns:
            Dictionary of plugin names to plugin instances.
        """
        return self.plugins
    
    def get_enabled_plugins(self) -> List[str]:
        """Get enabled plugin names.
        
        Returns:
            List of enabled plugin names.
        """
        return list(self.enabled_plugins)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get plugin information.
        
        Args:
            plugin_name: Plugin name.
            
        Returns:
            Plugin information or None if not found.
        """
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].get_info()
        return None
    
    def get_all_plugin_info(self) -> List[Dict[str, Any]]:
        """Get information for all plugins.
        
        Returns:
            List of plugin information dictionaries.
        """
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def initialize_plugins(self, config: Dict[str, Any] = None):
        """Initialize all plugins.
        
        Args:
            config: Plugin configuration.
        """
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin_config = config.get(plugin_name, {}) if config else {}
                success = plugin.initialize(plugin_config)
                if success:
                    logger.info(f"Initialized plugin: {plugin_name}")
                else:
                    logger.warning(f"Failed to initialize plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Error initializing plugin {plugin_name}: {e}")
    
    def cleanup(self):
        """Clean up all plugins."""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.cleanup()
                logger.info(f"Cleaned up plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin_name}: {e}")
