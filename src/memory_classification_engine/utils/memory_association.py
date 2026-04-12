"""Memory association manager for semantic memory connections."""

import os
import json
import threading
from typing import List, Dict, Optional, Any
from datetime import datetime
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.semantic import semantic_utility
from memory_classification_engine.utils.cache import MemoryCache


class MemoryAssociationManager:
    """Manager for memory associations based on semantic similarity."""
    
    _instance = None
    _lock = threading.RLock()  # Comment in Chinese removedtions
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MemoryAssociationManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, storage_path: str = "./data/associations", cache_size: int = 1000, cache_ttl: int = 3600):
        """Initialize memory association manager.
        
        Args:
            storage_path: Path to store association data.
            cache_size: Maximum cache size for associations.
            cache_ttl: Cache time-to-live in seconds.
        """
        if not hasattr(self, 'initialized'):
            with self._lock:
                if not hasattr(self, 'initialized'):
                    self.storage_path = storage_path
                    os.makedirs(self.storage_path, exist_ok=True)
                    self.associations_file = os.path.join(self.storage_path, "associations.json")
                    # Comment in Chinese removed
                    from memory_classification_engine.utils.cache import SmartCache
                    cache_config = {
                        'tier1': {
                            'max_size': cache_size,
                            'ttl': cache_ttl
                        },
                        'tier2': {
                            'cache_dir': ".cache/associations",
                            'ttl': cache_ttl * 24  # Comment in Chinese removed
                        }
                    }
                    self.cache = SmartCache(cache_config)
                    self.associations = self._load_associations()
                    self.initialized = True
                    self._save_pending = False  # Comment in Chinese removed
    
    def _load_associations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load associations from file.
        
        Returns:
            Dictionary of associations.
        """
        if os.path.exists(self.associations_file):
            try:
                with open(self.associations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading associations: {e}")
                return {}
        return {}
    
    def _save_associations(self):
        """Save associations to file."""
        try:
            # Comment in Chinese removedving
            os.makedirs(os.path.dirname(self.associations_file), exist_ok=True)
            # Comment in Chinese removedtion
            with self._lock:
                associations_copy = self.associations.copy()
            with open(self.associations_file, 'w', encoding='utf-8') as f:
                json.dump(associations_copy, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving associations: {e}")
    
    def create_association(self, memory_id1: str, memory_id2: str, similarity: float, metadata: Optional[Dict[str, Any]] = None):
        """Create an association between two memories.
        
        Args:
            memory_id1: First memory ID.
            memory_id2: Second memory ID.
            similarity: Semantic similarity score.
            metadata: Optional metadata about the association.
        """
        with self._lock:
            # Comment in Chinese removedtions
            for source_id, target_id in [(memory_id1, memory_id2), (memory_id2, memory_id1)]:
                if source_id not in self.associations:
                    self.associations[source_id] = []
                
                # Comment in Chinese removedxists
                existing = False
                for assoc in self.associations[source_id]:
                    if assoc['target_id'] == target_id:
                        # Comment in Chinese removedtion
                        assoc['similarity'] = similarity
                        assoc['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                        if metadata:
                            assoc['metadata'] = metadata
                        existing = True
                        break
                
                if not existing:
                    # Comment in Chinese removedtion
                    association = {
                        'target_id': target_id,
                        'similarity': similarity,
                        'created_at': datetime.utcnow().isoformat() + 'Z',
                        'updated_at': datetime.utcnow().isoformat() + 'Z'
                    }
                    if metadata:
                        association['metadata'] = metadata
                    self.associations[source_id].append(association)
        
        # Comment in Chinese removedtions
        self._save_associations()
        # Comment in Chinese removed
        self.cache.clear()
    
    def get_associations(self, memory_id: str, min_similarity: float = 0.5, limit: int = 10) -> List[Dict[str, Any]]:
        """Get associations for a memory.
        
        Args:
            memory_id: Memory ID to get associations for.
            min_similarity: Minimum similarity score for associations.
            limit: Maximum number of associations to return.
            
        Returns:
            List of associations sorted by similarity.
        """
        # Comment in Chinese removedy
        cache_key = f"associations:{memory_id}:{min_similarity}:{limit}"
        
        # Comment in Chinese removed
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        associations = []
        with self._lock:
            if memory_id in self.associations:
                # Comment in Chinese removedrity
                filtered = [assoc for assoc in self.associations[memory_id] if assoc['similarity'] >= min_similarity]
                # Comment in Chinese removedrity
                filtered.sort(key=lambda x: x['similarity'], reverse=True)
                # Comment in Chinese removedlts
                associations = filtered[:limit]
        
        # Comment in Chinese removed
        self.cache.set(cache_key, associations)
        
        return associations
    
    def build_associations(self, memories: List[Dict[str, Any]], min_similarity: float = 0.6):
        """Build associations between a list of memories.
        
        Args:
            memories: List of memories to build associations for.
            min_similarity: Minimum similarity score for associations.
        """
        if len(memories) < 2:
            return
        
        # Comment in Chinese removedtion
        memory_texts = {}
        for memory in memories:
            memory_id = memory.get('id')
            content = memory.get('content', '')
            if memory_id and content:
                memory_texts[memory_id] = content
        
        # Comment in Chinese removeds
        memory_ids = list(memory_texts.keys())
        for i, id1 in enumerate(memory_ids):
            for j, id2 in enumerate(memory_ids):
                if i >= j:  # Comment in Chinese removedtions
                    continue
                
                text1 = memory_texts[id1]
                text2 = memory_texts[id2]
                
                # Comment in Chinese removedrity
                similarity = semantic_utility.calculate_similarity(text1, text2)
                
                if similarity >= min_similarity:
                    # Comment in Chinese removedtion
                    metadata = {
                        'memory1_type': memories[i].get('memory_type', ''),
                        'memory2_type': memories[j].get('memory_type', ''),
                        'memory1_tier': memories[i].get('tier', 3),
                        'memory2_tier': memories[j].get('tier', 3)
                    }
                    self.create_association(id1, id2, similarity, metadata)
    
    def update_memory_associations(self, memory: Dict[str, Any], all_memories: List[Dict[str, Any]], min_similarity: float = 0.6):
        """Update associations for a single memory against all other memories.
        
        Args:
            memory: The memory to update associations for.
            all_memories: List of all memories to compare against.
            min_similarity: Minimum similarity score for associations.
        """
        memory_id = memory.get('id')
        if not memory_id:
            return
        
        memory_content = memory.get('content', '')
        if not memory_content:
            return
        
        # Comment in Chinese removeds
        for other_memory in all_memories:
            other_id = other_memory.get('id')
            if not other_id or other_id == memory_id:
                continue
            
            other_content = other_memory.get('content', '')
            if not other_content:
                continue
            
            # Comment in Chinese removedrity
            similarity = semantic_utility.calculate_similarity(memory_content, other_content)
            
            if similarity >= min_similarity:
                # Comment in Chinese removedtion
                metadata = {
                    'memory1_type': memory.get('memory_type', ''),
                    'memory2_type': other_memory.get('memory_type', ''),
                    'memory1_tier': memory.get('tier', 3),
                    'memory2_tier': other_memory.get('tier', 3)
                }
                self.create_association(memory_id, other_id, similarity, metadata)
    
    def remove_association(self, memory_id1: str, memory_id2: str):
        """Remove an association between two memories.
        
        Args:
            memory_id1: First memory ID.
            memory_id2: Second memory ID.
        """
        with self._lock:
            # Comment in Chinese removedctions
            for source_id, target_id in [(memory_id1, memory_id2), (memory_id2, memory_id1)]:
                if source_id in self.associations:
                    self.associations[source_id] = [
                        assoc for assoc in self.associations[source_id] 
                        if assoc['target_id'] != target_id
                    ]
                    # Comment in Chinese removedtion lists
                    if not self.associations[source_id]:
                        del self.associations[source_id]
        
        # Comment in Chinese removedtions
        self._save_associations()
        # Comment in Chinese removed
        self.cache.clear()
    
    def remove_memory_associations(self, memory_id: str):
        """Remove all associations for a memory.
        
        Args:
            memory_id: Memory ID to remove associations for.
        """
        with self._lock:
            # Comment in Chinese removed
            if memory_id in self.associations:
                del self.associations[memory_id]
            
            # Comment in Chinese removedt
            for source_id in list(self.associations.keys()):
                self.associations[source_id] = [
                    assoc for assoc in self.associations[source_id] 
                    if assoc['target_id'] != memory_id
                ]
                # Comment in Chinese removedtion lists
                if not self.associations[source_id]:
                    del self.associations[source_id]
        
        # Comment in Chinese removedtions
        self._save_associations()
        # Comment in Chinese removed
        self.cache.clear()
    
    def get_similar_memories(self, memory: Dict[str, Any], all_memories: List[Dict[str, Any]], top_k: int = 5, min_similarity: float = 0.6) -> List[Dict[str, Any]]:
        """Get similar memories based on semantic similarity.
        
        Args:
            memory: The memory to find similar memories for.
            all_memories: List of all memories to compare against.
            top_k: Number of top similar memories to return.
            min_similarity: Minimum similarity score.
            
        Returns:
            List of similar memories sorted by similarity.
        """
        memory_id = memory.get('id')
        memory_content = memory.get('content', '')
        if not memory_content:
            return []
        
        # Comment in Chinese removeds
        similarities = []
        for other_memory in all_memories:
            other_id = other_memory.get('id')
            if not other_id or other_id == memory_id:
                continue
            
            other_content = other_memory.get('content', '')
            if not other_content:
                continue
            
            similarity = semantic_utility.calculate_similarity(memory_content, other_content)
            if similarity >= min_similarity:
                similarities.append({
                    'memory': other_memory,
                    'similarity': similarity
                })
        
        # Comment in Chinese removedrity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Comment in Chinese removedlts
        top_similar = similarities[:top_k]
        
        # Comment in Chinese removeds
        return [item['memory'] for item in top_similar]
    
    def get_memory_clusters(self, memories: List[Dict[str, Any]], min_similarity: float = 0.7) -> List[List[Dict[str, Any]]]:
        """Cluster memories based on semantic similarity.
        
        Args:
            memories: List of memories to cluster.
            min_similarity: Minimum similarity score for clustering.
            
        Returns:
            List of memory clusters.
        """
        from sklearn.cluster import DBSCAN
        import numpy as np
        
        # Comment in Chinese removednt
        memories_with_content = [m for m in memories if m.get('content')]
        if not memories_with_content:
            return []
        
        # Comment in Chinese removedddings
        texts = [m['content'] for m in memories_with_content]
        embeddings = semantic_utility.batch_encode_texts(texts)
        
        # Comment in Chinese removedddings
        valid_embeddings = []
        valid_memories = []
        for i, emb in enumerate(embeddings):
            if emb is not None:
                valid_embeddings.append(emb)
                valid_memories.append(memories_with_content[i])
        
        if len(valid_embeddings) < 2:
            return [valid_memories] if valid_memories else []
        
        # Comment in Chinese removedy
        X = np.array(valid_embeddings)
        
        # Comment in Chinese removedring
        # Comment in Chinese removedighborhood
        # Comment in Chinese removed point
        dbscan = DBSCAN(eps=0.3, min_samples=2, metric='cosine')
        clusters = dbscan.fit_predict(X)
        
        # Comment in Chinese removedr
        cluster_dict = {}
        for i, cluster_id in enumerate(clusters):
            if cluster_id not in cluster_dict:
                cluster_dict[cluster_id] = []
            cluster_dict[cluster_id].append(valid_memories[i])
        
        # Comment in Chinese removedrs
        return list(cluster_dict.values())
    
    def clear_all_associations(self):
        """Clear all associations."""
        self.associations = {}
        self._save_associations()
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about associations.
        
        Returns:
            Dictionary of statistics.
        """
        total_associations = 0
        memory_count = len(self.associations)
        
        for memory_id, assocs in self.associations.items():
            total_associations += len(assocs)
        
        return {
            'total_associations': total_associations,
            'memory_count': memory_count,
            'average_associations_per_memory': total_associations / memory_count if memory_count > 0 else 0
        }


# Comment in Chinese removed
memory_association_manager = MemoryAssociationManager()
