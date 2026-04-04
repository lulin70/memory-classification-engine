# SDK使用指南

## 1. 概述

Memory Classification Engine SDK 提供了一个简洁的接口，用于与记忆分类引擎进行交互。SDK支持所有核心功能，包括记忆处理、检索和管理。

## 2. 安装

### 2.1 从源码安装

```bash
pip install -e .
```

### 2.2 从PyPI安装

```bash
pip install memory-classification-engine
```

## 3. 快速开始

### 3.1 初始化SDK客户端

```python
from memory_classification_engine.sdk import MemoryClassificationClient

# 初始化客户端
client = MemoryClassificationClient(
    base_url='http://localhost:5000',  # 服务器地址
    timeout=30  # 超时时间（秒）
)
```

### 3.2 处理消息

```python
# 处理用户消息
result = client.process_message(
    message="我喜欢在代码中使用驼峰命名法",
    context={"conversation_id": "123"}
)
print(result)
```

### 3.3 检索记忆

```python
# 检索相关记忆
memories = client.retrieve_memories(
    query="命名规范",
    limit=10
)
print(memories)
```

### 3.4 管理记忆

```python
# 获取记忆详情
memory = client.get_memory(memory_id="mem_123456")
print(memory)

# 更新记忆
updated_memory = client.update_memory(
    memory_id="mem_123456",
    content="我喜欢在代码中使用驼峰命名法和空格缩进"
)
print(updated_memory)

# 删除记忆
deletion_result = client.delete_memory(memory_id="mem_123456")
print(deletion_result)
```

### 3.5 获取系统信息

```python
# 获取系统统计信息
stats = client.get_stats()
print(stats)

# 获取插件信息
plugins = client.get_plugins()
print(plugins)

# 健康检查
health = client.health_check()
print(health)

# 获取版本信息
version = client.get_version()
print(version)
```

## 4. API参考

### 4.1 MemoryClassificationClient 类

#### 4.1.1 初始化参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| base_url | str | 'http://localhost:5000' | 服务器基础URL |
| timeout | int | 30 | 请求超时时间（秒） |

#### 4.1.2 方法

##### process_message(message, context=None)

处理用户消息并返回分类结果。

**参数：**
- `message` (str): 用户消息内容
- `context` (dict, optional): 上下文信息

**返回：**
- dict: 处理结果，包含记忆分类信息

##### retrieve_memories(query, limit=20)

根据查询关键词检索相关记忆。

**参数：**
- `query` (str): 搜索关键词
- `limit` (int, optional): 返回结果数量限制

**返回：**
- list: 记忆列表

##### get_memory(memory_id)

获取指定记忆的详细信息。

**参数：**
- `memory_id` (str): 记忆ID

**返回：**
- dict: 记忆详情

##### update_memory(memory_id, content)

更新指定记忆的内容。

**参数：**
- `memory_id` (str): 记忆ID
- `content` (str): 新的记忆内容

**返回：**
- dict: 更新后的记忆详情

##### delete_memory(memory_id)

删除指定记忆。

**参数：**
- `memory_id` (str): 记忆ID

**返回：**
- dict: 删除结果

##### get_stats()

获取系统统计信息。

**返回：**
- dict: 系统统计数据

##### get_plugins()

获取插件信息。

**返回：**
- list: 插件列表

##### health_check()

健康检查。

**返回：**
- dict: 健康状态

##### get_version()

获取版本信息。

**返回：**
- dict: 版本信息

## 5. 异常处理

SDK定义了以下异常类：

### 5.1 MemoryClassificationError

基础异常类，所有SDK异常的父类。

### 5.2 APIError

API调用错误。

### 5.3 ConnectionError

连接错误。

### 5.4 TimeoutError

请求超时错误。

### 5.5 ValidationError

输入验证错误。

## 6. 示例

### 6.1 基本使用示例

```python
from memory_classification_engine.sdk import MemoryClassificationClient, MemoryClassificationError

try:
    # 初始化客户端
    client = MemoryClassificationClient()
    
    # 处理消息
    result = client.process_message("我的生日是1990年1月1日")
    print("处理结果:", result)
    
    # 检索记忆
    memories = client.retrieve_memories("生日")
    print("检索结果:", memories)
    
    # 获取系统统计
    stats = client.get_stats()
    print("系统统计:", stats)
    
except MemoryClassificationError as e:
    print(f"错误: {e}")
```

### 6.2 高级使用示例

```python
from memory_classification_engine.sdk import MemoryClassificationClient

# 初始化客户端
client = MemoryClassificationClient(base_url='http://localhost:5000')

# 处理多条消息
messages = [
    "我喜欢Python编程语言",
    "Java是一种面向对象的语言",
    "JavaScript用于前端开发"
]

for message in messages:
    result = client.process_message(message)
    print(f"消息: {message}")
    print(f"结果: {result}")
    print("---")

# 批量检索
search_terms = ["Python", "Java", "前端"]

for term in search_terms:
    memories = client.retrieve_memories(term)
    print(f"搜索 '{term}' 的结果: {len(memories)} 条")
    for memory in memories[:2]:  # 只显示前2条
        print(f"  - {memory.get('content', '')}")
    print("---")
```

## 7. 性能优化

### 7.1 批量操作

对于多条消息的处理，建议使用批量操作以提高性能：

```python
# 批量处理消息
def batch_process_messages(messages):
    results = []
    for message in messages:
        result = client.process_message(message)
        results.append(result)
    return results

# 使用
messages = ["消息1", "消息2", "消息3"]
results = batch_process_messages(messages)
```

### 7.2 缓存策略

对于频繁使用的查询，建议实现本地缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_retrieve(query, limit=20):
    return client.retrieve_memories(query, limit)

# 使用
results1 = cached_retrieve("Python")  # 第一次请求，会调用API
results2 = cached_retrieve("Python")  # 第二次请求，会使用缓存
```

## 8. 故障排除

### 8.1 常见错误

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|----------|
| 403 Forbidden | 认证失败 | 检查API密钥或JWT令牌 |
| 404 Not Found | 资源不存在 | 检查记忆ID是否正确 |
| 429 Too Many Requests | 速率限制 | 减少请求频率或增加速率限制 |
| 500 Internal Server Error | 服务器错误 | 检查服务器日志 |

### 8.2 调试技巧

1. **启用详细日志**：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **检查网络连接**：

```python
import requests
try:
    response = requests.get('http://localhost:5000/api/health')
    print(f"健康检查状态码: {response.status_code}")
except Exception as e:
    print(f"连接错误: {e}")
```

3. **验证服务器状态**：

```bash
curl http://localhost:5000/api/health
```

## 9. 版本兼容性

| SDK版本 | 引擎版本 | 兼容性 |
|---------|---------|--------|
| 1.0.0 | 1.0.0 | ✅ |
| 1.0.0 | 1.1.0 | ✅ |
| 1.1.0 | 1.0.0 | ⚠️ 部分功能可能不可用 |

## 10. 贡献

如果您发现SDK中的问题或有改进建议，请在GitHub上提交issue或pull request。

## 11. 许可证

SDK使用MIT许可证，与主项目一致。
