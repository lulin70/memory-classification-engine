# TRAE SDK 集成指南

本指南将帮助您在 TRAE 中集成 Memory Classification Engine (MCE)，实现跨会话记忆回放功能。

## 1. 集成方式

TRAE 支持两种集成方式：

1. **MCP 插件**：通过 MCP 协议集成
2. **SDK 直接调用**：通过 Python SDK 直接调用

## 2. SDK 直接调用

### 步骤 1：安装 MCE

```bash
pip install memory-classification-engine
```

### 步骤 2：基本集成示例

```python
from memory_classification_engine import MemoryOrchestrator

# 初始化 MCE
memory = MemoryOrchestrator()

# 会话开始时的记忆回放
def on_session_start():
    """会话开始时调用，展示记忆回放"""
    # 调用记忆回放
    recall_result = memory.recall(context="general", limit=5)
    
    # 渲染到 TRAE 面板
    render_to_panel("MCE Memory Recall", format_memory_recall(recall_result))

# 处理用户消息
def on_user_message(msg):
    """处理用户消息，存储有价值的信息"""
    # 处理消息并存储记忆
    result = memory.learn(msg)
    
    # 如果有新记忆被存储，显示提示
    if result.get("success"):
        log_to_console(f"MCE recorded a new memory: {result.get('memory_type')}")

# 格式化记忆回放结果
def format_memory_recall(memories):
    """格式化记忆回放结果"""
    if not memories:
        return "📝 MCE Memory Recall\n\n## 已加载的记忆 (0/5)\n- 还没有任何记忆记录。\n- 随着我们对话，我会记住你的偏好、决策和重要信息。\n\n## 统计信息\n- 过滤噪音: 0条\n- LLM调用: 0次\n- 处理消息: 0条\n- 本周新增: 0条记忆"
    
    # 格式化记忆列表
    memory_list = "\n".join([f"- [{mem.get('memory_type')}] {mem.get('content')}" for mem in memories])
    
    # 获取统计信息
    stats = memory.get_stats()
    total_memories = stats.get("total_memories", 0)
    
    return f"📝 MCE Memory Recall\n\n## 已加载的记忆 ({len(memories)}/{total_memories})\n{memory_list}\n\n## 统计信息\n- 过滤噪音: {total_memories - len(memories)}条\n- LLM调用: 0次\n- 处理消息: {stats.get('total_processed', 0)}条\n- 本周新增: {stats.get('weekly_additions', 0)}条记忆"

# 记忆状态查看
def on_memory_status():
    """查看记忆系统状态"""
    status = memory.get_memory_quality()
    render_to_panel("Memory Status", format_memory_status(status))

# 格式化记忆状态
def format_memory_status(status):
    """格式化记忆状态"""
    return f"📊 Memory Status\n\n## 总体质量\n- 平均质量: {status.get('average_quality', 0):.2f}\n- 高质量记忆: {status.get('high_quality_memories', 0)}\n- 总记忆数: {status.get('total_memories', 0)}\n\n## 按类型分布\n{"\n".join([f"- {type}: {count}" for type, count in status.get('type_distribution', {}).items()])}"
```

### 步骤 3：高级集成示例

```python
from memory_classification_engine import MemoryOrchestrator

# 初始化 MCE
memory = MemoryOrchestrator()

class MCEIntegration:
    """MCE 集成类"""
    
    def __init__(self):
        self.memory = MemoryOrchestrator()
        self.current_context = "general"
    
    def on_session_start(self, context="general"):
        """会话开始时调用"""
        self.current_context = context
        recall_result = self.memory.recall(context=context, limit=5)
        return self._format_recall_result(recall_result)
    
    def on_user_message(self, message):
        """处理用户消息"""
        result = self.memory.learn(message)
        return result
    
    def on_session_end(self):
        """会话结束时调用"""
        # 生成本次会话的记忆摘要
        summary = self._generate_session_summary()
        # 清理临时记忆
        self.memory.clear_working_memory()
        return summary
    
    def get_memory_status(self, detail_level="summary"):
        """获取记忆状态"""
        if detail_level == "full":
            return self.memory.generate_quality_report()
        else:
            return self.memory.get_stats()
    
    def forget_memory(self, memory_id, reason="user_request"):
        """手动遗忘记忆"""
        return self.memory.forget(memory_id, reason=reason)
    
    def _format_recall_result(self, memories):
        """格式化记忆回放结果"""
        if not memories:
            return "📝 MCE Memory Recall\n\n## 已加载的记忆 (0/5)\n- 还没有任何记忆记录。\n- 随着我们对话，我会记住你的偏好、决策和重要信息。"
        
        memory_list = "\n".join([f"- [{mem.get('memory_type')}] {mem.get('content')}" for mem in memories])
        stats = self.memory.get_stats()
        total_memories = stats.get("total_memories", 0)
        
        return f"📝 MCE Memory Recall\n\n## 已加载的记忆 ({len(memories)}/{total_memories})\n{memory_list}\n\n## 统计信息\n- 过滤噪音: {total_memories - len(memories)}条\n- LLM调用: 0次\n- 处理消息: {stats.get('total_processed', 0)}条\n- 本周新增: {stats.get('weekly_additions', 0)}条记忆"
    
    def _generate_session_summary(self):
        """生成本次会话的记忆摘要"""
        # 获取本次会话的记忆
        session_memories = self.memory.get_working_memory()
        
        if not session_memories:
            return "本次会话没有新的记忆记录。"
        
        # 按类型分组
        by_type = {}
        for mem in session_memories:
            mem_type = mem.get('memory_type')
            if mem_type not in by_type:
                by_type[mem_type] = []
            by_type[mem_type].append(mem.get('content'))
        
        # 生成摘要
        summary = "本次会话新增记忆：\n"
        for mem_type, contents in by_type.items():
            summary += f"\n{mem_type}:\n"
            for content in contents:
                summary += f"- {content}\n"
        
        return summary

# 使用示例
mce_integration = MCEIntegration()

# 会话开始
recall_output = mce_integration.on_session_start("coding")
print(recall_output)

# 处理用户消息
mce_integration.on_user_message("我更喜欢使用双引号")
mce_integration.on_user_message("张三是后端开发工程师")

# 会话结束
summary = mce_integration.on_session_end()
print(summary)
```

## 3. MCP 插件集成

### 步骤 1：配置 MCP 服务器

在 TRAE 的 MCP 配置中添加以下内容：

```json
{
  "mcpServers": {
    "memory-classification-engine": {
      "command": "python",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp.server"]
    }
  }
}
```

### 步骤 2：TRAE 插件示例

```python
import json
import asyncio

class MCEMemoryPlugin:
    """MCE 记忆插件"""
    
    def __init__(self, trae_api):
        self.trae_api = trae_api
        self.mcp_client = trae_api.get_mcp_client("memory-classification-engine")
    
    async def on_session_start(self, context="general"):
        """会话开始时调用"""
        # 调用 mce_recall 工具
        result = await self.mcp_client.call("mce_recall", {
            "context": context,
            "limit": 5,
            "format": "text"
        })
        
        # 显示记忆回放
        self.trae_api.show_panel("MCE Memory Recall", result.get("content", ""))
        return result
    
    async def on_user_message(self, message):
        """处理用户消息"""
        # 调用 mce_process 工具
        result = await self.mcp_client.call("classify_memory", {
            "message": message
        })
        
        # 如果有值得记忆的信息，存储它
        if result.get("matched"):
            await self.mcp_client.call("store_memory", {
                "content": result.get("content"),
                "memory_type": result.get("memory_type"),
                "tier": result.get("tier")
            })
        
        return result
    
    async def get_memory_status(self):
        """获取记忆状态"""
        result = await self.mcp_client.call("mce_status", {
            "detail_level": "summary"
        })
        return result
    
    async def forget_memory(self, memory_id, reason="user_request"):
        """手动遗忘记忆"""
        result = await self.mcp_client.call("mce_forget", {
            "memory_id": memory_id,
            "reason": reason
        })
        return result

# 使用示例
async def main():
    # 初始化 TRAE API
    trae_api = get_tra_api()
    
    # 初始化 MCE 插件
    mce_plugin = MCEMemoryPlugin(trae_api)
    
    # 会话开始
    await mce_plugin.on_session_start("general")
    
    # 处理用户消息
    await mce_plugin.on_user_message("我更喜欢使用双引号")
    await mce_plugin.on_user_message("张三是后端开发工程师")
    
    # 获取记忆状态
    status = await mce_plugin.get_memory_status()
    print(status)

# 运行
asyncio.run(main())
```

## 4. 会话生命周期集成

### 完整流程

1. **会话开始**
   - 调用 `on_session_start()` 方法
   - 执行 `mce_recall` 获取相关记忆
   - 以格式化方式展示记忆列表
   - 注入记忆到系统提示（可选）

2. **会话进行中**
   - 对每条用户消息调用 `on_user_message()` 方法
   - 自动存储有价值的信息
   - 实时更新记忆质量指标

3. **会话结束**
   - 调用 `on_session_end()` 方法
   - 生成本次会话的记忆摘要
   - 清理临时记忆
   - 更新长期记忆存储

## 5. 最佳实践

- **保持上下文清晰**：为不同类型的任务使用不同的上下文参数
- **合理设置记忆限制**：根据实际需要调整 `limit` 参数
- **定期清理低价值记忆**：使用 `forget` 方法删除不需要的记忆
- **监控记忆质量**：定期检查记忆系统状态
- **记忆注入**：将记忆注入到系统提示中，让记忆成为 Agent 身份的一部分
- **批量处理**：对于大量消息，使用批量处理方法提高效率

## 6. 性能优化

- **缓存记忆**：在会话期间缓存常用记忆，减少重复检索
- **异步处理**：使用异步方法处理记忆操作，避免阻塞主线程
- **批量操作**：使用批量方法处理多条消息，减少 I/O 操作
- **索引优化**：确保存储系统有适当的索引，提高检索速度
- **内存管理**：定期清理低价值记忆，避免内存膨胀

## 7. 故障排除

### 常见问题

1. **MCE 初始化失败**
   - 检查 Python 环境是否正确
   - 确保已安装所有依赖
   - 查看日志输出了解具体错误

2. **记忆不显示**
   - 检查 MCE 数据存储路径是否正确
   - 确认有记忆被存储
   - 检查 `recall` 调用参数

3. **性能问题**
   - 确保 `recall` 操作在 50ms 内完成
   - 限制返回记忆数量（默认 5 条）
   - 使用缓存减少重复检索

4. **内存膨胀**
   - 定期清理低价值记忆
   - 设置合理的记忆存储限制
   - 监控记忆系统状态

## 8. 版本信息

- **MCE 版本**：v0.1.0-beta
- **TRAE SDK 版本**：v1.0+
- **Python 版本**：3.8+

---

通过以上集成，您可以在 TRAE 中体验 MCE 的跨会话记忆回放功能，享受更智能、更个性化的 AI 交互体验。