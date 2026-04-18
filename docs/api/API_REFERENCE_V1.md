# MCE API Reference v1.0

## Document Info

| Item | Content |
|------|---------|
| Version | 1.0.0 |
| Date | 2026-04-17 |
| Status | Production Ready |
| Engine Version | ENGINE_VERSION |

---

## 1. Python SDK API (Direct Engine Usage)

### 1.1 Initialization

```python
from memory_classification_engine import MemoryClassificationEngine

# Initialize engine (auto-warms cache on startup)
engine = MemoryClassificationEngine(config_path=None)
```

**Config Options** (via `config_path` or env):

| Key | Default | Description |
|-----|---------|-------------|
| `memory.limits.cache` | 1000 | SmartCache max entries |
| `memory.cache.ttl` | 3600 | Cache TTL in seconds |
| `cache.warmup.enabled` | True | Auto warmup at startup |
| `memory.forgetting.enabled` | True | Auto-archive low-weight memories |
| `storage.max_work_memory_size` | 100 | Working memory max size |

### 1.2 Core Methods

#### `process_message(message, context=None, execution_context=None) -> Dict`

Classify and store a message into memories.

```python
result = engine.process_message(
    message="I prefer using dark mode for coding",
    context={"user_id": "user_123", "scenario": "coding"}
)

# Returns:
{
    "success": True,
    "message": "I prefer using dark mode for coding",
    "matches": [
        {
            "id": "mem_xxx",
            "memory_type": "user_preference",
            "tier": 3,
            "confidence": 0.85,
            "content": "...",
            ...
        }
    ],
    "classification_time_ms": 45.2,
    "layer_used": 1  # 1=rule, 2=pattern, 3=semantic
}
```

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | str | Yes | User message to classify |
| `context` | dict | No | `{user_id, tenant_id, scenario}` |
| `execution_context` | dict | No | Internal execution metadata |

**Performance**: P50 ~350ms, P99 ~1.6s (after optimization)

---

#### `retrieve_memories(query=None, limit=5, memory_type=None, tenant_id=None, include_associations=False, user_id=None, scenario=None) -> List[Dict]`

Retrieve memories sorted by semantic relevance.

```python
# Basic retrieval
memories = engine.retrieve_memories(query="database", limit=5)

# With type filter
prefs = engine.retrieve_memories(query="preference", memory_type="user_preference", limit=10)

# With associations
memories = engine.retrieve_memories(query="project", limit=5, include_associations=True)
```

**Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | str/None | None | Search query (None = all, sorted by confidence) |
| `limit` | int | 5 | Max results (1-50) |
| `memory_type` | str | None | Filter: user_preference / correction / fact_declaration / decision / relationship / task_pattern / sentiment_marker |
| `tenant_id` | str | None | Tenant filter |
| `include_associations` | bool | False | Include related memories |
| `user_id` | str | None | Access control filter |
| `scenario` | str | None | Scenario validation |

**Returns:** List of memory dicts with `semantic_similarity` score when query is provided.

**Performance:** P50 ~0.01ms (cached), P99 ~50ms (with semantic sort)

---

#### `manage_memory(action, memory_id, data=None, user_id=None) -> Dict`

Manage individual memories (refresh, expire, delete).

```python
# Refresh a memory (increase weight)
result = engine.manage_memory(
    action="refresh",
    memory_id="mem_xxx",
    data={"weight_adjustment": 0.1}
)

# Mark as expired
result = engine.manage_memory(action="mark_expired", memory_id="mem_xxx")
```

**Actions:** `refresh`, `mark_expired`, `delete`

---

#### `get_stats(user_id=None) -> Dict`

Get system statistics.

```python
stats = engine.get_stats()
# Returns:
{
    "total_memories": 347,
    "by_tier": {"tier2": 12, "tier3": 289, "tier4": 46},
    "by_type": {"user_preference": 89, "decision": 67, ...},
    "cache_hit_rate": 97.8,
    "uptime_seconds": 3600,
    "engine_version": "x.y.z"
}
```

---

#### `export_memories(format="json", user_id=None, tenant_id=None, memory_types=None) -> Dict`

Export memories for backup/migration.

```python
result = engine.export_memories(format="json", memory_types=["decision"])
# result["data"] contains exported records
# result["count"] = number exported
```

**Formats:** `json`, `yaml`, `csv`

---

#### `import_memories(data, format="json", user_id=None) -> Dict`

Import memories from backup/external system.

```python
result = engine.import_memories(
    data='[{"content": "...", "memory_type": "decision", ...}]',
    format="json"
)
# result["imported"] = count imported
# result["skipped"] = count skipped (duplicates)
```

---

### 1.3 Advanced Methods

#### `process_message_with_agent(agent_name, message, context=None) -> Dict`

Process message scoped to a specific agent.

```python
result = engine.process_message_with_agent(
    agent_name="coder_agent",
    message="Use TypeScript strict mode",
    context={"task": "code_review"}
)
```

#### `provide_feedback(memory_id, feedback_type, value, comment=None) -> Dict`

Provide quality feedback on a classification.

```python
engine.provide_feedback(
    memory_id="mem_xxx",
    feedback_type="correctness",
    value="positive",
    comment="Classification was accurate"
)
```

**Feedback types:** `correctness`, `relevance`, `completeness`
**Values:** `positive`, `negative`, `neutral`

---

## 2. MCP Server Tools (11 tools)

**Server:** `memory_classification_engine.integration.layer2_mcp.server.MCPServer`
**Protocol:** JSON-RPC over stdio (MCP compliant)
**Start:** `python -m memory_classification_engine.integration.layer2_mcp.server`

### Tool List

| # | Name | Description | Required Params |
|---|------|-------------|----------------|
| 1 | **classify_memory** | Analyze message and classify memory type | `message` |
| 2 | **store_memory** | Store memory to appropriate tier | `content`, `memory_type` |
| 3 | **retrieve_memories** | Search memories by query | `query` |
| 4 | **get_memory_stats** | Get system statistics | (none) |
| 5 | **batch_classify** | Batch classify multiple messages | `messages[]` |
| 6 | **find_similar** | Find similar memories by content | `content` |
| 7 | **export_memories** | Export memories in various formats | (none) |
| 8 | **import_memories** | Import memories from backup | `data` |
| 9 | **mce_recall** | Recall relevant memories for context | (none) |
| 10 | **mce_status** | View memory system status | (none) |
| 11 | **mce_forget** | Manually forget a specific memory | `memory_id` |

### Detailed Tool Schemas

#### `classify_memory`

```json
{
    "name": "classify_memory",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Message to analyze"},
            "context": {"type": "string", "description": "Optional conversation context"}
        },
        "required": ["message"]
    }
}
```

**Example call:**
```json
{"method": "tools/call", "params": {"name": "classify_memory", "arguments": {"message": "Deploy to production server"}}}
```

#### `store_memory`

```json
{
    "name": "store_memory",
    "inputSchema": {
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "memory_type": {
                "type": "string",
                "enum": ["user_preference", "correction", "fact_declaration", "decision", "relationship", "task_pattern", "sentiment_marker"]
            },
            "tier": {"type": "integer", "enum": [2, 3, 4]},
            "context": {"type": "string"}
        },
        "required": ["content", "memory_type"]
    }
}
```

#### `retrieve_memories`

```json
{
    "name": "retrieve_memories",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 5, "minimum": 1, "maximum": 50},
            "tier": {"type": "integer", "enum": [2, 3, 4]}
        },
        "required": ["query"]
    }
}
```

#### `mce_recall` (Context-Aware Recall)

```json
{
    "name": "mce_recall",
    "inputSchema": {
        "type": "object",
        "properties": {
            "context": {"type": "string", "default": "general", "description": "coding / deployment / general"},
            "limit": {"type": "integer", "default": 5, "maximum": 20},
            "types": {"type": "array", "items": {"type": "string"}, "description": "Filter by memory type"},
            "format": {"type": "string", "enum": ["text", "json"], "default": "text"},
            "include_pending": {"type": "boolean", "default": true}
        }
    }
}
```

#### `mce_forget`

```json
{
    "name": "mce_forget",
    "inputSchema": {
        "type": "object",
        "properties": {
            "memory_id": {"type": "string"},
            "reason": {"type": "string"}
        },
        "required": ["memory_id"]
    }
}
```

---

## 3. Memory Types Reference

| Type | Tier | Description | Example |
|------|------|-------------|---------|
| `user_preference` | 2-3 | User preferences and habits | "Prefer dark mode" |
| `correction` | 2-3 | Error corrections | "That approach was wrong" |
| `fact_declaration` | 3 | Factual statements | "API rate limit: 100/min" |
| `decision` | 3 | Decision records | "Chose PostgreSQL over MongoDB" |
| `relationship` | 3-4 | Entity relationships | "Module A depends on B" |
| `task_pattern` | 2 | Recurring task patterns | "Run tests before commit" |
| `sentiment_marker` | 2-3 | Emotional/sentiment markers | User frustration signals |

### Tier System

| Tier | Name | Retention | Speed |
|------|------|-----------|-------|
| 2 | Procedural Memory | Medium-term (working) | Fastest |
| 3 | Episodic Memory | Long-term (episodes) | Fast |
| 4 | Semantic Memory | Permanent (facts) | Slower |

---

## 4. Error Codes

| Code | HTTP/MCP | Meaning |
|------|----------|---------|
| `E001` | 400 | Missing required parameter |
| `E002` | 400 | Invalid parameter value |
| `E003` | 401 | Authentication required |
| `E004` | 403 | Permission denied |
| `E005` | 404 | Memory not found |
| `E006` | 409 | Duplicate memory |
| `E007` | 500 | Classification pipeline error |
| `E008` | 500 | Storage error |
| `E009` | 503 | Service unavailable (initializing) |

---

## 5. Performance Benchmarks (Post-Optimization)

| Operation | P50 | P95 | P99 | Notes |
|-----------|-----|-----|-----|-------|
| `process_message` | 353 ms | 755 ms | 1643 ms | -71% vs baseline |
| `retrieve_memories` (cached) | 0.01 ms | 46 ms | 88 ms | Cache hit ~98% |
| `retrieve_memories` (long_query) | 44 ms | 50 ms | 50 ms | Semantic sort optimized |
| `retrieve_memories` (no_query) | 0.007 ms | 48 ms | 51 ms | Confidence sort |
| Engine init | 520 ms | — | — | Includes warmup |
