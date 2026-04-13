#!/bin/bash
# MCP Server startup script for TRAE
# This script sets up the environment and starts the MCP server

# Set environment variables for offline mode
export HF_HOME="/Users/lin/Documents/trae_projects/memory-classification-engine/models"
export TRANSFORMERS_CACHE="/Users/lin/Documents/trae_projects/memory-classification-engine/models"
export SENTENCE_TRANSFORMERS_HOME="/Users/lin/Documents/trae_projects/memory-classification-engine/models"
export HF_DATASETS_OFFLINE="1"
export HF_EVALUATE_OFFLINE="1"

# Change to project directory
cd "/Users/lin/Documents/trae_projects/memory-classification-engine"

# Activate virtual environment and start server
exec .venv/bin/python -m memory_classification_engine.integration.layer2_mcp.server
