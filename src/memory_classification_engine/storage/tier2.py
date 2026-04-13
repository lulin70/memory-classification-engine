import os
import json
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.helpers import get_current_time, format_memory
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.encryption import encryption_manager

class Tier2Storage:
    """Storage for procedural memory (tier 2)."""
    
    def __init__(self, storage_path: str = "./data/tier2"):
        """Initialize tier 2 storage.
        
        Args:
            storage_path: Path to store tier 2 memory files.
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # File paths
        self.preferences_file = os.path.join(self.storage_path, "user_preferences.json")
        self.corrections_file = os.path.join(self.storage_path, "corrections.json")
        self.claude_md_file = os.path.join(self.storage_path, "CLAUDE.md")
        
        # Load data from files
        self.preferences = self._load_file(self.preferences_file)
        self.corrections = self._load_file(self.corrections_file)
        
        # Memory cache for decrypted content
        self.cache = {}
        self.cache_size = 1000  # Max cache size
        
        # Ensure files exist
        if not os.path.exists(self.preferences_file):
            self._save_file(self.preferences_file, self.preferences)
        if not os.path.exists(self.corrections_file):
            self._save_file(self.corrections_file, self.corrections)
        
        # Initialize CLAUDE.md
        self._init_claude_md()
        
        # Batch update flag for CLAUDE.md
        self.pending_claude_update = False
    
    def _load_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            The loaded data as a list of dictionaries.
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}", exc_info=True)
        return []
    
    def _save_file(self, file_path: str, data: List[Dict[str, Any]]):
        """Save data to file.
        
        Args:
            file_path: Path to the file.
            data: The data to save.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}", exc_info=True)
    
    def _update_cache(self, memory_id: str, content: str):
        """Update cache with decrypted content.
        
        Args:
            memory_id: Memory ID.
            content: Decrypted content.
        """
        # Update cache
        self.cache[memory_id] = content
        # Limit cache size
        if len(self.cache) > self.cache_size:
            # Remove oldest item (FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    def _get_cached_content(self, memory_id: str) -> Optional[str]:
        """Get cached decrypted content.
        
        Args:
            memory_id: Memory ID.
            
        Returns:
            Decrypted content if cached, None otherwise.
        """
        return self.cache.get(memory_id)
    
    def _batch_update_claude_md(self):
        """Batch update CLAUDE.md file with current memories.
        This reduces the number of file writes.
        """
        if not self.pending_claude_update:
            return
        
        try:
            with open(self.claude_md_file, 'w', encoding='utf-8') as f:
                f.write("# Memory Summary\n")
                
                # Write preferences
                f.write("\n# User Preferences\n")
                for memory in self.preferences:
                    content = memory.get('content', '')
                    try:
                        if content.startswith('gAAAAA'):
                            # Check cache first
                            cached_content = self._get_cached_content(memory.get('id'))
                            if cached_content:
                                content = cached_content
                            else:
                                content = encryption_manager.decrypt(content)
                                self._update_cache(memory.get('id'), content)
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}", exc_info=True)
                    f.write(f"- {content}\n")
                
                f.write("\n")
                
                # Write corrections
                f.write("# Corrections\n")
                for memory in self.corrections:
                    content = memory.get('content', '')
                    try:
                        if content.startswith('gAAAAA'):
                            # Check cache first
                            cached_content = self._get_cached_content(memory.get('id'))
                            if cached_content:
                                content = cached_content
                            else:
                                content = encryption_manager.decrypt(content)
                                self._update_cache(memory.get('id'), content)
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}", exc_info=True)
                    f.write(f"- {content}\n")
            # Reset flag
            self.pending_claude_update = False
        except Exception as e:
            logger.error(f"Error updating CLAUDE.md: {e}", exc_info=True)
    
    def _init_claude_md(self):
        """Initialize CLAUDE.md file if it doesn't exist."""
        if not os.path.exists(self.claude_md_file):
            try:
                with open(self.claude_md_file, 'w', encoding='utf-8') as f:
                    f.write("# Comment in Chinese removedn")
                    f.write("# Comment in Chinese removedn")
                    f.write("# Comment in Chinese removedn")
            except Exception as e:
                logger.error(f"Error initializing CLAUDE.md: {e}", exc_info=True)
    
    def _update_claude_md(self):
        """Update CLAUDE.md file with current memories."""
        try:
            with open(self.claude_md_file, 'w', encoding='utf-8') as f:
                f.write("# Comment in Chinese removedn")
                
                # Comment in Chinese removeds
                f.write("# Comment in Chinese removedn")
                for memory in self.preferences:
                    content = memory.get('content', '')
                    try:
                        if content.startswith('gAAAAA'):
                            content = encryption_manager.decrypt(content)
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}", exc_info=True)
                    f.write(f"- {content}\n")
                
                f.write("\n")
                
                # Comment in Chinese removedctions
                f.write("# Comment in Chinese removedn")
                for memory in self.corrections:
                    content = memory.get('content', '')
                    try:
                        if content.startswith('gAAAAA'):
                            content = encryption_manager.decrypt(content)
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}", exc_info=True)
                    f.write(f"- {content}\n")
        except Exception as e:
            logger.error(f"Error updating CLAUDE.md: {e}", exc_info=True)
    
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        """Store a memory in tier 2.
        
        Args:
            memory: The memory to store.
            
        Returns:
            True if the memory was stored successfully, False otherwise.
        """
        try:
            # Get memory type from either 'type' or 'memory_type' field
            memory_type = memory.get('type') or memory.get('memory_type')
            current_time = get_current_time()
            
            # Set default fields if not present
            if 'created_at' not in memory:
                memory['created_at'] = current_time
            memory['updated_at'] = current_time
            memory['last_accessed'] = current_time
            memory['access_count'] = 1
            memory['status'] = 'active'
            
            # Store memory based on type
            if memory_type == 'user_preference':
                # Encrypt content if present
                if 'content' in memory:
                    memory['content'] = encryption_manager.encrypt(memory['content'])
                # Ensure both type and memory_type are set
                memory['type'] = 'user_preference'
                memory['memory_type'] = 'user_preference'
                self.preferences.append(memory)
                self._save_file(self.preferences_file, self.preferences)
                # Mark CLAUDE.md for batch update
                self.pending_claude_update = True
            elif memory_type == 'correction':
                # Encrypt content if present
                if 'content' in memory:
                    memory['content'] = encryption_manager.encrypt(memory['content'])
                # Ensure both type and memory_type are set
                memory['type'] = 'correction'
                memory['memory_type'] = 'correction'
                self.corrections.append(memory)
                self._save_file(self.corrections_file, self.corrections)
                # Mark CLAUDE.md for batch update
                self.pending_claude_update = True
            else:
                return False
            
            # Perform batch update if needed
            if self.pending_claude_update:
                import threading
                threading.Thread(target=self._batch_update_claude_md).start()
            
            return True
        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
            return False
    
    def retrieve_memories(self, query: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve memories from tier 2.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            
        Returns:
            A list of matching memories.
        """
        all_memories = []
        all_memories.extend(self.preferences)
        all_memories.extend(self.corrections)
        
        # Filter memories if query is provided
        if query:
            filtered_memories = []
            for memory in all_memories:
                # Get content for filtering
                content = memory.get('content', '')
                try:
                    if content.startswith('gAAAAA'):
                        # Check cache first
                        cached_content = self._get_cached_content(memory.get('id'))
                        if cached_content:
                            content = cached_content
                        else:
                            content = encryption_manager.decrypt(content)
                            self._update_cache(memory.get('id'), content)
                except Exception as e:
                    logger.error(f"Error decrypting memory: {e}", exc_info=True)
                
                if query.lower() in content.lower():
                    # Use the decrypted content for the returned memory
                    memory_copy = memory.copy()
                    memory_copy['content'] = content
                    filtered_memories.append(memory_copy)
            all_memories = filtered_memories
        else:
            # Decrypt content for all memories
            decrypted_memories = []
            for memory in all_memories:
                memory_copy = memory.copy()
                content = memory_copy.get('content', '')
                try:
                    if content.startswith('gAAAAA'):
                        # Check cache first
                        cached_content = self._get_cached_content(memory_copy.get('id'))
                        if cached_content:
                            content = cached_content
                        else:
                            content = encryption_manager.decrypt(content)
                            self._update_cache(memory_copy.get('id'), content)
                    memory_copy['content'] = content
                except Exception as e:
                    logger.error(f"Error decrypting memory: {e}", exc_info=True)
                decrypted_memories.append(memory_copy)
            all_memories = decrypted_memories
        
        # Ensure both type and memory_type fields are set
        for memory in all_memories:
            if 'type' in memory and 'memory_type' not in memory:
                memory['memory_type'] = memory['type']
            elif 'memory_type' in memory and 'type' not in memory:
                memory['type'] = memory['memory_type']
        
        # Sort by last accessed time (most recent first)
        def get_timestamp(value):
            try:
                from datetime import datetime
                if isinstance(value, str):
                    # Handle ISO format time strings
                    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()
                elif isinstance(value, (int, float)):
                    return float(value)
                else:
                    return 0
            except (ValueError, TypeError):
                return 0
        
        all_memories.sort(key=lambda x: get_timestamp(x.get('last_accessed', 0)), reverse=True)
        
        # Return limited result
        return all_memories[:limit]
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory in tier 2.
        
        Args:
            memory_id: The ID of the memory to update.
            updates: The updates to apply.
            
        Returns:
            True if the memory was updated successfully, False otherwise.
        """
        try:
            # Check preferences
            for i, memory in enumerate(self.preferences):
                if memory.get('id') == memory_id:
                    # Encrypt content if it's being updated
                    if 'content' in updates:
                        updates['content'] = encryption_manager.encrypt(updates['content'])
                    memory.update(updates)
                    memory['updated_at'] = get_current_time()
                    self._save_file(self.preferences_file, self.preferences)
                    # Mark CLAUDE.md for batch update
                    self.pending_claude_update = True
                    # Invalidate cache if content was updated
                    if 'content' in updates:
                        if memory_id in self.cache:
                            del self.cache[memory_id]
                    return True
            
            # Check corrections
            for i, memory in enumerate(self.corrections):
                if memory.get('id') == memory_id:
                    # Encrypt content if it's being updated
                    if 'content' in updates:
                        updates['content'] = encryption_manager.encrypt(updates['content'])
                    memory.update(updates)
                    memory['updated_at'] = get_current_time()
                    self._save_file(self.corrections_file, self.corrections)
                    # Mark CLAUDE.md for batch update
                    self.pending_claude_update = True
                    # Invalidate cache if content was updated
                    if 'content' in updates:
                        if memory_id in self.cache:
                            del self.cache[memory_id]
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error updating memory: {e}", exc_info=True)
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory from tier 2.
        
        Args:
            memory_id: The ID of the memory to delete.
            
        Returns:
            True if the memory was deleted successfully, False otherwise.
        """
        try:
            # Check preferences
            for i, memory in enumerate(self.preferences):
                if memory.get('id') == memory_id:
                    del self.preferences[i]
                    self._save_file(self.preferences_file, self.preferences)
                    # Mark CLAUDE.md for batch update
                    self.pending_claude_update = True
                    # Invalidate cache
                    if memory_id in self.cache:
                        del self.cache[memory_id]
                    return True
            
            # Check corrections
            for i, memory in enumerate(self.corrections):
                if memory.get('id') == memory_id:
                    del self.corrections[i]
                    self._save_file(self.corrections_file, self.corrections)
                    # Mark CLAUDE.md for batch update
                    self.pending_claude_update = True
                    # Invalidate cache
                    if memory_id in self.cache:
                        del self.cache[memory_id]
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting memory: {e}", exc_info=True)
            return False
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory by ID from tier 2.
        
        Args:
            memory_id: The ID of the memory to get.
            
        Returns:
            The memory if found, None otherwise.
        """
        try:
            # Check preferences
            for memory in self.preferences:
                if memory.get('id') == memory_id:
                    memory_copy = memory.copy()
                    # Decrypt content if needed
                    content = memory_copy.get('content', '')
                    try:
                        if content.startswith('gAAAAA'):
                            # Check cache first
                            cached_content = self._get_cached_content(memory_id)
                            if cached_content:
                                memory_copy['content'] = cached_content
                            else:
                                decrypted_content = encryption_manager.decrypt(content)
                                memory_copy['content'] = decrypted_content
                                self._update_cache(memory_id, decrypted_content)
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}", exc_info=True)
                    return memory_copy
            
            # Check corrections
            for memory in self.corrections:
                if memory.get('id') == memory_id:
                    memory_copy = memory.copy()
                    # Decrypt content if needed
                    content = memory_copy.get('content', '')
                    try:
                        if content.startswith('gAAAAA'):
                            # Check cache first
                            cached_content = self._get_cached_content(memory_id)
                            if cached_content:
                                memory_copy['content'] = cached_content
                            else:
                                decrypted_content = encryption_manager.decrypt(content)
                                memory_copy['content'] = decrypted_content
                                self._update_cache(memory_id, decrypted_content)
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}", exc_info=True)
                    return memory_copy
            
            return None
        except Exception as e:
            logger.error(f"Error getting memory: {e}", exc_info=True)
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tier 2 storage.
        
        Returns:
            A dictionary with statistics.
        """
        return {
            'total_preferences': len(self.preferences),
            'total_corrections': len(self.corrections),
            'total_memories': len(self.preferences) + len(self.corrections)
        }
