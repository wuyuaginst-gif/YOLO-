# 🚨 快速修复：推理接口 500 错误

## 问题
```
POST /api/v1/inference/image HTTP/1.1" 500 Internal Server Error
```

## 原因
**Docker 部署：** 使用了旧的镜像，缺少依赖包  
**本地部署：** 缺少 PyTorch 和 Ultralytics

---

## 🐳 Docker 部署修复（2 步）

### 步骤 1️⃣：重建 Docker 镜像

```bash
# 进入项目目录
cd /path/to/your/opencv-platform

# 方式 A：使用一键脚本（推荐）
./rebuild_docker.sh

# 方式 B：手动重建
docker compose -f docker-compose.dev.yml down --rmi all
docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up -d
```

### 步骤 2️⃣：验证修复

```bash
# 检查容器内的依赖
docker exec opencv-platform-dev pip list | grep -E "(torch|ultralytics)"

# 或访问 API 文档测试
http://localhost:8000/api/docs
```

---

## 💻 本地部署修复（3 步）

### 步骤 1️⃣：安装依赖

```bash
# 进入项目目录
cd /path/to/your/opencv-platform

# 选择安装方式（根据你的硬件）

# 方式 A：如果你有 NVIDIA GPU（推荐）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 方式 B：如果只使用 CPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
pip install -r requirements.txt
```

### 步骤 2️⃣：重启服务

```bash
# 按 Ctrl+C 停止，然后重新运行
python app.py
```

### 步骤 3️⃣：验证修复

访问 http://localhost:8000/api/docs 测试推理接口，或运行：

```bash
python debug_inference.py
```

应该看到 ✅ 全部通过。

---

## ⚡ 一键安装脚本

```bash
./install_dependencies.sh
```

---

## 📋 验证安装

```bash
# 检查 PyTorch
python -c "import torch; print('✅ PyTorch:', torch.__version__)"

# 检查 Ultralytics  
python -c "import ultralytics; print('✅ Ultralytics:', ultralytics.__version__)"
```

---

## 🔍 仍然有问题？

查看详细排查指南：[TROUBLESHOOTING.md](TROUBLESHOOTING.md)
