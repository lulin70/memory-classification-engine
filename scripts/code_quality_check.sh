#!/bin/bash
# 代码质量检查脚本
# 运行所有代码质量检查工具

set -e

echo "=========================================="
echo "  代码质量检查"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 运行 flake8
echo -e "${YELLOW}1. 运行 flake8 (代码风格检查)...${NC}"
if command_exists flake8; then
    flake8 src/memory_classification_engine --config=.flake8 --count --statistics
    echo -e "${GREEN}✓ flake8 检查通过${NC}"
else
    echo -e "${YELLOW}⚠ flake8 未安装，跳过${NC}"
fi
echo ""

# 运行 pylint
echo -e "${YELLOW}2. 运行 pylint (代码规范检查)...${NC}"
if command_exists pylint; then
    pylint src/memory_classification_engine --rcfile=.pylintrc --score=y || true
    echo -e "${GREEN}✓ pylint 检查完成${NC}"
else
    echo -e "${YELLOW}⚠ pylint 未安装，跳过${NC}"
fi
echo ""

# 运行 mypy
echo -e "${YELLOW}3. 运行 mypy (类型检查)...${NC}"
if command_exists mypy; then
    mypy src/memory_classification_engine --config-file=mypy.ini || true
    echo -e "${GREEN}✓ mypy 检查完成${NC}"
else
    echo -e "${YELLOW}⚠ mypy 未安装，跳过${NC}"
fi
echo ""

# 运行测试
echo -e "${YELLOW}4. 运行测试套件...${NC}"
if command_exists pytest; then
    PYTHONPATH=src pytest tests/ -v --tb=short --cov=src/memory_classification_engine --cov-report=term-missing --cov-report=html:htmlcov || true
    echo -e "${GREEN}✓ 测试运行完成${NC}"
else
    echo -e "${YELLOW}⚠ pytest 未安装，跳过${NC}"
fi
echo ""

# 检查是否有未提交的更改
echo -e "${YELLOW}5. 检查 Git 状态...${NC}"
if [ -d ".git" ]; then
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${RED}✗ 有未提交的更改:${NC}"
        git status --short
    else
        echo -e "${GREEN}✓ 工作区干净${NC}"
    fi
else
    echo -e "${YELLOW}⚠ 不是 Git 仓库${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}  代码质量检查完成${NC}"
echo "=========================================="
echo ""
echo "提示: 如果有错误，请修复后再提交代码。"
echo "查看 htmlcov/index.html 获取详细的测试覆盖率报告。"
