#!/bin/bash
# 安装 OpenCV Platform 依赖包

echo "================================================"
echo "OpenCV Platform - 依赖包安装脚本"
echo "================================================"
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
python --version
echo ""

# 升级 pip
echo "升级 pip..."
python -m pip install --upgrade pip
echo ""

# 安装 PyTorch（CPU 版本，如果有 GPU 请使用 GPU 版本）
echo "================================================"
echo "安装 PyTorch..."
echo "================================================"
# CPU 版本
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 如果你有 NVIDIA GPU，请使用下面的命令代替（取消注释）：
# python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo ""

# 安装其他依赖
echo "================================================"
echo "安装其他依赖..."
echo "================================================"
python -m pip install -r requirements.txt

echo ""
echo "================================================"
echo "验证安装..."
echo "================================================"

# 验证 PyTorch
python -c "import torch; print(f'✅ PyTorch {torch.__version__} 安装成功')" 2>/dev/null || echo "❌ PyTorch 安装失败"

# 验证 Ultralytics
python -c "import ultralytics; print(f'✅ Ultralytics {ultralytics.__version__} 安装成功')" 2>/dev/null || echo "❌ Ultralytics 安装失败"

# 验证 OpenCV
python -c "import cv2; print(f'✅ OpenCV {cv2.__version__} 安装成功')" 2>/dev/null || echo "❌ OpenCV 安装失败"

# 验证 Supervision
python -c "import supervision; print(f'✅ Supervision 安装成功')" 2>/dev/null || echo "❌ Supervision 安装失败"

echo ""
echo "================================================"
echo "安装完成！"
echo "================================================"
echo ""
echo "接下来请："
echo "1. 重启你的应用服务"
echo "2. 运行诊断脚本验证: python debug_inference.py"
echo ""
