from typing import List, Dict, Any
from memory_classification_engine.utils.logger import logger

class SemanticUtility:
    def __init__(self, config):
        self.config = config
        self.embedding_model = self._init_embedding_model()
    
    def _init_embedding_model(self):
        """初始化嵌入模型"""
        try:
            # 尝试使用sentence-transformers
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback semantic analysis")
            return None
    
    def calculate_similarity(self, text1, text2):
        """计算两个文本的语义相似度"""
        if not self.embedding_model:
            # 回退到简单的字符串相似度
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1, text2).ratio()
        
        try:
            # 使用嵌入模型计算相似度
            embeddings = self.embedding_model.encode([text1, text2])
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return similarity
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            # 回退到简单的字符串相似度
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1, text2).ratio()
    
    def extract_keywords(self, text):
        """提取文本的关键词"""
        try:
            # 使用NLTK或spaCy提取关键词
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from collections import Counter
            
            # 下载必要的资源
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # 分词
            tokens = word_tokenize(text.lower())
            
            # 过滤停用词
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
            
            # 计算词频
            word_counts = Counter(filtered_tokens)
            
            # 返回前5个关键词
            return [word for word, _ in word_counts.most_common(5)]
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def detect_language(self, text):
        """检测文本的语言"""
        try:
            import langdetect
            return langdetect.detect(text)
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'

# 创建全局实例
semantic_utility = SemanticUtility({})
