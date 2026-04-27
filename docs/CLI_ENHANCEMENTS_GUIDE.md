# CarryMem CLI 增强功能使用指南

**版本**: v0.2.0  
**日期**: 2026-04-27  
**状态**: 已实现

---

## 概述

本文档介绍 CarryMem 新增的 CLI 增强功能，包括：
- `doctor` - 系统诊断命令
- `status` - 系统状态查看
- `setup-mcp` - 简化的 MCP 配置

这些功能已在 `cli_enhancements.py` 模块中实现。

---

## 安装和使用

### 方式 1: 独立使用（推荐用于测试）

```bash
# 运行 doctor 命令
python3 -m memory_classification_engine.cli_enhancements doctor

# 运行 status 命令
python3 -m memory_classification_engine.cli_enhancements status

# 运行 setup-mcp 命令
python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool claude
```

### 方式 2: 集成到主 CLI（需要修改 cli.py）

将 `cli_enhancements.py` 中的函数导入到 `cli.py`：

```python
# 在 cli.py 顶部添加
from memory_classification_engine.cli_enhancements import (
    cmd_doctor,
    cmd_status,
    cmd_setup_mcp as cmd_setup_mcp_enhanced
)

# 在 main() 函数的 commands 字典中更新
commands = {
    # ... 现有命令 ...
    "doctor": cmd_doctor,
    "status": cmd_status,
    "setup-mcp": cmd_setup_mcp_enhanced,
    # ... 其他命令 ...
}
```

---

## 功能详解

### 1. Doctor 命令 - 系统诊断

**用途**: 自动检测系统健康状况，发现潜在问题

**使用方法**:
```bash
python3 -m memory_classification_engine.cli_enhancements doctor
```

**检查项目**:
1. ✅ Python 版本（需要 3.9+）
2. ✅ 全局命令可用性
3. ✅ 数据库状态
4. ✅ MCP 配置
5. ✅ 依赖包（PyYAML, Textual）

**输出示例**:
```
🔍 Checking CarryMem health...

✅ Python version: 3.11.0
✅ Command 'carrymem' is available
✅ Database: /Users/xxx/.carrymem/memories.db
   (42 memories, 1.2 MB)
✅ MCP config: Found in Claude Desktop
✅ PyYAML: Installed
ℹ️  Textual: Not installed (TUI unavailable)

==================================================
✅ All checks passed! CarryMem is healthy.
```

**问题诊断示例**:
```
🔍 Checking CarryMem health...

❌ Python version: 3.8.0 (需要 3.9+)
⚠️  Command 'carrymem' not in PATH
⚠️  Database not found: /Users/xxx/.carrymem/memories.db
⚠️  MCP config: Not configured in Claude Desktop

==================================================
❌ Found 1 issue(s):
   - Python 版本过低
⚠️  Found 3 warning(s):
   - 全局命令不可用
   - 数据库未初始化
   - MCP 未配置

💡 Suggested fixes:
   - Upgrade Python: brew install python@3.11
   - Run: pip uninstall carrymem -y && pip install -e .
   - Or add to PATH: export PATH="$PATH:$(python3 -m site --user-base)/bin"
   - Run: python3 -m memory_classification_engine.cli init
   - Run: python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool claude
```

---

### 2. Status 命令 - 系统状态

**用途**: 查看 CarryMem 当前状态概览

**使用方法**:
```bash
python3 -m memory_classification_engine.cli_enhancements status
```

**显示信息**:
1. 数据库信息（位置、大小、记忆数量）
2. 按类型统计
3. 按命名空间统计
4. MCP 连接状态
5. 最近活动

**输出示例**:
```
📊 CarryMem Status
==================================================

💾 Database: /Users/xxx/.carrymem/memories.db
📝 Memories: 42 items (1.2 MB)

📊 By Type:
   - user_preference: 15
   - factual_knowledge: 12
   - task_context: 8
   - conversation_history: 7

🏷️  Namespaces:
   - default: 30
   - work: 12

🔌 MCP Status:
   ✅ Claude Desktop: Configured
   ℹ️  Cursor: Not detected

🎯 Recent Activity:
   - I prefer dark mode
   - Using React for frontend development
   - Meeting with team at 3pm tomorrow
```

---

### 3. Setup-MCP 命令 - MCP 配置

**用途**: 自动检测并配置 MCP 集成

**使用方法**:

#### 自动检测模式（推荐）
```bash
python3 -m memory_classification_engine.cli_enhancements setup-mcp
# 或
python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool auto
```

#### 指定工具
```bash
# 配置 Claude Desktop
python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool claude

# 配置 Cursor
python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool cursor
```

**支持的工具**:
- Claude Desktop
- Cursor

**输出示例**:
```
🔌 Setting up MCP integration...

✅ Detected 1 tool(s):
   - claude

📝 Configuring claude...
✅ Updated /Users/xxx/Library/Application Support/Claude/claude_desktop_config.json

✅ MCP setup complete!

Next steps:
  1. Restart your tool (Claude Desktop/Cursor)
  2. Verify: python3 -m memory_classification_engine.cli_enhancements status
```

**配置内容**:
```json
{
  "mcpServers": {
    "carrymem": {
      "command": "python3",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"]
    }
  }
}
```

---

## 集成到主 CLI

如果要将这些命令集成到主 CLI（`carrymem` 命令），需要修改 `cli.py`：

### 步骤 1: 导入函数

在 `cli.py` 文件顶部添加：

```python
from memory_classification_engine.cli_enhancements import (
    cmd_doctor,
    cmd_status,
    cmd_setup_mcp
)
```

### 步骤 2: 更新命令字典

在 `main()` 函数中，更新 `commands` 字典：

```python
def main():
    # ... 现有代码 ...
    
    commands = {
        "add": cmd_add,
        "list": cmd_list,
        # ... 其他命令 ...
        "doctor": cmd_doctor,          # 新增
        "status": cmd_status,          # 新增
        "setup-mcp": cmd_setup_mcp,    # 更新
        # ... 其他命令 ...
    }
    
    # ... 其余代码 ...
```

### 步骤 3: 更新帮助信息

在 `show_help()` 函数中添加新命令的说明：

```python
def show_help():
    print(f"""
  {_bold('Commands:')}
    add <message>        Store a memory
    list                 List recent memories
    search <query>       Search memories
    show <key>           View memory details
    edit <key> <text>    Edit a memory
    forget <key>         Delete a memory
    clean                Remove expired/low-quality
    export <path>        Export memories to file
    import <path>        Import memories from file
    stats                Show memory statistics
    check                Check memory quality & conflicts
    doctor               Run system diagnostics      # 新增
    status               Show system status          # 新增
    setup-mcp            Configure MCP integration   # 更新
    tui                  Launch terminal UI
    serve                Start MCP HTTP server
    init                 Initialize CarryMem
    version              Show version

  {_bold('Examples:')}
    carrymem add "I prefer dark mode"
    carrymem search "theme"
    carrymem doctor                                  # 新增
    carrymem status                                  # 新增
    carrymem setup-mcp --tool claude                # 更新
    # ... 其他示例 ...
""")
```

### 步骤 4: 测试集成

```bash
# 重新安装
cd /Users/lin/trae_projects/carrymem
pip install -e .

# 测试新命令
carrymem doctor
carrymem status
carrymem setup-mcp --tool claude
```

---

## 故障排除

### 问题 1: 模块导入失败

**错误**:
```
ModuleNotFoundError: No module named 'memory_classification_engine.cli_enhancements'
```

**解决方案**:
```bash
# 确保文件存在
ls -la src/memory_classification_engine/cli_enhancements.py

# 重新安装
pip install -e .
```

### 问题 2: 命令不可用

**错误**:
```
Unknown command: doctor
```

**解决方案**:
- 使用完整路径：`python3 -m memory_classification_engine.cli_enhancements doctor`
- 或按照上述步骤集成到主 CLI

### 问题 3: 权限错误

**错误**:
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**:
```bash
# 检查文件权限
chmod 644 src/memory_classification_engine/cli_enhancements.py

# 不要使用 sudo
pip install -e .  # ✅ 正确
sudo pip install -e .  # ❌ 错误
```

---

## 测试

### 测试 Doctor 命令

```bash
# 正常情况
python3 -m memory_classification_engine.cli_enhancements doctor

# 模拟数据库不存在
mv ~/.carrymem/memories.db ~/.carrymem/memories.db.backup
python3 -m memory_classification_engine.cli_enhancements doctor
mv ~/.carrymem/memories.db.backup ~/.carrymem/memories.db
```

### 测试 Status 命令

```bash
# 查看状态
python3 -m memory_classification_engine.cli_enhancements status

# 添加记忆后再查看
python3 -m memory_classification_engine.cli add "test memory"
python3 -m memory_classification_engine.cli_enhancements status
```

### 测试 Setup-MCP 命令

```bash
# 自动检测
python3 -m memory_classification_engine.cli_enhancements setup-mcp

# 指定工具
python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool claude

# 验证配置
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

---

## 下一步

1. ✅ 测试所有新命令
2. ✅ 集成到主 CLI
3. ✅ 更新文档
4. [ ] 添加单元测试
5. [ ] 更新 CHANGELOG

---

## 相关文档

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排除指南
- [QUICK_FIX_GUIDE.md](QUICK_FIX_GUIDE.md) - 快速修复指南
- [OPTIMIZATION_RECOMMENDATIONS.md](OPTIMIZATION_RECOMMENDATIONS.md) - 优化建议
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - 实施总结

---

**最后更新**: 2026-04-27  
**版本**: v0.2.0
