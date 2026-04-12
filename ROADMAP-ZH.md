# Memory Classification Engine - 路线图

## 更新履历

| 版本 | 日期 | 更新人 | 更新内容 | 审核状态 |
|------|------|--------|----------|----------|
| v1.2.0 | 2026-04-12 | 产品团队 | 新增 VS Code 扩展、记忆质量仪表盘、待确认记忆和 Nudge 机制 | 已审核 |
| v1.1.0 | 2026-04-11 | 产品团队 | MCP Server 完成，Beta 测试启动 | 已审核 |
| v1.0.0 | 2026-04-10 | 产品团队 | 初始版本 - 三层集成策略规划 | 已审核 |

---

## 🎯 愿景

成为 Agent 记忆分类领域的标准组件，像 ChromaDB 之于向量存储一样，成为记忆分类的代名词。

---

## 三层集成策略

### Layer 1: Python SDK ✅ (已完成)

**状态**: 已可用

**目标**: 提供最基础的 Python 库，任何人都可以 pip install 之后自己接入

**核心功能**:
- [x] 实时消息分类
- [x] 7 种记忆类型识别
- [x] 三层判断管道
- [x] 四层记忆存储
- [x] 主动遗忘机制
- [x] VS Code 扩展
- [x] 记忆质量仪表盘
- [x] 待确认记忆机制
- [x] Nudge 主动复习机制

**下一步优化**:
- [ ] 完善 API 文档
- [ ] 添加更多使用示例
- [ ] 性能优化

---

### Layer 2: MCP Server ⭐ (Beta 测试中)

**状态**: ✅ 已完成核心功能，Beta 测试中

**目标**: 让 Claude Code、Cursor、OpenClaw 等支持 MCP 的工具可以直接调用

**为什么优先做 MCP？**

| 优势 | 说明 |
|------|------|
| 风口 | Anthropic 大力推 MCP，相关仓库涨势快 |
| 精准用户 | Claude Code / Cursor 用户正是目标受众 |
| 低投入 | 包装成本低（JSON-RPC 接口层） |
| 高转化 | 零摩擦使用，Topic 流量转化率高 |

**功能规划**:

#### Phase 1: 核心 MCP 工具 ✅ (已完成)

- [x] `classify_memory` - 分析消息并判断是否需要记忆
- [x] `store_memory` - 存储记忆到合适的层级
- [x] `retrieve_memories` - 检索相关记忆
- [x] `get_memory_stats` - 获取记忆统计信息
- [x] `batch_classify` - 批量分类
- [x] `find_similar` - 查找相似记忆
- [x] `export_memories` - 导出记忆
- [x] `import_memories` - 导入记忆

#### Phase 2: OpenClaw 集成 ✅ (已完成)

- [x] OpenClaw 适配器
- [x] OpenClaw 配置文件
- [x] 使用示例和文档

**技术方案**:

```python
# MCP Server 架构
mcp-server/
├── src/
│   └── mce_mcp_server/
│       ├── server.py      # MCP Server 主入口
│       ├── tools.py       # 工具定义
│       └── config.py      # 配置管理
├── pyproject.toml
└── README.md
```

**发布计划**:
- PyPI 包名: `mce-mcp-server`
- 提交到 MCP 社区仓库
- 在 Claude Code / Cursor 社区分享

---

### Layer 3: Framework Adapters (长期)

**状态**: 规划中

**目标**: 为主流 Agent 框架提供开箱即用的 Skill 包装

**框架适配计划**:

#### LangChain (优先级: 高)

```python
from memory_classification_engine.adapters.langchain import MemoryClassifierTool

tool = MemoryClassifierTool()
```

**功能**:
- [ ] MemoryClassifierTool 类
- [ ] 与 LangChain Memory 集成
- [ ] 使用文档和示例

#### CrewAI (优先级: 中)

```python
from memory_classification_engine.adapters.crewai import MemoryTool

tool = MemoryTool()
```

**功能**:
- [ ] MemoryTool 类
- [ ] 与 CrewAI Agent 集成
- [ ] 使用文档和示例

#### AutoGen (优先级: 中)

```python
from memory_classification_engine.adapters.autogen import MemoryAgent

agent = MemoryAgent()
```

**功能**:
- [ ] MemoryAgent 组件
- [ ] 与 AutoGen 对话集成
- [ ] 使用文档和示例

---

## 技术债务清理

### 代码质量优化 (持续进行)

**已完成**:
- [x] 修复 P0/P1 代码质量问题
- [x] 引擎类拆分重构 (Facade 模式)
- [x] 服务层架构实现
- [x] 代码审查清单
- [x] 静态代码分析工具配置

**进行中**:
- [ ] 完善单元测试覆盖率
- [ ] 性能基准测试
- [ ] 文档完善

**计划**:
- [ ] 引入依赖注入框架
- [ ] 完善错误处理机制
- [ ] 优化存储层性能

---

## 推广运营计划

### Phase 1: MCP Server 启动 ✅ (进行中)

**技术工作**:
- [x] 实现 MCP Server 核心功能 (8 个 tools)
- [x] 编写 MCP 配置文档
- [x] 创建 Claude Code 使用示例
- [x] 完成 27 个单元测试
- [ ] OpenClaw 集成
- [ ] 发布到 PyPI

**推广工作**:
- [x] 创建 Beta 测试指南 (中英文)
- [ ] 提交到 MCP 社区仓库
- [ ] 在 Claude Code Discord 分享
- [ ] 写技术博客

### Phase 2: 社区建设 (Month 2-3)

**内容营销**:
- 博客文章：《为什么你的 Agent 需要专业记忆分类》
- 演示视频：Claude Code + MCE 演示
- 用户案例：真实使用场景

**社区运营**:
- Reddit r/ClaudeAI
- Hacker News Show
- Twitter/X 技术圈
- GitHub Discussions

### Phase 3: Framework 集成 (Month 3-6)

**技术工作**:
- LangChain 适配器
- CrewAI 适配器
- AutoGen 适配器

**推广工作**:
- 在各框架社区发 PR
- 写集成教程
- 提供对比 benchmark

---

## 关键里程碑

| 时间 | 里程碑 | 关键指标 | 状态 |
|------|--------|---------|------|
| 2026-04-11 | MCP Server Beta 测试启动 | Beta 测试指南发布 | ✅ 已完成 |
| Month 1 | MCP Server 正式发布 | GitHub Stars: 200+ | 🔄 进行中 |
| Month 2 | 社区初步建立 | Stars: 500+, 社区成员: 50+ | ⏳ 待开始 |
| Month 3 | LangChain 适配 | Stars: 800+, 下载量: 1000/月 | ⏳ 待开始 |
| Month 6 | 完整生态 | Stars: 1500+, 下载量: 5000/月 | ⏳ 待开始 |

---

## 决策记录

### 为什么不做成 Skill 框架？

**讨论**: 是否应该做成类似 LangChain 的框架？

**决策**: 不做框架，专注引擎

**理由**:
1. 框架竞争激烈（LangChain, LlamaIndex 等）
2. 引擎定位更清晰，差异化明显
3. 更容易被其他框架集成
4. 维护成本更低

### 为什么 MCP Server 优先于 Framework Adapters？

**讨论**: 是否应该先做 LangChain 适配？

**决策**: MCP Server 优先

**理由**:
1. MCP 是风口，Anthropic 大力推广
2. 投入产出比更高（包装成本低，用户精准）
3. LangChain 适配可以作为 Layer 3 后续做
4. MCP 用户更愿意尝试新工具

---

## 附录

### 相关文档

- [架构设计](docs/architecture/architecture.md)
- [API 文档](docs/api/api.md)
- [用户指南](docs/user_guides/user_guide.md)
- [代码质量修复记录](docs/code_quality_fixes.md)

### 相关链接

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [Claude Code 文档](https://docs.anthropic.com/en/docs/claude-code/overview)
- [OpenClaw 项目](https://github.com/openclaw)

---

**文档版本**: v1.2.0  
**最后更新**: 2026-04-12  
**审核状态**: 已审核