# CarryMem 路线图

**当前版本**：v0.3.0
**最后更新**：2026-04-22

[English](ROADMAP.md) | **中文** | [日本語](ROADMAP-JP.md)

---

## 已完成里程碑

### v0.1 — 分类核心
- 三层分类漏斗（规则 → 模式 → 语义）
- 7 种记忆类型分类
- 基础规则匹配引擎

### v0.2 — 记忆类型与层级
- 7 种结构化记忆类型
- 4 层优先级系统 + TTL
- Memory Entry Schema v1.0

### v0.3 — 层级系统
- 感觉记忆（24h）/ 程序性记忆（90d）/ 情景记忆（365d）/ 语义记忆（永久）
- 基于层级的存储和检索

### v0.4 — 确认模式检测
- EN/CN/JP 确认模式检测
- 上下文感知异常处理

### v0.5 — CarryMem 主类
- `classify_message()` — 纯分类
- `classify_and_remember()` — 分类 + 存储
- `recall_memories()` / `forget_memory()`
- 纯上游模式（无需存储）

### v0.6 — SQLite 适配器
- FTS5 全文搜索
- 内容去重
- 基于层级的 TTL 自动过期
- `CarryMem(storage="sqlite")` 默认

### v0.7 — Obsidian 知识库
- ObsidianAdapter（只读）
- Markdown 直读 + FTS5 + YAML frontmatter + wiki-links
- MCP 3+3+3 模式（核心 + 存储 + 知识库）
- `recall_all()` 统一检索

### v0.8 — 主动声明与记忆画像
- `declare()` — 主动声明（confidence=1.0, source_layer="declaration"）
- `get_memory_profile()` — 结构化记忆聚合
- MCP 3+3+3+2 模式（+ 画像工具）

### v0.9 — 命名空间隔离
- 基于命名空间的项目级记忆隔离
- 跨命名空间检索支持
- SQLite namespace 列 + 自动迁移

### v0.10 — 智能调度与插件系统与 MCE-Bench
- `build_system_prompt()` — EN/CN/JP 提示词模板，记忆优先
- 插件适配器加载器（entry_points）
- MCE-Bench：180 用例公开基准数据集（EN/CN/JP × 60）
- MCP 3+3+3+2+1 模式（+ 提示词工具）

### v0.3.0 — 项目清理与重构
- Engine 精简重构（2263 → 182 行）
- 移除企业级功能（租户、访问控制、加密、分布式）
- 删除遗留目录和文件
- 统一测试套件（125/125 通过）
- README 重写，含对比表

### v0.3.0+ — 多语言增强与可携带性
- 中文/日语分类规则全面增强（ZH 79.1%→91.0%, JA 76.1%→89.6%）
- 修复日语语言检测（先检查 hiragana/katakana）
- 修复 CJK 短消息阈值
- `export_memories()` — JSON + Markdown 导出
- `import_memories()` — JSON 导入 + skip_existing 合并策略
- PyPI 打包完善（setup.py + pyproject.toml + MANIFEST.in）
- 125 个测试全部通过（EN×7 + ZH×7 + JA×7 + 噪声×3 + 集成 + 导出导入 + 边界）

---

## 下一阶段优先级

### 优先级 1：记忆合并与冲突解决
- 多 Agent 场景下的记忆一致性
- 冲突检测与解决策略
- 记忆版本控制

### 优先级 2：MCP 远程模式
- stdio → SSE/Streamable HTTP 传输
- 远程 CarryMem 服务器部署
- 多客户端支持

### 优先级 3：额外适配器
- Redis 适配器（分布式存储）
- PostgreSQL 适配器（企业级存储）
- S3/R2 适配器（云存储）

### 优先级 4：从其他工具导入
- Mem0 JSON 格式兼容
- LangChain Memory 格式兼容
- 通用 CSV 导入

---

## 长期愿景

**CarryMem = AI 记忆的 USB-C**

就像 USB-C 标准化了设备连接一样，CarryMem 旨在标准化 AI 记忆：
- **一种格式**：MemoryEntry JSON Schema v1.0
- **任意存储**：SQLite、Obsidian、Redis、PostgreSQL，或你的自定义适配器
- **任意工具**：MCP 协议实现通用 Agent 集成
- **你的数据**：记忆属于用户，不属于工具

> "不要记住一切。只记住重要的。"
