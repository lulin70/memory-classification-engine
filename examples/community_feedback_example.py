#!/usr/bin/env python3
"""Community feedback functionality example for Memory Classification Engine"""

from memory_classification_engine.community.feedback_manager import feedback_manager
from memory_classification_engine.sdk import MemoryClassificationSDK

def main():
    print("Memory Classification Engine - Community Feedback Example")
    print("=" * 60)
    
    # Test 1: Using feedback manager directly
    print("\n1. Testing Feedback Manager Directly:")
    print("-" * 40)
    
    # Submit a bug report
    bug_result = feedback_manager.submit_feedback(
        user_id="user123",
        feedback_type="bug",
        content="Memory classification is not working for Chinese text",
        severity="high",
        metadata={"memory_id": "mem_123456", "language": "Chinese"}
    )
    print(f"Bug submission: {bug_result}")
    bug_id = bug_result.get("feedback_id")
    
    # Submit a feature request
    feature_result = feedback_manager.submit_feedback(
        user_id="user123",
        feedback_type="feature",
        content="Add support for custom classification rules",
        severity="medium",
        metadata={"priority": "high"}
    )
    print(f"Feature submission: {feature_result}")
    feature_id = feature_result.get("feedback_id")
    
    # Get feedback details
    bug_feedback = feedback_manager.get_feedback(bug_id)
    print(f"\nBug feedback details: {bug_feedback}")
    
    # List all feedback
    all_feedback = feedback_manager.list_feedback()
    print(f"\nAll feedback ({len(all_feedback)} items):")
    for f in all_feedback[:3]:  # Show first 3
        print(f"  - {f['id']}: {f['feedback_type']} - {f['status']}")
    
    # Update feedback status
    update_result = feedback_manager.update_feedback_status(
        feedback_id=bug_id,
        status="in_progress",
        user_id="admin",
        comment="Starting to work on this bug"
    )
    print(f"\nStatus update: {update_result}")
    
    # Reply to feedback
    reply_result = feedback_manager.reply_to_feedback(
        feedback_id=bug_id,
        user_id="support",
        content="We're investigating this issue. Please provide more details if possible."
    )
    print(f"Reply: {reply_result}")
    
    # Get feedback statistics
    stats = feedback_manager.get_feedback_stats()
    print(f"\nFeedback statistics: {stats}")
    
    # Test 2: Using SDK (simulated)
    print("\n2. Testing SDK Integration:")
    print("-" * 40)
    print("Note: SDK requires a running API server. This is a simulated example.")
    print("In a real scenario, you would initialize the SDK like this:")
    print("sdk = MemoryClassificationSDK(api_key='YOUR_API_KEY')")
    print("Then call methods like sdk.submit_feedback(), sdk.list_feedback(), etc.")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")

if __name__ == "__main__":
    main()
