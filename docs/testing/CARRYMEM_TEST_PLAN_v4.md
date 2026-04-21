# CarryMem v0.9 测试计划 (v2.0)

**日期**: 2026-04-21
**版本**: v2.0 (对应 CarryMem v0.7~v0.9)
**参考**: CARRYMEM_USER_STORIES.md, CARRYMEM_DESIGN_v4.md

---

## 1. 测试分层

| 层级 | 范围 | 工具 | 目标覆盖率 |
|------|------|------|-----------|
| L1 单元测试 | 引擎层 (MCE) | pytest | ≥90% |
| L2 适配器测试 | SQLiteAdapter + ObsidianAdapter | pytest | ≥80% |
| L3 集成测试 | CarryMem 端到端 | pytest | ≥50% |
| L4 MCP 测试 | MCP Server 3+3+3+2 | MCP Inspector | 全工具覆盖 |
| L5 多语言测试 | EN/CN/JP 分类 | pytest | 每语言≥30条 |
| L6 Benchmark | MCE-Bench 180-case | classification_accuracy.py | Acc≥90% |

---

## 2. L2: 适配器测试

### 2.1 SQLiteAdapter Contract 测试 (7 个)

| 测试 | 说明 |
|------|------|
| test_remember_returns_stored_memory | remember 返回 StoredMemory |
| test_recall_finds_stored_memory | recall 能找到已存储的记忆 |
| test_recall_with_filters | 按 type/tier/confidence 过滤 |
| test_forget_removes_memory | forget 删除记忆 |
| test_remember_batch | 批量存储 |
| test_adapter_name_and_capabilities | 适配器属性 |
| test_get_stats | 统计信息 |

### 2.2 SQLiteAdapter 专项测试 (4 个)

| 测试 | 说明 |
|------|------|
| test_fts5_search | FTS5 全文搜索 |
| test_content_dedup | 内容去重 |
| test_tier_expiry | Tier 过期机制 |
| test_confidence_filter | 置信度过滤 |

### 2.3 ObsidianAdapter 测试 (12 个) — v0.7 新增

| 测试 | 说明 |
|------|------|
| test_index_vault | 索引 vault |
| test_incremental_index | 增量索引 |
| test_fts_search | FTS5 搜索 |
| test_fts_search_design_patterns | 设计模式搜索 |
| test_tag_filter | 标签过滤 |
| test_title_filter | 标题过滤 |
| test_remember_raises | 只读：remember 抛异常 |
| test_forget_raises | 只读：forget 抛异常 |
| test_get_tags | 获取标签列表 |
| test_get_linked_notes | 获取关联笔记 |
| test_get_stats | 统计信息 |
| test_capabilities | 适配器能力 |

### 2.4 ObsidianAdapter 单元测试 (6 个) — v0.7 新增

| 测试 | 说明 |
|------|------|
| test_parse_frontmatter_with_tags | YAML frontmatter 解析 |
| test_parse_frontmatter_empty | 空 frontmatter |
| test_parse_frontmatter_boolean_and_int | 布尔/整数解析 |
| test_extract_tags_from_frontmatter_and_inline | 标签提取 |
| test_extract_wiki_links | Wiki-link 提取 |
| test_extract_wiki_links_empty | 空 wiki-link |

---

## 3. L3: 集成测试

### 3.1 CarryMem 基础集成 (7 个) — v0.6

| 测试 | 用户故事 |
|------|---------|
| test_three_line_onboarding | US-001 |
| test_classify_without_storage | US-004 |
| test_storage_not_configured_error | US-004 |
| test_recall_by_type | US-003 |
| test_forget_memory | US-005 |
| test_context_merge_on_confirmation | US-006 |
| test_classify_and_remember | US-002 |

### 3.2 CarryMem 知识库集成 (8 个) — v0.7 新增

| 测试 | 说明 |
|------|------|
| test_knowledge_not_configured_error | 无知识库时报错 |
| test_index_knowledge | 索引知识库 |
| test_recall_from_knowledge | 检索知识库 |
| test_recall_all_memory_and_knowledge | 统一检索 |
| test_recall_all_knowledge_only | 仅知识库 |
| test_recall_all_memory_only | 仅记忆库 |
| test_knowledge_adapter_property | 适配器属性 |
| test_index_knowledge_not_configured | 未配置时索引报错 |

### 3.3 Profile 集成测试 (20 个) — v0.8 新增

**Declare 测试 (8 个)**:

| 测试 | 说明 |
|------|------|
| test_declare_preference | 声明偏好 |
| test_declare_fact | 声明事实 |
| test_declare_correction | 声明纠正 |
| test_declare_noise_still_stored | 噪音也存储 |
| test_declare_vs_classify_confidence | 对比 confidence |
| test_declare_no_storage_raises | 无存储报错 |
| test_declare_multiple | 多次声明 |
| test_declare_summary | 声明摘要 |

**Profile 测试 (8 个)**:

| 测试 | 说明 |
|------|------|
| test_empty_profile | 空画像 |
| test_profile_after_declare | 声明后画像 |
| test_profile_highlights | 高亮内容 |
| test_profile_no_storage | 无存储画像 |
| test_profile_by_tier | 按层级统计 |
| test_profile_after_classify_and_remember | 分类后画像 |
| test_profile_mixed_sources | 混合来源 |
| test_profile_summary_format | 摘要格式 |

**MCP Handler 测试 (4 个)**:

| 测试 | 说明 |
|------|------|
| test_declare_preference_handler | MCP 声明 |
| test_declare_preference_handler_empty | 空消息 |
| test_get_memory_profile_handler | MCP 画像 |
| test_declare_preference_handler_no_storage | 无存储 |

### 3.4 Namespace 集成测试 (11 个) — v0.9 新增

| 测试 | 说明 |
|------|------|
| test_default_namespace | 默认 namespace |
| test_custom_namespace | 自定义 namespace |
| test_write_to_namespace | 写入 namespace |
| test_isolation_write_read | 隔离读写 |
| test_isolation_forget | 隔离删除 |
| test_isolation_profile | 隔离画像 |
| test_cross_namespace_recall | 跨 namespace 检索 |
| test_recall_all_with_namespaces | 统一检索跨 namespace |
| test_backward_compatibility_no_namespace | 向后兼容 |
| test_adapter_namespace_property | 适配器属性 |
| test_stats_includes_namespace | 统计含 namespace |

---

## 4. L5: 多语言测试用例

### 4.1 英文测试用例 (30 条)

```python
EN_TEST_CASES = [
    # user_preference (5)
    {"msg": "I prefer dark mode in my editor", "type": "user_preference"},
    {"msg": "I don't like the default theme", "type": "user_preference"},
    {"msg": "I'd rather use Vim keybindings", "type": "user_preference"},
    {"msg": "Please stop suggesting Python 2", "type": "user_preference"},
    {"msg": "I mentioned before that I use macOS", "type": "user_preference"},
    # fact_declaration (5)
    {"msg": "Python 3.9 is the minimum required version", "type": "fact_declaration"},
    {"msg": "Our API rate limit is 1000 requests per minute", "type": "fact_declaration"},
    {"msg": "We have 100 employees in the engineering team", "type": "fact_declaration"},
    {"msg": "The database server is hosted on AWS", "type": "fact_declaration"},
    {"msg": "Redis has sub-millisecond read latency at p99", "type": "fact_declaration"},
    # decision (5)
    {"msg": "Let's go with the microservices approach", "type": "decision"},
    {"msg": "I decided to use SQLite for the default storage", "type": "decision"},
    {"msg": "We'll deploy to production every Friday", "type": "decision"},
    {"msg": "Okay, let's do it that way", "type": "decision"},
    {"msg": "Sounds good, go ahead with that plan", "type": "decision"},
    # correction (5)
    {"msg": "Actually, I meant TypeScript not JavaScript", "type": "correction"},
    {"msg": "No, the deadline is next Wednesday not Friday", "type": "correction"},
    {"msg": "Wait, that's wrong — we use PostgreSQL not MySQL", "type": "correction"},
    {"msg": "I need to correct my earlier statement about the API", "type": "correction"},
    {"msg": "The previous approach wasn't working well", "type": "correction"},
    # sentiment_marker (3)
    {"msg": "I'm really frustrated with the slow build times", "type": "sentiment_marker"},
    {"msg": "This new feature is amazing!", "type": "sentiment_marker"},
    {"msg": "I'm worried about the security implications", "type": "sentiment_marker"},
    # relationship (3)
    {"msg": "My manager Sarah wants the report by Friday", "type": "relationship"},
    {"msg": "John from the backend team is handling the API", "type": "relationship"},
    {"msg": "I work with the design team on UI decisions", "type": "relationship"},
    # task_pattern (2)
    {"msg": "Every Monday we have a team standup at 10am", "type": "task_pattern"},
    {"msg": "I always run the tests before pushing code", "type": "task_pattern"},
    # noise (2)
    {"msg": "Hello, how are you?", "type": None},
    {"msg": "What time is it?", "type": None},
]
```

### 4.2 中文测试用例 (30 条)

```python
ZH_TEST_CASES = [
    {"msg": "我喜欢用深色主题", "type": "user_preference"},
    {"msg": "我不太喜欢默认样式", "type": "user_preference"},
    {"msg": "还是用Vim快捷键比较好", "type": "user_preference"},
    {"msg": "别再推荐Python 2了", "type": "user_preference"},
    {"msg": "我之前说过我用Mac", "type": "user_preference"},
    {"msg": "Python 3.9是最低要求版本", "type": "fact_declaration"},
    {"msg": "我们的API限流是每分钟1000次请求", "type": "fact_declaration"},
    {"msg": "我们工程团队有100人", "type": "fact_declaration"},
    {"msg": "数据库服务器部署在AWS上", "type": "fact_declaration"},
    {"msg": "Redis在p99的读取延迟低于1毫秒", "type": "fact_declaration"},
    {"msg": "我们用微服务架构吧", "type": "decision"},
    {"msg": "我决定用SQLite做默认存储", "type": "decision"},
    {"msg": "每周五部署到生产环境", "type": "decision"},
    {"msg": "好的，就这样搞", "type": "decision"},
    {"msg": "行，按这个方案来", "type": "decision"},
    {"msg": "不对，我说的是TypeScript不是JavaScript", "type": "correction"},
    {"msg": "截止日期是下周三不是周五", "type": "correction"},
    {"msg": "等等，那个方案其实没那么好", "type": "correction"},
    {"msg": "我需要纠正之前关于API的说法", "type": "correction"},
    {"msg": "上次那个方案效果不好", "type": "correction"},
    {"msg": "构建速度太慢了，真的很烦", "type": "sentiment_marker"},
    {"msg": "这个新功能太棒了！", "type": "sentiment_marker"},
    {"msg": "我对安全问题有些担心", "type": "sentiment_marker"},
    {"msg": "我的经理Sarah要求周五前交报告", "type": "relationship"},
    {"msg": "后端团队的John在处理API", "type": "relationship"},
    {"msg": "我和设计团队一起做UI决策", "type": "relationship"},
    {"msg": "每周一上午10点我们有站会", "type": "task_pattern"},
    {"msg": "我每次推代码前都会跑测试", "type": "task_pattern"},
    {"msg": "你好，最近怎么样？", "type": None},
    {"msg": "现在几点了？", "type": None},
]
```

### 4.3 日文测试用例 (30 条)

```python
JA_TEST_CASES = [
    {"msg": "ダークモードが好きです", "type": "user_preference"},
    {"msg": "デフォルトのテーマはあまり好きではありません", "type": "user_preference"},
    {"msg": "Vimのキーバインドを使いたいです", "type": "user_preference"},
    {"msg": "Python 2はもう提案しないでください", "type": "user_preference"},
    {"msg": "前に言いましたが、Macを使っています", "type": "user_preference"},
    {"msg": "Python 3.9が最低要件バージョンです", "type": "fact_declaration"},
    {"msg": "APIのレート制限は1分間に1000リクエストです", "type": "fact_declaration"},
    {"msg": "エンジニアリングチームには100人の従業員がいます", "type": "fact_declaration"},
    {"msg": "データベースサーバーはAWSでホストされています", "type": "fact_declaration"},
    {"msg": "Redisのp99読み取りレイテンシは1ミリ秒未満です", "type": "fact_declaration"},
    {"msg": "マイクロサービスアプローチで行きましょう", "type": "decision"},
    {"msg": "デフォルトストレージにSQLiteを使うことに決めました", "type": "decision"},
    {"msg": "毎週金曜日に本番環境にデプロイします", "type": "decision"},
    {"msg": "はい、そうしましょう", "type": "decision"},
    {"msg": "いいよ、その計画で進めて", "type": "decision"},
    {"msg": "実はJavaScriptではなくTypeScriptのことでした", "type": "correction"},
    {"msg": "締め切りは金曜日ではなく水曜日です", "type": "correction"},
    {"msg": "待って、それは間違っています", "type": "correction"},
    {"msg": "APIについての以前の発言を訂正する必要があります", "type": "correction"},
    {"msg": "前のアプローチはうまくいっていませんでした", "type": "correction"},
    {"msg": "ビルド時間が遅くて本当にイライラします", "type": "sentiment_marker"},
    {"msg": "この新機能は素晴らしい！", "type": "sentiment_marker"},
    {"msg": "セキュリティの影響が心配です", "type": "sentiment_marker"},
    {"msg": "マネージャーのSarahが金曜日までにレポートを求めています", "type": "relationship"},
    {"msg": "バックエンドチームのJohnがAPIを担当しています", "type": "relationship"},
    {"msg": "デザインチームとUIの決定をしています", "type": "relationship"},
    {"msg": "毎週月曜日の午前10時にチームスタンドアップがあります", "type": "task_pattern"},
    {"msg": "コードをプッシュする前にいつもテストを実行します", "type": "task_pattern"},
    {"msg": "こんにちは、お元気ですか？", "type": None},
    {"msg": "今何時ですか？", "type": None},
]
```

---

## 5. L6: Benchmark 回归

```
运行: python benchmarks/classification_accuracy.py
预期: Accuracy ≥ 90%, F1 ≥ 97%, 7/7 types F1 ≥ 50%
当前: Accuracy 90.6%, F1 97.9% ✅
```

---

## 6. 测试执行与版本映射

| 版本 | 新增测试 | 总测试数 | 通过标准 |
|------|---------|---------|---------|
| v0.6 | 18 (L2+L3) | 18 | 全绿 |
| v0.7 | 26 (Obsidian+Knowledge) | 26+18 | 全绿+V6回归 |
| v0.8 | 20 (Declare+Profile) | 20+26+18 | 全绿+V7+V6回归 |
| v0.9 | 11 (Namespace) | 11+20+26+18 | 全绿+V8+V7+V6回归 |
| **总计** | **75** | **75** | **全部通过** ✅ |
