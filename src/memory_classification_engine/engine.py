import os
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.helpers import generate_memory_id, get_current_time
from memory_classification_engine.layers.rule_matcher import RuleMatcher
from memory_classification_engine.layers.pattern_analyzer import PatternAnalyzer
from memory_classification_engine.layers.semantic_classifier import SemanticClassifier
from memory_classification_engine.storage.tier2 import Tier2Storage
from memory_classification_engine.storage.tier3 import Tier3Storage
from memory_classification_engine.storage.tier4 import Tier4Storage

class MemoryClassificationEngine:
    """Memory Classification Engine."""
    
    def __init__(self, config_path: str = None):
        """Initialize the memory classification engine.
        
        Args:
            config_path: Path to the configuration file.
        """
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Initialize storage
        storage_path = self.config.get('storage.data_path', './data')
        os.makedirs(storage_path, exist_ok=True)
        
        self.tier2_storage = Tier2Storage(self.config.get('storage.tier2_path', './data/tier2'))
        self.tier3_storage = Tier3Storage(self.config.get('storage.tier3_path', './data/tier3'))
        self.tier4_storage = Tier4Storage(self.config.get('storage.tier4_path', './data/tier4'))
        
        # Initialize working memory
        self.working_memory = []
        self.max_work_memory_size = self.config.get('storage.max_work_memory_size', 100)
        
        # Initialize layers
        rules = self.config.get_rules().get('rules', [])
        self.rule_matcher = RuleMatcher(rules)
        self.pattern_analyzer = PatternAnalyzer()
        
        llm_enabled = self.config.get('llm.enabled', False)
        api_key = self.config.get('llm.api_key', '')
        self.semantic_classifier = SemanticClassifier(llm_enabled, api_key)
        
        # Initialize memory management
        self.forgetting_enabled = self.config.get('memory.forgetting.enabled', True)
        self.decay_factor = self.config.get('memory.forgetting.decay_factor', 0.9)
        self.min_weight = self.config.get('memory.forgetting.min_weight', 0.1)
        
        self.deduplication_enabled = self.config.get('memory.deduplication.enabled', True)
        self.similarity_threshold = self.config.get('memory.deduplication.similarity_threshold', 0.8)
        
        self.conflict_resolution_strategy = self.config.get('memory.conflict_resolution.strategy', 'latest')
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and classify memory.
        
        Args:
            message: The message to process.
            context: Optional context for the message.
            
        Returns:
            A dictionary containing the classification results.
        """
        # Step 1: Add message to working memory
        self._add_to_working_memory(message)
        
        # Step 2: Apply layers in order
        # Layer 1: Rule matching
        rule_matches = self.rule_matcher.match(message, context)
        
        # Layer 2: Pattern analysis
        pattern_matches = self.pattern_analyzer.analyze(message, context)
        
        # Layer 3: Semantic classification
        semantic_matches = self.semantic_classifier.classify(message, context)
        
        # Step 3: Combine results
        all_matches = rule_matches + pattern_matches + semantic_matches
        
        # Step 4: Deduplicate and resolve conflicts
        unique_matches = self._deduplicate_matches(all_matches)
        
        # Step 5: Store memories
        stored_memories = []
        for match in unique_matches:
            # Generate memory ID
            memory_id = generate_memory_id()
            match['id'] = memory_id
            
            # Add context if provided
            if context:
                match['context'] = context.get('conversation_id', '')
            
            # Rename memory_type to type for storage compatibility
            if 'memory_type' in match:
                match['type'] = match['memory_type']
            # Also keep memory_type for compatibility with retrieval
            if 'type' in match and 'memory_type' not in match:
                match['memory_type'] = match['type']
            
            # Store based on tier
            if match.get('tier') == 2:
                self.tier2_storage.store_memory(match)
            elif match.get('tier') == 3:
                self.tier3_storage.store_memory(match)
            elif match.get('tier') == 4:
                self.tier4_storage.store_memory(match)
            
            stored_memories.append(match)
        
        return {
            'message': message,
            'matches': stored_memories,
            'working_memory_size': len(self.working_memory)
        }
    
    def retrieve_memories(self, query: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories based on query.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            
        Returns:
            A list of matching memories.
        """
        # Retrieve from all tiers
        tier2_memories = self.tier2_storage.retrieve_memories(query, limit)
        tier3_memories = self.tier3_storage.retrieve_memories(query, limit)
        tier4_memories = self.tier4_storage.retrieve_memories(query, limit)
        
        # Combine and sort by confidence
        all_memories = tier2_memories + tier3_memories + tier4_memories
        all_memories.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Limit the result
        return all_memories[:limit]
    
    def manage_memory(self, action: str, memory_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage memory (view, edit, delete).
        
        Args:
            action: The action to perform (view, edit, delete).
            memory_id: The ID of the memory to manage.
            data: Optional data for editing.
            
        Returns:
            A dictionary containing the result.
        """
        # Try to find the memory in all tiers
        memory = None
        storage = None
        
        # Check tier 2
        tier2_memories = self.tier2_storage.retrieve_memories()
        for m in tier2_memories:
            if m.get('id') == memory_id:
                memory = m
                storage = self.tier2_storage
                break
        
        # Check tier 3
        if not memory:
            tier3_memories = self.tier3_storage.retrieve_memories()
            for m in tier3_memories:
                if m.get('id') == memory_id:
                    memory = m
                    storage = self.tier3_storage
                    break
        
        # Check tier 4
        if not memory:
            tier4_memories = self.tier4_storage.retrieve_memories()
            for m in tier4_memories:
                if m.get('id') == memory_id:
                    memory = m
                    storage = self.tier4_storage
                    break
        
        if not memory:
            return {'success': False, 'message': 'Memory not found'}
        
        if action == 'view':
            return {'success': True, 'memory': memory}
        
        elif action == 'edit':
            if data and storage:
                success = storage.update_memory(memory_id, data)
                if success:
                    # Get updated memory
                    updated_memory = None
                    if storage == self.tier2_storage:
                        for m in self.tier2_storage.retrieve_memories():
                            if m.get('id') == memory_id:
                                updated_memory = m
                                break
                    elif storage == self.tier3_storage:
                        for m in self.tier3_storage.retrieve_memories():
                            if m.get('id') == memory_id:
                                updated_memory = m
                                break
                    elif storage == self.tier4_storage:
                        for m in self.tier4_storage.retrieve_memories():
                            if m.get('id') == memory_id:
                                updated_memory = m
                                break
                    return {'success': True, 'memory': updated_memory}
            return {'success': False, 'message': 'Failed to update memory'}
        
        elif action == 'delete':
            if storage:
                success = storage.delete_memory(memory_id)
                return {'success': success, 'message': 'Memory deleted' if success else 'Failed to delete memory'}
        
        return {'success': False, 'message': 'Invalid action'}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the engine.
        
        Returns:
            A dictionary with statistics.
        """
        tier2_stats = self.tier2_storage.get_stats()
        tier3_stats = self.tier3_storage.get_stats()
        tier4_stats = self.tier4_storage.get_stats()
        
        return {
            'working_memory_size': len(self.working_memory),
            'tier2': tier2_stats,
            'tier3': tier3_stats,
            'tier4': tier4_stats,
            'total_memories': (
                tier2_stats.get('total_memories', 0) +
                tier3_stats.get('total_memories', 0) +
                tier4_stats.get('total_relationships', 0)
            )
        }
    
    def export_memories(self, format: str = "json") -> Dict[str, Any]:
        """Export memories.
        
        Args:
            format: Export format (json).
            
        Returns:
            A dictionary containing the exported memories.
        """
        tier2_memories = self.tier2_storage.retrieve_memories(limit=1000)
        tier3_memories = self.tier3_storage.retrieve_memories(limit=1000)
        tier4_memories = self.tier4_storage.retrieve_memories(limit=1000)
        
        if format == "json":
            return {
                'tier2': tier2_memories,
                'tier3': tier3_memories,
                'tier4': tier4_memories
            }
        
        return {'error': 'Unsupported format'}
    
    def import_memories(self, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        """Import memories.
        
        Args:
            data: The data to import.
            format: Import format (json).
            
        Returns:
            A dictionary containing the import result.
        """
        if format != "json":
            return {'error': 'Unsupported format'}
        
        imported_count = 0
        
        # Import tier 2 memories
        for memory in data.get('tier2', []):
            if self.tier2_storage.store_memory(memory):
                imported_count += 1
        
        # Import tier 3 memories
        for memory in data.get('tier3', []):
            if self.tier3_storage.store_memory(memory):
                imported_count += 1
        
        # Import tier 4 memories
        for memory in data.get('tier4', []):
            if self.tier4_storage.store_memory(memory):
                imported_count += 1
        
        return {'success': True, 'imported_count': imported_count}
    
    def _add_to_working_memory(self, message: str):
        """Add a message to working memory.
        
        Args:
            message: The message to add.
        """
        self.working_memory.append({
            'message': message,
            'timestamp': get_current_time()
        })
        
        # Limit working memory size
        if len(self.working_memory) > self.max_work_memory_size:
            self.working_memory.pop(0)
    
    def _deduplicate_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate matches.
        
        Args:
            matches: List of matches to deduplicate.
            
        Returns:
            List of unique matches.
        """
        if not self.deduplication_enabled:
            return matches
        
        unique_matches = []
        seen_contents = set()
        
        for match in matches:
            content = match.get('content', '').strip()
            if content not in seen_contents:
                seen_contents.add(content)
                unique_matches.append(match)
        
        return unique_matches
    
    def clear_working_memory(self):
        """Clear working memory."""
        self.working_memory = []
    
    def reload_config(self):
        """Reload configuration."""
        self.config.reload()
        
        # Update storage paths if changed
        tier2_path = self.config.get('storage.tier2_path', './data/tier2')
        tier3_path = self.config.get('storage.tier3_path', './data/tier3')
        tier4_path = self.config.get('storage.tier4_path', './data/tier4')
        
        self.tier2_storage = Tier2Storage(tier2_path)
        self.tier3_storage = Tier3Storage(tier3_path)
        self.tier4_storage = Tier4Storage(tier4_path)
        
        # Update rules
        rules = self.config.get_rules().get('rules', [])
        self.rule_matcher = RuleMatcher(rules)
        
        # Update LLM settings
        llm_enabled = self.config.get('llm.enabled', False)
        api_key = self.config.get('llm.api_key', '')
        self.semantic_classifier = SemanticClassifier(llm_enabled, api_key)
