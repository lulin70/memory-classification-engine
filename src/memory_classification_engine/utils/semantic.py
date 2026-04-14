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
            
            # 检查是否在离线模式
            offline_mode = os.environ.get('HF_DATASETS_OFFLINE') == '1' or os.environ.get('HF_EVALUATE_OFFLINE') == '1'
            
            # 获取模型名称
            model_name = self.config.get('semantic.model_name', 'all-MiniLM-L6-v2')
            
            # 尝试从本地路径加载模型
            local_model_paths = [
                os.path.join('.', 'models', model_name),
                os.path.join('.', 'models', f'models--sentence-transformers--{model_name}'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', model_name),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', f'models--sentence-transformers--{model_name}'),
                '/Users/lin/trae_projects/memory-classification-engine/models',
                '/Users/lin/trae_projects/memory-classification-engine/models/models--sentence-transformers--all-MiniLM-L6-v2'
            ]
            
            for local_path in local_model_paths:
                if os.path.exists(local_path):
                    # 检查是否是目录
                    if os.path.isdir(local_path):
                        # 检查是否包含 snapshots 目录
                        snapshots_dir = os.path.join(local_path, 'snapshots')
                        if os.path.exists(snapshots_dir):
                            # 列出 snapshots 目录中的所有子目录
                            import glob
                            snapshot_paths = glob.glob(os.path.join(snapshots_dir, '*'))
                            if snapshot_paths:
                                # 选择第一个快照目录
                                snapshot_path = snapshot_paths[0]
                                logger.info(f"Loading model from snapshot path: {snapshot_path}")
                                return SentenceTransformer(snapshot_path)
                        # 如果没有 snapshots 目录，尝试直接加载
                        logger.info(f"Loading model from local path: {local_path}")
                        return SentenceTransformer(local_path)
            
            # 如果本地路径不存在
            if offline_mode:
                logger.info("Offline mode enabled, using fallback semantic analysis")
                return None
            else:
                # 尝试从 Hugging Face 下载
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
            # 首先进行字符集检测
            # 日语检测（平假名或片假名是日语的特征）
            has_hiragana = any(0x3040 <= ord(c) <= 0x309F for c in text)
            has_katakana = any(0x30A0 <= ord(c) <= 0x30FF for c in text)
            
            if has_hiragana or has_katakana:
                return 'ja'
            
            # 中文检测（只有汉字，没有平假名或片假名）
            has_kanji = any(0x4E00 <= ord(c) <= 0x9FFF for c in text)
            if has_kanji:
                return 'zh-cn'
            
            # 使用 langdetect 进行更详细的检测
            import langdetect
            lang = langdetect.detect(text)
            
            # 对于简短文本，提高英语检测的准确性
            if len(text) < 10:
                # 检查是否包含常见英语单词或字母
                english_chars = any(c.isalpha() and c.isascii() for c in text)
                if english_chars:
                    return 'en'
            
            return lang
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            # 回退到基于字符集的检测
            has_hiragana = any(0x3040 <= ord(c) <= 0x309F for c in text)
            has_katakana = any(0x30A0 <= ord(c) <= 0x30FF for c in text)
            has_kanji = any(0x4E00 <= ord(c) <= 0x9FFF for c in text)
            
            if has_hiragana or has_katakana:
                return 'ja'
            elif has_kanji:
                return 'zh-cn'
            else:
                # 默认为英语
                return 'en'
    
    def encode_text(self, text):
        """编码文本为向量"""
        if not self.embedding_model:
            # 回退到简单的字符串编码
            return [ord(c) for c in text[:100]]
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Text encoding failed: {e}")
            # 回退机制
            return [ord(c) for c in text[:100]]

# 创建全局实例
semantic_utility = SemanticUtility({})
