# API文档

## 1. 概述

Memory Classification Engine 提供了一套完整的API接口，用于管理和操作记忆数据。本文档详细描述了所有API接口的使用方法、参数说明和返回值格式。

## 2. 核心API

### 2.1 MemoryClassificationEngine

#### 2.1.1 初始化

```python
from memory_classification_engine import MemoryClassificationEngine

# 初始化引擎
engine = MemoryClassificationEngine(config_path="config.yaml")
```

**参数**：
- `config_path`：配置文件路径，默认为 `config.yaml`

**返回值**：
- `MemoryClassificationEngine` 实例

#### 2.1.2 process_message

处理用户消息并分类存储。

```python
result = engine.process_message(
    message="我喜欢使用Python编写Web应用",
    context={"conversation_id": "123"}
)
```

**参数**：
- `message`：用户消息内容
- `context`：可选的上下文信息

**返回值**：
```python
{
    "message": "我喜欢使用Python编写Web应用",
    "matches": [
        {
            "id": "mem_123456",
            "type": "user_preference",
            "memory_type": "user_preference",
            "content": "我喜欢使用Python编写Web应用",
            "confidence": 0.9,
            "source": "user",
            "tier": 2,
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00",
            "last_accessed": "2024-01-01T12:00:00",
            "access_count": 1,
            "status": "active"
        }
    ],
    "working_memory_size": 1
}
```

#### 2.1.3 retrieve_memories

检索记忆数据。

```python
memories = engine.retrieve_memories(
    query="Python Web",
    memory_type="user_preference",
    limit=10,
    use_vector_search=True
)
```

**参数**：
- `query`：搜索关键词
- `memory_type`：记忆类型，可选
- `limit`：返回结果数量限制，默认10
- `use_vector_search`：是否使用向量搜索，默认True

**返回值**：
- 记忆列表，格式与 `process_message` 返回的 `matches` 相同

#### 2.1.4 manage_memory

管理记忆（查看、编辑、删除）。

```python
result = engine.manage_memory(
    action="edit",
    memory_id="mem_123456",
    data={"content": "我喜欢使用Python和JavaScript编写Web应用"}
)
```

**参数**：
- `action`：操作类型，可选值：`view`、`edit`、`delete`
- `memory_id`：记忆ID
- `data`：编辑时的更新数据，仅 `edit` 操作需要

**返回值**：
```python
{
    "success": True,
    "memory": {...}  # 仅 view 和 edit 操作返回
}
```

#### 2.1.5 get_stats

获取系统统计信息。

```python
stats = engine.get_stats()
```

**返回值**：
```python
{
    "working_memory_size": 10,
    "tier2": {
        "total_memories": 50,
        "active_memories": 45
    },
    "tier3": {
        "total_memories": 200,
        "active_memories": 180
    },
    "tier4": {
        "total_memories": 100,
        "active_memories": 95
    },
    "total_memories": 350
}
```

## 3. 存储层API

### 3.1 BaseStorage

#### 3.1.1 store_memory

存储记忆。

```python
success = storage.store_memory(memory)
```

**参数**：
- `memory`：记忆数据字典

**返回值**：
- `True` 成功，`False` 失败

#### 3.1.2 retrieve_memories

检索记忆。

```python
memories = storage.retrieve_memories(query, limit)
```

**参数**：
- `query`：搜索关键词，可选
- `limit`：返回数量限制，默认10

**返回值**：
- 记忆列表

#### 3.1.3 update_memory

更新记忆。

```python
success = storage.update_memory(memory_id, updates)
```

**参数**：
- `memory_id`：记忆ID
- `updates`：更新数据字典

**返回值**：
- `True` 成功，`False` 失败

#### 3.1.4 delete_memory

删除记忆。

```python
success = storage.delete_memory(memory_id)
```

**参数**：
- `memory_id`：记忆ID

**返回值**：
- `True` 成功，`False` 失败

### 3.2 Tier3StorageFTS

#### 3.2.1 warmup_cache

预热缓存。

```python
count = storage.warmup_cache(limit=100)
```

**参数**：
- `limit`：预热记忆数量，默认100

**返回值**：
- 预热的记忆数量

#### 3.2.2 get_cache_stats

获取缓存统计信息。

```python
stats = storage.get_cache_stats()
```

**返回值**：
```python
{
    "enabled": True,
    "size": 50,
    "max_size": 1000,
    "expired_items": 0,
    "ttl": 3600,
    "warmup_completed": True
}
```

## 4. 插件系统API

### 4.1 PluginManager

#### 4.1.1 load_plugin

加载插件。

```python
success = plugin_manager.load_plugin("sentiment_analyzer")
```

**参数**：
- `plugin_name`：插件名称

**返回值**：
- `True` 成功，`False` 失败

#### 4.1.2 load_all_plugins

加载所有插件。

```python
loaded_plugins = plugin_manager.load_all_plugins()
```

**返回值**：
- 加载的插件名称列表

#### 4.1.3 process_message

通过插件处理消息。

```python
results = plugin_manager.process_message(message, context)
```

**参数**：
- `message`：消息内容
- `context`：上下文信息

**返回值**：
- 插件处理结果字典

#### 4.1.4 process_memory

通过插件处理记忆。

```python
processed_memory = plugin_manager.process_memory(memory)
```

**参数**：
- `memory`：记忆数据

**返回值**：
- 处理后的记忆数据

## 5. 配置API

### 5.1 ConfigManager

#### 5.1.1 load_config

加载配置。

```python
config = ConfigManager.load_config("config.yaml")
```

**参数**：
- `config_path`：配置文件路径

**返回值**：
- 配置字典

#### 5.1.2 get

获取配置值。

```python
value = config.get("storage.data_path", "./data")
```

**参数**：
- `key`：配置键
- `default`：默认值

**返回值**：
- 配置值

## 6. 工具API

### 6.1 Helpers

#### 6.1.1 generate_memory_id

生成记忆ID。

```python
memory_id = generate_memory_id()
```

**返回值**：
- 记忆ID字符串

#### 6.1.2 get_current_time

获取当前时间。

```python
current_time = get_current_time()
```

**返回值**：
- ISO格式的时间字符串

### 6.2 Logger

#### 6.2.1 get_logger

获取日志记录器。

```python
logger = get_logger("memory_engine")
logger.info("Memory stored successfully")
```

**参数**：
- `name`：日志名称

**返回值**：
- 日志记录器实例

## 7. 异常处理

### 7.1 异常类

| 异常类 | 描述 |
|---------|------|
| `MemoryEngineError` | 基础异常类 |
| `StorageError` | 存储相关异常 |
| `MemoryNotFoundError` | 记忆未找到 |
| `MemoryAlreadyExistsError` | 记忆已存在 |
| `DatabaseError` | 数据库错误 |
| `FTS5Error` | FTS5相关错误 |
| `CacheError` | 缓存相关错误 |
| `ConfigurationError` | 配置错误 |

### 7.2 异常处理示例

```python
try:
    engine.process_message("测试消息")
except MemoryNotFoundError as e:
    print(f"记忆未找到: {e}")
except StorageError as e:
    print(f"存储错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 8. 最佳实践

### 8.1 API使用建议

1. **初始化**：在应用启动时初始化引擎实例
2. **错误处理**：始终捕获和处理异常
3. **参数验证**：在调用API前验证参数
4. **性能优化**：
   - 批量操作优于单个操作
   - 使用缓存减少重复查询
   - 合理设置查询限制

### 8.2 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 记忆存储失败 | 数据库连接问题 | 检查数据库权限和路径 |
| 搜索结果为空 | 索引未建立 | 重建FTS5索引 |
| 性能下降 | 缓存未预热 | 调用warmup_cache方法 |
| 插件加载失败 | 插件依赖缺失 | 安装插件依赖 |

## 9. 示例代码

### 9.1 基本使用

```python
from memory_classification_engine import MemoryClassificationEngine

# 初始化引擎
engine = MemoryClassificationEngine()

# 处理消息
result = engine.process_message("我喜欢使用Python")
print(f"处理结果: {result}")

# 搜索记忆
memories = engine.retrieve_memories("Python")
print(f"搜索结果: {len(memories)} 条")

# 获取统计信息
stats = engine.get_stats()
print(f"系统统计: {stats}")
```

### 9.2 高级使用

```python
from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.storage.tier3_fts import Tier3StorageFTS

# 初始化引擎
engine = MemoryClassificationEngine()

# 直接使用存储层
storage = Tier3StorageFTS("./data/tier3")

# 预热缓存
storage.warmup_cache(limit=200)

# 存储记忆
memory = {
    "id": "mem_123",
    "type": "user_preference",
    "content": "我喜欢使用JavaScript",
    "confidence": 0.9,
    "source": "user"
}
storage.store_memory(memory)

# 搜索记忆
results = storage.retrieve_memories("JavaScript")
print(f"搜索结果: {len(results)} 条")
```

## 10. 版本兼容性

### 10.1 API变更

| 版本 | 变更 |
|------|------|
| 1.0.0 | 初始版本 |
| 1.1.0 | 添加插件系统 |
| 1.2.0 | 添加FTS5搜索 |
| 1.3.0 | 添加缓存系统 |
| 1.4.0 | 添加向量存储和检索功能 |

### 10.2 向后兼容

- 1.x 版本保持API向后兼容
- 2.0 版本可能会有破坏性变更

## 11. 故障排除

### 11.1 常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| `DatabaseError: unable to open database file` | 数据库文件权限问题 | 检查文件权限 |
| `FTS5Error: FTS5 extension not available` | SQLite FTS5未启用 | 使用支持FTS5的SQLite版本 |
| `MemoryNotFoundError: Memory not found` | 记忆ID不存在 | 检查记忆ID是否正确 |

### 11.2 日志级别

- `DEBUG`：详细调试信息
- `INFO`：一般信息
- `WARNING`：警告信息
- `ERROR`：错误信息
- `CRITICAL`：严重错误

## 12. 贡献指南

### 12.1 API扩展

如果您需要扩展API，请遵循以下步骤：

1. 在对应模块中添加新方法
2. 更新API文档
3. 添加相应的测试用例
4. 提交Pull Request

### 12.2 反馈

如有API相关问题或建议，请通过以下方式反馈：

- GitHub Issues
- 邮件：support@memory-engine.com
- 论坛：forum.memory-engine.com
