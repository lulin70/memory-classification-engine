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
from memory_classification_engine.sdk import MemoryClassificationSDK

# 初始化SDK
sdk = MemoryClassificationSDK(
    api_key="YOUR_API_KEY",
    base_url="http://localhost:8000/api/v1"
)
```

### 3.2 处理消息

```python
# 处理用户消息
result = sdk.process_message(
    message="我喜欢在代码中使用驼峰命名法",
    context={"user_id": "user123", "tenant_id": "default"}
)
print(result)
```

### 3.3 检索记忆

```python
# 检索相关记忆
memories = sdk.retrieve_memories(
    query="命名规范",
    limit=5,
    tenant_id="default"
)
print(memories)
```

### 3.4 管理记忆

```python
# 获取记忆详情
memory = sdk.get_memory(memory_id="mem_123456")
print(memory)

# 更新记忆
updated_memory = sdk.update_memory(
    memory_id="mem_123456",
    data={"content": "我喜欢在代码中使用驼峰命名法和空格缩进"}
)
print(updated_memory)

# 删除记忆
deletion_result = sdk.delete_memory(memory_id="mem_123456")
print(deletion_result)
```

### 3.5 导出记忆

```python
# 导出记忆
export_data = sdk.export_memories(
    format="json",
    tenant_id="default",
    memory_types=["user_preference", "fact_declaration"]
)
with open("exported_memories.json", "wb") as f:
    f.write(export_data)
print("记忆导出完成")
```

### 3.6 使用Agent处理

```python
# 使用Agent处理消息
agent_result = sdk.process_with_agent(
    agent_name="claude_code",
    message="Write a Python function to calculate factorial",
    context={"user_id": "user123", "tenant_id": "default"}
)
print("Agent处理结果:", agent_result)
```

### 3.7 租户管理

```python
# 创建租户
create_result = sdk.create_tenant(
    tenant_id="company_a",
    name="Company A",
    tenant_type="enterprise",
    user_id="admin123"
)
print("创建租户结果:", create_result)

# 列出所有租户
tenants = sdk.list_tenants()
print("租户列表:", tenants)
```

## 4. API参考

### 4.1 MemoryClassificationSDK 类

#### 4.1.1 初始化参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| api_key | str | 必填 | API密钥，用于认证 |
| base_url | str | 'http://localhost:8000/api/v1' | API基础URL |

#### 4.1.2 方法

##### process_message(message, context=None)

处理用户消息并返回分类结果。

**参数：**
- `message` (str): 用户消息内容
- `context` (dict, optional): 上下文信息，包含user_id、tenant_id等

**返回：**
- dict: 处理结果，包含记忆分类信息

##### retrieve_memories(query=None, limit=5, tenant_id=None, memory_type=None, tier=None)

根据查询参数检索记忆。

**参数：**
- `query` (str, optional): 搜索查询字符串
- `limit` (int, optional): 最大结果数，默认5
- `tenant_id` (str, optional): 按租户ID过滤
- `memory_type` (str, optional): 按记忆类型过滤
- `tier` (int, optional): 按存储层级过滤

**返回：**
- dict: 包含记忆列表和总数的字典

##### get_memory(memory_id)

获取指定记忆的详细信息。

**参数：**
- `memory_id` (str): 记忆ID

**返回：**
- dict: 记忆详情

##### update_memory(memory_id, data)

更新指定记忆。

**参数：**
- `memory_id` (str): 记忆ID
- `data` (dict): 更新数据

**返回：**
- dict: 更新后的记忆详情

##### delete_memory(memory_id)

删除指定记忆。

**参数：**
- `memory_id` (str): 记忆ID

**返回：**
- dict: 删除结果

##### export_memories(format="json", tenant_id=None, memory_types=None)

导出记忆。

**参数：**
- `format` (str, optional): 导出格式 (json, csv, jsonl)
- `tenant_id` (str, optional): 按租户ID过滤
- `memory_types` (list, optional): 要导出的记忆类型列表

**返回：**
- bytes: 导出的数据

##### get_stats()

获取系统统计信息。

**返回：**
- dict: 系统统计数据

##### manage_memory(action, memory_id, data=None, user_id=None)

管理记忆操作（查看、编辑、删除）。

**参数：**
- `action` (str): 操作类型 (view, edit, delete)
- `memory_id` (str): 记忆ID
- `data` (dict, optional): 编辑操作的数据
- `user_id` (str, optional): 用户ID

**返回：**
- dict: 操作结果

##### process_with_agent(agent_name, message, context=None)

使用指定Agent处理消息。

**参数：**
- `agent_name` (str): Agent名称
- `message` (str): 消息内容
- `context` (dict, optional): 上下文信息

**返回：**
- dict: Agent处理结果

##### create_tenant(tenant_id, name, tenant_type, user_id=None, **kwargs)

创建新租户。

**参数：**
- `tenant_id` (str): 租户ID
- `name` (str): 租户名称
- `tenant_type` (str): 租户类型
- `user_id` (str, optional): 用户ID
- `**kwargs`: 其他租户属性

**返回：**
- dict: 创建结果

##### get_tenant(tenant_id)

获取租户信息。

**参数：**
- `tenant_id` (str): 租户ID

**返回：**
- dict: 租户详情

##### update_tenant(tenant_id, data)

更新租户信息。

**参数：**
- `tenant_id` (str): 租户ID
- `data` (dict): 更新数据

**返回：**
- dict: 更新结果

##### delete_tenant(tenant_id)

删除租户。

**参数：**
- `tenant_id` (str): 租户ID

**返回：**
- dict: 删除结果

##### list_tenants()

列出所有租户。

**返回：**
- dict: 租户列表

## 5. 异常处理

SDK会抛出以下异常：

### 5.1 通用异常

- `Exception`: 通用API错误
- `requests.exceptions.RequestException`: 网络请求错误

## 6. 示例

### 6.1 基本使用示例

```python
from memory_classification_engine.sdk import MemoryClassificationSDK

try:
    # 初始化SDK
    sdk = MemoryClassificationSDK(api_key="YOUR_API_KEY")
    
    # 处理消息
    result = sdk.process_message("我的生日是1990年1月1日")
    print("处理结果:", result)
    
    # 检索记忆
    memories = sdk.retrieve_memories(query="生日")
    print("检索结果:", memories)
    
    # 获取系统统计
    stats = sdk.get_stats()
    print("系统统计:", stats)
    
    # 导出记忆
    export_data = sdk.export_memories(format="json")
    with open("memories.json", "wb") as f:
        f.write(export_data)
    print("记忆导出完成")
    
 except Exception as e:
    print(f"错误: {e}")
```

### 6.2 高级使用示例

```python
from memory_classification_engine.sdk import MemoryClassificationSDK

# 初始化SDK
sdk = MemoryClassificationSDK(api_key="YOUR_API_KEY")

# 处理多条消息
messages = [
    "我喜欢Python编程语言",
    "Java是一种面向对象的语言",
    "JavaScript用于前端开发"
]

for message in messages:
    result = sdk.process_message(message)
    print(f"消息: {message}")
    print(f"结果: {result}")
    print("---")

# 批量检索
search_terms = ["Python", "Java", "前端"]

for term in search_terms:
    result = sdk.retrieve_memories(query=term, limit=3)
    print(f"搜索 '{term}' 的结果: {result.get('total', 0)} 条")
    for memory in result.get('memories', []):
        print(f"  - {memory.get('content', '')}")
    print("---")

# 使用Agent处理
agent_result = sdk.process_with_agent(
    agent_name="claude_code",
    message="Write a Python function to calculate factorial"
)
print("Agent处理结果:", agent_result)
```

## 7. 性能优化

### 7.1 批量操作

对于多条消息的处理，建议使用批量操作以提高性能：

```python
# 批量处理消息
def batch_process_messages(messages):
    results = []
    for message in messages:
        result = sdk.process_message(message)
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
def cached_retrieve(query, limit=5):
    result = sdk.retrieve_memories(query=query, limit=limit)
    return result

# 使用
results1 = cached_retrieve("Python")  # 第一次请求，会调用API
results2 = cached_retrieve("Python")  # 第二次请求，会使用缓存
```

## 8. 故障排除

### 8.1 常见错误

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|----------|
| 401 Unauthorized | API密钥无效 | 检查API密钥是否正确 |
| 403 Forbidden | 权限不足 | 检查用户权限 |
| 404 Not Found | 资源不存在 | 检查记忆ID或租户ID是否正确 |
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
    response = requests.get('http://localhost:8000/api/v1/stats')
    print(f"健康检查状态码: {response.status_code}")
except Exception as e:
    print(f"连接错误: {e}")
```

3. **验证服务器状态**：

```bash
curl http://localhost:8000/api/v1/stats
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
