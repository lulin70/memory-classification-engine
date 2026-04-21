# CarryMem v0.5~v0.6 测试计划 (v1.0)

**日期**: 2026-04-20
**版本**: v1.0
**参考**: CARRYMEM_USER_STORIES.md, CARRYMEM_DESIGN_v4.md

---

## 1. 测试分层

| 层级 | 范围 | 工具 | 目标覆盖率 |
|------|------|------|-----------|
| L1 单元测试 | 引擎层 (MCE) | pytest | ≥90% |
| L2 适配器测试 | SQLiteAdapter | pytest + TestStorageAdapterContract | ≥80% |
| L3 集成测试 | CarryMem 端到端 | pytest | ≥50% |
| L4 MCP 测试 | MCP Server 3+3 | MCP Inspector | 全工具覆盖 |
| L5 多语言测试 | EN/CN/JP 分类 | pytest | 每语言≥30条 |
| L6 Benchmark | MCE-Bench 180-case | classification_accuracy.py | Acc≥90% |

---

## 2. L1: 引擎层单元测试 (不变)

引擎层测试保持现有 881+ 测试不变，确保零存储依赖。

```python
# tests/test_engine.py (现有，不变)
class TestMemoryClassificationEngine:
    def test_classify_user_preference(self): ...
    def test_classify_fact_declaration(self): ...
    # ... 881+ 现有测试
```

---

## 3. L2: 适配器测试

### 3.1 StorageAdapter Contract 测试

```python
# tests/adapters/test_sqlite_contract.py
class TestSQLiteAdapterContract(TestStorageAdapterContract):
    def setUp(self):
        self.adapter = SQLiteAdapter(":memory:")

    # 继承的合约测试:
    # - test_remember_returns_stored_memory
    # - test_recall_finds_stored_memory
    # - test_recall_with_filters
    # - test_forget_removes_memory
    # - test_remember_batch
    # - test_adapter_name_and_capabilities
    # - test_get_stats
```

### 3.2 SQLiteAdapter 专项测试

```python
# tests/adapters/test_sqlite_specific.py
class TestSQLiteAdapterSpecific:

    def test_database_auto_creation(self):
        """数据库文件自动创建"""
        adapter = SQLiteAdapter("/tmp/test_carrymem.db")
        assert os.path.exists("/tmp/test_carrymem.db")

    def test_fts5_search(self):
        """FTS5 全文搜索"""
        adapter = SQLiteAdapter(":memory:")
        adapter.remember(MemoryEntry(id="1", type="fact_declaration",
                           content="Python 3.9 is the minimum version"))
        results = adapter.recall("Python")
        assert len(results) >= 1

    def test_content_dedup(self):
        """内容去重"""
        adapter = SQLiteAdapter(":memory:")
        entry = MemoryEntry(id="1", type="user_preference",
                            content="I prefer dark mode")
        adapter.remember(entry)
        adapter.remember(entry)  # 重复
        stats = adapter.get_stats()
        assert stats["total_count"] == 1  # 不重复

    def test_tier_expiry(self):
        """Tier 过期机制"""
        adapter = SQLiteAdapter(":memory:")
        entry = MemoryEntry(id="1", type="task_pattern", tier=1,
                            content="temp task")
        adapter.remember(entry)
        # 手动设置过期时间为过去
        adapter._execute(
            "UPDATE memories SET expires_at = datetime('now', '-1 hour') WHERE id = ?",
            ("1",)
        )
        deleted = adapter.forget_expired()
        assert deleted == 1

    def test_confidence_filter(self):
        """置信度过滤"""
        adapter = SQLiteAdapter(":memory:")
        adapter.remember(MemoryEntry(id="1", type="user_preference",
                           content="high conf", confidence=0.9))
        adapter.remember(MemoryEntry(id="2", type="user_preference",
                           content="low conf", confidence=0.3))
        results = adapter.recall("", filters={"confidence_min": 0.5})
        assert all(r.confidence >= 0.5 for r in results)
```

---

## 4. L3: 集成测试 (CarryMem 端到端)

```python
# tests/test_carrymem_integration.py
class TestCarryMemIntegration:

    def test_three_line_onboarding(self):
        """US-001: 三行代码接入"""
        from carrymem import CarryMem
        cm = CarryMem()
        result = cm.classify_and_remember("I prefer dark mode")
        assert result["stored"] is True
        assert result["entries"][0]["type"] == "user_preference"

    def test_classify_without_storage(self):
        """US-004: 纯分类模式"""
        from carrymem import CarryMem
        cm = CarryMem(storage=None)
        result = cm.classify_message("I prefer dark mode")
        assert result["entries"][0]["type"] == "user_preference"
        assert "stored" not in result or result.get("stored") is False

    def test_storage_not_configured_error(self):
        """无存储时调用存储方法报错"""
        from carrymem import CarryMem, StorageNotConfiguredError
        cm = CarryMem(storage=None)
        with pytest.raises(StorageNotConfiguredError):
            cm.recall_memories()

    def test_recall_by_type(self):
        """US-003: 按类型检索"""
        from carrymem import CarryMem
        cm = CarryMem()
        cm.classify_and_remember("I prefer dark mode")
        cm.classify_and_remember("We use PostgreSQL for our database")
        prefs = cm.recall_memories(filters={"type": "user_preference"})
        assert all(e["type"] == "user_preference" for e in prefs)

    def test_forget_memory(self):
        """US-005: 删除记忆"""
        from carrymem import CarryMem
        cm = CarryMem()
        result = cm.classify_and_remember("test message")
        memory_id = result["storage_keys"][0]
        assert cm.forget_memory(memory_id) is True
        assert cm.forget_memory(memory_id) is False

    def test_context_merge_on_confirmation(self):
        """US-006: 用户确认时合并上下文"""
        from carrymem import CarryMem
        cm = CarryMem()
        result = cm.classify_message(
            message="行，就这样搞",
            context="AI建议: 使用SQLite作为默认存储方案"
        )
        # 应该检测到确认模式并合并上下文
        entries = result["entries"]
        decision_entries = [e for e in entries if e["type"] == "decision"]
        if decision_entries:
            assert "SQLite" in decision_entries[0]["content"]
```

---

## 5. L5: 多语言测试用例

### 5.1 英文测试用例 (30 条)

```python
# tests/test_multilingual_en.py
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

### 5.2 中文测试用例 (30 条)

```python
# tests/test_multilingual_zh.py
ZH_TEST_CASES = [
    # user_preference (5)
    {"msg": "我喜欢用深色主题", "type": "user_preference"},
    {"msg": "我不太喜欢默认样式", "type": "user_preference"},
    {"msg": "还是用Vim快捷键比较好", "type": "user_preference"},
    {"msg": "别再推荐Python 2了", "type": "user_preference"},
    {"msg": "我之前说过我用Mac", "type": "user_preference"},

    # fact_declaration (5)
    {"msg": "Python 3.9是最低要求版本", "type": "fact_declaration"},
    {"msg": "我们的API限流是每分钟1000次请求", "type": "fact_declaration"},
    {"msg": "我们工程团队有100人", "type": "fact_declaration"},
    {"msg": "数据库服务器部署在AWS上", "type": "fact_declaration"},
    {"msg": "Redis在p99的读取延迟低于1毫秒", "type": "fact_declaration"},

    # decision (5)
    {"msg": "我们用微服务架构吧", "type": "decision"},
    {"msg": "我决定用SQLite做默认存储", "type": "decision"},
    {"msg": "每周五部署到生产环境", "type": "decision"},
    {"msg": "好的，就这样搞", "type": "decision"},
    {"msg": "行，按这个方案来", "type": "decision"},

    # correction (5)
    {"msg": "不对，我说的是TypeScript不是JavaScript", "type": "correction"},
    {"msg": "截止日期是下周三不是周五", "type": "correction"},
    {"msg": "等等，那个方案其实没那么好", "type": "correction"},
    {"msg": "我需要纠正之前关于API的说法", "type": "correction"},
    {"msg": "上次那个方案效果不好", "type": "correction"},

    # sentiment_marker (3)
    {"msg": "构建速度太慢了，真的很烦", "type": "sentiment_marker"},
    {"msg": "这个新功能太棒了！", "type": "sentiment_marker"},
    {"msg": "我对安全问题有些担心", "type": "sentiment_marker"},

    # relationship (3)
    {"msg": "我的经理Sarah要求周五前交报告", "type": "relationship"},
    {"msg": "后端团队的John在处理API", "type": "relationship"},
    {"msg": "我和设计团队一起做UI决策", "type": "relationship"},

    # task_pattern (2)
    {"msg": "每周一上午10点我们有站会", "type": "task_pattern"},
    {"msg": "我每次推代码前都会跑测试", "type": "task_pattern"},

    # noise (2)
    {"msg": "你好，最近怎么样？", "type": None},
    {"msg": "现在几点了？", "type": None},
]
```

### 5.3 日文测试用例 (30 条)

```python
# tests/test_multilingual_ja.py
JA_TEST_CASES = [
    # user_preference (5)
    {"msg": "ダークモードが好きです", "type": "user_preference"},
    {"msg": "デフォルトのテーマはあまり好きではありません", "type": "user_preference"},
    {"msg": "Vimのキーバインドを使いたいです", "type": "user_preference"},
    {"msg": "Python 2はもう提案しないでください", "type": "user_preference"},
    {"msg": "前に言いましたが、Macを使っています", "type": "user_preference"},

    # fact_declaration (5)
    {"msg": "Python 3.9が最低要件バージョンです", "type": "fact_declaration"},
    {"msg": "APIのレート制限は1分間に1000リクエストです", "type": "fact_declaration"},
    {"msg": "エンジニアリングチームには100人の従業員がいます", "type": "fact_declaration"},
    {"msg": "データベースサーバーはAWSでホストされています", "type": "fact_declaration"},
    {"msg": "Redisのp99読み取りレイテンシは1ミリ秒未満です", "type": "fact_declaration"},

    # decision (5)
    {"msg": "マイクロサービスアプローチで行きましょう", "type": "decision"},
    {"msg": "デフォルトストレージにSQLiteを使うことに決めました", "type": "decision"},
    {"msg": "毎週金曜日に本番環境にデプロイします", "type": "decision"},
    {"msg": "はい、そうしましょう", "type": "decision"},
    {"msg": "いいよ、その計画で進めて", "type": "decision"},

    # correction (5)
    {"msg": "実はJavaScriptではなくTypeScriptのことでした", "type": "correction"},
    {"msg": "締め切りは金曜日ではなく水曜日です", "type": "correction"},
    {"msg": "待って、それは間違っています", "type": "correction"},
    {"msg": "APIについての以前の発言を訂正する必要があります", "type": "correction"},
    {"msg": "前のアプローチはうまくいっていませんでした", "type": "correction"},

    # sentiment_marker (3)
    {"msg": "ビルド時間が遅くて本当にイライラします", "type": "sentiment_marker"},
    {"msg": "この新機能は素晴らしい！", "type": "sentiment_marker"},
    {"msg": "セキュリティの影響が心配です", "type": "sentiment_marker"},

    # relationship (3)
    {"msg": "マネージャーのSarahが金曜日までにレポートを求めています", "type": "relationship"},
    {"msg": "バックエンドチームのJohnがAPIを担当しています", "type": "relationship"},
    {"msg": "デザインチームとUIの決定をしています", "type": "relationship"},

    # task_pattern (2)
    {"msg": "毎週月曜日の午前10時にチームスタンドアップがあります", "type": "task_pattern"},
    {"msg": "コードをプッシュする前にいつもテストを実行します", "type": "task_pattern"},

    # noise (2)
    {"msg": "こんにちは、お元気ですか？", "type": None},
    {"msg": "今何時ですか？", "type": None},
]
```

---

## 6. L4: MCP Server 测试

### 6.1 核心工具测试

```python
# tests/test_mcp_core.py
class TestMCPCoreTools:
    """核心工具测试 — 无论是否配置 adapter 都应通过"""

    def test_classify_message_works_without_adapter(self): ...
    def test_batch_classify_works_without_adapter(self): ...
    def test_get_schema_works_without_adapter(self): ...
```

### 6.2 可选工具测试

```python
# tests/test_mcp_optional.py
class TestMCPOptionalTools:
    """可选工具测试 — 需要 adapter 配置"""

    def test_classify_and_remember_with_sqlite(self): ...
    def test_recall_memories_with_sqlite(self): ...
    def test_forget_memory_with_sqlite(self): ...

    def test_optional_tools_error_without_adapter(self):
        """无 adapter 时可选工具返回 storage_not_configured 错误"""
        ...
```

---

## 7. L6: Benchmark 回归

```python
# 确保 MCE-Bench 180-case 在所有改动后仍然通过
# 运行: python benchmarks/classification_accuracy.py

# 预期结果:
# Accuracy ≥ 90%
# F1 ≥ 97%
# 7/7 types F1 ≥ 50%
```

---

## 8. 测试执行计划

| 阶段 | 测试 | 时机 | 通过标准 |
|------|------|------|---------|
| v0.5 开发中 | L1 引擎测试 | 每次提交 | 881+ 全绿 |
| v0.5 开发中 | L5 多语言测试 | 新增用例后 | EN≥90%, CN≥85%, JA≥80% |
| v0.5 完成前 | L6 Benchmark | 合并前 | Acc≥90%, F1≥97% |
| v0.6 开发中 | L2 适配器测试 | 每次提交 | Contract 全绿 |
| v0.6 开发中 | L3 集成测试 | 每次提交 | US-001~005 全绿 |
| v0.6 完成前 | L4 MCP 测试 | 合并前 | 3+3 全工具覆盖 |
| v0.6 发布前 | 全量回归 | 发布前 | L1~L6 全绿 |
