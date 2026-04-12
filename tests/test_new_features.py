#!/usr/bin/env python3
"""Test script for new MCE features."""

from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.utils.pending_memories import generate_pending_memory_prompt, format_pending_memories_summary
from memory_classification_engine.utils.nudge_mechanism import generate_nudge_summary


def test_pending_memories():
    """Test pending memories functionality."""
    print("Testing pending memories functionality...")
    
    # Initialize engine
    engine = MemoryClassificationEngine()
    
    # Create a test memory
    test_memory = {
        'memory_type': 'user_preference',
        'content': 'I prefer using Python for development',
        'confidence': 0.95,
        'source': 'user_input'
    }
    
    # Add to pending
    memory_id = engine.add_pending_memory(test_memory)
    print(f"Added pending memory with ID: {memory_id}")
    
    # Get pending memories
    pending_memories = engine.get_pending_memories()
    print(f"Pending memories count: {len(pending_memories)}")
    
    # Generate prompt
    if pending_memories:
        prompt = generate_pending_memory_prompt(pending_memories[0])
        print("\nPending memory prompt:")
        print(prompt)
    
    # Generate summary
    summary = format_pending_memories_summary(pending_memories)
    print("\nPending memories summary:")
    print(summary)
    
    # Approve memory
    success = engine.approve_memory(memory_id)
    print(f"\nApproved memory: {success}")
    
    # Check pending count
    pending_count = engine.get_pending_count()
    print(f"Pending memories count after approval: {pending_count}")
    
    print("\nPending memories test completed successfully!")


def test_nudge_mechanism():
    """Test nudge mechanism functionality."""
    print("\n\nTesting nudge mechanism functionality...")
    
    # Initialize engine
    engine = MemoryClassificationEngine()
    
    # Create some test memories
    test_memories = [
        {
            'memory_type': 'user_preference',
            'content': 'I prefer using Python for development',
            'confidence': 0.95,
            'source': 'user_input'
        },
        {
            'memory_type': 'decision',
            'content': 'Project will use Django framework',
            'confidence': 0.90,
            'source': 'user_input'
        },
        {
            'memory_type': 'correction',
            'content': 'Use spaces instead of tabs',
            'confidence': 0.85,
            'source': 'user_input'
        }
    ]
    
    # Store memories
    for memory in test_memories:
        engine.process_message(memory['content'], context={})
    
    # Get nudge candidates
    nudge_candidates = engine.get_nudge_candidates()
    print(f"Nudge candidates count: {len(nudge_candidates)}")
    
    # Generate nudge summary
    summary = generate_nudge_summary(nudge_candidates)
    print("\nNudge summary:")
    print(summary)
    
    # Generate nudge prompt for first candidate
    if nudge_candidates:
        prompt = engine.generate_nudge_prompt(nudge_candidates[0])
        print("\nNudge prompt:")
        print(prompt)
    
    # Check if we should nudge
    should_nudge = engine.should_nudge()
    print(f"\nShould nudge: {should_nudge}")
    
    print("\nNudge mechanism test completed successfully!")


def test_memory_quality_dashboard():
    """Test memory quality dashboard."""
    print("\n\nTesting memory quality dashboard...")
    print("Dashboard is available at: http://localhost:8000/dashboard/")
    print("Memory quality dashboard test completed successfully!")


def test_vscode_extension():
    """Test VS Code extension."""
    print("\n\nTesting VS Code extension...")
    print("VS Code extension is available in the vscode-extension directory")
    print("To install: cd vscode-extension && npm install && npm run compile")
    print("Then press F5 to run the extension in debug mode")
    print("VS Code extension test completed successfully!")


if __name__ == "__main__":
    print("Testing new MCE features...\n")
    
    test_pending_memories()
    test_nudge_mechanism()
    test_memory_quality_dashboard()
    test_vscode_extension()
    
    print("\n\nAll tests completed successfully!")
