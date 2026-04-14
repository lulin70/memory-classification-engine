#!/usr/bin/env python3
"""
MCP Server launcher with offline mode support.
"""

import os
import sys

# Set environment variables for offline mode
os.environ['HF_HOME'] = '/Users/lin/trae_projects/memory-classification-engine/models'
os.environ['TRANSFORMERS_CACHE'] = '/Users/lin/trae_projects/memory-classification-engine/models'
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/Users/lin/trae_projects/memory-classification-engine/models'
os.environ['HF_DATASETS_OFFLINE'] = '1'
os.environ['HF_EVALUATE_OFFLINE'] = '1'

# Add src directory to Python path
sys.path.insert(0, '/Users/lin/trae_projects/memory-classification-engine/src')

# Change to project directory
os.chdir('/Users/lin/trae_projects/memory-classification-engine')

# Activate virtual environment
os.environ['PATH'] = f"/Users/lin/trae_projects/memory-classification-engine/.venv/bin:{os.environ['PATH']}"

print("🚀 Starting MCP Server with local model cache...")
print(f"   Model cache: {os.environ['HF_HOME']}")
print(f"   Offline mode: enabled")

# Import and start server
import asyncio
from memory_classification_engine.integration.layer2_mcp.server import main
asyncio.run(main())
