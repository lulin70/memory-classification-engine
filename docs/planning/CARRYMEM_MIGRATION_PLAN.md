# CarryMem 命名迁移计划 (v1.0)

**日期**: 2026-04-20
**版本**: v1.0
**参考**: MCP_POSITIONING_CONSENSUS_v3.md §9.6

---

## 1. 迁移范围

### 1.1 需要改名的对象

| 对象 | 当前名 | 目标名 | 优先级 |
|------|--------|--------|--------|
| 本地目录 | `memory-classification-engine` | `carrymem` | P0 |
| GitHub 仓库 | `memory-classification-engine` | `carrymem` | P1 (v0.7) |
| PyPI 包名 | `memory-classification-engine` | `carrymem` | P0 (v0.6) |
| Python 模块名 | `memory_classification_engine` | `carrymem` | P0 (v0.6) |
| CLI 命令 | `mce` | `carrymem` | P1 (v0.6) |
| 配置目录 | `~/.mce` | `~/.carrymem` | P1 (v0.6) |
| 环境变量前缀 | `MCE_` | `CARRYMEM_` | P2 (v0.7) |

### 1.2 不改名的对象

| 对象 | 名称 | 原因 |
|------|------|------|
| 引擎内部模块 | `mce/` | MCE 保留为引擎层内部名 (类似 InnoDB) |
| 引擎类名 | `MemoryClassificationEngine` | 内部实现，不影响用户 |
| 数据库表名 | `memories` | 存储层内部，不影响用户 |
| 现有文档引用 | v3.3 之前的文档 | 历史文档保持原样 |

---

## 2. 分阶段迁移

### Phase 1: v0.5 — 文档和品牌 (现在)

**动作**: 文档层面改名，代码不动

| 任务 | 描述 | 风险 |
|------|------|------|
| README.md 更新 | 标题改为 CarryMem，保留 MCE 作为引擎名引用 | 无 |
| ROADMAP.md 更新 | 已完成 | 无 |
| 共识文档更新 | 已完成 (v4.0) | 无 |
| 新文档使用 CarryMem | 所有新文档使用 CarryMem 品牌 | 无 |

**兼容性**: 100% — 代码完全不变

### Phase 2: v0.6 — 包名和目录 (2周后)

**动作**: PyPI 包名 + 本地目录名 + Python 模块名

#### 2.1 本地目录重命名

```bash
# 在 trae_projects 目录下执行
cd /Users/lin/trae_projects
mv memory-classification-engine carrymem
cd carrymem
```

#### 2.2 Python 模块重命名

```bash
# 在项目内
cd /Users/lin/trae_projects/carrymem/src
mv memory_classification_engine carrymem

# 更新所有内部 import
# find . -name "*.py" -exec sed -i '' 's/memory_classification_engine/carrymem/g' {} +
```

#### 2.3 PyPI 双包名

```toml
# pyproject.toml
[project]
name = "carrymem"
version = "0.6.0"

# 同时发布 mce 别名包
# mce/ 包只包含 __init__.py: from carrymem import *
```

#### 2.4 CLI 命令

```bash
# 新命令
carrymem run          # 启动 MCP Server
carrymem classify     # 分类单条消息
carrymem recall       # 检索记忆

# 旧命令 (兼容)
mce run               # → carrymem run
```

#### 2.5 配置目录

```bash
# 新配置目录
~/.carrymem/
├── config.yaml
├── memories.db       # SQLite 数据库
└── logs/

# 旧配置目录 (自动迁移)
~/.mce/               # v0.5 及之前
```

**兼容性**: 双包名 — `pip install mce` 自动安装 `carrymem`

### Phase 3: v0.7 — GitHub 仓库 (1月后)

**动作**: GitHub 仓库重命名

```bash
# GitHub 仓库重命名 (通过 GitHub API 或 Web UI)
# memory-classification-engine → carrymem

# GitHub 自动创建重定向
# https://github.com/lin/memory-classification-engine → https://github.com/lin/carrymem
# git remote 会自动跟随
```

**兼容性**: GitHub 自动重定向旧 URL

### Phase 4: v1.0 — 清理 (3月后)

**动作**: `mce` 别名标记 deprecated

```python
# mce/__init__.py
import warnings
warnings.warn(
    "The 'mce' package name is deprecated. Use 'carrymem' instead. "
    "The 'mce' alias will be removed in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)
from carrymem import *
```

**兼容性**: 6 个月过渡期

---

## 3. 内部 Import 迁移清单

### 3.1 需要更新的文件

| 文件 | 当前 import | 目标 import |
|------|------------|------------|
| `src/carrymem/__init__.py` | `from memory_classification_engine import ...` | 直接定义 |
| `src/carrymem/engine.py` | `from memory_classification_engine.layers import ...` | `from carrymem.mce.layers import ...` |
| `src/carrymem/mce/**/*.py` | `from memory_classification_engine import ...` | `from carrymem.mce import ...` |
| `src/carrymem/adapters/*.py` | `from memory_classification_engine.adapters import ...` | `from carrymem.adapters import ...` |
| `tests/**/*.py` | `from memory_classification_engine import ...` | `from carrymem import ...` |
| `benchmarks/*.py` | `from memory_classification_engine import ...` | `from carrymem import ...` |
| `setup.py` | `memory_classification_engine` | `carrymem` |

### 3.2 批量替换命令

```bash
# 在项目根目录执行
find . -name "*.py" -not -path "./.git/*" -exec sed -i '' \
    's/from memory_classification_engine/from carrymem.mce/g' {} +

find . -name "*.py" -not -path "./.git/*" -exec sed -i '' \
    's/import memory_classification_engine/import carrymem.mce/g' {} +

find . -name "*.py" -not -path "./.git/*" -exec sed -i '' \
    's/memory_classification_engine/carrymem/g' {} +
```

---

## 4. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 内部 import 遗漏 | 中 | 编译错误 | CI 全量测试 |
| 外部用户代码 break | 低 | 用户投诉 | 双包名 + 6个月过渡 |
| GitHub 重定向失效 | 极低 | 链接失效 | GitHub 官方支持 |
| 文档引用不一致 | 中 | 困惑 | 全文搜索替换 |

---

## 5. 执行检查清单

### Phase 1 (v0.5) — 现在执行

- [ ] README.md 标题更新为 CarryMem
- [ ] ROADMAP.md 已更新
- [ ] 共识文档已更新 (v4.0)
- [ ] 新文档使用 CarryMem 品牌

### Phase 2 (v0.6) — 代码迁移

- [ ] 本地目录重命名: `memory-classification-engine` → `carrymem`
- [ ] Python 模块重命名: `memory_classification_engine` → `carrymem`
- [ ] 内部 import 全量替换
- [ ] setup.py / pyproject.toml 更新
- [ ] CLI 命令更新: `mce` → `carrymem`
- [ ] 配置目录: `~/.mce` → `~/.carrymem`
- [ ] mce 别名包创建
- [ ] 全量测试通过 (881+)
- [ ] MCE-Bench 回归通过

### Phase 3 (v0.7) — GitHub 迁移

- [ ] GitHub 仓库重命名
- [ ] 验证重定向生效
- [ ] 更新所有外部引用

### Phase 4 (v1.0) — 清理

- [ ] mce 别名标记 deprecated
- [ ] 文档全面清理
