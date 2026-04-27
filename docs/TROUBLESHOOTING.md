# CarryMem 故障排除指南

**版本**: v0.8.0  
**更新日期**: 2026-04-27

---

## 常见问题

### 1. 命令找不到: `carrymem: command not found`

#### 症状
```bash
$ carrymem add "test"
zsh: command not found: carrymem
```

#### 原因
Python 的 bin 目录不在系统 PATH 中。

#### 解决方案

**方案 A: 重新安装（推荐）**

```bash
# 卸载
pip3 uninstall carrymem -y

# 重新安装
pip3 install carrymem

# 或从源码安装
cd /path/to/carrymem
pip3 install -e .
```

**方案 B: 添加到 PATH**

```bash
# 查找 Python bin 目录
python3 -m site --user-base

# 添加到 shell 配置文件
# 对于 zsh:
echo 'export PATH="$PATH:$(python3 -m site --user-base)/bin"' >> ~/.zshrc
source ~/.zshrc

# 对于 bash:
echo 'export PATH="$PATH:$(python3 -m site --user-base)/bin"' >> ~/.bashrc
source ~/.bashrc
```

**方案 C: 使用完整命令**

```bash
python3 -m memory_classification_engine.cli add "test"
python3 -m memory_classification_engine.cli list
```

**方案 D: 创建别名**

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
alias carrymem='python3 -m memory_classification_engine.cli'

# 重新加载
source ~/.zshrc  # 或 source ~/.bashrc
```

---

### 2. 数据库错误

#### 症状
```
Error: database is locked
Error: unable to open database file
```

#### 解决方案

**检查数据库位置**

```bash
# 默认位置
ls -la ~/.carrymem/memories.db

# 如果不存在，初始化
carrymem init
```

**修复损坏的数据库**

```bash
# 备份
cp ~/.carrymem/memories.db ~/.carrymem/memories.db.backup

# 重新初始化
rm ~/.carrymem/memories.db
carrymem init

# 导入备份（如果有导出文件）
carrymem import backup.json
```

---

### 3. MCP 配置问题

#### 症状
- Claude Desktop 无法连接 CarryMem
- MCP Server 启动失败

#### 解决方案

**检查配置文件**

```bash
# macOS
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 应该包含:
{
  "mcpServers": {
    "carrymem": {
      "command": "python3",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"]
    }
  }
}
```

**手动配置**

```bash
# 1. 找到配置文件
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Linux: ~/.config/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json

# 2. 编辑配置文件，添加 carrymem 配置

# 3. 重启 Claude Desktop
```

**测试 MCP Server**

```bash
# 直接运行 MCP Server
python3 -m memory_classification_engine.integration.layer2_mcp

# 应该看到 MCP Server 启动信息
```

---

### 4. Python 版本问题

#### 症状
```
ImportError: ...
SyntaxError: ...
```

#### 解决方案

**检查 Python 版本**

```bash
python3 --version
# 需要 Python 3.9 或更高版本
```

**升级 Python**

```bash
# macOS (使用 Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11

# 使用 pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

---

### 5. 依赖包问题

#### 症状
```
ModuleNotFoundError: No module named 'yaml'
ModuleNotFoundError: No module named 'textual'
```

#### 解决方案

**重新安装依赖**

```bash
# 基础依赖
pip3 install PyYAML

# TUI 依赖
pip3 install "carrymem[tui]"

# 语言检测依赖
pip3 install "carrymem[language]"

# 加密依赖
pip3 install "carrymem[encryption]"

# 所有依赖
pip3 install "carrymem[dev]"
```

---

### 6. 权限问题

#### 症状
```
PermissionError: [Errno 13] Permission denied: '/Users/xxx/.carrymem/memories.db'
```

#### 解决方案

**检查文件权限**

```bash
ls -la ~/.carrymem/
chmod 755 ~/.carrymem
chmod 644 ~/.carrymem/memories.db
```

**使用正确的用户**

```bash
# 不要使用 sudo 安装
pip3 install carrymem  # ✅ 正确
sudo pip3 install carrymem  # ❌ 错误
```

---

### 7. 记忆搜索不准确

#### 症状
- 搜索结果不相关
- 找不到明明存在的记忆

#### 解决方案

**重建搜索索引**

```bash
# 导出所有记忆
carrymem export backup.json

# 清空数据库
rm ~/.carrymem/memories.db

# 重新初始化
carrymem init

# 导入记忆
carrymem import backup.json
```

**使用更精确的查询**

```bash
# 使用引号
carrymem search "exact phrase"

# 使用类型过滤
carrymem list --type user_preference

# 使用命名空间
carrymem list --namespace work
```

---

### 8. 性能问题

#### 症状
- 命令响应慢
- 搜索耗时长

#### 解决方案

**清理过期记忆**

```bash
# 查看统计
carrymem stats

# 清理过期记忆
carrymem clean --expired

# 清理低质量记忆
carrymem clean --low-quality

# 干运行（查看会删除什么）
carrymem clean --expired --dry-run
```

**优化数据库**

```bash
# 导出
carrymem export backup.json

# 重建数据库
rm ~/.carrymem/memories.db
carrymem init
carrymem import backup.json
```

---

### 9. 导入/导出问题

#### 症状
```
Error: Invalid JSON format
Error: Failed to import memories
```

#### 解决方案

**检查 JSON 格式**

```bash
# 验证 JSON
python3 -m json.tool backup.json

# 如果格式错误，手动修复或重新导出
```

**使用正确的格式**

```json
[
  {
    "content": "I prefer dark mode",
    "type": "user_preference",
    "confidence": 0.95,
    "namespace": "default"
  }
]
```

---

### 10. TUI 无法启动

#### 症状
```
ModuleNotFoundError: No module named 'textual'
```

#### 解决方案

**安装 TUI 依赖**

```bash
pip3 install "carrymem[tui]"

# 或单独安装
pip3 install textual
```

**启动 TUI**

```bash
carrymem tui
```

---

## 诊断工具

### 健康检查

```bash
# 运行诊断（如果实现了）
carrymem doctor

# 输出示例:
# 🔍 Checking CarryMem health...
# ✅ Python version: 3.11.0
# ✅ Command available: carrymem
# ✅ Database: ~/.carrymem/memories.db (42 memories, 1.2 MB)
# ✅ MCP config: Found
# ⚠️  Warning: 5 expired memories (run 'carrymem clean --expired')
```

### 查看状态

```bash
# 查看系统状态（如果实现了）
carrymem status

# 输出示例:
# 📊 CarryMem Status
# 💾 Database: ~/.carrymem/memories.db
# 📝 Memories: 42 items (1.2 MB)
# 🏷️  Namespaces: default (30), work (12)
# 🔌 MCP: Connected to Claude Desktop
```

### 查看日志

```bash
# 查看详细日志
carrymem add "test" --verbose

# 查看数据库信息
sqlite3 ~/.carrymem/memories.db "SELECT COUNT(*) FROM memories;"
```

---

## 获取帮助

### 文档

- 📖 [README](../README.md)
- 🚀 [Quick Start Guide](QUICK_START_GUIDE.md)
- 🔧 [Quick Fix Guide](QUICK_FIX_GUIDE.md)
- 📋 [API Reference](API_REFERENCE.md)

### 社区

- 🐛 [报告 Bug](https://github.com/lulin70/memory-classification-engine/issues)
- 💬 [讨论](https://github.com/lulin70/memory-classification-engine/discussions)
- 📧 Email: lulin70@gmail.com

### 调试模式

```bash
# 启用详细输出
export CARRYMEM_DEBUG=1
carrymem add "test"

# 查看 Python 错误
python3 -m memory_classification_engine.cli add "test" 2>&1
```

---

## 常见错误代码

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| `E001` | 命令找不到 | 添加到 PATH 或重新安装 |
| `E002` | 数据库错误 | 检查权限或重新初始化 |
| `E003` | MCP 配置错误 | 检查配置文件 |
| `E004` | Python 版本过低 | 升级到 3.9+ |
| `E005` | 依赖包缺失 | 重新安装依赖 |

---

**最后更新**: 2026-04-27  
**版本**: v0.8.0
