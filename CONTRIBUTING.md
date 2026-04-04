# 贡献指南

## 如何贡献

我们欢迎并感谢所有形式的贡献，包括但不限于：

- 报告bug
- 提交功能请求
- 改进文档
- 提交代码

## 开发流程

### 1. 环境设置

1. **克隆仓库**
   ```bash
   git clone https://github.com/lulin70/memory-classification-engine.git
   cd memory-classification-engine
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # 或
   venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

### 2. 代码规范

- 使用 `black` 进行代码格式化
  ```bash
  black src/ tests/
  ```

- 使用 `isort` 管理导入
  ```bash
  isort src/ tests/
  ```

- 使用 `flake8` 进行代码检查
  ```bash
  flake8 src/ tests/
  ```

- 使用 `mypy` 进行类型检查
  ```bash
  mypy src/
  ```

### 3. 测试

- 运行所有测试
  ```bash
  python -m pytest tests/
  ```

- 运行特定测试
  ```bash
  python -m pytest tests/test_engine.py
  ```

### 4. 提交代码

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **提交更改**
   ```bash
   git add .
   git commit -m "你的提交信息"
   ```

3. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **创建Pull Request**
   - 访问 GitHub 仓库
   - 点击 "New Pull Request"
   - 选择你的分支
   - 填写PR描述

## 代码风格

- 使用4个空格进行缩进
- 类名使用驼峰命名法（CamelCase）
- 函数和变量名使用蛇形命名法（snake_case）
- 模块名使用小写字母，可使用下划线
- 每行代码长度不超过120个字符
- 文档字符串使用Google风格

## 报告问题

如果你发现了bug或有功能请求，请在GitHub上创建一个issue，包括：

- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息
- 相关截图（如果适用）

## 行为准则

我们遵循以下行为准则：

- 尊重所有贡献者
- 接受建设性批评
- 关注社区的最佳利益
- 友善和包容

## 许可证

通过贡献，你同意你的贡献将在MIT许可证下发布。