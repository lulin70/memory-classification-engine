# 记忆分类引擎用户指南

## 1. 简介

记忆分类引擎（Memory Classification Engine）是一个智能记忆管理系统，能够自动分类、存储和检索用户的记忆。本指南将帮助你了解如何使用记忆分类引擎的各项功能，充分发挥其能力。

## 2. 基本使用

### 2.1 初始化引擎

```python
from memory_classification_engine import MemoryClassificationEngine

# 初始化引擎
engine = MemoryClassificationEngine()
```

### 2.2 处理消息

```python
# 处理用户消息
user_message = "记住，我不喜欢在代码中使用破折号"
result = engine.process_message(user_message)
print(result)
# 输出: {"matched": true, "memory_type": "user_preference", "tier": 2, "content": "不喜欢在代码中使用破折号", "confidence": 1.0, "source": "rule:0"}
```

### 2.3 检索记忆

```python
# 检索记忆
memories = engine.retrieve_memories("代码风格")
print(memories)
```

### 2.4 处理反馈

```python
# 处理用户反馈
memory_id = "your_memory_id"
feedback = {"type": "positive", "comment": "This memory is accurate"}
result = engine.process_feedback(memory_id, feedback)
print(result)
```

### 2.5 优化系统

```python
# 优化系统
result = engine.optimize_system()
print(result)
```

### 2.6 压缩记忆

```python
# 压缩记忆
tenant_id = "your_tenant_id"
result = engine.compress_memories(tenant_id)
print(result)
```

## 3. Agent框架使用

### 3.1 注册Agent

```python
# 注册Agent
agent_config = {
    'adapter': 'claude_code',  # 支持的适配器：claude_code, work_buddy, trae, openclaw
    'api_key': 'your_api_key'  # 如果需要API密钥
}
result = engine.register_agent('my_agent', agent_config)
print(result)
```

### 3.2 列出Agent

```python
# 列出所有注册的Agent
result = engine.list_agents()
print("注册的Agent:", result)
```

### 3.3 使用Agent处理消息

```python
# 使用Agent处理消息
result = engine.process_message_with_agent('my_agent', "Hello, world!")
print("Agent处理结果:", result)
```

### 3.4 注销Agent

```python
# 注销Agent
result = engine.unregister_agent('my_agent')
print(result)
```

## 4. 知识库集成

### 4.1 将记忆写回知识库

```python
# 将记忆写回知识库
memory_id = "your_memory_id"
result = engine.write_memory_to_knowledge(memory_id)
print("写回知识库结果:", result)
```

### 4.2 从知识库获取知识

```python
# 从知识库获取相关知识
result = engine.get_knowledge("科幻小说")
print("知识库检索结果:", result)
```

### 4.3 同步知识库

```python
# 同步知识库
result = engine.sync_knowledge_base()
print("知识库同步结果:", result)
```

### 4.4 获取知识库统计信息

```python
# 获取知识库统计信息
result = engine.get_knowledge_statistics()
print("知识库统计信息:", result)
```

## 5. 高级功能

### 5.1 VS Code 扩展

#### 5.1.1 安装和配置

1. **安装扩展**：
   - 打开 VS Code 或 Cursor
   - 点击扩展图标（左侧边栏）
   - 搜索 "Memory Classification Engine"
   - 点击 "安装"

2. **配置扩展**：
   - 打开 VS Code 设置（File → Preferences → Settings）
   - 搜索 "Memory Classification Engine"
   - 配置 MCP 服务器地址（默认为 http://localhost:8000）

#### 5.1.2 使用扩展

1. **查看记忆**：
   - 点击左侧边栏的 "Memory Classification Engine" 图标
   - 展开不同的记忆类型查看记忆

2. **操作记忆**：
   - 右键点击记忆，选择 "Recall" 查看详情
   - 右键点击记忆，选择 "Forget" 删除记忆
   - 点击顶部的 "Export" 按钮导出记忆
   - 点击顶部的 "Import" 按钮导入记忆

### 5.2 记忆质量仪表盘

#### 5.2.1 访问仪表盘

1. **启动服务器**：
   ```bash
   cd memory-classification-engine
   python3 -m memory_classification_engine.api.server
   ```

2. **访问仪表盘**：
   - 打开浏览器，访问 http://localhost:8000/dashboard/
   - 查看记忆质量统计和图表

#### 5.2.2 使用仪表盘

1. **时间范围过滤**：
   - 选择不同的时间范围（7天、30天、90天）
   - 点击 "Refresh" 按钮刷新数据

2. **查看详细信息**：
   - 查看记忆质量趋势图表
   - 查看记忆类型分布
   - 查看记忆质量详情表格

### 5.3 待确认记忆

#### 5.3.1 添加待确认记忆

```python
# 添加待确认记忆
memory = {
    'memory_type': 'user_preference',
    'content': 'I prefer using Python',
    'confidence': 0.95
}
memory_id = engine.add_pending_memory(memory)
print(f"Pending memory ID: {memory_id}")
```

#### 5.3.2 处理待确认记忆

```python
# 获取待确认记忆
pending_memories = engine.get_pending_memories()
print(f"Pending memories: {len(pending_memories)}")

# 批准记忆
if pending_memories:
    memory_id = pending_memories[0]['id']
    success = engine.approve_memory(memory_id)
    print(f"Approved memory: {success}")

# 拒绝记忆
if pending_memories:
    memory_id = pending_memories[0]['id']
    success = engine.reject_memory(memory_id)
    print(f"Rejected memory: {success}")

# 获取待确认记忆数量
count = engine.get_pending_count()
print(f"Pending memories count: {count}")
```

### 5.4 Nudge 机制

#### 5.4.1 获取 Nudge 候选

```python
# 获取 Nudge 候选
nudge_candidates = engine.get_nudge_candidates(limit=5)
print(f"Nudge candidates: {len(nudge_candidates)}")

# 生成 Nudge 提示
if nudge_candidates:
    prompt = engine.generate_nudge_prompt(nudge_candidates[0])
    print("Nudge prompt:")
    print(prompt)
```

#### 5.4.2 记录 Nudge 交互

```python
# 记录 Nudge 交互
if nudge_candidates:
    memory_id = nudge_candidates[0]['id']
    success = engine.record_nudge_interaction(memory_id, 'confirm')
    print(f"Recorded nudge interaction: {success}")

# 检查是否应该 Nudge
should_nudge = engine.should_nudge()
print(f"Should nudge: {should_nudge}")
```

### 5.5 多租户管理

```python
# 创建租户
tenant_id = "company_tenant"
result = engine.tenant_manager.create_tenant(
    tenant_id,
    "Company Tenant",
    "enterprise",
    user_id="admin"
)
print("创建租户结果:", result)

# 获取租户
tenant = engine.tenant_manager.get_tenant(tenant_id)
print("租户信息:", tenant)

# 列出所有租户
tenants = engine.tenant_manager.list_tenants()
print("所有租户:", tenants)
```

### 5.6 隐私设置

```python
# 设置用户隐私设置
user_id = "user1"
settings = {
    "data_retention_days": 30,
    "enable_encryption": True,
    "share_with_agents": False
}
result = engine.privacy_manager.set_user_settings(user_id, settings)
print("设置隐私设置结果:", result)

# 获取用户隐私设置
result = engine.privacy_manager.get_user_settings(user_id)
print("用户隐私设置:", result)

# 导出用户数据
result = engine.privacy_manager.export_user_data(user_id)
print("导出用户数据结果:", result)

# 删除用户数据
result = engine.privacy_manager.delete_user_data(user_id)
print("删除用户数据结果:", result)
```

### 5.7 审计日志

```python
# 查看审计日志
logs = engine.audit_manager.get_logs(user_id="user1", action="process_message")
print("审计日志:", logs)

# 生成审计报告
report = engine.audit_manager.generate_report(start_time="2026-01-01", end_time="2026-01-31")
print("审计报告:", report)
```

### 5.8 性能监控

```python
# 获取性能指标
metrics = engine.performance_monitor.get_metrics()
print("性能指标:", metrics)

# 重置性能指标
engine.performance_monitor.reset_metrics()
print("性能指标已重置")
```

## 6. 最佳实践

### 6.1 记忆管理

- **定期优化**：定期调用 `optimize_system()` 方法优化系统性能，建议每天或每周执行一次
- **压缩记忆**：定期调用 `compress_memories()` 方法压缩记忆，减少存储空间，建议每月执行一次
- **设置重要性**：对于重要的记忆，设置较高的重要性级别，确保它们不会被遗忘
- **批量操作**：对于大量记忆操作，使用批量API而不是单个操作，提高效率
- **记忆标签**：为记忆添加标签，便于后续检索和管理

### 6.2 Agent使用

- **选择合适的Agent**：根据任务类型选择合适的Agent框架，例如ClaudeCode适合代码生成，WorkBuddy适合协作任务
- **管理Agent生命周期**：使用完Agent后，及时注销它们，释放资源
- **配置Agent参数**：根据具体需求配置Agent的参数，以获得最佳效果
- **Agent组合**：对于复杂任务，可以组合多个Agent的能力
- **错误处理**：为Agent操作添加适当的错误处理，提高系统稳定性

### 6.3 知识库集成

- **设置Obsidian vault**：确保正确设置Obsidian vault路径，以便记忆能够正确写回知识库
- **定期同步**：定期调用 `sync_knowledge_base()` 方法同步知识库，确保数据一致性
- **合理组织知识**：在Obsidian中合理组织知识，使用文件夹和标签分类
- **知识链接**：在Obsidian中创建知识之间的链接，形成知识网络
- **版本控制**：考虑使用Git等版本控制系统管理Obsidian vault

### 6.4 性能优化

- **调整缓存大小**：根据系统资源调整缓存大小，平衡性能和内存使用
- **禁用不需要的功能**：如果不需要某些功能（如LLM或Neo4j），可以在配置文件中禁用它们，提高性能
- **优化存储**：定期清理不需要的记忆，减少存储压力
- **批量处理**：对于大量数据操作，使用批量处理减少数据库访问次数
- **异步操作**：对于耗时操作，考虑使用异步处理，提高系统响应速度
- **硬件优化**：根据系统负载，适当增加内存或使用SSD存储

### 6.5 安全最佳实践

- **API密钥管理**：使用环境变量或密钥管理服务存储API密钥，避免硬编码
- **数据加密**：启用敏感数据加密，保护用户隐私
- **访问控制**：设置适当的访问权限，限制对记忆的访问
- **审计日志**：启用审计日志，记录系统操作
- **定期备份**：定期备份记忆数据，防止数据丢失

### 6.6 常见使用场景

#### 6.6.1 智能客服

```python
# 初始化引擎
engine = MemoryClassificationEngine()

# 处理用户查询
def handle_customer_query(user_id, query):
    # 检索相关记忆
    memories = engine.retrieve_memories(query, user_id=user_id)
    
    # 构建上下文
    context = {
        "user_id": user_id,
        "previous_memories": memories
    }
    
    # 处理查询
    result = engine.process_message(query, context=context)
    
    # 存储新记忆
    if result.get("matches"):
        for match in result["matches"]:
            # 可以添加额外的元数据
            match["user_id"] = user_id
            engine.manage_memory("edit", match["id"], match)
    
    return result
```

#### 6.6.2 个人助理

```python
# 初始化引擎
engine = MemoryClassificationEngine()

# 管理用户偏好
def update_user_preference(user_id, preference):
    result = engine.process_message(
        f"用户偏好：{preference}",
        context={"user_id": user_id, "memory_type": "user_preference"}
    )
    return result

# 检索用户偏好
def get_user_preferences(user_id):
    memories = engine.retrieve_memories(
        "user_preference",
        memory_type="user_preference",
        user_id=user_id
    )
    return memories

# 智能推荐
def recommend_content(user_id, current_topic):
    # 检索相关记忆
    memories = engine.retrieve_memories(
        current_topic,
        user_id=user_id,
        limit=5
    )
    
    # 基于记忆生成推荐
    recommendations = []
    for memory in memories:
        if "preference" in memory.get("content", "").lower():
            recommendations.append(memory["content"])
    
    return recommendations
```

#### 6.6.3 企业知识管理

```python
# 初始化引擎
engine = MemoryClassificationEngine()

# 创建企业租户
def create_company_tenant(company_id, company_name):
    result = engine.tenant_manager.create_tenant(
        company_id,
        company_name,
        "enterprise"
    )
    return result

# 共享记忆到团队
def share_memory_to_team(memory_id, team_id):
    result = engine.manage_memory(
        "edit",
        memory_id,
        {"visibility": "team", "team_id": team_id}
    )
    return result

# 批量导入企业知识
def import_company_knowledge(company_id, knowledge_items):
    for item in knowledge_items:
        result = engine.process_message(
            item["content"],
            context={
                "user_id": "system",
                "tenant_id": company_id,
                "memory_type": "fact_declaration"
            }
        )
    return len(knowledge_items)
```

## 7. 故障排除

### 7.1 常见问题

#### 7.1.1 记忆分类不准确

**问题**：记忆分类结果与预期不符。

**解决方案**：
- 检查规则配置是否正确
- 考虑启用LLM功能，提高分类准确性
- 提供反馈，帮助系统学习和改进

#### 7.1.2 性能问题

**问题**：系统响应缓慢或内存使用过高。

**解决方案**：
- 调整缓存大小和批处理大小
- 禁用不需要的功能
- 定期优化系统和压缩记忆

#### 7.1.3 知识库集成问题

**问题**：无法将记忆写回知识库或从知识库获取知识。

**解决方案**：
- 确保Obsidian已安装且vault路径设置正确
- 检查文件权限
- 确保Obsidian vault目录存在

#### 7.1.4 Agent框架问题

**问题**：无法注册或使用Agent。

**解决方案**：
- 检查Agent适配器是否正确安装
- 确保API密钥有效（如果需要）
- 检查网络连接

### 7.2 日志和调试

- **查看日志**：系统会生成详细的日志，帮助你了解系统运行状态和错误信息
- **启用调试模式**：在配置文件中设置 `debug: true`，获取更详细的调试信息
- **使用性能监控**：定期检查性能指标，发现潜在问题

### 7.3 联系支持

如果遇到无法解决的问题，请在GitHub仓库中创建一个issue，提供详细的错误信息和复现步骤，我们将尽快帮助你解决问题。

## 8. 总结

记忆分类引擎是一个强大的智能记忆管理系统，通过合理使用其各项功能，你可以：

- 自动分类和存储用户记忆
- 智能检索相关记忆
- 与多种Agent框架集成，扩展系统能力
- 与Obsidian等知识库工具集成，实现知识的双向流动
- 保护用户隐私，确保数据安全
- 优化系统性能，提高响应速度

希望本指南能够帮助你充分利用记忆分类引擎的能力，为你的应用或服务增添智能记忆管理功能。