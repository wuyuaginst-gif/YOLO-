#!/bin/bash

# OpenCV Platform 启动脚本（Docker）

set -e

echo "========================================="
echo "  启动 OpenCV Platform"
echo "========================================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "✗ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose
if ! docker compose version &> /dev/null; then
    echo "✗ Docker Compose 未安装或版本过低，请升级到 Docker Compose v2+"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，使用默认配置"
    cp .env.example .env
fi

# 启动服务
echo ""
echo "📍 启动 Docker 容器..."
docker compose up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker ps

echo ""
echo "========================================="
echo "  ✓ 服务已启动！"
echo "========================================="
echo ""
echo "访问地址:"
echo "  • OpenCV Platform: http://localhost:8000"
echo "  • API 文档:        http://localhost:8000/api/docs"
echo ""
echo "查看日志:"
echo "  docker compose logs -f"
echo ""
echo "停止服务:"
echo "  ./scripts/stop.sh"
echo ""
