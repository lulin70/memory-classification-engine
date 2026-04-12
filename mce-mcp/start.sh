#!/bin/bash

# Memory Classification Engine MCP Server Start Script

echo "Starting Memory Classification Engine MCP Server..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# 检查依赖
if ! python3 -c "import memory_classification_engine" &> /dev/null; then
    echo "Error: memory-classification-engine is not installed"
    echo "Please run: pip install -e .."
    exit 1
fi

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "Warning: config.yaml not found, using default configuration"
fi

# 启动服务器
echo "Starting MCP Server on http://0.0.0.0:8080"
echo "Available tools:"
echo "  - classify_message: Classify a message into memory types"
echo "  - retrieve_memories: Retrieve relevant memories"
echo "  - manage_forgetting: Manage memory forgetting process"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 server.py
