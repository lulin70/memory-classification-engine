# MCE Installation Guide v2

*Memory Classification Engine — Installation, Configuration, and Troubleshooting*

**Version**: 0.2.0 | **Last Updated**: 2026-04-18 | **Status**: Production Ready

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Quick Install](#2-quick-install)
3. [From Source](#3-from-source)
4. [MCP Server Setup](#4-mcp-server-setup)
5. [Configuration Guide](#5-configuration-guide)
6. [Verification Checklist](#6-verification-checklist)
7. [Troubleshooting](#7-troubleshooting)
8. [Next Steps](#8-next-steps)

---

## 1. Prerequisites

### System Requirements

| Requirement | Minimum | Recommended | Tested |
|-------------|---------|-------------|--------|
| Python | **3.9+** | 3.9+, 3.10+, 3.11+, 3.12+ | 3.9.6 (macOS), 3.10+ (Linux) |
| OS | macOS 10.15+, Ubuntu 18.04+, Windows 10+ | Any with Python 3.8+ | macOS (Apple Silicon), Ubuntu 22.04 |
| RAM | 256 MB available | 512 MB+ | <100MB typical usage |
| Disk | 50 MB free | 200 MB+ | ~30 MB for core install |

### Python Dependencies (Core)

These are installed automatically with `pip install`:

| Package | Version | Purpose |
|--------|---------|---------|
| PyYAML | >=5.1 | Rule configuration parsing |
| `typing-extensions` | >=4.0 | Type hints (Python <3.10) |

### Optional Dependencies

| Package | Purpose | Install Command |
|---------|---------|----------------|
| `scikit-learn` | **Recommended** — Vector encoding optimization for semantic similarity calculations | `pip install scikit-learn` |
| `faiss-cpu` or `faiss-gpu` | FAISS vector index acceleration (Tier 3) | `pip install faiss-cpu` |
| `networkx` | Knowledge graph operations (Tier 4) | `pip install networkx` |
| `zhipuai` | ZhipuAI GLM LLM backend (Layer 3) | `pip install zhipuai` |
| `openai` | OpenAI API backend (Layer 3 alternative) | `pip install openai` |
| `flask` / `fastapi` | REST API server | `pip install -e ".[api]"` |
| `pytest` | Running test suite | `pip install -e ".[testing]"` |

> **Note on scikit-learn**: Strongly recommended. Without it, the confidence estimation in distillation mode falls back to a default value (0.85) when cosine similarity calculation encounters errors. With it, you get accurate embedding-based similarity scores.

---

## 2. Quick Install

### 2.1 Core Installation (Minimum)

```bash
pip install memory-classification-engine
```

This installs:
- Core classification engine (three-layer pipeline)
- Four-tier storage (T1-T4)
- Rule matcher + pattern analyzer
- SmartCache with warmup
- Basic CLI tools

**Verification**:

```bash
python -c "from memory_classification_engine import MemoryClassificationEngine; e = MemoryClassificationEngine(); print('✅ MCE loaded successfully')"
```

Expected output: `✅ MCE loaded successfully`

### 2.2 Full Installation (All Features)

```bash
pip install -e ".[api],[llm]"  # Or clone and install from source
pip install scikit-learn       # Recommended for vector optimization
```

### 2.3 Development Installation

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd memory-classification-engine
pip install -e ".[testing]"  # Or: pip install -e ".[api],[llm],[testing]"
pytest  # Should show: 874 passed in ~10 min
```

---

## 3. From Source

### 3.1 Clone and Setup

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd memory-classification-engine

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Verify
python -m pytest tests/ -q  # Quick test run (should pass 874 tests)
```

### 3.2 Project Structure After Install

```
memory-classification-engine/
├── src/memory_classification_engine/   # Core package
├── mce-mcp/                           # MCP Server
├── config/rules.yaml                  # Classification rules (editable)
├── data/                              # Runtime data (auto-created)
├── benchmarks/                        # Performance tools
├── examples/                          # Usage examples
└── tests/                             # Test suite (874 tests)
```

---

## 4. MCP Server Setup

MCE ships with a built-in MCP Server (**Production v1.0.0**, Protocol: 2024-11-05).

### 4.1 For Claude Code

**Step 1**: Start the MCP server (stdio transport for Claude Code/Cursor)

```bash
# Option A: Module mode (recommended — works from anywhere)
python3 -m memory_classification_engine.integration.layer2_mcp

# Option B: Direct path (if running from project root)
python3 src/memory_classification_engine/integration/layer2_mcp/server.py
```

Expected output:
```
MCP Server initialized
Version: 1.0.0 (Production)
Protocol: 2024-11-05
Ready (stdio transport)
```

**Step 2**: Configure Claude Code

Create or edit `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "mce": {
      "command": "python3",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"]
    }
  }
}
```

> **Note**: Use `-m` module mode (Option A above). This works regardless of your current directory.

**Step 3**: Verify in Claude Code

Open Claude Code and type `/mcp`. You should see `mce` listed with 11 available tools.

### 4.2 For Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mce": {
    "command": "python3",
    "args": ["-m", "memory_classification_engine.integration.layer2_mcp"]
  }
}
```

### 4.3 For OpenClaw

Configuration template is available at `mce-mcp/config/` (see `advanced_rules.json` for reference format). OpenClaw-specific config coming in v0.3.0.

---

## 5. Configuration Guide

### 5.1 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCE_LLM_API_KEY` | None | API key for LLM backend (ZhipuAI/OpenAI) |
| `MCE_LLM_ENABLED` | `false` | Enable Layer 3 semantic classification |
| `MCE_LLM_PROVIDER` | `zhipuai` | LLM provider: `zhipuai`, `openai`, `ollama` |
| `MCE_DATA_PATH` | `./data` | Base directory for storage files |
| `MCE_LOG_LEVEL` | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |
| `MCE_CACHE_SIZE` | `1000` | Maximum cache entries |
| `MCE_CACHE_TTL` | `3600` | Cache TTL in seconds |

Example:

```bash
export MCE_LLM_ENABLED=true
export MCE_LLM_API_KEY="your-api-key-here"
export MCE_LOG_LEVEL=DEBUG
```

### 5.2 config.yaml Reference

Main configuration file is at `config/rules.yaml`. Key sections:

```yaml
# Classification rules (Layer 1)
rules:
  - pattern: "remember.*prefer"
    type: user_preference
    confidence: 0.95
    tier: 2
    
  - pattern: "too complex.*simpler"
    type: correction
    confidence: 0.85
    tier: 3

# Memory settings
memory:
  forgetting:
    min_weight: 0.1
    decay_rate: 0.05
  archive_threshold: 30  # days
  
# Storage paths
storage:
  tier2_path: ./data/tier2
  tier3_path: ./data/tier3
  tier4_path: ./data/tier4

# Feedback loop (v2.0)
feedback_loop:
  enabled: true
  auto_apply_threshold: 0.8
  min_pattern_occurrences: 3

# Distillation (v2.0)
distillation:
  enabled: false
  high_confidence_threshold: 0.85
  low_confidence_threshold: 0.50
```

### 5.3 Neo4j Setup (Optional — Tier 4 Knowledge Graph)

If you want persistent knowledge graph storage:

```bash
# Install Neo4j (Docker recommended)
docker run --name neo4j -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Set environment variable
export MCE_NEO4J_URI=bolt://localhost:7687
export MCE_NEO4J_USER=neo4j
export MCE_NEO4J_PASSWORD=password
```

If Neo4j is not available, MCE automatically falls back to in-memory NetworkX graph (fully functional, non-persistent across restarts).

### 5.4 Obsidian Integration (Optional)

Set the vault path in config or environment variable:

```bash
export MCE_OBSIDIAN_VAULT=/path/to/your/obsidian/vault
```

Memories tagged as `fact_declaration` or `decision` will be synced to your Obsidian vault as daily notes.

---

## 6. Verification Checklist

Run through this checklist after installation to confirm everything works:

### Core Functionality

- [ ] **Import test**: `python -c "from memory_classification_engine import MemoryClassificationEngine; print('OK')"` → prints `OK`
- [ ] **Engine init**: `MemoryClassificationEngine()` initializes without error (< 2 seconds)
- [ ] **Process message**: `engine.process_message("I prefer spaces over tabs")` returns dict with `matches` list containing classified memories
- [ ] **Retrieve memories**: `engine.retrieve_memories("code style", limit=3)` returns list (not empty after storing some)
- [ ] **Compact mode**: `engine.retrieve_memories("test", retrieval_mode='compact')` returns within 20ms
- [ ] **Balanced mode**: `engine.retrieve_memories("test", retrieval_mode='balanced')` returns results
- [ ] **Stats**: `engine.get_stats()` returns dict with keys: `working_memory_size`, `storage`, `memory`, `cache`

### MCP Server (if installed)

- [ ] Server starts without error: `python3 -m memory_classification_engine.integration.layer2_mcp`
- [ ] Version shows `1.0.0` in startup output
- [ ] Protocol version shows `2024-11-05`
- [ ] Tools are visible in Claude Code/Cursor (`/mcp` command)

### Advanced Features (if dependencies installed)

- [ ] **Feedback loop**: `engine.process_feedback(mem_id, {"type": "wrong_type", "correct_type": "decision"})` runs without error
- [ ] **Distillation**: `from memory_classification_engine.layers.distillation import DistillationRouter` imports successfully
- [ ] **FAISS Tier 3**: No dimension mismatch warnings during vector operations

### Test Suite

- [ ] **Full test run**: `pytest tests/ -q` → **874 passed, 0 failed**
- [ ] **Thread safety**: Tests involving concurrent get/store/delete pass (added in D-1.1)

---

## 7. Troubleshooting

### 7.1 Installation Issues

#### Issue: `ModuleNotFoundError: No module named 'yaml'`

**Cause**: PyYAML not installed.

**Fix**:
```bash
pip install pyyaml
# Or reinstall the package:
pip install --force-reinstall memory-classification-engine
```

#### Issue: `ImportError: cannot import name 'MemoryClassificationEngine'`

**Cause**: Package not installed or wrong Python environment.

**Fix**:
```bash
# Check which python is being used
which python3
python3 --version

# Ensure you're in the right venv (if using one)
which pip
pip show memory-classification-engine

# Reinstall if needed
pip install -e .
```

#### Issue: `Permission denied` during pip install

**Fix**:
```bash
# Option 1: Use --user flag
pip install --user memory-classification-engine

# Option 2: Use virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install memory-classification-engine
```

#### Issue: `scikit-learn` import error in distillation module

**Symptom**: `ModuleNotFoundError: No module named 'sklearn'` or `ImportError: cannot import name 'cosine_similarity'`

**Cause**: scikit-learn not installed (optional but recommended).

**Fix**:
```bash
pip install scikit-learn
# Verify
python -c "from sklearn.metrics.pairwise import cosine_similarity; print('OK')"
```

**Impact without fix**: Confidence estimation in distillation mode defaults to 0.85 (medium confidence) instead of computing actual similarity. Core functionality unaffected.

#### Issue: `FAISS not found` warning at startup

**Symptom**: Log message `FAISS library not found, using fallback vector store`

**Cause**: FAISS is optional. This is expected behavior.

**Fix**: No action needed for basic use. For production workloads with large memory counts (>10k):
```bash
pip install faiss-cpu  # or faiss-cuda if you have NVIDIA GPU
```

#### Issue: `zhipuai` import error when `MCE_LLM_ENABLED=true`

**Cause**: zhipuai package not installed but Layer 3 LLM is enabled.

**Fix**:
```bash
pip install zhipuai
export MCE_LLM_API_KEY="your-key-here"

# Or disable Layer 3 if not needed:
unset MCE_LLM_ENABLED
# or export MCE_LLM_ENABLED=false
```

### 7.2 Runtime Issues

#### Issue: First query is very slow (>500ms)

**Cause**: Normal behavior on first call. Cache needs to warm up, and indexes need to build.

**Fix**: This is expected. Subsequent queries should be fast (<50ms). The engine automatically warms up 4 hot query patterns during initialization. First-call latency is a one-time cost.

**Verification**: Run the same query twice — second call should be significantly faster.

#### Issue: `Cache warmup fails silently`

**Symptom**: Warning log about warmup, but no cached entries afterward.

**Cause**: Data directory permissions issue, or no stored memories yet to warm up from.

**Fix**:
```bash
# Check data directory exists and is writable
ls -la ./data/
chmod -R u+w ./data/

# Note: Warmup only works if there are existing memories to preload.
# Fresh installations will have empty cache until first process_message() calls.
```

#### Issue: `MCP server starts but tools not showing in Claude Code`

**Cause**: Usually incorrect path in settings.json or transport type mismatch.

**Fix**:
1. **Check path**: Use absolute path, not relative path, in `settings.json`
2. **Check transport**: MCE uses `stdio` transport by default. Make sure no conflicting transport config
3. **Restart Claude Code** after modifying settings.json
4. **Verify server starts cleanly**: Run `python3 mce-mcp/server.py` manually and check for errors

```json
// Correct format (use YOUR actual absolute path):
{
  "mcpServers": {
    "mce": {
      "command": "python3",
      "args": ["/Users/lin/trae_projects/memory-classification-engine/mce-mcp/server.py"]
    }
  }
}
```

#### Issue: `Neo4j connection refused` warnings

**Symptom**: Log messages about failing to connect to localhost:7687

**Cause**: Neo4j is not running. This is **expected and harmless** — MCE auto-falls back to in-memory graph storage.

**Fix**: Either start Neo4j (if you need persistent knowledge graphs) or ignore the warning (in-memory mode works fine for most use cases).

#### Issue: `Obsidian vault path not set or does not exist` warning

**Cause**: `MCE_OBSIDIAN_VAULT` not configured or path doesn't exist.

**Fix**: Set the environment variable or ignore if you don't use Obsidian integration:
```bash
export MCE_OBSIDIAN_VAULT=/path/to/your/vault
# Or just ignore — Obsidian sync is optional
```

### 7.3 Performance Issues

#### Issue: `process_message` takes >1 second

**Normal range**: 100ms – 1500ms depending on complexity and whether Layer 3 (LLM) is triggered.

**If consistently slow (>2s)**:
1. Check if `MCE_LLM_ENABLED=true` — Layer 3 adds LLM latency
2. Check if this is the first call (cache warmup is one-time)
3. Check system resources (CPU/RAM) — FAISS indexing can be memory-intensive
4. Run benchmark: `python benchmarks/baseline_benchmark.py` to establish baseline

**Optimization tips**:
```python
# Use compact mode for speed-critical lookups
engine.retrieve_memories("keyword", retrieval_mode='compact')  # <10ms

# Individual calls are fine for typical workloads (<100 msgs/day)
for msg in messages:
    engine.process_message(msg)
```

#### Issue: Memory usage growing over time

**Cause**: Working memory cache grows with usage. MCE has built-in memory management that triggers cleanup.

**Automatic handling**: MCE's `MemoryMonitor` thread:
- Monitors memory usage every 30 seconds
- Triggers garbage collection when usage >80%
- Aggressively reduces cache size when >90%
- Logs performance alerts

**Manual intervention** (if needed):
```python
engine.optimize_system()  # Force optimization
engine.compress_memories(tenant_id="default", force=True)  # Aggressive compression for specific tenant
```

#### Issue: High disk usage (92%+ warnings)

**Cause**: Tier 3 SQLite databases and vector indices grow over time.

**Fix**:
```python
# Run full optimization (GC + cache reduction + compression)
engine.optimize_system()
```

> **Note**: MCE has automatic memory management (monitor thread at 80%/90% thresholds). Manual optimization is rarely needed.

Also consider: `rm -rf data/*.db && rm -rf data/*-journal` to reset storage (loses all stored memories).

### 7.4 Test Failures

#### Issue: `NameError: name 'start_time' is not defined` in retrieve_memories

**Cause**: This was a bug in `_retrieve_balanced` method where `start_time` was referenced before being defined.

**Status**: **Fixed in D-1.4**. If you see this, update to latest version:
```bash
pip install --upgrade memory-classification-engine
# or if from source:
git pull && pip install -e .
```

#### Issue: Concurrent access errors under MCP multi-request scenarios

**Symptom**: Intermittent `KeyError` or stale data in `get_memory()` results.

**Status**: **Fixed in D-1.1**. All index operations are now protected by `threading.RLock`. If using an older version, upgrade.

---

## 8. Next Steps

After successful installation and verification:

1. **Read the blog post**: [Why Your Agent Needs Professional Memory Classification](./blog/why-your-agent-needs-professional-memory-classification.md)
2. **Try the quick example**: See `examples/basic_usage.py` or `examples/complete_example.py`
3. **Configure MCP for your editor**: Follow Section 4 for Claude Code / Cursor setup
4. **Explore adaptive modes**: Try all three `retrieval_mode` options with your data
5. **Check the API reference**: See [API_REFERENCE_V1.md](../api/API_REFERENCE_V1.md) for complete SDK/MCP/REST documentation
6. **Run the benchmark**: `python benchmarks/baseline_benchmark.py` to measure performance on your hardware

### Getting Help

- **Issues**: [github.com/lulin70/memory-classification-engine/issues](https://github.com/lulin70/memory-classification-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/lulin70/memory-classification-engine/discussions)
- **Documentation**: See `docs/` folder for architecture, design, testing, and user guides

---

**Document Version**: 0.2.0
**Last Updated**: 2026-04-18
**Tested Against**: MCE v0.2.0 (874 tests passing, 0 failures, Demo 26/30 = 87%)
