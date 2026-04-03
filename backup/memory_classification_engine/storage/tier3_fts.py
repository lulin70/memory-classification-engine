import sqlite3
import os
import re
from typing import Dict, List, Optional, Any
from memory_classification_engine.storage.base import BaseStorage
from memory_classification_engine.utils.cache import MemoryCache

class Tier3StorageFTS(BaseStorage):
    def __init__(self, storage_path: str = "./data/tier3", enable_cache: bool = True, cache_size: int = 1000, cache_ttl: int = 3600):
        super().__init__(storage_path)
        self.db_path = os.path.join(storage_path, "episodic_memories.db")
        self.enable_cache = enable_cache
        if enable_cache:
            self.cache = MemoryCache(max_size=cache_size, ttl=cache_ttl)
        self._init_db()
    
    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS episodic_memories (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    memory_type TEXT,
                    content TEXT,
                    confidence REAL,
                    source TEXT,
                    tier INTEGER,
                    created_at TEXT,
                    updated_at TEXT,
                    last_accessed TEXT,
                    access_count INTEGER,
                    status TEXT
                )
            ''')
            
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
                print(f"FTS5 initialization failed (using regular search): {e}")
            
            conn.commit()
            conn.close()
        except Exception as e:
            self._handle_error(e)
    
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        try:
            memory = self._prepare_memory(memory)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO episodic_memories 
                (id, type, memory_type, content, confidence, source, tier, 
                created_at, updated_at, last_accessed, access_count, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory['id'], memory.get('type', ''), memory.get('memory_type', ''),
                memory.get('content', ''), memory.get('confidence', 0.0),
                memory.get('source', ''), memory.get('tier', 3),
                memory['created_at'], memory['updated_at'], memory['last_accessed'],
                memory['access_count'], memory['status']
            ))
            
            conn.commit()
            conn.close()
            
            if self.enable_cache:
                self.cache.set(memory['id'], memory)
            
            return True
        except Exception as e:
            return self._handle_error(e)
    
    def retrieve_memories(self, query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            if not query:
                return self._fallback_retrieve(query, limit)
            
            cache_key = f"search:{query}:{limit}"
            if self.enable_cache and self.cache.exists(cache_key):
                return self.cache.get(cache_key)
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if self._is_english_query(query):
                try:
                    cursor.execute('''
                        SELECT em.*, rank
                        FROM episodic_memories em
                        JOIN episodic_memories_fts fts ON em.rowid = fts.rowid
                        WHERE em.status = 'active' AND fts MATCH ?
                        ORDER BY rank ASC, em.confidence DESC
                        LIMIT ?
                    ''', (query, limit))
                except Exception as e:
                    print(f"FTS5 search failed, falling back to regular search: {e}")
                    return self._fallback_retrieve(query, limit)
            else:
                return self._fallback_retrieve(query, limit)
            
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memory = dict(row)
                if 'rank' in memory:
                    del memory['rank']
                memories.append(memory)
            
            if self.enable_cache:
                self.cache.set(cache_key, memories)
            
            return memories
        except Exception as e:
            self._handle_error(e)
            return self._fallback_retrieve(query, limit)
    
    def _fallback_retrieve(self, query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if query:
                cursor.execute('''
                    SELECT * FROM episodic_memories 
                    WHERE status = 'active' AND content LIKE ? 
                    ORDER BY confidence DESC 
                    LIMIT ?
                ''', (f'%{query}%', limit))
            else:
                cursor.execute('''
                    SELECT * FROM episodic_memories 
                    WHERE status = 'active' 
                    ORDER BY confidence DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memory = dict(row)
                memories.append(memory)
            
            return memories
        except Exception as e:
            self._handle_error(e)
            return []
    
    def _is_english_query(self, query: str) -> bool:
        return bool(re.match(r'^[a-zA-Z\s]+$', query))
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key != 'id':
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if 'updated_at' not in updates:
                set_clauses.append("updated_at = ?")
                values.append(self._get_current_time())
            
            if set_clauses:
                query = f"UPDATE episodic_memories SET {', '.join(set_clauses)} WHERE id = ?"
                values.append(memory_id)
                
                cursor.execute(query, values)
                conn.commit()
                
                result = cursor.rowcount > 0
                
                if result and self.enable_cache:
                    memory = self._get_memory_by_id(memory_id)
                    if memory:
                        self.cache.set(memory_id, memory)
            else:
                result = False
            
            conn.close()
            return result
        except Exception as e:
            return self._handle_error(e)
    
    def delete_memory(self, memory_id: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM episodic_memories WHERE id = ?', (memory_id,))
            conn.commit()
            
            result = cursor.rowcount > 0
            conn.close()
            
            if result and self.enable_cache:
                self.cache.delete(memory_id)
            
            return result
        except Exception as e:
            return self._handle_error(e)
    
    def _get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM episodic_memories WHERE id = ?', (memory_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            self._handle_error(e)
            return None
    
    def warmup_cache(self, limit: int = 100) -> int:
        if not self.enable_cache:
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
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
                self.cache.set(memory['id'], memory)
                count += 1
            
            return count
        except Exception as e:
            self._handle_error(e)
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        if not self.enable_cache:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "size": self.cache.size(),
            "max_size": self.cache.max_size,
            "expired_items": self.cache.expired_count,
            "ttl": self.cache.ttl,
            "warmup_completed": True
        }
    
    def invalidate_cache(self, memory_id: Optional[str] = None) -> bool:
        if not self.enable_cache:
            return False
        
        try:
            if memory_id:
                self.cache.delete(memory_id)
            else:
                self.cache.clear()
            return True
        except Exception as e:
            return self._handle_error(e)
