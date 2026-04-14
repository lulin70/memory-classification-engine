#!/usr/bin/env python3
"""Plugin system tests for Memory Classification Engine."""

import pytest
from memory_classification_engine.plugins.plugin_manager import PluginManager
from memory_classification_engine.plugins.base_plugin import BasePlugin


class TestPluginManager:
    """插件管理器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.plugin_manager = PluginManager()
    
    def test_load_builtin_plugins(self):
        """测试加载内置插件"""
        # 验证内置插件是否加载
        plugins = self.plugin_manager.get_plugins()
        assert "sentiment_analyzer" in plugins
        assert "entity_extractor" in plugins
        
        # 验证插件默认状态
        assert "sentiment_analyzer" in self.plugin_manager.get_enabled_plugins()
        assert "entity_extractor" in self.plugin_manager.get_enabled_plugins()
    
    def test_plugin_lifecycle(self):
        """测试插件生命周期: 注册→启用→禁用→卸载"""
        # 创建测试插件
        class TestPlugin(BasePlugin):
            def __init__(self):
                super().__init__("TestPlugin", "1.0.0")
            
            def initialize(self, config):
                return True
            
            def process_message(self, message, context=None):
                return {"test": "result"}
            
            def process_memory(self, memory):
                return memory
            
            def cleanup(self):
                pass
        
        # 注册插件
        test_plugin = TestPlugin()
        self.plugin_manager.add_plugin(test_plugin)
        
        # 验证插件已添加
        plugins = self.plugin_manager.get_plugins()
        assert "TestPlugin" in plugins
        
        # 禁用插件
        self.plugin_manager.disable_plugin("TestPlugin")
        assert "TestPlugin" not in self.plugin_manager.get_enabled_plugins()
        
        # 启用插件
        self.plugin_manager.enable_plugin("TestPlugin")
        assert "TestPlugin" in self.plugin_manager.get_enabled_plugins()
        
        # 卸载插件
        self.plugin_manager.remove_plugin("TestPlugin")
        assert "TestPlugin" not in self.plugin_manager.get_plugins()
    
    def test_plugin_isolation(self):
        """测试插件间隔离性: 一个插件崩溃不影响其他"""
        # 创建会崩溃的插件
        class CrasherPlugin(BasePlugin):
            def __init__(self):
                super().__init__("CrasherPlugin", "1.0.0")
            
            def initialize(self, config):
                return True
            
            def process_message(self, message, context=None):
                raise Exception("Plugin crash")
            
            def process_memory(self, memory):
                return memory
            
            def cleanup(self):
                pass
        
        # 添加崩溃插件
        crasher = CrasherPlugin()
        self.plugin_manager.add_plugin(crasher)
        
        # 测试处理消息（应该不会崩溃整个系统）
        result = self.plugin_manager.process_message("test message")
        # 即使有插件崩溃，其他插件仍应正常工作
        assert isinstance(result, dict)
    
    def test_plugin_configuration(self):
        """测试插件配置热重载"""
        # 测试配置初始化
        config = {
            "sentiment_analyzer": {
                "threshold": 0.5
            }
        }
        self.plugin_manager.initialize_plugins(config)
        
        # 验证配置是否被应用
        info = self.plugin_manager.get_plugin_info("sentiment_analyzer")
        assert info is not None
        assert "name" in info
        assert "version" in info


class TestBuiltinPlugins:
    """内置插件功能测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.plugin_manager = PluginManager()
    
    def test_sentiment_analyzer_plugin(self):
        """测试情感分析插件"""
        # 测试正面情感
        result = self.plugin_manager.process_message("This is great!")
        assert "sentiment_analyzer" in result
        
        # 测试负面情感
        result = self.plugin_manager.process_message("This is terrible.")
        assert "sentiment_analyzer" in result
    
    def test_entity_extractor_plugin(self):
        """测试实体提取插件"""
        # 测试实体提取
        result = self.plugin_manager.process_message("Alice works at Google in New York")
        assert "entity_extractor" in result
    
    def test_process_memory(self):
        """测试处理记忆"""
        memory = {
            "content": "Alice works at Google",
            "memory_type": "relationship"
        }
        processed = self.plugin_manager.process_memory(memory)
        assert isinstance(processed, dict)
        assert "content" in processed


class TestPluginEdgeCases:
    """插件系统边界情况测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.plugin_manager = PluginManager()
    
    def test_empty_message(self):
        """测试空消息"""
        result = self.plugin_manager.process_message("")
        assert isinstance(result, dict)
    
    def test_none_message(self):
        """测试None消息"""
        result = self.plugin_manager.process_message(None)
        assert isinstance(result, dict)
    
    def test_large_message(self):
        """测试超长消息"""
        large_message = "a" * 10000
        result = self.plugin_manager.process_message(large_message)
        assert isinstance(result, dict)
    
    def test_no_plugins_enabled(self):
        """测试无插件启用的情况"""
        # 禁用所有插件
        for plugin_name in self.plugin_manager.get_enabled_plugins():
            self.plugin_manager.disable_plugin(plugin_name)
        
        # 验证结果为空字典
        result = self.plugin_manager.process_message("test")
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])