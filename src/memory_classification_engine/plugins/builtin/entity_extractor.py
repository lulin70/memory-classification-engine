"""Entity extractor plugin."""

import re
from typing import Dict, List, Optional, Any
from memory_classification_engine.plugins.base_plugin import BasePlugin


class EntityExtractorPlugin(BasePlugin):
    """Entity extractor plugin."""
    
    def __init__(self):
        """Initialize the entity extractor plugin."""
        super().__init__("entity_extractor", "1.0.0")
        # Common words to exclude from person names
        self.common_words = {'The', 'And', 'But', 'For', 'Are', 'Use', 'Works', 'Uses', 'At'}
    
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the plugin.
        
        Args:
            config: Plugin configuration.
            
        Returns:
            True if initialization was successful, False otherwise.
        """
        if config:
            if 'common_words' in config:
                self.common_words.update(config['common_words'])
        return True
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a message.
        
        Args:
            message: The message to process.
            context: Optional context information.
            
        Returns:
            Entity extraction result.
        """
        entities = self._extract_entities(message)
        return {
            'entities': entities,
            'entity_count': len(entities)
        }
    
    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Process a memory.
        
        Args:
            memory: The memory to process.
            
        Returns:
            Memory with entity information.
        """
        if 'content' in memory:
            entities = self._extract_entities(memory['content'])
            if entities:
                memory['entities'] = entities
        return memory
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text.
        
        Args:
            text: Text to extract entities from.
            
        Returns:
            List of extracted entities.
        """
        entities = []
        
        # Extract potential organizations first (capitalized words after "at", "in", "from", "by")
        org_pattern_with_prep = r'\b(at|in|from|for|by)\s+([A-Z][a-zA-Z]+)\b'
        org_matches = re.findall(org_pattern_with_prep, text, re.IGNORECASE)
        
        for prep, org in org_matches:
            if len(org) > 2:
                entities.append({
                    'text': org,
                    'type': 'organization',
                    'confidence': 0.7
                })
        
        # Extract potential names (capitalized words in English)
        name_pattern = r'\b[A-Z][a-z]+\b'
        potential_names = re.findall(name_pattern, text)
        
        for name in potential_names:
            if len(name) > 2 and name not in self.common_words:
                # Check if not already added as organization
                if not any(e['text'] == name and e['type'] == 'organization' for e in entities):
                    entities.append({
                        'text': name,
                        'type': 'person',
                        'confidence': 0.6
                    })
        
        # Also extract all caps as organizations
        org_pattern_caps = r'\b[A-Z]{2,}\b'
        potential_orgs = re.findall(org_pattern_caps, text)
        
        for org in potential_orgs:
            # Check if not already added
            if not any(e['text'] == org for e in entities):
                entities.append({
                    'text': org,
                    'type': 'organization',
                    'confidence': 0.5
                })
        
        return entities
