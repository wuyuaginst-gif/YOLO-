# OpenCV Platform 部署指南

本文档介绍如何部署 OpenCV Platform v2.0。

## 📋 目录

- [系统要求](#系统要求)
- [Docker 开发环境部署](#docker-开发环境部署)
- [Docker 生产环境部署](#docker-生产环境部署)
- [本地开发部署](#本地开发部署)
- [常见问题](#常见问题)

---

## 🔧 系统要求

### 最低配置
- **CPU**: 2 核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **操作系统**: Linux / macOS / Windows (with WSL2)

### 推荐配置
- **CPU**: 4 核心以上
- **内存**: 8GB RAM 以上
- **GPU**: NVIDIA GPU（用于加速训练和推理）
- **存储**: 50GB+ SSD
- **操作系统**: Ubuntu 20.04 LTS 或更高版本

### 软件要求
- **Docker**: 20.10+ 
- **Docker Compose**: 1.29+
- **Python**: 3.8+ (仅本地开发)

---

## 🐳 Docker 开发环境部署

开发环境支持代码热重载，适合开发和调试。

### 1. 克隆项目

```bash
git clone <repository-url>
cd webapp
```

### 2. 配置环境变量（可选）

```bash
cp .env.example .env
# 编辑 .env 文件调整配置
vim .env
```

### 3. 启动开发环境

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 4. 验证部署

```bash
# 查看容器状态
docker-compose -f docker-compose.dev.yml ps

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f opencv-platform-dev

# 健康检查
curl http://localhost:8000/api/v1/system/health
```

### 5. 访问应用

- **Web UI**: http://localhost:8000
- **API 文档**: http://localhost:8000/api/docs
- **健康检查**: http://localhost:8000/api/v1/system/health

### 6. 停止服务

```bash
docker-compose -f docker-compose.dev.yml down
```

---

## 🚀 Docker 生产环境部署

生产环境针对性能优化，适合生产部署。

### 1. 配置环境变量

```bash
cp .env.example .env
vim .env
```

**重要配置项：**
```bash
APP_NAME=OpenCV Platform
APP_VERSION=2.0.0
DEBUG=False  # 生产环境设置为 False
API_PORT=8000
```

### 2. 构建生产镜像

```bash
docker-compose -f docker-compose.prod.yml build
```

### 3. 启动生产环境

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. 监控和维护

#### 查看服务状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

#### 查看日志
```bash
# 查看所有日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看最近 100 行日志
docker-compose -f docker-compose.prod.yml logs --tail=100
```

#### 重启服务
```bash
docker-compose -f docker-compose.prod.yml restart
```

#### 更新服务
```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose -f docker-compose.prod.yml build

# 重启服务
docker-compose -f docker-compose.prod.yml up -d
```

### 5. 备份和恢复

#### 备份数据
```bash
# 备份 data 目录
tar -czf opencv-platform-data-$(date +%Y%m%d).tar.gz data/

# 备份到远程服务器（可选）
scp opencv-platform-data-*.tar.gz user@backup-server:/backup/
```

#### 恢复数据
```bash
# 解压备份文件
tar -xzf opencv-platform-data-20231201.tar.gz
```

---

## 💻 本地开发部署

适合不使用 Docker 的开发场景。

### 1. 环境准备

```bash
# 安装 Python 3.8+
python3 --version

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件
vim .env
```

### 4. 创建必要目录

```bash
mkdir -p data/{datasets,models,exports,uploads,annotation_projects}
mkdir -p logs
```

### 5. 启动应用

#### 方式一：使用 Python 直接运行
```bash
python app.py
```

#### 方式二：使用 Uvicorn（推荐）
```bash
# 开发模式（支持热重载）
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. 验证部署

```bash
# 检查服务
curl http://localhost:8000/api/v1/system/health

# 查看系统信息
curl http://localhost:8000/api/v1/system/info
```

---

## 🔍 常见问题

### Q1: Docker 容器无法启动？

**解决方案：**
```bash
# 检查 Docker 服务
sudo systemctl status docker

# 查看容器日志
docker-compose -f docker-compose.dev.yml logs

# 清理并重新启动
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### Q2: GPU 不可用？

**解决方案：**
```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 安装 NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Q3: 端口被占用？

**解决方案：**
```bash
# 查看端口占用
sudo lsof -i :8000

# 修改 .env 文件中的端口
vim .env
# API_PORT=8001

# 或者在 docker-compose 中修改端口映射
vim docker-compose.dev.yml
# ports:
#   - "8001:8000"
```

### Q4: 依赖安装失败？

**解决方案：**
```bash
# 升级 pip
pip install --upgrade pip

# 使用镜像源加速（中国用户）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### Q5: 内存不足？

**解决方案：**

编辑 docker-compose 文件，调整资源限制：

```yaml
deploy:
  resources:
    limits:
      memory: 4G  # 降低内存限制
    reservations:
      memory: 2G
```

### Q6: 数据持久化问题？

**解决方案：**

确保 data 目录正确挂载：

```yaml
volumes:
  - ./data:/app/data  # 确保此行存在
```

### Q7: 自动标注失败？

**可能原因：**
- 模型文件不存在
- 图片格式不支持
- 内存不足

**解决方案：**
```bash
# 下载预训练模型
cd data/models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# 检查图片格式
file image.jpg

# 增加内存限制
# 编辑 docker-compose.yml
```

---

## 📞 技术支持

如遇到其他问题，请：

1. 查看项目 [Issues](https://github.com/your-repo/issues)
2. 提交新的 Issue
3. 联系开发团队

---

## 🔐 安全建议

### 生产环境安全配置

1. **修改默认端口**
```bash
API_PORT=8080  # 使用非默认端口
```

2. **配置防火墙**
```bash
# 仅允许特定 IP 访问
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

3. **使用 HTTPS**
建议使用 Nginx 作为反向代理并配置 SSL 证书。

4. **定期更新**
```bash
# 更新系统包
sudo apt update && sudo apt upgrade

# 更新 Docker 镜像
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

5. **备份策略**
- 每日备份数据目录
- 每周备份完整系统
- 异地存储备份

---

## 📊 性能优化

### 1. 使用 GPU 加速

在 docker-compose.prod.yml 中添加 GPU 支持：

```yaml
services:
  opencv-platform:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 2. 调整 Worker 数量

根据 CPU 核心数调整：

```bash
# 在 Dockerfile.prod 中
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3. 缓存优化

配置 Redis 缓存（可选）：

```yaml
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

---

<div align="center">

**Happy Deploying! 🚀**

Made with ❤️ by OpenCV Platform Team

</div>
