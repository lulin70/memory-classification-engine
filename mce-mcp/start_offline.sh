#!/bin/bash

# MCP Server offline startup script
# Uses local model cache to avoid network requests

# Set environment variables for offline mode
export HF_HOME="/Users/lin/trae_projects/memory-classification-engine/models"
export TRANSFORMERS_CACHE="/Users/lin/trae_projects/memory-classification-engine/models"
export SENTENCE_TRANSFORMERS_HOME="/Users/lin/trae_projects/memory-classification-engine/models"
export HF_DATASETS_OFFLINE="1"
export HF_EVALUATE_OFFLINE="1"

# Add src directory to Python path
export PYTHONPATH="/Users/lin/trae_projects/memory-classification-engine/src:$PYTHONPATH"

# Change to project directory
cd "/Users/lin/trae_projects/memory-classification-engine/mce-mcp"

# Start MCP Server
echo "🚀 Starting MCE MCP Server in offline mode..."
echo "   Model cache: $HF_HOME"
echo "   Offline mode: enabled"
echo ""

python3 -m mce_mcp_server.server