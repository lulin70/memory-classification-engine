# Memory Classification Engine

## 项目概述

Memory Classification Engine 是一个智能记忆管理系统，用于分类、存储和检索用户的记忆数据。该系统采用多层存储架构，支持全文搜索、缓存预热和插件扩展，为用户提供高效的记忆管理能力。

## 目录结构

```
memory-classification-engine/
├── docs/             # 文档目录
├── src/              # 源代码
├── tests/            # 测试代码
└── requirements.txt  # 依赖文件
```

## 主要功能

- **多层存储架构**：工作记忆、程序性记忆、情节记忆、语义记忆
- **全文搜索**：基于SQLite FTS5的倒排索引检索
- **缓存系统**：LRU缓存和预热机制
- **插件架构**：支持功能扩展
- **异常处理**：统一的异常体系
- **CI/CD**：自动化测试和构建

## 快速开始

### 安装依赖

```bash
pip install -e .
```

### 运行测试

```bash
python -m pytest tests/
```

## 文档

### 架构文档
- [架构设计](./architecture/architecture.md)

### 用户指南
- [用户故事与场景](./user_guides/user_stories.md)
- [测试计划](./user_guides/testing.md)

### API文档
- [API文档](./api/api.md)
