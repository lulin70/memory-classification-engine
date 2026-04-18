#!/usr/bin/env python3
"""Test script to reproduce Tier2Storage initialization issue."""

from memory_classification_engine.storage.tier2 import Tier2Storage

print("Testing Tier2Storage initialization...")
try:
    storage = Tier2Storage('./data/tier2')
    print("SUCCESS: Tier2Storage initialized successfully")
    print(f"Preferences: {len(storage.preferences)} items")
    print(f"Corrections: {len(storage.corrections)} items")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
