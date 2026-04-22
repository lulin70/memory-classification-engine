# CarryMem v0.3 测试计划 (v3.0)

**日期**: 2026-04-22
**版本**: v3.0 (对应 CarryMem v0.3.0)
**参考**: CARRYMEM_ARCHITECTURE_v4.md, CARRYMEM_DESIGN_v4.md

---

## 1. 测试策略

### 1.1 测试文件

统一测试套件: `tests/test_carrymem.py` (32 个测试)

### 1.2 测试分类

| 分类 | 测试类 | 测试数 | 覆盖范围 |
|------|--------|--------|---------|
| 分类核心 | TestClassification | 6 | process_message, to_memory_entry |
| CarryMem 核心 | TestCarryMemCore | 7 | classify_and_remember, recall, forget, stats |
| 主动声明 | TestDeclare | 3 | declare, confidence=1.0, source_layer |
| 记忆画像 | TestMemoryProfile | 2 | get_memory_profile |
| 命名空间 | TestNamespace | 2 | 隔离, 跨 namespace 检索 |
| 智能调度 | TestBuildSystemPrompt | 4 | EN/CN/JP prompt, 无 context |
| 插件加载 | TestPluginLoader | 5 | load_adapter, list_available, string storage |
| SQLite 适配器 | TestSQLiteAdapter | 5 | remember, recall, forget, stats, profile |

---

## 2. 测试用例详情

### 2.1 TestClassification (6 tests)

| ID | 测试用例 | 输入 | 预期 |
|----|---------|------|------|
| C01 | test_preference_classification | "I prefer dark mode" | type=user_preference |
| C02 | test_correction_classification | "No, I said Python not JavaScript" | matches 非空 |
| C03 | test_decision_classification | "Let's use PostgreSQL" | matches 非空 |
| C04 | test_empty_message | "" | matches=[] |
| C05 | test_noise_rejection | "ok" | matches=[] |
| C06 | test_to_memory_entry | "I prefer dark mode" | schema_version=1.0.0, should_remember=True |

### 2.2 TestCarryMemCore (7 tests)

| ID | 测试用例 | 预期 |
|----|---------|------|
| M01 | test_classify_and_remember | stored=True, storage_keys 非空 |
| M02 | test_recall_memories | 返回结果 > 0 |
| M03 | test_forget_memory | deleted=True |
| M04 | test_get_stats | total_count > 0 |
| M05 | test_classify_message_no_storage | should_remember=True |
| M06 | test_storage_not_configured_error | 抛出异常 |
| M07 | test_cross_feature | classify→recall→forget 完整流程 |

### 2.3 TestDeclare (3 tests)

| ID | 测试用例 | 预期 |
|----|---------|------|
| D01 | test_declare_basic | declared=True, source="declaration" |
| D02 | test_declare_confidence_is_1 | confidence=1.0 |
| D03 | test_declare_source_layer | source_layer="declaration" |

### 2.4 TestMemoryProfile (2 tests)

| ID | 测试用例 | 预期 |
|----|---------|------|
| P01 | test_get_memory_profile | total_memories > 0, highlights 非空 |
| P02 | test_profile_no_storage | total_memories=0 |

### 2.5 TestNamespace (2 tests)

| ID | 测试用例 | 预期 |
|----|---------|------|
| N01 | test_namespace_isolation | project-a 只能查到自己的记忆 |
| N02 | test_cross_namespace_recall | 跨 namespace 检索返回结果 |

### 2.6 TestBuildSystemPrompt (4 tests)

| ID | 测试用例 | 预期 |
|----|---------|------|
| S01 | test_english_prompt | 包含 "User Memories" |
| S02 | test_chinese_prompt | 包含 "用户记忆" |
| S03 | test_japanese_prompt | 包含 "ユーザー記憶" |
| S04 | test_prompt_without_context | 包含 "User Memories" |

### 2.7 TestPluginLoader (5 tests)

| ID | 测试用例 | 预期 |
|----|---------|------|
| L01 | test_load_builtin_sqlite | 返回 SQLiteAdapter |
| L02 | test_load_builtin_obsidian | 返回 ObsidianAdapter |
| L03 | test_load_unknown | 返回 None |
| L04 | test_list_available_adapters | 包含 sqlite, obsidian |
| L05 | test_carrymem_with_string_storage | 正常创建实例 |

### 2.8 TestSQLiteAdapter (5 tests)

| ID | 测试用例 | 预期 |
|----|---------|------|
| A01 | test_remember_and_recall | recall 返回结果 |
| A02 | test_forget | deleted=True |
| A03 | test_get_stats | total_count > 0 |
| A04 | test_get_profile | total_memories > 0 |
| A05 | test_content_dedup | 相同内容不重复存储 |

---

## 3. MCE-Bench 基准测试

### 3.1 数据集

| 语言 | 文件 | 用例数 |
|------|------|--------|
| English | benchmarks/dataset/en.json | 60 |
| Chinese | benchmarks/dataset/zh.json | 60 |
| Japanese | benchmarks/dataset/ja.json | 60 |
| **Total** | | **180** |

### 3.2 运行方式

```bash
python benchmarks/run_benchmark.py
python benchmarks/leaderboard.py
```

---

## 4. 运行测试

```bash
# 运行全部测试
python3 -m pytest tests/test_carrymem.py -v

# 运行特定分类
python3 -m pytest tests/test_carrymem.py::TestClassification -v
python3 -m pytest tests/test_carrymem.py::TestDeclare -v
python3 -m pytest tests/test_carrymem.py::TestNamespace -v

# 运行基准测试
python3 benchmarks/run_benchmark.py
```

---

## 5. 测试覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| carrymem.py | 90%+ | ✅ 32/32 passing |
| engine.py | 80%+ | ✅ covered via TestClassification |
| adapters/sqlite_adapter.py | 90%+ | ✅ covered via TestSQLiteAdapter |
| adapters/loader.py | 90%+ | ✅ covered via TestPluginLoader |
| MCP handlers | 70%+ | ⚠️ 需要手动测试 |
