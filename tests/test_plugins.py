"""Tests for plugin system functionality."""

import pytest
import tempfile
import os
from memory_classification_engine.plugins import PluginManager, BasePlugin
from memory_classification_engine.plugins.builtin.sentiment_analyzer import SentimentAnalyzerPlugin
from memory_classification_engine.plugins.builtin.entity_extractor import EntityExtractorPlugin


class TestPluginManager:
    """Test plugin manager functionality."""
    
    @pytest.fixture
    def plugin_manager(self):
        """Create a plugin manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield PluginManager(temp_dir)
    
    def test_initialization(self, plugin_manager):
        """Test plugin manager initialization."""
        assert plugin_manager is not None
        assert len(plugin_manager.get_plugins()) >= 2  # At least built-in plugins
    
    def test_builtin_plugins(self, plugin_manager):
        """Test built-in plugins are loaded."""
        plugins = plugin_manager.get_plugins()
        assert 'sentiment_analyzer' in plugins
        assert 'entity_extractor' in plugins
    
    def test_enable_disable_plugin(self, plugin_manager):
        """Test enabling and disabling plugins."""
        # Disable a plugin
        plugin_manager.disable_plugin('sentiment_analyzer')
        enabled = plugin_manager.get_enabled_plugins()
        assert 'sentiment_analyzer' not in enabled
        
        # Enable it back
        plugin_manager.enable_plugin('sentiment_analyzer')
        enabled = plugin_manager.get_enabled_plugins()
        assert 'sentiment_analyzer' in enabled
    
    def test_process_message(self, plugin_manager):
        """Test processing message through plugins."""
        message = "I love Python programming"
        results = plugin_manager.process_message(message)
        
        # Check sentiment analyzer results
        if 'sentiment_analyzer' in plugin_manager.get_enabled_plugins():
            assert 'sentiment_analyzer' in results
            assert results['sentiment_analyzer']['sentiment'] == 'positive'
        
        # Check entity extractor results
        if 'entity_extractor' in plugin_manager.get_enabled_plugins():
            assert 'entity_extractor' in results
            entities = results['entity_extractor']['entities']
            assert len(entities) > 0
    
    def test_process_memory(self, plugin_manager):
        """Test processing memory through plugins."""
        memory = {
            'id': 'test_mem_1',
            'content': 'Python is a great programming language',
            'type': 'fact_declaration',
            'confidence': 0.9
        }
        
        processed_memory = plugin_manager.process_memory(memory)
        
        # Should have sentiment analysis
        assert 'sentiment' in processed_memory
        assert processed_memory['sentiment']['sentiment'] == 'positive'
        
        # Should have entities
        assert 'entities' in processed_memory
        assert len(processed_memory['entities']) > 0
    
    def test_get_plugin_info(self, plugin_manager):
        """Test getting plugin information."""
        info = plugin_manager.get_plugin_info('sentiment_analyzer')
        assert info is not None
        assert info['name'] == 'sentiment_analyzer'
        assert info['version'] == '1.0.0'
    
    def test_get_all_plugin_info(self, plugin_manager):
        """Test getting all plugin information."""
        info_list = plugin_manager.get_all_plugin_info()
        assert len(info_list) >= 2
        assert any(info['name'] == 'sentiment_analyzer' for info in info_list)
        assert any(info['name'] == 'entity_extractor' for info in info_list)


class TestSentimentAnalyzerPlugin:
    """Test sentiment analyzer plugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create a sentiment analyzer plugin."""
        return SentimentAnalyzerPlugin()
    
    def test_initialization(self, plugin):
        """Test plugin initialization."""
        assert plugin.name == 'sentiment_analyzer'
        assert plugin.version == '1.0.0'
    
    def test_initialize(self, plugin):
        """Test plugin initialization with config."""
        config = {
            'positive_words': ['awesome', 'fantastic'],
            'negative_words': ['awful', 'terrible']
        }
        success = plugin.initialize(config)
        assert success is True
    
    def test_process_message_positive(self, plugin):
        """Test processing positive message."""
        message = "This is a great product, I love it!"
        result = plugin.process_message(message)
        assert result['sentiment'] == 'positive'
        assert result['confidence'] > 0.5
    
    def test_process_message_negative(self, plugin):
        """Test processing negative message."""
        message = "This product is terrible, I hate it!"
        result = plugin.process_message(message)
        assert result['sentiment'] == 'negative'
        assert result['confidence'] > 0.5
    
    def test_process_message_neutral(self, plugin):
        """Test processing neutral message."""
        message = "This product is okay."
        result = plugin.process_message(message)
        assert result['sentiment'] == 'neutral'
        assert result['confidence'] == 0.5
    
    def test_process_memory(self, plugin):
        """Test processing memory."""
        memory = {
            'id': 'test_mem_1',
            'content': 'The service was excellent!',
            'type': 'feedback'
        }
        processed = plugin.process_memory(memory)
        assert 'sentiment' in processed
        assert processed['sentiment']['sentiment'] == 'positive'


class TestEntityExtractorPlugin:
    """Test entity extractor plugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create an entity extractor plugin."""
        return EntityExtractorPlugin()
    
    def test_initialization(self, plugin):
        """Test plugin initialization."""
        assert plugin.name == 'entity_extractor'
        assert plugin.version == '1.0.0'
    
    def test_initialize(self, plugin):
        """Test plugin initialization with config."""
        config = {
            'common_words': ['Test', 'Demo']
        }
        success = plugin.initialize(config)
        assert success is True
    
    def test_process_message(self, plugin):
        """Test processing message with entities."""
        message = "John works at Google and uses Python"
        result = plugin.process_message(message)
        assert 'entities' in result
        entities = result['entities']
        
        # Should extract John as person
        assert any(e['text'] == 'John' and e['type'] == 'person' for e in entities)
        
        # Should extract Google as organization
        assert any(e['text'] == 'Google' and e['type'] == 'organization' for e in entities)
    
    def test_process_memory(self, plugin):
        """Test processing memory with entities."""
        memory = {
            'id': 'test_mem_1',
            'content': 'Mary is employed by Microsoft',
            'type': 'fact_declaration'
        }
        processed = plugin.process_memory(memory)
        assert 'entities' in processed
        entities = processed['entities']
        
        # Should extract Mary as person
        assert any(e['text'] == 'Mary' and e['type'] == 'person' for e in entities)
        
        # Should extract Microsoft as organization
        assert any(e['text'] == 'Microsoft' and e['type'] == 'organization' for e in entities)
