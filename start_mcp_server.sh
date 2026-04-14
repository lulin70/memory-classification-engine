# 记忆内存引擎 MCP 服务器启动脚本

# 设置模型缓存路径
export SENTENCE_TRANSFORMERS_HOME=/Users/lin/trae_projects/memory-classification-engine/models
export TRANSFORMERS_CACHE=/Users/lin/trae_projects/memory-classification-engine/models
export HF_HOME=/Users/lin/trae_projects/memory-classification-engine/models

# 激活虚拟环境
source .venv/bin/activate

# 启动 MCP 服务器
cd /Users/lin/trae_projects/memory-classification-engine
python -m memory_classification_engine.integration.layer2_mcp.server
