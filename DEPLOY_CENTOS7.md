# OpenCV Platform - CentOS 7.5 部署指南

本文档提供在 CentOS 7.5 服务器上使用 Docker 部署 OpenCV Platform 的完整指南。

## 📋 系统要求

### 硬件要求
- **CPU**: 4 核心或以上（推荐 8 核心）
- **内存**: 8GB 或以上（推荐 16GB）
- **硬盘**: 50GB 可用空间（推荐 100GB）
- **GPU**: 可选（用于加速训练和推理）

### 软件要求
- **操作系统**: CentOS 7.5 或以上
- **Docker**: 20.10 或以上
- **Docker Compose**: 2.0 或以上
- **Python**: 3.12（容器内）

## 🚀 快速部署（一键脚本）

### 1. 下载项目代码

```bash
# 使用 Git 克隆
git clone https://github.com/wuyuaginst-gif/YOLO-.git
cd YOLO-/webapp

# 或者下载 ZIP 解压
wget https://github.com/wuyuaginst-gif/YOLO-/archive/refs/heads/main.zip
unzip main.zip
cd YOLO--main/webapp
```

### 2. 运行一键部署脚本

```bash
# 给脚本执行权限
chmod +x scripts/deploy-centos7.sh

# 运行部署脚本（会自动安装 Docker、Docker Compose 并启动服务）
./scripts/deploy-centos7.sh
```

脚本会自动完成：
- ✅ 检查 CentOS 版本
- ✅ 安装 Docker 和 Docker Compose
- ✅ 配置防火墙（开放 8000 端口）
- ✅ 创建必要的目录结构
- ✅ 构建 Docker 镜像（Python 3.12）
- ✅ 启动服务
- ✅ 健康检查

### 3. 访问应用

部署成功后，访问以下地址：

- **Web UI**: `http://your-server-ip:8000`
- **API 文档**: `http://your-server-ip:8000/api/docs`

## 📖 手动部署（分步指南）

如果您希望手动控制每个步骤，请参考以下指南。

### 步骤 1: 安装 Docker

```bash
# 卸载旧版本
sudo yum remove -y docker docker-client docker-client-latest docker-common \
    docker-latest docker-latest-logrotate docker-logrotate docker-engine

# 安装依赖
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加 Docker 仓库
sudo yum-config-manager --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

### 步骤 2: 安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 创建软链接
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# 验证安装
docker-compose --version
```

### 步骤 3: 配置防火墙

```bash
# 开放 8000 端口
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 或者禁用防火墙（不推荐）
# sudo systemctl stop firewalld
# sudo systemctl disable firewalld
```

### 步骤 4: 准备应用

```bash
# 进入项目目录
cd /path/to/YOLO-/webapp

# 创建环境配置文件
cp .env.example .env

# 编辑配置文件（根据实际情况修改）
vi .env

# 创建必要的目录
mkdir -p data/{datasets,models,exports,uploads,annotation_projects}
mkdir -p logs
```

### 步骤 5: 构建镜像

```bash
# 使用生产环境配置构建镜像
docker-compose -f docker-compose.prod.yml build

# 或者使用无缓存构建
docker-compose -f docker-compose.prod.yml build --no-cache
```

### 步骤 6: 启动服务

```bash
# 后台启动服务
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 步骤 7: 验证部署

```bash
# 检查健康状态
curl http://localhost:8000/api/v1/system/health

# 查看系统信息
curl http://localhost:8000/api/v1/system/info
```

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

### 数据管理

```bash
# 备份数据目录
tar -czf opencv-data-backup-$(date +%Y%m%d).tar.gz data/

# 恢复数据
tar -xzf opencv-data-backup-YYYYMMDD.tar.gz

# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune
```

### 更新应用

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose -f docker-compose.prod.yml build

# 重启服务
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## 🐛 故障排查

### 问题 1: Docker 服务无法启动

```bash
# 检查 Docker 服务状态
sudo systemctl status docker

# 查看 Docker 日志
sudo journalctl -u docker

# 重启 Docker 服务
sudo systemctl restart docker
```

### 问题 2: 容器无法启动

```bash
# 查看容器日志
docker-compose -f docker-compose.prod.yml logs opencv-platform

# 进入容器调试
docker exec -it opencv-platform-prod /bin/bash

# 检查容器状态
docker inspect opencv-platform-prod
```

### 问题 3: 端口被占用

```bash
# 检查端口占用
sudo netstat -tulpn | grep 8000

# 或使用 ss 命令
sudo ss -tulpn | grep 8000

# 停止占用端口的进程
sudo kill -9 <PID>
```

### 问题 4: 内存不足

```bash
# 查看内存使用
free -h

# 调整 Docker 内存限制（docker-compose.prod.yml）
deploy:
  resources:
    limits:
      memory: 4G  # 降低内存限制
```

### 问题 5: 磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 清理 Docker 镜像
docker image prune -a

# 清理 Docker 容器
docker container prune

# 清理 Docker 卷
docker volume prune
```

## 🔒 安全建议

### 1. 修改默认端口

编辑 `docker-compose.prod.yml`：

```yaml
ports:
  - "8888:8000"  # 将外部端口改为 8888
```

### 2. 配置 HTTPS

使用 Nginx 反向代理：

```bash
# 安装 Nginx
sudo yum install -y nginx

# 配置 SSL 证书
# 编辑 /etc/nginx/conf.d/opencv-platform.conf
```

### 3. 限制访问 IP

编辑 `docker-compose.prod.yml`：

```yaml
ports:
  - "127.0.0.1:8000:8000"  # 仅本地访问
```

### 4. 定期更新

```bash
# 更新系统
sudo yum update -y

# 更新 Docker
sudo yum update docker-ce docker-ce-cli containerd.io

# 更新应用
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 性能优化

### 1. 调整资源限制

编辑 `docker-compose.prod.yml`：

```yaml
deploy:
  resources:
    limits:
      cpus: '8.0'      # 增加 CPU 核心数
      memory: 16G      # 增加内存限制
```

### 2. 使用 SSD 存储

确保 `data` 目录在 SSD 上以提升 I/O 性能。

### 3. 启用 GPU 支持

如果服务器有 NVIDIA GPU：

```bash
# 安装 NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | \
    sudo tee /etc/yum.repos.d/nvidia-docker.repo

sudo yum install -y nvidia-container-toolkit
sudo systemctl restart docker

# 修改 Dockerfile.prod 使用 GPU 版本的 PyTorch
# 修改 docker-compose.prod.yml 添加 GPU 支持
```

## 📞 技术支持

如遇问题，请：

1. 查看日志：`docker-compose -f docker-compose.prod.yml logs -f`
2. 提交 Issue：https://github.com/wuyuaginst-gif/YOLO-/issues
3. 查看文档：https://github.com/wuyuaginst-gif/YOLO-/blob/main/README.md

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

**祝您部署顺利！** 🎉
