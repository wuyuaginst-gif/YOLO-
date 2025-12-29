#!/bin/bash

# OpenCV Platform 环境设置脚本

set -e

echo "========================================="
echo "  OpenCV Platform 环境设置"
echo "========================================="

# 检查 Python 版本
echo "📍 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python 已安装: $PYTHON_VERSION"
else
    echo "✗ Python 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 检查 Docker
echo ""
echo "📍 检查 Docker 环境..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✓ Docker 已安装: $DOCKER_VERSION"
else
    echo "✗ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 创建虚拟环境（可选）
echo ""
echo "📍 创建 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ 虚拟环境已创建"
else
    echo "✓ 虚拟环境已存在"
fi

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
echo ""
echo "📍 升级 pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "📍 安装 Python 依赖..."
pip install -r requirements.txt

# 创建 .env 文件
echo ""
echo "📍 创建环境配置文件..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env 文件已创建，请根据需要修改配置"
else
    echo "✓ .env 文件已存在"
fi

# 创建必要的目录
echo ""
echo "📍 创建数据目录..."
mkdir -p data/{datasets,models,exports,uploads}
echo "✓ 数据目录已创建"

echo ""
echo "========================================="
echo "  ✓ 环境设置完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 编辑 .env 文件配置参数"
echo "2. 使用 Docker Compose 启动服务:"
echo "   ./scripts/start.sh"
echo ""
echo "或者直接运行（开发模式）:"
echo "   python app.py"
echo ""
