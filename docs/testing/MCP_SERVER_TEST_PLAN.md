# MCP Server 测试计划

## 更新履历

| 版本 | 日期 | 更新人 | 更新内容 | 审核状态 |
|------|------|--------|----------|----------|
| v1.0.0 | 2026-04-11 | 测试团队 | 初始版本 - MCP Server 发布前测试计划 | 待审核 |

---

## 1. 测试目标

确保 MCP Server 在发布前达到生产环境可用标准：

- ✅ 所有 8 个 Tools 功能正确
- ✅ MCP 协议兼容性 100%
- ✅ 与 Claude Code / Cursor 兼容
- ✅ 性能满足承诺指标
- ✅ 错误处理完善
- ✅ 文档准确完整

---

## 2. 测试范围

### 2.1 测试对象

| 组件 | 文件路径 | 测试重点 |
|------|---------|---------|
| MCP Server | `integration/layer2_mcp/server.py` | 协议实现、生命周期管理 |
| Tools | `integration/layer2_mcp/tools.py` | 8个Tools定义、参数验证 |
| Handlers | `integration/layer2_mcp/handlers.py` | 业务逻辑、错误处理 |
| 配置 | `config/mcp_config.json` | 配置示例正确性 |

### 2.2 测试类型

```
┌─────────────────────────────────────────────────────────┐
│                    测试金字塔                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           E2E 测试 (5%)                         │   │
│  │  • Claude Code 集成测试                         │   │
│  │  • Cursor 集成测试                              │   │
│  │  • 真实场景测试                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                      ▲                                  │
│  ┌───────────────────┴─────────────────────────────┐   │
│  │           集成测试 (20%)                        │   │
│  │  • MCP 协议兼容性测试                           │   │
│  │  • 工具调用流程测试                             │   │
│  │  • 错误场景测试                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                      ▲                                  │
│  ┌───────────────────┴─────────────────────────────┐   │
│  │           单元测试 (75%)                        │   │
│  │  • Tools 定义测试                               │   │
│  │  • Handlers 逻辑测试                            │   │
│  │  • Server 方法测试                              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 测试环境

### 3.1 硬件环境

| 环境 | 配置 | 用途 |
|------|------|------|
| 开发机 | MacBook Pro M3, 16GB RAM | 开发和单元测试 |
| 测试机 | Ubuntu 22.04, 8GB RAM | 集成测试和性能测试 |
| CI 环境 | GitHub Actions | 自动化测试 |

### 3.2 软件环境

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.9, 3.10, 3.11, 3.12 | 多版本兼容测试 |
| Claude Desktop | 最新版 | MCP 客户端测试 |
| Cursor | 最新版 | MCP 客户端测试 |
| pytest | 8.x | 测试框架 |
| pytest-asyncio | 0.23.x | 异步测试支持 |

### 3.3 测试数据

```python
# test_fixtures.py
TEST_MESSAGES = [
    # 用户偏好
    {"message": "我喜欢使用双引号而不是单引号", "expected_type": "user_preference"},
    {"message": "记住，我更喜欢简洁的代码", "expected_type": "user_preference"},
    
    # 纠正信号
    {"message": "上次那个方案太复杂了，我们换个简单点的", "expected_type": "correction"},
    {"message": "不对，应该是用 POST 而不是 GET", "expected_type": "correction"},
    
    # 事实声明
    {"message": "Python 3.12 发布了新的类型推断功能", "expected_type": "fact_declaration"},
    
    # 决策记录
    {"message": "我们决定使用 PostgreSQL 而不是 MySQL", "expected_type": "decision"},
    
    # 关系信息
    {"message": "张三负责后端，李四做前端", "expected_type": "relationship"},
    
    # 任务模式
    {"message": "每次提交代码前都要跑测试", "expected_type": "task_pattern"},
    
    # 情感标记
    {"message": "每次部署都要手动操作，太繁琐了", "expected_type": "sentiment_marker"},
    
    # 非记忆内容
    {"message": "你好", "expected_type": None},
    {"message": "谢谢", "expected_type": None},
]
```

---

## 4. 测试用例

### 4.1 单元测试

#### 4.1.1 Tools 定义测试

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-001 | 验证所有Tools定义 | 检查 TOOLS 列表 | 包含8个Tool定义 | P0 |
| TC-002 | 验证Tool名称唯一性 | 检查 name 字段 | 无重复名称 | P0 |
| TC-003 | 验证Tool Schema完整性 | 检查每个Tool的 inputSchema | 包含 type, properties, required | P0 |
| TC-004 | 验证参数类型定义 | 检查各参数类型 | string/integer/number/array/object 正确 | P0 |
| TC-005 | 验证枚举值定义 | 检查 enum 字段 | memory_type, tier 等枚举值完整 | P0 |
| TC-006 | 验证参数范围限制 | 检查 minimum/maximum | limit, threshold 等范围正确 | P1 |

#### 4.1.2 参数验证测试

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-007 | 验证必填参数检查 | 传入缺少必填参数的请求 | 返回错误：Missing required field | P0 |
| TC-008 | 验证参数类型检查 | 传入错误类型的参数 | 返回错误：must be a string/integer | P0 |
| TC-009 | 验证枚举值检查 | 传入无效的枚举值 | 返回错误：must be one of | P0 |
| TC-010 | 验证数值范围检查 | 传入超出范围的数值 | 返回错误：must be >= / <= | P1 |
| TC-011 | 验证未知参数检查 | 传入未定义的参数 | 返回错误：Unknown field | P1 |
| TC-012 | 验证有效参数 | 传入完全正确的参数 | 验证通过，无错误 | P0 |

#### 4.1.3 Handlers 逻辑测试

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-013 | classify_memory 正常流程 | 传入有效消息 | 返回 matched, memory_type, confidence | P0 |
| TC-014 | classify_memory 无匹配 | 传入无记忆价值的消息 | 返回 matched: false | P0 |
| TC-015 | store_memory 正常流程 | 传入有效记忆数据 | 返回 memory_id, stored: true | P0 |
| TC-016 | retrieve_memories 正常流程 | 传入查询关键词 | 返回 memories 列表 | P0 |
| TC-017 | retrieve_memories 空结果 | 传入无匹配的关键词 | 返回空列表 | P0 |
| TC-018 | get_memory_stats 正常流程 | 请求统计信息 | 返回 total_memories, by_tier 等 | P0 |
| TC-019 | batch_classify 正常流程 | 传入多条消息 | 返回所有消息的分类结果 | P0 |
| TC-020 | find_similar 正常流程 | 传入参考内容 | 返回相似记忆列表 | P0 |
| TC-021 | export_memories 正常流程 | 请求导出 | 返回指定格式的数据 | P1 |
| TC-022 | import_memories 正常流程 | 传入有效数据 | 返回 imported_count | P1 |

#### 4.1.4 Server 方法测试

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-023 | initialize 请求处理 | 发送 initialize 请求 | 返回正确的协议版本和 serverInfo | P0 |
| TC-024 | tools/list 请求处理 | 发送 tools/list 请求 | 返回8个Tool定义 | P0 |
| TC-025 | tools/call 请求处理 | 发送 tools/call 请求 | 调用对应 handler 并返回结果 | P0 |
| TC-026 | shutdown 请求处理 | 发送 shutdown 请求 | 返回 null result | P0 |
| TC-027 | 未知方法处理 | 发送未知方法请求 | 返回 error: Method not found | P0 |
| TC-028 | JSON解析错误处理 | 发送无效JSON | 返回 error: Parse error | P0 |

### 4.2 集成测试

#### 4.2.1 MCP 协议兼容性测试

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-029 | 协议版本协商 | 发送 initialize 请求 | 返回 protocolVersion: 2024-11-05 | P0 |
| TC-030 | 生命周期管理 | initialize → tools/list → shutdown | 每个步骤都正确响应 | P0 |
| TC-031 | JSON-RPC 格式验证 | 检查所有响应格式 | 符合 JSON-RPC 2.0 规范 | P0 |
| TC-032 | 错误码规范 | 触发各种错误场景 | 返回正确的 JSON-RPC 错误码 | P0 |
| TC-033 | 通知处理 | 发送 initialized 通知 | 无响应（通知不返回结果） | P1 |
| TC-034 | 批量请求处理 | 发送多个请求 | 每个请求都有对应响应 | P1 |

#### 4.2.2 工具调用流程测试

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-035 | 完整分类流程 | 发送消息 → classify_memory | 返回正确的分类结果 | P0 |
| TC-036 | 存储-检索流程 | store_memory → retrieve_memories | 能检索到刚存储的记忆 | P0 |
| TC-037 | 批量分类流程 | batch_classify 多条消息 | 返回所有消息的分类结果 | P0 |
| TC-038 | 相似度查找流程 | store_memory → find_similar | 能找到相似的记忆 | P0 |
| TC-039 | 导出-导入流程 | export_memories → import_memories | 数据完整导入 | P1 |
| TC-040 | 统计信息流程 | 多次操作 → get_memory_stats | 统计数据正确更新 | P1 |

#### 4.2.3 错误场景测试

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-041 | 无效Tool名称 | 调用不存在的Tool | 返回错误：Unknown tool | P0 |
| TC-042 | 无效参数格式 | 传入格式错误的参数 | 返回参数验证错误 | P0 |
| TC-043 | 引擎初始化失败 | 配置错误导致引擎失败 | 返回友好的错误信息 | P0 |
| TC-044 | 存储服务异常 | 模拟存储服务失败 | 返回错误，不崩溃 | P0 |
| TC-045 | 网络超时（如适用） | 模拟超时场景 | 返回超时错误 | P1 |
| TC-046 | 并发请求处理 | 同时发送多个请求 | 所有请求都正确处理 | P1 |

### 4.3 兼容性测试

#### 4.3.1 Claude Code 兼容性

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-047 | Claude Code 初始化 | 配置到 Claude Code 并启动 | 正常初始化，无错误 | P0 |
| TC-048 | Claude Code 工具发现 | 在 Claude Code 中查看可用工具 | 显示所有8个工具 | P0 |
| TC-049 | Claude Code classify_memory | 在对话中触发分类 | 正确分类并返回结果 | P0 |
| TC-050 | Claude Code store_memory | 在对话中存储记忆 | 成功存储 | P0 |
| TC-051 | Claude Code retrieve_memories | 在对话中检索记忆 | 返回相关记忆 | P0 |
| TC-052 | Claude Code 长对话测试 | 进行10+轮对话 | 记忆持续有效 | P0 |

#### 4.3.2 Cursor 兼容性

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-053 | Cursor 初始化 | 配置到 Cursor 并启动 | 正常初始化，无错误 | P0 |
| TC-054 | Cursor 工具发现 | 在 Cursor 中查看可用工具 | 显示所有8个工具 | P0 |
| TC-055 | Cursor 工具调用 | 在对话中调用工具 | 正确执行并返回结果 | P0 |

#### 4.3.3 Python 版本兼容性

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-056 | Python 3.9 测试 | 在 Python 3.9 环境运行 | 所有测试通过 | P0 |
| TC-057 | Python 3.10 测试 | 在 Python 3.10 环境运行 | 所有测试通过 | P0 |
| TC-058 | Python 3.11 测试 | 在 Python 3.11 环境运行 | 所有测试通过 | P0 |
| TC-059 | Python 3.12 测试 | 在 Python 3.12 环境运行 | 所有测试通过 | P0 |

### 4.4 性能测试

| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|--------|
| TC-060 | 单条消息处理延迟 | 测量 classify_memory 耗时 | < 10ms (Layer 1/2) | P1 |
| TC-061 | 检索延迟 | 测量 retrieve_memories 耗时 | < 15ms | P1 |
| TC-062 | 并发处理 | 100并发请求 | 无错误，响应时间可接受 | P1 |
| TC-063 | 内存占用 | 长时间运行监控 | < 100MB | P1 |
| TC-064 | 批量处理性能 | batch_classify 100条消息 | 处理时间 < 1s | P2 |

---

## 5. 测试执行计划

### 5.1 测试阶段

```
Week 1: 单元测试执行
├─ Day 1-2: Tools 定义测试
├─ Day 3-4: 参数验证测试
├─ Day 5: Handlers 逻辑测试
└─ Day 6-7: Server 方法测试

Week 2: 集成测试执行
├─ Day 1-2: MCP 协议兼容性测试
├─ Day 3-4: 工具调用流程测试
└─ Day 5-7: 错误场景测试

Week 3: 兼容性测试执行
├─ Day 1-3: Claude Code 兼容性测试
├─ Day 4-5: Cursor 兼容性测试
└─ Day 6-7: Python 版本兼容性测试

Week 4: 性能测试 + 修复 + 回归
├─ Day 1-2: 性能测试
├─ Day 3-5: Bug 修复
└─ Day 6-7: 回归测试
```

### 5.2 测试通过标准

| 指标 | 目标值 | 最低可接受值 |
|------|--------|-------------|
| 单元测试通过率 | 100% | 100% |
| 集成测试通过率 | 100% | 95% |
| 兼容性测试通过率 | 100% | 90% |
| 代码覆盖率 | > 80% | > 70% |
| 性能指标达成 | 100% | 80% |
| 严重缺陷数 | 0 | 0 |
| 中等缺陷数 | 0 | < 3 |

### 5.3 测试环境准备清单

- [ ] Python 3.9, 3.10, 3.11, 3.12 环境
- [ ] Claude Desktop 安装并配置
- [ ] Cursor 安装并配置
- [ ] 测试数据准备完成
- [ ] 测试脚本准备完成
- [ ] CI/CD 流水线配置完成

---

## 6. 测试工具

### 6.1 自动化测试

```python
# pytest 配置
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=memory_classification_engine
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    compatibility: Compatibility tests
    performance: Performance tests
    slow: Slow tests
```

### 6.2 手动测试脚本

```bash
#!/bin/bash
# manual_test.sh - 手动测试脚本

echo "=== MCP Server 手动测试 ==="

# 1. 启动 MCP Server
echo "1. 启动 MCP Server..."
python -m memory_classification_engine mcp &
SERVER_PID=$!
sleep 2

# 2. 发送 initialize 请求
echo "2. 发送 initialize 请求..."
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"test","version":"1.0"}}}' | python -m memory_classification_engine mcp

# 3. 发送 tools/list 请求
echo "3. 发送 tools/list 请求..."
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | python -m memory_classification_engine mcp

# 4. 发送 tools/call 请求
echo "4. 发送 tools/call 请求..."
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"classify_memory","arguments":{"message":"我喜欢使用双引号"}}}' | python -m memory_classification_engine mcp

# 5. 关闭 Server
kill $SERVER_PID

echo "=== 测试完成 ==="
```

### 6.3 性能测试脚本

```python
# performance_test.py
import time
import asyncio
import statistics
from memory_classification_engine.integration.layer2_mcp.handlers import Handlers

async def benchmark_classify():
    """Benchmark classify_memory handler."""
    handlers = Handlers()
    
    latencies = []
    for _ in range(100):
        start = time.time()
        await handlers.handle_classify_memory({"message": "我喜欢使用双引号"})
        latencies.append((time.time() - start) * 1000)  # Convert to ms
    
    print(f"Average latency: {statistics.mean(latencies):.2f}ms")
    print(f"P95 latency: {sorted(latencies)[int(len(latencies)*0.95)]:.2f}ms")
    print(f"P99 latency: {sorted(latencies)[int(len(latencies)*0.99)]:.2f}ms")

if __name__ == "__main__":
    asyncio.run(benchmark_classify())
```

---

## 7. 缺陷管理

### 7.1 缺陷分级

| 级别 | 定义 | 示例 | 修复时限 |
|------|------|------|---------|
| P0 (严重) | 导致系统崩溃或主要功能不可用 | Server 启动失败、Tool 调用崩溃 | 立即 |
| P1 (高) | 主要功能受影响，有 workaround | 性能不达标、兼容性 issue | 24小时 |
| P2 (中) | 次要功能受影响 | 文档错误、日志不完善 | 本周 |
| P3 (低) | 轻微问题 | 代码风格、注释缺失 | 下次迭代 |

### 7.2 缺陷跟踪

使用 GitHub Issues 跟踪缺陷：
- 标签: `bug`, `mcp-server`, `p0/p1/p2/p3`
- 里程碑: `MCP Server Release`
- 指派: 相关开发人员

---

## 8. 测试报告模板

### 8.1 日报模板

```markdown
# MCP Server 测试日报 - YYYY-MM-DD

## 今日完成
- [ ] 测试用例 TC-001 ~ TC-010
- [ ] 发现缺陷: #123, #124

## 测试统计
- 执行用例: 10
- 通过: 8
- 失败: 2
- 阻塞: 0

## 缺陷统计
- 新增: 2
- 修复: 1
- 遗留: 3

## 明日计划
- [ ] 测试用例 TC-011 ~ TC-020
- [ ] 验证缺陷修复

## 风险
- 无
```

### 8.2 最终报告模板

```markdown
# MCP Server 测试报告

## 测试概述
- 测试时间: YYYY-MM-DD ~ YYYY-MM-DD
- 测试人员: XXX
- 测试范围: MCP Server 所有功能

## 测试统计
- 总用例数: 64
- 通过: 60 (93.75%)
- 失败: 2 (3.125%)
- 跳过: 2 (3.125%)

## 缺陷统计
- 严重: 0
- 高: 1
- 中: 2
- 低: 3

## 测试结论
- [ ] 可以发布
- [ ] 需要修复后发布
- [ ] 不能发布

## 建议
- ...
```

---

## 9. 发布检查清单

在发布前必须完成以下检查：

### 9.1 功能检查
- [ ] 所有 8 个 Tools 功能正常
- [ ] MCP 协议兼容性 100%
- [ ] Claude Code 兼容性验证通过
- [ ] Cursor 兼容性验证通过

### 9.2 质量检查
- [ ] 单元测试通过率 100%
- [ ] 集成测试通过率 100%
- [ ] 代码覆盖率 > 80%
- [ ] 无 P0/P1 缺陷遗留

### 9.3 文档检查
- [ ] README 更新完成
- [ ] API 文档准确
- [ ] 配置示例正确
- [ ] 使用说明完整

### 9.4 发布检查
- [ ] 版本号更新
- [ ] CHANGELOG 更新
- [ ] PyPI 包测试通过
- [ ] GitHub Release 准备完成

---

**测试计划版本**: v1.0.0  
**创建日期**: 2026-04-11  
**审核状态**: 待审核  
**计划路径**: `/Users/lin/trae_projects/memory-classification-engine/docs/testing/MCP_SERVER_TEST_PLAN.md`
