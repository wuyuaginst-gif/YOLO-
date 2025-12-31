# 问题排查指南

## 🔴 当前问题：推理接口返回 500 错误

### 问题现象
```
opencv-platform-dev | INFO: 192.168.2.93:64787 - "POST /api/v1/inference/image HTTP/1.1" 500 Internal Server Error
```

### 根本原因
**缺少核心依赖包**，导致 YOLO 服务无法初始化：

- ❌ `torch` (PyTorch) - **未安装**
- ❌ `ultralytics` - **未安装**
- ✅ `opencv-python` - 已安装

### 诊断结果
运行 `python debug_inference.py` 输出：
```
❌ PyTorch 导入失败: No module named 'torch'
❌ Ultralytics 导入失败: No module named 'ultralytics'
```

---

## 💡 解决方案

### 方案一：使用安装脚本（推荐）

```bash
# 运行安装脚本
./install_dependencies.sh
```

### 方案二：手动安装

#### 1️⃣ 安装 PyTorch

**如果你有 NVIDIA GPU：**
```bash
# CUDA 11.8 版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 或 CUDA 12.1 版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**如果只使用 CPU：**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### 2️⃣ 安装其他依赖

```bash
pip install -r requirements.txt
```

#### 3️⃣ 验证安装

```bash
# 运行诊断脚本
python debug_inference.py
```

应该看到：
```
✅ PyTorch 已安装: x.x.x
✅ Ultralytics 已安装: x.x.x
✅ YOLO 服务已初始化
✅ 模型加载成功
✅ 推理成功
```

---

## 🔄 重启服务

安装完依赖后，需要重启应用服务：

### Docker 部署
```bash
# 停止服务
docker compose -f docker-compose.dev.yml down

# 重新构建镜像（如果需要）
docker compose -f docker-compose.dev.yml build

# 启动服务
docker compose -f docker-compose.dev.yml up -d

# 查看日志
docker compose -f docker-compose.dev.yml logs -f
```

### 本地部署
```bash
# 停止当前服务（Ctrl+C）

# 重新启动
python app.py

# 或使用 uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 测试推理接口

重启服务后，测试推理接口：

### 使用 curl
```bash
# 准备一张测试图片
# 然后执行推理请求
curl -X POST "http://localhost:8000/api/v1/inference/image" \
  -F "file=@test_image.jpg" \
  -F "model_name=yolo11n.pt" \
  -F "confidence=0.25"
```

### 预期响应
```json
{
  "success": true,
  "message": "Inference completed successfully",
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.89,
      "bbox": [100, 150, 300, 450]
    }
  ],
  "inference_time": 0.023,
  "image_shape": [480, 640, 3]
}
```

---

## 📝 常见问题

### Q1: 安装 PyTorch 时出错
**A:** 检查 Python 版本（需要 3.8+），确保网络连接正常，可以尝试使用国内镜像：
```bash
pip install torch torchvision torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 模型下载失败
**A:** 首次运行时，Ultralytics 会自动下载预训练模型。如果下载失败：
1. 检查网络连接
2. 手动下载模型文件到 `data/models/` 目录
3. 从官网下载：https://github.com/ultralytics/assets/releases

### Q3: GPU 不可用
**A:** 检查：
1. NVIDIA 驱动是否安装
2. CUDA 版本是否匹配
3. PyTorch 是否安装了 CUDA 版本

运行诊断：
```bash
python -c "import torch; print('CUDA可用:', torch.cuda.is_available())"
```

### Q4: 内存不足
**A:** YOLO 模型推理需要一定内存：
- yolo11n.pt (最小): ~10 MB，推理需 ~500 MB 内存
- yolo11s.pt (小): ~22 MB，推理需 ~1 GB 内存
- yolo11m.pt (中): ~50 MB，推理需 ~2 GB 内存
- yolo11l.pt (大): ~88 MB，推理需 ~4 GB 内存
- yolo11x.pt (超大): ~136 MB，推理需 ~8 GB 内存

如果内存不足，使用更小的模型或增加系统内存。

---

## 🔍 调试技巧

### 1. 查看详细日志
```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 启动应用
python app.py
```

### 2. 使用 Python REPL 测试
```python
from backend.services.yolo_service import yolo_service

# 测试模型加载
model = yolo_service.load_model("yolo11n.pt")
print(f"模型加载成功: {model.task}")

# 测试推理
result = yolo_service.infer("test.jpg")
print(f"推理结果: {result.success}")
```

### 3. 检查 API 文档
访问 http://localhost:8000/api/docs 查看交互式 API 文档，直接在浏览器中测试接口。

---

## 📞 需要帮助？

如果问题仍未解决：

1. 运行完整诊断：`python debug_inference.py > diagnostic.log 2>&1`
2. 查看应用日志
3. 检查系统资源（内存、磁盘空间）
4. 提供详细错误信息

---

## ✅ 验证清单

安装完成后，确保以下所有项都通过：

- [ ] PyTorch 已安装并可导入
- [ ] Ultralytics 已安装并可导入  
- [ ] YOLO 服务初始化成功
- [ ] 模型可以正常加载
- [ ] 推理测试通过
- [ ] API 接口返回 200 状态码
- [ ] 前端可以正常调用推理接口

全部通过后，你的 OpenCV Platform 就可以正常使用了！
