# CarryMem v0.3.0 — TRAE 集成测试报告

> **测试方**: TRAE Self Improvement 项目组  
> **测试日期**: 2026-04-18  
> **CarryMem 版本**: 0.3.0  
> **CarryMem 路径**: `/Users/lin/trae_projects/carrymem`  
> **Python 环境**: macOS, Python 3.x (TraeAI virtualenv)  
> **测试脚本**: `test_trae_integration.py`, `test_chinese_recall.py`

---

## 一、测试结论

| 功能 | 状态 | 说明 |
|------|------|------|
| 模块导入 | ✅ 通过 | `import memory_classification_engine` 成功，v0.3.0 |
| 初始化 | ⚠️ 有警告 | 实例可创建，但 config 文件缺失 |
| 消息分类 | ✅ 通过 | 中英文均能正确分类到7种类型 |
| 记忆存储 | ✅ 通过 | `classify_and_remember()` 返回 stored=True |
| 记忆画像 | ✅ 通过 | `get_memory_profile()` 返回正确的统计信息 |
| **记忆召回（中文）** | ❌ **失败** | **中文查询全部返回0结果** |
| 记忆召回（英文） | ✅ 通过 | 英文关键词可正确召回 |
| MCP Server 导入 | ⚠️ 部分可用 | 可导入 MCPServer + 12个工具，但导出名与文档不一致 |
| API 文档一致性 | ❌ 不一致 | README 声明的方法在实际代码中不存在 |

**总体评估：核心功能（分类+存储）可用，但召回功能对中文存在严重缺陷，无法在生产环境使用。**

---

## 二、问题清单

### BUG-1: 中文召回全部返回空 [严重程度: 🔴 P0]

**现象**：

```
存储: cm.classify_and_remember("我偏好使用Python开发") → stored=True ✅
召回: cm.recall_memories("偏好")          → found=0 ❌
召回: cm.recall_memories("偏好使用Python") → found=0 ❌
召回: cm.recall_memories("偏")             → found=0 ❌
召回: cm.recall_memories("使用")           → found=0 ❌
召回: cm.recall_memories("Python")         → found=1 ✅  ← 同一条消息的英文部分能命中
```

**影响**：TRAE 是中文用户为主的环境，90%以上的对话是中文。如果中文召回不工作，整个记忆系统等于废的。

**复现步骤**：
```python
from memory_classification_engine.carrymem import CarryMem
cm = CarryMem()
cm.classify_and_remember("我偏好使用PostgreSQL作为数据库")
results = cm.recall_memories("偏好")  # 返回 []
results = cm.recall_memories("PostgreSQL")  # 能返回结果
```

**推测原因**：
- recall 的检索逻辑可能基于英文 tokenization（如 split() 或正则 `\w+`），中文 CJK 字符未被正确切分为检索词
- 或者 SQLite 的 FTS/LIKE 匹配对中文支持有问题
- adapter 类型确认为 `SQLiteAdapter`，数据确实写入了 `_memories` 字典

**建议修复方向**：
1. 检查 `recall_memories()` 内部的文本匹配逻辑，确认是否处理了 CJK 字符
2. 如果使用 SQLite FTS，确认启用了合适的 tokenizer（如 unicode61 或 jieba）
3. 至少应支持简单的 `content LIKE '%关键词%'` 作为 fallback

---

### BUG-2: README API 文档与实际代码不一致 [严重程度: 🟡 P1]

**README 声明的 API vs 实际代码**:

| README 写法 | 实际代码 | 状态 |
|-------------|---------|------|
| `cm.declare_preference(key, value)` | `cm.declare()` | ❌ 方法名不同 |
| `create_mcp_server()` | `MCPServer` 类 | ❌ 导出名不同 |
| `.storage` 属性 | `.adapter` 属性 | ❌ 属性名不同 |
| `memory_type` 在 entry 中有值 | 返回 `'?'` | ⚠️ classify 结果中 type 为空 |

**影响**：按 README 文档集成会直接报错。

**建议**：
- 同步 README 与代码，或提供 `declare_preference` 作为 `declare` 的 alias
- MCP 文档中说明使用 `MCPServer` 类而非 `create_mcp_server()` 函数

---

### WARN-1: 配置文件缺失 [严重程度: 🟡 P1]

**现象**：
```
Error loading config: [Errno 2] No such file or directory: './config/config.yaml'
Error loading rules: [Errno 2] No such file or directory: './config/advanced_rules.json'
```

**影响**：
- CarryMem 使用默认配置运行，可能不是最优行为
- advanced_rules.json 缺失意味着高级分类规则未加载

**建议**：
- 在项目根目录或 `src/` 下提供 `config/config.example.yaml` 和 `config/advanced_rules.example.json`
- 或在初始化时自动生成默认配置文件（首次运行时）

---

### WARN-2: MCP Server 启动方式不明确 [严重程度: 🟢 P2]

**现象**：
- `python -m memory_classification_engine.integration.layer2_mcp` 可以启动（但需要手动 kill）
- 但没有明确的启动参数说明、端口配置、transport 方式（stdio/sse）
- TOOLS 是 dict 格式（`{name: tool_dict}`）而非对象列表，遍历时需注意

**建议**：
- README 中补充 MCP Server 的完整启动示例（含端口、transport、认证等）
- 提供 systemd/docker-compose 的部署模板

---

## 三、通过的测试项

以下功能经验证正常工作：

| 测试 | 输入 | 输出 | 备注 |
|------|------|------|------|
| 分类 - 英文偏好 | "I prefer dark mode" | type=user_preference, conf=0.6 | ✅ |
| 分类 - 中文偏好 | "我偏好使用PostgreSQL" | type=user_preference, conf=0.75 | ✅ |
| 分类 - 决策 | "重要决策: 采用微服务架构" | type=decision, entries=1 | ✅ |
| 分类 - 事实 | "Python 3.12 released" | type=fact, entries=1 | ✅ |
| 分类 - 纠正 | "纠正: 数据库是MySQL不是PG" | type=correction, entries=2 | ✅ |
| 分类 - 情感(无匹配) | "今天心情不错" | entries=0, remember=False | ✅ 正确识别为无需记忆 |
| 存储 | classify_and_remember ×4条 | 全部 stored=True | ✅ |
| Profile | get_memory_profile() | total=4, by_type 正确 | ✅ |
| 英文召回 | "Python", "dark mode" | 分别找到1条 | ✅ |
| MCP导入 | import MCPServer, TOOLS | 成功, 12个工具 | ✅ |

---

## 四、TRAE 集成路线图（待 BUG-1 修复后）

### Phase 1: MCP Server 接入（预计 30 分钟）

```json
// .trae/mcp.json 新增:
{
  "carrymem": {
    "command": "python3",
    "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
    "cwd": "/Users/lin/trae_projects/carrymem"
  }
}
```

### Phase 2: self_improving_agent.py 集成

每轮对话后自动调用 `classify_and_remember()` 存储关键信息。

### Phase 3: DevSquad MemoryBridge 联动

让 Claw 桥接数据也经过 CarryMem 分类后再存储。

---

## 五、测试环境详情

```
OS: macOS
Python: TraeAI virtualenv (Trae IDE 内置)
CarryMem: v0.3.0 (pip install -e .)
依赖状态: mcp, pyyaml, python-dateutil 已安装
数据存储: SQLiteAdapter (内存模式, 未持久化到磁盘)
测试时间: 2026-04-18
```

---

*本报告由 TRAE Self Improvement 项目组生成*
*请 CarryMem 项目组优先处理 BUG-1（中文召回）和 BUG-2（API 文档一致性）*
