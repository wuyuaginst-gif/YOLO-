#!/bin/bash
# 部署验证脚本 - 快速检查部署状态

set -e

echo "=========================================="
echo "OpenCV Platform 部署验证"
echo "=========================================="
echo ""

# 检查容器是否运行
if ! docker ps | grep -q opencv-platform-dev; then
    echo "❌ 容器未运行"
    echo "请先启动: docker compose -f docker-compose.dev.yml up -d"
    exit 1
fi

echo "✅ 容器正在运行"
echo ""

# 检查关键依赖
echo "检查依赖包..."
TORCH_VERSION=$(docker exec opencv-platform-dev pip show torch 2>/dev/null | grep Version | cut -d' ' -f2)
ULTRA_VERSION=$(docker exec opencv-platform-dev pip show ultralytics 2>/dev/null | grep Version | cut -d' ' -f2)

if [ -n "$TORCH_VERSION" ] && [ -n "$ULTRA_VERSION" ]; then
    echo "✅ PyTorch: $TORCH_VERSION"
    echo "✅ Ultralytics: $ULTRA_VERSION"
else
    echo "❌ 依赖包缺失，需要重新构建镜像"
    exit 1
fi

echo ""

# 检查目录权限
echo "检查目录权限..."
if docker exec opencv-platform-dev test -w /app/data/uploads/; then
    echo "✅ uploads 目录可写"
else
    echo "⚠️  uploads 目录无写权限，尝试修复..."
    docker exec -u root opencv-platform-dev chmod -R 777 /app/data
    echo "✅ 权限已修复"
fi

echo ""

# 健康检查
echo "检查服务健康状态..."
HTTP_CODE=$(docker exec opencv-platform-dev curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/system/health 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API 服务正常"
else
    echo "❌ API 服务异常 (HTTP $HTTP_CODE)"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 部署验证通过！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  - Web UI:   http://localhost:8000"
echo "  - API 文档: http://localhost:8000/api/docs"
echo ""
echo "查看日志："
echo "  docker logs opencv-platform-dev -f"
