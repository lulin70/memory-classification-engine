# CarryMem 特性实现状态 (v3.0)

**更新日期**: 2026-04-22
**版本**: v3.0 (对应 CarryMem v0.3.0)

---

## 核心特性

| 特性 | 版本 | 状态 | 说明 |
|------|------|------|------|
| 三层分类漏斗 | v0.1 | ✅ 完成 | Rule → Pattern → Semantic |
| 7 种记忆类型 | v0.2 | ✅ 完成 | preference/correction/fact/decision/relationship/task_pattern/sentiment |
| 4 级优先 Tier | v0.3 | ✅ 完成 | Sensory(24h)/Procedural(90d)/Episodic(365d)/Semantic(永久) |
| 确认模式检测 | v0.4 | ✅ 完成 | EN/CN/JP 三语确认模式 |
| CarryMem 主类 | v0.5 | ✅ 完成 | classify_message/classify_and_remember/recall/forget |
| SQLite 适配器 | v0.6 | ✅ 完成 | FTS5 + Dedup + TTL + Namespace |
| Obsidian 适配器 | v0.7 | ✅ 完成 | Markdown直读 + FTS5 + Frontmatter + Wiki-links |
| 主动声明 declare() | v0.8 | ✅ 完成 | confidence=1.0, source_layer="declaration" |
| 记忆画像 get_profile() | v0.8 | ✅ 完成 | SQL聚合 + 中文摘要 |
| Namespace 隔离 | v0.9 | ✅ 完成 | 项目级隔离 + 跨 namespace 检索 |
| 智能调度 build_system_prompt() | v0.10 | ✅ 完成 | EN/CN/JP prompt + memory-first priority |
| Plugin 适配器加载 | v0.10 | ✅ 完成 | entry_points + loader.py |
| MCE-Bench 公开基准 | v0.10 | ✅ 完成 | 180 用例 (EN/CN/JP × 60) |

---

## MCP 工具状态 (3+3+3+2+1)

| 工具组 | 工具 | 状态 |
|--------|------|------|
| **Core (3)** | classify_message | ✅ |
| | get_classification_schema | ✅ |
| | batch_classify | ✅ |
| **Storage (3)** | classify_and_remember | ✅ |
| | recall_memories | ✅ |
| | forget_memory | ✅ |
| **Knowledge (3)** | index_knowledge | ✅ |
| | recall_from_knowledge | ✅ |
| | recall_all | ✅ |
| **Profile (2)** | declare_preference | ✅ |
| | get_memory_profile | ✅ |
| **Prompt (1)** | get_system_prompt | ✅ |

---

## 测试状态

| 测试套件 | 测试数 | 状态 |
|---------|--------|------|
| tests/test_carrymem.py | 32 | ✅ 全部通过 |
| benchmarks/ (MCE-Bench) | 180 | ✅ 数据集就绪 |

---

## 项目结构清理 (v0.3.0)

| 操作 | 说明 |
|------|------|
| engine.py 精简 | 2263行 → 182行，移除企业级功能 |
| 删除遗留目录 | dashboard/, demo/, examples/, mce-mcp/, scripts/, vscode-extension/ |
| 删除遗留文档 | api/, blog/, config/, demo_report/, privacy_enhancement/ 等 |
| 统一测试套件 | test_v6~v10 → test_carrymem.py |
| 删除遗留 utils | encryption, access_control, distributed, tenant 等 |

---

## 待开发特性

| 特性 | 优先级 | 说明 |
|------|--------|------|
| Redis 适配器 | 中 | 分布式存储场景 |
| PostgreSQL 适配器 | 中 | 企业级存储场景 |
| 记忆合并/冲突解决 | 高 | 多 Agent 场景下的记忆一致性 |
| 记忆导出/导入 | 高 | 用户数据可携带性 |
| MCP 远程模式 | 中 | stdio → SSE/Streamable HTTP |
| 记忆质量评分 | 低 | 自动评估记忆质量 |
