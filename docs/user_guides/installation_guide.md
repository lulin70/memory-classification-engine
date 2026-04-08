# 记忆分类引擎安装指南

## 系统要求

- Python 3.8 或更高版本
- pip 包管理器
- 可选：Neo4j 数据库（用于知识图谱存储）
- 可选：Obsidian（用于知识库集成）

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd memory-classification-engine
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

为了安全管理API Key，建议使用环境变量来配置：

```bash
# 设置GLM API Key（如果需要使用LLM功能）
export MCE_LLM_API_KEY="your_glm_api_key"

# 启用LLM功能（可选）
export MCE_LLM_ENABLED=true

# 可选：设置配置文件路径
export MCE_CONFIG_PATH="./config/config.yaml"
```

### 4. 配置文件

编辑 `config/config.yaml` 文件，根据需要调整配置：

```yaml
# LLM settings (optional)
llm:
  enabled: false  # 默认为false，设置为true启用
  api_key: ""  # 建议通过环境变量设置，不要直接在此文件中填写
  model: "glm-4-plus"
  temperature: 0.3
  max_tokens: 500
  timeout: 30  # In seconds

# Neo4j settings (optional)
neo4j:
  enabled: true
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "password"
  database: "neo4j"
  connection_pool_size: 10
  max_transaction_retry_time: 30

# Knowledge base settings (optional)
knowledge:
  obsidian_vault_path: ""  # 设置Obsidian vault路径
```

### 5. 安装Neo4j（可选）

如果你想使用Neo4j作为知识图谱存储后端，需要：

#### 方法1：下载安装Neo4j Desktop

1. 从 [Neo4j官网](https://neo4j.com/download/) 下载并安装Neo4j Desktop
2. 启动Neo4j Desktop，创建一个新的数据库
3. 启动数据库，默认用户名是 `neo4j`，密码需要设置

#### 方法2：使用Docker运行Neo4j

```bash
docker run --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

#### 验证Neo4j连接

1. 在浏览器中访问 `http://localhost:7474`
2. 使用用户名 `neo4j` 和密码 `password` 登录（如果使用Docker）
3. 首次登录时需要修改密码，确保与 `config/config.yaml` 中的配置一致

### 6. 安装Obsidian（可选）

如果你想使用Obsidian作为知识库集成，需要：

1. 从 [Obsidian官网](https://obsidian.md/download) 下载并安装Obsidian
2. 创建一个新的Obsidian vault
3. 在 `config/config.yaml` 文件中设置 `obsidian_vault_path` 为你的Obsidian vault路径

## 基本使用

### 1. 初始化引擎

```python
from memory_classification_engine import MemoryClassificationEngine

# 初始化引擎
engine = MemoryClassificationEngine()
```

### 2. 处理消息

```python
# 处理用户消息
user_message = "记住，我不喜欢在代码中使用破折号"
result = engine.process_message(user_message)
print(result)
# 输出: {"matched": true, "memory_type": "user_preference", "tier": 2, "content": "不喜欢在代码中使用破折号", "confidence": 1.0, "source": "rule:0"}
```

### 3. 检索记忆

```python
# 检索记忆
memories = engine.retrieve_memories("代码风格")
print(memories)
```

### 4. 使用Agent框架

```python
# 注册Agent
agent_config = {
    'adapter': 'claude_code',  # 支持的适配器：claude_code, work_buddy, trae, openclaw
    'api_key': 'your_api_key'  # 如果需要API密钥
}
engine.register_agent('my_agent', agent_config)

# 列出所有注册的Agent
agents = engine.list_agents()
print("注册的Agent:", agents)

# 使用Agent处理消息
result = engine.process_message_with_agent('my_agent', "Hello, world!")
print("Agent处理结果:", result)

# 注销Agent
engine.unregister_agent('my_agent')
```

### 5. 知识库集成

```python
# 将记忆写回知识库
memory_id = "your_memory_id"
write_result = engine.write_memory_to_knowledge(memory_id)
print("写回知识库结果:", write_result)

# 从知识库获取相关知识
knowledge = engine.get_knowledge("科幻小说")
print("知识库检索结果:", knowledge)

# 同步知识库
engine.sync_knowledge_base()
print("知识库同步完成")

# 获取知识库统计信息
stats = engine.get_knowledge_statistics()
print("知识库统计信息:", stats)
```

## 常见问题和解决方案

### 1. 安装依赖失败

**问题**：执行 `pip install -r requirements.txt` 时失败。

**解决方案**：
- 确保你使用的是Python 3.8或更高版本
- 尝试使用 `pip install --upgrade pip` 升级pip
- 如果特定包安装失败，尝试单独安装该包

### 2. Neo4j连接失败

**问题**：启动引擎时出现Neo4j连接错误。

**解决方案**：
- 确保Neo4j服务正在运行
- 检查 `config/config.yaml` 中的Neo4j配置是否正确
- 验证Neo4j的用户名和密码是否正确
- 如果不需要Neo4j，可以在配置文件中将 `neo4j.enabled` 设置为 `false`

### 3. Obsidian集成失败

**问题**：无法将记忆写回Obsidian。

**解决方案**：
- 确保Obsidian已安装
- 检查 `config/config.yaml` 中的 `obsidian_vault_path` 是否正确设置
- 确保你有足够的权限访问Obsidian vault目录

### 4. LLM功能不可用

**问题**：启用LLM功能后，处理消息时出现错误。

**解决方案**：
- 确保已设置 `MCE_LLM_API_KEY` 环境变量
- 检查 `config/config.yaml` 中的LLM配置是否正确
- 确保你的API密钥有效且有足够的配额

### 5. 性能问题

**问题**：引擎运行缓慢或内存使用过高。

**解决方案**：
- 确保你的系统满足最低要求
- 调整 `config/config.yaml` 中的内存相关配置
- 考虑禁用不需要的功能（如LLM或Neo4j）

## 故障排除

如果遇到其他问题，请检查以下内容：

1. **日志文件**：查看系统生成的日志文件，了解具体错误信息
2. **配置文件**：确保配置文件中的设置正确
3. **依赖版本**：确保所有依赖包的版本兼容
4. **系统资源**：确保系统有足够的内存和CPU资源

## 联系支持

如果问题仍然存在，请在GitHub仓库中创建一个issue，提供详细的错误信息和复现步骤，我们将尽快帮助你解决问题。
