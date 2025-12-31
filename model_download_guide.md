# 模型下载后是否需要重启容器？

## ✅ 简短回答：**不需要重启！**

## 📝 详细说明

### 为什么不需要重启？

当你运行：
```bash
docker exec opencv-platform-dev python3 -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"
```

这个命令做了什么：
1. ✅ 从 Ultralytics 服务器下载 `yolo11n.pt` 模型（~6 MB）
2. ✅ 保存到容器内的缓存目录：`~/.cache/ultralytics/` 或 `/app/data/models/`
3. ✅ 模型文件持久化存储在容器的文件系统中
4. ✅ 下次推理请求时，直接加载本地模型文件

### 模型加载机制

查看你的代码 `backend/services/yolo_service.py`：

```python
def load_model(self, model_name: str) -> YOLO:
    """加载模型"""
    if model_name in self.models:
        return self.models[model_name]  # ⬅️ 从内存缓存加载
    
    model_path = settings.MODELS_DIR / model_name
    
    # 如果本地不存在,尝试下载预训练模型
    if not model_path.exists():
        try:
            print(f"Downloading pretrained model: {model_name}")
            model = YOLO(model_name)  # ⬅️ 下载并缓存
            self.models[model_name] = model
            return model
        except Exception as e:
            raise FileNotFoundError(f"...")
    
    model = YOLO(str(model_path))  # ⬅️ 从本地加载
    self.models[model_name] = model
    return model
```

**工作流程：**
1. 第一次请求：检查本地 → 不存在 → 下载 → 缓存到内存和磁盘
2. 第二次请求：检查内存缓存 → 存在 → 直接返回
3. 重启后请求：检查磁盘 → 存在 → 加载到内存

---

## 🎯 执行后立即测试

下载完模型后，**立即就可以**测试推理接口，无需任何重启：

```bash
# 1. 下载模型
docker exec opencv-platform-dev python3 -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"

# 2. 等待下载完成（看到 ✅ 或模型信息）

# 3. 立即测试推理（无需重启）
curl -X POST "http://localhost:8000/api/v1/inference/image" \
  -F "file=@test_image.jpg" \
  -F "model_name=yolo11n.pt" \
  -F "confidence=0.25"
```

---

## 📋 验证模型下载成功

### 方法 1：检查模型文件
```bash
# 检查 Ultralytics 缓存目录
docker exec opencv-platform-dev ls -lh ~/.cache/ultralytics/

# 或检查应用模型目录
docker exec opencv-platform-dev ls -lh /app/data/models/
```

应该看到 `yolo11n.pt` 文件（约 6 MB）。

### 方法 2：在容器内测试加载
```bash
docker exec opencv-platform-dev python3 << 'EOF'
from ultralytics import YOLO

# 加载模型（应该很快，因为已下载）
model = YOLO('yolo11n.pt')

print(f"✅ 模型加载成功")
print(f"   模型类型: {model.task}")
print(f"   类别数量: {len(model.names)}")
print(f"   设备: {model.device}")
