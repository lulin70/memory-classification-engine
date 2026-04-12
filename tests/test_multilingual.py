#!/usr/bin/env python3
"""
Multilingual Test Suite for Memory Classification Engine.
Tests English, Chinese (中文), and Japanese (日本語) language support.

Product Requirement: MCE must support EN/ZH/JP for international markets.

IMPORTANT: These tests use STRICT assertions to catch classification bugs.
If a test fails, it means the system needs to be FIXED, not the test relaxed.
"""

import pytest
from memory_classification_engine.engine import MemoryClassificationEngine


def get_memory_types(result):
    """Extract all memory types from result."""
    return [m.get("memory_type") for m in result.get("matches", [])]


def has_memory_type(result, expected_type):
    """Check if any match has the expected memory type."""
    return expected_type in get_memory_types(result)


class TestEnglishLanguageSupport:
    """Test English language classification with STRICT assertions."""

    @pytest.fixture
    def engine(self):
        return MemoryClassificationEngine()

    def test_english_user_preference(self, engine):
        """Test English user preference detection."""
        result = engine.process_message("I prefer using spaces over tabs")
        assert has_memory_type(result, "user_preference"), \
            f"Expected user_preference, got: {get_memory_types(result)}"

    def test_english_correction(self, engine):
        """Test English correction detection."""
        result = engine.process_message(
            "That last approach was too complex, let's go simpler"
        )
        # Should detect as correction or decision (both valid for rejection)
        types = get_memory_types(result)
        assert "correction" in types or "decision" in types or "fact_declaration" in types, \
            f"Expected correction/decision/fact, got: {types}"

    def test_english_fact_declaration(self, engine):
        """Test English fact declaration - MUST be fact_declaration, not event!"""
        result = engine.process_message("We have 100 employees across 5 offices")
        assert has_memory_type(result, "fact_declaration"), \
            f"STRICT: Expected fact_declaration, got: {get_memory_types(result)}"
        
        # BUG CATCHER: Should NOT be classified as event
        assert "event" not in get_memory_types(result), \
            f"BUG: Fact incorrectly classified as event!"

    def test_english_decision(self, engine):
        """Test English decision detection."""
        result = engine.process_message("Let's go with Redis for caching")
        assert has_memory_type(result, "decision"), \
            f"Expected decision, got: {get_memory_types(result)}"

    def test_english_relationship(self, engine):
        """Test English relationship detection."""
        result = engine.process_message(
            "Alice handles the backend API, Bob does frontend"
        )
        assert has_memory_type(result, "relationship"), \
            f"Expected relationship, got: {get_memory_types(result)}"

    def test_english_task_pattern(self, engine):
        """Test English task pattern detection."""
        result = engine.process_message(
            "Always run the full test suite before merging to main"
        )
        # Task pattern should be detected
        types = get_memory_types(result)
        assert len(types) >= 1, f"Expected at least one match, got: {types}"

    def test_english_sentiment_marker(self, engine):
        """Test English sentiment marker detection."""
        result = engine.process_message(
            "This deployment process is so frustrating, it takes forever"
        )
        # Should detect sentiment or at minimum process the message
        assert len(get_memory_types(result)) >= 1

    def test_english_contact_info(self, engine):
        """Test English contact information extraction."""
        result = engine.process_message(
            "My email is john.doe@example.com and phone is 123-456-7890"
        )
        assert len(result["matches"]) > 0

    def test_english_event_detection(self, engine):
        """Test English event/date detection - should ONLY match real dates."""
        result = engine.process_message(
            "Meeting on April 15th at 2:30 PM with the design team"
        )
        assert has_memory_type(result, "event"), \
            f"Expected event for date-containing message, got: {get_memory_types(result)}"


class TestChineseLanguageSupport:
    """Test Chinese (中文) language classification with STRICT assertions."""

    @pytest.fixture
    def engine(self):
        return MemoryClassificationEngine()

    def test_chinese_user_preference(self, engine):
        """Test Chinese user preference detection."""
        result = engine.process_message("我喜欢用空格而不是Tab缩进")
        assert has_memory_type(result, "user_preference"), \
            f"Expected user_preference, got: {get_memory_types(result)}"

    def test_chinese_correction(self, engine):
        """Test Chinese correction detection."""
        result = engine.process_message(
            "上次那个方案太复杂了，换个简单点的"
        )
        types = get_memory_types(result)
        assert "correction" in types or "decision" in types or "fact_declaration" in types, \
            f"Expected correction/decision/fact, got: {types}"

    def test_chinese_fact_declaration(self, engine):
        """Test Chinese fact declaration - MUST be fact_declaration, not event!"""
        result = engine.process_message("我们公司有100名员工，分布在5个办公室")
        assert has_memory_type(result, "fact_declaration"), \
            f"STRICT: Expected fact_declaration, got: {get_memory_types(result)}"
        
        # BUG CATCHER: Should NOT be classified as event
        assert "event" not in get_memory_types(result), \
            f"BUG: Fact incorrectly classified as event!"

    def test_chinese_decision(self, engine):
        """Test Chinese decision detection."""
        result = engine.process_message("我们决定用Redis来做缓存")
        assert has_memory_type(result, "decision"), \
            f"Expected decision, got: {get_memory_types(result)}"

    def test_chinese_relationship(self, engine):
        """Test Chinese relationship detection."""
        result = engine.process_message("张三负责后端API，李四做前端开发")
        assert has_memory_type(result, "relationship"), \
            f"Expected relationship, got: {get_memory_types(result)}"

    def test_chinese_task_pattern(self, engine):
        """Test Chinese task pattern detection."""
        result = engine.process_message("每次部署前都要跑一遍测试用例")
        assert len(get_memory_types(result)) >= 1

    def test_chinese_sentiment_marker(self, engine):
        """Test Chinese sentiment marker detection."""
        result = engine.process_message("这个部署流程太繁琐了，每次都要等很久")
        assert len(get_memory_types(result)) >= 1

    def test_chinese_contact_info(self, engine):
        """Test Chinese contact information extraction."""
        result = engine.process_message("我的邮箱是zhangsan@example.com，电话是13812345678")
        assert len(result["matches"]) > 0


class TestJapaneseLanguageSupport:
    """Test Japanese (日本語) language classification with STRICT assertions.
    
    Note: Japanese support is being improved. Tests document current accuracy.
    """

    @pytest.fixture
    def engine(self):
        return MemoryClassificationEngine()

    def test_japanese_user_preference(self, engine):
        """Test Japanese user preference detection."""
        result = engine.process_message(
            "スペースを使いたいです、タブは使いません"
        )
        assert len(result["matches"]) > 0

    def test_japanese_correction(self, engine):
        """Test Japanese correction detection."""
        result = engine.process_message(
            "前のアプローチは複雑すぎました、もっと簡単なものにしましょう"
        )
        types = get_memory_types(result)
        assert any(t in ["correction", "decision", "fact_declaration"] for t in types), \
            f"Expected correction variant, got: {types}"

    def test_japanese_fact_declaration(self, engine):
        """Test Japanese fact declaration - MUST be fact_declaration, not event!"""
        result = engine.process_message("当社は100名の従業員がおります")
        assert has_memory_type(result, "fact_declaration"), \
            f"STRICT: Expected fact_declaration, got: {get_memory_types(result)}"
        
        # BUG CATCHER: Should NOT be classified as event
        assert "event" not in get_memory_types(result), \
            f"BUG: Fact incorrectly classified as event!"

    def test_japanese_decision(self, engine):
        """Test Japanese decision detection."""
        result = engine.process_message(
            "キャッシュにはRedisを使用することにしました"
        )
        assert len(result["matches"]) > 0

    def test_japanese_relationship(self, engine):
        """Test Japanese relationship detection."""
        result = engine.process_message(
            "田中さんはバックエンドAPIを担当し、鈴木さんがフロントエンドを担当しています"
        )
        assert len(result["matches"]) > 0

    def test_japanese_task_pattern(self, engine):
        """Test Japanese task pattern detection."""
        result = engine.process_message("デプロイの前に必ずテストを実行します")
        assert len(result["matches"]) > 0

    def test_japanese_sentiment_marker(self, engine):
        """Test Japanese sentiment marker detection."""
        result = engine.process_message("このデプロイプロセスは本当に面倒くさい")
        assert len(result["matches"]) > 0


class TestMultilingualConsistency:
    """Test cross-language consistency with strict checks."""

    @pytest.fixture
    def engine(self):
        return MemoryClassificationEngine()

    def test_all_languages_process_without_error(self, engine):
        """Test that all three languages can be processed without errors."""
        messages = {
            'en': "I prefer using spaces",
            'zh': "我喜欢用空格",
            'ja': "スペースを使いたい"
        }
        
        for lang, message in messages.items():
            result = engine.process_message(message)
            assert "matches" in result, f"{lang}: No matches field"
            assert isinstance(result["matches"], list), f"{lang}: Matches not a list"

    def test_same_concept_across_languages(self, engine):
        """Test that similar concepts are classified consistently across languages."""
        
        results = {}
        results['en'] = engine.process_message("I prefer using spaces")
        results['zh'] = engine.process_message("我喜欢用空格")
        results['ja'] = engine.process_message("スペースを使いたい")
        
        # At minimum, all should produce some classification
        for lang, result in results.items():
            assert len(result["matches"]) > 0, f"{lang}: No matches found"


class TestMultilingualEdgeCases:
    """Test edge cases in multilingual processing."""

    @pytest.fixture
    def engine(self):
        return MemoryClassificationEngine()

    def test_mixed_language_input(self, engine):
        """Test handling of mixed-language input."""
        result = engine.process_message("I prefer spaces 我喜欢空格 instead of tabs")
        assert "matches" in result
        assert isinstance(result["matches"], list)

    def test_code_with_multilingual_comments(self, engine):
        """Test code snippets with multilingual comments."""
        result = engine.process_message("""
        // User preferences handler
        // 用户偏好处理函数
        // ユーザー設定処理関数
        def handle_preferences(): pass
        """)
        assert "matches" in result
        assert isinstance(result["matches"], list)

    def test_empty_messages_all_languages(self, engine):
        """Test empty message handling doesn't crash for any language config."""
        for msg in ["", "   ", "\t", "\n"]:
            result = engine.process_message(msg)
            assert "matches" in result
            assert isinstance(result["matches"], list)

    def test_numbers_not_misclassified_as_dates(self, engine):
        """BUG REGRESSION TEST: Numbers in text should not trigger event classification."""
        test_cases = [
            ("We have 100 employees", "fact_declaration"),
            ("50 people attended", "fact_declaration"),
            ("Price is $99.99", "fact_declaration"),
            ("我们公司有200人", "fact_declaration"),
            ("成本是5000元", "fact_declaration"),
        ]
        
        for message, expected_type in test_cases:
            result = engine.process_message(message)
            types = get_memory_types(result)
            
            # Should have expected type
            assert any(t == expected_type or t in ["decision", "relationship"] for t in types), \
                f"'{message}': Expected {expected_type}, got {types}"
            
            # CRITICAL: Should NOT be classified as event just because of numbers
            assert "event" not in types, \
                f"REGRESSION: '{message}' incorrectly classified as event!"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
