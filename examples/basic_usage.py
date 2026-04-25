"""Basic usage example for CarryMem.

This example demonstrates:
1. Creating a CarryMem instance
2. Classifying and storing memories
3. Recalling memories
4. Using context manager for proper resource cleanup
"""

from memory_classification_engine import CarryMem

def main():
    with CarryMem() as cm:
        print("=== CarryMem Basic Usage Example ===\n")

        print("1. Classifying and storing memories...")
        r1 = cm.classify_and_remember("I prefer dark mode for my IDE")
        r2 = cm.classify_and_remember("My favorite programming language is Python")
        r3 = cm.classify_and_remember("I usually work from 9 AM to 5 PM")
        print(f"  Stored: {r1['stored_count']} / {r1['total_processed']} memories\n")

        print("2. Recalling memories about 'programming'...")
        results = cm.recall_memories(query="programming language")
        for memory in results:
            print(f"  - {memory.content} (confidence: {memory.confidence:.2f})")
        print()

        print("3. Recalling memories about 'preferences'...")
        results = cm.recall_memories(query="preferences", filters={"type": "user_preference"})
        for memory in results:
            print(f"  - {memory.content} (type: {memory.type})")
        print()

        print("4. Memory statistics:")
        stats = cm.get_stats()
        print(f"  Total memories: {stats['total_count']}")
        print(f"  By type: {stats['by_type']}")
        print()

        print("5. User profile:")
        profile = cm.get_memory_profile()
        print(f"  {profile['summary']}")
        print()

if __name__ == "__main__":
    main()
