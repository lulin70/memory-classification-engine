# Installation Guide v2 逐行审核报告
**审核日期**: 2026-04-18  
**审核人**: QA (基于实际代码库验证)  
**文件**: `docs/user_guides/installation_guide_v2.md`  
**对照文件**: `setup.py`, 实际源码路径, 文件系统  

---

## 审核结果总览

| 严重级别 | 数量 | 发布影响 |
|---------|------|---------|
| 🔴 **Critical** (用户照做会失败) | 6 | **必须修复才能发布** |
| 🟡 **Major** (信息不准确) | 5 | 应该修复 |
| 🟢 **Minor** (笔误/排版) | 2 | 可后续修复 |

---

## 🔴 Critical Issues (必须修复)

### C-1: §4.1 MCP Server 路径错误 — 指向错误的 Server 实现

**文档原文 (L141-144)**:
```bash
cd mce-mcp
python3 server.py
```

**实际情况**:
- `mce-mcp/mce_mcp_server/server.py` 是 **HTTP Server (port 8080)**，只有 **6 个工具**
- 真正的 stdio MCP Server（Demo 测试中 6/6 通过的那个）在:
  ```
  src/memory_classification_engine/integration/layer2_mcp/server.py
  ```
  它有 **11 个工具**，使用 **stdio transport**

**用户照做的后果**: 启动的是 HTTP 版本，不是 Claude Code 需要的 stdio 版本。Claude Code 配置会失败。

**修正方案**:
```bash
# 方案 A: 使用模块启动 (推荐)
python3 -m memory_classification_engine.integration.layer2_mcp

# 方案 B: 直接运行
python3 src/memory_classification_engine/integration/layer2_mcp/server.py
```

---

### C-2: §4.1 MCP 启动输出描述与实际不符

**文档原文 (L147-152)**:
```
Expected output:
MCP Server starting...
Version: 1.0.0 (Production)
Protocol: 2024-11-05
Listening on stdio transport...
```

**实际情况** (`layer2_mcp/server.py` L38-39):
```python
VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"
```
但实际启动输出不包含 "Listening on stdio transport..." 这行文字。stdio server 直接开始读取 stdin。

**修正**: 更新为实际输出或删除预期输出块。

---

### C-3: §2.3 `[dev]` extra 不存在

**文档原文 (L93)**:
```bash
pip install -e ".[dev]"
```

**实际情况** (`setup.py` L14-19):
```python
extras_require={
    "api": ["Flask", "aiohttp", "socketio"],
    "llm": ["requests"],
    "testing": ["pytest", "pytest-benchmark", "pytest-asyncio"],
    "profiling": ["memory-profiler"],
}
```
**没有 `[dev]` extra！**

**用户照做的后果**: `pip install -e ".[dev]"` 报错: `Invalid extra: dev`

**修正**: 改为 `pip install -e ".[testing]"` 或列出所有需要的 extras。

---

### C-4: §8.2 `examples/quickstart.py` 不存在

**文档原文 (L553)**:
```
2. **Try the quick example**: See `examples/quickstart.py`
```

**实际情况** (`examples/` 目录):
```
basic_usage.py              ✅ 存在
complete_example.py          ✅ 存在
community_feedback_example.py ✅ 存在
recommendation_example.py    ✅ 存在
quickstart.py               ❌ 不存在!
```

**修正**: 改为 `examples/basic_usage.py` 或 `examples/complete_example.py`

---

### C-5: §7.3 `process_batch()` 方法不存在

**文档原文 (L493)**:
```python
engine.process_batch(messages)  # More efficient than individual calls
```

**实际情况**: 在 `engine.py` 中搜索 `def process_batch` → **无匹配**

**修正**: 删除此示例，或改为循环调用 `process_message()`

---

### C-6: §7.3 `archive_low_weight_memories()` 方法不存在

**文档原文 (L518-519)**:
```python
engine.archive_low_weight_memories(weight_calculator=default_calc)
```

**实际情况**: 在 `engine.py` 中搜索 `def archive_low_weight` → **无匹配**

**修正**: 删除此示例

---

## 🟡 Major Issues (应该修复)

### M-1: 文档版本号混乱

**文档头部 (L5)**:
```
**Version**: 2.0 | **Last Updated**: 2026-04-18 | **Status**: Production Ready (v1.0.0)
```

**文档尾部 (L567-569)**:
```
**Document Version**: 2.0
**Tested Against**: MCE v1.0.0 Production (874 tests passing, 0 failures)
```

**问题**: 
- 文档自称 "Version: 2.0" — 这是什么版本？文档版本？
- "Tested Against: MCE v1.0.0" — 但引擎实际是 **v0.2.0**
- 用户会困惑：到底装的是哪个版本？

**修正**: 统一为 `v0.2.0`

---

### M-2: Python 版本要求不一致

**文档 (L28)**:
```
| Python | 3.8+ | 3.9+, 3.11+, 3.12+ |
```

**setup.py (L30)**:
```python
python_requires=">=3.9",
```

**问题**: 文档说 3.8+，但 setup.py 要求 >=3.9。3.8 用户安装会失败。

**修正**: 文档改为 `3.9+` 或改为 `3.9+ (推荐 3.10+)`

---

### M-3: §4.3 OpenClaw 配置文件不存在

**文档原文 (L190)**:
```
Configuration file is provided at `mce-mcp/config/openclaw_config.json`.
```

**实际情况**: 
```
mce-mcp/config/
├── advanced_rules.json     ✅
├── access_control.json     ✅
└── openclaw_config.json   ❌ 不存在!
```

**修正**: 删除此句或标注 "(coming soon)"

---

### M-4: mce-mcp/setup.py 版本和依赖未同步

**`mce-mcp/setup.py` 当前内容**:
```python
version="1.0.0",                    # ← 应该更新?
install_requires=[
    "memory-classification-engine>=0.4.0",  # ← 应该是 >=0.2.0!
],
```

**问题**: 
- MCP 包版本还是 1.0.0（如果跟随主包应该是 0.2.0 或独立编号）
- 依赖要求 `>=0.4.0` 但主包当前是 `0.2.0`，安装时会报找不到合适版本

**修正**: 改为 `>=0.2.0`

---

### M-5: §5.1 `ollam` 拼写错误

**文档原文 (L202)**:
```
| `MCE_LLM_PROVIDER` | `zhipuai` | LLM provider: `zhipuai`, `openai`, `ollam` |
```

**应为**: `ollama`（少了个 'a'）

---

## 🟢 Minor Issues

### m-1: §3.2 项目结构中 `mce-mcp/` 定位不清

文档将 `mce-mcp/` 作为项目子目录展示，但它实际上是一个**独立的可分发包**（有自己的 setup.py）。可能让用户困惑是否需要单独安装。

### m-2: §4.1 Claude Code 工具数量说 "11 available tools"

**文档 (L173)**:
```
You should see `mce` listed with 11 available tools.
```

**验证**: `layer2_mcp/tools.py` 确实定义了 11 个工具 ✅ 这个是对的！

---

## 验证通过的项 ✅

以下内容经验证是正确的：

| 章节 | 内容 | 验证方法 |
|------|------|---------|
| §1 核心依赖 | PyYAML, typing-extensions | ✅ setup.py install_requires 匹配 |
| §1 可选依赖 | scikit-learn, faiss, networkx, zhipuai, openai | ✅ 都是可选 import，有 fallback |
| §2.1 pip install 命令 | `pip install memory-classification-engine` | ✅ 与 setup.py name 匹配 |
| §2.1 验证命令 | from/import + init | ✅ Demo 测试 A1-A2 通过 |
| §6 Process message 返回值 | `matches` list | ✅ 已在 REL-001 修正 |
| §6 Stats 返回值 keys | working_memory_size, storage, memory, cache | ✅ Demo A5 验证通过 |
| §6 Feedback 签名 | `(mem_id, {"type":..., "correct_type":...})` | ✅ REL-002 已修正 |
| §7.1 scikit-learn troubleshooting | ImportError 处理 | ✅ 正确 |
| §7.4 start_time bugfix 说明 | D-1.4 修复记录 | ✅ 正确 |
| §7.4 RLock thread safety | D-1.1 修复记录 | ✅ 正确 |

---

## 修复优先级建议

### 必须在发布前修复 (P0):

| ID | 修复内容 | 改动量 |
|----|---------|--------|
| C-1 | §4.1 MCP 路径改为 layer2_mcp | 改 3 行 |
| C-3 | §2.3 `"[dev]"` → `"[testing]"` | 改 1 字 |
| C-4 | §8.2 `quickstart.py` → `basic_usage.py` | 改 1 字 |
| C-5 | §7.3 删除 `process_batch` 示例 | 删 2 行 |
| C-6 | §7.3 删除 `archive_low_weight_memories` 示例 | 删 2 行 |

### 强烈建议发布前修复 (P1):

| ID | 修复内容 | 改动量 |
|----|---------|--------|
| M-1 | 版本号统一为 v0.2.0 | 改 3 处 |
| M-2 | Python 3.8+ → 3.9+ | 改 1 处 |
| M-4 | mce-mcp/setup.py 依赖 ≥0.2.0 | 改 1 行 |
| M-5 | ollam → ollama | 改 1 字 |

### 可接受延后 (P2):

| ID | 修复内容 | 备注 |
|----|---------|------|
| C-2 | MCP 启动输出描述 | 不影响功能 |
| M-3 | openclaw_config.json 引用 | 标注 coming soon 即可 |

---

**审核结论**: 安装指南存在 **6 个 Critical 问题**，其中 3 个会导致用户照着做直接失败（C-1/C-3/C-4）。建议全部 P0 修复后再创建 GitHub Release。
