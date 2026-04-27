# Phase 3 实施计划: 生态与集成 (v0.7.0)

> **目标**: CarryMem 成为 AI 记忆的标准层
> **版本**: v0.6.0 → v0.7.0
> **制定日期**: 2026-04-26

---

## 一、实施顺序与依赖关系

```
3.4 第三方适配器 SDK (基础设施)
  ↓
3.1 MCP 远程模式 (SSE/HTTP)
  ↓
3.2 更多适配器 (JSON 文件适配器 + 适配器模板)
  ↓
3.3 异步 API (async/await)
  ↓
3.5 Claude Code + Cursor 集成配置
```

---

## 二、3.4 第三方适配器 SDK

### 现状
- `StorageAdapter` ABC 已有 7 个抽象/默认方法
- `AsyncStorageAdapter` Protocol 已定义但无实现
- `TestStorageAdapterContract` 契约测试已存在
- loader.py 只支持同步适配器

### 改进
1. **完善适配器开发文档**: 在 base.py 中增加详细 docstring
2. **适配器注册机制增强**: loader.py 支持异步适配器
3. **适配器模板**: 创建 `adapters/template.py` 作为开发起点
4. **setup.py 入口组**: 增加 `carrymem.async_adapters` 组

---

## 三、3.1 MCP 远程模式 (SSE/HTTP)

### 现状
- 仅支持 stdio 传输
- 手写 MCP 协议实现
- 无 SSE/HTTP 支持

### 设计

使用 Python 标准库 `http.server` + `sseclient` 模式实现轻量级 HTTP/SSE 传输：

```python
class MCPHTTPServer:
    """HTTP+SSE transport for MCP protocol."""

    def __init__(self, host="127.0.0.1", port=8765, carrymem_config=None):
        self._host = host
        self._port = port
        self._handlers = Handlers(carrymem_config)

    async def start(self):
        # 启动 HTTP 服务器
        # GET /sse → SSE 事件流（服务端推送）
        # POST /message → 客户端发送 JSON-RPC 请求

    async def stop(self):
        # 优雅关闭
```

### 启动方式
```bash
# stdio 模式（现有）
python -m memory_classification_engine.integration.layer2_mcp

# HTTP/SSE 模式（新增）
carrymem serve --host 127.0.0.1 --port 8765
```

### 实现位置
- **新文件**: `integration/layer2_mcp/http_server.py`
- **修改**: `cli.py` — 新增 `serve` 命令
- **修改**: `setup.py` — 新增 `carrymem-serve` console_scripts

---

## 四、3.2 更多适配器

### JSON 文件适配器

零依赖的文件系统适配器，适合轻量级场景：

```python
class JSONAdapter(StorageAdapter):
    """JSON file-based storage adapter."""

    def __init__(self, path: str = "~/.carrymem/memories.json", namespace: str = "default"):
        # 每个命名空间一个 JSON 文件
        # 读写整个文件（适合 < 10K 记忆）
```

### 适配器模板

```python
class TemplateAdapter(StorageAdapter):
    """Template for creating custom adapters."""

    def remember(self, entry, _skip_commit=False) -> StoredMemory: ...
    def recall(self, query, filters=None, limit=20) -> List[StoredMemory]: ...
    def forget(self, storage_key) -> bool: ...
    @property
    def name(self) -> str: ...
```

---

## 五、3.3 异步 API

### 设计

为 CarryMem 核心类添加异步方法，以 `a` 前缀命名：

```python
class AsyncCarryMem:
    """Async wrapper around CarryMem."""

    async def classify_and_remember(self, message, context=None, language=None): ...
    async def recall_memories(self, query=None, filters=None, limit=20): ...
    async def forget_memory(self, memory_id): ...
    async def build_context(self, context=None, ...): ...
```

实现方式：使用 `asyncio.get_event_loop().run_in_executor()` 将同步调用包装为异步。

---

## 六、3.5 Claude Code + Cursor 集成

### Claude Code 配置

创建 `.claude/` 目录下的配置文件：

```json
{
  "mcpServers": {
    "carrymem": {
      "command": "python",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
      "env": {}
    }
  }
}
```

### Cursor 配置

创建 `.cursor/` 目录下的 MCP 配置：

```json
{
  "mcpServers": {
    "carrymem": {
      "command": "python",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"]
    }
  }
}
```

### 实现方式
- **新文件**: `integrations/claude_code/` 和 `integrations/cursor/`
- **CLI 命令**: `carrymem init-claude` / `carrymem init-cursor`

---

## 七、文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `integration/layer2_mcp/http_server.py` | 新建 | HTTP/SSE 传输 |
| `adapters/json_adapter.py` | 新建 | JSON 文件适配器 |
| `adapters/template.py` | 新建 | 适配器开发模板 |
| `async_carrymem.py` | 新建 | 异步 API 包装 |
| `integrations/claude_code/mcp.json` | 新建 | Claude Code 配置 |
| `integrations/cursor/mcp.json` | 新建 | Cursor 配置 |
| `cli.py` | 修改 | 新增 serve/init-claude/init-cursor 命令 |
| `loader.py` | 修改 | 支持异步适配器加载 |
| `setup.py` | 修改 | 新增 console_scripts + entry_points |
| `test_v070.py` | 新建 | Phase 3 测试 |
