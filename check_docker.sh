#!/bin/bash
echo "=========================================="
echo "Docker 镜像和容器诊断"
echo "=========================================="
echo ""

echo "1. 检查镜像构建时间："
docker images | grep opencv-platform

echo ""
echo "2. 检查容器是否在运行："
docker ps -a | grep opencv-platform

echo ""
echo "3. 检查容器内的 Python 包："
echo "   (如果容器正在运行)"
docker exec opencv-platform-dev pip list 2>/dev/null | grep -E "(torch|ultralytics|opencv)" || echo "   容器未运行或无法连接"

echo ""
echo "4. 检查 Dockerfile.prod 内容："
grep -E "(torch|ultralytics)" Dockerfile.prod

echo ""
echo "=========================================="
echo "可能的问题："
echo "=========================================="
echo "A. 镜像是旧的，没有重新构建"
echo "B. 使用了缓存的镜像层，跳过了包安装"
echo "C. 构建过程中包安装失败但没有报错"
echo ""
echo "解决方案："
echo "1. 重新构建镜像（不使用缓存）："
echo "   docker compose -f docker-compose.dev.yml build --no-cache"
echo ""
echo "2. 或者删除旧镜像后重新构建："
echo "   docker compose -f docker-compose.dev.yml down --rmi all"
echo "   docker compose -f docker-compose.dev.yml up -d --build"
