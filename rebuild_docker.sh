#!/bin/bash
# OpenCV Platform - Docker 镜像重建脚本
# 用于解决依赖包缺失问题

set -e  # 遇到错误立即退出

echo "=========================================="
echo "OpenCV Platform - Docker 镜像重建"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装！${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装！${NC}"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker 和 Docker Compose 已安装${NC}"
echo ""

# 显示当前镜像信息
echo -e "${BLUE}当前镜像信息:${NC}"
docker images | grep opencv-platform || echo "  未找到 opencv-platform 镜像"
echo ""

# 显示当前容器状态
echo -e "${BLUE}当前容器状态:${NC}"
docker ps -a | grep opencv-platform || echo "  未找到 opencv-platform 容器"
echo ""

# 询问用户是否继续
echo -e "${YELLOW}⚠️  此操作将：${NC}"
echo "  1. 停止并删除旧容器"
echo "  2. 删除旧镜像"
echo "  3. 重新构建镜像（不使用缓存）"
echo "  4. 启动新容器"
echo ""
echo -e "${YELLOW}注意：数据卷（data目录）不会被删除${NC}"
echo ""

read -p "是否继续？(y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 0
fi

echo ""
echo "=========================================="
echo "开始重建流程..."
echo "=========================================="
echo ""

# Step 1: 停止并删除容器和镜像
echo -e "${BLUE}Step 1/4: 停止并删除旧容器和镜像...${NC}"
docker compose -f docker-compose.dev.yml down --rmi all 2>/dev/null || {
    echo -e "${YELLOW}⚠️  没有找到运行中的服务，继续...${NC}"
}
echo -e "${GREEN}✅ 完成${NC}"
echo ""

# Step 2: 重新构建镜像（不使用缓存）
echo -e "${BLUE}Step 2/4: 重新构建镜像（不使用缓存）...${NC}"
echo "这可能需要几分钟时间，请耐心等待..."
docker compose -f docker-compose.dev.yml build --no-cache
echo -e "${GREEN}✅ 镜像构建完成${NC}"
echo ""

# Step 3: 启动服务
echo -e "${BLUE}Step 3/4: 启动服务...${NC}"
docker compose -f docker-compose.dev.yml up -d
echo -e "${GREEN}✅ 服务已启动${NC}"
echo ""

# 等待服务启动
echo "等待服务启动..."
sleep 5

# Step 4: 验证安装
echo -e "${BLUE}Step 4/4: 验证依赖包安装...${NC}"
echo ""

echo "检查 PyTorch:"
if docker exec opencv-platform-dev pip show torch &> /dev/null; then
    VERSION=$(docker exec opencv-platform-dev pip show torch | grep Version | cut -d' ' -f2)
    echo -e "${GREEN}✅ PyTorch ${VERSION} 已安装${NC}"
else
    echo -e "${RED}❌ PyTorch 未安装${NC}"
fi

echo "检查 Ultralytics:"
if docker exec opencv-platform-dev pip show ultralytics &> /dev/null; then
    VERSION=$(docker exec opencv-platform-dev pip show ultralytics | grep Version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Ultralytics ${VERSION} 已安装${NC}"
else
    echo -e "${RED}❌ Ultralytics 未安装${NC}"
fi

echo "检查 OpenCV:"
if docker exec opencv-platform-dev pip show opencv-python-headless &> /dev/null; then
    VERSION=$(docker exec opencv-platform-dev pip show opencv-python-headless | grep Version | cut -d' ' -f2)
    echo -e "${GREEN}✅ OpenCV ${VERSION} 已安装${NC}"
else
    echo -e "${RED}❌ OpenCV 未安装${NC}"
fi

echo ""
echo "=========================================="
echo "重建完成！"
echo "=========================================="
echo ""

# 显示服务状态
echo -e "${BLUE}服务状态:${NC}"
docker compose -f docker-compose.dev.yml ps
echo ""

# 显示访问信息
echo -e "${GREEN}🎉 服务已就绪！${NC}"
echo ""
echo "访问地址："
echo "  - Web UI:     http://localhost:8000"
echo "  - API 文档:   http://localhost:8000/api/docs"
echo "  - 健康检查:   http://localhost:8000/api/v1/system/health"
echo ""

echo "查看日志："
echo "  docker compose -f docker-compose.dev.yml logs -f"
echo ""

echo "测试推理接口："
echo "  curl -X POST http://localhost:8000/api/v1/inference/image \\"
echo "    -F 'file=@test_image.jpg' \\"
echo "    -F 'model_name=yolo11n.pt' \\"
echo "    -F 'confidence=0.25'"
echo ""

# 询问是否查看日志
read -p "是否查看服务日志？(y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose -f docker-compose.dev.yml logs -f
fi
