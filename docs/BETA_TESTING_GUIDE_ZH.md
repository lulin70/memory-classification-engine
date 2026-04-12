# MCP Server Beta 测试指南

<p align="center">
  <strong>中文</strong> ·
  <a href="./BETA_TESTING_GUIDE_EN.md">English</a>
</p>

---

## 🎯 测试目标

感谢参与 Memory Classification Engine MCP Server 的 Beta 测试！

你的反馈将帮助我们改进产品，让它更好地服务于 Claude Code 用户。

---

## 📦 测试包内容

### 1. 项目仓库

```bash
# 克隆仓库
git clone https://github.com/lulin70/memory-classification-engine.git
cd memory-classification-engine
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装项目
pip install -e .

# 下载模型（首次运行需要）
python download_model.py
```

### 3. 配置 Claude Code

```bash
# 1. 找到 Claude Code 配置目录
# macOS: ~/.config/claude/
# Windows: %APPDATA%/Claude/

# 2. 创建或编辑 config.json
cat > ~/.config/claude/config.json << 'EOF'
{
  "mcpServers": {
    "memory-classification-engine": {
      "command": "python",
      "args": ["-m", "memory_classification_engine", "mcp"],
      "env": {
        "MCE_CONFIG_PATH": "$(pwd)/config/config.yaml",
        "MCE_DATA_PATH": "$(pwd)/data",
        "HF_DATASETS_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "HF_HOME": "$(pwd)/models"
      }
    }
  }
}
EOF

# 3. 重启 Claude Code
```

---

## 🧪 测试场景

### 场景 1: 基础功能测试（5分钟）

**目标**: 验证 MCP Server 能正常工作

**步骤**:
1. 启动 Claude Code
2. 查看 MCP tools 列表（应该显示 8 个 tools）
3. 发送一条消息: "我喜欢使用双引号"
4. 观察是否自动分类并存储记忆

**预期结果**:
- Claude Code 显示可用的 tools
- 消息被正确分类为 user_preference
- 记忆被存储

### 场景 2: 记忆检索测试（5分钟）

**目标**: 验证记忆能被正确检索

**步骤**:
1. 告诉 Claude: "记住，我更喜欢 Python 而不是 JavaScript"
2. 过几分钟，问: "我之前说过我喜欢什么编程语言？"
3. 观察 Claude 是否能回忆起你的偏好

**预期结果**:
- Claude 能检索到之前的记忆
- 回答准确反映你的偏好

### 场景 3: 长期对话测试（10分钟）

**目标**: 验证多轮对话中的记忆保持

**步骤**:
1. 进行 5-10 轮技术讨论
2. 在对话中自然表达偏好和决策
   - "我觉得这个方案太复杂了"
   - "我们团队用 PostgreSQL"
   - "张三负责后端开发"
3. 在对话后期询问之前的讨论内容

**预期结果**:
- 重要信息被自动记忆
- Claude 能关联上下文
- 不会重复询问已知信息

### 场景 4: 边界情况测试（5分钟）

**目标**: 测试异常处理

**步骤**:
1. 发送非常短的消息: "好"
2. 发送非常长的消息（复制一大段代码）
3. 发送无意义的消息: "asdfgh"

**预期结果**:
- 短消息/无意义消息被正确忽略
- 长消息能正常处理
- 系统不会崩溃

---

## 📊 反馈收集

### 必答问题

请复制以下模板填写：

```markdown
## Beta 测试反馈

### 基本信息
- 测试日期: 2026-XX-XX
- Claude Code 版本: 
- 操作系统: macOS/Windows/Linux
- Python 版本: 

### 功能测试
1. MCP Server 是否正常启动？
   - [ ] 是
   - [ ] 否
   - 问题描述: 

2. 8 个 Tools 是否都能正常工作？
   - [ ] 是
   - [ ] 否
   - 哪个 Tool 有问题: 

3. 记忆分类是否准确？
   - [ ] 非常准确
   - [ ] 比较准确
   - [ ] 一般
   - [ ] 不太准确
   - 举例说明: 

4. 记忆检索是否有效？
   - [ ] 非常有效
   - [ ] 比较有效
   - [ ] 一般
   - [ ] 不太有效
   - 举例说明: 

### 性能体验
5. 响应速度如何？
   - [ ] 很快 (< 1秒)
   - [ ] 较快 (1-3秒)
   - [ ] 一般 (3-5秒)
   - [ ] 较慢 (> 5秒)

6. 是否遇到卡顿或崩溃？
   - [ ] 没有
   - [ ] 偶尔
   - [ ] 经常
   - 问题描述: 

### 整体评价
7. 你会推荐给朋友使用吗？
   - [ ] 一定会
   - [ ] 可能会
   - [ ] 不确定
   - [ ] 可能不会
   - [ ] 一定不会

8. 最满意的 3 个功能:
   1. 
   2. 
   3. 

9. 最需要改进的 3 个方面:
   1. 
   2. 
   3. 

10. 其他建议:
    
```

---

## 🐛 问题报告

如果遇到问题，请在 GitHub 提交 Issue:

```
https://github.com/lulin70/memory-classification-engine/issues/new
```

**Issue 模板**:

```markdown
**标题**: [Bug] 简短描述

**环境**:
- OS: 
- Python: 
- Claude Code 版本: 

**复现步骤**:
1. 
2. 
3. 

**预期结果**:

**实际结果**:

**错误日志**:
```

---

## 💡 使用技巧

### 1. 让记忆更准确

- 明确表达偏好: "我喜欢...", "我更喜欢..."
- 明确表达纠正: "不对，应该是..."
- 明确表达决策: "我们决定..."

### 2. 优化检索效果

- 使用关键词查询: "我之前说的 Python 偏好"
- 提供上下文: "关于代码风格的讨论"

### 3. 避免误分类

- 避免模糊的表达: "这个还行"
- 避免临时的想法: "也许可以试试..."

---

## 📞 联系方式

如有问题，可以通过以下方式联系：

- GitHub Issues: https://github.com/lulin70/memory-classification-engine/issues
- GitHub Discussions: https://github.com/lulin70/memory-classification-engine/discussions
- Email: [你的邮箱]

---

## 🎁 感谢

再次感谢参与 Beta 测试！

你的反馈对我们非常重要，将直接影响产品的最终形态。

测试完成后，你将：
- 获得正式版的优先使用权
- 在项目的 Contributors 名单中留名
- 获得一份详细的测试报告

---

**测试包版本**: v0.1.0-beta  
**最后更新**: 2026-04-11  
**预计测试时间**: 30-60 分钟
