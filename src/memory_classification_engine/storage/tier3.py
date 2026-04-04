import os
import sqlite3
import re
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.helpers import get_current_time
from memory_classification_engine.utils.logger import logger

# Try to import vector search dependencies
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    import faiss
    VECTOR_SEARCH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Vector search dependencies not available: {e}")
    VECTOR_SEARCH_AVAILABLE = False

class Tier3Storage:
    """Storage for episodic memory (tier 3)."""
    
    def __init__(self, storage_path: str = "./data/tier3", enable_cache: bool = True, cache_size: int = 1000, cache_ttl: int = 3600, enable_vector_search: bool = True):
        """Initialize tier 3 storage.
        
        Args:
            storage_path: Path to store tier 3 memory database.
            enable_cache: Whether to enable cache.
            cache_size: Maximum cache size.
            cache_ttl: Cache time-to-live in seconds.
            enable_vector_search: Whether to enable vector search.
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Database path
        self.db_path = os.path.join(self.storage_path, "episodic_memories.db")
        
        # Cache settings
        self.enable_cache = enable_cache
        if enable_cache:
            from memory_classification_engine.utils.cache import MemoryCache
            self.cache = MemoryCache(max_size=cache_size, ttl=cache_ttl)
        
        # Vector search settings
        self.enable_vector_search = enable_vector_search and VECTOR_SEARCH_AVAILABLE
        if self.enable_vector_search:
            # Initialize TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            # Initialize FAISS index
            self.index = None
            self.memory_ids = []
            self._init_vector_index()
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create episodic memories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS episodic_memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    memory_type TEXT,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    confidence REAL NOT NULL,
                    source TEXT NOT NULL,
                    context TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Create index on type and status
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type_status ON episodic_memories (type, status)')
            
            # Create index on last_accessed
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON episodic_memories (last_accessed)')
            
            # Create FTS5 virtual table for full-text search
            try:
                cursor.execute('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS episodic_memories_fts USING fts5(
                        content,
                        content_rowid=rowid,
                        content=episodic_memories
                    )
                ''')
                
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS episodic_memories_ai AFTER INSERT ON episodic_memories BEGIN
                        INSERT INTO episodic_memories_fts(rowid, content) VALUES (new.rowid, new.content);
                    END
                ''')
                
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS episodic_memories_ad AFTER DELETE ON episodic_memories BEGIN
                        INSERT INTO episodic_memories_fts(episodic_memories_fts, rowid, content) VALUES('delete', old.rowid, old.content);
                    END
                ''')
                
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS episodic_memories_au AFTER UPDATE ON episodic_memories BEGIN
                        INSERT INTO episodic_memories_fts(episodic_memories_fts, rowid, content) VALUES('delete', old.rowid, old.content);
                        INSERT INTO episodic_memories_fts(rowid, content) VALUES (new.rowid, new.content);
                    END
                ''')
            except Exception as e:
                logger.warning(f"FTS5 initialization failed (using regular search): {e}")
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
    
    def _init_vector_index(self):
        """Initialize vector index from existing memories."""
        if not self.enable_vector_search:
            return
        
        try:
            # Get all active memories
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, content FROM episodic_memories WHERE status = ?', ('active',))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                # No memories to index
                self.index = None
                self.memory_ids = []
                return
            
            # Extract content and IDs
            contents = [row['content'] for row in rows]
            self.memory_ids = [row['id'] for row in rows]
            
            # Create TF-IDF vectors
            vectors = self.vectorizer.fit_transform(contents).toarray().astype('float32')
            
            # Create FAISS index
            dimension = vectors.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(vectors)
            
            logger.info(f"Vector index initialized with {len(self.memory_ids)} memories")
        except Exception as e:
            logger.error(f"Error initializing vector index: {e}", exc_info=True)
            self.enable_vector_search = False
    
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        """Store a memory in tier 3.
        
        Args:
            memory: The memory to store.
            
        Returns:
            True if the memory was stored successfully, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = get_current_time()
            
            # Add timestamps if not present
            if 'created_at' not in memory:
                memory['created_at'] = current_time
            memory['updated_at'] = current_time
            memory['last_accessed'] = current_time
            memory['access_count'] = 1
            memory['status'] = 'active'
            
            # Ensure memory_type field is present
            if 'memory_type' not in memory and 'type' in memory:
                memory['memory_type'] = memory['type']
            
            # Insert memory
            cursor.execute('''
                INSERT INTO episodic_memories 
                (id, type, memory_type, content, created_at, updated_at, last_accessed, access_count, confidence, source, context, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.get('id'),
                memory.get('type'),
                memory.get('memory_type'),
                memory.get('content'),
                memory.get('created_at'),
                memory.get('updated_at'),
                memory.get('last_accessed'),
                memory.get('access_count'),
                memory.get('confidence'),
                memory.get('source'),
                memory.get('context'),
                memory.get('status')
            ))
            
            conn.commit()
            conn.close()
            
            # Update cache
            if self.enable_cache and hasattr(self, 'cache') and memory.get('id'):
                self.cache.set(memory['id'], memory)
            
            # Update vector index
            if self.enable_vector_search and memory.get('id') and memory.get('content'):
                self._update_vector_index(memory)
            
            return True
        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
            return False
    
    def retrieve_memories(self, query: str = None, limit: int = 10, use_vector_search: bool = False) -> List[Dict[str, Any]]:
        """Retrieve memories from tier 3.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            use_vector_search: Whether to use vector search instead of FTS5.
            
        Returns:
            A list of matching memories.
        """
        try:
            if not query:
                return self._fallback_retrieve(query, limit)
            
            # Check cache
            cache_key = f"search:{query}:{limit}:{use_vector_search}"
            if self.enable_cache and hasattr(self, 'cache') and self.cache.exists(cache_key):
                return self.cache.get(cache_key)
            
            # Use vector search if requested and enabled
            if use_vector_search and self.enable_vector_search:
                vector_results = self._vector_search(query, limit)
                if vector_results:
                    # Update cache
                    if self.enable_cache and hasattr(self, 'cache'):
                        self.cache.set(cache_key, vector_results)
                    return vector_results
            
            # Fall back to FTS5 or regular search
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if self._is_english_query(query):
                try:
                    # Use FTS5 for English queries
                    cursor.execute('''
                        SELECT em.*, episodic_memories_fts.rank
                        FROM episodic_memories em
                        JOIN episodic_memories_fts ON em.rowid = episodic_memories_fts.rowid
                        WHERE em.status = 'active' AND episodic_memories_fts MATCH ?
                        ORDER BY episodic_memories_fts.rank ASC, em.confidence DESC
                        LIMIT ?
                    ''', (query, limit))
                except Exception as e:
                    logger.warning(f"FTS5 search failed, falling back to regular search: {e}")
                    return self._fallback_retrieve(query, limit)
            else:
                # Fallback to regular search for non-English queries
                return self._fallback_retrieve(query, limit)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert rows to dictionaries
            memories = []
            for row in rows:
                memory = dict(row)
                if 'rank' in memory:
                    del memory['rank']
                # Ensure memory_type field is present
                if 'type' in memory and 'memory_type' not in memory:
                    memory['memory_type'] = memory['type']
                memories.append(memory)
            
            # Update cache
            if self.enable_cache and hasattr(self, 'cache'):
                self.cache.set(cache_key, memories)
            
            return memories
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}", exc_info=True)
            return self._fallback_retrieve(query, limit)
    
    def _vector_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories using vector similarity.
        
        Args:
            query: Query string to search for.
            limit: Maximum number of memories to return.
            
        Returns:
            A list of matching memories sorted by similarity.
        """
        if not self.enable_vector_search or self.index is None:
            return []
        
        try:
            # Create vector for the query
            try:
                query_vector = self.vectorizer.transform([query]).toarray().astype('float32')
            except Exception as e:
                # If vectorizer hasn't been fit yet, return empty list
                logger.error(f"Error creating query vector: {e}")
                return []
            
            # Search FAISS index
            distances, indices = self.index.search(query_vector, limit)
            
            # Get memory IDs from indices
            matched_memory_ids = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx < len(self.memory_ids):
                    matched_memory_ids.append(self.memory_ids[idx])
            
            if not matched_memory_ids:
                return []
            
            # Get memories from database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create placeholders for SQL query
            placeholders = ','.join(['?'] * len(matched_memory_ids))
            cursor.execute(f'''
                SELECT * FROM episodic_memories 
                WHERE status = 'active' AND id IN ({placeholders})
                ORDER BY instr(',{','.join(matched_memory_ids)},', ',' || id || ',')
            ''', matched_memory_ids)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert rows to dictionaries
            memories = []
            for row in rows:
                memory = dict(row)
                # Ensure memory_type field is present
                if 'type' in memory and 'memory_type' not in memory:
                    memory['memory_type'] = memory['type']
                memories.append(memory)
            
            return memories
        except Exception as e:
            logger.error(f"Error in vector search: {e}", exc_info=True)
            return []
    
    def _fallback_retrieve(self, query: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Fallback retrieve method using regular SQL LIKE search.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            
        Returns:
            A list of matching memories.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if query:
                # Search for query in content
                cursor.execute('''
                    SELECT * FROM episodic_memories 
                    WHERE status = 'active' AND content LIKE ? 
                    ORDER BY last_accessed DESC 
                    LIMIT ?
                ''', (f'%{query}%', limit))
            else:
                # Get all active memories
                cursor.execute('''
                    SELECT * FROM episodic_memories 
                    WHERE status = 'active' 
                    ORDER BY last_accessed DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert rows to dictionaries
            memories = []
            for row in rows:
                memory = dict(row)
                # Ensure memory_type field is present
                if 'type' in memory and 'memory_type' not in memory:
                    memory['memory_type'] = memory['type']
                memories.append(memory)
            
            return memories
        except Exception as e:
            logger.error(f"Error in fallback retrieve: {e}", exc_info=True)
            return []
    
    def _is_english_query(self, query: str) -> bool:
        """Check if a query is English-only.
        
        Args:
            query: The query string to check.
            
        Returns:
            True if the query is English-only, False otherwise.
        """
        return bool(re.match(r'^[a-zA-Z\s]+$', query))
    
    def _update_vector_index(self, memory: Dict[str, Any]):
        """Update vector index with a new memory.
        
        Args:
            memory: The memory to add to the vector index.
        """
        if not self.enable_vector_search:
            return
        
        try:
            content = memory.get('content', '')
            memory_id = memory.get('id', '')
            
            if not content or not memory_id:
                return
            
            # Check if memory already exists in index
            if memory_id in self.memory_ids:
                return
            
            # Create vector for the new memory
            try:
                vector = self.vectorizer.transform([content]).toarray().astype('float32')
            except Exception as e:
                # If vectorizer hasn't been fit yet, fit it with this content
                self.vectorizer.fit([content])
                vector = self.vectorizer.transform([content]).toarray().astype('float32')
            
            # Create or update FAISS index
            if self.index is None:
                dimension = vector.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
            
            # Add vector to index
            self.index.add(vector)
            self.memory_ids.append(memory_id)
            
            logger.debug(f"Added memory {memory_id} to vector index")
        except Exception as e:
            logger.error(f"Error updating vector index: {e}", exc_info=True)
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory in tier 3.
        
        Args:
            memory_id: The ID of the memory to update.
            updates: The updates to apply.
            
        Returns:
            True if the memory was updated successfully, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query
            set_clause = []
            params = []
            
            for key, value in updates.items():
                set_clause.append(f"{key} = ?")
                params.append(value)
            
            # Always update the updated_at timestamp
            set_clause.append("updated_at = ?")
            params.append(get_current_time())
            
            # Add memory_id to params
            params.append(memory_id)
            
            # Execute update
            cursor.execute(f'''
                UPDATE episodic_memories 
                SET {', '.join(set_clause)} 
                WHERE id = ?
            ''', params)
            
            conn.commit()
            conn.close()
            
            result = cursor.rowcount > 0
            
            # Update cache
            if result and self.enable_cache and hasattr(self, 'cache'):
                # Invalidate cache for this memory
                self.cache.delete(memory_id)
                # Also invalidate search caches
                self._invalidate_search_caches()
            
            # Update vector index if content changed
            if result and self.enable_vector_search and 'content' in updates:
                # Rebuild vector index
                self._init_vector_index()
            
            return result
        except Exception as e:
            logger.error(f"Error updating memory: {e}", exc_info=True)
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory from tier 3.
        
        Args:
            memory_id: The ID of the memory to delete.
            
        Returns:
            True if the memory was deleted successfully, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Soft delete by setting status to 'deleted'
            cursor.execute('''
                UPDATE episodic_memories 
                SET status = 'deleted', updated_at = ? 
                WHERE id = ?
            ''', (get_current_time(), memory_id))
            
            conn.commit()
            conn.close()
            
            result = cursor.rowcount > 0
            
            # Update cache
            if result and self.enable_cache and hasattr(self, 'cache'):
                # Invalidate cache for this memory
                self.cache.delete(memory_id)
                # Also invalidate search caches
                self._invalidate_search_caches()
            
            # Update vector index
            if result and self.enable_vector_search:
                # Rebuild vector index
                self._init_vector_index()
            
            return result
        except Exception as e:
            logger.error(f"Error deleting memory: {e}", exc_info=True)
            return False
    
    def _invalidate_search_caches(self):
        """Invalidate all search-related caches."""
        if self.enable_cache and hasattr(self, 'cache'):
            # Invalidate all search caches
            keys_to_delete = []
            for key in self.cache.cache:
                if key.startswith('search:'):
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                self.cache.delete(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tier 3 storage.
        
        Returns:
            A dictionary with statistics.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total memories
            cursor.execute('SELECT COUNT(*) FROM episodic_memories')
            total = cursor.fetchone()[0]
            
            # Get active memories
            cursor.execute('SELECT COUNT(*) FROM episodic_memories WHERE status = ?', ('active',))
            active = cursor.fetchone()[0]
            
            # Get memory types
            cursor.execute('SELECT type, COUNT(*) FROM episodic_memories WHERE status = ? GROUP BY type', ('active',))
            types = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            stats = {
                'total_memories': total,
                'active_memories': active,
                'memory_types': types
            }
            
            # Add cache stats if enabled
            if self.enable_cache and hasattr(self, 'cache'):
                stats['cache'] = self.get_cache_stats()
            
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {
                'total_memories': 0,
                'active_memories': 0,
                'memory_types': {}
            }
    
    def warmup_cache(self, limit: int = 100) -> int:
        """Warm up the cache with frequently accessed memories.
        
        Args:
            limit: Maximum number of memories to warm up.
            
        Returns:
            Number of memories loaded into cache.
        """
        if not self.enable_cache or not hasattr(self, 'cache'):
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get most frequently accessed memories
            cursor.execute('''
                SELECT * FROM episodic_memories 
                WHERE status = 'active' 
                ORDER BY access_count DESC, updated_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            count = 0
            for row in rows:
                memory = dict(row)
                # Ensure memory_type field is present
                if 'type' in memory and 'memory_type' not in memory:
                    memory['memory_type'] = memory['type']
                self.cache.set(memory['id'], memory)
                count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error warming up cache: {e}", exc_info=True)
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            A dictionary with cache statistics.
        """
        if not self.enable_cache or not hasattr(self, 'cache'):
            return {"enabled": False}
        
        return {
            "enabled": True,
            "size": self.cache.size(),
            "max_size": self.cache.max_size,
            "expired_items": getattr(self.cache, 'expired_count', 0),
            "ttl": self.cache.ttl,
            "warmup_completed": True
        }
    
    def invalidate_cache(self, memory_id: Optional[str] = None) -> bool:
        """Invalidate cache for a specific memory or all caches.
        
        Args:
            memory_id: Optional memory ID to invalidate. If None, invalidate all caches.
            
        Returns:
            True if cache was invalidated successfully, False otherwise.
        """
        if not self.enable_cache or not hasattr(self, 'cache'):
            return False
        
        try:
            if memory_id:
                self.cache.delete(memory_id)
            else:
                self.cache.clear()
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}", exc_info=True)
            return False
