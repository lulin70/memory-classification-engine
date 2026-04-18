#!/usr/bin/env python3
"""US-001: Verify actual API signatures"""
import sys
import inspect

from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

print('='*60)
print('API SIGNATURE VERIFICATION (US-001)')
print('='*60)

# 1. process_feedback
print('\n[1] process_feedback signature:')
try:
    sig = inspect.signature(engine.process_feedback)
    print(f'  {sig}')
except Exception as e:
    print(f'  ERROR: {e}')

# 2. register_agent
print('\n[2] register_agent signature:')
try:
    sig = inspect.signature(engine.register_agent)
    print(f'  {sig}')
except Exception as e:
    print(f'  ERROR: {e}')

# 3. compress_memories
print('\n[3] compress_memories signature:')
try:
    sig = inspect.signature(engine.compress_memories)
    print(f'  {sig}')
except Exception as e:
    print(f'  ERROR: {e}')

# 4. process_message return schema (sample)
print('\n[4] process_message return schema (sample):')
try:
    result = engine.process_message('test message for schema check')
    if isinstance(result, dict):
        print(f'  Top-level keys: {list(result.keys())}')
        if 'matches' in result and result['matches']:
            match0 = result['matches'][0]
            if isinstance(match0, dict):
                print(f'  matches[0] keys: {list(match0.keys())}')
                print(f'    type: {match0.get("type", "N/A")}')
                print(f'    memory_type: {match0.get("memory_type", "N/A")}')
                print(f'    confidence: {match0.get("confidence", "N/A")}')
            else:
                print(f'  matches[0] type: {type(match0)}')
        else:
            print('  matches is empty or not present')
except Exception as e:
    print(f'  ERROR: {e}')

# 5. ConfigManager location
print('\n[5] ConfigManager search:')
try:
    from memory_classification_engine.config import ConfigManager
    print('  Found at: memory_classification_engine.config.ConfigManager')
except ImportError as e:
    print(f'  Not at expected path: {e}')
    try:
        import memory_classification_engine
        subs = [x for x in dir(memory_classification_engine) if not x.startswith('_')]
        print(f'  Available: {subs[:20]}')
    except:
        pass

# 6. get_stats signature
print('\n[6] get_stats signature:')
try:
    sig = inspect.signature(engine.get_stats)
    print(f'  {sig}')
    stats = engine.get_stats()
    if isinstance(stats, dict):
        print(f'  Returns dict with keys: {list(stats.keys())[:10]}')
except Exception as e:
    print(f'  ERROR: {e}')

# 7. retrieve_memories signature
print('\n[7] retrieve_memories signature:')
try:
    sig = inspect.signature(engine.retrieve_memories)
    print(f'  {sig}')
except Exception as e:
    print(f'  ERROR: {e}')

# 8. export_memories signature
print('\n[8] export_memories signature:')
try:
    sig = inspect.signature(engine.export_memories)
    print(f'  {sig}')
except Exception as e:
    print(f'  ERROR: {e}')

print('\n' + '='*60)
print('VERIFICATION COMPLETE')
print('='*60)
