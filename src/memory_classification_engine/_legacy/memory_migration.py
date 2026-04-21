# Comment in Chinese removed
"""
Memory Migration System

Enables memory export/import between different Agent instances
"""

import json
import logging
import time
import hashlib
from typing import List, Dict, Any, Optional

logger = logging.getLogger('memory-migration')

class MemoryMigrationManager:
    """记忆迁移管理器
    
    实现记忆的导出和导入功能，支持跨会话、跨 Agent 的记忆迁移
    """
    
    def __init__(self):
        """初始化记忆迁移管理器"""
        self.export_version = "1.0"
        logger.info("MemoryMigrationManager initialized")
    
    def export_memories(self, memories: List[Dict[str, Any]], include_metadata: bool = True) -> str:
        """导出记忆为标准格式
        
        Args:
            memories: 记忆列表
            include_metadata: 是否包含元数据
            
        Returns:
            导出的 JSON 字符串
        """
        try:
            # 准备导出数据
            export_data = {
                "version": self.export_version,
                "exported_at": time.time(),
                "memory_count": len(memories),
                "memories": []
            }
            
            # 处理每个记忆
            for memory in memories:
                # 标准化记忆格式
                standardized_memory = self._standardize_memory(memory)
                
                # 添加到导出数据
                export_data["memories"].append(standardized_memory)
            
            # 生成校验和
            if include_metadata:
                export_data["checksum"] = self._generate_checksum(export_data["memories"])
            
            # Comment in Chinese removed 字符串
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported {len(memories)} memories")
            return json_str
            
        except Exception as e:
            logger.error(f"Error exporting memories: {e}")
            raise
    
    def import_memories(self, json_str: str, validate_checksum: bool = True) -> List[Dict[str, Any]]:
        """从标准格式导入记忆
        
        Args:
            json_str: 导出的 JSON 字符串
            validate_checksum: 是否验证校验和
            
        Returns:
            导入的记忆列表
        """
        try:
            # Comment in Chinese removed
            import_data = json.loads(json_str)
            
            # 验证版本
            if "version" not in import_data:
                raise ValueError("Missing version in import data")
            
            # 验证校验和
            if validate_checksum and "checksum" in import_data:
                calculated_checksum = self._generate_checksum(import_data.get("memories", []))
                if import_data["checksum"] != calculated_checksum:
                    raise ValueError("Checksum validation failed")
            
            # 处理记忆
            imported_memories = []
            for memory in import_data.get("memories", []):
                # 转换为内部格式
                internal_memory = self._convert_to_internal(memory)
                imported_memories.append(internal_memory)
            
            logger.info(f"Imported {len(imported_memories)} memories")
            return imported_memories
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            raise
        except Exception as e:
            logger.error(f"Error importing memories: {e}")
            raise
    
    def _standardize_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """标准化记忆格式
        
        Args:
            memory: 原始记忆对象
            
        Returns:
            标准化的记忆对象
        """
        # 标准字段映射
        standard_memory = {
            "id": memory.get("id", self._generate_memory_id()),
            "content": memory.get("content", ""),
            "memory_type": memory.get("memory_type", "unknown"),
            "tier": memory.get("tier", 3),
            "confidence": memory.get("confidence", 0.0),
            "created_at": memory.get("created_at", time.time()),
            "last_accessed": memory.get("last_accessed", time.time()),
            "weight": memory.get("weight", 0.5),
            "metadata": memory.get("metadata", {})
        }
        
        # 添加可选字段
        if "source" in memory:
            standard_memory["source"] = memory["source"]
        if "context" in memory:
            standard_memory["context"] = memory["context"]
        if "associations" in memory:
            standard_memory["associations"] = memory["associations"]
        if "tenant_id" in memory:
            standard_memory["tenant_id"] = memory["tenant_id"]
        if "user_id" in memory:
            standard_memory["user_id"] = memory["user_id"]
        
        return standard_memory
    
    def _convert_to_internal(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """将标准格式转换为内部格式
        
        Args:
            memory: 标准化的记忆对象
            
        Returns:
            内部格式的记忆对象
        """
        # 直接返回标准化格式，因为内部格式与标准格式兼容
        return memory
    
    def _generate_checksum(self, memories: List[Dict[str, Any]]) -> str:
        """生成校验和
        
        Args:
            memories: 记忆列表
            
        Returns:
            校验和字符串
        """
        try:
            # 将记忆列表转换为字符串
            memory_str = json.dumps(memories, sort_keys=True, ensure_ascii=False)
            # Comment in Chinese removed 校验和
            checksum = hashlib.md5(memory_str.encode('utf-8')).hexdigest()
            return checksum
        except Exception as e:
            logger.error(f"Error generating checksum: {e}")
            return ""
    
    def _generate_memory_id(self) -> str:
        """生成记忆 ID
        
        Returns:
            记忆 ID
        """
        timestamp = int(time.time() * 1000)
        random_suffix = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()[:6]
        return f"mem_{timestamp}_{random_suffix}"
    
    def export_to_file(self, memories: List[Dict[str, Any]], file_path: str, include_metadata: bool = True):
        """导出记忆到文件
        
        Args:
            memories: 记忆列表
            file_path: 文件路径
            include_metadata: 是否包含元数据
        """
        try:
            json_str = self.export_memories(memories, include_metadata)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"Exported {len(memories)} memories to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting to file: {e}")
            raise
    
    def import_from_file(self, file_path: str, validate_checksum: bool = True) -> List[Dict[str, Any]]:
        """从文件导入记忆
        
        Args:
            file_path: 文件路径
            validate_checksum: 是否验证校验和
            
        Returns:
            导入的记忆列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
            return self.import_memories(json_str, validate_checksum)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error importing from file: {e}")
            raise
    
    def validate_export_data(self, json_str: str) -> Dict[str, Any]:
        """验证导出数据的有效性
        
        Args:
            json_str: 导出的 JSON 字符串
            
        Returns:
            验证结果
        """
        try:
            import_data = json.loads(json_str)
            
            validation_result = {
                "valid": True,
                "version": import_data.get("version"),
                "memory_count": len(import_data.get("memories", [])),
                "exported_at": import_data.get("exported_at"),
                "errors": []
            }
            
            # 检查必要字段
            if "version" not in import_data:
                validation_result["valid"] = False
                validation_result["errors"].append("Missing version")
            
            if "memories" not in import_data:
                validation_result["valid"] = False
                validation_result["errors"].append("Missing memories")
            
            # 检查记忆格式
            for i, memory in enumerate(import_data.get("memories", [])):
                if "id" not in memory:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Memory {i} missing id")
                if "content" not in memory:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Memory {i} missing content")
                if "memory_type" not in memory:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Memory {i} missing memory_type")
            
            return validation_result
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [f"Invalid JSON: {str(e)}"]
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }

# 全局记忆迁移管理器实例
memory_migration_manager = MemoryMigrationManager()

def get_memory_migration_manager() -> MemoryMigrationManager:
    """获取记忆迁移管理器实例
    
    Returns:
        MemoryMigrationManager 实例
    """
    return memory_migration_manager

if __name__ == "__main__":
    # 测试记忆迁移功能
    manager = MemoryMigrationManager()
    
    # 示例记忆数据
    sample_memories = [
        {
            "id": "mem_1",
            "content": "我更喜欢使用双引号",
            "memory_type": "user_preference",
            "tier": 2,
            "confidence": 0.9,
            "created_at": time.time() - 3600,
            "last_accessed": time.time() - 1800,
            "weight": 0.8
        },
        {
            "id": "mem_2",
            "content": "张三是后端开发工程师",
            "memory_type": "relationship",
            "tier": 4,
            "confidence": 0.85,
            "created_at": time.time() - 7200,
            "last_accessed": time.time() - 3600,
            "weight": 0.7
        }
    ]
    
    # 测试导出
    print("Testing export...")
    json_str = manager.export_memories(sample_memories)
    print(f"Exported JSON: {json_str[:200]}...")
    
    # 测试导入
    print("\nTesting import...")
    imported_memories = manager.import_memories(json_str)
    print(f"Imported {len(imported_memories)} memories")
    for memory in imported_memories:
        print(f"  - {memory['memory_type']}: {memory['content']}")
    
    # 测试文件导出导入
    print("\nTesting file export/import...")
    test_file = "test_memories.json"
    manager.export_to_file(sample_memories, test_file)
    file_imported = manager.import_from_file(test_file)
    print(f"Imported from file: {len(file_imported)} memories")
    
    # 测试验证
    print("\nTesting validation...")
    validation = manager.validate_export_data(json_str)
    print(f"Validation result: {validation}")
    
    print("\nMemory migration tests completed!")
