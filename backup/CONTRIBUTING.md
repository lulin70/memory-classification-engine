# 贡献指南

感谢您对 Memory Classification Engine 项目的兴趣！我们欢迎各种形式的贡献，包括但不限于代码提交、问题报告、文档改进等。

## 贡献流程

1. **Fork 仓库**：在 GitHub 上 fork 本项目到您自己的账户
2. **克隆仓库**：将 fork 后的仓库克隆到本地
   ```bash
   git clone https://github.com/your-username/memory-classification-engine.git
   ```
3. **创建分支**：创建一个新的分支用于您的贡献
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **进行修改**：实现您的功能或修复
5. **运行测试**：确保您的修改不会破坏现有功能
   ```bash
   python -m pytest tests/
   ```
6. **提交代码**：使用清晰的提交信息提交您的修改
   ```bash
   git commit -m "feat: 描述您的修改"
   ```
7. **推送分支**：将您的分支推送到 GitHub
   ```bash
   git push origin feature/your-feature-name
   ```
8. **创建 PR**：在 GitHub 上创建一个 Pull Request，描述您的修改

## 代码规范

- 遵循 PEP 8 代码风格
- 使用 Black 进行代码格式化
- 确保代码有适当的注释
- 为新功能添加测试用例

## 提交规范

提交信息应遵循以下格式：

```
type: 描述

详细描述（可选）
```

其中 `type` 可以是：
- `feat`：新功能
- `fix`：bug 修复
- `docs`：文档更新
- `style`：代码风格调整
- `refactor`：代码重构
- `test`：测试相关
- `chore`：构建或依赖更新

## 问题报告

如果您发现了 bug 或有新功能建议，请在 GitHub Issues 中提交。提交时请包含：

- 问题的详细描述
- 重现步骤（如果是 bug）
- 预期行为
- 实际行为
- 环境信息（Python 版本等）

## 开发环境设置

1. 安装开发依赖：
   ```bash
   pip install -e .[dev]
   ```

2. 运行代码风格检查：
   ```bash
   flake8 src/
   ```

3. 运行代码格式化：
   ```bash
   black src/
   ```

## 联系我们

如果您有任何问题或建议，可以通过 GitHub Issues 与我们联系。

再次感谢您的贡献！