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
        
        # Comment in Chinese removedths
        self.preferences_file = os.path.join(self.storage_path, "user_preferences.json")
        self.corrections_file = os.path.join(self.storage_path, "corrections.json")
        self.claude_md_file = os.path.join(self.storage_path, "CLAUDE.md")
        
        # Comment in Chinese removed
        self.preferences = self._load_file(self.preferences_file)
        self.corrections = self._load_file(self.corrections_file)
        
        # Ensure files exist
        if not os.path.exists(self.preferences_file):
            self._save_file(self.preferences_file, self.preferences)
        if not os.path.exists(self.corrections_file):
            self._save_file(self.corrections_file, self.corrections)
        
        # Comment in Chinese removed
        self._init_claude_md()
    
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
            
            # Comment in Chinese removednt
            if 'created_at' not in memory:
                memory['created_at'] = current_time
            memory['updated_at'] = current_time
            memory['last_accessed'] = current_time
            memory['access_count'] = 1
            memory['status'] = 'active'
            
            # Comment in Chinese removed
            if memory_type == 'user_preference':
                # Comment in Chinese removednt
                if 'content' in memory:
                    memory['content'] = encryption_manager.encrypt(memory['content'])
                # Ensure both type and memory_type are set
                memory['type'] = 'user_preference'
                memory['memory_type'] = 'user_preference'
                self.preferences.append(memory)
                self._save_file(self.preferences_file, self.preferences)
                self._update_claude_md()
            elif memory_type == 'correction':
                # Comment in Chinese removednt
                if 'content' in memory:
                    memory['content'] = encryption_manager.encrypt(memory['content'])
                # Ensure both type and memory_type are set
                memory['type'] = 'correction'
                memory['memory_type'] = 'correction'
                self.corrections.append(memory)
                self._save_file(self.corrections_file, self.corrections)
                self._update_claude_md()
            else:
                return False
            
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
        
        # Comment in Chinese removedd
        if query:
            filtered_memories = []
            for memory in all_memories:
                # Comment in Chinese removedring
                content = memory.get('content', '')
                try:
                    if content.startswith('gAAAAA'):
                        content = encryption_manager.decrypt(content)
                except Exception as e:
                    logger.error(f"Error decrypting memory: {e}", exc_info=True)
                
                if query.lower() in content.lower():
                    # Comment in Chinese removedrn
                    memory['content'] = content
                    filtered_memories.append(memory)
            all_memories = filtered_memories
        else:
            # Comment in Chinese removedd
            for memory in all_memories:
                content = memory.get('content', '')
                try:
                    if content.startswith('gAAAAA'):
                        memory['content'] = encryption_manager.decrypt(content)
                except Exception as e:
                    logger.error(f"Error decrypting memory: {e}", exc_info=True)
        
        # Comment in Chinese removednt
        for memory in all_memories:
            if 'type' in memory and 'memory_type' not in memory:
                memory['memory_type'] = memory['type']
            elif 'memory_type' in memory and 'type' not in memory:
                memory['type'] = memory['memory_type']
        
        # Comment in Chinese removedirst)
        def get_timestamp(value):
            try:
                from datetime import datetime
                if isinstance(value, str):
                    # Comment in Chinese removed格式的时间字符串
                    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()
                elif isinstance(value, (int, float)):
                    return float(value)
                else:
                    return 0
            except (ValueError, TypeError):
                return 0
        
        all_memories.sort(key=lambda x: get_timestamp(x.get('last_accessed', 0)), reverse=True)
        
        # Comment in Chinese removedlt
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
                    self._update_claude_md()
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
                    self._update_claude_md()
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
            # Comment in Chinese removeds
            for i, memory in enumerate(self.preferences):
                if memory.get('id') == memory_id:
                    del self.preferences[i]
                    self._save_file(self.preferences_file, self.preferences)
                    self._update_claude_md()
                    return True
            
            # Comment in Chinese removedctions
            for i, memory in enumerate(self.corrections):
                if memory.get('id') == memory_id:
                    del self.corrections[i]
                    self._save_file(self.corrections_file, self.corrections)
                    self._update_claude_md()
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
                    # Decrypt content if needed
                    content = memory.get('content', '')
                    try:
                        if content.startswith('gAAAAA'):
                            memory['content'] = encryption_manager.decrypt(content)
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}", exc_info=True)
                    return memory
            
            # Check corrections
            for memory in self.corrections:
                if memory.get('id') == memory_id:
                    # Decrypt content if needed
                    content = memory.get('content', '')
                    try:
                        if content.startswith('gAAAAA'):
                            memory['content'] = encryption_manager.decrypt(content)
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}", exc_info=True)
                    return memory
            
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
