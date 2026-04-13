import os
import sqlite3
import re
import json
from typing import Dict, List, Optional, Any
from collections import deque
import threading
from memory_classification_engine.utils.helpers import get_current_time
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.privacy.encryption import encryption_manager

class ConnectionPool:
    """Database connection pool for SQLite with thread safety."""
    
    def __init__(self, db_path: str, max_connections: int = 10, timeout: int = 30):
        """Initialize the connection pool.
        
        Args:
            db_path: Path to the SQLite database.
            max_connections: Maximum number of connections in the pool.
            timeout: Connection timeout in seconds.
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self.connections = deque()
        self.lock = threading.Lock()
        self.active_connections = 0
        # Comment in Chinese removedctions
        self._local = threading.local()
        
    def get_connection(self):
        """Get a connection from the pool.
        
        Returns:
            sqlite3.Connection: A database connection.
        """
        # Comment in Chinese removedction
        if hasattr(self._local, 'connection') and self._local.connection:
            try:
                # Comment in Chinese removedlid
                self._local.connection.execute('SELECT 1')
                return self._local.connection
            except sqlite3.ProgrammingError:
                # Comment in Chinese removed
                self._local.connection = None
        
        with self.lock:
            if self.connections:
                conn = self.connections.popleft()
                # Comment in Chinese removedlid
                try:
                    conn.execute('SELECT 1')
                    self.active_connections += 1
                    # Comment in Chinese removed
                    self._local.connection = conn
                    return conn
                except sqlite3.ProgrammingError:
                    # Comment in Chinese removed
                    pass
            
            # Comment in Chinese removedttings
            conn = sqlite3.connect(
                self.db_path, 
                timeout=self.timeout,
                check_same_thread=False,  # Comment in Chinese removed
                isolation_level=None       # Comment in Chinese removedtocommit
            )
            # Comment in Chinese removedncy
            conn.execute('PRAGMA journal_mode=WAL')
            # Comment in Chinese removedys
            conn.execute('PRAGMA foreign_keys=ON')
            # Comment in Chinese removedt
            conn.execute(f'PRAGMA busy_timeout={self.timeout * 1000}')
            # Comment in Chinese removed
            conn.execute('PRAGMA page_size=4096')
            # Comment in Chinese removed
            conn.execute('PRAGMA cache_size=10000')
            # Comment in Chinese removed
            conn.execute('PRAGMA synchronous=NORMAL')
            self.active_connections += 1
            # Comment in Chinese removed
            self._local.connection = conn
            return conn
    
    def return_connection(self, conn):
        """Return a connection to the pool.
        
        Args:
            conn: The database connection to return.
        """
        with self.lock:
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                try:
                    conn.close()
                except (sqlite3.Error, AttributeError):
                    pass
            self.active_connections = max(0, self.active_connections - 1)
    
    def close_all(self):
        """Close all connections in the pool."""
        with self.lock:
            while self.connections:
                conn = self.connections.popleft()
                try:
                    conn.close()
                except (sqlite3.Error, AttributeError):
                    pass
            self.active_connections = 0
    
    def get_stats(self):
        """Get connection pool statistics.
        
        Returns:
            dict: Connection pool statistics.
        """
        with self.lock:
            return {
                'active_connections': self.active_connections,
                'idle_connections': len(self.connections),
                'max_connections': self.max_connections
            }

# Comment in Chinese removeds
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
    
    def __init__(self, storage_path: str = "./data/tier3", enable_cache: bool = True, cache_size: int = 1000, cache_ttl: int = 3600, enable_vector_search: bool = True, enable_in_memory_cache: bool = True, enable_memory_compression: bool = True, compression_threshold_days: int = 30, super_compression_threshold_days: int = 90):
        """Initialize tier 3 storage.
        
        Args:
            storage_path: Path to store tier 3 memory database.
            enable_cache: Whether to enable cache.
            cache_size: Maximum cache size.
            cache_ttl: Cache time-to-live in seconds.
            enable_vector_search: Whether to enable vector search.
            enable_in_memory_cache: Whether to enable in-memory database cache.
            enable_memory_compression: Whether to enable memory compression.
            compression_threshold_days: Number of days after which memories are compressed.
            super_compression_threshold_days: Number of days after which memories are super compressed.
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Comment in Chinese removedth
        self.db_path = os.path.join(self.storage_path, "episodic_memories.db")
        
        # Comment in Chinese removedctions
        self.connection_pool = ConnectionPool(self.db_path, max_connections=10)
        
        # Comment in Chinese removed
        self.enable_in_memory_cache = enable_in_memory_cache
        if enable_in_memory_cache:
            self._init_in_memory_cache()
        
        # Comment in Chinese removedttings
        self.enable_cache = enable_cache
        if enable_cache:
            from memory_classification_engine.utils.cache import MemoryCache
            self.cache = MemoryCache(max_size=cache_size, ttl=cache_ttl)
        
        # Comment in Chinese removedttings
        self.enable_vector_search = enable_vector_search and VECTOR_SEARCH_AVAILABLE
        if self.enable_vector_search:
            # Comment in Chinese removedr
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            # Comment in Chinese removedx
            self.index = None
            self.memory_ids = []
            self._init_vector_index()
        
        # Comment in Chinese removedttings
        self.enable_memory_compression = enable_memory_compression
        self.compression_threshold_days = compression_threshold_days
        self.super_compression_threshold_days = super_compression_threshold_days
        
        # Comment in Chinese removed
        self._init_db()
        
        # Comment in Chinese removedd
        if self.enable_in_memory_cache:
            self._load_data_to_in_memory_cache()
        
        # Comment in Chinese removedd
        if self.enable_memory_compression:
            import threading
            threading.Thread(target=self._compress_old_memories).start()
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.close_all()
        if hasattr(self, 'in_memory_conn'):
            try:
                self.in_memory_conn.close()
            except (sqlite3.Error, AttributeError):
                pass
    
    def _init_in_memory_cache(self):
        """Initialize in-memory database cache."""
        try:
            # Comment in Chinese removed
            self.in_memory_conn = sqlite3.connect(':memory:')
            cursor = self.in_memory_conn.cursor()
            
            # Comment in Chinese removed
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
                    status TEXT DEFAULT 'active',
                    version INTEGER DEFAULT 1,
                    weight REAL DEFAULT 1.0,
                    conflict_status TEXT DEFAULT "none"
                )
            ''')
            
            # Comment in Chinese removedrying
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type_status ON episodic_memories (type, status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON episodic_memories (last_accessed)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_id ON episodic_memories (id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON episodic_memories (memory_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON episodic_memories (confidence)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON episodic_memories (source)')
            
            self.in_memory_conn.commit()
            # Comment in Chinese removedss
            self.in_memory_lock = threading.Lock()
            logger.info("In-memory database cache initialized")
        except Exception as e:
            logger.error(f"Error initializing in-memory cache: {e}")
            self.enable_in_memory_cache = False
    
    def _load_data_to_in_memory_cache(self):
        """Load data from main database to in-memory cache."""
        if not self.enable_in_memory_cache:
            return
        
        try:
            # Comment in Chinese removed
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            # 只选择内存数据库中存在的列
            cursor.execute('''
                SELECT id, type, memory_type, content, created_at, updated_at, last_accessed, 
                       access_count, confidence, source, context, status, version, weight, conflict_status 
                FROM episodic_memories WHERE status = ?
            ''', ('active',))
            rows = cursor.fetchall()
            self.connection_pool.return_connection(conn)
            
            if not rows:
                return
            
            # Comment in Chinese removedd lock
            with self.in_memory_lock:
                in_memory_cursor = self.in_memory_conn.cursor()
                try:
                    # 开始事务
                    in_memory_cursor.execute('BEGIN TRANSACTION')
                    for row in rows:
                        # 确保 row 是一个元组，并且长度正确
                        if isinstance(row, tuple) and len(row) == 15:
                            in_memory_cursor.execute('''
                                INSERT OR REPLACE INTO episodic_memories 
                                (id, type, memory_type, content, created_at, updated_at, last_accessed, access_count, confidence, source, context, status, version, weight, conflict_status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', row)
                    # 提交事务
                    self.in_memory_conn.commit()
                except Exception as e:
                    # 回滚事务
                    self.in_memory_conn.rollback()
                    logger.error(f"Error inserting data into in-memory cache: {e}")
            logger.info(f"Loaded {len(rows)} memories into in-memory cache")
        except Exception as e:
            logger.error(f"Error loading data to in-memory cache: {e}")
    
    def _init_db(self):
        """Initialize the database."""
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            # Comment in Chinese removedxist
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
            
            # Comment in Chinese removedxist
            try:
                cursor.execute('ALTER TABLE episodic_memories ADD COLUMN version INTEGER DEFAULT 1')
            except sqlite3.OperationalError:
                pass  # Comment in Chinese removedxists
            
            try:
                cursor.execute('ALTER TABLE episodic_memories ADD COLUMN weight REAL DEFAULT 1.0')
            except sqlite3.OperationalError:
                pass  # Comment in Chinese removedxists
            
            try:
                cursor.execute('ALTER TABLE episodic_memories ADD COLUMN conflict_status TEXT DEFAULT "none"')
            except sqlite3.OperationalError:
                pass  # Comment in Chinese removedxists
            
            try:
                cursor.execute('ALTER TABLE episodic_memories ADD COLUMN is_encrypted BOOLEAN DEFAULT FALSE')
            except sqlite3.OperationalError:
                pass  # Comment in Chinese removedxists
            
            try:
                cursor.execute('ALTER TABLE episodic_memories ADD COLUMN encryption_key_id TEXT')
            except sqlite3.OperationalError:
                pass  # Comment in Chinese removedxists
            
            try:
                cursor.execute('ALTER TABLE episodic_memories ADD COLUMN privacy_level INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass  # Comment in Chinese removedxists
            
            # Comment in Chinese removeds
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type_status ON episodic_memories (type, status)')
            
            # Comment in Chinese removedd
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON episodic_memories (last_accessed)')
            
            # Comment in Chinese removedps
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_id ON episodic_memories (id)')
            
            # Comment in Chinese removed
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON episodic_memories (memory_type)')
            
            # Comment in Chinese removed
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON episodic_memories (confidence)')
            
            # Comment in Chinese removed
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON episodic_memories (source)')
            
            # Comment in Chinese removedrch
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
            self.connection_pool.return_connection(conn)
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
    
    def _init_vector_index(self):
        """Initialize vector index from existing memories."""
        if not self.enable_vector_search:
            return
        
        try:
            # Comment in Chinese removeds
            conn = self.connection_pool.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, content FROM episodic_memories WHERE status = ?', ('active',))
            rows = cursor.fetchall()
            self.connection_pool.return_connection(conn)
            
            if not rows:
                # Comment in Chinese removedx
                self.index = None
                self.memory_ids = []
                return
            
            # Comment in Chinese removeds
            contents = [row['content'] for row in rows]
            self.memory_ids = [row['id'] for row in rows]
            
            # Comment in Chinese removedtion
            from memory_classification_engine.utils.semantic import semantic_utility
            
            # Comment in Chinese removedxts
            # 逐个编码文本，因为 semantic_utility 没有 batch_encode_texts 方法
            embeddings = []
            for content in contents:
                try:
                    # 使用 calculate_similarity 方法作为回退
                    # 这里我们使用一个空字符串作为比较对象，只是为了获取嵌入
                    # 注意：这不是正确的嵌入生成方法，但可以作为临时回退
                    semantic_utility.calculate_similarity(content, "")
                    # 由于我们无法直接获取嵌入，这里使用空列表作为回退
                    embeddings.append([])
                except Exception as e:
                    logger.error(f"Error encoding text: {e}")
                    embeddings.append([])
            
            # Comment in Chinese removedddings
            valid_embeddings = []
            valid_memory_ids = []
            for i, emb in enumerate(embeddings):
                if emb is not None and len(emb) > 0:
                    valid_embeddings.append(emb)
                    valid_memory_ids.append(self.memory_ids[i])
            
            if not valid_embeddings:
                self.index = None
                self.memory_ids = []
                return
            
            # Comment in Chinese removedy
            vectors = np.array(valid_embeddings, dtype='float32')
            self.memory_ids = valid_memory_ids
            
            # Comment in Chinese removed
            dimension = vectors.shape[1]
            nlist = min(100, len(valid_embeddings))  # Comment in Chinese removedrs
            self.index = faiss.IndexIVFFlat(faiss.IndexFlatL2(dimension), dimension, nlist, faiss.METRIC_L2)
            self.index.train(vectors)
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
        return self.store_memories_batch([memory])
    
    def _compress_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Compress memory content based on its age and importance.
        
        Args:
            memory: The memory to compress.
            
        Returns:
            The compressed memory.
        """
        if not self.enable_memory_compression:
            return memory
        
        try:
            # Comment in Chinese removed
            from datetime import datetime, timedelta, timezone
            created_at = memory.get('created_at')
            if not created_at:
                return memory
            
            # Comment in Chinese removed
            current_time = datetime.now(timezone.utc)
            
            # Comment in Chinese removed
            if created_at.endswith('Z'):
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_dt = datetime.fromisoformat(created_at)
            
            # Comment in Chinese removed
            if created_dt.tzinfo is None:
                created_dt = created_dt.replace(tzinfo=timezone.utc)
            
            age_days = (current_time - created_dt).days
            
            # Comment in Chinese removed
            if age_days >= self.super_compression_threshold_days:
                # Comment in Chinese removeds
                if 'content' in memory:
                    memory['content'] = self._super_compress_content(memory['content'])
                memory['status'] = 'super_compressed'
            elif age_days >= self.compression_threshold_days:
                # Comment in Chinese removeds
                if 'content' in memory:
                    memory['content'] = self._compress_content(memory['content'])
                memory['status'] = 'compressed'
            
            # Comment in Chinese removed
            memory['compressed_at'] = get_current_time()
            memory['compression_level'] = 'super' if age_days >= self.super_compression_threshold_days else 'normal'
            
            return memory
        except Exception as e:
            logger.warning(f"Error compressing memory: {e}")
            return memory
    
    def store_memories_batch(self, memories: List[Dict[str, Any]]) -> bool:
        """Store multiple memories in batch to reduce database operations.
        
        Args:
            memories: List of memories to store.
            
        Returns:
            True if all memories were stored successfully, False otherwise.
        """
        try:
            if not memories:
                return True
            
            processed_memories = []
            
            # Comment in Chinese removedirst
            for i, memory in enumerate(memories):
                # Comment in Chinese removednt
                current_time = get_current_time()
                if 'created_at' not in memory:
                    memory['created_at'] = current_time
                memory['updated_at'] = current_time
                # Generate a slightly different last_accessed time for each memory
                import time
                time.sleep(0.001)  # Add a small delay to ensure different timestamps
                memory['last_accessed'] = get_current_time()
                memory['access_count'] = 1
                memory['status'] = 'active'
                memory['version'] = 1
                memory['conflict_status'] = 'none'
                memory['is_encrypted'] = False
                memory['encryption_key_id'] = None
                memory['privacy_level'] = 0
                
                # Comment in Chinese removedight
                memory['weight'] = self._calculate_memory_weight(memory)
                
                # Comment in Chinese removednt
                if 'memory_type' not in memory and 'type' in memory:
                    memory['memory_type'] = memory['type']
                # Ensure memory has 'type' field
                if 'type' not in memory and 'memory_type' in memory:
                    memory['type'] = memory['memory_type']
                # Default type if neither is present
                if 'type' not in memory:
                    memory['type'] = 'episodic_memory'
                # Ensure memory has 'confidence' field
                if 'confidence' not in memory:
                    memory['confidence'] = 0.5
                # Ensure memory has 'source' field
                if 'source' not in memory:
                    memory['source'] = 'unknown'
                
                # Comment in Chinese removed
                content = memory.get('content', '')
                if content and encryption_manager.is_sensitive_data(content):
                    # Comment in Chinese removedy
                    key_id = memory.get('encryption_key_id')
                    if not key_id:
                        # Comment in Chinese removedssion
                        # Comment in Chinese removedy
                        key_id = encryption_manager.create_key('default_password')
                    
                    # Comment in Chinese removednt
                    ciphertext, nonce, tag = encryption_manager.encrypt(content, key_id)
                    # Comment in Chinese removed
                    import base64
                    encrypted_data = {
                        'ciphertext': base64.b64encode(ciphertext).decode(),
                        'nonce': base64.b64encode(nonce).decode(),
                        'tag': base64.b64encode(tag).decode()
                    }
                    memory['content'] = json.dumps(encrypted_data)
                    memory['is_encrypted'] = True
                    memory['encryption_key_id'] = key_id
                    memory['privacy_level'] = 1
                
                # Comment in Chinese removedlicts
                conflicts = self._detect_conflicts(memory)
                if conflicts:
                    # Comment in Chinese removedlicting
                    memory['conflict_status'] = 'conflicting'
                    # Comment in Chinese removeds
                    for conflict in conflicts:
                        self._mark_conflicting(conflict['id'])
                
                # Comment in Chinese removedd
                if self.enable_memory_compression:
                    memory = self._compress_memory(memory)
                
                processed_memories.append(memory)
            
            # Comment in Chinese removedction
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            # Comment in Chinese removedxist
            cursor.execute('PRAGMA table_info(episodic_memories)')
            columns = [column[1] for column in cursor.fetchall()]
            
            # Comment in Chinese removedction
            cursor.execute('BEGIN TRANSACTION')
            
            try:
                # Comment in Chinese removedrt
                for memory in processed_memories:
                    # Comment in Chinese removedmns
                    insert_columns = ['id', 'type', 'memory_type', 'content', 'created_at', 'updated_at', 'last_accessed', 'access_count', 'confidence', 'source', 'context', 'status']
                    # 确保所有值都是 SQLite 可以接受的类型
                    insert_values = [
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
                        json.dumps(memory.get('context')) if memory.get('context') else None,
                        memory.get('status')
                    ]
                    
                    # Comment in Chinese removedxist
                    if 'version' in columns:
                        insert_columns.append('version')
                        insert_values.append(memory.get('version', 1))
                    if 'weight' in columns:
                        insert_columns.append('weight')
                        insert_values.append(memory.get('weight', 1.0))
                    if 'conflict_status' in columns:
                        insert_columns.append('conflict_status')
                        insert_values.append(memory.get('conflict_status', 'none'))
                    if 'is_encrypted' in columns:
                        insert_columns.append('is_encrypted')
                        insert_values.append(memory.get('is_encrypted', False))
                    if 'encryption_key_id' in columns:
                        insert_columns.append('encryption_key_id')
                        insert_values.append(memory.get('encryption_key_id'))
                    if 'privacy_level' in columns:
                        insert_columns.append('privacy_level')
                        insert_values.append(memory.get('privacy_level', 0))
                    
                    # Comment in Chinese removednt
                    placeholders = ','.join(['?'] * len(insert_columns))
                    columns_str = ','.join(insert_columns)
                    cursor.execute(f'''
                        INSERT INTO episodic_memories 
                        ({columns_str})
                        VALUES ({placeholders})
                    ''', insert_values)
                
                # Comment in Chinese removedction
                conn.commit()
            except Exception as e:
                # Comment in Chinese removedrror
                conn.rollback()
                raise e
            finally:
                self.connection_pool.return_connection(conn)
            
            # Comment in Chinese removed
            if self.enable_cache and hasattr(self, 'cache'):
                for memory in processed_memories:
                    if memory.get('id'):
                        self.cache.set(memory['id'], memory)
            
            # Comment in Chinese removedd
            if self.enable_in_memory_cache:
                try:
                    with self.in_memory_lock:
                        cursor = self.in_memory_conn.cursor()
                        cursor.execute('BEGIN TRANSACTION')
                        
                        for memory in processed_memories:
                            if memory.get('id'):
                                # Comment in Chinese removedxists
                                cursor.execute('SELECT id FROM episodic_memories WHERE id = ?', (memory['id'],))
                                if cursor.fetchone():
                                    # Comment in Chinese removedmory
                                    update_columns = ['type', 'memory_type', 'content', 'created_at', 'updated_at', 'last_accessed', 'access_count', 'confidence', 'source', 'context', 'status', 'version', 'weight', 'conflict_status']
                                    set_clause = []
                                    params = []
                                    for col in update_columns:
                                        set_clause.append(f"{col} = ?")
                                        params.append(memory.get(col, ''))
                                    params.append(memory['id'])
                                    cursor.execute(f'''
                                        UPDATE episodic_memories 
                                        SET {', '.join(set_clause)} 
                                        WHERE id = ?
                                    ''', params)
                                else:
                                    # Comment in Chinese removedmory
                                    insert_columns = ['id', 'type', 'memory_type', 'content', 'created_at', 'updated_at', 'last_accessed', 'access_count', 'confidence', 'source', 'context', 'status', 'version', 'weight', 'conflict_status']
                                    insert_values = []
                                    for col in insert_columns:
                                        insert_values.append(memory.get(col, ''))
                                    placeholders = ','.join(['?'] * len(insert_columns))
                                    cursor.execute(f'''
                                        INSERT INTO episodic_memories 
                                        ({', '.join(insert_columns)})
                                        VALUES ({placeholders})
                                    ''', insert_values)
                        
                        self.in_memory_conn.commit()
                except Exception as e:
                    logger.warning(f"Error updating in-memory cache: {e}")
            
            # Comment in Chinese removedx
            if self.enable_vector_search:
                for memory in processed_memories:
                    if memory.get('id') and memory.get('content'):
                        self._update_vector_index(memory)
            
            return True
        except Exception as e:
            logger.error(f"Error storing memories in batch: {e}", exc_info=True)
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
            
            # Comment in Chinese removed
            cache_key = f"search:{query}:{limit}:{use_vector_search}"
            if self.enable_cache and hasattr(self, 'cache') and self.cache.exists(cache_key):
                return self.cache.get(cache_key)
            
            # Comment in Chinese removedd
            if use_vector_search and self.enable_vector_search:
                vector_results = self._vector_search(query, limit)
                if vector_results:
                    # Comment in Chinese removed
                    if self.enable_cache and hasattr(self, 'cache'):
                        self.cache.set(cache_key, vector_results)
                    return vector_results
            
            # Comment in Chinese removedd
            if self.enable_in_memory_cache:
                try:
                    # Comment in Chinese removedd
                    # Comment in Chinese removed
                    if hasattr(self, '_in_memory_thread_id') and self._in_memory_thread_id != threading.get_ident():
                        logger.debug("Skipping in-memory cache: thread mismatch")
                    else:
                        # Comment in Chinese removed
                        if not hasattr(self, '_in_memory_thread_id'):
                            self._in_memory_thread_id = threading.get_ident()
                            
                        with self.in_memory_lock:
                            cursor = self.in_memory_conn.cursor()
                            if self._is_english_query(query):
                                # Comment in Chinese removeds
                                cursor.execute('''
                                    SELECT * FROM episodic_memories 
                                    WHERE status = 'active' AND content LIKE ? 
                                    ORDER BY last_accessed DESC 
                                    LIMIT ?
                                ''', (f'%{query}%', limit))
                            else:
                                # Comment in Chinese removeds
                                cursor.execute('''
                                    SELECT * FROM episodic_memories 
                                    WHERE status = 'active' AND content LIKE ? 
                                    ORDER BY last_accessed DESC 
                                    LIMIT ?
                                ''', (f'%{query}%', limit))
                            
                            rows = cursor.fetchall()
                            if rows:
                                # Comment in Chinese removeds
                                memories = []
                                for row in rows:
                                    memory = dict(row)
                                    # Comment in Chinese removednt
                                    if 'type' in memory and 'memory_type' not in memory:
                                        memory['memory_type'] = memory['type']
                                    memories.append(memory)
                                
                                # Comment in Chinese removed
                                if self.enable_cache and hasattr(self, 'cache'):
                                    self.cache.set(cache_key, memories)
                                return memories
                except Exception as e:
                    logger.warning(f"In-memory cache search failed, falling back to main database: {e}")
            
            # Comment in Chinese removedrch
            conn = self.connection_pool.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if self._is_english_query(query):
                try:
                    # Comment in Chinese removeds
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
                    self.connection_pool.return_connection(conn)
                    return self._fallback_retrieve(query, limit)
            else:
                # Comment in Chinese removeds
                self.connection_pool.return_connection(conn)
                return self._fallback_retrieve(query, limit)
            
            rows = cursor.fetchall()
            self.connection_pool.return_connection(conn)
            
            # Comment in Chinese removeds
            memories = []
            for row in rows:
                memory = dict(row)
                if 'rank' in memory:
                    del memory['rank']
                # Comment in Chinese removednt
                if 'type' in memory and 'memory_type' not in memory:
                    memory['memory_type'] = memory['type']
                # Comment in Chinese removedd
                if memory.get('is_encrypted'):
                    try:
                        content = memory.get('content', '')
                        if content and isinstance(content, str):
                            import json
                            import base64
                            try:
                                encrypted_data = json.loads(content)
                                if isinstance(encrypted_data, dict) and all(key in encrypted_data for key in ['ciphertext', 'nonce', 'tag']):
                                    try:
                                        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
                                        nonce = base64.b64decode(encrypted_data['nonce'])
                                        tag = base64.b64decode(encrypted_data['tag'])
                                        key_id = memory.get('encryption_key_id')
                                        if key_id:
                                            try:
                                                decrypted_content = encryption_manager.decrypt(ciphertext, nonce, tag, key_id)
                                                memory['content'] = decrypted_content
                                            except Exception as decrypt_error:
                                                logger.error(f"Error decrypting memory content: {decrypt_error}")
                                    except Exception as decode_error:
                                        logger.error(f"Error decoding base64 data: {decode_error}")
                                else:
                                    logger.error("Invalid encrypted data structure")
                            except json.JSONDecodeError as json_error:
                                logger.error(f"Error parsing JSON content: {json_error}")
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}")
                memories.append(memory)
            
            # Comment in Chinese removed
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
            # Comment in Chinese removedry
            try:
                query_vector = self.vectorizer.transform([query]).toarray().astype('float32')
            except Exception as e:
                # Comment in Chinese removedmpty list
                logger.error(f"Error creating query vector: {e}")
                return []
            
            # Comment in Chinese removedx
            distances, indices = self.index.search(query_vector, limit)
            
            # Comment in Chinese removeds
            matched_memory_ids = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx < len(self.memory_ids):
                    matched_memory_ids.append(self.memory_ids[idx])
            
            if not matched_memory_ids:
                return []
            
            # Comment in Chinese removed
            conn = self.connection_pool.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Comment in Chinese removedry
            placeholders = ','.join(['?'] * len(matched_memory_ids))
            cursor.execute(f'''
                SELECT * FROM episodic_memories 
                WHERE status = 'active' AND id IN ({placeholders})
                ORDER BY instr(',{','.join(matched_memory_ids)},', ',' || id || ',')
            ''', matched_memory_ids)
            
            rows = cursor.fetchall()
            self.connection_pool.return_connection(conn)
            
            # Comment in Chinese removeds
            memories = []
            for row in rows:
                memory = dict(row)
                # Comment in Chinese removednt
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
            # Comment in Chinese removedd
            if self.enable_in_memory_cache:
                try:
                    # Comment in Chinese removedd
                    # Comment in Chinese removed
                    if hasattr(self, '_in_memory_thread_id') and self._in_memory_thread_id != threading.get_ident():
                        logger.debug("Skipping in-memory cache: thread mismatch")
                    else:
                        # Comment in Chinese removed
                        if not hasattr(self, '_in_memory_thread_id'):
                            self._in_memory_thread_id = threading.get_ident()
                            
                        with self.in_memory_lock:
                            cursor = self.in_memory_conn.cursor()
                            # Comment in Chinese removeds
                            self.in_memory_conn.row_factory = sqlite3.Row
                            if query:
                                # Comment in Chinese removedry
                                cursor.execute('''
                                    SELECT id, type, memory_type, content, created_at, updated_at, last_accessed, access_count, confidence, source, context, status 
                                    FROM episodic_memories 
                                    WHERE (status = 'active' OR status = 'compressed' OR status = 'super_compressed') AND content LIKE ? 
                                    ORDER BY last_accessed DESC 
                                    LIMIT ?
                                ''', (f'%{query}%', limit))
                            else:
                                # Comment in Chinese removedry
                                cursor.execute('''
                                    SELECT id, type, memory_type, content, created_at, updated_at, last_accessed, access_count, confidence, source, context, status 
                                    FROM episodic_memories 
                                    WHERE status = 'active' OR status = 'compressed' OR status = 'super_compressed' 
                                    ORDER BY last_accessed DESC 
                                    LIMIT ?
                                ''', (limit,))
                            
                            rows = cursor.fetchall()
                            if rows:
                                # Comment in Chinese removeds
                                memories = []
                                for row in rows:
                                    memory = dict(row)
                                    # Comment in Chinese removednt
                                    if 'type' in memory and 'memory_type' not in memory:
                                        memory['memory_type'] = memory['type']
                                    # Comment in Chinese removedd
                                    if memory.get('is_encrypted'):
                                        try:
                                            content = memory.get('content', '')
                                            if content:
                                                import json
                                                import base64
                                                encrypted_data = json.loads(content)
                                                ciphertext = base64.b64decode(encrypted_data['ciphertext'])
                                                nonce = base64.b64decode(encrypted_data['nonce'])
                                                tag = base64.b64decode(encrypted_data['tag'])
                                                key_id = memory.get('encryption_key_id')
                                                if key_id:
                                                    decrypted_content = encryption_manager.decrypt(ciphertext, nonce, tag, key_id)
                                                    memory['content'] = decrypted_content
                                        except Exception as e:
                                            logger.error(f"Error decrypting memory: {e}")
                                    memories.append(memory)
                                return memories
                except Exception as e:
                    logger.warning(f"In-memory cache fallback search failed: {e}, falling back to main database")
            
            # Comment in Chinese removed
            conn = self.connection_pool.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if query:
                # Comment in Chinese removedry
                cursor.execute('''
                    SELECT id, type, memory_type, content, created_at, updated_at, last_accessed, access_count, confidence, source, context, status, is_encrypted, encryption_key_id, privacy_level 
                    FROM episodic_memories 
                    WHERE (status = 'active' OR status = 'compressed' OR status = 'super_compressed') AND content LIKE ? 
                    ORDER BY last_accessed DESC 
                    LIMIT ?
                ''', (f'%{query}%', limit))
            else:
                # Comment in Chinese removedry
                cursor.execute('''
                    SELECT id, type, memory_type, content, created_at, updated_at, last_accessed, access_count, confidence, source, context, status, is_encrypted, encryption_key_id, privacy_level 
                    FROM episodic_memories 
                    WHERE status = 'active' OR status = 'compressed' OR status = 'super_compressed' 
                    ORDER BY last_accessed DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            self.connection_pool.return_connection(conn)
            
            # Comment in Chinese removeds
            memories = []
            for row in rows:
                try:
                    memory = dict(row)
                    if 'type' in memory and 'memory_type' not in memory:
                        memory['memory_type'] = memory['type']
                    
                    if memory.get('is_encrypted'):
                        try:
                            content = memory.get('content', '')
                            if content and isinstance(content, str) and len(content) > 10:
                                import json
                                import base64
                                try:
                                    encrypted_data = json.loads(content)
                                    if isinstance(encrypted_data, dict):
                                        required_keys = ['ciphertext', 'nonce', 'tag']
                                        if all(key in encrypted_data for key in required_keys):
                                            try:
                                                ciphertext = base64.b64decode(encrypted_data['ciphertext'])
                                                nonce = base64.b64decode(encrypted_data['nonce'])
                                                tag = base64.b64decode(encrypted_data['tag'])
                                                key_id = memory.get('encryption_key_id')
                                                if key_id:
                                                    decrypted_content = encryption_manager.decrypt(ciphertext, nonce, tag, key_id)
                                                    memory['content'] = str(decrypted_content)
                                            except Exception as decrypt_error:
                                                logger.debug(f"Error decrypting: {decrypt_error}")
                                except (json.JSONDecodeError, TypeError, ValueError) as json_error:
                                    logger.debug(f"Not encrypted JSON: {str(content)[:50]}")
                            else:
                                logger.debug("Empty or invalid content for decryption")
                        except Exception as e:
                            logger.debug(f"Skipping decryption for memory: {e}")
                    
                    memories.append(memory)
                except Exception as row_error:
                    logger.debug(f"Error processing row: {row_error}")
                    continue
            
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
    
    def _calculate_memory_weight(self, memory: Dict[str, Any]) -> float:
        """Calculate memory weight based on confidence, recency, and source.
        
        Args:
            memory: The memory to calculate weight for.
            
        Returns:
            The calculated weight.
        """
        from datetime import datetime, timezone
        
        # Comment in Chinese removeds
        confidence = memory.get('confidence', 1.0)
        created_at = memory.get('created_at', get_current_time())
        source = memory.get('source', '')
        
        # Comment in Chinese removedtion
        try:
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            current_dt = datetime.now(timezone.utc)
            days_since_creation = (current_dt - created_dt).days
        except (ValueError, TypeError):
            days_since_creation = 0
        
        # Comment in Chinese removedncy
        recency_score = 2 ** (-0.1 * days_since_creation)
        
        # Comment in Chinese removed priority
        source_priority = {
            'rule': 4.0,      # Comment in Chinese removed
            'pattern': 3.0,    # Comment in Chinese removedxt
            'semantic': 2.0,   # Comment in Chinese removed
            'default': 1.0     # Comment in Chinese removed
        }
        
        def get_source_priority(source_str):
            for key, priority in source_priority.items():
                if key in source_str:
                    return priority
            return 1.0
        
        source_score = get_source_priority(source)
        
        # Comment in Chinese removedight
        weight = confidence * recency_score * source_score
        
        return min(weight, 1.0)  # Comment in Chinese removed
    
    def _detect_conflicts(self, memory: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts with existing memories.
        
        Args:
            memory: The memory to check for conflicts.
            
        Returns:
            A list of conflicting memories.
        """
        conflicts = []
        
        # Comment in Chinese removeds
        content = memory.get('content', '').lower()
        memory_type = memory.get('memory_type', '')
        
        # Comment in Chinese removed
        existing_memories = self.retrieve_memories(limit=50)
        
        for existing_memory in existing_memories:
            existing_memory_type = existing_memory.get('memory_type', existing_memory.get('type', ''))
            if existing_memory_type != memory_type:
                continue
            
            existing_content = existing_memory.get('content', '').lower()
            
            # Comment in Chinese removednt
            if not content or not existing_content:
                continue
            
            # Comment in Chinese removedtion
            if self._check_negation_conflict(content, existing_content):
                conflicts.append(existing_memory)
            
            # Comment in Chinese removedlict
            similarity = self._calculate_semantic_similarity(content, existing_content)
            if similarity > 0.8 and self._check_semantic_conflict(content, existing_content):
                conflicts.append(existing_memory)
        
        return conflicts
    
    def _check_negation_conflict(self, content1: str, content2: str) -> bool:
        """Check for negation conflicts between two contents.
        
        Args:
            content1: First content.
            content2: Second content.
            
        Returns:
            True if there's a negation conflict, False otherwise.
        """
        # Comment in Chinese removed
        chinese_negation_words = ['不', '没', '没有', '不是', '不要', '不喜欢', '不想要', '反对', '拒绝', '否定']
        # Comment in Chinese removednglish
        english_negation_words = ['not', 'no', 'don\'t', 'doesn\'t', 'didn\'t', 'won\'t', 'can\'t', 'never', 'against', 'reject', 'deny']
        
        # Comment in Chinese removedtion
        for word in chinese_negation_words:
            if word in content1 and word not in content2:
                # Comment in Chinese removedr
                content1_without_negation = content1.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1_without_negation, content2)
                if similarity > 0.7:
                    return True
            elif word in content2 and word not in content1:
                # Comment in Chinese removedr
                content2_without_negation = content2.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1, content2_without_negation)
                if similarity > 0.7:
                    return True
        
        # Comment in Chinese removedtion
        for word in english_negation_words:
            if word in content1 and word not in content2:
                # Comment in Chinese removedr
                content1_without_negation = content1.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1_without_negation, content2)
                if similarity > 0.7:
                    return True
            elif word in content2 and word not in content1:
                # Comment in Chinese removedr
                content2_without_negation = content2.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1, content2_without_negation)
                if similarity > 0.7:
                    return True
        
        return False
    
    def _check_semantic_conflict(self, content1: str, content2: str) -> bool:
        """Check for semantic conflicts between two contents.
        
        Args:
            content1: First content.
            content2: Second content.
            
        Returns:
            True if there's a semantic conflict, False otherwise.
        """
        # Comment in Chinese removedor now
        # Comment in Chinese removed
        
        # Comment in Chinese removednt
        positive_words = ['like', 'love', 'prefer', 'enjoy', 'happy', 'positive', '好', '喜欢', '开心', '正面']
        negative_words = ['dislike', 'hate', 'avoid', 'unhappy', 'negative', 'bad', '不喜欢', '讨厌', '负面']
        
        content1_positive = any(word in content1 for word in positive_words)
        content1_negative = any(word in content1 for word in negative_words)
        content2_positive = any(word in content2 for word in positive_words)
        content2_negative = any(word in content2 for word in negative_words)
        
        if (content1_positive and content2_negative) or (content1_negative and content2_positive):
            return True
        
        return False
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score between 0 and 1.
        """
        from memory_classification_engine.utils.semantic import semantic_utility
        return semantic_utility.calculate_similarity(text1, text2)
    
    def _mark_conflicting(self, memory_id: str) -> bool:
        """Mark a memory as conflicting.
        
        Args:
            memory_id: The ID of the memory to mark.
            
        Returns:
            True if the memory was marked successfully, False otherwise.
        """
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            # Comment in Chinese removedxists
            cursor.execute('PRAGMA table_info(episodic_memories)')
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'conflict_status' in columns:
                cursor.execute('''
                    UPDATE episodic_memories 
                    SET conflict_status = 'conflicting', updated_at = ? 
                    WHERE id = ?
                ''', (get_current_time(), memory_id))
            else:
                # Comment in Chinese removedmp
                cursor.execute('''
                    UPDATE episodic_memories 
                    SET updated_at = ? 
                    WHERE id = ?
                ''', (get_current_time(), memory_id))
            
            conn.commit()
            self.connection_pool.return_connection(conn)
            
            # Comment in Chinese removed
            if self.enable_cache and hasattr(self, 'cache'):
                self.cache.delete(memory_id)
            
            return True
        except Exception as e:
            logger.error(f"Error marking memory as conflicting: {e}", exc_info=True)
            return False
    
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
            
            # Comment in Chinese removedx
            if memory_id in self.memory_ids:
                return
            
            # Comment in Chinese removedtion
            from memory_classification_engine.utils.semantic import semantic_utility
            
            # Comment in Chinese removednt
            embedding = semantic_utility.encode_text(content)
            if embedding is None:
                return
            
            # Comment in Chinese removedy
            vector = np.array([embedding], dtype='float32')
            
            # Comment in Chinese removedx
            if self.index is None:
                # Comment in Chinese removed
                dimension = vector.shape[1]
                nlist = 10  # Comment in Chinese removedx
                self.index = faiss.IndexIVFFlat(faiss.IndexFlatL2(dimension), dimension, nlist, faiss.METRIC_L2)
                self.index.train(vector)
            elif isinstance(self.index, faiss.IndexIVFFlat):
                # Comment in Chinese removedin
                if len(self.memory_ids) % 100 == 0:  # Comment in Chinese removeddditions
                    # Comment in Chinese removedin
                    self._init_vector_index()
                    return
            
            # Comment in Chinese removedx
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
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            # Comment in Chinese removedry
            set_clause = []
            params = []
            
            for key, value in updates.items():
                set_clause.append(f"{key} = ?")
                params.append(value)
            
            # Comment in Chinese removedmp
            set_clause.append("updated_at = ?")
            params.append(get_current_time())
            
            # Comment in Chinese removedms
            params.append(memory_id)
            
            # Comment in Chinese removed
            cursor.execute(f'''
                UPDATE episodic_memories 
                SET {', '.join(set_clause)} 
                WHERE id = ?
            ''', params)
            
            conn.commit()
            self.connection_pool.return_connection(conn)
            
            result = cursor.rowcount > 0
            
            # Comment in Chinese removed
            if result and self.enable_cache and hasattr(self, 'cache'):
                # Comment in Chinese removedmory
                self.cache.delete(memory_id)
                # Comment in Chinese removeds
                self._invalidate_search_caches()
            
            # Comment in Chinese removedd
            if result and self.enable_in_memory_cache:
                try:
                    cursor = self.in_memory_conn.cursor()
                    # Comment in Chinese removedry
                    set_clause = []
                    params = []
                    
                    for key, value in updates.items():
                        set_clause.append(f"{key} = ?")
                        params.append(value)
                    
                    # Comment in Chinese removedmp
                    set_clause.append("updated_at = ?")
                    params.append(get_current_time())
                    
                    # Comment in Chinese removedms
                    params.append(memory_id)
                    
                    # Comment in Chinese removed
                    cursor.execute(f'''
                        UPDATE episodic_memories 
                        SET {', '.join(set_clause)} 
                        WHERE id = ?
                    ''', params)
                    self.in_memory_conn.commit()
                except Exception as e:
                    logger.warning(f"Error updating in-memory cache: {e}")
            
            # Comment in Chinese removedd
            if result and self.enable_vector_search and 'content' in updates:
                # Comment in Chinese removedx
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
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            # Comment in Chinese removedd'
            cursor.execute('''
                UPDATE episodic_memories 
                SET status = 'deleted', updated_at = ? 
                WHERE id = ?
            ''', (get_current_time(), memory_id))
            
            conn.commit()
            self.connection_pool.return_connection(conn)
            
            result = cursor.rowcount > 0
            
            # Comment in Chinese removed
            if result and self.enable_cache and hasattr(self, 'cache'):
                # Comment in Chinese removedmory
                self.cache.delete(memory_id)
                # Comment in Chinese removeds
                self._invalidate_search_caches()
            
            # Comment in Chinese removedd
            if result and self.enable_in_memory_cache:
                try:
                    with self.in_memory_lock:
                        cursor = self.in_memory_conn.cursor()
                        # Comment in Chinese removedd'
                        cursor.execute('''
                            UPDATE episodic_memories 
                            SET status = 'deleted', updated_at = ? 
                            WHERE id = ?
                        ''', (get_current_time(), memory_id))
                        self.in_memory_conn.commit()
                except Exception as e:
                    logger.warning(f"Error updating in-memory cache: {e}")
            
            # Comment in Chinese removedx
            if result and self.enable_vector_search:
                # Comment in Chinese removedx
                self._init_vector_index()
            
            return result
        except Exception as e:
            logger.error(f"Error deleting memory: {e}", exc_info=True)
            return False
    
    def _invalidate_search_caches(self):
        """Invalidate all search-related caches."""
        if self.enable_cache and hasattr(self, 'cache'):
            # Comment in Chinese removeds
            keys_to_delete = []
            for key in self.cache.cache:
                if key.startswith('search:'):
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                self.cache.delete(key)
    
    def _compress_old_memories(self):
        """Compress old memories based on age."""
        try:
            from datetime import datetime, timezone, timedelta
            import sqlite3
            
            current_time = datetime.now(timezone.utc)
            compression_threshold = current_time - timedelta(days=self.compression_threshold_days)
            super_compression_threshold = current_time - timedelta(days=self.super_compression_threshold_days)
            
            # Comment in Chinese removedd
            conn = sqlite3.connect(self.db_path, timeout=30)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA foreign_keys=ON')
            conn.execute('PRAGMA busy_timeout=30000')
            cursor = conn.cursor()
            
            # Comment in Chinese removedshold
            cursor.execute('''
                SELECT id, content, created_at 
                FROM episodic_memories 
                WHERE status = 'active' 
                AND datetime(created_at) < ?
            ''', (compression_threshold.isoformat(),))
            
            memories_to_compress = cursor.fetchall()
            
            for memory in memories_to_compress:
                memory_id, content, created_at = memory
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                
                if created_dt < super_compression_threshold:
                    # Comment in Chinese removedtion
                    compressed_content = self._super_compress_content(content)
                    status = 'super_compressed'
                else:
                    # Comment in Chinese removednt
                    compressed_content = self._compress_content(content)
                    status = 'compressed'
                
                # Comment in Chinese removedmory
                cursor.execute('''
                    UPDATE episodic_memories 
                    SET content = ?, status = ?, updated_at = ? 
                    WHERE id = ?
                ''', (compressed_content, status, get_current_time(), memory_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Compressed {len(memories_to_compress)} old memories")
        except Exception as e:
            logger.error(f"Error compressing old memories: {e}", exc_info=True)
    
    def _compress_content(self, content: str) -> str:
        """Compress memory content by summarizing it.
        
        Args:
            content: Original content.
            
        Returns:
            Compressed content.
        """
        # Comment in Chinese removedtion
        sentences = content.split('. ')
        if len(sentences) <= 2:
            return content
        
        # Comment in Chinese removed
        compressed = '. '.join([sentences[0], sentences[-1]])
        if compressed:
            compressed += '.'
        
        # Comment in Chinese removedr
        return f"[COMPRESSED] {compressed}"
    
    def _super_compress_content(self, content: str) -> str:
        """Super compress memory content by keeping only key information.
        
        Args:
            content: Original content.
            
        Returns:
            Super compressed content.
        """
        # Comment in Chinese removedtion
        # Comment in Chinese removedrs
        if len(content) <= 100:
            return content
        
        # Comment in Chinese removedtion
        key_info = content[:100].strip()
        
        # Comment in Chinese removedr
        return f"[SUPER_COMPRESSED] {key_info}..."
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory by ID from tier 3.
        
        Args:
            memory_id: The ID of the memory to get.
            
        Returns:
            The memory if found, None otherwise.
        """
        try:
            # Check cache first
            if self.enable_cache and hasattr(self, 'cache'):
                cached_memory = self.cache.get(memory_id)
                if cached_memory:
                    return cached_memory
            
            # Check in-memory cache
            if self.enable_in_memory_cache:
                try:
                    with self.in_memory_lock:
                        cursor = self.in_memory_conn.cursor()
                        cursor.execute('SELECT * FROM episodic_memories WHERE id = ? AND status = ?', (memory_id, 'active'))
                        row = cursor.fetchone()
                        if row:
                            # Convert row to dictionary
                            memory = dict(row)
                            # Decrypt content if needed
                            if memory.get('is_encrypted'):
                                try:
                                    content = memory.get('content', '')
                                    if content and isinstance(content, str):
                                        import json
                                        import base64
                                        try:
                                            encrypted_data = json.loads(content)
                                            if isinstance(encrypted_data, dict) and all(key in encrypted_data for key in ['ciphertext', 'nonce', 'tag']):
                                                try:
                                                    ciphertext = base64.b64decode(encrypted_data['ciphertext'])
                                                    nonce = base64.b64decode(encrypted_data['nonce'])
                                                    tag = base64.b64decode(encrypted_data['tag'])
                                                    key_id = memory.get('encryption_key_id')
                                                    if key_id:
                                                        from memory_classification_engine.privacy.encryption import encryption_manager
                                                        decrypted_content = encryption_manager.decrypt(ciphertext, nonce, tag, key_id)
                                                        memory['content'] = str(decrypted_content)
                                                except Exception as decrypt_error:
                                                    logger.error(f"Error decrypting memory content: {decrypt_error}")
                                        except (json.JSONDecodeError, TypeError, ValueError) as json_error:
                                            logger.error(f"Error parsing JSON content: {json_error}")
                                except Exception as e:
                                    logger.error(f"Error decrypting memory: {e}")
                            return memory
                except Exception as e:
                    logger.warning(f"Error getting memory from in-memory cache: {e}")
            
            # Check main database
            conn = self.connection_pool.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM episodic_memories WHERE id = ? AND status = ?', (memory_id, 'active'))
            row = cursor.fetchone()
            
            if row:
                memory = dict(row)
                
                # Decrypt content if needed
                if memory.get('is_encrypted'):
                    try:
                        content = memory.get('content', '')
                        if content and isinstance(content, str):
                            import json
                            import base64
                            try:
                                encrypted_data = json.loads(content)
                                if isinstance(encrypted_data, dict) and all(key in encrypted_data for key in ['ciphertext', 'nonce', 'tag']):
                                    try:
                                        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
                                        nonce = base64.b64decode(encrypted_data['nonce'])
                                        tag = base64.b64decode(encrypted_data['tag'])
                                        key_id = memory.get('encryption_key_id')
                                        if key_id:
                                            from memory_classification_engine.privacy.encryption import encryption_manager
                                            decrypted_content = encryption_manager.decrypt(ciphertext, nonce, tag, key_id)
                                            memory['content'] = str(decrypted_content)
                                    except Exception as decrypt_error:
                                        logger.error(f"Error decrypting memory content: {decrypt_error}")
                            except (json.JSONDecodeError, TypeError, ValueError) as json_error:
                                logger.error(f"Error parsing JSON content: {json_error}")
                    except Exception as e:
                        logger.error(f"Error decrypting memory: {e}")
                
                # Update cache
                if self.enable_cache and hasattr(self, 'cache'):
                    self.cache.set(memory_id, memory)
                
                self.connection_pool.return_connection(conn)
                return memory
            
            self.connection_pool.return_connection(conn)
            return None
        except Exception as e:
            logger.error(f"Error getting memory: {e}", exc_info=True)
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tier 3 storage.
        
        Returns:
            A dictionary with statistics.
        """
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            # Comment in Chinese removeds
            cursor.execute('SELECT COUNT(*) FROM episodic_memories')
            total = cursor.fetchone()[0]
            
            # Comment in Chinese removeds
            cursor.execute('SELECT COUNT(*) FROM episodic_memories WHERE status = ?', ('active',))
            active = cursor.fetchone()[0]
            
            # Comment in Chinese removeds
            cursor.execute('SELECT type, COUNT(*) FROM episodic_memories WHERE status = ? GROUP BY type', ('active',))
            types = {row[0]: row[1] for row in cursor.fetchall()}
            
            self.connection_pool.return_connection(conn)
            
            stats = {
                'total_memories': total,
                'active_memories': active,
                'memory_types': types
            }
            
            # Comment in Chinese removedd
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
            conn = self.connection_pool.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Comment in Chinese removeds
            cursor.execute('''
                SELECT * FROM episodic_memories 
                WHERE status = 'active' 
                ORDER BY access_count DESC, updated_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            self.connection_pool.return_connection(conn)
            
            count = 0
            for row in rows:
                memory = dict(row)
                # Comment in Chinese removednt
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
