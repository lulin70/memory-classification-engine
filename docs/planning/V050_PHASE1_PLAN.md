# Phase 1 实施计划: 智能上下文注入 (v0.5.0)

> **目标**: CarryMem 不只是被动存储，而是主动为 AI 提供上下文
> **版本**: v0.4.3 → v0.5.0
> **制定日期**: 2026-04-26

---

## 一、实施顺序与依赖关系

```
1.2 记忆衰减与强化 (基础设施)
  ↓
1.3 查询缓存层 (性能保障)
  ↓
1.1 智能上下文注入 (核心功能，依赖 1.2 的 importance_score)
  ↓
1.4 记忆合并与冲突解决 (多 Agent 场景)
  ↓
1.5 记忆版本化 (可追溯性)
```

---

## 二、1.2 记忆衰减与强化

### 现状
- `access_count` 列已存在，但只增不减，从未用于排序
- 无 `last_accessed_at` 列
- 无 `importance_score` 列
- recall 排序仅靠 `confidence DESC`

### Schema 变更

```sql
ALTER TABLE memories ADD COLUMN last_accessed_at TEXT;
ALTER TABLE memories ADD COLUMN importance_score REAL NOT NULL DEFAULT 0.0;
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance_score DESC);
CREATE INDEX IF NOT EXISTS idx_memories_last_accessed ON memories(last_accessed_at DESC);
```

### 重要性评分公式

```python
importance_score = (
    confidence          # 基础置信度 (0-1)
    * type_weight       # 类型权重 (correction=1.3, decision=1.2, preference=1.1, fact=1.0, ...)
    * recency_factor    # 时间衰减 (1.0 → 0.3, 半衰期30天)
    * access_factor     # 访问强化 (1.0 + log(1 + access_count) * 0.1)
)
```

**类型权重**:
| 类型 | 权重 | 理由 |
|------|------|------|
| correction | 1.3 | 纠正最高优先，覆盖旧信息 |
| decision | 1.2 | 用户决策不可违背 |
| user_preference | 1.1 | 偏好影响体验 |
| fact_declaration | 1.0 | 事实基线 |
| relationship | 1.0 | 关系基线 |
| task_pattern | 0.9 | 模式可变 |
| sentiment_marker | 0.8 | 情感最易变 |

**时间衰减**:
```python
def recency_factor(created_at: datetime, now: datetime) -> float:
    age_days = (now - created_at).days
    half_life = 30  # 30天半衰期
    return 0.3 + 0.7 * (0.5 ** (age_days / half_life))
    # 0天: 1.0, 30天: 0.65, 90天: 0.475, 365天: 0.33
```

**访问强化**:
```python
def access_factor(access_count: int) -> float:
    return 1.0 + math.log(1 + access_count) * 0.1
    # 0次: 1.0, 1次: 1.069, 5次: 1.179, 10次: 1.239, 50次: 1.394
```

### 实现位置
- **新文件**: `src/memory_classification_engine/scoring.py` — 评分算法
- **修改**: `sqlite_adapter.py` — Schema 迁移 + recall 排序改为 importance_score
- **修改**: `sqlite_adapter.py` — recall 时更新 `last_accessed_at`
- **修改**: `base.py` — StoredMemory 增加 `importance_score` 和 `last_accessed_at` 字段

### 验收标准
- [ ] 新旧数据库自动迁移（ALTER TABLE + 计算现有记录的 importance_score）
- [ ] recall 结果按 importance_score DESC 排序
- [ ] 每次召回更新 last_accessed_at
- [ ] importance_score 在 remember 时计算并存储
- [ ] 提供 `recalculate_importance()` 方法手动重算

---

## 三、1.3 查询缓存层

### 设计

```python
class RecallCache:
    """LRU cache for recall results with TTL invalidation."""

    def __init__(self, max_size: int = 256, ttl_seconds: int = 300):
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._cache: OrderedDict[str, _CacheEntry] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[List[StoredMemory]]: ...
    def put(self, key: str, value: List[StoredMemory]) -> None: ...
    def invalidate(self, namespace: str = None) -> None: ...
    def clear(self) -> None: ...
```

**缓存 Key**:
```python
cache_key = f"{namespace}:{query}:{filters_hash}:{limit}"
```

**失效策略**:
- TTL: 5分钟自动过期
- 写入失效: remember/forget/declare 后清除该 namespace 缓存
- LRU: 超过 max_size 淘汰最久未访问

### 实现位置
- **新文件**: `src/memory_classification_engine/cache.py`
- **修改**: `sqlite_adapter.py` — recall 方法先查缓存
- **修改**: `sqlite_adapter.py` — remember/forget 后清除缓存
- **修改**: `carrymem.py` — 暴露 `clear_cache()` 方法

### 验收标准
- [ ] 重复查询命中缓存，跳过数据库
- [ ] 写入操作自动失效缓存
- [ ] TTL 过期后自动清除
- [ ] 线程安全
- [ ] 可通过配置禁用缓存

---

## 四、1.1 智能上下文注入

### 现有 build_system_prompt 的问题

1. **无智能排序**: 只按 confidence DESC，不考虑时效性和访问频率
2. **无 Token 预算**: 可能生成超长 prompt
3. **无结构化输出**: 只返回字符串，无法程序化处理
4. **无上下文感知**: 不分析对话内容来选择最相关记忆

### 新增 API

```python
def build_context(
    self,
    context: Optional[str] = None,
    max_memories: int = 10,
    max_knowledge: int = 5,
    max_tokens: int = 2000,
    language: str = "en",
) -> Dict[str, Any]:
    """Build structured context for AI injection.

    Returns:
        {
            "system_prompt": str,          # 完整系统提示词
            "memories": List[Dict],        # 选中的记忆列表
            "knowledge": List[Dict],       # 选中的知识条目
            "token_estimate": int,         # 估算 token 数
            "selection_reason": str,       # 选择理由
        }
    """

def build_system_prompt(
    self,
    context: Optional[str] = None,
    max_memories: int = 10,
    max_knowledge: int = 5,
    max_tokens: int = 2000,
    language: str = "en",
) -> str:
    """Enhanced: now uses importance_score ranking + token budget."""
```

### 上下文选择算法

```python
def _select_memories_for_context(
    memories: List[Dict],
    context: str,
    max_count: int,
    max_tokens: int,
) -> List[Dict]:
    # 1. 按 importance_score DESC 排序
    # 2. 如果有 context，对每条记忆计算 context_relevance
    #    context_relevance = token_overlap(context, memory.content) * 0.5
    #    final_score = importance_score * 0.7 + context_relevance * 0.3
    # 3. 按 final_score DESC 选前 max_count 条
    # 4. 估算 token 数 (chars / 4 for English, chars / 2 for CJK)
    # 5. 如果超出 max_tokens，从末尾裁剪
```

### Token 估算

```python
def _estimate_tokens(text: str) -> int:
    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff')
    other_count = len(text) - cjk_count
    return cjk_count // 1 + other_count // 4 + 1
```

### 实现位置
- **修改**: `carrymem.py` — 重写 build_system_prompt + 新增 build_context
- **新文件**: `src/memory_classification_engine/context.py` — 上下文选择算法

### 验收标准
- [ ] build_context 返回结构化数据
- [ ] build_system_prompt 使用 importance_score 排序
- [ ] Token 预算控制输出长度
- [ ] 有 context 时优先选择相关记忆
- [ ] 无 context 时按 importance_score 全局排序
- [ ] 支持 en/zh/ja 三语 prompt

---

## 五、1.4 记忆合并与冲突解决

### 设计

```python
class MemoryMerger:
    """Merge memories from multiple agents/namespaces."""

    STRATEGIES = ("latest_wins", "highest_confidence", "merge_all")

    def merge(
        self,
        memories: List[Dict],
        strategy: str = "latest_wins",
        conflict_callback: Optional[Callable] = None,
    ) -> List[Dict]:
        """Merge memories, resolving conflicts.

        Conflict detection: same content_hash across different namespaces.
        """
```

### 冲突检测
- 同一 content_hash 出现在不同 namespace → 潜在冲突
- 同一 type + 相似 content (Levenshtein ratio > 0.8) → 语义冲突

### 合并策略
| 策略 | 行为 |
|------|------|
| latest_wins | 保留 updated_at 最新的 |
| highest_confidence | 保留 confidence 最高的 |
| merge_all | 保留所有，标记为 duplicate_of |

### 实现位置
- **新文件**: `src/memory_classification_engine/merge.py`
- **修改**: `carrymem.py` — 新增 `merge_memories()` 方法

### 验收标准
- [ ] 检测跨 namespace 的 content_hash 冲突
- [ ] 三种合并策略均可工作
- [ ] 冲突回调机制可用

---

## 六、1.5 记忆版本化

### Schema 变更

```sql
ALTER TABLE memories ADD COLUMN version INTEGER NOT NULL DEFAULT 1;

CREATE TABLE IF NOT EXISTS memory_versions (
    version_id TEXT PRIMARY KEY,
    memory_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    changed_at TEXT NOT NULL DEFAULT (datetime('now')),
    change_reason TEXT,
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

CREATE INDEX IF NOT EXISTS idx_mv_memory_id ON memory_versions(memory_id);
CREATE INDEX IF NOT EXISTS idx_mv_memory_version ON memory_versions(memory_id, version);
```

### API

```python
def update_memory(
    self,
    storage_key: str,
    new_content: str,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Update a memory's content, creating a version history entry."""

def get_memory_history(
    self,
    storage_key: str,
) -> List[Dict[str, Any]]:
    """Get version history of a memory."""

def rollback_memory(
    self,
    storage_key: str,
    version: int,
) -> Dict[str, Any]:
    """Roll back a memory to a specific version."""
```

### 实现位置
- **修改**: `sqlite_adapter.py` — Schema 迁移 + 版本表
- **修改**: `carrymem.py` — 新增 update_memory / get_memory_history / rollback_memory
- **修改**: `base.py` — StoredMemory 增加 `version` 字段

### 验收标准
- [ ] update_memory 创建版本记录
- [ ] get_memory_history 返回完整历史
- [ ] rollback_memory 恢复到指定版本
- [ ] 版本号自增

---

## 七、文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `scoring.py` | 新建 | 重要性评分算法 |
| `cache.py` | 新建 | LRU 查询缓存 |
| `context.py` | 新建 | 上下文选择算法 |
| `merge.py` | 新建 | 记忆合并与冲突解决 |
| `carrymem.py` | 修改 | 新增 build_context/update_memory/merge_memories 等 |
| `sqlite_adapter.py` | 修改 | Schema 迁移 + importance_score + 缓存集成 |
| `base.py` | 修改 | StoredMemory 增加 importance_score/last_accessed_at/version |
| `__version__.py` | 修改 | 0.4.3 → 0.5.0 |
| `test_carrymem.py` | 修改 | 新增测试 |
| `test_scoring.py` | 新建 | 评分算法测试 |
| `test_cache.py` | 新建 | 缓存测试 |
| `test_context.py` | 新建 | 上下文注入测试 |
| `test_merge.py` | 新建 | 合并测试 |
| `test_versioning.py` | 新建 | 版本化测试 |

---

## 八、风险与缓解

| 风险 | 缓解 |
|------|------|
| Schema 迁移破坏旧数据库 | ALTER TABLE ADD COLUMN 是安全的；importance_score 默认 0.0，提供 recalculate_importance() |
| 缓存一致性问题 | 写入即失效 + TTL 双重保障 |
| importance_score 计算性能 | 在 remember 时计算并存储，recall 时直接排序，无需实时计算 |
| Token 估算不准确 | 保守估算 + max_tokens 硬限制 |
