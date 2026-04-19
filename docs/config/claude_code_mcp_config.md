# Claude Code MCP 配置指南

本指南将帮助您在 Claude Code 中配置 Memory Classification Engine (MCE) MCP 服务器，实现跨会话记忆回放功能。

## 1. 配置步骤

### 步骤 1：安装 MCE

```bash
pip install memory-classification-engine
```

### 步骤 2：创建 MCP 配置文件

在 `~/.claude/mcp.json` 文件中添加以下配置：

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

### 步骤 3：创建 CLAUDE.md 文件

在项目根目录创建 `CLAUDE.md` 文件，添加以下指令：

```markdown
## Memory System
When starting a new conversation, ALWAYS call mce_recall first.
Present results in a formatted list before responding to the user.
During conversation, call mce_process on each message that may contain memorable info.
```

## 2. 使用流程

### 新会话开始
1. 启动 Claude Code
2. 发送第一条消息
3. Claude 会自动调用 `mce_recall` 工具
4. 展示记忆列表，格式如下：

```
📝 MCE Memory Recall

## 已加载的记忆 (5/20)
- [偏好] 使用双引号而非单引号          置信度0.95 规则层   引用8次
- [偏好] 不喜欢过度设计的架构            置信度0.92 语义层   引用5次
- [决策] 项目采用Python技术栈             置信度0.89 模式层   +3关联
- [纠正] 否决复杂方案->倾向简化           置信度0.89 模式层
- [关系] 张三负责后端，李四做前端         置信度0.95 规则层

## 统计信息
- 过滤噪音: 23条
- LLM调用: 0次
- 处理消息: 342条
- 本周新增: 7条记忆

💡 这些记忆将影响我的回复，确保一致性体验
```

### 会话进行中
- 对每条包含值得记忆信息的消息，Claude 会调用 `mce_process` 工具
- 自动存储有价值的信息到 MCE

## 3. 工具说明

### mce_recall
- **功能**：回忆当前上下文中的相关记忆
- **参数**：
  - `context`：会话上下文（默认为 "general"）
  - `limit`：返回记忆数量限制（默认为 5）
  - `types`：按记忆类型过滤
  - `format`：输出格式（"text" 或 "json"）
  - `include_pending`：是否包含低置信度记忆

### mce_status
- **功能**：查看记忆系统状态
- **参数**：
  - `detail_level`：详细程度（"summary" 或 "full"）

### mce_forget
- **功能**：手动遗忘指定记忆
- **参数**：
  - `memory_id`：记忆 ID
  - `reason`：遗忘原因（可选）

## 4. 故障排除

### 常见问题

1. **MCP 服务器无法启动**
   - 检查 Python 环境是否正确
   - 确保已安装所有依赖
   - 查看日志输出了解具体错误

2. **记忆不显示**
   - 检查 MCE 数据存储路径是否正确
   - 确认有记忆被存储
   - 检查 `mce_recall` 调用参数

3. **性能问题**
   - 确保 `recall` 操作在 50ms 内完成
   - 限制返回记忆数量（默认 5 条）

## 5. 最佳实践

- **保持会话上下文清晰**：在 `mce_recall` 中使用具体的上下文参数
- **合理设置记忆限制**：根据实际需要调整 `limit` 参数
- **定期清理低价值记忆**：使用 `mce_forget` 工具删除不需要的记忆
- **监控记忆质量**：使用 `mce_status` 工具定期检查记忆系统状态

## 6. 示例

### 示例 1：代码上下文

```markdown
## Memory System
When starting a new conversation about coding, call mce_recall with context="coding".
Present results in a formatted list before responding to the user.
```

### 示例 2：部署上下文

```markdown
## Memory System
When starting a new conversation about deployment, call mce_recall with context="deployment".
Present results in a formatted list before responding to the user.
```

## 7. 版本信息

- **MCE 版本**：v0.1.0-beta
- **MCP 协议版本**：2024-11-05
- **支持的 Claude Code 版本**：v1.0+

---

通过以上配置，您可以在 Claude Code 中体验 MCE 的跨会话记忆回放功能，享受更智能、更个性化的 AI 交互体验。