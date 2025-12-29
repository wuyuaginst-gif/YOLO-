#!/bin/bash

# OpenCV Platform 开发模式启动脚本

set -e

echo "========================================="
echo "  启动 OpenCV Platform (开发模式)"
echo "========================================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，请先运行: ./scripts/setup.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "📍 检查依赖..."
pip install -q -r requirements.txt

# 创建 .env 文件
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env 文件已创建"
fi

echo ""
echo "========================================="
echo "  ✓ 启动开发服务器"
echo "========================================="
echo ""

# 启动应用
python app.py
