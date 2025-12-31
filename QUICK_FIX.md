# 🚨 快速修复：推理接口 500 错误

## 问题
```
POST /api/v1/inference/image HTTP/1.1" 500 Internal Server Error
```

## 原因
**缺少核心依赖包：**
- ❌ PyTorch (torch)
- ❌ Ultralytics

## 立即修复（3 步）

### 步骤 1️⃣：安装依赖

在你的**本地环境**（不是沙箱环境）运行：

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
# 如果使用 Docker
docker compose -f docker-compose.dev.yml restart

# 如果是直接运行
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
