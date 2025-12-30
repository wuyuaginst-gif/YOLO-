#!/bin/bash

# OpenCV Platform - 开发模式快速启动脚本
# 使用热重载，代码修改立即生效，无需重新构建

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# 显示 banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   OpenCV Platform - Development Mode                     ║
║   基于 Ultralytics YOLO 的开源计算机视觉平台             ║
║                                                           ║
║   🔥 热重载模式：代码修改立即生效                        ║
║   📦 Docker 挂载：无需重新构建镜像                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# 检查 Docker
print_info "检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    print_error "Docker 未安装，请先安装 Docker"
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose 未安装，请先安装 Docker Compose"
fi

print_success "Docker 环境检查通过"

# 检查 .env 文件
print_info "检查环境变量配置..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        print_warning ".env 文件不存在，从 .env.example 创建"
        cp .env.example .env
        print_success ".env 文件已创建，请根据需要修改配置"
    else
        print_error ".env 文件不存在，且未找到 .env.example"
    fi
else
    print_success "环境变量配置文件存在"
fi

# 检查数据目录
print_info "检查数据目录..."
mkdir -p data/datasets data/models data/exports data/uploads data/annotation_projects logs
print_success "数据目录已就绪"

# 解析命令行参数
ACTION=${1:-"up"}

case $ACTION in
    build)
        print_info "构建开发镜像..."
        docker-compose -f docker-compose.dev.yml build
        print_success "镜像构建完成"
        ;;
    
    up|start)
        print_info "启动开发环境..."
        
        # 检查镜像是否存在
        if ! docker images | grep -q "opencv-platform.*dev"; then
            print_warning "开发镜像不存在，开始构建..."
            docker-compose -f docker-compose.dev.yml build
        fi
        
        # 启动服务
        docker-compose -f docker-compose.dev.yml up
        ;;
    
    up-d|start-d)
        print_info "后台启动开发环境..."
        
        # 检查镜像是否存在
        if ! docker images | grep -q "opencv-platform.*dev"; then
            print_warning "开发镜像不存在，开始构建..."
            docker-compose -f docker-compose.dev.yml build
        fi
        
        # 后台启动服务
        docker-compose -f docker-compose.dev.yml up -d
        
        print_success "开发环境已启动"
        print_info "查看日志: ./dev.sh logs"
        print_info "停止服务: ./dev.sh stop"
        
        echo ""
        echo -e "${GREEN}🌐 访问地址：${NC}"
        echo "  - 主页:          http://localhost:8000"
        echo "  - Solutions:     http://localhost:8000/solutions"
        echo "  - API 文档:      http://localhost:8000/api/docs"
        echo "  - Label Studio:  http://localhost:8087"
        ;;
    
    down|stop)
        print_info "停止开发环境..."
        docker-compose -f docker-compose.dev.yml down
        print_success "开发环境已停止"
        ;;
    
    restart)
        print_info "重启开发环境..."
        docker-compose -f docker-compose.dev.yml restart
        print_success "开发环境已重启"
        ;;
    
    logs)
        print_info "查看日志（Ctrl+C 退出）..."
        docker-compose -f docker-compose.dev.yml logs -f
        ;;
    
    status|ps)
        print_info "查看服务状态..."
        docker-compose -f docker-compose.dev.yml ps
        ;;
    
    shell|bash)
        print_info "进入容器 Shell..."
        docker exec -it opencv-platform-dev /bin/bash
        ;;
    
    clean)
        print_warning "清理开发环境（保留数据）..."
        read -p "确定要清理吗？(y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f docker-compose.dev.yml down
            docker rmi opencv-platform:dev || true
            print_success "清理完成"
        else
            print_info "已取消"
        fi
        ;;
    
    rebuild)
        print_info "重新构建并启动开发环境..."
        docker-compose -f docker-compose.dev.yml down
        docker-compose -f docker-compose.dev.yml build --no-cache
        docker-compose -f docker-compose.dev.yml up -d
        print_success "重新构建完成"
        ;;
    
    test)
        print_info "运行测试..."
        docker exec opencv-platform-dev python -m pytest tests/
        ;;
    
    help|--help|-h)
        echo "OpenCV Platform 开发模式脚本"
        echo ""
        echo "用法: ./dev.sh [command]"
        echo ""
        echo "命令:"
        echo "  build       - 构建开发镜像"
        echo "  up, start   - 启动开发环境（前台）"
        echo "  up-d        - 后台启动开发环境"
        echo "  stop, down  - 停止开发环境"
        echo "  restart     - 重启开发环境"
        echo "  logs        - 查看日志"
        echo "  status, ps  - 查看服务状态"
        echo "  shell, bash - 进入容器 Shell"
        echo "  clean       - 清理开发环境"
        echo "  rebuild     - 重新构建并启动"
        echo "  test        - 运行测试"
        echo "  help        - 显示帮助信息"
        echo ""
        echo "快速开始:"
        echo "  1. 首次使用: ./dev.sh build"
        echo "  2. 启动开发: ./dev.sh up-d"
        echo "  3. 查看日志: ./dev.sh logs"
        echo "  4. 修改代码: 代码会自动重载（1-2 秒）"
        echo "  5. 停止服务: ./dev.sh stop"
        echo ""
        echo "访问地址:"
        echo "  - http://localhost:8000        - 主页"
        echo "  - http://localhost:8000/api/docs - API 文档"
        ;;
    
    *)
        print_error "未知命令: $ACTION，使用 './dev.sh help' 查看帮助"
        ;;
esac
