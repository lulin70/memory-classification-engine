# MCE MCP Server

Memory Classification Engine MCP (Model Context Protocol) Server for Claude Code, Cursor and other MCP-supported tools.

## 📋 Overview

MCE MCP Server provides a standard MCP interface for the Memory Classification Engine, allowing AI agents and tools to:

- Classify messages into memory types
- Retrieve relevant memories
- Manage memory forgetting process
- Search memories with compact index
- Get memory timeline context
- Get full memory details

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install mce-mcp-server

# Or install from source
pip install -e .
```

### Configuration

Create a `config.yaml` file:

```yaml
server:
  host: 0.0.0.0
  port: 8080

logging:
  level: INFO
```

### Start Server

```bash
# Using console script
mce-mcp-server

# Or run directly
python -m mce_mcp_server.server
```

The server will start on `http://localhost:8080`

## 🛠️ Available Tools

### 1. classify_message

Classify a message into memory types.

**Parameters:**
- `message` (required): The message to classify
- `context` (optional): Additional context for classification
- `execution_context` (optional): Execution context with feedback signals

**Example:**
```json
{
  "toolcall": {
    "name": "classify_message",
    "params": {
      "message": "The capital of France is Paris",
      "context": {
        "conversation_id": "conv_123",
        "user_id": "user_456"
      }
    }
  }
}
```

### 2. retrieve_memories

Retrieve memories related to a query.

**Parameters:**
- `query` (required): Search query
- `memory_type` (optional): Filter by memory type
- `limit` (optional): Maximum number of results (default: 10)

**Example:**
```json
{
  "toolcall": {
    "name": "retrieve_memories",
    "params": {
      "query": "capital cities",
      "limit": 5
    }
  }
}
```

### 3. search_memories

Search memories with compact index (~50 tokens per entry).

**Parameters:**
- `query` (required): Search query
- `memory_type` (optional): Filter by memory type
- `limit` (optional): Maximum number of results (default: 20)

**Example:**
```json
{
  "toolcall": {
    "name": "search_memories",
    "params": {
      "query": "Paris",
      "limit": 10
    }
  }
}
```

### 4. get_memory_timeline

Get memory timeline context (~200 tokens per entry).

**Parameters:**
- `memory_ids` (required): List of memory IDs

**Example:**
```json
{
  "toolcall": {
    "name": "get_memory_timeline",
    "params": {
      "memory_ids": ["mem_123", "mem_456"]
    }
  }
}
```

### 5. get_memory_details

Get full memory details (~500 tokens per entry).

**Parameters:**
- `memory_id` (required): Memory ID

**Example:**
```json
{
  "toolcall": {
    "name": "get_memory_details",
    "params": {
      "memory_id": "mem_123"
    }
  }
}
```

### 6. manage_forgetting

Manage memory forgetting process.

**Parameters:**
- `memory_id` (required): Memory ID
- `action` (optional): Action to perform (default: "decrease_weight")
- `weight_adjustment` (optional): Weight adjustment amount (default: 0.1)

**Example:**
```json
{
  "toolcall": {
    "name": "manage_forgetting",
    "params": {
      "memory_id": "mem_123",
      "action": "decrease_weight",
      "weight_adjustment": 0.2
    }
  }
}
```

## 🔧 Integration

### Claude Code

Add to your MCP configuration:

```toml
[mcp.servers.mce]
command = "python3"
args = ["-m", "mce_mcp_server.server"]
enabled = true
required = false
startup_timeout_ms = 30000
tool_timeout_ms = 120000
```

### OpenClaw

Use the provided adapter:

```python
from memory_classification_engine.agents.adapters.openclaw import OpenClawAdapter

adapter = OpenClawAdapter()
result = adapter.process_message("Hello world")
```

## 📊 Performance

- **Response Time**: < 100ms for classification
- **Memory Usage**: ~50MB baseline
- **Scalability**: Handles 100+ requests per second

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License

## 📞 Support

For issues and feature requests, please open an issue on GitHub.

---

**Version**: 1.0.0  
**Last Updated**: 2026-04-14