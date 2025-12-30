# OpenCV Platform 部署指南

## 🎯 已解决的问题

### ✅ Dockerfile 包名修复
- **问题**: `libgl1-mesa-glx` 包在新版 Debian 中已被移除
- **解决**: 已更新为 `libgl1`
- **文件**: `Dockerfile` 和 `Dockerfile.lite` 均已修复

## 🚀 部署方式

### 方式一：Docker 部署（推荐用于生产环境）

#### 1. 查看构建进度
```bash
cd /home/root/wuyu/YOLO-/webapp
tail -f build_final.log
```

#### 2. 等待构建完成后启动
```bash
# 查看镜像是否构建成功
docker images | grep opencv-platform

# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f opencv-platform
```

#### 3. 访问服务
- **OpenCV Platform**: http://YOUR_SERVER_IP:8000
- **API 文档**: http://YOUR_SERVER_IP:8000/api/docs  
- **Label Studio**: http://YOUR_SERVER_IP:8000:8080

### 方式二：本地 Python 环境（快速测试）

#### 前提条件
- Python 3.8+ （服务器当前是 Python 3.6，建议升级或使用 Docker）

#### 1. 升级 Python（如果需要）
```bash
# CentOS/RHEL
sudo yum install -y python39 python39-pip

# 或者使用 pyenv
curl https://pyenv.run | bash
pyenv install 3.9.0
pyenv global 3.9.0
```

#### 2. 设置虚拟环境
```bash
cd /home/root/wuyu/YOLO-/webapp

# 使用 Python 3.9
python3.9 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

#### 3. 安装依赖
```bash
# 安装基础依赖
pip install fastapi uvicorn[standard] python-multipart jinja2

# 安装 CV 相关库（CPU 版本，更快）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install ultralytics opencv-python-headless Pillow numpy pyyaml requests
```

#### 4. 启动服务
```bash
# 创建环境配置
cp .env.example .env

# 启动应用
python app.py
```

#### 5. 访问服务
打开浏览器访问: http://YOUR_SERVER_IP:8000

## 📊 Docker 构建说明

### 精简版 Dockerfile (Dockerfile.lite)
- ✅ 使用 CPU 版本的 PyTorch（更小更快）
- ✅ 移除不必要的系统依赖
- ✅ 优化镜像大小
- ⚡ 预计构建时间: 10-15 分钟（取决于网络速度）

### 完整版 Dockerfile
- 包含 GPU 支持（CUDA 库）
- 镜像更大，构建时间更长
- 适合有 GPU 的生产环境

## 🔧 故障排查

### 问题 1: Docker 构建超时
**解决方案**: 
- 检查网络连接
- 使用 Docker Hub 镜像加速器
- 或使用本地 Python 环境部署

### 问题 2: Python 版本过低
```bash
# 检查 Python 版本
python3 --version

# 如果低于 3.8，需要升级或使用 Docker
```

### 问题 3: 端口被占用
```bash
# 检查端口
sudo lsof -i :8000
sudo lsof -i :8080

# 修改端口（编辑 .env 文件）
vi .env
# 修改 API_PORT 和 LABEL_STUDIO_PORT
```

### 问题 4: 内存不足
```bash
# 检查内存
free -h

# 限制 Docker 内存使用（编辑 docker-compose.yml）
services:
  opencv-platform:
    mem_limit: 4g
```

## 📝 快速测试

### 1. 健康检查
```bash
curl http://localhost:8000/api/v1/system/health
```

### 2. 系统信息
```bash
curl http://localhost:8000/api/v1/system/info
```

### 3. 测试推理
```bash
# 下载测试图片
wget https://ultralytics.com/images/bus.jpg

# 执行推理
curl -X POST "http://localhost:8000/api/v1/inference/image" \
  -F "file=@bus.jpg" \
  -F "model_name=yolov8n.pt" \
  -F "confidence=0.25"
```

## 🎯 推荐部署流程

### 对于快速测试：
1. 使用本地 Python 环境
2. 安装 CPU 版本的依赖
3. 立即启动测试

### 对于生产环境：
1. 等待 Docker 构建完成
2. 使用 docker compose 启动
3. 配置 Nginx 反向代理
4. 设置 HTTPS

## 📞 获取帮助

- **项目文档**: [README.md](README.md)
- **快速开始**: [QUICKSTART.md](QUICKSTART.md)
- **项目总结**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **GitHub 仓库**: https://github.com/wuyuaginst-gif/YOLO-

## ✅ 部署检查清单

- [ ] Python 3.8+ 已安装（或 Docker 可用）
- [ ] 依赖已安装
- [ ] 环境配置文件 .env 已创建
- [ ] 数据目录已创建
- [ ] 服务可以正常启动
- [ ] 可以访问 Web 界面
- [ ] API 健康检查通过
- [ ] 推理功能正常工作

---

🎉 祝使用愉快！如有问题请查看文档或提交 Issue。
