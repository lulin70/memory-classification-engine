#!/usr/bin/env python3
"""Core functionality tests for Memory Classification Engine"""

import pytest
from memory_classification_engine import MemoryClassificationEngine


def test_engine_initialization():
    """Test engine initialization."""
    engine = MemoryClassificationEngine()
    assert engine is not None


def test_process_message():
    """Test message processing."""
    engine = MemoryClassificationEngine()
    result = engine.process_message("I like to use camelCase in code")
    assert isinstance(result, dict)
    assert 'matches' in result


def test_retrieve_memories():
    """Test memory retrieval."""
    engine = MemoryClassificationEngine()
    # First process a message to create some memories
    engine.process_message("I like to use camelCase in code")
    # Then retrieve memories
    memories = engine.retrieve_memories("code")
    assert isinstance(memories, list)


def test_get_stats():
    """Test getting statistics."""
    engine = MemoryClassificationEngine()
    stats = engine.get_stats()
    assert isinstance(stats, dict)
    assert 'storage' in stats
    assert 'total_memories' in stats['storage']
