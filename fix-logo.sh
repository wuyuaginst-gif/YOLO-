#!/bin/bash
# Logo 显示问题快速修复脚本

set -e

echo "🔧 开始修复 Docker 部署中的 Logo 显示问题..."
echo "================================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查本地文件
echo -e "\n${YELLOW}步骤 1: 检查本地 Logo 文件...${NC}"
if [ -f "frontend/static/company-logo.png" ]; then
    echo -e "${GREEN}✅ 本地 Logo 文件存在${NC}"
    ls -lh frontend/static/company-logo.png
else
    echo -e "${RED}❌ 错误: 本地 Logo 文件不存在！${NC}"
    exit 1
fi

# 2. 停止现有容器
echo -e "\n${YELLOW}步骤 2: 停止现有容器...${NC}"
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# 3. 清理 Docker 缓存
echo -e "\n${YELLOW}步骤 3: 清理 Docker 缓存...${NC}"
docker system prune -f

# 4. 重新构建镜像（不使用缓存）
echo -e "\n${YELLOW}步骤 4: 重新构建镜像（不使用缓存）...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# 5. 启动服务
echo -e "\n${YELLOW}步骤 5: 启动服务...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# 6. 等待服务启动
echo -e "\n${YELLOW}步骤 6: 等待服务启动（15秒）...${NC}"
for i in {15..1}; do
    echo -ne "${GREEN}$i ${NC}"
    sleep 1
done
echo ""

# 7. 检查容器状态
echo -e "\n${YELLOW}步骤 7: 检查容器状态...${NC}"
docker-compose -f docker-compose.prod.yml ps

# 8. 验证容器内文件
echo -e "\n${YELLOW}步骤 8: 验证容器内 Logo 文件...${NC}"
if docker exec opencv-platform-prod test -f /app/frontend/static/company-logo.png; then
    echo -e "${GREEN}✅ 容器内 Logo 文件存在${NC}"
    docker exec opencv-platform-prod ls -lh /app/frontend/static/company-logo.png
else
    echo -e "${RED}❌ 错误: 容器内 Logo 文件不存在！${NC}"
    echo -e "${YELLOW}尝试手动复制文件...${NC}"
    docker cp frontend/static/company-logo.png opencv-platform-prod:/app/frontend/static/
    docker exec -u root opencv-platform-prod chown appuser:appuser /app/frontend/static/company-logo.png
    docker exec -u root opencv-platform-prod chmod 644 /app/frontend/static/company-logo.png
    echo -e "${GREEN}✅ 文件已手动复制${NC}"
fi

# 9. 测试静态文件访问
echo -e "\n${YELLOW}步骤 9: 测试静态文件访问...${NC}"
sleep 3
HTTP_CODE=$(docker exec opencv-platform-prod curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/company-logo.png)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Logo 可以正常访问 (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Logo 访问失败 (HTTP $HTTP_CODE)${NC}"
fi

# 10. 显示访问信息
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✅ 修复完成！${NC}"
echo -e "\n请访问以下地址查看效果:"
echo -e "  🌐 主页: ${GREEN}http://localhost:8000${NC}"
echo -e "  📖 API 文档: ${GREEN}http://localhost:8000/api/docs${NC}"
echo -e "  🖼️  Logo 直接访问: ${GREEN}http://localhost:8000/static/company-logo.png${NC}"

# 11. 查看日志
echo -e "\n${YELLOW}查看服务日志 (Ctrl+C 退出):${NC}"
docker-compose -f docker-compose.prod.yml logs -f --tail=50
