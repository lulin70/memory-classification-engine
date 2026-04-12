from typing import List, Dict, Any
from memory_classification_engine.utils.logger import logger

class SemanticUtility:
    def __init__(self, config):
        self.config = config
        self.embedding_model = self._init_embedding_model()
    
    def _init_embedding_model(self):
        """初始化嵌入模型"""
        try:
            from sentence_transformers import SentenceTransformer
            import os
            
            # 获取模型名称
            model_name = self.config.get('semantic.model_name', 'all-MiniLM-L6-v2')
            
            # 尝试从本地路径加载模型
            local_model_paths = [
                os.path.join('.', 'models', model_name),
                os.path.join('.', 'models', f'models--sentence-transformers--{model_name}'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', model_name),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', f'models--sentence-transformers--{model_name}')
            ]
            
            for local_path in local_model_paths:
                if os.path.exists(local_path):
                    logger.info(f"Loading model from local path: {local_path}")
                    return SentenceTransformer(local_path)
            
            # 如果本地路径不存在，尝试从 Hugging Face 下载
            logger.info(f"Loading model from Hugging Face: sentence-transformers/{model_name}")
            return SentenceTransformer(f'sentence-transformers/{model_name}')
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback semantic analysis")
            return None
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}, using fallback semantic analysis")
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
            # Comment in Chinese removedy提取关键词
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
            
            # Comment in Chinese removed个关键词
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
