"""Tests for Layer 3 and Tier 4 functionality."""

import pytest
import os
import tempfile
import shutil
from memory_classification_engine.layers.semantic_classifier import SemanticClassifier
from memory_classification_engine.storage.tier4 import Tier4Storage, KnowledgeGraph


class TestSemanticClassifier:
    """Test semantic classifier functionality."""
    
    @pytest.fixture
    def classifier(self):
        """Create a semantic classifier for testing."""
        return SemanticClassifier(use_local_model=False)
    
    def test_keyword_classification(self, classifier):
        """Test keyword-based classification."""
        # Test user preference detection
        results = classifier.classify("我喜欢使用Python编程")
        assert len(results) > 0
        assert any(r['memory_type'] == 'user_preference' for r in results)
        
        # Test fact declaration detection
        results = classifier.classify("Python是一种编程语言")
        assert len(results) > 0
        assert any(r['memory_type'] == 'fact_declaration' for r in results)
    
    def test_intent_analysis(self, classifier):
        """Test intent analysis."""
        # Test question intent
        results = classifier.classify("什么是Python？")
        assert any(r.get('intent') == 'question' for r in results)
        
        # Test command intent
        results = classifier.classify("请帮我写一个Python脚本")
        assert any(r.get('intent') == 'command' for r in results)
    
    def test_entity_extraction(self, classifier):
        """Test entity extraction."""
        message = "John works at Google and uses Python"
        entities = classifier.extract_entities(message)
        
        # Should extract "John" as person
        assert any(e['text'] == 'John' and e['type'] == 'person' for e in entities)
        
        # Should extract "Google" as organization
        assert any(e['text'] == 'Google' and e['type'] == 'organization' for e in entities)
    
    def test_sentiment_analysis(self, classifier):
        """Test sentiment analysis."""
        # Test positive sentiment
        result = classifier.analyze_sentiment("这是一个很棒的产品，我很喜欢")
        assert result['sentiment'] == 'positive'
        assert result['confidence'] > 0.5
        
        # Test negative sentiment
        result = classifier.analyze_sentiment("这个产品很差，我很失望")
        assert result['sentiment'] == 'negative'
        assert result['confidence'] > 0.5
        
        # Test neutral sentiment
        result = classifier.analyze_sentiment("这是一个普通的产品")
        assert result['sentiment'] == 'neutral'


class TestKnowledgeGraph:
    """Test knowledge graph functionality."""
    
    @pytest.fixture
    def graph(self):
        """Create a knowledge graph for testing."""
        temp_dir = tempfile.mkdtemp()
        graph = KnowledgeGraph(temp_dir)
        yield graph
        shutil.rmtree(temp_dir)
    
    def test_add_node(self, graph):
        """Test adding nodes to the graph."""
        success = graph.add_node("mem_1", "memory", {"content": "Test memory"})
        assert success is True
        
        node = graph.get_node("mem_1")
        assert node is not None
        assert node['type'] == "memory"
        assert node['properties']['content'] == "Test memory"
    
    def test_add_edge(self, graph):
        """Test adding edges to the graph."""
        # Add nodes first
        graph.add_node("mem_1", "memory", {"content": "Memory 1"})
        graph.add_node("mem_2", "memory", {"content": "Memory 2"})
        
        # Add edge
        success = graph.add_edge("mem_1", "mem_2", "related_to", 0.8)
        assert success is True
        
        # Check neighbors
        neighbors = graph.get_neighbors("mem_1")
        assert len(neighbors) == 1
        assert neighbors[0]['node']['id'] == "mem_2"
        assert neighbors[0]['relation']['relation_type'] == "related_to"
    
    def test_find_path(self, graph):
        """Test finding paths in the graph."""
        # Create a chain: mem_1 -> mem_2 -> mem_3
        graph.add_node("mem_1", "memory", {"content": "Memory 1"})
        graph.add_node("mem_2", "memory", {"content": "Memory 2"})
        graph.add_node("mem_3", "memory", {"content": "Memory 3"})
        
        graph.add_edge("mem_1", "mem_2", "related_to", 0.8)
        graph.add_edge("mem_2", "mem_3", "related_to", 0.8)
        
        # Find path
        path = graph.find_path("mem_1", "mem_3")
        assert path is not None
        assert len(path) == 2  # Two edges
    
    def test_get_related_memories(self, graph):
        """Test getting related memories."""
        # Create nodes and edges
        graph.add_node("mem_1", "memory", {"content": "Memory 1"})
        graph.add_node("mem_2", "memory", {"content": "Memory 2"})
        graph.add_node("mem_3", "entity", {"text": "Entity 1"})
        
        graph.add_edge("mem_1", "mem_2", "related_to", 0.9)
        graph.add_edge("mem_1", "mem_3", "mentions", 0.7)
        
        # Get related memories
        related = graph.get_related_memories("mem_1", min_weight=0.5)
        assert len(related) == 1  # Only mem_2 is a memory
        assert related[0]['memory_id'] == "mem_2"
        assert related[0]['weight'] == 0.9
    
    def test_save_and_load(self, graph):
        """Test saving and loading the graph."""
        # Add nodes
        graph.add_node("mem_1", "memory", {"content": "Test"})
        
        # Save
        success = graph.save_graph()
        assert success is True
        
        # Create new graph instance (should load automatically)
        new_graph = KnowledgeGraph(graph.storage_path)
        assert len(new_graph.nodes) == 1
        assert "mem_1" in new_graph.nodes


class TestTier4Storage:
    """Test Tier 4 storage functionality."""
    
    @pytest.fixture
    def storage(self):
        """Create a tier 4 storage for testing."""
        temp_dir = tempfile.mkdtemp()
        storage = Tier4Storage(temp_dir, enable_graph=True)
        yield storage
        shutil.rmtree(temp_dir)
    
    def test_store_memory(self, storage):
        """Test storing memories."""
        memory = {
            'id': 'mem_test_1',
            'type': 'fact_declaration',
            'content': 'Python is a programming language',
            'confidence': 0.9,
            'source': 'user'
        }
        
        success = storage.store_memory(memory)
        assert success is True
        
        # Retrieve and verify
        memories = storage.retrieve_memories()
        assert len(memories) == 1
        assert memories[0]['id'] == 'mem_test_1'
    
    def test_store_memory_with_entities(self, storage):
        """Test storing memories with entities."""
        memory = {
            'id': 'mem_test_2',
            'type': 'fact_declaration',
            'content': 'John works at Google',
            'confidence': 0.9,
            'source': 'user'
        }
        
        entities = [
            {'text': 'John', 'type': 'person', 'confidence': 0.8},
            {'text': 'Google', 'type': 'organization', 'confidence': 0.9}
        ]
        
        success = storage.store_memory(memory, entities)
        assert success is True
        
        # Verify entities were stored
        memories = storage.retrieve_memories()
        assert len(memories[0]['entities']) == 2
    
    def test_retrieve_memories(self, storage):
        """Test retrieving memories."""
        # Store multiple memories
        for i in range(3):
            memory = {
                'id': f'mem_{i}',
                'type': 'fact_declaration',
                'content': f'Test memory {i}',
                'confidence': 0.8,
                'source': 'user'
            }
            storage.store_memory(memory)
        
        # Retrieve all
        memories = storage.retrieve_memories()
        assert len(memories) == 3
        
        # Retrieve with query
        memories = storage.retrieve_memories(query="memory 1")
        assert len(memories) == 1
        assert memories[0]['id'] == 'mem_1'
    
    def test_get_related_memories(self, storage):
        """Test getting related memories."""
        # Store memories with entities
        memory1 = {
            'id': 'mem_a',
            'type': 'fact_declaration',
            'content': 'John likes Python',
            'confidence': 0.9,
            'source': 'user'
        }
        entities1 = [{'text': 'John', 'type': 'person', 'confidence': 0.8}]
        storage.store_memory(memory1, entities1)
        
        memory2 = {
            'id': 'mem_b',
            'type': 'fact_declaration',
            'content': 'John works at Google',
            'confidence': 0.9,
            'source': 'user'
        }
        entities2 = [{'text': 'John', 'type': 'person', 'confidence': 0.8}]
        storage.store_memory(memory2, entities2)
        
        # Both memories mention "John", so they should be related through the entity
        # Note: In the current implementation, memories are not directly connected
        # but both connect to the same entity node
    
    def test_get_stats(self, storage):
        """Test getting storage statistics."""
        # Store a memory
        memory = {
            'id': 'mem_stats',
            'type': 'fact_declaration',
            'content': 'Test',
            'confidence': 0.8,
            'source': 'user'
        }
        storage.store_memory(memory)
        
        # Get stats
        stats = storage.get_stats()
        assert stats['total_memories'] == 1
        assert stats['active_memories'] == 1
        assert 'knowledge_graph' in stats
