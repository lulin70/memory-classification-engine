"""Neo4j knowledge graph implementation for semantic memory storage."""

import os
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict
import threading

from neo4j import GraphDatabase, basic_auth
from memory_classification_engine.utils.helpers import get_current_time
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.config import ConfigManager


class Neo4jKnowledgeGraph:
    """Knowledge graph using Neo4j as backend."""
    
    def __init__(self, storage_path: str = "./data/tier4"):
        """Initialize the Neo4j knowledge graph.
        
        Args:
            storage_path: Path to store knowledge graph data (backup purposes).
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Load Neo4j configuration
        config_manager = ConfigManager()
        neo4j_config = config_manager.get('neo4j', {})
        
        self.neo4j_enabled = neo4j_config.get('enabled', True)
        if self.neo4j_enabled:
            self.uri = neo4j_config.get('uri', 'bolt://localhost:7687')
            self.user = neo4j_config.get('user', 'neo4j')
            self.password = neo4j_config.get('password', 'password')
            self.database = neo4j_config.get('database', 'neo4j')
            
            # Initialize Neo4j driver
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=basic_auth(self.user, self.password),
                    max_connection_pool_size=neo4j_config.get('connection_pool_size', 10),
                    max_transaction_retry_time=neo4j_config.get('max_transaction_retry_time', 30)
                )
                # Test connection
                with self.driver.session(database=self.database) as session:
                    session.run("RETURN 1")
                logger.info("Neo4j connection established")
                
                # Initialize schema
                self._init_schema()
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                self.neo4j_enabled = False
        
        # Fallback to in-memory storage if Neo4j is not available
        if not self.neo4j_enabled:
            logger.warning("Neo4j not available, falling back to in-memory storage")
            self.nodes = {}  # node_id -> node_data
            self.edges = defaultdict(list)  # node_id -> list of (target_id, relation_type, weight)
            self._load_graph()
        
        logger.info("Neo4jKnowledgeGraph initialized")
    
    def _init_schema(self):
        """Initialize Neo4j schema."""
        if not self.neo4j_enabled:
            return
        
        try:
            with self.driver.session(database=self.database) as session:
                # Create constraints for faster lookups
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE")
                session.run("CREATE INDEX IF NOT EXISTS FOR (n:Node) ON (n.type)")
                session.run("CREATE INDEX IF NOT EXISTS FOR ()-[r:RELATIONSHIP]->() ON (r.type)")
                logger.info("Neo4j schema initialized")
        except Exception as e:
            logger.error(f"Error initializing Neo4j schema: {e}")
    
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
            if self.neo4j_enabled:
                # Use Neo4j
                with self.driver.session(database=self.database) as session:
                    # Merge node (create if not exists, update if exists)
                    session.run(
                        """
                        MERGE (n:Node {id: $node_id})
                        SET n.type = $node_type,
                            n.properties = $properties,
                            n.created_at = COALESCE(n.created_at, $current_time),
                            n.updated_at = $current_time
                        """,
                        node_id=node_id,
                        node_type=node_type,
                        properties=properties,
                        current_time=get_current_time()
                    )
            else:
                # Fallback to in-memory
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
            if self.neo4j_enabled:
                # Use Neo4j
                with self.driver.session(database=self.database) as session:
                    # First ensure both nodes exist
                    session.run(
                        """
                        MERGE (s:Node {id: $source_id})
                        MERGE (t:Node {id: $target_id})
                        """,
                        source_id=source_id,
                        target_id=target_id
                    )
                    
                    # Create relationship
                    session.run(
                        """
                        MATCH (s:Node {id: $source_id}), (t:Node {id: $target_id})
                        MERGE (s)-[r:RELATIONSHIP {type: $relation_type}]->(t)
                        SET r.weight = $weight,
                            r.properties = $properties,
                            r.created_at = $current_time
                        """,
                        source_id=source_id,
                        target_id=target_id,
                        relation_type=relation_type,
                        weight=weight,
                        properties=properties or {},
                        current_time=get_current_time()
                    )
                    
                    # Update node timestamps
                    session.run(
                        """
                        MATCH (n:Node) WHERE n.id IN [$source_id, $target_id]
                        SET n.updated_at = $current_time
                        """,
                        source_id=source_id,
                        target_id=target_id,
                        current_time=get_current_time()
                    )
            else:
                # Fallback to in-memory
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
        try:
            if self.neo4j_enabled:
                # Use Neo4j
                with self.driver.session(database=self.database) as session:
                    result = session.run(
                        """
                        MATCH (n:Node {id: $node_id})
                        RETURN n.id as id, n.type as type, n.properties as properties, n.created_at as created_at, n.updated_at as updated_at
                        """,
                        node_id=node_id
                    )
                    
                    record = result.single()
                    if record:
                        return {
                            'id': record['id'],
                            'type': record['type'],
                            'properties': record['properties'],
                            'created_at': record['created_at'],
                            'updated_at': record['updated_at']
                        }
                    return None
            else:
                # Fallback to in-memory
                return self.nodes.get(node_id)
        except Exception as e:
            logger.error(f"Error getting node {node_id}: {e}")
            return None
    
    def get_neighbors(self, node_id: str, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get neighboring nodes.
        
        Args:
            node_id: Node ID.
            relation_type: Optional relation type filter.
            
        Returns:
            List of neighboring nodes with relationship info.
        """
        try:
            if self.neo4j_enabled:
                # Use Neo4j
                with self.driver.session(database=self.database) as session:
                    if relation_type:
                        result = session.run(
                            """
                            MATCH (s:Node {id: $node_id})-[r:RELATIONSHIP {type: $relation_type}]->(t:Node)
                            RETURN t.id as target_id, t.type as target_type, t.properties as target_properties, 
                                   t.created_at as target_created_at, t.updated_at as target_updated_at,
                                   r.type as relation_type, r.weight as relation_weight, r.properties as relation_properties, r.created_at as relation_created_at
                            """,
                            node_id=node_id,
                            relation_type=relation_type
                        )
                    else:
                        result = session.run(
                            """
                            MATCH (s:Node {id: $node_id})-[r:RELATIONSHIP]->(t:Node)
                            RETURN t.id as target_id, t.type as target_type, t.properties as target_properties, 
                                   t.created_at as target_created_at, t.updated_at as target_updated_at,
                                   r.type as relation_type, r.weight as relation_weight, r.properties as relation_properties, r.created_at as relation_created_at
                            """,
                            node_id=node_id
                        )
                    
                    neighbors = []
                    for record in result:
                        neighbors.append({
                            'node': {
                                'id': record['target_id'],
                                'type': record['target_type'],
                                'properties': record['target_properties'],
                                'created_at': record['target_created_at'],
                                'updated_at': record['target_updated_at']
                            },
                            'relation': {
                                'target_id': record['target_id'],
                                'relation_type': record['relation_type'],
                                'weight': record['relation_weight'],
                                'properties': record['relation_properties'],
                                'created_at': record['relation_created_at']
                            }
                        })
                    return neighbors
            else:
                # Fallback to in-memory
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
        except Exception as e:
            logger.error(f"Error getting neighbors for node {node_id}: {e}")
            return []
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 3) -> Optional[List[Dict[str, Any]]]:
        """Find a path between two nodes using BFS.
        
        Args:
            start_id: Starting node ID.
            end_id: Target node ID.
            max_depth: Maximum search depth.
            
        Returns:
            Path as list of edges, or None if no path found.
        """
        try:
            if self.neo4j_enabled:
                # Use Neo4j's built-in path finding
                with self.driver.session(database=self.database) as session:
                    result = session.run(
                        """
                        MATCH path = shortestPath((s:Node {id: $start_id})-[*1..$max_depth]->(t:Node {id: $end_id}))
                        UNWIND relationships(path) AS r
                        RETURN r.type as type, r.weight as weight, r.properties as properties, r.created_at as created_at
                        """,
                        start_id=start_id,
                        end_id=end_id,
                        max_depth=max_depth
                    )
                    
                    path = []
                    for record in result:
                        path.append({
                            'relation_type': record['type'],
                            'weight': record['weight'],
                            'properties': record['properties'],
                            'created_at': record['created_at']
                        })
                    
                    return path if path else None
            else:
                # Fallback to in-memory BFS
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
        except Exception as e:
            logger.error(f"Error finding path between {start_id} and {end_id}: {e}")
            return None
    
    def get_related_memories(self, memory_id: str, min_weight: float = 0.5) -> List[Dict[str, Any]]:
        """Get memories related to a given memory.
        
        Args:
            memory_id: Memory ID.
            min_weight: Minimum relationship weight.
            
        Returns:
            List of related memories.
        """
        try:
            if self.neo4j_enabled:
                # Use Neo4j
                with self.driver.session(database=self.database) as session:
                    result = session.run(
                        """
                        MATCH (m:Node {id: $memory_id})-[r:RELATIONSHIP]->(n:Node {type: 'memory'})
                        WHERE r.weight >= $min_weight
                        RETURN n.id as memory_id, r.type as relation_type, r.weight as weight, n.properties as properties
                        ORDER BY r.weight DESC
                        """,
                        memory_id=memory_id,
                        min_weight=min_weight
                    )
                    
                    related = []
                    for record in result:
                        related.append({
                            'memory_id': record['memory_id'],
                            'relation_type': record['relation_type'],
                            'weight': record['weight'],
                            'properties': record['properties']
                        })
                    return related
            else:
                # Fallback to in-memory
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
        except Exception as e:
            logger.error(f"Error getting related memories for {memory_id}: {e}")
            return []
    
    def _load_graph(self):
        """Load graph from disk (fallback only)."""
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
        """Save graph to disk (fallback only)."""
        if not self.neo4j_enabled:
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
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics.
        
        Returns:
            Dictionary with graph statistics.
        """
        try:
            if self.neo4j_enabled:
                # Use Neo4j
                with self.driver.session(database=self.database) as session:
                    # Get total nodes
                    node_count_result = session.run("MATCH (n:Node) RETURN count(n) as count")
                    total_nodes = node_count_result.single()['count']
                    
                    # Get node types
                    node_types_result = session.run(
                        "MATCH (n:Node) RETURN n.type as type, count(n) as count GROUP BY n.type"
                    )
                    node_types = {record['type']: record['count'] for record in node_types_result}
                    
                    # Get total edges
                    edge_count_result = session.run("MATCH ()-[r:RELATIONSHIP]->() RETURN count(r) as count")
                    total_edges = edge_count_result.single()['count']
            else:
                # Fallback to in-memory
                node_types = defaultdict(int)
                for node in self.nodes.values():
                    node_types[node['type']] += 1
                
                total_nodes = len(self.nodes)
                total_edges = sum(len(edges) for edges in self.edges.values())
            
            return {
                'total_nodes': total_nodes,
                'total_edges': total_edges,
                'node_types': dict(node_types),
                'backend': 'neo4j' if self.neo4j_enabled else 'in-memory'
            }
        except Exception as e:
            logger.error(f"Error getting graph stats: {e}")
            return {
                'total_nodes': 0,
                'total_edges': 0,
                'node_types': {},
                'backend': 'in-memory'
            }
    
    def close(self):
        """Close Neo4j driver."""
        if self.neo4j_enabled and hasattr(self, 'driver'):
            try:
                self.driver.close()
                logger.info("Neo4j driver closed")
            except Exception as e:
                logger.error(f"Error closing Neo4j driver: {e}")
