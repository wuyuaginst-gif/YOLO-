#!/bin/bash
# OpenCV Platform 部署测试脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检测 Docker Compose 命令
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}✗${NC} Docker Compose 未安装"
    exit 1
fi

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OpenCV Platform - 部署测试                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 测试 1: 检查 Docker 服务
echo -e "${BLUE}[测试 1/7]${NC} 检查 Docker 服务..."
if docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker 服务正常"
else
    echo -e "${RED}✗${NC} Docker 服务异常"
    exit 1
fi

# 测试 2: 检查容器状态
echo -e "${BLUE}[测试 2/7]${NC} 检查容器状态..."
if docker ps | grep -q "opencv-platform-prod"; then
    echo -e "${GREEN}✓${NC} 容器运行中"
    docker ps | grep "opencv-platform-prod"
else
    echo -e "${RED}✗${NC} 容器未运行"
    exit 1
fi

# 测试 3: 检查容器健康状态
echo -e "${BLUE}[测试 3/7]${NC} 检查容器健康状态..."
health=$(docker inspect --format='{{.State.Health.Status}}' opencv-platform-prod 2>/dev/null || echo "none")
if [ "$health" = "healthy" ]; then
    echo -e "${GREEN}✓${NC} 容器健康状态: $health"
elif [ "$health" = "none" ]; then
    echo -e "${YELLOW}⚠${NC} 容器无健康检查配置"
else
    echo -e "${YELLOW}⚠${NC} 容器健康状态: $health"
fi

# 测试 4: 检查端口监听
echo -e "${BLUE}[测试 4/7]${NC} 检查端口监听..."
if netstat -tuln 2>/dev/null | grep -q ":8000" || ss -tuln 2>/dev/null | grep -q ":8000"; then
    echo -e "${GREEN}✓${NC} 端口 8000 正在监听"
else
    echo -e "${RED}✗${NC} 端口 8000 未监听"
    exit 1
fi

# 测试 5: 健康检查 API
echo -e "${BLUE}[测试 5/7]${NC} 测试健康检查 API..."
if curl -f -s http://localhost:8000/api/v1/system/health > /dev/null; then
    echo -e "${GREEN}✓${NC} 健康检查 API 正常"
    curl -s http://localhost:8000/api/v1/system/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/v1/system/health
else
    echo -e "${RED}✗${NC} 健康检查 API 失败"
    exit 1
fi

# 测试 6: 系统信息 API
echo -e "${BLUE}[测试 6/7]${NC} 测试系统信息 API..."
if curl -f -s http://localhost:8000/api/v1/system/info > /dev/null; then
    echo -e "${GREEN}✓${NC} 系统信息 API 正常"
    echo -e "\n${YELLOW}系统信息:${NC}"
    curl -s http://localhost:8000/api/v1/system/info | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/v1/system/info
else
    echo -e "${RED}✗${NC} 系统信息 API 失败"
    exit 1
fi

# 测试 7: Web UI 访问
echo -e "\n${BLUE}[测试 7/7]${NC} 测试 Web UI 访问..."
if curl -f -s http://localhost:8000/ > /dev/null; then
    echo -e "${GREEN}✓${NC} Web UI 可访问"
else
    echo -e "${RED}✗${NC} Web UI 访问失败"
    exit 1
fi

# 显示资源使用
echo -e "\n${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}资源使用情况:${NC}"
docker stats --no-stream opencv-platform-prod

# 显示容器日志（最后 20 行）
echo -e "\n${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}最近日志 (最后 20 行):${NC}"
docker logs --tail 20 opencv-platform-prod

# 测试总结
echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}║              ✓ 所有测试通过！                            ║${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}访问地址:${NC}"
echo -e "  🌐 Web UI:    ${GREEN}http://$(hostname -I | awk '{print $1}'):8000${NC}"
echo -e "  📖 API Docs:  ${GREEN}http://$(hostname -I | awk '{print $1}'):8000/api/docs${NC}"
echo -e "  🎨 数据标注:  ${GREEN}http://$(hostname -I | awk '{print $1}'):8000/annotation${NC}"
echo ""
