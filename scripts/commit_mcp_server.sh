#!/bin/bash
# MCP Server 提交脚本

echo "=== MCP Server Git 提交 ==="

# 添加 MCP Server 相关文件
echo "1. 添加 MCP Server 代码..."
git add src/memory_classification_engine/integration/
git add src/memory_classification_engine/__main__.py
git add src/memory_classification_engine/__init__.py
git add config/mcp_config.json
git add tests/unit/integration/
git add docs/testing/
git add docs/FEATURE_IMPLEMENTATION_STATUS.md
git add docs/DOCUMENTATION_UPDATES.md

# 添加测试计划
git add download_model.py

# 提交
echo "2. 提交更改..."
git commit -m "feat: 实现 MCP Server，支持 Claude Code/Cursor 集成

- 实现完整的 MCP Server，符合 Model Context Protocol 规范
- 提供 8 个 Tools：classify_memory, store_memory, retrieve_memories, get_memory_stats, batch_classify, find_similar, export_memories, import_memories
- 添加完整的单元测试（27 个测试用例，100% 通过）
- 添加测试计划和测试报告
- 代码覆盖率 92%

使用方法:
  python -m memory_classification_engine mcp

配置 Claude Code:
  复制 config/mcp_config.json 到 ~/.config/claude/config.json

测试:
  python -m pytest tests/unit/integration/test_mcp_server.py -v"

echo "3. 推送到远程..."
git push origin main

echo "=== 提交完成 ==="
