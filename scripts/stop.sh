#!/bin/bash

# OpenCV Platform 停止脚本

set -e

echo "========================================="
echo "  停止 OpenCV Platform"
echo "========================================="

echo ""
echo "📍 停止 Docker 容器..."
docker-compose down

echo ""
echo "✓ 服务已停止"
echo ""
