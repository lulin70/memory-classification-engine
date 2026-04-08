from typing import Dict, Any, List, Optional
from memory_classification_engine.utils.logger import logger
import os
import json

class KnowledgeManager:
    def __init__(self, config):
        self.config = config
        self.obsidian_vault_path = self.config.get('knowledge.obsidian_vault_path', '')
        self.knowledge_base = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """加载知识库"""
        if self.obsidian_vault_path and os.path.exists(self.obsidian_vault_path):
            self._load_obsidian_vault()
        else:
            logger.warning('Obsidian vault path not set or does not exist')
    
    def _load_obsidian_vault(self):
        """加载Obsidian vault"""
        try:
            # 遍历Obsidian vault目录
            for root, dirs, files in os.walk(self.obsidian_vault_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, self.obsidian_vault_path)
                        
                        # 读取文件内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 存储到知识库
                        self.knowledge_base[relative_path] = {
                            'content': content,
                            'path': file_path,
                            'last_modified': os.path.getmtime(file_path)
                        }
            
            logger.info(f'Loaded {len(self.knowledge_base)} files from Obsidian vault')
        except Exception as e:
            logger.error(f'Failed to load Obsidian vault: {e}')
    
    def get_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """获取知识库中的相关知识"""
        results = []
        
        # 简单的字符串匹配
        for path, knowledge in self.knowledge_base.items():
            if query in knowledge['content']:
                results.append({
                    'path': path,
                    'content': knowledge['content'],
                    'score': 1.0  # 简单的匹配得分
                })
        
        # 按得分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def write_memory_to_knowledge(self, memory: Dict[str, Any]) -> bool:
        """将记忆写回知识库"""
        if not self.obsidian_vault_path or not os.path.exists(self.obsidian_vault_path):
            logger.error('Obsidian vault path not set or does not exist')
            return False
        
        try:
            # 生成文件名
            memory_id = memory.get('id', '')
            memory_type = memory.get('memory_type', 'unknown')
            filename = f'{memory_id}_{memory_type}.md'
            file_path = os.path.join(self.obsidian_vault_path, filename)
            
            # 生成文件内容
            content = f"# {memory_type}\n\n"
            content += f"**ID**: {memory_id}\n"
            content += f"**Created At**: {memory.get('created_at', '')}\n"
            content += f"**Last Accessed**: {memory.get('last_accessed', '')}\n"
            content += f"**Weight**: {memory.get('weight', 1.0)}\n"
            content += f"**Importance**: {memory.get('importance', 'medium')}\n"
            content += f"**Sensitivity Level**: {memory.get('sensitivity_level', 'low')}\n"
            content += f"**Visibility**: {memory.get('visibility', 'private')}\n\n"
            content += f"## Content\n\n{memory.get('content', '')}\n"
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新知识库
            self.knowledge_base[filename] = {
                'content': content,
                'path': file_path,
                'last_modified': os.path.getmtime(file_path)
            }
            
            logger.info(f'Wrote memory {memory_id} to knowledge base')
            return True
        except Exception as e:
            logger.error(f'Failed to write memory to knowledge base: {e}')
            return False
    
    def sync_knowledge_base(self):
        """同步知识库"""
        self._load_knowledge_base()
        logger.info('Synced knowledge base')
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return {
            'total_files': len(self.knowledge_base),
            'vault_path': self.obsidian_vault_path
        }
