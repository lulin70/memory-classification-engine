# 记忆导入/导出格式标准

## 1. 概述

本文档定义了记忆分类引擎的记忆数据导入/导出格式标准，旨在提供一种标准化的方式来交换和备份记忆数据。该标准支持跨系统、跨平台的记忆数据迁移和共享。

## 2. 格式规范

### 2.1 核心格式

记忆数据采用 JSON 格式，支持以下结构：

```json
{
  "version": "1.0",
  "metadata": {
    "exported_at": "2026-04-08T12:00:00Z",
    "exported_by": "user_id",
    "engine_version": "0.1.0",
    "total_memories": 100
  },
  "memories": [
    {
      "id": "mem_123456",
      "type": "user_preference",
      "memory_type": "user_preference",
      "content": "我喜欢在早上喝咖啡",
      "confidence": 0.9,
      "source": "user",
      "tier": 2,
      "created_at": "2026-04-01T10:00:00Z",
      "updated_at": "2026-04-01T10:00:00Z",
      "last_accessed": "2026-04-01T10:00:00Z",
      "access_count": 1,
      "status": "active",
      "weight": 0.9,
      "tenant_id": "default",
      "language": "zh",
      "language_confidence": 0.99,
      "sensitivity_level": "low",
      "visibility": "private",
      "context": "conversation_123",
      "conversation_history": [
        {
          "id": "msg_1",
          "content": "你好",
          "timestamp": "2026-04-01T09:59:00Z"
        }
      ],
      "created_by": "user_id",
      "associations": [
        {
          "target_id": "mem_654321",
          "similarity": 0.8,
          "metadata": {
            "type": "semantic",
            "created_at": "2026-04-01T10:01:00Z"
          }
        }
      ],
      "metadata": {
        "tags": ["coffee", "morning"],
        "priority": "high",
        "expires_at": null
      }
    }
  ]
}
```

### 2.2 字段说明

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `version` | string | 是 | 格式版本号，当前为 "1.0" |
| `metadata` | object | 是 | 导出元数据 |
| `metadata.exported_at` | string | 是 | 导出时间，ISO 8601 格式 |
| `metadata.exported_by` | string | 否 | 导出用户 ID |
| `metadata.engine_version` | string | 是 | 引擎版本号 |
| `metadata.total_memories` | number | 是 | 导出的记忆总数 |
| `memories` | array | 是 | 记忆数据数组 |
| `memories[].id` | string | 是 | 记忆 ID |
| `memories[].type` | string | 是 | 记忆类型 |
| `memories[].memory_type` | string | 是 | 记忆类型（与 type 相同） |
| `memories[].content` | string | 是 | 记忆内容 |
| `memories[].confidence` | number | 是 | 置信度，范围 0-1 |
| `memories[].source` | string | 是 | 记忆来源 |
| `memories[].tier` | number | 是 | 记忆层级（2-4） |
| `memories[].created_at` | string | 是 | 创建时间，ISO 8601 格式 |
| `memories[].updated_at` | string | 是 | 更新时间，ISO 8601 格式 |
| `memories[].last_accessed` | string | 是 | 最后访问时间，ISO 8601 格式 |
| `memories[].access_count` | number | 是 | 访问次数 |
| `memories[].status` | string | 是 | 记忆状态（active, archived, forgotten） |
| `memories[].weight` | number | 是 | 记忆权重 |
| `memories[].tenant_id` | string | 是 | 租户 ID |
| `memories[].language` | string | 是 | 语言代码 |
| `memories[].language_confidence` | number | 是 | 语言检测置信度 |
| `memories[].sensitivity_level` | string | 是 | 敏感度级别（low, medium, high） |
| `memories[].visibility` | string | 是 | 可见性（private, team, org） |
| `memories[].context` | string | 否 | 上下文信息 |
| `memories[].conversation_history` | array | 否 | 对话历史 |
| `memories[].created_by` | string | 是 | 创建者 ID |
| `memories[].associations` | array | 否 | 记忆关联 |
| `memories[].metadata` | object | 否 | 额外元数据 |

### 2.3 记忆类型

| 类型 | 描述 |
|------|------|
| `user_preference` | 用户偏好 |
| `correction` | 纠正信号 |
| `fact_declaration` | 事实声明 |
| `decision` | 决策记录 |
| `relationship` | 关系信息 |
| `task_pattern` | 任务模式 |
| `sentiment_marker` | 情感标记 |
| `conversation_context` | 对话上下文 |

### 2.4 记忆层级

| 层级 | 描述 | 存储方式 |
|------|------|----------|
| 2 | 程序性记忆 | JSON 文件 |
| 3 | 情节记忆 | SQLite + FTS5 + 向量存储 |
| 4 | 语义记忆 | SQLite + 知识图谱 |

## 3. 导入/导出 API

### 3.1 导出 API

```python
# 导出所有记忆
export_result = engine.export_memories(format="json", user_id="user1")

# 导出指定租户的记忆
export_result = engine.export_memories(format="json", user_id="user1", tenant_id="company_tenant")

# 导出指定类型的记忆
export_result = engine.export_memories(
    format="json", 
    user_id="user1", 
    memory_types=["user_preference", "fact_declaration"]
)
```

### 3.2 导入 API

```python
# 导入记忆
import_data = {
    "version": "1.0",
    "metadata": {
        "exported_at": "2026-04-08T12:00:00Z",
        "exported_by": "user1",
        "engine_version": "0.1.0",
        "total_memories": 5
    },
    "memories": [
        # 记忆数据...
    ]
}

import_result = engine.import_memories(data=import_data, format="json", user_id="user1")
```

## 4. 实现细节

### 4.1 导出流程

1. **验证权限**：检查用户是否有导出权限
2. **收集记忆**：从各个存储层级收集记忆数据
3. **处理敏感数据**：解密敏感记忆
4. **构建导出结构**：按照标准格式构建导出数据
5. **生成元数据**：添加导出时间、版本等元数据
6. **返回结果**：返回导出的记忆数据

### 4.2 导入流程

1. **验证权限**：检查用户是否有导入权限
2. **验证格式**：验证导入数据格式是否符合标准
3. **处理敏感数据**：加密敏感记忆
4. **导入记忆**：将记忆写入相应的存储层级
5. **更新缓存**：清除缓存，确保数据一致性
6. **返回结果**：返回导入结果和统计信息

## 5. 兼容性

### 5.1 向后兼容

- 版本 1.0 支持与未来版本的向后兼容
- 导入时会自动处理旧版本格式
- 缺失字段会使用默认值

### 5.2 跨系统兼容

- 格式设计考虑了跨系统兼容性
- 支持与其他记忆管理系统的数据交换
- 提供转换工具用于不同格式之间的转换

## 6. 安全考虑

### 6.1 数据安全

- 导出时会自动解密敏感数据
- 导入时会自动加密敏感数据
- 建议在传输和存储导出数据时使用加密

### 6.2 访问控制

- 导出和导入操作需要相应的权限
- 导入时会检查记忆的可见性和权限
- 支持基于角色的访问控制

## 7. 示例

### 7.1 导出示例

```python
# 导出所有记忆
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()
export_result = engine.export_memories(format="json", user_id="user1")

# 保存到文件
import json
with open("memories_export.json", "w", encoding="utf-8") as f:
    json.dump(export_result, f, ensure_ascii=False, indent=2)

print(f"导出完成，共导出 {len(export_result.get('memories', []))} 条记忆")
```

### 7.2 导入示例

```python
# 导入记忆
from memory_classification_engine import MemoryClassificationEngine
import json

engine = MemoryClassificationEngine()

# 从文件读取
with open("memories_export.json", "r", encoding="utf-8") as f:
    import_data = json.load(f)

import_result = engine.import_memories(data=import_data, format="json", user_id="user1")
print(f"导入完成，共导入 {import_result.get('imported_count', 0)} 条记忆")
```

## 8. 最佳实践

1. **定期备份**：定期导出记忆数据作为备份
2. **版本控制**：对导出的记忆数据进行版本控制
3. **数据验证**：导入前验证数据格式和完整性
4. **增量导出**：支持增量导出，减少数据传输量
5. **数据清理**：导入前清理重复和无效数据

## 9. 未来扩展

- 支持更多导出格式（如 CSV、XML）
- 支持增量导出和导入
- 支持记忆数据的压缩
- 支持跨系统的记忆同步
- 支持记忆数据的验证和修复

## 10. 结论

本格式标准为记忆分类引擎提供了一种标准化的记忆数据交换方式，支持跨系统、跨平台的记忆数据迁移和共享。通过遵循此标准，可以确保记忆数据的一致性和完整性，同时提高系统的可扩展性和互操作性。