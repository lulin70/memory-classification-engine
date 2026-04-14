#!/usr/bin/env python3
"""Classification pipeline integration tests for Memory Classification Engine."""

import pytest
from memory_classification_engine.coordinators.classification_pipeline import ClassificationPipeline
from memory_classification_engine.utils.config import ConfigManager


class TestClassificationPipeline:
    """分类管道集成测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = ConfigManager()
        self.pipeline = ClassificationPipeline(self.config)
    
    def test_layer1_rule_match_priority(self):
        """测试 Layer1 规则匹配优先于 Layer2/3"""
        # 测试明确的规则匹配
        message = "My email is test@example.com"
        result = self.pipeline.classify(message)
        
        # 应该匹配到 contact_information 类型
        assert len(result) > 0
        memory_types = [match['memory_type'] for match in result]
        assert 'contact_information' in memory_types
    
    def test_layer2_pattern_analysis_fallback(self):
        """测试 Layer2 在 Layer1 未匹配时触发"""
        # 测试模式分析
        message = "Alice handles the backend API"
        result = self.pipeline.classify(message)
        
        # 应该匹配到 relationship 类型
        assert len(result) > 0
        memory_types = [match['memory_type'] for match in result]
        assert 'relationship' in memory_types
    
    def test_layer3_semantic_last_resort(self):
        """测试 Layer3 作为最后手段"""
        # 测试语义分类（需要依赖模型）
        message = "The weather is nice today"
        result = self.pipeline.classify(message)
        
        # 应该有分类结果
        assert isinstance(result, list)
    
    def test_confidence_score_degradation(self):
        """测试置信度随层级递减"""
        # 测试规则匹配的高置信度
        email_message = "My email is test@example.com"
        email_result = self.pipeline.classify(email_message)
        if email_result:
            email_confidence = email_result[0].get('confidence', 0)
            assert email_confidence > 0.8
        
        # 测试默认分类的较低置信度
        general_message = "Hello world"
        general_result = self.pipeline.classify_with_defaults(general_message, "en")
        assert len(general_result) > 0
        general_confidence = general_result[0].get('confidence', 1)
        assert general_confidence < 0.6
    
    def test_default_classification_fallback(self):
        """测试默认分类回退"""
        # 测试无匹配时的默认分类
        message = "Random text with no specific pattern"
        result = self.pipeline.classify_with_defaults(message, "en")
        
        # 应该有默认分类结果
        assert len(result) > 0
        assert result[0]['memory_type'] == 'fact_declaration'
        assert result[0]['source'] == 'default:general'
    
    def test_preference_keyword_classification(self):
        """测试偏好关键词分类"""
        # 测试偏好关键词
        message = "I prefer using spaces over tabs"
        result = self.pipeline.classify_with_defaults(message, "en")
        
        # 应该识别为 user_preference
        assert len(result) > 0
        assert result[0]['memory_type'] == 'user_preference'
        assert 'preference' in result[0]['source']
    
    def test_correction_keyword_classification(self):
        """测试修正关键词分类"""
        # 测试修正关键词
        message = "That approach is wrong"
        result = self.pipeline.classify_with_defaults(message, "en")
        
        # 应该识别为 correction
        assert len(result) > 0
        assert result[0]['memory_type'] == 'correction'
    
    def test_decision_keyword_classification(self):
        """测试决策关键词分类"""
        # 测试决策关键词
        message = "Let's use Redis for caching"
        result = self.pipeline.classify_with_defaults(message, "en")
        
        # 应该识别为 decision
        assert len(result) > 0
        assert result[0]['memory_type'] == 'decision'
        assert 'decision' in result[0]['source']


class TestCrossLanguagePipeline:
    """跨语言分类管道测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = ConfigManager()
        self.pipeline = ClassificationPipeline(self.config)
    
    def test_mixed_language_input(self):
        """测试混合语言输入"""
        # 测试中英文混合
        message = "I love 中国 food"
        result = self.pipeline.classify_with_defaults(message, "en")
        
        # 应该有分类结果
        assert len(result) > 0
    
    def test_chinese_classification(self):
        """测试中文分类"""
        # 测试中文偏好
        message = "我喜欢用空格"
        result = self.pipeline.classify_with_defaults(message, "zh")
        
        # 应该识别为 user_preference
        assert len(result) > 0
        assert result[0]['memory_type'] == 'user_preference'
    
    def test_japanese_classification(self):
        """测试日文分类"""
        # 测试日文偏好
        message = "私はスペースを使いたい"
        result = self.pipeline.classify_with_defaults(message, "ja")
        
        # 应该有分类结果
        assert len(result) > 0


class TestPipelineEdgeCases:
    """分类管道边界情况测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = ConfigManager()
        self.pipeline = ClassificationPipeline(self.config)
    
    def test_empty_message(self):
        """测试空消息"""
        result = self.pipeline.classify("")
        assert result == []
        
        # 测试默认分类
        result_with_default = self.pipeline.classify_with_defaults("", "en")
        assert len(result_with_default) > 0
    
    def test_very_long_message(self):
        """测试超长消息"""
        long_message = "a" * 10000
        result = self.pipeline.classify(long_message)
        assert isinstance(result, list)
    
    def test_special_characters(self):
        """测试特殊字符"""
        message = "!@#$%^&*()"
        result = self.pipeline.classify_with_defaults(message, "en")
        assert len(result) > 0
    
    def test_none_message(self):
        """测试None消息"""
        result = self.pipeline.classify(None)
        assert result == []
        
        # 测试默认分类
        result_with_default = self.pipeline.classify_with_defaults(None, "en")
        assert len(result_with_default) > 0


class TestPipelineExecutionContext:
    """执行上下文测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = ConfigManager()
        self.pipeline = ClassificationPipeline(self.config)
    
    def test_execution_context_with_feedback(self):
        """测试带反馈的执行上下文"""
        # 测试带反馈信号的执行上下文
        message = "Alice works at Google"
        execution_context = {
            "feedback_signals": {
                "positive": ["relationship"],
                "negative": ["fact_declaration"]
            }
        }
        
        result = self.pipeline.classify(message, execution_context=execution_context)
        assert isinstance(result, list)
    
    def test_context_integration(self):
        """测试上下文集成"""
        # 测试带上下文的分类
        message = "Meeting tomorrow"
        context = {
            "user_id": "user1",
            "tenant_id": "tenant1",
            "previous_messages": ["What's the plan for tomorrow?"]
        }
        
        result = self.pipeline.classify(message, context=context)
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])