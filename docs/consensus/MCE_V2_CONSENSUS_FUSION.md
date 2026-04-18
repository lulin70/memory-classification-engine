# MCE v2.0 → 产品方向优化：方案融合与推进路径共识
**日期**: 2026-04-18  
**参与方**: PM / 架构师 / 测试专家 / 独立开发者  
**输入文档**: 
- `RELEASE_PREP_PLAN_V1.md` (当前执行计划, D-1✅ D-2✅ D-2.5✅ REL-001~004✅)
- `MCE_产品方向优化提案.md` (下午讨论的产品方向)
- `DEMO_INTERACTION_REPORT_v1.md` (26/30 通过)
- `USER_STORY_CALIBRATION_v1.md` (API 签名校准)

---

## 0. 两份方案的对齐分析

### 0.1 当前状态快照（RELEASE_PREP_PLAN_V1 执行进度）

| 阶段 | 任务 | 状态 | 产出 |
|------|------|------|------|
| **D-1** 技术加固 | 4项修复 (RLock/comments/exception/start_time) | ✅ 完成 | 874 测试通过 |
| **D-2.1** 技术博客 | 深度技术博客 | ✅ 完成 | docs/blog/ |
| **D-2.2** User Story 校准 | 用户画像+旅程+API校准 | ✅ 完成 | docs/product-manager/ |
| **D-2.3** Demo 测试 | 4场景×30步 | ✅ 完成 | 26/30 (87%) |
| **D-2.4** 安装指南 v2 | 8节+12 troubleshooting | ✅ 完成 | docs/user_guides/ |
| **D-2.5** 全员审核 | 四方签字 | ✅ 一致通过 | docs/review/ |
| **REL-001~004** 发布前修复 | README/API/Demo/audit修复 | ✅ 完成 | 26/30↑ |
| **Phase A** PyPI 发布 | 双包发布+社区推广 | ⏳ 待执行 | — |

### 0.2 产品方向提案的核心主张

| 主张 | 内容 | 与当前代码的关系 |
|------|------|------------------|
| **定位**: 引擎非产品 | MCE 是分类引擎，不是完整记忆库 | 当前代码已有 T1-T4 存储层，需重新审视 |
| **存储外置** | 输出 JSON Schema，用户决定存哪 | 当前代码有 SQLite/Neo4j/FAISS 内置存储，存在矛盾 |
| **Obsidian 作为 v1 默认后端** | Markdown 文件即数据库 | 当前有 Obsidian 集成但未作为主要输出通道 |
| **标准化记忆格式** | JSON Schema 定义条目字段 | 当前返回 dict 但无正式 Schema 定义 |
| **会话级召回接口** | 新会话自动注入历史记忆 | 当前有 retrieve_memories 但无"会话初始化"封装 |
| **不做的事** | 不自建向量DB/不做UI/不做SaaS/不做跨工具采集 | 与当前代码的 FAISS/Neo4j 存在定位冲突 |

### 0.3 关键矛盾点

| # | 矛盾 | 当前代码现状 | 提案主张 | 需要决策 |
|---|------|-------------|---------|---------|
| B1 | **内置存储 vs 存储外置** | T1(内存)+T2(SQLite)+T3(FAISS)+T4(Neo4j) | 输出 JSON Schema，存储由适配器决定 | 是否重构存储架构？ |
| B2 | **向量检索内置 vs 外部** | 内置 FAISS 向量索引 + SmartCache | 基础检索(类型+时间+关键词)，语义检索留给外部 | FAISS 定位是什么？ |
| B3 | **PyPI 先发 vs 方案先定** | D-2.5 已批准进入 Phase A | 提案的 Phase 1 任务可能改变发布内容 | 是否暂停 Phase A？ |
| B4 | **MCP Server 定位** | 作为独立服务端进程 | 作为 Agent 工具侧的实时采集入口 | 功能边界是否调整？ |

---

## 1. 👔 产品经理 (PM) 分析

### 1.1 对两份方案的整体评估

**当前 RELEASE_PREP_PLAN_V1 的价值**：
- 完成了从"能跑"到"能发布"的质量门槛跨越
- 874 测试通过、Demo 87%、四方审核一致通过 —— 这是**工程可信度**的基础
- 博客、安装指南、User Story 文档 —— 这是**市场就绪度**的基础

**产品方向提案的价值**：
- 解决了"分类之后呢？"的根本问题 —— 用户不只需要分类结果，需要完整的记忆闭环
- 明确了"引擎 vs 产品"的定位边界 —— 这决定了技术债偿还的方向
- 4 个开放问题（Schema 字段、文件组织、遗忘配置、适配器接口）—— 这些是**下一步必须回答的问题**

### 1.2 PM 的关键判断

**判断 1: 不应放弃 Phase A (PyPI 发布)，但应调整发布内容**

理由：
- 当前 874 测试 + 26/30 Demo + 四方审核 = 工程质量已达标
- 如果因为产品方向调整而推迟发布，会浪费已完成的工作（博客、指南、Demo）
- **建议**: 按 Phase A 发布当前版本为 **v0.2.0 (Engine Preview)**，同时明确标注这是"引擎核心"，存储适配器在 v0.3

**判断 2: 提案的 Phase 1 任务应拆分为两个子阶段**

```
v0.2.0 (Engine Preview)     → Engine Core + MCP Server (PyPI 发布)
v0.3.0 (提案P1)   → JSON Schema 标准化 + Obsidian 适配器 + 会话召回
v0.4.0 (提案P2)   → 自定义规则 + 遗忘工程化 + 模式晋升
```

**判断 3: 开放问题的优先级排序**

| 开放问题 | 优先级 | 理由 |
|----------|--------|------|
| Q1: JSON Schema 字段定义 | **P0** | 所有后续工作的基础，没有 Schema 就没有标准输出 |
| Q4: 存储适配器接口设计 | **P0** | 决定架构走向，必须在写任何适配器前确定 |
| Q2: Obsidian 文件组织方式 | P1 | 依赖 Q1 和 Q4，有了 Schema 和接口才能设计文件布局 |
| Q3: 遗忘机制配置化程度 | P2 | 当前默认值可用，用户自定义是增强功能 |

### 1.3 PM 推荐的推进路径

```
Week 1 (Now):    ┌─ Phase A: PyPI 发布 v0.2.0 (Engine Preview)
                 │   - mce-core 包 (pip install memory-classification-engine)
                 │   - mce-mcp-server 包
                 │   - 同步发布博客到公众号/GitHub
                 │
Week 2-3:       ├─ Phase B: 产品方向落地 (提案 Phase 1)
                 │   B-1: 定义 MemoryEntry JSON Schema (Q1)
                 │   B-2: 设计 StorageAdapter 抽象接口 (Q4)
                 │   B-3: 实现 ObsidianStorageAdapter (Q2)
                 │   B-4: 实现 SessionRecall 接口 (会话级召回)
                 │
Week 4:         ├─ Phase C: 质量验证 + v0.3.0 发布准备
                 │   - 新功能的单元测试 + 集成测试
                 │   - 更新文档 (README + API Reference)
                 │   - Demo 测试覆盖新流程 (Obsidian 写入 + 会话召回)
                 │
Week 5+:        └─ Phase D: 社区运营 + 反馈收集
                     - GitHub Issues 响应
                     - 公众号文章《人是不可压缩的》
                     - 收集用户反馈指导 v2.2 规划
```

---

## 2. 🏗️ 架构师 (ARCH) 分析

### 2.1 对"存储外置"主张的技术评估

**PM 提案说"MCE 不做重存储"，但当前代码现实是：**

```
当前架构:
  Engine → StorageCoordinator → Tier1(RAM) + Tier2(SQLite) + Tier3(FAISS) + Tier4(Neo4j)
                                    ↑
                              这些都是"内置存储"

PM 提案目标架构:
  Engine → MemoryEntry(JSON Schema) → StorageAdapter(interface) → Obsidian/SQLite/JSON
                                        ↑
                                  适配器模式，存储完全外置
```

**架构师判断: 不需要推翻现有存储层，而是增加一个"标准化出口"**

具体方案：

```python
# 当前: process_message() 返回内部存储格式
result = engine.process_message("I prefer double quotes")
# result = {'message': ..., 'matches': [{internal_storage_format...}]}

# 目标: 增加 to_memory_entry() 方法，输出标准格式
entry = engine.to_memory_entry(result)
# entry = MemoryEntry(
#     id="mem_xxx",
#     type="user_preference",
#     content="I prefer double quotes",
#     confidence=0.92,
#     source="rule_match",
#     tier=2,
#     created_at="2026-04-18T15:00:00Z",
#     context={"session_id": "xxx"},
#     metadata={"raw_message": "I prefer double quotes"}
# )
```

**这样做的优势**：
1. 现有的 T1-T4 存储层保留不变（它们是引擎内部的缓存/工作区）
2. 新增 `to_memory_entry()` 作为"对外标准出口"
3. `StorageAdapter` 接收 `MemoryEntry` 对象，写入外部存储
4. 内部存储和外部存储解耦 —— 内部用于引擎运行时性能，外部用于用户持久化记忆资产

### 2.2 对 4 个开放问题的技术方案

#### Q1: JSON Schema 字段定义

```json
{
  "$schema": "https://memory-classification-engine.dev/schema/v1",
  "type": "object",
  "required": ["id", "type", "content", "created_at", "source"],
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "type": {
      "type": "string",
      "enum": ["user_preference", "correction", "fact_declaration", 
               "decision", "relationship", "task_pattern", "sentiment_marker"]
    },
    "content": {"type": "string", "maxLength": 10000},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "source": {
      "type": "string",
      "enum": ["rule_match", "pattern_analysis", "semantic_inference", "user_feedback"]
    },
    "tier": {"type": "integer", "minimum": 1, "maximum": 4},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"},
    "expires_at": {"type": "string", "format": "date-time"},
    "context": {
      "type": "object",
      "properties": {
        "session_id": {"type": "string"},
        "agent_name": {"type": "string"},
        "tenant_id": {"type": "string"}
      }
    },
    "metadata": {"type": "object"},
    "status": {
      "type": "string",
      "enum": ["active", "archived", "expired", "conflict_pending"]
    },
    "links": {
      "type": "array",
      "items": {"type": "string", "format": "uri"}
    }
  }
}
```

**设计决策说明**:
- `id`: UUID 格式，全局唯一
- `type`: 7 种枚举，与现有分类体系对齐
- `content`: 限制 10K 字符，防止异常长消息
- `confidence`: 0-1 浮点数
- `source`: 4 种来源，对应三层漏斗 + 反馈
- `tier`: 1-4 整数，与现有存储层级对应
- `expires_at`: 支持遗忘机制的时间戳
- `status`: 支持生命周期管理
- `links`: 支持记忆间关联（如 correction→decision）

#### Q4: 存储适配器接口设计

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class MemoryEntry:
    id: str
    type: str
    content: str
    confidence: float = 0.0
    source: str = ""
    tier: int = 3
    created_at: str = ""
    updated_at: str = ""
    expires_at: Optional[str] = None
    context: dict = None
    metadata: dict = None
    status: str = "active"
    links: List[str] = None

class StorageAdapter(ABC):
    """Abstract base for all storage backends"""
    
    @abstractmethod
    def store(self, entry: MemoryEntry) -> bool:
        """Store a single memory entry. Returns True on success."""
        ...
    
    @abstractmethod
    def store_batch(self, entries: List[MemoryEntry]) -> int:
        """Store multiple entries. Returns count of successfully stored."""
        ...
    
    @abstractmethod
    def retrieve(self, query: str, memory_type: Optional[str] = None,
                 limit: int = 20, since: Optional[str] = None,
                 until: Optional[str] = None) -> List[MemoryEntry]:
        """Retrieve memories by query with optional filters."""
        ...
    
    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """Delete a memory by ID."""
        ...
    
    @abstractmethod
    def get_stats(self) -> dict:
        """Get storage statistics."""
        ...

class ObsidianAdapter(StorageAdapter):
    """Writes memories as Markdown files into an Obsidian vault"""
    def __init__(self, vault_path: str, organization: str = "by_type"):
        """
        Args:
            vault_path: Path to Obsidian vault root
            organization: File organization strategy:
                - 'by_type': One folder per memory type (recommended)
                - 'by_date': One folder per day
                - 'flat': All in single folder
        """
        ...

class JSONFileAdapter(StorageAdapter):
    """Writes memories as JSON lines file (one JSON per line)"""
    ...

class SQLiteAdapter(StorageAdapter):
    """Uses SQLite for structured persistent storage"""
    ...
```

**关于事务支持的决策**: 
- v1 不需要事务支持。记忆写入频率低（几十条/天），追加写入为主
- `store_batch()` 可以逐条调用 `store()`，失败时记录日志继续
- 如果未来需要事务（如企业版），可以在子类中实现

#### Q2: Obsidian 文件组织方式

**推荐: `by_type` (按类型分文件夹)**

理由:
- 用户最常按类型查找记忆（"我之前做了什么决策？"）
- 符合 MCE 的 7 类型分类体系
- Obsidian 的文件夹视图天然适合这种组织方式
- 未来如果需要跨类型搜索，可以用 Dataview 插件

```
obsidian_vault/
├── MCE Memories/
│   ├── user_preference/
│   │   ├── 2026-04-18_prefers-double-quotes.md
│   │   └── 2026-04-16_uses-spaces-not-tabs.md
│   ├── decision/
│   │   ├── 2026-04-17_use-redis-for-caching.md
│   │   └── 2026-04-15_project-python-not-go.md
│   ├── correction/
│   ├── fact_declaration/
│   ├── relationship/
│   ├── task_pattern/
│   └── sentiment_marker/
└── .obsidian/
```

每个 Markdown 文件格式:

```markdown
---
id: mem_20260418_150000_abc123
type: user_preference
confidence: 0.92
source: rule_match
tier: 2
created_at: 2026-04-18T15:00:00Z
status: active
links:
  - mem_20260417_decision_redis
tags: [mce/memory, preference/code-style]
---

I prefer double quotes, not single quotes.

> **Context**: Discussed during code review of auth module
> **Session**: claude-code-session-42
```

#### Q3: 遗忘机制配置化程度

**推荐: v1 提供合理默认值 + 可选高级配置**

```yaml
# config/forgetting.yaml (新增)
default_policy:
  enabled: true
  decay_rate: 0.05          # 每天衰减 5% 权重
  min_weight: 0.1           # 低于此值归档
  archive_after_days: 30    # 30 天未访问归档
  delete_after_days: 90     # 90 天未访问删除 (可选)

per_type_overrides:
  user_preference:
    decay_rate: 0.01         # 偏好衰减慢（长期有效）
    archive_after_days: 180
  sentiment_marker:
    decay_rate: 0.20         # 情绪衰减快（短期有效）
    archive_after_days: 7
  decision:
    decay_rate: 0.02         # 决策中等衰减
    archive_after_days: 90
```

**默认值策略**: 大多数用户不需要调这些参数。只有 Power User 在 `config/forgetting.yaml` 中覆盖。

### 2.3 架构师推荐的代码改动范围

| 改动 | 文件 | 工作量 | 依赖 |
|------|------|--------|------|
| 新增 `MemoryEntry` 数据类 | `src/mce/schemas.py` (新文件) | 0.5d | 无 |
| 新增 `to_memory_entry()` 方法 | `engine.py` | 0.5d | schemas.py |
| 新增 `StorageAdapter` ABC | `src/mce/adapters/base.py` (新文件) | 0.5d | 无 |
| 实现 `ObsidianAdapter` | `src/mce/adapters/obsidian.py` (新文件) | 1.5d | base.py |
| 实现 `JSONFileAdapter` | `src/mce/adapters/json_file.py` (新文件) | 0.5d | base.py |
| 新增 `SessionRecall` 封装 | `engine.py` 或新文件 | 1d | adapters |
| 更新 `process_message()` 返回值兼容性 | `engine.py` | 0.5d | 无 |
| 单元测试 (Schema + Adapter + Recall) | `tests/` | 1d | 以上全部 |

**总计: ~6 天开发工作量**

---

## 3. 🧪 测试专家 (QA) 分析

### 3.1 当前测试覆盖率评估

| 维度 | 当前状态 | 目标状态 (v2.1) | 差距 |
|------|---------|-----------------|------|
| 单元测试 | 874 tests passing | 保持 + 新增 Schema/Adapter 测试 | 需 +50~80 tests |
| 集成测试 | Demo 26/30 (87%) | 目标 28+/30 | 需修复剩余 2 个分类准确度 + 2 个 agent 注册 |
| API 兼容性 | 发现 5 处 API 文档偏差 | 全部修正 ✅ | 已完成 |
| 性能基线 | 有 benchmark 数据 | 需增加 Adapter 写入/读取性能基线 | 缺失 |
| 端到端流程 | 无 (只有 Demo 脚本) | 需要: 分类→Schema→Adapter写入→召回 全链路 | 缺失 |

### 3.2 对新功能的测试策略

#### MemoryEntry Schema 测试 (TC-SCHEMA-001~010)

| TC ID | 测试项 | 方法 |
|-------|--------|------|
| SCHEMA-001 | 必填字段验证 | 创建缺必填字段的 Entry → 应抛 ValidationError |
| SCHEMA-002 | type 枚举验证 | 传入非法 type → 应抛 ValueError |
| SCHEMA-003 | content 长度限制 | 传入 >10000 字符 → 应截断或拒绝 |
| SCHEMA-004 | confidence 范围 | 传入 >1.0 或 <0 → 应 clamp 到 [0,1] |
| SCHEMA-005 | 序列化/反序列化 | Entry → JSON → Entry 往返一致性 |
| SCHEMA-006 | 从 process_message 结果转换 | `to_memory_entry()` 输出符合 Schema |
| SCHEMA-007 | 所有 7 种 type 都能正确生成 | 逐一验证 |
| SCHEMA-008 | context 字段可选性 | 无 context 时不应报错 |
| SCHEMA-009 | links 字段空列表合法性 | links=[] 应正常 |
| SCHEMA-010 | 时间戳 ISO 格式验证 | created_at 应为合法 ISO 8601 |

#### StorageAdapter 测试 (TC-ADAPTER-001~015)

| TC ID | 测试项 | 方法 |
|-------|--------|------|
| ADAPTER-001 | Obsidian store → 文件存在 | store() 后检查 vault 中有 .md 文件 |
| ADAPTER-002 | Obsidian frontmatter 正确性 | 解析生成的 .md 文件 YAML 头 |
| ADAPTER-003 | Obsidian by_type 组织 | 文件出现在正确的 type 子目录 |
| ADAPTER-004 | Obsidian retrieve 按类型过滤 | 只返回指定 type 的记忆 |
| ADAPTER-005 | Obsidian retrieve 关键词搜索 | 内容匹配的记忆被召回 |
| ADAPTER-006 | JSONFile store → 可读 | store() 后文件可 json.loads 读取 |
| ADAPTER-007 | JSONFile store_batch → 数量正确 | 存入 N 条，retrieve 能取回 N 条 |
| ADAPTER-008 | delete 后 retrieve 为空 | 删除后不再出现 |
| ADAPTER-009 | 并发 store 安全性 | 10 线程同时 store 无数据损坏 |
| ADAPTER-010 | 空 vault/path 处理 | 目录不存在时自动创建 |
| ADAPTER-011 | 特殊字符转义 | content 含 `<>&"` 时 Markdown 安全 |
| ADAPTER-012 | 中文内容正确编码 | UTF-8 中文不乱码 |
| ADAPTER-013 | 超长 content 截断 | >10000 字符时处理正确 |
| ADAPTER-014 | get_stats 返回合理统计 | count/type_breakdown 正确 |
| ADAPTER-015 | 重复 ID 处理 | 相同 ID 再次 store 行为明确 (更新? 跳过?) |

#### SessionRecall 测试 (TC-RECALL-001~008)

| TC ID | 测试项 | 方法 |
|-------|--------|------|
| RECALL-001 | 空存储时 recall 返回空列表 | 无记忆时 [] |
| RECALL-002 | 有记忆时 recall 返回相关条目 | 存入偏好 → recall "code style" → 返回该偏好 |
| RECALL-003 | recall 按 session 过滤 | 不同 session 的记忆不混淆 |
| RECALL-004 | recall 按 type 过滤 | 只返回指定类型的记忆 |
| RECALL-005 | recall 时间范围 | since/until 参数生效 |
| RECALL-006 | recall limit 参数 | 返回数量不超过 limit |
| RECALL-007 | recall 响应时间 < 2s | 符合成功指标 |
| RECALL-008 | recall 注入上下文格式 | 输出格式适合 LLM prompt 注入 |

### 3.3 QA 对 Demo 测试的升级建议

当前 Demo (demo_test.py) 覆盖的是引擎内部功能。v2.1 需要新增 **E2E Demo 场景**:

```python
# Scenario E: Complete Memory Lifecycle (NEW)
# E1: Classify → E2: Convert to Schema → E3: Store via Adapter 
#      → E4: Recall from Adapter → E5: Inject into Context

# Scenario F: Cross-Session Migration (NEW)
# F1: Session A: Store 10 memories via Obsidian adapter
# F2: Shutdown engine
# F3: Session B: Init new engine + point to same vault
# F4: Recall → verify all 10 memories recovered
```

### 3.4 QA 推荐的测试优先级

| 优先级 | 测试类别 | 理由 |
|--------|---------|------|
| P0 | Schema 验证 (TC-SCHEMA-001~010) | 所有后续工作依赖 Schema 正确性 |
| P0 | ObsidianAdapter 核心 (ADAPTER-001~006) | v1 默认后端，必须可靠 |
| P1 | SessionRecall (RECALL-001~008) | 核心用户体验功能 |
| P1 | JSONFileAdapter (ADAPTER-006~007) | 最简单的适配器，适合 CI 测试 |
| P2 | 边界情况 (ADAPTER-009~015) | 增强，不影响发布 |
| P2 | E2E Demo (Scenario E/F) | 展示用，可后续补充 |

---

## 4. 💻 独立开发者 (Dev) 分析

### 4.1 从开发者视角看两份方案的可行性

**当前代码库的开发者体验评估**:

| 维度 | 评分 | 说明 |
|------|------|------|
| 安装体验 | 7/10 | pip install 可用但有依赖坑 (sklearn, faiss) |
| API 易用性 | 6/10 | 返回结构嵌套 (`matches[0]['type']`) 不够直觉 |
| 文档完整性 | 8/10 | 安装指南 v2 很详细，12 项 troubleshooting |
| Debug 友好度 | 5/10 | 日志太 verbose，错误信息不够清晰 |
| 测试覆盖 | 9/10 | 874 tests，回归稳定 |
| 扩展性 | 6/10 | 要嵌入自己的项目需要理解较多内部概念 |

**产品方向提案对开发者体验的影响**:

正面影响:
- `MemoryEntry` 标准化数据类 → API 更清晰，IDE 自动补全更好
- `StorageAdapter` 接口 → 开发者可以写自己的适配器
- Obsidian 适配器 → 开箱即用的"看得见"的记忆存储
- `SessionRecall` → 减少样板代码

需要关注的风险:
- 新增抽象层可能增加学习曲线
- `to_memory_entry()` 是额外一步，可能让简单用例变复杂
- 适配器模式增加了包体积和导入复杂度

### 4.2 开发者的具体实施建议

#### 建议 1: 保持向后兼容

```python
# v2.0 的用法仍然有效
engine = MemoryClassificationEngine()
result = engine.process_message("I prefer double quotes")
# result['matches'][0]['type'] → 仍然工作

# v2.1 新增的标准出口 (可选使用)
from memory_classification_engine import MemoryEntry, to_memory_entry
entry = to_memory_entry(result)  # 新方法
# entry.type → 更清晰的访问方式
```

**不要破坏现有 API！** `process_message()` 的返回格式保持不变，新增 `to_memory_entry()` 作为辅助函数。

#### 建议 2: 适配器应该是可选依赖

```python
# setup.py
extras_require = {
    'core': [],  # No extra deps
    'obsidian': ['frontmatter'],  # YAML parsing for Obsidian
    'testing': ['pytest', 'pytest-cov'],
}

# 用户选择安装:
# pip install memory-classification-engine       # Core only
# pip install memory-classification-engine[obsidian] # With Obsidian support
```

不要把 Obsidian 依赖塞进 core 包。

#### 建议 3: audit.py 的 JSON 崩溃修复应该立即合入

刚才发现并修复了 `audit.py:29` 的 JSON 解析崩溃问题（损坏日志行导致整个模块无法导入）。这个 fix 应该：
1. 立即提交到 main 分支
2. 加入 v0.2.0 发布范围
3. 补充单元测试确保 `_load_logs()` 跳过损坏行不会丢失数据

#### 建议 4: Demo 剩余 4 个失败的分析

| # | 失败 | 根因 | 是否需修 | 建议 |
|---|------|------|---------|------|
| A3.2 | "No, do it like this" → user_preference | 规则引擎匹配到 "prefer" 关键词而非 correction 模式 | **值得修** | 调整规则优先级或添加否定词检测 |
| A3.5 | "frustrating" → fact_declaration | 规则引擎未识别情绪词汇 | **值得修** | Layer 2 pattern analyzer 应捕获 |
| C2 | register_agent 返回 error | agent_manager 内部逻辑问题 | **暂缓** | 属于高级功能，v2.1 再修 |
| C2b | process_message 无 agent_id 参数 | API 设计问题 | **暂缓** | 同上 |

A3.2 和 A3.5 涉及**分类准确度**，这是 MCE 的核心竞争力，建议在 v2.1 优先修复。

### 4.3 开发者的工作量估算汇总

| 任务 | 工作量 | 复杂度 | 备注 |
|------|--------|--------|------|
| audit.py fix 合入 | 0.1d | 低 | 已有代码，只需提交 |
| MemoryEntry + Schema | 0.5d | 低 | 纯数据类 |
| to_memory_entry() | 0.5d | 低 | 映射函数 |
| StorageAdapter ABC | 0.5d | 低 | 接口定义 |
| ObsidianAdapter | 1.5d | 中 | Markdown 生成 + 文件组织 |
| JSONFileAdapter | 0.5d | 低 | JSONL 格式 |
| SessionRecall | 1d | 中 | 多源聚合 + 排序 |
| A3.2/A3.5 分类修复 | 1d | 中 | 规则调试 |
| 新增测试 (~80 tests) | 1d | 中 | Schema/Adapter/Recall |
| 文档更新 | 0.5d | 低 | README/API Ref |
| **总计** | **~7d** | | 1 人周左右 |

---

## 5. 共识达成

### 5.1 四方立场对比

| 议题 | PM | ARCH | QA | DEV | 共识? |
|------|-----|------|----|-----|--------|
| **是否先发 v0.2.0 PyPI?** | ✅ 发 (Engine Preview) | ✅ 发 | ✅ 发 | ✅ 发 | **✅ 一致** |
| **v0.2.0 定位标签** | "Engine Preview" | "Core SDK" | "Stable Beta" | "v0.2.0" | **✅ 都同意先发** |
| **存储层是否重构?** | 加"标准出口"即可 | 加 Adapter 抽象 | 不影响测试 | 保持兼容 | **✅ 不推翻，只扩展** |
| **JSON Schema 优先级** | P0 | P0 | P0 | P0 | **✅ 最高优先** |
| **Obsidian 适配器优先级** | P0 (v1 默认) | P0 | P0 | P0 | **✅ v2.1 必做** |
| **SessionRecall 优先级** | P0 | P1 | P1 | P1 | **⚠️ ARCH/QA/DEV 认为 P1，PM 坚持 P0** |
| **A3.2/A3.5 分类修复** | P0 | P1 | P0 | P0 | **✅ P0 共识 (3/4)** |
| **审计日志崩溃 fix** | 立即合入 | 立即合入 | 立即合入 | 立即合入 | **✅ 一致** |

### 5.2 最终共识方案

#### 共识 1: 分阶段发布路径

```
═══════════════════════════════════════════════════════════
  v0.2.0 "Engine Core"  ←  当前可立即执行
═══════════════════════════════════════════════════════════
  内容:
    ✅ 当前所有代码 (874 tests, 26/30 demo)
    ✅ audit.py JSON 崩溃修复
    ✅ README/API 文档更新 (REL-001~004 已完成)
    ✅ mce-core pip 包
    ✅ mce-mcp-server pip 包
    ✅ 技术博客发布
    ✅ GitHub Release
  
  不包含:
    ❌ MemoryEntry Schema (v2.1)
    ❌ StorageAdapter (v2.1)
    ❌ Obsidian 适配器 (v2.1)
    ❌ SessionRecall (v2.1)
    ❌ A3.2/A3.5 分类修复 (v2.1)

═══════════════════════════════════════════════════════════
  v0.3.0 "Memory Lifecycle"  ←  提案 Phase 1 落地
═══════════════════════════════════════════════════════════
  新增内容:
    📦 MemoryEntry JSON Schema (Q1 解决)
    📦 StorageAdapter 抽象接口 (Q4 解决)
    📦 ObsidianStorageAdapter (Q2 解决)
    📦 JSONFileStorageAdapter (CI 测试友好)
    📦 SessionRecall 接口 (会话级召回)
    🔧 A3.2/A3.5 分类准确度修复
    🧪 ~80 新测试用例
    📝 更新文档 (API Reference + 用户指南)

═══════════════════════════════════════════════════════════
  v0.4.0 "Adaptive Classification"  ←  提案 Phase 2 (远期)
═══════════════════════════════════════════════════════════
  新增内容:
    用户自定义分类规则 (YAML 配置)
    遗忘机制工程化 (configurable decay)
    模式晋升规则 (Tier 3 → Tier 2 auto-promotion)
    记忆冲突检测
```

#### 共识 2: v0.2.0 发布检查清单 (立即执行)

| # | 任务 | Owner | 状态 |
|---|------|-------|------|
| V0-1 | audit.py JSON 崩溃 fix 合入 main | Dev | ⏳ 待做 |
| V0-2 | 打 tag v0.2.0 | Dev | ⏳ |
| V0-3 | 构建 mce-core sdist/wheel | Dev | ⏳ |
| V0-4 | 构建 mce-mcp-server sdist/wheel | Dev | ⏳ |
| V0-5 | GitHub Release (含 changelog) | PM | ⏳ |
| V0-6 | 发布技术博客 | PM | ⏳ |
| V0-7 | 更新 README-ZH/JP 版本号 | PM | ⏳ |
| V0-8 | 全量回归测试 (874 tests) | QA | ⏳ |

#### 共识 3: v0.3.0 开发任务分解 (发布后启动)

| # | 任务 | Owner | 估时 | 依赖 |
|---|------|-------|------|------|
| V1-01 | 定义 MemoryEntry 数据类 + JSON Schema | Arch | 0.5d | 无 |
| V1-02 | 实现 to_memory_entry() 转换函数 | Dev | 0.5d | V1-01 |
| V1-03 | 定义 StorageAdapter ABC 接口 | Arch | 0.5d | 无 |
| V1-04 | 实现 ObsidianStorageAdapter | Dev | 1.5d | V1-03 |
| V1-05 | 实现 JSONFileStorageAdapter | Dev | 0.5d | V1-03 |
| V1-06 | 实现 SessionRecall 接口 | Dev | 1d | V1-03 |
| V1-07 | 修复 A3.2 (correction 分类) | Dev | 0.5d | 无 |
| V1-08 | 修复 A3.5 (sentiment 分类) | Dev | 0.5d | 无 |
| V1-09 | 编写 Schema 测试 (10 cases) | QA | 0.5d | V1-01 |
| V1-10 | 编写 Adapter 测试 (15 cases) | QA | 1d | V1-04 |
| V1-11 | 编写 Recall 测试 (8 cases) | QA | 0.5d | V1-06 |
| V1-12 | E2E Demo (Scenario E/F) | QA | 0.5d | V1-04+V1-06 |
| V1-13 | 更新 README + API Reference | PM | 0.5d | V1-01~V1-06 |
| V1-14 | 更新安装指南 (新增 Obsidian 章节) | PM | 0.5d | V1-04 |
| V1-15 | 全量回归 (874 + ~80 新测试) | QA | 0.5d | 全部 |

### 5.3 开放问题解决方案总结

| 问题 | 决策 | 谁决定的 |
|------|------|---------|
| Q1: JSON Schema 字段 | 14 字段定义 (见 §2.2) | 架构师提出，全员认可 |
| Q2: Obsidian 文件组织 | `by_type` (按类型分文件夹) | PM 提出，架构师确认可行 |
| Q3: 遗忘配置化 | 默认值 + 可选 forgetting.yaml 覆盖 | 全员认可 |
| Q4: 适配器接口 | StorageAdapter ABC + 6 方法 | 架构师设计，Dev 确认可实现 |

### 5.4 风险登记册 (更新)

| 风险 | 可能性 | 影响 | 缓解措施 | 负责人 |
|------|--------|------|---------|--------|
| v0.2.0 发布后被问"怎么存到 Obsidian?" | 高 | 中 | README 明确标注 "v0.3 增加 Obsidian 支持"；Issue template 引导 | PM |
| MemoryEntry Schema 在 v2.2 需要 breaking change | 中 | 中 | v1 Schema 使用 version URI，未来可演进 | Arch |
| Obsidian 适配器性能不达预期 (数千条文件) | 低 | 中 | 先实测；必要时加索引层 | Dev |
| SessionRecall 响应时间 > 2s | 中 | 高 | 设计时考虑预加载 + 缓存；QA 设性能基线 | Arch+QA |
| 用户不理解"引擎 vs 产品"定位 | 高 | 中 | README 首屏明确定位；博客文章解释 | PM |

---

## 6. 签字

```
================================================================================
                    MCE 方案融合共识会议纪要
              RELEASE_PREP_PLAN_V1 × 产品方向优化提案
                         2026-04-18
================================================================================

核心决策:
  ✅ 分两步走: v0.2.0 (Engine Core, 立即发布) → v0.3.0 (Memory Lifecycle)
  ✅ 不推翻现有存储层，增加"标准出口" + "适配器抽象"
  ✅ 4 个开放问题全部给出解决方案
  ✅ v2.1 工作量估算: ~7 人日

SIGNATURES:

  👔 Product Manager:     ✅ APPROVED    Date: 2026-04-18
  🏗️ Architect:           ✅ APPROVED    Date: 2026-04-18
  🧪 Test Expert (QA):    ✅ APPROVED    Date: 2026-04-18
  💻 Developer:           ✅ APPROVED    Date: 2026-04-18


CONSENSUS: ✅ UNANIMOUS — 执行 v0.2.0 发布 → 启动 v0.3.0 开发

Next Step: 用户确认本共识 → 立即执行 V0-1~V0-8 (v0.2.0 发布)
================================================================================
```
