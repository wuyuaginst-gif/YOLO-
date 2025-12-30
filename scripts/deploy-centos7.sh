#!/bin/bash
# OpenCV Platform 部署脚本 - CentOS 7.5 优化版
# 使用 Python 3.12 + Docker

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印横幅
print_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         OpenCV Platform - 部署脚本                       ║
║         CentOS 7.5 + Python 3.12 + Docker               ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -eq 0 ]; then 
        log_warning "建议不要使用 root 用户运行，但继续执行..."
    fi
}

# 检查 CentOS 版本
check_os() {
    log_info "检查操作系统版本..."
    
    if [ -f /etc/centos-release ]; then
        os_version=$(cat /etc/centos-release)
        log_success "检测到: $os_version"
    else
        log_error "未检测到 CentOS 系统"
        exit 1
    fi
}

# 检查并安装 Docker
install_docker() {
    log_info "检查 Docker 安装状态..."
    
    if command -v docker &> /dev/null; then
        docker_version=$(docker --version)
        log_success "Docker 已安装: $docker_version"
        return 0
    fi
    
    log_warning "Docker 未安装，开始安装..."
    
    # 卸载旧版本
    sudo yum remove -y docker \
        docker-client \
        docker-client-latest \
        docker-common \
        docker-latest \
        docker-latest-logrotate \
        docker-logrotate \
        docker-engine 2>/dev/null || true
    
    # 安装依赖
    sudo yum install -y yum-utils \
        device-mapper-persistent-data \
        lvm2
    
    # 添加 Docker 仓库
    sudo yum-config-manager --add-repo \
        https://download.docker.com/linux/centos/docker-ce.repo
    
    # 安装 Docker
    sudo yum install -y docker-ce docker-ce-cli containerd.io
    
    # 启动 Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 添加当前用户到 docker 组
    sudo usermod -aG docker $USER || true
    
    log_success "Docker 安装完成"
    log_warning "请注销并重新登录以使 Docker 组权限生效，或运行: newgrp docker"
}

# 检查并安装 Docker Compose
install_docker_compose() {
    log_info "检查 Docker Compose 安装状态..."
    
    if command -v docker-compose &> /dev/null; then
        compose_version=$(docker-compose --version)
        log_success "Docker Compose 已安装: $compose_version"
        return 0
    fi
    
    log_warning "Docker Compose 未安装，开始安装..."
    
    # 下载 Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    
    # 添加执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose 2>/dev/null || true
    
    log_success "Docker Compose 安装完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    if command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --permanent --add-port=8000/tcp 2>/dev/null || true
        sudo firewall-cmd --reload 2>/dev/null || true
        log_success "防火墙已配置 (开放端口 8000)"
    else
        log_warning "未检测到 firewalld，跳过防火墙配置"
    fi
}

# 创建环境配置文件
create_env_file() {
    log_info "创建环境配置文件..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        log_success ".env 文件已创建"
        log_warning "请根据实际情况修改 .env 文件中的配置"
    else
        log_info ".env 文件已存在，跳过创建"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p data/datasets
    mkdir -p data/models
    mkdir -p data/exports
    mkdir -p data/uploads
    mkdir -p data/annotation_projects
    mkdir -p logs
    
    # 创建 .gitkeep 文件
    touch data/datasets/.gitkeep
    touch data/models/.gitkeep
    touch data/exports/.gitkeep
    touch data/uploads/.gitkeep
    touch data/annotation_projects/.gitkeep
    
    log_success "目录结构创建完成"
}

# 下载预训练模型
download_models() {
    log_info "检查预训练模型..."
    
    if [ ! -f data/models/yolov8n.pt ]; then
        log_info "下载 YOLOv8n 模型..."
        wget -q --show-progress \
            https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt \
            -O data/models/yolov8n.pt
        log_success "YOLOv8n 模型下载完成"
    else
        log_info "YOLOv8n 模型已存在"
    fi
}

# 构建 Docker 镜像
build_docker_image() {
    log_info "构建 Docker 镜像..."
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    log_success "Docker 镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "等待服务启动 (60秒)..."
    sleep 60
    
    log_info "检查服务状态..."
    docker-compose -f docker-compose.prod.yml ps
    
    log_info "检查健康状态..."
    max_retries=10
    retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -f http://localhost:8000/api/v1/system/health > /dev/null 2>&1; then
            log_success "服务健康检查通过"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log_info "等待服务启动... (${retry_count}/${max_retries})"
        sleep 5
    done
    
    log_warning "健康检查未通过，请检查日志: docker-compose -f docker-compose.prod.yml logs"
}

# 显示访问信息
show_access_info() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}║                  部署完成！                              ║${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}访问地址:${NC}"
    echo -e "  🌐 Web UI:    ${GREEN}http://$(hostname -I | awk '{print $1}'):8000${NC}"
    echo -e "  📖 API Docs:  ${GREEN}http://$(hostname -I | awk '{print $1}'):8000/api/docs${NC}"
    echo ""
    echo -e "${BLUE}常用命令:${NC}"
    echo -e "  查看日志: ${YELLOW}docker-compose -f docker-compose.prod.yml logs -f${NC}"
    echo -e "  停止服务: ${YELLOW}docker-compose -f docker-compose.prod.yml down${NC}"
    echo -e "  重启服务: ${YELLOW}docker-compose -f docker-compose.prod.yml restart${NC}"
    echo -e "  查看状态: ${YELLOW}docker-compose -f docker-compose.prod.yml ps${NC}"
    echo ""
}

# 主函数
main() {
    print_banner
    
    # 检查环境
    check_root
    check_os
    
    # 安装依赖
    install_docker
    install_docker_compose
    
    # 配置系统
    configure_firewall
    
    # 准备应用
    create_env_file
    create_directories
    
    # 下载模型 (可选)
    read -p "是否下载预训练模型 YOLOv8n? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        download_models
    fi
    
    # 构建和启动
    build_docker_image
    start_services
    
    # 检查服务
    check_services
    
    # 显示访问信息
    show_access_info
}

# 运行主函数
main "$@"
