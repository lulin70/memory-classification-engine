# CarryMem 快速修复指南

**日期**: 2026-04-27  
**版本**: v0.8.0  
**问题**: 全局 `carrymem` 命令不可用

---

## 问题诊断

### 症状

```bash
$ carrymem add "test"
zsh: command not found: carrymem
```

### 原因

setup.py 已经配置了全局命令，但需要重新安装才能生效。

---

## 解决方案

### 方案 1: 重新安装（推荐）

```bash
# 进入项目目录
cd /Users/lin/trae_projects/carrymem

# 卸载旧版本
pip uninstall carrymem -y

# 重新安装（开发模式）
pip install -e .

# 验证
carrymem version
```

**预期输出**:
```
CarryMem v0.8.0
```

---

### 方案 2: 使用完整命令（临时）

如果重新安装后仍不可用，使用完整命令：

```bash
python3 -m memory_classification_engine.cli add "test"
python3 -m memory_classification_engine.cli list
```

---

### 方案 3: 创建别名（临时）

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
alias carrymem='python3 -m memory_classification_engine.cli'

# 重新加载
source ~/.zshrc  # 或 source ~/.bashrc
```

---

## 验证修复

### 测试命令

```bash
# 1. 检查版本
carrymem version

# 2. 添加记忆
carrymem add "I prefer dark mode"

# 3. 列表显示
carrymem list

# 4. 搜索
carrymem search "dark"
```

### 预期结果

所有命令都应该正常工作，不再需要 `python3 -m ...` 前缀。

---

## 常见问题

### Q1: 重新安装后仍然找不到命令

**A**: 检查 Python 的 bin 目录是否在 PATH 中

```bash
# 查找 carrymem 安装位置
which carrymem

# 如果找不到，检查 Python bin 目录
python3 -m site --user-base

# 添加到 PATH（如果需要）
export PATH="$PATH:$(python3 -m site --user-base)/bin"
```

---

### Q2: 使用 pip install carrymem 安装的版本

**A**: 如果是从 PyPI 安装的，需要等待新版本发布，或者：

```bash
# 卸载 PyPI 版本
pip uninstall carrymem

# 从源码安装
cd /Users/lin/trae_projects/carrymem
pip install -e .
```

---

### Q3: 多个 Python 版本

**A**: 确保使用正确的 pip

```bash
# 使用 python3 对应的 pip
python3 -m pip install -e .

# 或者使用 pip3
pip3 install -e .
```

---

## 已修复的问题

✅ **setup.py 配置正确** - entry_points 已经配置了 `carrymem` 命令  
✅ **CLI 模块存在** - `memory_classification_engine.cli:main` 可用  
✅ **所有命令实现** - add, list, search, export, import 等都已实现

---

## 下一步

修复后，请更新以下文档：

1. **README.md** - 添加重新安装说明
2. **QUICK_START_GUIDE.md** - 更新安装步骤
3. **USER_READINESS_ASSESSMENT.md** - 更新评估结果

---

**修复完成后，CarryMem 的可用性评分将从 7/10 提升到 8/10！** 🚀
