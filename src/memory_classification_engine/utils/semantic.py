"""Semantic utility functions for memory association."""

import numpy as np
from typing import List, Optional, Any, Dict
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.cache import MemoryCache

# Try to import sentence transformers
SENTENCE_TRANSFORMERS_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available, using fallback semantic analysis")


class SemanticUtility:
    """Semantic utility class for memory association."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one instance."""
        if cls._instance is None:
            cls._instance = super(SemanticUtility, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', cache_size: int = 1000, cache_ttl: int = 3600):
        """Initialize semantic utility.
        
        Args:
            model_name: Name of the sentence transformer model.
            cache_size: Maximum cache size for semantic calculations.
            cache_ttl: Cache time-to-live in seconds.
        """
        if not hasattr(self, 'initialized'):
            self.model_name = model_name
            self.model = None
            # Use SmartCache for better performance
            from memory_classification_engine.utils.cache import SmartCache
            cache_config = {
                'tier1': {
                    'max_size': cache_size,
                    'ttl': cache_ttl
                },
                'tier2': {
                    'cache_dir': ".cache/semantic",
                    'ttl': cache_ttl * 24  # Longer TTL for file cache
                }
            }
            self.cache = SmartCache(cache_config)
            self._initialize_model()
            self.initialized = True
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded sentence transformer model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to load model {self.model_name}: {e}")
                self.model = None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score between 0 and 1.
        """
        # 快速路径：如果文本相同，直接返回1.0
        if text1 == text2:
            return 1.0
        
        # 快速路径：如果任一文本为空，直接返回0.0
        if not text1 or not text2:
            return 0.0
        
        # 生成缓存键（排序以确保 (a,b) 和 (b,a) 使用相同的键）
        if text1 <= text2:
            cache_key = f"similarity:{text1}:{text2}"
        else:
            cache_key = f"similarity:{text2}:{text1}"
        
        # 检查缓存
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        similarity = 0.0
        
        # 先使用词袋模型计算相似度，如果相似度较低，再使用句子转换器
        # 这样可以避免在明显不相似的文本上使用昂贵的模型计算
        bow_similarity = self._calculate_bag_of_words_similarity(text1, text2)
        
        # 如果词袋相似度已经很高，直接使用
        if bow_similarity > 0.7:
            similarity = bow_similarity
        elif self.model:
            try:
                # 使用句子转换器计算语义相似度
                embeddings = self.model.encode([text1, text2])
                similarity = self._cosine_similarity(embeddings[0], embeddings[1])
            except Exception as e:
                logger.error(f"Error calculating similarity with model: {e}")
                # 回退到词袋相似度
                similarity = bow_similarity
        else:
            # 回退到词袋相似度
            similarity = bow_similarity
        
        # 存储结果到缓存
        self.cache.set(cache_key, similarity)
        
        return similarity
    
    def encode_text(self, text: str) -> Optional[np.ndarray]:
        """Encode text to vector embedding.
        
        Args:
            text: Text to encode.
            
        Returns:
            Vector embedding or None if encoding fails.
        """
        # Generate cache key
        cache_key = f"embedding:{text}"
        
        # Check if embedding is in cache
        cached_embedding = self.cache.get(cache_key)
        if cached_embedding is not None:
            return np.array(cached_embedding)
        
        if self.model:
            try:
                embedding = self.model.encode(text)
                # Store in cache
                self.cache.set(cache_key, embedding.tolist())
                return embedding
            except Exception as e:
                logger.error(f"Error encoding text: {e}")
        
        return None
    
    def batch_encode_texts(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Encode multiple texts to vector embeddings.
        
        Args:
            texts: List of texts to encode.
            
        Returns:
            List of vector embeddings.
        """
        embeddings = []
        
        if self.model:
            try:
                # Check cache first
                uncached_texts = []
                uncached_indices = []
                
                for i, text in enumerate(texts):
                    cache_key = f"embedding:{text}"
                    cached_embedding = self.cache.get(cache_key)
                    if cached_embedding is not None:
                        embeddings.append(np.array(cached_embedding))
                    else:
                        uncached_texts.append(text)
                        uncached_indices.append(i)
                
                # Encode uncached texts in batch
                if uncached_texts:
                    batch_embeddings = self.model.encode(uncached_texts)
                    for i, idx in enumerate(uncached_indices):
                        embedding = batch_embeddings[i]
                        embeddings.insert(idx, embedding)
                        # Store in cache
                        cache_key = f"embedding:{uncached_texts[i]}"
                        self.cache.set(cache_key, embedding.tolist())
                
                return embeddings
            except Exception as e:
                logger.error(f"Error batch encoding texts: {e}")
        
        # Fall back to individual encoding
        for text in texts:
            embeddings.append(self.encode_text(text))
        
        return embeddings
    
    def find_similar_texts(self, query: str, texts: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find most similar texts to a query.
        
        Args:
            query: Query text.
            texts: List of texts to search.
            top_k: Number of top results to return.
            
        Returns:
            List of dictionaries with text, similarity score, and index.
        """
        if not texts:
            return []
        
        # Generate cache key
        cache_key = f"find_similar:{query}:{','.join(texts[:10])}...{len(texts)}"
        
        # Check if result is in cache
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Calculate similarities
        similarities = []
        for i, text in enumerate(texts):
            similarity = self.calculate_similarity(query, text)
            similarities.append({
                'text': text,
                'similarity': similarity,
                'index': i
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Get top k results
        top_results = similarities[:top_k]
        
        # Store in cache
        self.cache.set(cache_key, top_results)
        
        return top_results
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector.
            vec2: Second vector.
            
        Returns:
            Cosine similarity score.
        """
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        
        return dot_product / (norm_vec1 * norm_vec2)
    
    def _calculate_bag_of_words_similarity(self, text1: str, text2: str) -> float:
        """Calculate bag-of-words similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score between 0 and 1.
        """
        # Tokenize texts
        def tokenize(text):
            return set(word.lower() for word in text.split() if word.isalnum())
        
        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)
        
        if not tokens1 and not tokens2:
            return 1.0
        
        # Calculate Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0
    
    def clear_cache(self):
        """Clear the semantic cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Cache statistics.
        """
        return self.cache.get_stats()


# Global instance
semantic_utility = SemanticUtility()
