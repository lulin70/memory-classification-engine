"""Tier 4 semantic memory storage with knowledge graph."""

import os
import sqlite3
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict

from memory_classification_engine.utils.helpers import get_current_time
from memory_classification_engine.utils.logger import logger


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
        
        # Knowledge graph
        self.enable_graph = enable_graph
        if enable_graph:
            self.knowledge_graph = KnowledgeGraph(storage_path)
        
        # Initialize database
        self._init_db()
        
        logger.info("Tier4Storage initialized")
    
    def _init_db(self):
        """Initialize the database."""
        try:
            conn = sqlite3.connect(self.db_path)
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
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Create index on type and status
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type_status ON semantic_memories (type, status)')
            
            # Create index on entities (for graph queries)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities ON semantic_memories (entities)')
            
            conn.commit()
            conn.close()
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
            
            # Serialize entities and relations
            entities_json = json.dumps(entities) if entities else '[]'
            relations_json = json.dumps(memory.get('relations', []))
            
            # Insert memory
            cursor.execute('''
                INSERT INTO semantic_memories 
                (id, type, memory_type, content, semantic_embedding, entities, relations, created_at, updated_at, last_accessed, access_count, confidence, source, context, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
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
            ))
            
            conn.commit()
            conn.close()
            
            # Add to knowledge graph
            if self.enable_graph:
                self._add_to_knowledge_graph(memory, entities)
            
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
            
            # Save graph
            self.knowledge_graph.save_graph()
            
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
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if query:
                # Search in content
                cursor.execute('''
                    SELECT * FROM semantic_memories 
                    WHERE status = 'active' AND content LIKE ? 
                    ORDER BY last_accessed DESC 
                    LIMIT ?
                ''', (f'%{query}%', limit))
            else:
                # Get all active memories
                cursor.execute('''
                    SELECT * FROM semantic_memories 
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
                # Parse JSON fields
                memory['entities'] = json.loads(memory.get('entities', '[]'))
                memory['relations'] = json.loads(memory.get('relations', '[]'))
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
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            placeholders = ','.join(['?'] * len(related_ids))
            cursor.execute(f'''
                SELECT * FROM semantic_memories 
                WHERE status = 'active' AND id IN ({placeholders})
            ''', related_ids)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Build result with relationship info
            memories = []
            for row in rows:
                memory = dict(row)
                memory['entities'] = json.loads(memory.get('entities', '[]'))
                memory['relations'] = json.loads(memory.get('relations', '[]'))
                
                # Add relationship info
                relation_info = next((r for r in related if r['memory_id'] == memory['id']), None)
                if relation_info:
                    memory['relation'] = {
                        'type': relation_info['relation_type'],
                        'weight': relation_info['weight']
                    }
                
                memories.append(memory)
            
            # Sort by relationship weight
            memories.sort(key=lambda x: x.get('relation', {}).get('weight', 0), reverse=True)
            
            return memories
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
            conn = sqlite3.connect(self.db_path)
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
            
            conn.close()
            
            stats = {
                'total_memories': total,
                'active_memories': active,
                'memory_types': types
            }
            
            # Add graph stats if enabled
            if self.enable_graph:
                stats['knowledge_graph'] = self.knowledge_graph.get_stats()
            
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {
                'total_memories': 0,
                'active_memories': 0,
                'memory_types': {}
            }
