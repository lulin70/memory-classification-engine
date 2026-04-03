import os
import sqlite3
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.helpers import get_current_time

class Tier4Storage:
    """Storage for semantic memory (tier 4)."""
    
    def __init__(self, storage_path: str = "./data/tier4"):
        """Initialize tier 4 storage.
        
        Args:
            storage_path: Path to store tier 4 memory database.
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Database path
        self.db_path = os.path.join(self.storage_path, "semantic_memories.db")
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create semantic entities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS semantic_entities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Create semantic relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS semantic_relationships (
                    id TEXT PRIMARY KEY,
                    subject_id TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    source TEXT NOT NULL,
                    context TEXT,
                    FOREIGN KEY (subject_id) REFERENCES semantic_entities(id),
                    FOREIGN KEY (object_id) REFERENCES semantic_entities(id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_entity_type ON semantic_entities (type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationship_subject ON semantic_relationships (subject_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationship_object ON semantic_relationships (object_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationship_predicate ON semantic_relationships (predicate)')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        """Store a memory in tier 4.
        
        Args:
            memory: The memory to store.
            
        Returns:
            True if the memory was stored successfully, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = get_current_time()
            
            # Store fact declaration
            if memory.get('type') == 'fact_declaration':
                # Extract entities and relationships from content
                # For simplicity, we'll store the fact as a relationship
                # In a real implementation, we would use NLP to extract entities
                
                # Create a subject entity
                subject_id = f"entity_{get_current_time().replace(':', '').replace('-', '').replace('T', '').replace('Z', '')}"
                cursor.execute('''
                    INSERT INTO semantic_entities 
                    (id, name, type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    subject_id,
                    "User",  # Assuming user is the subject
                    "person",
                    current_time,
                    current_time
                ))
                
                # Create an object entity
                object_id = f"entity_{get_current_time().replace(':', '').replace('-', '').replace('T', '').replace('Z', '')}_obj"
                cursor.execute('''
                    INSERT INTO semantic_entities 
                    (id, name, type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    object_id,
                    memory.get('content', '')[:50],  # Use first 50 chars as object name
                    "fact",
                    current_time,
                    current_time
                ))
                
                # Create a relationship
                relationship_id = memory.get('id')
                cursor.execute('''
                    INSERT INTO semantic_relationships 
                    (id, subject_id, predicate, object_id, created_at, updated_at, confidence, source, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    relationship_id,
                    subject_id,
                    "declares",
                    object_id,
                    current_time,
                    current_time,
                    memory.get('confidence', 1.0),
                    memory.get('source', 'user'),
                    memory.get('context')
                ))
            
            # Store relationship information
            elif memory.get('type') == 'relationship':
                # Extract entities and relationships from content
                # For simplicity, we'll store the relationship directly
                
                # Create subject and object entities if they don't exist
                # In a real implementation, we would use NLP to extract entities
                
                # Create a subject entity
                subject_id = f"entity_{get_current_time().replace(':', '').replace('-', '').replace('T', '').replace('Z', '')}"
                cursor.execute('''
                    INSERT INTO semantic_entities 
                    (id, name, type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    subject_id,
                    "Entity1",  # Placeholder
                    "entity",
                    current_time,
                    current_time
                ))
                
                # Create an object entity
                object_id = f"entity_{get_current_time().replace(':', '').replace('-', '').replace('T', '').replace('Z', '')}_obj"
                cursor.execute('''
                    INSERT INTO semantic_entities 
                    (id, name, type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    object_id,
                    "Entity2",  # Placeholder
                    "entity",
                    current_time,
                    current_time
                ))
                
                # Create a relationship
                relationship_id = memory.get('id')
                cursor.execute('''
                    INSERT INTO semantic_relationships 
                    (id, subject_id, predicate, object_id, created_at, updated_at, confidence, source, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    relationship_id,
                    subject_id,
                    "related_to",  # Placeholder
                    object_id,
                    current_time,
                    current_time,
                    memory.get('confidence', 1.0),
                    memory.get('source', 'user'),
                    memory.get('context')
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
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
                # Search for query in relationships
                cursor.execute('''
                    SELECT sr.*, se1.name as subject_name, se2.name as object_name 
                    FROM semantic_relationships sr
                    JOIN semantic_entities se1 ON sr.subject_id = se1.id
                    JOIN semantic_entities se2 ON sr.object_id = se2.id
                    WHERE sr.context LIKE ? OR se1.name LIKE ? OR se2.name LIKE ?
                    ORDER BY sr.created_at DESC
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            else:
                # Get all relationships
                cursor.execute('''
                    SELECT sr.*, se1.name as subject_name, se2.name as object_name 
                    FROM semantic_relationships sr
                    JOIN semantic_entities se1 ON sr.subject_id = se1.id
                    JOIN semantic_entities se2 ON sr.object_id = se2.id
                    ORDER BY sr.created_at DESC
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert rows to dictionaries
            memories = []
            for row in rows:
                memory_type = 'relationship' if row['predicate'] != 'declares' else 'fact_declaration'
                memory = {
                    'id': row['id'],
                    'type': memory_type,
                    'memory_type': memory_type,
                    'content': f"{row['subject_name']} {row['predicate']} {row['object_name']}",
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'confidence': row['confidence'],
                    'source': row['source'],
                    'context': row['context']
                }
                memories.append(memory)
            
            return memories
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory in tier 4.
        
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
                if key in ['confidence', 'context', 'source']:
                    set_clause.append(f"{key} = ?")
                    params.append(value)
            
            # Always update the updated_at timestamp
            set_clause.append("updated_at = ?")
            params.append(get_current_time())
            
            # Add memory_id to params
            params.append(memory_id)
            
            # Execute update
            cursor.execute(f'''
                UPDATE semantic_relationships 
                SET {', '.join(set_clause)} 
                WHERE id = ?
            ''', params)
            
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating memory: {e}")
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory from tier 4.
        
        Args:
            memory_id: The ID of the memory to delete.
            
        Returns:
            True if the memory was deleted successfully, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete the relationship
            cursor.execute('DELETE FROM semantic_relationships WHERE id = ?', (memory_id,))
            
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tier 4 storage.
        
        Returns:
            A dictionary with statistics.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total entities
            cursor.execute('SELECT COUNT(*) FROM semantic_entities')
            total_entities = cursor.fetchone()[0]
            
            # Get total relationships
            cursor.execute('SELECT COUNT(*) FROM semantic_relationships')
            total_relationships = cursor.fetchone()[0]
            
            # Get entity types
            cursor.execute('SELECT type, COUNT(*) FROM semantic_entities GROUP BY type')
            entity_types = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get relationship predicates
            cursor.execute('SELECT predicate, COUNT(*) FROM semantic_relationships GROUP BY predicate')
            predicates = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'total_entities': total_entities,
                'total_relationships': total_relationships,
                'entity_types': entity_types,
                'predicates': predicates
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_entities': 0,
                'total_relationships': 0,
                'entity_types': {},
                'predicates': {}
            }
