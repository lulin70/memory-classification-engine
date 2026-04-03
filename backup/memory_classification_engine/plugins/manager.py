import os
import importlib
from typing import Dict, List, Optional, Any
from memory_classification_engine.plugins.base import Plugin

class PluginManager:
    def __init__(self, plugins_dir: str = "./plugins"):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, Plugin] = {}
        self.loaded_plugins: List[str] = []
    
    def load_plugin(self, plugin_name: str) -> bool:
        try:
            module_path = f"memory_classification_engine.plugins.plugins.{plugin_name}"
            module = importlib.import_module(module_path)
            
            plugin_class = getattr(module, f"{plugin_name.capitalize()}Plugin")
            plugin = plugin_class(plugin_name)
            
            if plugin.initialize():
                self.plugins[plugin_name] = plugin
                self.loaded_plugins.append(plugin_name)
                return True
            return False
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> List[str]:
        loaded_plugins = []
        plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
        
        if os.path.exists(plugins_dir):
            for file in os.listdir(plugins_dir):
                if file.endswith(".py") and file != "__init__.py":
                    plugin_name = file[:-3]
                    if self.load_plugin(plugin_name):
                        loaded_plugins.append(plugin_name)
        
        return loaded_plugins
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        results = {}
        for plugin_name, plugin in self.plugins.items():
            try:
                result = plugin.process_message(message, context)
                results[plugin_name] = result
            except Exception as e:
                print(f"Error processing message with plugin {plugin_name}: {e}")
                results[plugin_name] = {"error": str(e)}
        return results
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        processed_memory = memory.copy()
        for plugin_name, plugin in self.plugins.items():
            try:
                processed_memory = plugin.process_memory(processed_memory)
            except Exception as e:
                print(f"Error processing memory with plugin {plugin_name}: {e}")
        return processed_memory
    
    def unload_plugin(self, plugin_name: str) -> bool:
        if plugin_name in self.plugins:
            try:
                plugin = self.plugins[plugin_name]
                plugin.cleanup()
                del self.plugins[plugin_name]
                self.loaded_plugins.remove(plugin_name)
                return True
            except Exception as e:
                print(f"Failed to unload plugin {plugin_name}: {e}")
                return False
        return False
    
    def get_loaded_plugins(self) -> List[str]:
        return self.loaded_plugins
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        return self.plugins.get(plugin_name)
