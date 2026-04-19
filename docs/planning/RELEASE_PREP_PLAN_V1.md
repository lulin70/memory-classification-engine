# MCE 发布前推进计划 — D 先行（内容营销 + 质量加固）

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档名称 | MCE 发布前推进计划（D 先行版） |
| 版本 | v1.0.0 |
| 日期 | 2026-04-17 |
| 编制团队 | 产品经理 + 架构师 + 测试专家 + 独立开发者 |
| 审核状态 | ⏳ 待全员审核 |
| 前置文档 | ROADMAP.md (v2.0.0), OPTIMIZATION_ROADMAP_V1.md |

## 更新履历

| 版本 | 日期 | 更新人 | 更新内容 | 审核状态 |
|------|------|--------|----------|----------|
| v1.0.0 | 2026-04-17 | 多角色团队 | 初始版本，整合三方顾虑为可执行计划 | ⏳ 待审核 |

---

## 一、决策背景

### 1.1 决策议题

**是否先做 D（内容营销）再做 A（PyPI 发布）？**

### 1.2 决策结论

**✅ 全员共识：D 先行 → 技术加固 → 内容创作 → 全员审核 → A 发布**

### 1.3 决策理由矩阵

| 角色 | 核心顾虑 | D 先行如何解决 |
|------|---------|---------------|
| 👨‍💼 **产品经理** | 产品有隐藏 bug 会带来负面首因效应 | 博客写作过程 = 深度自测；写博文必须通读全部代码和文档 |
| 🏗️ **架构师** | A-1~A4 四项技术债未还；无完整回归测试 | D 前专门设 D-1 阶段（~2h）完成技术加固+回归 |
| 🧪 **测试专家** | 真实使用流程未验证；安装流程可能有坑 | 录 demo = 覆盖真实流程；写安装指南 = 发现安装问题 |

---

## 二、推进计划总览

```
┌─────────────────────────────────────────────────────────────┐
│                    D 先行发布路线图                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐                                          │
│  │ Phase D-1     │  技术加固（架构师主导，~2h）              │
│  │  ~2 hours    │                                          │
│  │              │  ├─ D-1.1 修复竞态条件                    │
│  │              │  ├─ D-1.2 补完残留注释                    │
│  │              │  ├─ D-1.3 异常处理加固                    │
│  │              │  └─ D-1.4 全量回归测试                    │
│  └──────┬───────┘                                          │
│         │ 通过 ✓                                            │
│         ▼                                                  │
│  ┌──────────────┐                                          │
│  │ Phase D-2     │  内容创作与深度 QA（全员参与，3-5d）      │
│  │  3-5 days   │                                          │
│  │              │  ├─ D-2.1 PM: 深度技术博客                │
│  │              │  ├─ D-2.2 PM: User Story 校准            │
│  │              │  ├─ D-2.3 QA: Demo 流程录制 + 问题报告    │
│  │              │  └─ D-2.4 QA: 安装指南 v2               │
│  └──────┬───────┘                                          │
│         │ 完成                                              │
│         ▼                                                  │
│  ┌──────────────┐                                          │
│  │ Phase D-3     │  全员审核共识（~0.5d）                   │
│  │  ~4 hours   │                                          │
│  │              │  └─ D-2.5 四方会审 → 签字/驳回           │
│  └──────┬───────┘                                          │
│         │ 共识 ✓                                           │
│         ▼                                                  │
│  ┌──────────────┐                                          │
│  │ Phase A       │  PyPI 正式发布（~1d）                   │
│  │  ~1 day     │                                          │
│  │              │  ├─ A-1 双包发布                         │
│  │              │  ├─ A-2 MCP 社区提交                     │
│  │              │  └─ A-3 Discord 分享                      │
│  └──────────────┘                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 依赖关系

```
D-1.1 ─┐
D-1.2 ─┼→ D-1.4 (全量回归) ─→ D-2.x (并行) ─→ D-2.5 (全员终审) ─→ Phase A
D-1.3 ─┘                              │
                                         │
  D-2并行任务:                            │
  ┌─────────────────────────────┐        │
  │ PM: D-2.1 博客              │        │
  │   ↓                          │        │
  │ ⚠️ D-2.1R 博客专项审核门禁 ◄──┼────────┘ (ARCH+QA 签字后才放行)
  │   ↓ (通过后)                 │
  │ PM: D-2.2 User Story 校准    │
  │                             │
  │ QA: D-2.3 Demo 录制+报告     │
  │ QA: D-2.4 安装指南 v2       │
  └─────────────────────────────┘
```

---

## 三、Phase D-1：技术加固（架构师主导）

> **目标**：将产品从 Beta+ 提升到 RC 级别，消除已知技术风险

### D-1.1 修复 `_index_dirty` 竞态条件

**来源**：架构师顾虑 A-1

**问题描述**：
[storage_coordinator.py](../src/memory_classification_engine/coordinators/storage_coordinator.py) 中 `get_memory()` 方法的 `_index_dirty` 标志和 `_id_index` 字典在多线程场景下存在竞态条件。MCP Server 多并发请求时可能导致：
- 读取到过期索引数据
- 并发 rebuild 导致重复扫描

**修复方案**：

```python
# Before (current - unsafe):
def get_memory(self, memory_id):
    if not self._index_dirty and memory_id in self._id_index:
        storage, _ = self._id_index[memory_id]
        return storage.get_memory_by_id(memory_id)
    
# After (proposed - thread-safe):
import threading

class StorageCoordinator:
    def __init__(self, config):
        ...
        self._index_lock = threading.RLock()
        self._id_index: Dict[str, tuple] = {}
        self._index_dirty = True
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        with self._index_lock:
            if not self._index_dirty and memory_id in self._id_index:
                storage, _ = self._id_index[memory_id]
                try:
                    return storage.get_memory_by_id(memory_id)
                except AttributeError:
                    self._index_dirty = True
        
        if self._index_dirty:
            self._rebuild_index()
        
        with self._index_lock:
            if memory_id in self._id_index:
                storage, _ = self._id_index[memory_id]
                try:
                    return storage.get_memory_by_id(memory_id)
                except AttributeError:
                    pass
        
        # Fallback: linear scan (only when index misses)
        for storage in [self.tier2_storage, self.tier3_storage, self.tier4_storage]:
            try:
                memories = storage.retrieve_memories()
                for memory in memories:
                    if memory.get('id') == memory_id:
                        with self._index_lock:
                            self._id_index[memory_id] = (storage, memory.get('tier', 3))
                        return memory
            except Exception as e:
                logger.warning(f"Error searching {storage.__class__.__name__}: {e}")
        return None
    
    def store_memory(self, memory: Dict) -> bool:
        result = self._store_to_tier(memory)
        if result:
            with self._index_lock:
                self._index_dirty = True
        return result
    
    def delete_memory(self, memory_id: str) -> bool:
        result = self._delete_from_tier(memory_id)
        if result:
            with self._index_lock:
                self._id_index.pop(memory_id, None)
        return result
    
    def update_memory(self, memory_id: str, updates: Dict) -> bool:
        result = self._update_memory_internal(memory_id, updates)
        if result:
            with self._index_lock:
                self._index_dirty = True
        return result
```

**验收标准**：
- [ ] `get_memory()` 在单线程下行为不变（696 测试不回归）
- [ ] 新增并发测试：10 线程同时 get/store/delete 无异常
- [ ] `_rebuild_index()` 加锁保护，不会并发执行多次

**交付物**：修改后的 [storage_coordinator.py](../src/memory_classification_engine/coordinators/storage_coordinator.py)

**工作量**：~30min

---

### D-1.2 补完 semantic_classifier.py 残留占位符注释

**来源**：架构师顾虑 A-2

**问题描述**：
[semantic_classifier.py:50-51](../src/memory_classification_engine/layers/semantic_classifier.py#L50) 存在两行残留的 "Comment in Chinese removed" 占位符注释，在之前批量修复时被遗漏。

**当前代码**（第 50-51 行）：
```python
        # Comment in Chinese removed客户端
        # Comment in Chinese removed等
```

**修复方案**：替换为有意义的英文注释：

```python
        # Attempt to initialize LLM client from available providers
        # Supports ZhipuAI (GLM) as primary LLM backend
```

**验收标准**：
- [ ] Grep 全项目确认零 "Comment in Chinese removed" 残留
- [ ] 替换后的注释准确描述代码意图

**交付物**：修改后的 [semantic_classifier.py](../src/memory_classification_engine/layers/semantic_classifier.py)

**工作量**：~15min

---

### D-1.3 distillation.py 异常处理加固

**来源**：架构师顾虑 A-4

**问题描述**：
[distillation.py:259](../src/memory_classification_engine/layers/distillation.py#L259) 和 [distillation.py:293](../src/memory_classification_engine/layers/distillation.py#L293) 的 except 块静默吞掉异常（`pass`），导致余弦相似度计算失败时返回默认值而非记录问题。

**当前代码**：
```python
                try:
                    emb = self.semantic_utility.embedding_model.encode([message, best['content']])
                    from sklearn.metrics.pairwise import cosine_similarity
                    similarity = float(cosine_similarity([emb[0]], [emb[1]])[0][0])
                except Exception:
                    pass  # ← 静默吞异常
```

**修复方案**：
```python
                try:
                    emb = self.semantic_utility.embedding_model.encode([message, best['content']])
                    from sklearn.metrics.pairwise import cosine_similarity
                    similarity = float(cosine_similarity([emb[0]], [emb[1]])[0][0])
                except Exception as e:
                    logger.warning(f"Confidence estimation failed, using default: {e}")
                    similarity = 0.85  # Default to medium confidence on failure
```

同样修复第 293 行的 `finally: pass`。

**验收标准**：
- [ ] 异常路径有日志输出（logger.warning）
- [ ] 默认值合理且有注释说明
- [ ] 不影响现有测试通过率

**交付物**：修改后的 [distillation.py](../src/memory_classification_engine/layers/distillation.py)

**工作量**：~5min

---

### D-1.4 全量测试回归确认

**来源**：架构师顾虑 + 测试专家共同要求

**目标**：确认 D-1.1 ~ D-1.3 的修改不引入任何回归

**执行步骤**：

```bash
cd /Users/lin/trae_projects/memory-classification-engine
pytest tests/ -v --tb=short --cov=src --cov-report=term-missing
```

**验收标准**：
- [ ] 全部 696 个测试通过（0 failure, 0 error）
- [ ] 新增至少 2 个并发测试用例（覆盖 D-1.1 的线程安全）
- [ ] 代码覆盖率不低于修改前水平

**交付物**：
- 测试运行报告（stdout 输出）
- 如有失败：bug report + fix

**工作量**：~10min（不含修复时间）

---

## 四、Phase D-2：内容创作与深度 QA（全员参与）

> **目标**：通过内容创作过程完成深度自测，产出高质量对外材料

### D-2.1 PM：深度技术博客

**来源**：产品经理核心顾虑 — "博客写作过程 = 深度自测"

**文章标题**：Why Your Agent Needs Professional Memory Classification

**文章定位**：面向 AI Agent 开发者的技术深度文，不是产品介绍软文

**要求大纲**（PM 必须覆盖以下章节）：

```
1. The Memory Problem Every Agent Has (5 min read)
   - Option A: Save nothing → forgets everything
   - Option B: Save everything → noise drowns signal
   - Real user quotes showing the pain

2. Why "Classification Before Storage" Matters (core insight)
   - Show the before/after of one message classification
   - Cost comparison table (traditional vs MCE)
   - The three-layer pipeline explained visually

3. Architecture Deep Dive (requires reading ALL source code)
   - Layer 1: Rule matching (60%+ zero cost) — show real rules
   - Layer 2: Pattern analysis (30%+ zero LLM) — show pattern examples
   - Layer 3: Semantic inference (<10% fallback) — when and why
   - Four-tier storage with lifecycle diagram

4. v2.0 Features (new!)
   - Adaptive retrieval modes (compact/balanced/comprehensive)
   - Feedback loop automation
   - Model distillation interface

5. Performance Data (from our benchmarks)
   - process_message: -74%
   - Cache hit rate: 97.83%
   - Test count: 696

6. How to Use It (real code, copy-paste runnable)
   - 30-second quickstart
   - MCP Server setup for Claude Code
   - Retrieval mode selection guide

7. What's Next (teaser for LangChain adapter, etc.)
```

**写作过程中的强制检查点（QA 要求）**：

| 检查点 | 触发条件 | 动作 |
|--------|---------|------|
| CP-P1 | 写 §2 "Classification Before Storage" 时 | 必须实际跑一遍 `process_message()` 验证描述准确 |
| CP-P2 | 写 §3 "Architecture" 时 | 必须逐个打开源文件确认模块名/方法名/参数正确 |
| CP-P3 | 写 §5 "Performance Data" 时 | 必须重新跑一次 benchmark 确认数字没变 |
| CP-P4 | 写 §6 "How to Use" 时 | 必须按文档步骤从头安装一遍，确认无坑 |

**如果检查点发现问题**：
- 记录到 [D-2.2 User Story 校准文档](#d-22-pm-user-story-校准文档)
- 如果是 bug → 立即通知开发者修复
- 如果是文档错误 → 立即修正文档

**交付物**：
- 博客 Markdown 文件：`docs/blog/why-your-agent-needs-professional-memory-classification.md`
- 英文版（主）+ 可选中文版

### D-2.1R：博客专项审核（独立门禁，必须在 D-2.2 前完成）

> **来源**：产品经理明确要求 — "文章给测试专家和架构师审核，要求达成共识"

**触发条件**：D-2.1 博客初稿完成

**审核流程**：

```
PM 提交博客初稿
    ↓
┌─────────────────────────────────────┐
│  架构师技术审核（~30min）            │
│  ├─ §3 Architecture: 模块名/方法名/参数是否与源码一致？     │
│  ├─ §5 Performance Data: 基准数字是否与 final_results.json 吻合？│
│  ├─ §6 Code Examples: 代码能否直接 copy-paste 跑通？         │
│  └─ 结论: ✅ Approve / ⚠️ With fixes (标注行号+修改要求) / ❌ Block │
└──────────────┬──────────────────────┘
               │ ARCH 通过
               ▼
┌─────────────────────────────────────┐
│  测试专家可复现性审核（~30min）       │
│  ├─ 按 §6 步骤从头安装一遍，确认无坑                         │
│  ├─ 跑一遍完整流程（process → retrieve → feedback → stats）    │
│  └─ 结论: ✅ Approve / ⚠️ With fixes / ❌ Block              │
└──────────────┬──────────────────────┘
               │ QA 通过
               ▼
        博客审核通过 ✓ → 进入 D-2.2 User Story 校准
```

**审核清单（Checklist）**：

| # | 检查项 | 审核人 | 结果 |
|---|--------|--------|------|
| BR-1 | 所有引用的类名/方法名与源码一致 | ARCH | ⬜ |
| BR-2 | 所有性能数据可由 benchmark 复现 | ARCH | ⬜ |
| BR-3 | 所有代码示例可直接运行（copy-paste） | ARCH | ⬜ |
| BR-4 | 无过度承诺（不夸大、不隐瞒局限） | ARCH | ⬜ |
| BR-5 | 安装步骤可在干净环境复现 | QA | ⬜ |
| BR-6 | 核心功能流程（process→retrieve）端到端跑通 | QA | ⬜ |
| BR-7 | 三种 retrieval_mode 示例均验证通过 | QA | ⬜ |

**如果出现 Block**：
- ARCH Block：技术错误 → PM 修正后重新提交 ARCH 审核
- QA Block：不可复现 → PM 修正 + 更新文档后重新提交 QA 审核
- 双方都 Block：升级为全员讨论

**交付物**：
- `docs/blog/BLOG_REVIEW_v1.md`（审核记录，含每条意见和处置结果）
- 审核后的最终版博客（标记 "Reviewed by ARCH ✅, Reviewed by QA ✅"）

**签字格式**：

```markdown
## Blog Review Sign-off

| Role | Name | Date | Verdict | Key Comments |
|------|------|------|---------|-------------|
| 🏗️ Architect | _____________ | ____ | ✅ / ⚠️ N fixes / ❌ Block | ______ |
| 🧪 Test Expert | _____________ | ____ | ✅ / ⚠️ N fixes / ❌ Block | ______ |
| 👨‍💼 PM (Author) | _____________ | ____ | Changes accepted: Y/N | ______ |
```

**工作量**：~1h（审核双方各 ~30min）

**工作量**：D-2.1 本体 ~1-2d + D-2.1R 审核 ~1h

---

### D-2.2 PM：User Story 校准文档

**来源**：产品经理顾虑 — "写 user story 时自然校准对用户场景理解偏差"

**目标**：基于 D-2.1 博客写作过程中发现的问题，校准我们对用户场景的理解

**文档模板**：

```markdown
# User Story 校准记录

## 日期：2026-04-xx
## 触发事件：D-2.1 博客写作过程中的发现

### 发现 1：[具体发现]
- **来源**：博客 §X 写作 / demo 录制 / 安装测试
- **原假设**：我们原来认为...
- **实际情况**：实际上...
- **影响评估**：高/中/低
- **行动项**：
  - [ ] 需要修的 bug
  - [ ] 需要改的文档
  - [ ] 需要调整的产品方向

### 发现 2：...

## User Story 更新

### US-001: [原有 user story]
- **变更前**：...
- **变更后**：...
- **变更原因**：发现 X

### US-002 (新增): [新发现的 user story]
- **As a** ... 
- **I want to** ...
- **So that** ...
- **Acceptance Criteria**: ...

## 结论
- 用户场景理解偏差数：X
- 需要修复的 bug 数：Y
- 需要更新的文档数：Z
- 产品方向是否需要调整：是/否
```

**验收标准**：
- [ ] 至少记录 3 个发现（可以是正面的"比预期好"或负面的"有问题"）
- [ ] 每个 discovery 都有明确的 action item
- [ ] User story 有具体的增删改

**交付物**：`docs/product-manager/USER_STORY_CALIBRATION_v1.md`

**审核人**：全员

**工作量**：~0.5d（与 D-2.1 同步进行）

---

### D-2.3 QA：Demo 真实使用流程录制 + 交互问题报告

**来源**：测试专家顾虑 — "录 demo 时覆盖真实使用流程，发现交互层面的问题"

**Demo 脚本（必须按顺序完整执行）**：

```
Scenario A: First-time User (New Installation)
  Step A1: pip install memory-classification-engine
  Step A2: python -c "from mce import *; e = MemoryClassificationEngine()"
  Step A3: Process 5 different message types (preference/correction/fact/decision/sentiment)
  Step A4: Retrieve memories with all 3 modes (compact/balanced/comprehensive)
  Step A5: Check memory stats
  Step A6: Process feedback on one memory

Scenario B: Claude Code User (MCP Integration)
  Step B1: Start MCP server: cd mce-mcp && python3 server.py
  Step B2: Configure Claude Code settings.json
  Step B3: Send 3 messages via Claude Code + classify_memory tool
  Step B4: Use retrieve_memories tool with different modes
  Step B5: Export/import memories via MCP tools
  Step B6: Stop MCP server cleanly

Scenario C: Power User (Advanced Features)
  Step C1: Load engine with custom config
  Step C2: Register agent and process with agent
  Step C3: Use feedback loop (process_feedback 3+ times on same type)
  Step C4: Try distillation router (if LLM enabled)
  Step C5: Run optimize_system()
  Step C6: Run compress_memories()

Scenario D: Edge Cases (Stress Test)
  Step D1: Empty string message
  Step D2: Very long message (>10000 chars)
  Step D3: Special characters (emoji, unicode, HTML)
  Step D4: Rapid sequential calls (100 messages in loop)
  Step D5: Concurrent MCP requests (if applicable)
```

**交互问题报告模板**：

```markdown
# Demo 交互问题报告

## 执行日期：2026-04-xx
## 执行者：测试专家
## Demo 脚本版本：v1.0

## 执行结果总览
| Scenario | Steps Total | Passed | Failed | Issues Found |
|----------|------------|--------|--------|-------------|
| A: First-time User | 6 | ? | ? | ? |
| B: Claude Code MCP | 6 | ? | ? | ? |
| C: Power User | 6 | ? | ? | ? |
| D: Edge Cases | 5 | ? | ? | ? |

## 详细 Issue 清单

### Issue-001: [标题]
- **Scenario**: A3
- **Severity**: Critical/Major/Minor/Info
- **Reproduction**: （精确步骤）
- **Expected**: ...
- **Actual**: ...
- **Screenshot/GIF**: （如有）
- **Root Cause Analysis**: （初步判断）
- **Recommendation**: ...

### Issue-002: ...

## 总结
- Critical issues: X (must fix before release)
- Major issues: Y (should fix before release)
- Minor issues: Z (can defer to next version)
- Info items: W (documentation improvements)

## Release Readiness Assessment
- ✅ Ready to release (0 Critical, 0 Major)
- ⚠️ Ready with caveats (0 Critical, N Major documented)
- ❌ Not ready (N Critical or N Major blocking)
```

**交付物**：
- `docs/testing/DEMO_INTERACTION_REPORT_v1.md`
- Demo GIF/截图（如有交互问题）

**审核人**：产品经理（用户体验）+ 架构师（技术根因）

**工作量**：~1-1.5d

---

### D-2.4 QA：安装指南 v2（含 troubleshooting）

**来源**：测试专家顾虑 — "写安装指南时自然发现安装流程有坑"

**目标**：重写安装指南，基于真实安装测试结果，增加 troubleshooting 章节

**强制前提**：必须在**干净环境**下执行（全新 Python venv）

**安装测试矩阵**：

| 环境 | Python 版本 | OS | 预期结果 |
|------|-----------|-----|---------|
| 最小安装 | 3.8 | macOS | 仅核心功能可用 |
| 完整安装 | 3.11 | macOS | 全功能可用 |
| 带 LLM | 3.11 | macOS | Layer 3 可用 |
| 最小安装 | 3.9 | Linux (Ubuntu) | 核心功能可用 |
| Docker 安装 | - | - | 容器内可用 |

**安装指南 v2 结构**：

```markdown
# MCE Installation Guide v2

## 1. Prerequisites (updated)
  - Python 3.8+ (tested on 3.8, 3.9, 3.10, 3.11, 3.12)
  - NEW: scikit-learn recommended (for vector encoding optimization)
  - Optional dependencies matrix

## 2. Quick Install (5 commands, verified)
  ## 2.1 Core only
  ## 2.2 With API server
  ## 2.3 With LLM support
  ## 2.4 Full installation (all features)

## 3. From Source (for developers)
  ## 3.1 Clone & setup
  ## 3.2 Development mode
  ## 3.3 Running tests

## 4. MCP Server Setup (updated for v1.0.0 Production)
  ## 4.1 Claude Code configuration
  ## 4.2 Cursor configuration
  ## 4.3 OpenClaw configuration
  ## 4.4 Verification steps

## 5. Configuration Guide
  ## 5.1 Environment variables
  ## 5.2 config.yaml reference
  ## 5.3 Neo4j setup (optional)
  ## 5.4 Obsidian integration (optional)

## 6. Troubleshooting (NEW - based on real issues found)
  ### 6.1 Installation Issues
    - Issue: "ImportError: No module named 'yaml'"
      Fix: pip install pyyaml
    - Issue: "FAISS not found warning"
      Fix: This is expected; FAISS is optional
    - Issue: "sklearn cosine_similarity import error"
      Fix: pip install scikit-learn
    - (add more based on actual testing...)

  ### 6.2 Runtime Issues
    - Issue: "Cache warmup fails silently"
      Fix: Check data directory permissions
    - Issue: "MCP server starts but tools not showing"
      Fix: Verify stdio transport config
    - (add more based on actual testing...)

  ### 6.3 Performance Issues
    - Issue: "First query is slow"
      Fix: Normal behavior; cache warms up after first call
    - (add more based on actual testing...)

## 7. Verification Checklist
  - [ ] Engine imports without error
  - [ ] Engine initializes without error
  - [ ] process_message() returns valid result
  - [ ] retrieve_memories() returns results
  - [ ] MCP server starts and responds
  - [ ] All 696 tests pass

## 8. Next Steps
  - Link to blog post
  - Link to API reference
  - Link to GitHub issues for bug reports
```

**验收标准**：
- [ ] 每个安装步骤都在干净环境下验证通过
- [ ] troubleshooting 章节包含至少 8 个真实遇到的问题及解决方案
- [ ] verification checklist 可由用户自行执行
- [ ] 中英双语（英文为主，中文可选）

**交付物**：
- `docs/user_guides/installation_guide_v2.md`（替换旧版）
- 安装测试日志（每个环境的命令输出）

**审核人**：产品经理（用户视角）+ 架构师（技术准确性）

**工作量**：~1d

---

## 五、Phase D-3：全员审核共识

### D-2.5 四方会审

**目标**：所有 D-2 产出物经过全员审核，达成共识后才能进入 Phase A

**审核清单**：

| # | 产出物 | 作者 | 审核人 | 审核重点 | 状态 |
|---|-------|------|--------|---------|------|
| R-1 | 技术博客 | PM | ARCH + QA | **D-2.1R 已初审通过，此处为终审确认**：技术准确性、可复现性、无过度承诺 | ⬜ |
| R-2 | User Story 校准 | PM | ARCH + QA + DEV | 发现是否有遗漏、action item 是否合理 | ⬜ |
| R-3 | Demo 交互报告 | QA | PM + ARCH | Issue 严重度评估、release readiness 判定 | ⬜ |
| R-4 | 安装指南 v2 | QA | PM + ARCH | 步骤可复现、troubleshooting 覆盖面 | ⬜ |
| R-5 | D-1 技术加固验证 | DEV | QA | 测试通过率、新测试覆盖 | ⬜ |
| **R-B** | **博客专项审核记录 (D-2.1R)** | **PM+ARCH+QA** | **全员** | **⬜（必须先于 R-1~R-5 完成）** | ⬜ |

**注意**：R-B（博客专项审核）是**前置门禁**，必须在 D-2.5 全员会审前完成并签字。D-2.5 的 R-1 仅做终审确认。

**审核流程**：

```
Step 1: 各作者提交产出物到 docs/release-prep/
Step 2: 审核人在产出物中直接批注（GitHub PR review style）
Step 3: 汇总会议（30min）逐条过审阅意见
Step 4: 分类：
        → Agree: 确认通过
        → Agree with changes: 标注修改要求，作者修改后自动通过
        → Blocker: 必须讨论解决的阻塞问题
Step 5: 如果 Blocker > 0 → 返回修改 → 重新审核
        如果 Blocker = 0 → 全员签字确认 → 进入 Phase A
```

**签字格式**：

```markdown
## Release Pre-Publication Review Sign-off

| Role | Name | Date | Verdict | Comments |
|------|------|------|---------|----------|
| 👨‍💼 Product Manager | _____________ | ____ | ✅ Approve / ⚠️ With changes / ❌ Block | ______ |
| 🏗️ Architect | _____________ | ____ | ✅ Approve / ⚠️ With changes / ❌ Block | ______ |
| 🧪 Test Expert | _____________ | ____ | ✅ Approve / ⚠️ With changes / ❌ Block | ______ |
| 💻 Developer | _____________ | ____ | ✅ Approve / ⚠️ With changes / ❌ Block | ______ |

**Consensus**: ✅ Achieved / ❌ Not achieved
**Blockers remaining**: __
**Target release date**: ____
```

**交付物**：`docs/release-prep/REVIEW_SIGNOFF_v1.md`

**工作量**：~4h（含汇总会议）

---

## 六、Phase A：PyPI 正式发布

> **前置条件**：D-3 全员审核通过，Blockers = 0

### A-1 双包发布

**包信息**：

| 包名 | 内容 | 版本 |
|------|------|------|
| `memory-classification-engine` | 核心 SDK + CLI | 1.0.0 |
| `mce-mcp-server` | MCP Server（含依赖 core） | 1.0.0 |

**发布检查清单**：
- [ ] setup.py / pyproject.toml 配置正确
- [ ] VERSION 变量 = "1.0.0"
- [ ] README.md 作为 PyPI long description
- [ ] LICENSE 文件存在
- [ ] MANIFEST.in 包含必要文件
- [ ] `python -m build` 成功
- [ ] `twine check dist/*` 无警告
- [ ] 测试 sdist 和 wheel 都能正常安装

### A-2 MCP 社区仓库提交

**目标仓库**：https://github.com/modelcontextprotocol/servers

**提交内容**：
- MCE MCP Server 的 README
- 配置示例（Claude Code / Cursor）
- 截图（如有）

### A-3 社区分享

**渠道**：
- Claude Code Discord (#showcase 频道）
- Reddit r/ClaudeAI
- Hacker News Show（如有新闻价值）

**素材来源**：D-2 的全部产出物

---

## 七、时间线

```
Week 1 Day 1-2:
  ████ D-1 技术加固（~4h 总）
  │  D-1.1 竞态条件修复 (30min)
  │  D-1.2 残留注释补完 (15min)
  │  D-1.3 异常处理加固 (5min)
  │  D-1.4 全量回归测试 (10min + buffer)
  │
  ├── D-2 开始（并行推进）────────────────────────────┐
  │                                                      │
  │  PM ══════════════════════════════╗                  │
  │   ├─ D-2.1 技术博客撰写 (~1.5d)      │                  │
  │   ├─ ⚠️ D-2.1R 博客专项审核 (~1h)   │ ← 独立门禁，ARCH+QA签字  │
  │   └─ D-2.2 User Story 校准 (~0.5d)  │                  │
  │                                    │                  │
  │  QA ══════════════════════════════╗                  │
  │   ├─ D-2.3 Demo 录制+报告 (~1.5d) │                  │
  │   └─ D-2.4 安装指南 v2 (~1d)      │                  │
  │                                    │                  │
  └────────────────────────────────────┘                  │
                                                       │
Week 1 Day 5-6:                                         │
  ████ D-3 全员审核共识 (~4h) ◄──────────────────────────┘
  
Week 2 Day 1-2:
  ████ Phase A: PyPI 发布 (~1d)
```

**关键里程碑**：

| 里程碑 | 目标日期 | 依赖 | 验收标准 |
|--------|---------|------|---------|
| M1: 技术加固完成 | D+0.5 day | 无 | 696 测试 + 新并发测试全过 |
| **M2: 博客完成 + 专项审核通过** | **D+2.5 day** | **M1** | **PM 初稿 ✅ + ARCH 审核 ✅ + QA 审核 ✅ + R-B 签字** |
| M3: Demo + 安装指南完成 | D+3 day | M1 | QA 自审通过，真实环境验证通过 |
| M4: 全员审核通过 | D+4.5 day | M2+M3 | Blockers=0，四方签字（R-B 已前置完成） |
| M5: PyPI 上线 | D+5.5 day | M4 | 双包可 pip install |

---

## 八、风险登记册

| ID | 风险 | 概率 | 影响 | 缓解措施 | 责任人 | 状态 |
|----|------|------|------|---------|--------|------|
| R-01 | D-1 修改引入新 regression | 低 | 高 | 每项修改立即跑 696 测试 | DEV | ⏳ 监控 |
| R-02 | 博客写作发现重大 bug | 中 | 高 | 发现后立即修复，延期发布 | PM | ⏳ 监控 |
| R-03 | Demo 录制发现阻塞性 issue | 低 | 高 | 阻塞 issue 优先于 D-1 修复 | QA | ⏳ 监控 |
| R-04 | 安装在某些环境失败 | 中 | 中 | troubleshooting 覆盖 + CI matrix | QA | ⏳ 监控 |
| R-05 | 全员审核出现分歧无法达成共识 | 低 | 高 | 设定仲裁规则：ARCH 对技术问题有一票否决权 | ALL | ⏳ 监控 |
| R-06 | 竞品在 D 期间发布类似功能 | 低 | 中 | 差异化足够深（三层管道+四层存储），不受影响 | PM | ⏳ 接受 |
| R-07 | D-2 时间超估，延期发布 | 中 | 中 | 设 hard deadline：D+5 天必须出结果，否则砍 scope | PM | ⏳ 监控 |

---

## 九、成功标准

### 发布前必须满足（Hard Gates）

- [ ] **HG-1**: D-1.4 全量测试通过（696 + 新增 ≥ 2 个并发测试）
- [ ] **HG-2**: D-2.3 Demo 报告中 0 个 Critical issue
- [ ] **HG-3**: D-2.5 全员审核 Blockers = 0
- [ ] **HG-4**: D-2.4 安装指南在 ≥ 3 个环境验证通过

### 发布后追踪指标（Soft Goals）

| 指标 | Week 1 目标 | Month 1 目标 |
|------|-----------|-------------|
| PyPI 下载量 | > 50 | > 500 |
| GitHub Stars | > 10 | > 100 |
| Discord/Reddit 讨论 | ≥ 3 threads | ≥ 20 threads |
| Bug reports | < 5 | < 20 (且无 Critical) |
| 用户好评率 | N/A | > 80% positive |

---

**文档版本**: v1.0.0
**编制日期**: 2026-04-17
**审核状态**: ⏳ 待全员审核

---

## 附录：各角色顾虑 → 任务映射表

| 顾虑来源 | 具体顾虑 | 映射到任务 | 验收方式 |
|---------|---------|-----------|---------|
| 🏗️ 架构师 | A-1: `_index_dirty` 竞态条件 | **D-1.1** | 并发测试通过 |
| 🏗️ 架构师 | A-2: 残留占位符注释 | **D-1.2** | Grep 零残留 |
| 🏗️ 架构师 | A-3: SmartCache 线程安全 | **D-1.1** (同锁机制覆盖) | 并发测试通过 |
| 🏗️ 架构师 | A-4: distillation 静默异常 | **D-1.3** | 日志可观测 |
| 🏗️ 架构师 | 完整回归测试 | **D-1.4** | 696 测试全过 |
| 👨‍💼 产品经理 | 博客写作 = 深度自测 | **D-2.1** | 博客经 ARCH+QA 审核 |
| 👨‍💼 产品经理 | 通读文档发现遗漏/错误 | **D-2.1** (CP-P1~P4) | 检查点记录 |
| 👨‍💼 产品经理 | User Story 校准 | **D-2.2** | 校准文档经全员审 |
| 🧪 测试专家 | Demo 覆盖真实流程 | **D-2.3** | 4 场景 23 步全覆盖 |
| 🧪 测试专家 | 发现交互层面问题 | **D-2.3** | Issue 报告 + 严重度评级 |
| 🧪 测试专家 | 安装流程有坑 | **D-2.4** | 干净环境 5 种配置验证 |
| 🧪 测试专家 | 预判用户问题 | **D-2.4** | troubleshooting ≥ 8 条 |
