# Memory Classification Engine - Roadmap (路线图)

## 更新历史

| 版本 | 日期 | 更新者 | 更新内容 | 审核状态 |
|------|------|--------|---------|---------|
| v0.2.1 | 2026-04-19 | 工程团队 | **纯上游定位**: README 以"分类优先"叙事重写，MCP 工具标记废弃（8 个存储→v0.3 移除），STORAGE_STRATEGY.md 新建，共识 v3（路线 B 决策） | 已审核 |
| v0.2.0 | 2026-04-18 | 工程团队 | Phase 1 优化完成（process_message -74%），Phase 2 功能交付，MCP Server 生产就绪，**874 个测试**，Demo 26/30 (87%) | 已审核 |

---

## 愿景

**MCE 是 AI Agent 的标准记忆分类中间件。**

就像 **ChromaDB** 成为向量存储的代名词一样，MCE 致力于成为**记忆分类**的代名词 —— 决定什么可以进入任何记忆系统的"安检机"。

**产品定位**: *"你的 Agent 用 Supermemory/Mem0/Obsidian 来**存储**记忆。MCE 告诉它该**存储什么**。"*

**核心叙事**: 先分类，后存储。你来决定。

---

## 战略决策：纯上游路线 (2026-04-19)

**决策文档**: [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md)

### 发生了什么变化

| 之前 (v0.2.0) | 之后 (v0.3.0+) |
|---------------|---------------|
| MCP: 11 个工具（分类 + 全套 CRUD） | MCP: 4 个工具（仅分类） |
| "记忆分类引擎" | "记忆分类**中间件**" |
| 与 Supermemory / Mem0 竞争 | **互补**它们（下游客户） |
| 内置 SQLite 存储必需 | 存储通过 **StorageAdapter ABC** 委托 |
| 叙事: "不是什么都记" | 叙事: "**先分类再存储**" |

### 为什么做这个决策

1. **Supermemory 有 YC + Benchmark #1 + Cloudflare 基础设施。** 无法在存储上竞争。
2. **Mem0 有 18k Stars + 向量+图混合存储。** 它们的存储久经考验。
3. **但它们都没有在存储前做分类。** 这就是空白 —— 而 MCE 占领了这个位置。
4. **60%+ 的消息不需要 LLM 处理。** 这是独立于存储的价值。

---

## 已完成的里程碑

### v0.2.0 发布 ✅ (2026-04-18)

**状态**: 已发布，已打标签，已推送到 GitHub

| 组件 | 详情 |
|------|------|
| 核心引擎 | 三层管道（规则 → 模式 → 语义），7 种类型，4 个层级 |
| 性能 | `process_message` P99: -74% (5669→1452ms)，缓存命中率: 97.83% |
| 测试套件 | **874 个测试通过，0 失败** |
| Demo | 26/30 场景通过 (87%) |
| MCP Server | stdio 传输，11 个工具（3 个核心 + 8 个废弃） |
| 文档 | README + 安装指南 + API 参考 + 共识文档 |

### Phase 0: 纯上游定位 ✅ (2026-04-19)

**状态**: 已提交 (`a8dc7b3e`)，已推送

| 任务 | 文件 | 变更 |
|------|------|------|
| 工具废弃标记 | [tools.py](../src/memory_classification_engine/integration/layer2_mcp/tools.py) | 8 个存储工具标记 `[Deprecated v0.3]` |
| 版本修复 | [server.py](../src/memory_classification_engine/integration/layer2_mcp/server.py) | serverInfo 0.1.0 → 0.2.0 |
| HTTP 服务端废弃 | [mce-mcp/server.py](../mce-mcp/mce_mcp_server/server.py) | 添加 DEPRECATED 块注释 |
| README 重写 | [README.md](../README.md) | "Classification First" 叙事、FAQ、架构图 |
| 存储策略指南 | [STORAGE_STRATEGY.md](../docs/user_guides/STORAGE_STRATEGY.md) | **新建** — Supermemory/Mem0/Obsidian 集成指南 |
| 安装指南更新 | [installation_guide_v2.md](../docs/user_guides/installation_guide_v2.md) | MCP 章节对齐纯上游模式 |
| 共识文档 | [MCP_POSITIONING_CONSENSUS_v3.md](../docs/consensus/) | 完整战略决策文档（路线 B） |

---

## 当前版本: v0.2.0 (稳定)

### 包含内容

```
MCE v0.2.0
├── 核心分类引擎
│   ├── 第一层: 规则匹配 (60%+ 覆盖率, 零成本)
│   ├── 第二层: 模式分析 (30%+, 零 LLM)
│   ├── 第三层: 语义推理 (<10%, LLM 兜底)
│   ├── 7 种记忆类型 (user_preference / correction / fact / decision / relationship / pattern / sentiment)
│   ├── 4 个建议层级 (sensory / procedural / episodic / semantic)
│   ├── 反馈循环 (从纠正中自动学习)
│   └── 蒸馏路由器 (成本感知路由)
│
├── MCP Server (stdio, 生产就绪)
│   ├── classify_memory     ← 核心 (v0.3 保留)
│   ├── batch_classify      ← 核心 (v0.3 保留)
│   ├── mce_status          ← 核心 (v0.3 保留)
│   ├── store_memory        ← ⚠️ v0.3 废弃
│   ├── retrieve_memories   ← ⚠️ v0.3 废弃
│   ├── get_memory_stats    ← ⚠️ v0.3 废弃
│   ├── find_similar        ← ⚠️ v0.3 废弃
│   ├── export_memories     ← ⚠️ v0.3 废弃
│   ├── import_memories     ← ⚠️ v0.3 废弃
│   ├── mce_recall          ← ⚠️ v0.3 废弃
│   └── mce_forget          ← ⚠️ v0.3 废弃
│
└── 内置存储 (SQLite)
    └── v0.3 将封装为 BuiltInStorageAdapter @deprecated
```

---

## 下一步: v0.3.0 — 纯上游迁移

**目标**: 约 6 人日 | **Breaking Change**: 是（移除 8 个 MCP 工具）

### V3-MCP-01: tools.py 重写 (11 → 4 个工具)

移除 8 个废弃存储工具。仅保留：

| 工具 | 用途 |
|------|------|
| `classify_message` | 分类单条消息 → MemoryEntry JSON |
| `get_classification_schema` | 返回 7 类型 + 4 层级定义供下游映射 |
| `batch_classify` | 批量分类 → MemoryEntry[] |
| `mce_status` | 引擎状态（版本、能力、运行时间） |

### V3-MCP-02: handlers.py 重写 (-422 行)

删除 8 个存储处理器方法。修改 `handle_classify_memory` 输出 MemoryEntry Schema v1.0 格式。新增 `handle_get_classification_schema`。

### V3-MCP-03: engine.py — 新增 `to_memory_entry()` 方法

将 `process_message()` 结果转换为标准化 MemoryEntry JSON：

```json
{
  "schema_version": "1.0.0",
  "should_remember": true,
  "entries": [{
    "id": "mce_20260419_001",
    "type": "user_preference",
    "confidence": 0.95,
    "tier": 2,
    "source_layer": "rule",
    "reasoning": "...",
    "suggested_action": "store",
    "metadata": {...}
  }],
  "summary": {...},
  "engine_info": {"mode": "classification_only"}
}
```

### V3-MCP-04: StorageAdapter ABC（新建抽象层）

```python
class StorageAdapter(ABC):
    def store(self, entry: MemoryEntry) -> str: ...
    def store_batch(self, entries: List[MemoryEntry]) -> List[str]: ...
    def retrieve(self, query: str, limit: int) -> List[Dict]: ...
    def delete(self, storage_id: str) -> bool: ...
    def get_stats(self) -> Dict: ...
    @property
    def name(self) -> str: ...       # 如 "supermemory", "obsidian"
    @property
    def capabilities(self) -> Dict: ...  # {"vector_search": True, ...}
```

### V3-MCP-05: BuiltInStorageAdapter (@deprecated)

将当前 SQLite 逻辑封装为适配器。标记 `@deprecated`。仅用于过渡期兼容。

### V3-06~08: 分类准确率修复

- A3.2: correction 类型准确率提升
- A3.5: sentiment_marker 准确率提升
- 目标: 清晰消息分类准确率 >85%

### V3-09~14: 测试体系重构

| 任务 | 描述 |
|------|------|
| V3-09 | **MCE-Bench 180-case** — 分类准确率基准（P0，生存关键） |
| V3-10 | Fuzz 测试（1000 个随机输入，验证无崩溃） |
| V3-11 | MCP 集成测试（仅 4 个工具，无 DB 依赖） |
| V3-12 | 全量回归（目标: 874+ 全绿） |

### V3-15~17: 文档 & 案例

| 任务 | 描述 |
|------|------|
| V3-15 | 迁移指南（v0.2 → v0.3: 数据导出脚本） |
| V3-16 | 案例: "MCE + Supermemory = 完整记忆链路" |
| V3-17 | 更新的安装指南（默认纯分类模式） |

---

## 未来里程碑 (v0.3 之后)

### v0.4.0 — 官方下游适配器

| 适配器 | 优先级 | 工作量 |
|--------|--------|--------|
| **SupermemoryAdapter** | P0 | ~2d |
| **ObsidianAdapter** | P0 | ~1.5d |
| **Mem0Adapter** | P1 | ~1.5d |
| **JSONFileAdapter**（默认回退） | P0 | ~0.5d |

### v0.5.0 — `get_classification_schema` 增强

- 下游自动映射表（MCE 类型 → Supermemory 标签 → Mem0 类别 → Obsidian 文件夹）
- Schema 版本管理（v1.0 → v1.1 向后兼容）
- Web UI Schema 浏览器

### v0.6.0 — MCE-Bench 公开发布

- 180-case 标准基准数据集
- 排行榜格式（准确率 / 延迟 / 千条消息成本）
- 开放社区投稿
- 目标: 清晰消息准确率 >90%

### v1.0.0 — 行业标准

- 分类准确率 >95%
- 5+ 下游系统官方适配器
- 社区贡献适配器生态
- 学术论文: "为什么对 AI 记忆来说分类比存储更重要"

---

## 架构演进

```
v0.2.0 (当前)                    v0.3.0 (下一版)                   v1.0.0 (愿景)
┌─────────────┐                   ┌─────────────┐                   ┌─────────────┐
│  MCP Server  │                   │  MCP Server  │                   │  MCP Server  │
│  11 个工具    │                   │  4 个工具     │                   │  4 个工具     │
│  (8 个废弃)  │ ──breaking─────▶  │  (纯分类)    │                   │  (纯分类)    │
└──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘
       │                                 │                                 │
┌──────▼──────┐                   ┌──────▼──────┐                   ┌──────▼──────┐
│   引擎       │                   │   引擎       │                   │   引擎       │
│  (单体)      │                   │  (+to_memory │                   │  (优化)      │
│             │                   │   _entry())  │                   │  (>95% 准确) │
└──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘
       │                                 │                                 │
┌──────▼──────┐                   ┌──────▼──────┐                   ┌──────▼──────┐
│  SQLite     │                   │ Adapter ABC  │                   │ 适配器生态  │
│  (硬编码)    │                   │  + BuiltIn   │                   │ (5+ 官方)   │
└─────────────┘                   │  (deprecated)│                   │ + 社区贡献   │
                                 └──────┬──────┘                   └─────────────┘
                                        │
                              ┌──────────┼──────────┐
                              ▼           ▼           ▼
                         [Supermem]   [Obsidian]   [Mem0]   ...更多
```

---

## 关键指标目标

| 指标 | v0.2.0 (当前) | v0.3.0 (目标) | v1.0.0 (愿景) |
|------|--------------|---------------|---------------|
| MCP 工具数 | 11 (8 个废弃) | **4** (纯分类) | 4 |
| 代码量 (layer2_mcp/) | ~1580 行 | **~650 行** (-59%) | ~500 行 |
| 测试场景 | 92 (含 DB 依赖) | **43** (无 DB 依赖) (-53%) | 50+ |
| 分类准确率 | 未知 (~60% demo) | **>85%** (MCE-Bench) | **>95%** |
| 下游适配器 | 0 | 1 (BuiltIn @deprec) | **5+ 官方** |
| LLM 调用比例 | <10% | <10% | <5% |

---

## 决策记录

### DR-001: 为什么选纯上游而不是全栈？(2026-04-19)

**考虑过的选项**:
- A: 全栈（和 Supermemory/Mem0 在存储上竞争）❌
- B: 纯上游（仅分类，存储交给下游）✅
- C: 双模式（两个包）❌

**决策**: 路线 B — 纯上游

**关键原因**:
1. 无法在存储上竞争（Supermemory YC 投资，Mem0 18k stars）
2. 但没人把分类做好 —— 7 篇竞品文章**全部忽略**了这个维度
3. "仓库 vs 安检机"比喻很有说服力且有差异化
4. 代码减少 59%，测试减少 53%，维护负担大幅降低

**完整分析**: [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md)

### DR-002: 为什么先做 MCP 而不是框架适配器？(2026-04-11)

**决策**: MCP 优先于 LangChain/CrewAI/AutoGen 适配器

**理由仍然有效**:
- MCP 是趋势（Anthropic 大力推广）
- Claude Code / Cursor 用户 = 精准目标受众
- 低包装成本，高转化率
- 框架适配器可以作为 Layer 3 后续再做

### DR-003: 为什么不做 Skill 框架？(2026-04-10)

**决策**: 引擎，不是框架

**理由仍然有效**:
- 框架竞争激烈（LangChain、LlamaIndex）
- 引擎定位更清晰，差异化更强
- 更容易被其他框架集成
- 维护成本更低

---

## 推广计划

### Phase 1: 发布（现在 — v0.2.0）

- [x] GitHub 发布 v0.2.0
- [x] README 重写（Classification First 叙事）
- [ ] PyPI 发布（等待用户确认）
- [ ] "Classification First" 博客文章（起草中）

### Phase 2: 内容营销（与 v0.3 开发并行）

| 渠道 | 内容 | 状态 |
|------|------|------|
| Hacker News | "我为 AI 记忆系统做了一个前置过滤器" | ⏳ 计划中 |
| Reddit r/ClaudeAI | "MCE + Supermemory: 完整记忆链路教程" | ⏳ 计划中 |
| GitHub Discussions | Show HN 帖子 + 架构讲解 | ⏳ 计划中 |
| MCP Community | 提交到官方 MCP 工具注册表 | ⏳ 计划中 |
| 博客（中文/英文） | "为什么对 AI 记忆来说分类比存储更重要" | ⏳ 计划中 |
| Demo 视频 | 30 秒 Claude Code + MCE 操作 GIF | ⏳ 计划中 |

### Phase 3: 生态增长（v0.3 之后）

- 官方适配器发布（Supermemory、Obsidian、Mem0）
- MCE-Bench 公开排行榜
- 社区适配器贡献
- 主流 Agent 框架集成教程

---

## 附录

### 相关文档

| 文档 | 描述 |
|------|------|
| [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md) | 战略决策：为什么选纯上游 |
| [COMPETITOR_ANALYSIS_CONSENSUS_v2.md](./docs/consensus/COMPETITOR_ANALYSIS_CONSENSUS_v2.md) | 7 篇竞品文章深度分析 |
| [STRATEGIC_REVIEW_CONSENSUS_20260419.md](./docs/consensus/STRATEGIC_REVIEW_CONSENSUS_20260419.md) | 战略审视会议纪要 |
| [STORAGE_STRATEGY.md](./docs/user_guides/STORAGE_STRATEGY.md) | 下游集成指南 |
| [API 参考](./docs/api/API_REFERENCE_V1.md) | 完整 SDK/MCP/REST 文档 |
| [安装指南](./docs/user_guides/installation_guide_v2.md) | 安装、配置、故障排除 |

### 相关链接

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [Claude Code 文档](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Supermemory](https://supermemory.ai) — 推荐下游（云端）
- [Mem0](https://mem0.ai) — 推荐下游（自托管）

---

**文档版本**: v3.0.0
**最后更新**: 2026-04-19
**下次更新**: v0.3.0 发布后
