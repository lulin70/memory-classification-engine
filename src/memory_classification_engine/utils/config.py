import os
import logging
import json
from typing import Dict, Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

_logger = logging.getLogger('memory-classification-engine')


class ConfigManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.environ.get('MCE_CONFIG_PATH', '')
        self.config = self.load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.
        
        Args:
            key: The configuration key, using dot notation (e.g., "storage.data_path").
            default: The default value to return if the key is not found.
            
        Returns:
            The configuration value or the default.
        """
        # Comment in Chinese removedirst
        env_key = key.upper().replace('.', '_')
        if f'MCE_{env_key}' in os.environ:
            return os.environ[f'MCE_{env_key}']
        
        # Comment in Chinese removed
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.json'):
                    return json.load(f) or {}
                if YAML_AVAILABLE:
                    return yaml.safe_load(f) or {}
                return json.load(f) or {}
        except Exception as e:
            _logger.debug(f"Config file not found: {self.config_path}")
            return {}
    
    def reload(self):
        """Reload the configuration from file."""
        self.config = self.load_config()
    
    def get_rules(self, rules_path: str = None) -> Dict[str, Any]:
        rules_path = rules_path or self.get('rules.config_path', './config/advanced_rules.json')
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                if rules_path.endswith('.json'):
                    return json.load(f) or {}
                if YAML_AVAILABLE and (rules_path.endswith('.yaml') or rules_path.endswith('.yml')):
                    return yaml.safe_load(f) or {}
                if YAML_AVAILABLE:
                    return yaml.safe_load(f) or {}
                return json.load(f) or {}
        except Exception as e:
            _logger.debug(f"Rules file not found: {rules_path}")
            return {}

    def set(self, key: str, value: Any):
        """Set a configuration value by key.
        
        Args:
            key: The configuration key, using dot notation (e.g., "storage.data_path").
            value: The value to set.
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent level
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
