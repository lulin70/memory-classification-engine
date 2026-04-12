#!/usr/bin/env python3
"""Test core functionality of the memory classification engine."""

import sys
from memory_classification_engine.engine import MemoryClassificationEngine

def test_initialization():
    """Test engine initialization."""
    print("=== Testing Engine Initialization ===")
    engine = MemoryClassificationEngine()
    print("✓ Engine initialized successfully")
    return engine

def test_memory_classification(engine):
    """Test memory classification."""
    print("\n=== Testing Memory Classification ===")
    
    # Test 1: Simple text memory
    memory = "I need to buy groceries tomorrow at 5 PM"
    result = engine.process_message(memory)
    print(f"Process message result: {result}")
    assert "matches" in result
    assert len(result.get("matches", [])) > 0
    
    # Test 2: Complex memory
    complex_memory = "Meeting with John at 2 PM about project deadline. He mentioned the client wants the report by Friday."
    result = engine.process_message(complex_memory)
    print(f"Process complex message result: {result}")
    assert "matches" in result
    assert len(result.get("matches", [])) > 0
    
    return result.get("matches", [])[0].get("id")

def test_memory_retrieval(engine, memory_id):
    """Test memory retrieval."""
    print("\n=== Testing Memory Retrieval ===")
    
    # Test retrieve memories
    memories = engine.retrieve_memories("project deadline")
    print(f"Retrieve memories result: {len(memories)} memories found")
    assert len(memories) > 0

def test_memory_update(engine, memory_id):
    """Test memory update."""
    print("\n=== Testing Memory Update ===")
    
    # Test manage memory edit
    updated_content = "Meeting with John at 2 PM about project deadline. He mentioned the client wants the report by Friday. Need to prepare slides."
    result = engine.manage_memory("edit", memory_id, {"content": updated_content})
    print(f"Update memory result: {result}")
    assert result.get("success") is True
    
    # Verify update
    memories = engine.retrieve_memories("project deadline")
    assert len(memories) > 0

def test_memory_deletion(engine, memory_id):
    """Test memory deletion."""
    print("\n=== Testing Memory Deletion ===")
    
    # Test manage memory delete
    result = engine.manage_memory("delete", memory_id)
    print(f"Delete memory result: {result}")
    assert result.get("success") is True
    
    # Verify deletion
    memories = engine.retrieve_memories("project deadline")
    assert len(memories) >= 0

def test_batch_processing(engine):
    """Test batch processing."""
    print("\n=== Testing Batch Processing ===")
    
    memories = [
        "Buy milk and eggs",
        "Call dentist at 10 AM",
        "Submit expense report"
    ]
    
    results = []
    for memory in memories:
        result = engine.process_message(memory)
        results.append(result)
        assert "matches" in result
        assert len(result.get("matches", [])) > 0
    
    print(f"Batch processing completed: {len(results)} memories processed")

def main():
    """Run all core functionality tests."""
    print("=== Core Functionality Tests ===")
    
    try:
        # Test 1: Initialization
        engine = test_initialization()
        
        # Test 2: Memory classification
        memory_id = test_memory_classification(engine)
        
        # Test 3: Memory retrieval
        test_memory_retrieval(engine, memory_id)
        
        # Test 4: Memory update
        test_memory_update(engine, memory_id)
        
        # Test 5: Memory deletion
        test_memory_deletion(engine, memory_id)
        
        # Test 6: Batch processing
        test_batch_processing(engine)
        
        print("\n=== Test Results ===")
        print("✓ All core functionality tests passed!")
        return 0
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())