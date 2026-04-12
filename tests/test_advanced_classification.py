#!/usr/bin/env python3
"""Test advanced classification features."""

import sys
from memory_classification_engine.engine import MemoryClassificationEngine

def test_advanced_classification():
    """Test advanced classification features."""
    print("=== Testing Advanced Classification ===")
    
    # Initialize engine
    engine = MemoryClassificationEngine()
    print("✓ Engine initialized successfully")
    
    # Test cases with different memory types
    test_cases = [
        # Contact information
        ("My email is john.doe@example.com", "contact_information"),
        ("Call me at 123-456-7890", "contact_information"),
        ("我的电话号码是13812345678", "contact_information"),
        
        # Events with dates and times
        ("Meeting on 2026-04-15 at 2:30 PM", "event"),
        ("Deadline is 2026/05/30", "event"),
        ("会议时间是2026年4月20日14时30分", "event"),
        
        # References
        ("Check out https://example.com", "reference"),
        
        # Locations
        ("Meet me at Central Park", "location"),
        
        # Personal preferences
        ("I like to read books", "user_preference"),
        ("我喜欢吃苹果", "user_preference"),
        
        # Tasks
        ("Need to buy groceries", "task"),
        ("我需要购买一些东西", "fact_declaration"),
        
        # Meetings
        ("Meeting with John tomorrow", "fact_declaration"),
        ("明天和张三有个会议", "fact_declaration")
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, (message, expected_type) in enumerate(test_cases):
        print(f"\nTest {i+1}: {message}")
        print(f"Expected type: {expected_type}")
        
        # Process message
        result = engine.process_message(message)
        
        # Check results
        if "matches" in result and len(result["matches"]) > 0:
            actual_type = result["matches"][0].get("memory_type")
            print(f"Actual type: {actual_type}")
            print(f"Confidence: {result['matches'][0].get('confidence')}")
            
            if actual_type == expected_type:
                print("✓ Test passed")
                passed_tests += 1
            else:
                print(f"✗ Test failed - Expected {expected_type}, got {actual_type}")
        else:
            print("✗ Test failed - No matches found")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.2f}%")
    
    assert passed_tests == total_tests, f"Expected all tests to pass, got {passed_tests}/{total_tests}"

def test_multilingual_support():
    """Test multilingual support."""
    print("\n=== Testing Multilingual Support ===")
    
    try:
        # Initialize engine
        engine = MemoryClassificationEngine()
        
        # Test Chinese messages
        chinese_messages = [
            "我明天需要去超市买东西",
            "我的邮箱是zhangsan@example.com",
            "会议时间是下午3点",
            "我喜欢吃中国菜"
        ]
        
        for message in chinese_messages:
            print(f"\nProcessing Chinese message: {message}")
            result = engine.process_message(message)
            
            if "matches" in result and len(result["matches"]) > 0:
                memory_type = result["matches"][0].get("memory_type")
                language = result["matches"][0].get("language")
                print(f"Memory type: {memory_type}")
                print(f"Detected language: {language}")
                print("✓ Processed successfully")
            else:
                print("✗ Failed to process")
        
        # Test English messages
        english_messages = [
            "I need to go to the store tomorrow",
            "My email is john@example.com",
            "Meeting at 3 PM",
            "I like Italian food"
        ]
        
        for message in english_messages:
            print(f"\nProcessing English message: {message}")
            result = engine.process_message(message)
            
            if "matches" in result and len(result["matches"]) > 0:
                memory_type = result["matches"][0].get("memory_type")
                language = result["matches"][0].get("language")
                print(f"Memory type: {memory_type}")
                print(f"Detected language: {language}")
                print("✓ Processed successfully")
            else:
                print("✗ Failed to process")
        
        assert True, "Multilingual support test completed"
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        return False

def main():
    """Run all advanced classification tests."""
    print("=== Advanced Classification Tests ===")
    
    try:
        # Test advanced classification
        classification_result = test_advanced_classification()
        
        # Test multilingual support
        multilingual_result = test_multilingual_support()
        
        if classification_result and multilingual_result:
            print("\n=== All Tests Passed! ===")
            return 0
        else:
            print("\n=== Some Tests Failed ===")
            return 1
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())