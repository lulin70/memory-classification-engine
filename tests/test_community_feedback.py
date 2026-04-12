#!/usr/bin/env python3
"""Test script for community feedback functionality."""

import os
import sys
import json
from src.memory_classification_engine.community.feedback_manager import feedback_manager


def test_submit_feedback():
    """Test submitting feedback."""
    print("Testing feedback submission...")
    
    # Submit a bug report
    bug_result = feedback_manager.submit_feedback(
        user_id="test_user_1",
        feedback_type="bug",
        content="Memory classification is not working for Chinese text",
        severity="high",
        metadata={"memory_id": "mem_123456", "language": "Chinese"}
    )
    print(f"Bug submission result: {bug_result}")
    assert bug_result.get("success") is True
    bug_id = bug_result.get("feedback_id")
    
    # Submit a feature request
    feature_result = feedback_manager.submit_feedback(
        user_id="test_user_2",
        feedback_type="feature",
        content="Add support for custom classification rules",
        severity="medium",
        metadata={"priority": "high"}
    )
    print(f"Feature submission result: {feature_result}")
    assert feature_result.get("success") is True
    feature_id = feature_result.get("feedback_id")
    
    # Submit a suggestion
    suggestion_result = feedback_manager.submit_feedback(
        user_id="test_user_3",
        feedback_type="suggestion",
        content="Improve memory retrieval performance",
        severity="low"
    )
    print(f"Suggestion submission result: {suggestion_result}")
    assert suggestion_result.get("success") is True
    suggestion_id = suggestion_result.get("feedback_id")
    
    return bug_id, feature_id, suggestion_id


def test_get_feedback():
    """Test getting feedback by ID."""
    print("\nTesting get feedback...")
    
    # Submit a test feedback
    result = feedback_manager.submit_feedback(
        user_id="test_user_4",
        feedback_type="question",
        content="How to integrate with Obsidian?"
    )
    feedback_id = result.get("feedback_id")
    
    # Get the feedback
    feedback = feedback_manager.get_feedback(feedback_id)
    print(f"Retrieved feedback: {feedback}")
    assert feedback is not None
    assert feedback.get("id") == feedback_id
    assert feedback.get("user_id") == "test_user_4"
    
    return feedback_id


def test_list_feedback():
    """Test listing feedback with filters."""
    print("\nTesting list feedback...")
    
    # List all feedback
    all_feedback = feedback_manager.list_feedback()
    print(f"All feedback ({len(all_feedback)} items):")
    for f in all_feedback:
        print(f"  - {f['id']}: {f['feedback_type']} - {f['status']}")
    
    # List open feedback
    open_feedback = feedback_manager.list_feedback(status="open")
    print(f"\nOpen feedback ({len(open_feedback)} items):")
    for f in open_feedback:
        print(f"  - {f['id']}: {f['feedback_type']}")
    
    # List bug feedback
    bug_feedback = feedback_manager.list_feedback(feedback_type="bug")
    print(f"\nBug feedback ({len(bug_feedback)} items):")
    for f in bug_feedback:
        print(f"  - {f['id']}: {f['content'][:50]}...")
    
    assert len(all_feedback) > 0


def test_update_feedback_status():
    """Test updating feedback status."""
    print("\nTesting update feedback status...")
    
    # Submit a test feedback
    result = feedback_manager.submit_feedback(
        user_id="test_user_5",
        feedback_type="bug",
        content="Test bug for status update"
    )
    feedback_id = result.get("feedback_id")
    
    # Update status to in_progress
    update_result = feedback_manager.update_feedback_status(
        feedback_id=feedback_id,
        status="in_progress",
        user_id="admin",
        comment="Starting to work on this bug"
    )
    print(f"Update status to in_progress: {update_result}")
    assert update_result.get("success") is True
    
    # Check if status was updated
    feedback = feedback_manager.get_feedback(feedback_id)
    assert feedback.get("status") == "in_progress"
    assert len(feedback.get("replies", [])) > 0
    
    # Update status to resolved
    update_result = feedback_manager.update_feedback_status(
        feedback_id=feedback_id,
        status="resolved",
        user_id="admin",
        comment="Bug has been fixed"
    )
    print(f"Update status to resolved: {update_result}")
    assert update_result.get("success") is True
    
    # Check if status was updated
    feedback = feedback_manager.get_feedback(feedback_id)
    assert feedback.get("status") == "resolved"


def test_reply_to_feedback():
    """Test replying to feedback."""
    print("\nTesting reply to feedback...")
    
    # Submit a test feedback
    result = feedback_manager.submit_feedback(
        user_id="test_user_6",
        feedback_type="question",
        content="How to use the SDK?"
    )
    feedback_id = result.get("feedback_id")
    
    # Add a reply
    reply_result = feedback_manager.reply_to_feedback(
        feedback_id=feedback_id,
        user_id="support",
        content="You can find SDK documentation in the docs/api/sdk.md file"
    )
    print(f"Reply result: {reply_result}")
    assert reply_result.get("success") is True
    
    # Check if reply was added
    feedback = feedback_manager.get_feedback(feedback_id)
    replies = feedback.get("replies", [])
    assert len(replies) > 0
    assert replies[0].get("user_id") == "support"
    assert "SDK documentation" in replies[0].get("content")


def test_get_feedback_stats():
    """Test getting feedback statistics."""
    print("\nTesting get feedback stats...")
    
    stats = feedback_manager.get_feedback_stats()
    print(f"Feedback statistics: {stats}")
    assert "total" in stats
    assert "status_counts" in stats
    assert "type_counts" in stats
    assert stats.get("total") > 0


def test_export_feedback():
    """Test exporting feedback."""
    print("\nTesting export feedback...")
    
    export_filename = "test_feedback_export.json"
    export_result = feedback_manager.export_feedback(export_filename)
    print(f"Export result: {export_result}")
    assert export_result.get("success") is True
    
    # Check if file was created
    assert os.path.exists(export_filename)
    
    # Read and verify the exported data
    with open(export_filename, 'r', encoding='utf-8') as f:
        exported_data = json.load(f)
    
    print(f"Exported data: {exported_data.keys()}")
    assert "exported_at" in exported_data
    assert "total_feedback" in exported_data
    assert "feedback" in exported_data
    assert exported_data.get("total_feedback") > 0
    
    # Clean up
    if os.path.exists(export_filename):
        os.remove(export_filename)


def main():
    """Run all tests."""
    print("Starting community feedback tests...")
    
    try:
        # Test 1: Submit feedback
        bug_id, feature_id, suggestion_id = test_submit_feedback()
        print(f"✓ Test 1 passed: Submitted feedback with IDs: {bug_id}, {feature_id}, {suggestion_id}")
        
        # Test 2: Get feedback
        feedback_id = test_get_feedback()
        print(f"✓ Test 2 passed: Retrieved feedback {feedback_id}")
        
        # Test 3: List feedback
        test_list_feedback()
        print("✓ Test 3 passed: Listed feedback with filters")
        
        # Test 4: Update feedback status
        test_update_feedback_status()
        print("✓ Test 4 passed: Updated feedback status")
        
        # Test 5: Reply to feedback
        test_reply_to_feedback()
        print("✓ Test 5 passed: Replied to feedback")
        
        # Test 6: Get feedback stats
        test_get_feedback_stats()
        print("✓ Test 6 passed: Got feedback statistics")
        
        # Test 7: Export feedback
        test_export_feedback()
        print("✓ Test 7 passed: Exported feedback")
        
        print("\n🎉 All tests passed!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
