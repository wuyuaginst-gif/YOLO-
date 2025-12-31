# 🔍 依赖包都在，但仍然 500 错误的可能原因

## ✅ 确认状态
你的容器内已正确安装：
- ✅ torch 2.9.1+cpu
- ✅ ultralytics 8.3.243
- ✅ opencv-python 4.12.0.88
- ✅ fastapi 0.128.0
- ✅ supervision 0.27.0

**但仍然遇到 500 错误**，原因可能是：

---

## 🎯 可能原因分析

### 1️⃣ 首次运行自动下载模型失败

**问题：**
当你使用 `yolo11n.pt` 时，如果本地不存在，Ultralytics 会自动下载。下载可能失败：

```python
# backend/services/yolo_service.py 第 46-53 行
if not model_path.exists():
    try:
        print(f"Downloading pretrained model: {model_name}")
        model = YOLO(model_name)  # ⬅️ 这里会下载模型
        # ...
    except Exception as e:
        raise FileNotFoundError(f"Model {model_name} not found and download failed: {e}")
```

**症状：**
- 第一次推理请求超时或失败
- 网络问题导致下载中断
- 磁盘空间不足

**解决方案：**
```bash
# 进入容器手动下载模型
docker exec -it opencv-platform-dev bash
python3 -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"
```

---

### 2️⃣ 文件上传问题

**问题：**
- 上传的文件为空
- 文件类型验证失败
- 文件保存路径没有写权限

**检查点：**
```python
# backend/api/routes.py 第 95 行
if not allowed_file(file.filename, ["jpg", "jpeg", "png", "bmp"]):
    raise HTTPException(status_code=400, detail="Invalid file type")
```

**可能的错误：**
- 文件扩展名大写（如 `.JPG`）被拒绝
- 文件名包含特殊字符
- `data/uploads/` 目录权限问题

---

### 3️⃣ 目录权限问题

**问题：**
Docker 容器使用非 root 用户（appuser），可能没有写权限：

```dockerfile
# Dockerfile.prod 第 96-97 行
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser  # ⬅️ 以 appuser 运行
```

**检查方法：**
```bash
# 检查目录权限
docker exec opencv-platform-dev ls -la /app/data/
docker exec opencv-platform-dev ls -la /app/data/uploads/

# 应该看到 appuser appuser
```

**解决方案：**
```bash
# 修复权限
docker exec -u root opencv-platform-dev chown -R appuser:appuser /app/data
docker exec -u root opencv-platform-dev chmod -R 777 /app/data
```

---

### 4️⃣ YOLO 服务初始化失败

**问题：**
虽然包都安装了，但服务可能初始化失败：

```python
# backend/services/yolo_service.py 第 273 行
yolo_service = YOLOService() if ULTRALYTICS_AVAILABLE else None
```

**可能的错误：**
- `YOLOService.__init__()` 抛出异常
- `ULTRALYTICS_AVAILABLE` 为 False
- 导入错误但被静默处理

**检查方法：**
```bash
docker exec opencv-platform-dev python3 -c "
import sys
sys.path.insert(0, '/app')
from backend.services.yolo_service import yolo_service, ULTRALYTICS_AVAILABLE
print(f'ULTRALYTICS_AVAILABLE: {ULTRALYTICS_AVAILABLE}')
print(f'yolo_service is None: {yolo_service is None}')
"
```

---

### 5️⃣ 请求参数类型错误

**问题：**
FastAPI 的 Form 参数类型不匹配：

```python
# backend/api/routes.py 第 85-88 行
async def infer_image(
    file: UploadFile = File(...),
    model_name: Optional[str] = Form(None),
    confidence: Optional[float] = Form(None),  # ⬅️ 需要 float
    iou_threshold: Optional[float] = Form(None),
    img_size: Optional[int] = Form(None)  # ⬅️ 需要 int
):
```

**客户端错误示例：**
```bash
# ❌ 错误：传递字符串而不是数字
curl -F "confidence=twenty-five"  # 应该是 0.25

# ✅ 正确
curl -F "confidence=0.25"
```

---

### 6️⃣ 模型推理超时

**问题：**
- CPU 推理速度慢
- 图片太大
- 容器资源限制

**症状：**
```yaml
# docker-compose.dev.yml 第 86-93 行
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 8G  # ⬅️ 内存限制
```

**解决方案：**
- 使用更小的模型（yolo11n.pt）
- 降低图片分辨率
- 增加资源限制

---

### 7️⃣ 异常处理中的错误

**问题：**
推理失败但错误处理代码也抛出异常：

```python
# backend/services/yolo_service.py 第 123-130 行
except Exception as e:
    return InferenceResponse(
        success=False,
        message=f"Inference failed: {str(e)}",  # ⬅️ 如果 str(e) 失败？
        detections=[],
        inference_time=0.0,
        image_shape=[0, 0, 0]
    )
```

---

### 8️⃣ 真实图片格式问题

**问题：**
- 图片损坏
- 不支持的颜色模式（如 RGBA、CMYK）
- 特殊格式的 JPEG/PNG

**检查方法：**
```python
from PIL import Image
img = Image.open('problematic.jpg')
print(f"Mode: {img.mode}")  # 应该是 RGB
print(f"Size: {img.size}")
```

---

## 🔧 诊断步骤

### Step 1: 查看容器日志
```bash
docker logs opencv-platform-dev --tail 100
```

**寻找：**
- Python traceback
- "Exception"、"Error"、"Failed" 等关键词
- 模型下载消息

### Step 2: 测试 YOLO 服务
```bash
./diagnose_500_error.sh
```

### Step 3: 测试 API 接口
```bash
./test_api.sh
```

### Step 4: 使用真实图片测试
```bash
# 准备一张真实图片
curl -X POST "http://localhost:8000/api/v1/inference/image" \
  -F "file=@real_photo.jpg" \
  -F "model_name=yolo11n.pt" \
  -F "confidence=0.25" \
  -v  # ⬅️ 显示详细信息
```

---

## 🎯 最可能的原因（排序）

基于经验，最可能的原因是：

1. **模型首次下载失败**（60% 可能性）
   - 网络问题
   - 下载超时
   
2. **目录权限问题**（20% 可能性）
   - uploads 目录没有写权限
   - 模型保存失败

3. **请求参数错误**（10% 可能性）
   - 客户端传递的参数类型不对
   
4. **图片格式问题**（5% 可能性）
   - 特殊格式的图片
   
5. **其他**（5% 可能性）

---

## ✅ 快速修复检查清单

在你的**本地环境**运行以下命令：

### 1. 查看详细日志
```bash
docker logs opencv-platform-dev --tail 100 | grep -i error
```

### 2. 检查模型是否存在
```bash
docker exec opencv-platform-dev ls -la /app/data/models/
docker exec opencv-platform-dev ls -la /root/.cache/ultralytics/ 2>/dev/null
```

### 3. 手动下载模型（如果缺失）
```bash
docker exec opencv-platform-dev python3 -c "from ultralytics import YOLO; model=YOLO('yolo11n.pt'); print('Model downloaded successfully')"
```

### 4. 测试权限
```bash
docker exec opencv-platform-dev touch /app/data/uploads/test.txt
docker exec opencv-platform-dev rm /app/data/uploads/test.txt
```

### 5. 运行诊断脚本
```bash
./diagnose_500_error.sh
./test_api.sh
```

---

## 📞 下一步

**请运行以下命令并提供输出：**

```bash
# 1. 查看最近的错误日志
docker logs opencv-platform-dev --tail 50 2>&1 | grep -A 5 -B 5 "500"

# 2. 或查看所有日志
docker logs opencv-platform-dev --tail 100

# 3. 运行诊断脚本
./diagnose_500_error.sh > diagnostic_output.txt 2>&1
cat diagnostic_output.txt
```

提供这些信息后，我能精确定位问题所在！🎯
