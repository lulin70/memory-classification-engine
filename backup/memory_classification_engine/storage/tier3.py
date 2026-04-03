import sqlite3
import os
from typing import Dict, List, Optional, Any
from memory_classification_engine.storage.base import BaseStorage

class Tier3Storage(BaseStorage):
    def __init__(self, storage_path: str = "./data/tier3"):
        super().__init__(storage_path)
        self.db_path = os.path.join(storage_path, "episodic_memories.db")
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
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON episodic_memories(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON episodic_memories(status)')
            
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
            return True
        except Exception as e:
            return self._handle_error(e)
    
    def retrieve_memories(self, query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
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
            return result
        except Exception as e:
            return self._handle_error(e)
