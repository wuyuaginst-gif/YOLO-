# 🐳 Docker 部署指南

OpenCV Platform 提供多种 Docker 部署方式，适配不同的使用场景。

## 📋 部署方式对比

| 部署方式 | 适用场景 | Python 版本 | 复杂度 | 推荐度 |
|---------|---------|------------|--------|--------|
| **docker-compose.prod.yml** | 🏢 生产环境（CentOS 7.5） | 3.12 | ⭐ | ⭐⭐⭐⭐⭐ |
| docker-compose.yml | 开发/测试环境 | 3.9 | ⭐⭐ | ⭐⭐⭐ |
| Dockerfile.lite | 轻量级部署（CPU Only） | 3.9 | ⭐⭐ | ⭐⭐⭐ |
| Dockerfile | 标准部署 | 3.9 | ⭐⭐ | ⭐⭐ |

## 🚀 快速开始（生产环境 - CentOS 7.5）

### 一键部署脚本

```bash
# 1. 克隆项目
git clone https://github.com/wuyuaginst-gif/YOLO-.git
cd YOLO-/webapp

# 2. 运行一键部署
chmod +x scripts/deploy-centos7.sh
./scripts/deploy-centos7.sh
```

脚本会自动完成：
- ✅ 检查系统环境（CentOS 7.5）
- ✅ 安装 Docker 和 Docker Compose
- ✅ 配置防火墙（开放 8000 端口）
- ✅ 构建 Docker 镜像（Python 3.12）
- ✅ 启动服务
- ✅ 健康检查验证

### 手动部署

```bash
# 1. 确保已安装 Docker 和 Docker Compose
docker --version
docker-compose --version

# 2. 创建环境配置
cp .env.example .env
vi .env  # 根据需要修改配置

# 3. 构建并启动
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. 检查状态
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

## 🧪 部署验证

### 自动化测试

```bash
./scripts/test-deployment.sh
```

测试包括：
- ✅ Docker 服务状态
- ✅ 容器运行状态
- ✅ 端口监听检查
- ✅ API 健康检查
- ✅ Web UI 访问测试

### 手动验证

```bash
# 1. 检查容器状态
docker ps | grep opencv-platform

# 2. 测试健康检查
curl http://localhost:8000/api/v1/system/health

# 3. 查看系统信息
curl http://localhost:8000/api/v1/system/info

# 4. 浏览器访问
# http://your-server-ip:8000
```

## 📦 Docker 镜像说明

### Dockerfile.prod（生产环境 - 推荐）

**特点：**
- 🐍 Python 3.12（最新稳定版）
- 🔒 非 root 用户运行（安全）
- 💾 优化的镜像大小
- 🏥 内置健康检查
- ⚡ 生产级配置

**使用场景：**
- CentOS 7.5 生产服务器
- 需要 Python 3.12 兼容性
- 注重安全和稳定性

**镜像大小：** ~2GB

### Dockerfile.lite（轻量级）

**特点：**
- 🐍 Python 3.9
- 💻 CPU Only PyTorch
- 📦 最小依赖
- ⚡ 快速构建

**使用场景：**
- 资源受限环境
- 仅 CPU 推理
- 快速测试部署

**镜像大小：** ~1.5GB

### Dockerfile（标准版）

**特点：**
- 🐍 Python 3.9
- 🖥️ 完整依赖
- 📚 标准配置

**使用场景：**
- 开发和测试
- 标准部署

**镜像大小：** ~2GB

## 🔧 常用管理命令

### 服务管理

```bash
# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 查看状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看资源使用
docker stats opencv-platform-prod
```

### 镜像管理

```bash
# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 无缓存构建
docker-compose -f docker-compose.prod.yml build --no-cache

# 查看镜像
docker images | grep opencv-platform

# 删除镜像
docker rmi opencv-platform:latest

# 清理未使用镜像
docker image prune -a
```

### 数据管理

```bash
# 备份数据
tar -czf opencv-data-$(date +%Y%m%d).tar.gz data/

# 恢复数据
tar -xzf opencv-data-YYYYMMDD.tar.gz

# 查看数据卷
docker volume ls
```

## 📊 资源配置

### 默认资源限制（docker-compose.prod.yml）

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # 最多使用 4 个 CPU 核心
      memory: 8G       # 最多使用 8GB 内存
    reservations:
      cpus: '2.0'      # 保证 2 个 CPU 核心
      memory: 4G       # 保证 4GB 内存
```

### 调整资源限制

根据服务器配置修改 `docker-compose.prod.yml`：

```yaml
# 低配置服务器（4 核 8GB）
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G

# 高配置服务器（16 核 32GB）
deploy:
  resources:
    limits:
      cpus: '8.0'
      memory: 16G
```

## 🔒 安全建议

### 1. 修改默认端口

```yaml
ports:
  - "8888:8000"  # 外部端口改为 8888
```

### 2. 限制访问 IP

```yaml
ports:
  - "127.0.0.1:8000:8000"  # 仅本地访问
```

### 3. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. 定期更新

```bash
# 更新代码
git pull origin main

# 重新构建
docker-compose -f docker-compose.prod.yml build

# 重启服务
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## 🐛 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs opencv-platform

# 检查容器状态
docker inspect opencv-platform-prod

# 进入容器调试
docker exec -it opencv-platform-prod /bin/bash
```

### 端口被占用

```bash
# 查找占用进程
sudo netstat -tulpn | grep 8000

# 停止占用进程
sudo kill -9 <PID>
```

### 镜像构建失败

```bash
# 清理构建缓存
docker builder prune -a

# 重新构建
docker-compose -f docker-compose.prod.yml build --no-cache
```

## 📚 相关文档

- [详细部署指南](DEPLOY_CENTOS7.md) - CentOS 7.5 完整部署步骤
- [部署检查清单](DEPLOYMENT_CHECKLIST.md) - 部署前后检查项
- [项目 README](README.md) - 项目概述和功能介绍

## 📞 技术支持

- 📖 文档: https://github.com/wuyuaginst-gif/YOLO-/blob/main/README.md
- 🐛 问题: https://github.com/wuyuaginst-gif/YOLO-/issues
- 💬 讨论: https://github.com/wuyuaginst-gif/YOLO-/discussions

---

**祝您部署顺利！** 🎉
