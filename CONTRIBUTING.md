# Contributing to CarryMem

感谢你对 CarryMem 项目的关注！我们欢迎各种形式的贡献。

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/carrymem.git
cd carrymem
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
pip install -e .  # 开发模式安装
```

### 4. 运行测试

```bash
pytest tests/ -v
```

## 代码规范

### Python 代码风格

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 最大行长度：100 字符
- 使用类型提示（Type Hints）

### 命名约定

- 类名：`PascalCase`
- 函数/方法：`snake_case`
- 常量：`UPPER_SNAKE_CASE`
- 私有方法：`_leading_underscore`

### 文档字符串

使用 Google 风格的文档字符串：

```python
def function_name(param1: str, param2: int) -> bool:
    """简短描述函数功能。
    
    更详细的描述（可选）。
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
        
    Returns:
        返回值的描述
        
    Raises:
        ValueError: 什么情况下抛出此异常
    """
    pass
```

## 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链相关

**示例**:
```
feat(semantic): add multilingual synonym expansion

- Add support for Chinese and Japanese synonyms
- Implement cross-language mapping
- Add 500+ technical terms

Closes #123
```

## 测试要求

### 1. 单元测试

- 所有新功能必须有对应的单元测试
- 测试覆盖率应保持在 80% 以上
- 使用 pytest 框架

```python
def test_classify_preference():
    """Test preference classification."""
    cm = CarryMem()
    result = cm.classify_message("I prefer dark mode")
    assert result['type'] == 'preference'
    assert result['confidence'] > 0.8
```

### 2. 集成测试

- 测试多个模块的交互
- 测试真实使用场景

### 3. 性能测试

- 关键操作应有性能基准测试
- 确保性能不退化

```python
def test_recall_performance():
    """Test recall performance with 500 memories."""
    # 应在 100ms 内完成
    assert duration < 0.1
```

## Pull Request 流程

### 1. Fork 仓库

点击 GitHub 页面右上角的 "Fork" 按钮。

### 2. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 3. 开发和测试

```bash
# 编写代码
# 运行测试
pytest tests/ -v

# 检查代码风格
flake8 src/
```

### 4. 提交更改

```bash
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

1. 访问你的 Fork 仓库
2. 点击 "New Pull Request"
3. 填写 PR 描述：
   - 更改内容
   - 相关 Issue
   - 测试结果
   - 截图（如适用）

### 6. Code Review

- 维护者会审查你的代码
- 根据反馈进行修改
- 所有测试必须通过
- 至少一个维护者批准后才能合并

## 项目结构

```
carrymem/
├── src/
│   └── memory_classification_engine/
│       ├── __init__.py
│       ├── carrymem.py          # 主入口
│       ├── engine.py             # 分类引擎
│       ├── quality_scorer.py     # 质量评分
│       ├── conflict_detector.py  # 冲突检测
│       ├── adapters/             # 存储适配器
│       ├── layers/               # 分类层
│       ├── semantic/             # 语义扩展
│       └── utils/                # 工具函数
├── tests/                        # 测试文件
├── docs/                         # 文档
├── benchmarks/                   # 性能基准
└── examples/                     # 示例代码
```

## 开发指南

### 添加新的记忆类型

1. 在 `layers/` 目录创建新的层类
2. 继承 `BaseLayer` 类
3. 实现 `classify()` 方法
4. 在 `engine.py` 中注册新层
5. 添加测试用例

### 添加新的存储适配器

1. 在 `adapters/` 目录创建新适配器
2. 继承 `BaseAdapter` 类
3. 实现所有抽象方法
4. 添加测试用例

### 添加新的语言支持

1. 在 `semantic/data/` 添加同义词文件
2. 更新 `semantic/expander.py`
3. 添加语言检测规则
4. 添加测试用例

## 常见问题

### Q: 如何运行特定的测试？

```bash
pytest tests/test_carrymem.py::TestENPreference -v
```

### Q: 如何查看测试覆盖率？

```bash
pytest --cov=src/memory_classification_engine tests/
```

### Q: 如何调试测试？

```bash
pytest tests/ -v -s  # -s 显示 print 输出
pytest tests/ --pdb  # 失败时进入调试器
```

### Q: 如何生成文档？

```bash
cd docs
make html
```

## 获取帮助

- 📖 查看 [文档](README.md)
- 💬 提交 [Issue](https://github.com/yourusername/carrymem/issues)
- 📧 发送邮件到 your.email@example.com

## 行为准则

- 尊重所有贡献者
- 保持友好和专业
- 接受建设性批评
- 关注项目目标

## 许可证

通过贡献代码，你同意你的贡献将在 MIT 许可证下发布。

---

**感谢你的贡献！** 🎉
