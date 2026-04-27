# CarryMem 竞品分析与差异化策略

**日期**: 2026-04-27
**版本**: v0.8.1
**基于**: 2026 AI 记忆赛道竞品调研

---

## 一、竞品格局总览

2026 年 AI 记忆赛道已从"概念验证"进入"产品竞争"阶段。按技术流派分为五大阵营：

### 1. 文件系统派（主流共识）

| 产品 | 核心特点 | 存储 | 集成 |
|------|---------|------|------|
| **OpenChronicle** | 本地优先、模型无关，7 分类扁平 Markdown | 本地 Markdown | MCP 多 Agent |
| **MemU** (陈宏) | 记忆智能体，Agent-Driven Memory | 文件系统 | 独立 |
| **OpenViking** (岭钢) | 虚拟文件系统，分层按需加载，企业级 | 虚拟文件系统 | OpenClaw |
| **memory-manager SKILL** | 分层冷热架构(hot/context/user)，蒸馏提炼 | Markdown 分层 | Skill/提示词/触发器 |

### 2. 代码/结构派

| 产品 | 核心特点 | 存储 |
|------|---------|------|
| **派AI** (李博杰) | Python 代码作为记忆载体，可执行验证 | Python 文件 |
| **Memov** (伯炎) | Git 管理编程记忆，影子 Git 记录决策分支 | Git 仓库 |

### 3. 全栈/混合派

| 产品 | 核心特点 | 存储 |
|------|---------|------|
| **MemoS** (熊飞宇) | 记忆操作系统，三层架构(参数/KV/外部) | 混合 |

### 4. 开源框架

| 产品 | 核心特点 | 存储 |
|------|---------|------|
| **MemBrain** | 自适应实体树，SOTA 基准 | 混合 |
| **Mem0** | 早期开源，向量数据库 | Milvus + 持久化 |
| **MemOS** (记忆张量) | 参数化/激活/明文三层，全局调度 | 混合 |

### 5. 集成工具

| 产品 | 核心特点 | 存储 |
|------|---------|------|
| **memsearch** (Zilliz) | Claude Code/OpenClaw 插件，Milvus 向量索引 | Milvus + Markdown |
| **附近的记忆** | 一条提示词构建，极简卡片笔记 | 目录 + 文本 |

---

## 二、CarryMem 的独特位置

### 竞品共性 vs CarryMem 差异

| 维度 | 竞品共性 | CarryMem 差异 |
|------|---------|--------------|
| **存储** | Markdown 文件 或 向量数据库 | **SQLite + FTS5** — 结构化+全文搜索，无需额外服务 |
| **分类** | 手动文件夹/标签 或 无分类 | **7 类型 + 4 层级自动分类** — AI 自动判断记忆类型和重要性 |
| **接入** | MCP 协议 或 SDK | **MCP + CLI + Python API + TUI** — 四种接入方式 |
| **粒度** | 文档级（整篇文章） | **偏好/事实级**（"I prefer dark mode"）— 身份级记忆 |
| **依赖** | 需要向量数据库/额外服务 | **零依赖核心** — pip install 即用 |
| **所有权** | 多数本地 | **本地优先 + 可导出** — 数据永远属于用户 |

### CarryMem 的三个不可替代性

1. **5 行代码接入** — 最轻量的记忆层
   ```python
   from memory_classification_engine import CarryMem
   cm = CarryMem()
   cm.classify_and_remember("I prefer dark mode")
   memories = cm.recall_memories("dark mode")
   print(cm.build_system_prompt())
   ```

2. **身份级记忆** — 不是"你读过什么"，而是"你是谁"
   - 其他产品存储文档/知识
   - CarryMem 存储偏好/决策/习惯/纠正 — 这些定义了"你是谁"

3. **零依赖核心** — 不需要 Milvus/Redis/向量数据库
   - SQLite + FTS5 内置于 Python 标准库
   - 语义搜索通过同义词扩展实现（不需要 embedding 模型）

---

## 三、差异化策略

### 策略 1：身份层定位（vs 知识层）

**核心叙事转变**：

```
Before: "AI 记忆系统"（和 Mem0/MemOS 竞争）
After:  "AI 身份层"（独特定位，无直接竞争）
```

**具体行动**：
- 新增 `carrymem whoami` — 输出你的 AI 身份画像
- `build_system_prompt()` 强化身份注入 — "This user prefers dark mode, uses Python for data analysis..."
- README 标语改为 "The Identity Layer for AI — Your AI remembers who you are"

### 策略 2：极简集成（vs 复杂部署）

**核心叙事**：

```
Mem0 需要 Milvus → 部署复杂
OpenViking 需要企业部署 → 门槛高
CarryMem → pip install carrymem → 5 行代码 → 完成
```

**具体行动**：
- MCP 工具新增 `auto_remember` 模式 — AI 对话自动提取并存储记忆
- 新增 `carrymem quickstart` — 交互式引导，30 秒完成首次配置
- 保证核心功能零外部依赖

### 策略 3：跨 Agent 身份同步（vs 单 Agent 记忆）

**核心叙事**：

```
OpenChronicle: 多 Agent 共享同一个记忆池（文件系统）
CarryMem: 多 Agent 共享同一个身份（结构化记忆）
```

**具体行动**：
- `carrymem profile export` — 导出身份画像（JSON），可导入其他 AI 工具
- MCP `get_memory_profile` 增强 — 返回结构化身份摘要
- 支持 `.carrymem/profile.json` 自动同步

### 策略 4：记忆质量（vs 记忆堆积）

**核心叙事**：

```
其他产品: 记忆只会越来越多，从不清理
CarryMem: 记忆有生命周期 — 创建、强化、衰减、过期
```

**具体行动**：
- `carrymem check` 已实现 — 冲突检测 + 质量评分 + 过期清理
- 重要性评分（importance_score）已实现 — 自动衰减 + 访问强化
- 新增 `carrymem clean --auto` — 自动清理低质量/过期记忆

---

## 四、与主要竞品的对比矩阵

| 能力 | CarryMem | Mem0 | OpenChronicle | MemoS | memsearch |
|------|----------|------|---------------|-------|-----------|
| 零依赖核心 | ✅ | ❌ (Milvus) | ✅ | ❌ | ❌ (Milvus) |
| 自动分类 | ✅ (7类型) | ❌ | ❌ (手动) | ✅ | ❌ |
| 重要性评分 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 记忆生命周期 | ✅ | ❌ | ❌ | ✅ | ❌ |
| CLI 工具 | ✅ (17命令) | ❌ | ❌ | ❌ | ❌ |
| TUI 界面 | ✅ | ❌ | ❌ | ❌ | ❌ |
| MCP 集成 | ✅ | ✅ | ✅ | ❌ | ✅ |
| 冲突检测 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 数据加密 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 版本历史 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 5 行代码接入 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 身份画像 | ✅ | ❌ | ❌ | ❌ | ❌ |

**CarryMem 是唯一同时具备**：零依赖 + 自动分类 + CLI + TUI + 加密 + 版本历史 + 身份画像 的记忆系统。

---

## 五、下一步行动

### v0.8.2: 差异化强化（立即实施）

| 任务 | 说明 | 优先级 |
|------|------|--------|
| `carrymem whoami` | 输出 AI 身份画像摘要 | P0 |
| MCP `auto_remember` | 对话自动提取记忆 | P0 |
| `carrymem profile export` | 导出身份画像 JSON | P1 |
| README 重写 | 强调"身份层"定位 | P1 |

### v0.9.0: 生态扩展

| 任务 | 说明 | 优先级 |
|------|------|--------|
| PyPI 发布 | pip install carrymem | P0 |
| VS Code 集成 | setup-mcp 支持 VS Code Copilot | P1 |
| Windsurf 集成 | setup-mcp 支持 Windsurf | P2 |

### v1.0.0: 正式发布

| 任务 | 说明 | 优先级 |
|------|------|--------|
| API 冻结 | 稳定公共 API | P0 |
| 性能白皮书 | 公开基准数据 | P1 |
| 安全审计 | 第三方审查 | P1 |

---

## 六、核心结论

> **CarryMem 不是"另一个记忆系统"，而是"AI 的身份层"。**
>
> 竞品解决的是"AI 怎么记住信息"，CarryMem 解决的是"AI 怎么认识你"。
>
> 这是从"知识管理"到"身份管理"的范式升级。

在 2026 年的记忆赛道中，CarryMem 的独特价值是：
1. **最轻量** — 5 行代码，零依赖
2. **最智能** — 自动分类 + 重要性评分 + 生命周期管理
3. **最完整** — CLI + TUI + MCP + Python API 四位一体
4. **最安全** — 本地存储 + 加密 + 版本历史
5. **最懂你** — 不只记住信息，更记住你是谁
