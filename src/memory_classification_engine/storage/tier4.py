"""Tier 4 semantic memory storage with knowledge graph."""

import os
import sqlite3
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict, deque
import threading

from memory_classification_engine.utils.helpers import get_current_time
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.storage.neo4j_knowledge_graph import Neo4jKnowledgeGraph
from memory_classification_engine.privacy.encryption import encryption_manager


class ConnectionPool:
    """Database connection pool for SQLite."""
    
    def __init__(self, db_path: str, max_connections: int = 5):
        """Initialize the connection pool.
        
        Args:
            db_path: Path to the SQLite database.
            max_connections: Maximum number of connections in the pool.
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = deque()
        self.lock = threading.Lock()
        
    def get_connection(self):
        """Get a connection from the pool.
        
        Returns:
            sqlite3.Connection: A database connection.
        """
        with self.lock:
            if self.connections:
                conn = self.connections.popleft()
                # Check if connection is still valid
                try:
                    conn.execute('SELECT 1')
                    return conn
                except sqlite3.ProgrammingError:
                    # Connection is invalid, create new one
                    pass
            
            # Create a new connection with thread-safe settings
            conn = sqlite3.connect(
                self.db_path, 
                timeout=30,
                check_same_thread=False,  # Allow cross-thread usage
                isolation_level=None       # Enable autocommit
            )
            # Enable WAL mode for better concurrency
            conn.execute('PRAGMA journal_mode=WAL')
            # Enable foreign keys
            conn.execute('PRAGMA foreign_keys=ON')
            # Set busy timeout
            conn.execute('PRAGMA busy_timeout=30000')
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
                conn.close()
    
    def close_all(self):
        """Close all connections in the pool."""
        with self.lock:
            while self.connections:
                conn = self.connections.popleft()
                try:
                    conn.close()
                except:
                    pass


class KnowledgeGraph:
    """Knowledge graph for storing semantic relationships."""
    
    def __init__(self, storage_path: str = "./data/tier4"):
        """Initialize the knowledge graph.
        
        Args:
            storage_path: Path to store knowledge graph data.
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # In-memory graph storage
        self.nodes = {}  # node_id -> node_data
        self.edges = defaultdict(list)  # node_id -> list of (target_id, relation_type, weight)
        
        # Load existing graph
        self._load_graph()
        
        logger.info("KnowledgeGraph initialized")
    
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any]) -> bool:
        """Add a node to the knowledge graph.
        
        Args:
            node_id: Unique identifier for the node.
            node_type: Type of the node (e.g., 'memory', 'entity', 'concept').
            properties: Node properties.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            self.nodes[node_id] = {
                'id': node_id,
                'type': node_type,
                'properties': properties,
                'created_at': get_current_time(),
                'updated_at': get_current_time()
            }
            return True
        except Exception as e:
            logger.error(f"Error adding node {node_id}: {e}")
            return False
    
    def add_edge(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Add an edge (relationship) between two nodes.
        
        Args:
            source_id: Source node ID.
            target_id: Target node ID.
            relation_type: Type of relationship.
            weight: Relationship weight (0.0 to 1.0).
            properties: Additional relationship properties.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Check if nodes exist
            if source_id not in self.nodes:
                logger.warning(f"Source node {source_id} does not exist")
                return False
            if target_id not in self.nodes:
                logger.warning(f"Target node {target_id} does not exist")
                return False
            
            # Add edge
            edge_data = {
                'target_id': target_id,
                'relation_type': relation_type,
                'weight': weight,
                'properties': properties or {},
                'created_at': get_current_time()
            }
            
            self.edges[source_id].append(edge_data)
            
            # Update node timestamps
            self.nodes[source_id]['updated_at'] = get_current_time()
            self.nodes[target_id]['updated_at'] = get_current_time()
            
            return True
        except Exception as e:
            logger.error(f"Error adding edge {source_id} -> {target_id}: {e}")
            return False
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID.
        
        Args:
            node_id: Node ID.
            
        Returns:
            Node data or None if not found.
        """
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get neighboring nodes.
        
        Args:
            node_id: Node ID.
            relation_type: Optional relation type filter.
            
        Returns:
            List of neighboring nodes with relationship info.
        """
        if node_id not in self.edges:
            return []
        
        neighbors = []
        for edge in self.edges[node_id]:
            if relation_type is None or edge['relation_type'] == relation_type:
                target_node = self.nodes.get(edge['target_id'])
                if target_node:
                    neighbors.append({
                        'node': target_node,
                        'relation': edge
                    })
        
        return neighbors
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 3) -> Optional[List[Dict[str, Any]]]:
        """Find a path between two nodes using BFS.
        
        Args:
            start_id: Starting node ID.
            end_id: Target node ID.
            max_depth: Maximum search depth.
            
        Returns:
            Path as list of edges, or None if no path found.
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return None
        
        # BFS
        visited = {start_id}
        queue = [(start_id, [])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id == end_id:
                return path
            
            if len(path) >= max_depth:
                continue
            
            for edge in self.edges.get(current_id, []):
                target_id = edge['target_id']
                if target_id not in visited:
                    visited.add(target_id)
                    new_path = path + [edge]
                    queue.append((target_id, new_path))
        
        return None
    
    def get_related_memories(self, memory_id: str, min_weight: float = 0.5) -> List[Dict[str, Any]]:
        """Get memories related to a given memory.
        
        Args:
            memory_id: Memory ID.
            min_weight: Minimum relationship weight.
            
        Returns:
            List of related memories.
        """
        related = []
        
        for edge in self.edges.get(memory_id, []):
            if edge['weight'] >= min_weight:
                target_node = self.nodes.get(edge['target_id'])
                if target_node and target_node['type'] == 'memory':
                    related.append({
                        'memory_id': edge['target_id'],
                        'relation_type': edge['relation_type'],
                        'weight': edge['weight'],
                        'properties': target_node['properties']
                    })
        
        # Sort by weight
        related.sort(key=lambda x: x['weight'], reverse=True)
        
        return related
    
    def _load_graph(self):
        """Load graph from disk."""
        graph_file = os.path.join(self.storage_path, "knowledge_graph.json")
        
        if os.path.exists(graph_file):
            try:
                with open(graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.nodes = data.get('nodes', {})
                    self.edges = defaultdict(list, data.get('edges', {}))
                logger.info(f"Loaded knowledge graph with {len(self.nodes)} nodes")
            except Exception as e:
                logger.error(f"Error loading knowledge graph: {e}")
    
    def save_graph(self):
        """Save graph to disk."""
        graph_file = os.path.join(self.storage_path, "knowledge_graph.json")
        
        try:
            data = {
                'nodes': self.nodes,
                'edges': dict(self.edges)
            }
            
            with open(graph_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved knowledge graph with {len(self.nodes)} nodes")
            return True
        except Exception as e:
            logger.error(f"Error saving knowledge graph: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics.
        
        Returns:
            Dictionary with graph statistics.
        """
        node_types = defaultdict(int)
        for node in self.nodes.values():
            node_types[node['type']] += 1
        
        edge_count = sum(len(edges) for edges in self.edges.values())
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': edge_count,
            'node_types': dict(node_types)
        }


class Tier4Storage:
    """Storage for semantic memory (tier 4) with knowledge graph integration."""
    
    def __init__(self, storage_path: str = "./data/tier4", enable_graph: bool = True):
        """Initialize tier 4 storage.
        
        Args:
            storage_path: Path to store tier 4 memory database.
            enable_graph: Whether to enable knowledge graph.
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Database path
        self.db_path = os.path.join(self.storage_path, "semantic_memories.db")
        
        # Database connection pool
        self.connection_pool = ConnectionPool(self.db_path)
        
        # Memory cache
        self.memory_cache = {}
        self.cache_lock = threading.Lock()
        self.cache_size = 100  # Max cache size
        
        # Knowledge graph
        self.enable_graph = enable_graph
        if enable_graph:
            self.knowledge_graph = Neo4jKnowledgeGraph(storage_path)
        
        # Initialize database
        self._init_db()
        
        logger.info("Tier4Storage initialized")
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.close_all()
        if hasattr(self, 'knowledge_graph') and hasattr(self.knowledge_graph, 'close'):
            self.knowledge_graph.close()
    
    def _init_db(self):
        """Initialize the database."""
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            # Create semantic memories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    memory_type TEXT,
                    content TEXT NOT NULL,
                    semantic_embedding TEXT,
                    entities TEXT,
                    relations TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    confidence REAL NOT NULL,
                    source TEXT NOT NULL,
                    context TEXT,
                    status TEXT DEFAULT 'active',
                    is_encrypted BOOLEAN DEFAULT FALSE,
                    encryption_key_id TEXT,
                    privacy_level INTEGER DEFAULT 0
                )
            ''')
            
            # Create index on type and status
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type_status ON semantic_memories (type, status)')
            
            # Create index on entities (for graph queries)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities ON semantic_memories (entities)')
            
            # Create index on last_accessed for faster sorting
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON semantic_memories (last_accessed)')
            
            # Create index on id for faster lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_id ON semantic_memories (id)')
            
            # Create index on memory_type
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON semantic_memories (memory_type)')
            
            # Create index on confidence
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON semantic_memories (confidence)')
            
            # Create index on source
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON semantic_memories (source)')
            
            conn.commit()
            self.connection_pool.return_connection(conn)
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
    
    def store_memory(self, memory: Dict[str, Any], entities: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Store a memory in tier 4 with semantic information.
        
        Args:
            memory: The memory to store.
            entities: Optional list of entities extracted from the memory.
            
        Returns:
            True if the memory was stored successfully, False otherwise.
        """
        try:
            # Get memory ID
            memory_id = memory.get('id')
            if not memory_id:
                return False
            
            # Ensure content is not None
            if not memory.get('content'):
                logger.warning(f"Memory {memory_id} has no content, skipping storage")
                return False
            
            # Ensure confidence is present
            if 'confidence' not in memory:
                memory['confidence'] = 0.5
            
            # Ensure source is present
            if 'source' not in memory:
                memory['source'] = 'unknown'
            
            current_time = get_current_time()
            
            # Add timestamps if not present
            if 'created_at' not in memory:
                memory['created_at'] = current_time
            memory['updated_at'] = current_time
            memory['last_accessed'] = current_time
            memory['access_count'] = 1
            memory['status'] = 'active'
            memory['is_encrypted'] = False
            memory['encryption_key_id'] = None
            memory['privacy_level'] = 0
            
            # Encrypt sensitive data
            content = memory.get('content', '')
            if content and encryption_manager.is_sensitive_data(content):
                # Create or use existing encryption key
                key_id = memory.get('encryption_key_id')
                if not key_id:
                    # Create a new key for each user or session
                    # In a real system, you would use a user-specific key
                    key_id = encryption_manager.create_key('default_password')
                
                # Encrypt content
                ciphertext, nonce, tag = encryption_manager.encrypt(content, key_id)
                # Store encrypted data as base64
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
            
            # Ensure memory_type field is present
            if 'memory_type' not in memory and 'type' in memory:
                memory['memory_type'] = memory['type']
            
            # Serialize entities and relations
            entities_json = json.dumps(entities) if entities else '[]'
            relations_json = json.dumps(memory.get('relations', []))
            
            # Retry mechanism for database locked errors
            max_retries = 3
            for retry in range(max_retries):
                try:
                    conn = self.connection_pool.get_connection()
                    cursor = conn.cursor()
                    
                    # Check table structure
                    cursor.execute("PRAGMA table_info(semantic_memories)")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    # Build dynamic SQL based on actual columns
                    base_columns = ['id', 'type', 'memory_type', 'content', 'semantic_embedding', 'entities', 'relations', 
                                  'created_at', 'updated_at', 'last_accessed', 'access_count', 'confidence', 
                                  'source', 'context', 'status']
                    optional_columns = ['is_encrypted', 'encryption_key_id', 'privacy_level']
                    
                    # Determine which columns to include
                    included_columns = base_columns.copy()
                    values = [
                        memory.get('id'),
                        memory.get('type'),
                        memory.get('memory_type'),
                        memory.get('content'),
                        memory.get('semantic_embedding', ''),
                        entities_json,
                        relations_json,
                        memory.get('created_at'),
                        memory.get('updated_at'),
                        memory.get('last_accessed'),
                        memory.get('access_count'),
                        memory.get('confidence'),
                        memory.get('source'),
                        memory.get('context'),
                        memory.get('status')
                    ]
                    
                    # Add optional columns if they exist
                    if 'is_encrypted' in columns:
                        included_columns.append('is_encrypted')
                        values.append(memory.get('is_encrypted', False))
                    if 'encryption_key_id' in columns:
                        included_columns.append('encryption_key_id')
                        values.append(memory.get('encryption_key_id'))
                    if 'privacy_level' in columns:
                        included_columns.append('privacy_level')
                        values.append(memory.get('privacy_level', 0))
                    
                    # Build SQL statement
                    columns_str = ', '.join(included_columns)
                    placeholders = ', '.join(['?' for _ in values])
                    
                    sql = f"""
                        INSERT OR REPLACE INTO semantic_memories 
                        ({columns_str})
                        VALUES ({placeholders})
                    """
                    
                    # Insert memory
                    cursor.execute(sql, values)
                    
                    conn.commit()
                    self.connection_pool.return_connection(conn)
                    break
                except sqlite3.OperationalError as e:
                    if 'database is locked' in str(e) and retry < max_retries - 1:
                        logger.warning(f"Database locked, retrying ({retry + 1}/{max_retries})...")
                        self.connection_pool.return_connection(conn)
                        import time
                        time.sleep(0.5)  # Wait before retrying
                    else:
                        raise
            
            # Add to memory cache
            # Create a copy of the memory with entities added
            cached_memory = memory.copy()
            cached_memory['entities'] = entities if entities else []
            cached_memory['relations'] = memory.get('relations', [])
            
            with self.cache_lock:
                self.memory_cache[memory_id] = cached_memory
                # Limit cache size
                if len(self.memory_cache) > self.cache_size:
                    # Remove oldest item
                    oldest_key = next(iter(self.memory_cache))
                    del self.memory_cache[oldest_key]
            
            # Add to knowledge graph (async to avoid blocking)
            if self.enable_graph:
                import threading
                threading.Thread(target=self._add_to_knowledge_graph, args=(memory, entities)).start()
            
            return True
        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
            return False
    
    def _add_to_knowledge_graph(self, memory: Dict[str, Any], entities: Optional[List[Dict[str, Any]]]):
        """Add memory and entities to knowledge graph.
        
        Args:
            memory: The memory to add.
            entities: List of entities extracted from the memory.
        """
        try:
            memory_id = memory.get('id')
            if not memory_id:
                return
            
            # 快速路径：如果知识图谱不可用，直接返回
            if not hasattr(self, 'knowledge_graph') or self.knowledge_graph is None:
                return
            
            # Add memory node
            self.knowledge_graph.add_node(
                memory_id,
                'memory',
                {
                    'content': memory.get('content', ''),
                    'memory_type': memory.get('memory_type', ''),
                    'confidence': memory.get('confidence', 0.0)
                }
            )
            
            # Add entity nodes and relationships
            if entities:
                for entity in entities:
                    entity_id = f"entity_{entity['text'].lower().replace(' ', '_')}"
                    
                    # Add entity node
                    self.knowledge_graph.add_node(
                        entity_id,
                        entity.get('type', 'unknown'),
                        {
                            'text': entity['text'],
                            'confidence': entity.get('confidence', 0.0)
                        }
                    )
                    
                    # Add relationship between memory and entity
                    self.knowledge_graph.add_edge(
                        memory_id,
                        entity_id,
                        'mentions',
                        entity.get('confidence', 0.5)
                    )
            
            # 批量保存：每100个记忆保存一次，而不是每次都保存
            # 这里使用一个简单的计数器来控制保存频率
            if not hasattr(self, '_graph_save_counter'):
                self._graph_save_counter = 0
            
            self._graph_save_counter += 1
            if self._graph_save_counter % 100 == 0:
                # Save graph
                self.knowledge_graph.save_graph()
                self._graph_save_counter = 0
            
        except Exception as e:
            logger.error(f"Error adding to knowledge graph: {e}")
    
    def retrieve_memories(self, query: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve memories from tier 4.
        
        Args:
            query: Optional query string to filter memories.
            limit: Maximum number of memories to return.
            
        Returns:
            A list of matching memories.
        """
        try:
            # Try to get from cache first if no query
            if not query:
                with self.cache_lock:
                    if self.memory_cache:
                        # Return most recent memories from cache
                        cached_memories = list(self.memory_cache.values())
                        # Sort by last_accessed
                        cached_memories.sort(key=lambda x: x.get('last_accessed', ''), reverse=True)
                        return cached_memories[:limit]
            
            conn = self.connection_pool.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if is_encrypted column exists
            cursor.execute("PRAGMA table_info(semantic_memories)")
            columns = [column[1] for column in cursor.fetchall()]
            has_is_encrypted = 'is_encrypted' in columns
            
            if has_is_encrypted:
                select_columns = 'id, type, memory_type, content, semantic_embedding, entities, relations, created_at, updated_at, last_accessed, access_count, confidence, source, context, status, is_encrypted, encryption_key_id, privacy_level'
            else:
                select_columns = 'id, type, memory_type, content, semantic_embedding, entities, relations, created_at, updated_at, last_accessed, access_count, confidence, source, context, status'
            
            if query:
                # Search in content with optimized query
                cursor.execute(f'''
                    SELECT {select_columns} 
                    FROM semantic_memories 
                    WHERE status = 'active' AND content LIKE ? 
                    ORDER BY last_accessed DESC 
                    LIMIT ?
                ''', (f'%{query}%', limit))
            else:
                # Get all active memories with optimized query
                cursor.execute(f'''
                    SELECT {select_columns} 
                    FROM semantic_memories 
                    WHERE status = 'active' 
                    ORDER BY last_accessed DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            self.connection_pool.return_connection(conn)
            
            # Convert rows to dictionaries
            memories = []
            for row in rows:
                memory = dict(row)
                # Parse JSON fields
                import json
                memory['entities'] = json.loads(memory.get('entities', '[]'))
                memory['relations'] = json.loads(memory.get('relations', '[]'))
                # Decrypt content if it's encrypted
                if has_is_encrypted and memory.get('is_encrypted'):
                    try:
                        content = memory.get('content', '')
                        if content:
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
                # Update cache
                with self.cache_lock:
                    self.memory_cache[memory['id']] = memory
                    # Limit cache size
                    if len(self.memory_cache) > self.cache_size:
                        # Remove oldest item
                        oldest_key = next(iter(self.memory_cache))
                        del self.memory_cache[oldest_key]
                memories.append(memory)
            
            return memories
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}", exc_info=True)
            return []
    
    def get_related_memories(self, memory_id: str, min_weight: float = 0.5) -> List[Dict[str, Any]]:
        """Get memories related to a given memory using knowledge graph.
        
        Args:
            memory_id: Memory ID.
            min_weight: Minimum relationship weight.
            
        Returns:
            List of related memories.
        """
        if not self.enable_graph:
            return []
        
        try:
            # Get related memory IDs from knowledge graph
            related = self.knowledge_graph.get_related_memories(memory_id, min_weight)
            
            if not related:
                return []
            
            # Retrieve full memory data
            related_ids = [r['memory_id'] for r in related]
            
            # Try to get from cache first
            cached_memories = []
            remaining_ids = []
            
            with self.cache_lock:
                for memory_id in related_ids:
                    if memory_id in self.memory_cache:
                        cached_memories.append(self.memory_cache[memory_id])
                    else:
                        remaining_ids.append(memory_id)
            
            # Get remaining from database
            db_memories = []
            if remaining_ids:
                conn = self.connection_pool.get_connection()
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                placeholders = ','.join(['?'] * len(remaining_ids))
                cursor.execute(f'''
                    SELECT * FROM semantic_memories 
                    WHERE status = 'active' AND id IN ({placeholders})
                ''', remaining_ids)
                
                rows = cursor.fetchall()
                self.connection_pool.return_connection(conn)
                
                for row in rows:
                    memory = dict(row)
                    memory['entities'] = json.loads(memory.get('entities', '[]'))
                    memory['relations'] = json.loads(memory.get('relations', '[]'))
                    # Update cache
                    with self.cache_lock:
                        self.memory_cache[memory['id']] = memory
                        # Limit cache size
                        if len(self.memory_cache) > self.cache_size:
                            # Remove oldest item
                            oldest_key = next(iter(self.memory_cache))
                            del self.memory_cache[oldest_key]
                    db_memories.append(memory)
            
            # Combine cached and database memories
            all_memories = cached_memories + db_memories
            
            # Build result with relationship info
            result = []
            for memory in all_memories:
                # Add relationship info
                relation_info = next((r for r in related if r['memory_id'] == memory['id']), None)
                if relation_info:
                    memory['relation'] = {
                        'type': relation_info['relation_type'],
                        'weight': relation_info['weight']
                    }
                
                result.append(memory)
            
            # Sort by relationship weight
            result.sort(key=lambda x: x.get('relation', {}).get('weight', 0), reverse=True)
            
            return result
        except Exception as e:
            logger.error(f"Error getting related memories: {e}", exc_info=True)
            return []
    
    def find_semantic_path(self, start_memory_id: str, end_memory_id: str) -> Optional[List[Dict[str, Any]]]:
        """Find a semantic path between two memories.
        
        Args:
            start_memory_id: Starting memory ID.
            end_memory_id: Target memory ID.
            
        Returns:
            Path as list of relationship steps, or None if no path found.
        """
        if not self.enable_graph:
            return None
        
        try:
            path = self.knowledge_graph.find_path(start_memory_id, end_memory_id)
            return path
        except Exception as e:
            logger.error(f"Error finding semantic path: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tier 4 storage.
        
        Returns:
            A dictionary with statistics.
        """
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            # Get total memories
            cursor.execute('SELECT COUNT(*) FROM semantic_memories')
            total = cursor.fetchone()[0]
            
            # Get active memories
            cursor.execute('SELECT COUNT(*) FROM semantic_memories WHERE status = ?', ('active',))
            active = cursor.fetchone()[0]
            
            # Get memory types
            cursor.execute('SELECT type, COUNT(*) FROM semantic_memories WHERE status = ? GROUP BY type', ('active',))
            types = {row[0]: row[1] for row in cursor.fetchall()}
            
            self.connection_pool.return_connection(conn)
            
            stats = {
                'total_memories': total,
                'active_memories': active,
                'memory_types': types
            }
            
            # Add graph stats if enabled
            if self.enable_graph:
                stats['knowledge_graph'] = self.knowledge_graph.get_stats()
            
            # Add cache stats
            with self.cache_lock:
                stats['cache'] = {
                    'size': len(self.memory_cache),
                    'max_size': self.cache_size
                }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {
                'total_memories': 0,
                'active_memories': 0,
                'memory_types': {}
            }
