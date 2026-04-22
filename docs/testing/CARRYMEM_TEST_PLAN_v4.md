# CarryMem v0.3 测试计划 (v3.0)

**日期**: 2026-04-22
**版本**: v3.0 (对应 CarryMem v0.3.0)
**参考**: CARRYMEM_ARCHITECTURE_v4.md, CARRYMEM_DESIGN_v4.md

---

## 1. 测试策略

### 1.1 测试文件

统一测试套件: `tests/test_carrymem.py` (114 个测试)

### 1.2 测试分类

| 分类 | 测试类 | 测试数 | 覆盖范围 |
|------|--------|--------|---------|
| EN 偏好 | TestENPreference | 4 | prefer, like, always, never |
| EN 纠正 | TestENCorrection | 5 | no/wrong/correction/actually/scratch |
| EN 事实 | TestENFactDeclaration | 3 | version, rate_limit, company |
| EN 决策 | TestENDecision | 2 | let's go with, decided |
| EN 关系 | TestENRelationship | 2 | manager, team member |
| EN 任务 | TestENTaskPattern | 2 | weekly standup, always test |
| EN 情感 | TestENSentiment | 2 | frustrating, amazing |
| ZH 偏好 | TestZHPreference | 4 | 喜欢, 倾向, 习惯, 别用 |
| ZH 纠正 | TestZHCorrection | 8 | 错了, 不对, 纠正, 说错了, 方法错, 配置错, 不对不对, 忽略 |
| ZH 事实 | TestZHFactDeclaration | 2 | 版本, 限流 |
| ZH 决策 | TestZHDecision | 2 | 用微服务, 决定用 |
| ZH 关系 | TestZHRelationship | 2 | 经理, 团队 |
| ZH 任务 | TestZHTaskPattern | 2 | 每周站会, 每次测试 |
| ZH 情感 | TestZHSentiment | 2 | 太慢, 太棒了 |
| JA 偏好 | TestJAPreference | 4 | 好き, 使いたい, いつも, より |
| JA 纠正 | TestJACorrection | 6 | 間違って, 訂正, いやいや, 間違った, エラー, 前に言った |
| JA 事实 | TestJAFactDeclaration | 2 | バージョン, レート制限 |
| JA 决策 | TestJADecision | 2 | 行きましょう, 決めました |
| JA 关系 | TestJARelationship | 2 | 担当, マネージャー |
| JA 任务 | TestJATaskPattern | 2 | 毎週, いつも |
| JA 情感 | TestJASentiment | 2 | イライラ, 素晴らしい |
| EN 噪声 | TestENNoiseRejection | 7 | ok, thanks, hello, how are you, see you, just a test, empty |
| ZH 噪声 | TestZHNoiseRejection | 5 | 好的, 谢谢, 你好, 明白了, 怎么 |
| JA 噪声 | TestJANoiseRejection | 5 | はい, ありがとう, こんにちは, わかりました, 開発環境 |
| 语言检测 | TestLanguageDetection | 6 | en, zh-cn, ja-hiragana, ja-katakana, ja-mixed, zh-no-kana |
| 核心集成 | TestCarryMemCore | 12 | classify, recall, forget, declare, profile, prompt, no-storage |
| 命名空间 | TestNamespace | 2 | 隔离, 跨 namespace |
| 插件加载 | TestPluginLoader | 5 | sqlite, obsidian, unknown, list, string |
| SQLite 适配器 | TestSQLiteAdapter | 4 | remember, forget, stats, profile |
| 边界测试 | TestEdgeCases | 7 | empty, none, short, to_memory_entry, mixed, ja+en, zh+en |

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
