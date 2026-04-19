# MCE 战略审视 × 当前计划：四方审核与共识报告
**日期**: 2026-04-19  
**输入文档**: 
- `MCE_战略审视报告_20260419.md` (战略审视)
- `RELEASE_PREP_PLAN_V1.md` (执行计划) + `MCE_V2_CONSENSUS_FUSION.md` (融合共识)
- `ROADMAP.md`, `README.md` (当前对外文档)

---

## 0. 核心发现：战略报告 vs 现状的对齐分析

### 0.1 战略报告的关键判断（我们是否同意？）

| # | 战略报告判断 | 我们的事实核查 | 结论 |
|---|------------|---------------|------|
| S1 | "分类作为独立价值，市场尚未有人系统占据" | ✅ 正确。Mem0/Supermemory/Graphiti 都讲存储+检索，没人讲分类质量 | **同意** |
| S2 | "MCP 是真正的差异化筹码，但没有充分展示" | ⚠️ 部分正确。README 有 MCP 章节，但未作为**第一差异化点**突出 | **同意，需调整** |
| S3 | "v2.0 特性和 v1.0 生产状态混在一起叙述，没有清晰区分" | 🔴 **完全正确！** README 把 Adaptive Retrieval/Feedback Loop/Distillation 当正式功能展示，无 Beta 标注 | **必须修正** |
| S4 | "Obsidian 适配器还没上线，迁移闭环没打通" | ✅ 正确。这是 v0.3.0 的内容，当前 v0.2.0 不包含 | **同意，已规划** |
| S5 | "缺乏真实场景效果验证 / Benchmark 数据" | ✅ 正确。有内部 benchmark 但无公开对比数据 | **同意，需补充** |
| S6 | "引擎定位需要具体场景来展示价值" | ✅ 同意。当前 README 有示例但缺 end-to-end 场景故事 | **部分同意，v0.3 补充** |
| S7 | "传播速度落后于赛道发展速度" | ⚠️ 部分同意。但我们的策略是 D-first（内容先行），现在正在执行 | **方向正确，加速即可** |

### 0.2 战略报告建议 vs 我们的计划的对照

| 战略报告建议 | 我们的对应计划 | 差距 |
|-------------|--------------|------|
| 最高优先: 打通 Obsidian 适配器 | v0.3.0 Phase B: V1-04 ObsidianAdapter (1.5d) | ✅ 已规划 |
| 最高优先: v2.0 功能加 Beta 标注 | ❌ **未做！README 无任何 Beta 标注** | **🔴 必须立即修复** |
| 高优先: 写 Case Study 带数据 | ⏳ 未列入 v0.2.0/v0.3 计划 | **🟡 应加入 v0.3** |
| 高优先: "分类是前置问题"叙事文章 | ✅ 博客已写 (D-2.1)，但角度是技术科普而非差异化定位 | 🟡 可优化角度 |
| 暂缓: 跨工具采集/企业级/自建语义检索 | ✅ 一致。共识文档明确"不做的事" | ✅ 对齐 |

---

## 1. 👔 产品经理 (PM) 分析与顾虑

### 1.1 PM 对战略报告的评估

**高度认同的部分**：
1. §七"差异化重新梳理"——不应该再说"比 Mem0 更好"，应该聚焦"分类是记忆系统的前置问题"。这个洞察非常精准
2. §五"README 过度承诺"——v2.0 功能当正式功能展示确实会伤害信任
3. §八"迷茫来自还没做到而非做错了"——这个心理诊断准确

**PM 不同意或需补充的部分**：

**不同意 S7 "传播落后"的焦虑感**：
- 战略报告写于 4/19，但我们从 4/18 开始已经在执行 D-first 内容策略
- 博客已完成、安装指南完成、Demo 完成、审核通过、代码已 push
- 传播不是"落后"，而是"刚刚开始"
- **建议**: 把焦虑转化为具体的下一步行动清单，而不是停留在情绪层面

**补充：战略报告遗漏了一个关键维度——用户画像**

战略报告说"应该主打的场景：AI Agent 开发者"，但没有进一步细分：
- **开发者 A**: 用 Claude Code 写代码，想要"代码偏好不被遗忘" → MCP 直接满足
- **开发者 B**: 构建自己的 Agent 产品，想嵌入记忆能力 → SDK 满足
- **研究者 C**: 研究 AI 记忆架构 → 论文/设计文档吸引

这三类人的需求不同，README 应该分层触达。

### 1.2 PM 的顾虑清单

#### PM-C1: README 过度承诺 — 这是最紧急的问题

**顾虑**: 当前 README 把 Adaptive Retrieval / Feedback Loop / Distillation 作为正式功能展示，和 MCP Server v1.0.0 Production 放在同等位置。用户会以为这些功能同样稳定。

**事实**:
- Feedback Loop: 需要 LLM API key 才能完整运行，默认配置下 RuleTuner 的 confidence threshold 可能不触发
- Distillation: ConfidenceEstimator 在 Demo 中显示 "LLM calls require API key"——说明核心路由依赖外部服务
- Adaptive Retrieval: compact/balanced/comprehensive 三种模式**可以工作**（Demo B3 验证），但 P99 性能数据是在理想条件下测的

**客观回答**: 
- 三种模式中，**Adaptive Retrieval 是最成熟的**（Demo 验证通过，无需外部依赖）
- Feedback Loop 和 Distillation 属于 **"架构到位，生产验证不足"**
- 建议: 给后两者加 `(Experimental)` 标签

**行动**: 立即在 README 中添加稳定性标注。

#### PM-C2: 缺少"30 秒内让用户理解价值"的一句话

**顾虑**: README 第一屏信息量大（三层漏斗图 + 成本表 + 对比表），新用户可能看不完就走了。

**事实**: 
- 当前首屏: 标题 + slogan + 问题描述 + How MCE Is Different + 成本表 = 约 60 行
- claude-mem 的 README 首屏更简洁: 一句话 + 一个命令 + 一个 GIF
- Supermemory 的首屏: 一行标语 + Stars 数 + Install 按钮

**客观回答**: 
- MCE 的产品复杂度高于竞品（它是引擎不是工具），所以 README 天然会更长
- 但可以在首屏增加一个 **"30-second value pitch"** 区块
- 参考: "Classify memories before storing them. 60%+ zero LLM cost. Works with Claude Code via MCP."

**行动**: 重构 README 首屏，增加 value pitch。

#### PM-C3: Roadmap 的里程碑时间线不现实

**顾虑**: ROADMAP.md 写 "Month 1: Stars 200+, Month 2: Stars 500+, Month 3: Stars 800+"。这些数字没有依据。

**事实**: 
- 当前实际 Stars: 未确认（战略报告说"还没有到被公众号报道的门槛"）
- claude-mem 达到 51k Stars 用了很长时间
- Supermemory 20.9k Stars 也是积累结果
- 设定数字目标而没有获客策略等于空谈

**客观回答**: 
- 数字目标应改为**行动目标**而非结果目标
- 例如: Month 1 目标从 "Stars 200+" 改为 "发布 3 篇技术文章 + 提交 MCP 社区仓库 + 回复所有 Issues"

**行动**: 重写 ROADMAP 里程碑为行动导向。

#### PM-C4: 对比表格可能引发反效果

**顾虑**: README 中有 MCE vs Mem0/MemGPT/LangChain Memory/claude-mem 的对比表格，MCE 在多数项打 ✓。

**事实**: 
- 战略报告 §七 明确指出: "放在一张对比表里虽然视觉上占优势，但会引发'那我为什么不直接用 Mem0'的问题"
- 用户看到对比表后的典型反应: "Mem0 有 25k+ Stars，我为什么要用一个没听说过的?"

**客观回答**: 
- 对比表在早期阶段**弊大于利**
- 应该替换为 **"Why not X?" FAQ 形式**，主动回答用户可能的疑问
- 或者在对比表中加上 "Stars" 列，诚实展示现状

**行动**: 重构或移除对比表，改为 FAQ 格式。

#### PM-C5: v0.2.0 Release Notes 缺失

**顾虑**: 我们已经 commit 了 v0.2.0 tag 并 push 了，但还没有写 GitHub Release notes。

**事实**: 
- GitHub Release 页面目前不存在（或只有之前的版本）
- Release notes 是用户了解版本变更的第一入口
- 没有好的 Release notes = 发布不完整

**行动**: 这是本次会议后的第一优先任务。

---

## 2. 🏗️ 架构师 (ARCH) 分析与顾虑

### 2.1 ARCH 对战略报告的评估

**高度认同的部分**：
1. §六"存储外置、引擎可嵌入——这是最重要的决策，不能动摇" — 与我们的 StorageAdapter 方案完全一致
2. §六"四层存储和认知心理学对齐" — 学术支撑增加了设计的可信度
3. §六"依赖极简(core 只需 PyYAML)" — 这是真正的竞争优势

**ARCH 不同意或需补充的部分**：

**关于 §六"Tier 4 语义存储的实际价值"质疑**:
- 战略报告问: "如果只是存关系类型记忆，是否值得强调?"
- **ARCH 回答**: Tier 4 (Neo4j/in-memory graph) 目前主要用于:
  1. relationship 类型记忆的多跳检索 (A→B→C)
  2. 冲突检测 (同一实体两个矛盾决策)
  3. 未来图谱推理的基础设施
- **是的，当前利用率不高**，但这是**前瞻性投资**，不应因为当前用得少就弱化
- **建议**: README 中降低 Tier 4 的宣传比重，但在 Architecture 文档中保留完整说明

**关于 §九"暂缓: 自建语义检索"**:
- 完全同意。FAISS 向量索引已经够用，自建向量 DB 是重复造轮子
- 但注意: **我们不"自建"语义检索，我们"内置"FAISS 作为可选依赖**
- 这个区别应该在对外沟通中明确

### 2.2 ARCH 的顾虑清单

#### ARCH-C1: v2.0 功能的生产稳定性边界不清

**顾虑**: 战略报告问 "v2.0 功能和 v1.0 MCP Server 是否同一可靠性级别?" —— 这是一个工程层面的问题。

**事实核查**:

| 功能 | 代码状态 | 测试覆盖 | 外部依赖 | 生产可用性 |
|------|---------|---------|---------|-----------|
| 三层漏斗分类 | ✅ 完整 | ✅ 874 tests 覆盖 | 无 (纯规则+模式) | **Production** |
| 四层存储 T1-T3 | ✅ 完整 | ✅ 测试覆盖 | SQLite (内置) | **Production** |
| Adaptive Retrieval | ✅ 完整 | ✅ Demo B3 通过 | 无 | **Production** |
| SmartCache | ✅ 完整 | ✅ 97.83% hit rate | 无 | **Production** |
| RLock 线程安全 | ✅ 刚修复 | ✅ Demo D5 通过 (10线程0错误) | 无 | **Production** |
| MCP Server (stdio) | ✅ 完整 | ✅ Demo B 6/6 | 无 | **Production v1.0.0** |
| Feedback Loop | ⚠️ 架构到位 | ⚠️ 无独立测试套件 | LLM API (optional) | **Experimental** |
| Distillation | ⚠️ 架构到位 | ⚠️ 无独立测试套件 | LLM API (optional) | **Experimental** |
| Tier 4 (Neo4j Graph) | ⚠️ 基础实现 | ⚠️ 边缘覆盖 | Neo4j (external) | **Beta** |

**客观回答**: 
- 6/9 项达到 Production 级别
- 2 项 (Feedback Loop, Distillation) 是 Experimental
- 1 项 (Tier 4) 是 Beta

**行动**: 在 README 和 ROADMAP 中明确标注每个功能的成熟度级别。

#### ARCH-C2: StorageAdapter 设计需要考虑向后兼容

**顾虑**: 共识方案提出新增 `MemoryEntry` + `StorageAdapter` + `to_memory_entry()`。这会影响现有 API 吗？

**事实**:
- `process_message()` 返回值不变（仍返回 dict）
- `to_memory_entry()` 是新的辅助函数，不影响现有调用方
- `StorageAdapter` 是新的抽象层，现有 T1-T4 存储继续工作
- **结论**: 完全向后兼容，零 breaking change

**但有一个细节**: 如果用户同时使用内部存储(T1-T4)和外部适配器(Obsidian)，同一条记忆会存两份。这需要文档说明。

**行动**: 在 v0.3 文档中说明"双存储"行为和推荐用法。

#### ARCH-C3: 性能基线数据需要公开透明化

**顾虑**: 战略报告指出 "Supermemory 在 LongMemEval 全项第一"。如果我们发布后被拿去做 Benchmark，排名如何？

**事实**:
- 内部 benchmark: process_message P99=1452ms, retrieve P99=66ms, cache hit=97.83%
- 这些数据是在特定条件下测的 (39K 条记忆, 单线程, warm cache)
- **我们没有参加过任何公开 Benchmark**

**客观回答**:
- 公开 Benchmark 参与应该是 v0.4 或之后的任务
- 当前阶段，**公开内部基准数据并标注测试条件** 比 参加 Benchmark 更合适
- 这样既展示了诚意，又不会因排名不好而尴尬

**行动**: 在 README 中增加 "Performance" 章节，附带测试条件说明。

#### ARCH-C4: MCP Server 存在两个实现的问题

**顾虑**: 安装指南 QA 发现了 `mce-mcp/mce_mcp_server/server.py`(HTTP, 6工具) 和 `src/.../layer2_mcp/server.py`(stdio, 11工具) 两个实现。这会让用户困惑。

**事实**:
- HTTP 版本是早期的 PoC 实现
- stdio 版本是对接 Claude Code/Cursor 的正式版本
- 两个版本的 tool set 不一致 (6 vs 11)

**客观回答**:
- **HTTP 版本应该标记为 Deprecated 或删除**
- 或者至少在文档中明确区分: "HTTP 版本仅供开发调试，生产环境请使用 stdio 版本"

**行动**: 在 mce-mcp 目录添加 DEPRECATED 说明，或在 setup.py 中移除 HTTP server 入口。

---

## 3. 🧪 测试专家 (QA) 分析与顾虑

### 3.1 QA 对战略报告的评估

**高度认同的部分**：
1. §五"README 过度承诺" — QA 从 Demo 测试中亲身体验到: 26/30 通过意味着 4 个失败点是真实的用户体验问题
2. §五"缺乏真实场景的效果验证" — QA 的 E2E Scenario E/F 计划正是为了填补这个空白

**QA 不同意或需补充的部分**：

**关于 §三"GitHub 数据还不在可见级别"**:
- QA 角度: Stars 数量不是质量指标
- 但 **Test Coverage 是** — 874 tests passing 是一个可以被量化的质量信号
- **建议**: 在 README badge 区域突出显示 test coverage，这比 Stars 更能证明项目健康度

### 3.2 QA 的顾虑清单

#### QA-C1: Demo 剩余 4 个失败的根本原因未深挖

**顾虑**: Demo 26/30 通过，剩余 4 个失败:
- A3.2: "No, do it like this" → 分类为 user_preference 而非 correction
- A3.5: "This workflow is so frustrating" → 分类为 fact_declaration 而非 sentiment_marker
- C2: register_agent() 返回 error
- C2b: process_message() 不接受 agent_id 参数

**事实**:
- A3.2/A3.5 是**分类准确度问题**，直接影响核心竞争力
- C2/C2b 是**高级功能问题**，影响范围小
- 战略报告强调 "分类质量是护城河，但护城河需要被证明" — 这两个失败正好证明了护城河还有漏洞

**客观回答**:
- A3.2 的根因: 规则引擎匹配到 "do it like this" 中的关键词，未能识别否定语境
- A3.5 的根因: 规则引擎未将 "frustrating" 识别为情绪词汇
- **这两个问题在 v0.3 应该作为 P0 修复**，因为它直接关系到"分类质量"的核心主张

**行动**: 
- A3.2/A3.5 加入 v0.3 V1-07/V1-08 任务列表 (原已有)
- 新增专项: 为 correction/sentiment 类型编写 20+ 边界测试用例

#### QA-C2: 安装指南 QA 发现了 11 个问题 — 还有多少没发现？

**顾虑**: 我们刚做了逐行审核发现了 11 个问题 (6 Critical)。那其他文档呢？

**事实**:
- installation_guide_v2.md: 已审核 ✅
- README.md: Quick Start 示例已验证 ✅，但全文未逐行审核
- README-ZH.md / README-JP.md: 未审核（可能是英文版的翻译，继承相同问题）
- user_guide.md: 未审核
- design*.md / architecture*.md: 未审核
- API_REFERENCE_V1.md: 未审核

**客观回答**: 
- 文档审核是一个持续过程，不可能一次做完
- **优先级**: 先确保面向用户的文档 (README + Installation Guide) 准确
- 内部文档 (design/architecture/API) 可以在 v0.3 逐步审核

**行动**: 本次先锁定 README 全文审核，其他延后。

#### QA-C3: 874 tests 的"有效覆盖率"是多少？

**顾虑**: 874 tests 听起来很多，但有多少是在测试真正重要的路径？

**事实** (粗略估算):
- ~200 tests: 基础单元测试 (各模块初始化、简单方法)
- ~150 tests: 存储层 CRUD (SQLite/内存操作)
- ~100 tests: 分类规则匹配 (Layer 1)
- ~80 tests: 模式分析 (Layer 2)
- ~50 tests: 语义推断 (Layer 3, mock LLM)
- ~100 tests: 引擎集成 (process_message 全流程)
- ~50 tests: MCP Server (tool 调用)
- ~50 tests: 配置/日志/工具函数
- ~44 tests: 其他 (privacy, community, utils 等)

**关键缺口**:
- **Feedback Loop 独立测试**: ≈0 (散落在引擎集成测试中)
- **Distillation 独立测试**: ≈0
- **StorageAdapter 测试**: ≈0 (还没写)
- **SessionRecall 测试**: ≈0 (还没写)
- **回归防护**: start_time bug 之前存在了多久? 13 个 latent failures!

**客观回答**: 
- 874 tests 的**广度足够**，但**深度不够均匀**
- Feedback Loop / Distillation 的测试缺失尤其值得关注
- 建议: v0.3 至少为 Experimental 功能补上基础测试 (每个 ≥10 cases)

**行动**: 在 v0.3 测试计划中加入 "Experimental 功能最小测试集" 要求。

#### QA-C4: audit.py JSON 崩溃 bug 暴露了测试盲区

**顾虑**: audit.py 中损坏的日志行导致整个模块无法导入。这种"单点故障级"bug 为什么没有被测试捕获?

**事实**:
- `_load_logs()` 方法没有 try/except 包裹 json.loads()
- 损坏的日志行 (双花括号 `{{`) 是之前 Demo 测试运行时产生的副作用
- **没有任何测试覆盖 `_load_logs()` 的异常输入场景**

**客观回答**: 
- 这是"快乐路径测试"的典型案例 — 只测了正常输入
- 修复方式 (try/except + continue) 是正确的
- 但应该补一个测试: "传入含损坏行的日志文件，不应崩溃"

**行动**: 加入 v0.3 测试计划 (TC-AUDIT-001: 异常日志文件处理)

---

## 4. 💻 独立开发者 (Dev) 分析与顾虑

### 4.1 Dev 对战略报告的评估

**高度认同的部分**：
1. §六"依赖极简(core 只需 PyYAML)" — 这是真正的工程优势，pip install 体验好
2. §九"暂缓: 自建语义检索" — 完全同意，不要造轮子
3. §八"技术上没被超越，传播上还没被看见" — 代码质量自信是有依据的

**Dev 不同意或需补充的部分**：

**关于 §九"最高优先: 两周内打通 Obsidian 适配器"**:
- 2 周 (10 个工作日) 做 ObsidianAdapter 是可行的
- 但还要同时做: JSON Schema + SessionRecall + A3.2/A3.5 修复 + 新增 ~80 tests
- 总工作量 ~7 人日 (之前估算)
- **如果只有 1 个人做，2 周很紧; 如果 2 个人并行，可行**
- **建议**: 确认人力资源再承诺时间线

### 4.2 Dev 的顾虑清单

#### DEV-C1: mce-mcp 双包发布的复杂性

**顾虑**: 当前有两个包要发布:
- `memory-classification-engine` (core, v0.2.0)
- `mce-mcp-server` (MCP wrapper, 也标为 v0.2.0)

但 mce-mcp 内部有两个 server 实现 (HTTP + stdio), 且 setup.py 刚修过。

**事实**:
- Core 包: dist/ 下已有 wheel (71K) + sdist (96K) ✅
- MCP 包: **还没有构建!** mce-mcp/setup.py 存在但没有 run build
- MCP 包的依赖 `>=0.2.0` 刚修正，但本地没验证能否正确 install

**客观回答**: 
- 需要在发布前单独构建 mce-mcp 包
- 并且做一个 "fresh install" 测试: 在干净的 venv 里 pip install 两个包，验证 import 正常

**行动**: 加入 V0 发布前 checklist。

#### DEV-C2: 版本号策略需要长期规划

**顾虑**: 当前版本号历史混乱:
```
代码内部 __init__.py:     0.1.0 → 0.2.0 (刚统一)
setup.py:                 0.4.0 → 0.2.0 (刚统一)
mce-mcp/setup.py:         1.0.0 → 0.2.0 (刚统一)
MCP Server VERSION:       1.0.0 (保持不变 — 这是协议版本)
```

未来怎么递增?
- Core 包: 0.2.0 → 0.3.0 → 0.4.0 → 1.0.0?
- MCP 包: 跟随 core 还是独立编号?
- MCP VERSION (协议版): 保持 1.0.0 直到协议变化?

**客观回答**: 
- 推荐 SemVer 策略:
  - Core: `0.x.y` (x=重大功能, y=bugfix)。到 1.0.0 的条件: Obsidian 适配器 + Case Study + 100+ GitHub Stars
  - MCP 包: 跟随 core 版本号 (`mce-mcp-server==0.2.0` 依赖 `mce-core==0.2.0`)
  - MCP VERSION (协议): 独立于包版本，按 MCP 协议规范递增

**行动**: 写入 CONTRIBUTING.md 或 docs/VERSIONING.md。

#### DEV-C3: 代码中仍有 394 个 placeholder comment 的残留风险

**顾虑**: 之前修复了 394 个 placeholder comment，但修复方式是替换为英文注释。这些注释的质量如何?

**事实**:
- 修复时使用了上下文感知的英文注释 (如 semantic_classifier.py 的 LLM client 初始化说明)
- 但没有逐一审查每条注释的准确性
- 如果有注释误导了后续开发者，也是技术债

**客观回答**: 
- 这是 P2 优先级的"代码卫生"问题
- 不影响功能，但影响可维护性
- 建议: 在 v0.3 的 code review 环节抽查 10%

**行动**: 加入 v0.3 code review checklist。

#### DEV-C4: Demo 脚本的维护成本

**顾虑**: demo_test.py 有 30 步骤，每次代码变更后都需要重跑验证。谁来维护?

**事实**:
- Demo 脚本是我们自己写的 QA 工具，不是给用户的
- 它的价值在于: 每次 release 前跑一遍，确保核心交互流程不退化
- 维护者应该是 QA (或 whoever owns release quality)

**客观答案**: 
- 将 demo_test.py 加入 CI/CD pipeline (如果有)
- 或者在 release checklist 中列为手动步骤
- 每次 release 前更新断言以匹配最新 API (如这次 REL-003 所做的)

**行动**: 在 RELEASE_PREP_PLAN 中固化 demo test 为 release gate。

---

## 5. 团队顾虑汇总与客观回答矩阵

| # | 顾虑 | 提出者 | 严重度 | 客观回答 | 行动 | 负责人 |
|---|------|--------|--------|---------|------|--------|
| 1 | README v2.0 功能无 Beta 标注 (过度承诺) | PM | **🔴 P0** | 6/9 功能 Production, 2 Experimental, 1 Beta | 立即修复 README | PM |
| 2 | 缺少 30s Value Pitch | PM | 🟡 P1 | MCE 复杂度高但可提炼一句话 | 重构首屏 | PM |
| 3 | Roadmap 星数目标不现实 | PM | 🟡 P1 | 改为行动目标 | 重写里程碑 | PM |
| 4 | 对比表格可能有反效果 | PM | 🟡 P1 | 改为 FAQ 格式 | 重构 README | PM |
| 5 | v0.2.0 Release Notes 缺失 | PM | **🔴 P0** | tag 已打但 Release 页面未创建 | 立即创建 | PM |
| 6 | 功能成熟度分级不清 | ARCH | 🟡 P1 | 已有 6/9 Production 数据 | 加标注到文档 | ARCH |
| 7 | MCP 双实现困惑 (HTTP vs stdio) | ARCH | 🟡 P1 | HTTP 是废弃 PoC | 标记 Deprecated | DEV |
| 8 | 性能数据缺少测试条件说明 | ARCH | 🟢 P2 | 有内部数据但未公开 | 增加 Performance 章节 | ARCH |
| 9 | A3.2/A3.5 分类准确度漏洞 | QA | **🔴 P0** | 护城河有洞，影响核心主张 | v0.3 P0 修复 | DEV |
| 10 | Feedback Loop/Distillation 测试缺失 | QA | 🟡 P1 | ≈0 独立测试 | 各补 ≥10 cases | QA+DEV |
| 11 | audit.py 异常处理测试缺失 | QA | 🟢 P2 | 无异常输入覆盖 | 补 TC-AUDIT-001 | DEV |
| 12 | mce-mcp 包未构建 + fresh install 未验证 | DEV | **🔴 P0** | 只有 core 包构建了 | 立即构建+验证 | DEV |
| 13 | 版本号策略未文档化 | DEV | 🟢 P2 | 多处版本号容易再次漂移 | 写 VERSIONING.md | DEV |
| 14 | Demo 脚本维护责任不清 | DEV | 🟢 P2 | 每次 release 要更新断言 | 固化为 release gate | QA |

---

## 6. 修订后的推进计划

### Phase 0: v0.2.0 发布收尾 (今天, 2h)

| # | 任务 | Owner | 时间 |
|---|------|-------|------|
| F0-1 | README 添加功能成熟度标注 (Production/Experimental/Beta) | PM | 30min |
| F0-2 | 创建 GitHub Release v0.2.0 (changelog) | PM | 30min |
| F0-3 | 构建 mce-mcp-server 包 + fresh install 验证 | DEV | 30min |
| F0-4 | 标记 HTTP server 为 Deprecated | DEV | 15min |
| F0-5 | Commit + Push + 更新 tag (amend if needed) | DEV | 15min |

### Phase 1: README/Roadmap 重构 (本周, 4h)

| # | 任务 | Owner | 时间 |
|---|------|-------|------|
| F1-1 | README 首屏重构: 增加 30s Value Pitch | PM | 1h |
| F1-2 | README: 对比表 → "Why Not X?" FAQ | PM | 1h |
| F1-3 | README: 增加 Performance 章节 (附测试条件) | ARCH | 30min |
| F1-4 | ROADMAP: 星数目标 → 行动目标 | PM | 30min |
| F1-5 | README-ZH/README-JP 同步更新 | PM | 1h |
| F1-6 | README 全文逐行审核 | QA | 1h |

### Phase 2: v0.3.0 开发 (下周, ~7 人日)

| # | 任务 | Owner | 估时 | 依赖 |
|---|------|-------|------|------|
| V3-01 | MemoryEntry JSON Schema 定义 | ARCH | 0.5d | 无 |
| V3-02 | to_memory_entry() 转换函数 | DEV | 0.5d | V3-01 |
| V3-03 | StorageAdapter ABC 接口 | ARCH | 0.5d | 无 |
| V3-04 | ObsidianStorageAdapter 实现 | DEV | 1.5d | V3-03 |
| V3-05 | JSONFileStorageAdapter (CI友好) | DEV | 0.5d | V3-03 |
| V3-06 | SessionRecall 接口 | DEV | 1d | V3-03 |
| V3-07 | **A3.2 修复: correction 分类准确度** | DEV | 0.5d | 无 |
| V3-08 | **A3.5 修复: sentiment 分类准确度** | DEV | 0.5d | 无 |
| V3-09 | Schema 测试 (10 cases) | QA | 0.5d | V3-01 |
| V3-10 | Adapter 测试 (15 cases) | QA | 1d | V3-04 |
| V3-11 | Recall 测试 (8 cases) | QA | 0.5d | V3-06 |
| V3-12 | Feedback Loop 最小测试集 (≥10 cases) | QA | 0.5d | 无 |
| V3-13 | Distillation 最小测试集 (≥10 cases) | QA | 0.5d | 无 |
| V3-14 | E2E Demo Scenario E/F | QA | 0.5d | V3-04+V3-06 |
| V3-15 | 文档更新 (API Ref + Install Guide Obsidian 章) | PM | 0.5d | V3-01~V3-06 |
| V3-16 | **Case Study: MCE 真实使用场景** (带数据) | PM | 1d | V3-04 |
| V3-17 | 全量回归 (874 + ~80 new) | QA | 0.5d | 全部 |

### Phase 3: 内容营销 (与 Phase 2 并行)

| # | 任务 | Owner | 时间 |
|---|------|-------|------|
| F3-1 | 提交 MCP 社区仓库 | PM | 1h |
| F3-2 | "分类是前置问题"英文文章 (Zenn/HN) | PM | 3h |
| F3-3 | Reddit r/ClaudeAI 发帖 | PM | 1h |
| F3-4 | GitHub Discussions 活跃化 | PM | 持续 |

---

## 7. 共识签字

```
================================================================================
              MCE 战略审视 × 四方审核 共识会议纪要
                    2026-04-19
================================================================================

战略报告核心结论采纳情况:
  ✅ "分类作为独立价值" — 确认为核心差异化定位
  ✅ "MCP 是第一差异化点" — 提升为 README 首屏要素
  ✅ "v2.0 功能需加 Beta 标注" — 立即执行 (F0-1)
  ✅ "对比表改为 FAQ" — Phase 1 执行 (F1-2)
  ✅ "Obsidian 适配器最高优先" — 纳入 v0.3 Phase 2 (V3-04)
  ✅ "Case Study 带数据" — 纳入 v0.3 (V3-16)
  ⚠️ "传播落后" — 不完全认同，已在执行 D-first 策略，加速即可

团队顾虑处理:
  🔴 P0 ×5: README Beta 标注 / Release Notes / mce-mcp 构建 / 分类准确度 / fresh install
  🟡 P1 ×7: Value Pitch / Roadmap / 对比表 / 成熟度分级 / MCP 双实现 / FL/Dist 测试
  🟢 P2 ×3: 性能章节 / 版本策略 / Demo 维护

推进计划:
  Phase 0 (今天): v0.2.0 发布收尾 (5 tasks, ~2h)
  Phase 1 (本周): README/Roadmap 重构 (6 tasks, ~4h)
  Phase 2 (下周): v0.3.0 开发 (17 tasks, ~7人日)
  Phase 3 (并行): 内容营销 (4 tasks)

SIGNATURES:

  👔 Product Manager:     ✅ APPROVED    Date: 2026-04-19
  🏗️ Architect:           ✅ APPROVED    Date: 2026-04-19
  🧪 Test Expert (QA):    ✅ APPROVED    Date: 2026-04-19
  💻 Developer:           ✅ APPROVED    Date: 2026-04-19


CONSENSUS: ✅ UNANIMOUS — 执行 Phase 0→1→2→3

Next Step: 立即执行 F0-1~F0-5 (v0.2.0 发布收尾)
================================================================================
```
