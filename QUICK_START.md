# 🚀 快速开始指南

## 📋 目录

1. [开发环境设置](#开发环境设置)
2. [训练安全帽检测模型](#训练安全帽检测模型)
3. [Docker 优化使用](#docker-优化使用)

---

## 🛠️ 开发环境设置

### 方法一：使用开发模式（推荐）⭐⭐⭐

**特点**: 代码修改立即生效，无需重新构建镜像

```bash
# 1. 首次构建（只需一次）
./dev.sh build

# 2. 启动开发环境
./dev.sh up-d

# 3. 查看日志
./dev.sh logs

# 4. 修改代码
# 编辑 backend/api/routes.py 或其他文件
# 保存后，服务器会自动重载（1-2 秒）

# 5. 停止服务
./dev.sh stop
```

**访问地址**:
- 主页: http://localhost:8000
- Solutions: http://localhost:8000/solutions
- API 文档: http://localhost:8000/api/docs
- Label Studio: http://localhost:8087

### 方法二：使用生产模式

```bash
# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 方法三：本地 Python 环境

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py

# 或使用 uvicorn（支持热重载）
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🎯 训练安全帽检测模型

### Step 1: 准备数据集

#### 选项 A: 使用公开数据集（快速开始）

```bash
# 从 Roboflow 下载
# 搜索: "safety helmet detection"
# 导出格式: YOLO v11

# 或从 Kaggle 下载
# 搜索: "hard hat detection"
```

#### 选项 B: 标注自己的数据

1. **收集图片**
   - 最少 500 张
   - 推荐 1000-2000 张
   - 多角度、多场景

2. **使用 Label Studio 标注**
```bash
# 访问标注页面
http://localhost:8000/labelstudio

# 创建项目
# 上传图片
# 标注（person-with-helmet, person-without-helmet）
# 导出为 YOLO 格式
```

3. **组织数据集结构**
```bash
data/datasets/helmet_detection/
├── data.yaml
├── images/
│   ├── train/  (70% 图片)
│   ├── val/    (20% 图片)
│   └── test/   (10% 图片)
└── labels/
    ├── train/  (对应标注)
    ├── val/
    └── test/
```

4. **创建 data.yaml**
```yaml
path: /app/data/datasets/helmet_detection
train: images/train
val: images/val
test: images/test
nc: 2
names:
  0: person-with-helmet
  1: person-without-helmet
```

### Step 2: 训练模型

#### 方法 A: 使用训练脚本（推荐）

```bash
# 基础训练（快速测试）
python scripts/train_helmet_detection.py \
  --data data/datasets/helmet_detection/data.yaml \
  --model yolo11n.pt \
  --epochs 50 \
  --batch 16 \
  --device cpu

# 高精度训练
python scripts/train_helmet_detection.py \
  --data data/datasets/helmet_detection/data.yaml \
  --model yolo11m.pt \
  --epochs 100 \
  --batch 16 \
  --device cuda \
  --patience 50

# 查看所有参数
python scripts/train_helmet_detection.py --help
```

#### 方法 B: 使用 Web UI

1. 访问 http://localhost:8000/training
2. 填写参数:
   - 项目名称: helmet_detection_v1
   - 数据集路径: /app/data/datasets/helmet_detection
   - 模型类型: yolo11m
   - 训练轮数: 100
   - 批次大小: 16
3. 点击"开始训练"
4. 监控训练进度

#### 方法 C: 使用 API

```python
import requests

config = {
    "project_name": "helmet_detection_v1",
    "dataset_path": "/app/data/datasets/helmet_detection",
    "model_type": "yolo11m",
    "epochs": 100,
    "batch_size": 16,
    "img_size": 640,
    "device": "cpu"
}

response = requests.post(
    "http://localhost:8000/api/v1/training/start",
    json=config
)

task_id = response.json()["task_id"]
print(f"训练任务: {task_id}")
```

### Step 3: 评估模型

```python
from ultralytics import YOLO

# 加载最佳模型
model = YOLO('runs/detect/helmet_detection_v1/weights/best.pt')

# 验证
metrics = model.val(data='data/datasets/helmet_detection/data.yaml')
print(f"mAP50: {metrics.box.map50:.4f}")
print(f"mAP50-95: {metrics.box.map:.4f}")
```

### Step 4: 部署和使用

#### 上传模型到平台

1. 访问 http://localhost:8000/models
2. 上传 `runs/detect/helmet_detection_v1/weights/best.pt`

#### 推理测试

```python
import requests

# 单张图片推理
files = {'file': open('construction_site.jpg', 'rb')}
data = {
    'model_name': 'helmet_detection_v1_best.pt',
    'confidence': 0.25
}

response = requests.post(
    'http://localhost:8000/api/v1/inference/image',
    files=files,
    data=data
)

result = response.json()
for detection in result['detections']:
    print(f"{detection['class_name']}: {detection['confidence']:.2f}")
```

#### 实时监控（视频流）

```python
from ultralytics import YOLO
import cv2

model = YOLO('helmet_detection_v1_best.pt')
cap = cv2.VideoCapture(0)  # 或视频文件

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    results = model(frame, conf=0.25)
    annotated = results[0].plot()
    
    # 检查违规
    for box in results[0].boxes:
        if model.names[int(box.cls[0])] == 'person-without-helmet':
            print("⚠️ 警告：未佩戴安全帽！")
    
    cv2.imshow('Helmet Detection', annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 🚢 Docker 优化使用

### 问题：每次代码更新都要重装 Python 环境

### 解决方案 1: 使用开发模式（推荐）⭐⭐⭐

```bash
# 首次构建
./dev.sh build

# 启动（代码挂载，热重载）
./dev.sh up-d

# 修改代码
# - 保存后自动重载（1-2 秒）
# - 无需重新构建镜像

# 只有修改 requirements.txt 时才需要重新构建
./dev.sh rebuild
```

**原理**: 
- 代码目录挂载到容器
- Uvicorn 热重载
- 依赖在镜像中，不受代码变化影响

**优势**:
- ✅ 代码修改 1-2 秒生效
- ✅ 无需重新构建镜像
- ✅ 最佳开发体验

### 解决方案 2: 使用优化的 Dockerfile（生产环境）

**已优化**: `Dockerfile.prod` 使用分层缓存

```dockerfile
# 先复制依赖文件
COPY requirements.txt .

# 安装依赖（这层会被缓存）
RUN pip install -r requirements.txt

# 最后复制代码（代码变化不触发依赖重装）
COPY . .
```

**效果**:
- ✅ 首次构建: 5-10 分钟
- ✅ 代码更新后: 30-60 秒

**使用方法**:
```bash
# 代码更新后，快速重新构建
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 解决方案 3: 多阶段构建 + 基础镜像

```bash
# 1. 构建基础镜像（只需一次）
docker build -f Dockerfile.base -t opencv-platform-base:latest .

# 2. 构建应用镜像（很快）
docker build -f Dockerfile.app -t opencv-platform:latest .

# 3. 更新代码后，只重新构建应用镜像（10-20 秒）
docker build -f Dockerfile.app -t opencv-platform:latest .
```

### 性能对比

| 方案 | 首次构建 | 代码更新 | 依赖更新 | 适用场景 |
|------|---------|---------|---------|---------|
| 开发模式 | 5-10 分钟 | **1-2 秒** | 5-10 分钟 | 日常开发 ⭐⭐⭐ |
| 优化 Dockerfile | 5-10 分钟 | 30-60 秒 | 5-10 分钟 | 生产部署 |
| 基础镜像 | 5-10 分钟 | **10-20 秒** | 5-10 分钟 | CI/CD |

### 推荐工作流程

```bash
# 开发阶段（日常）
./dev.sh up-d        # 启动开发环境
# 修改代码，自动重载
./dev.sh logs        # 查看日志
./dev.sh stop        # 停止

# 测试/部署
docker-compose -f docker-compose.prod.yml build  # 利用缓存，快速构建
docker-compose -f docker-compose.prod.yml up -d

# 依赖更新时
./dev.sh rebuild     # 重新构建开发镜像
```

---

## 📚 相关文档

### 核心文档
- [完整 README](./README.md) - 项目总览
- [安全帽检测训练指南](./HELMET_DETECTION_GUIDE.md) - 详细训练步骤
- [Docker 优化指南](./DOCKER_OPTIMIZATION_GUIDE.md) - Docker 构建优化

### Solutions 功能
- [Ultralytics Solutions](./ULTRALYTICS_SOLUTIONS.md) - 7 种智能解决方案
- [功能集成总结](./SOLUTIONS_FEATURE_SUMMARY.md) - 功能概览

### 技术文档
- [API 文档](http://localhost:8000/api/docs) - 在线 API 文档
- [测试报告](./TEST_REPORT.md) - 系统测试结果

### 部署文档
- [Docker 构建指南](./DOCKER_BUILD_GUIDE.md)
- [Logo 修复指南](./DOCKER_LOGO_FIX.md)
- [更新指南](./UPDATE_GUIDE.md)

---

## 🎯 常见任务速查

### 启动服务
```bash
# 开发模式（推荐）
./dev.sh up-d

# 生产模式
docker-compose -f docker-compose.prod.yml up -d
```

### 查看日志
```bash
# 开发模式
./dev.sh logs

# 生产模式
docker-compose -f docker-compose.prod.yml logs -f
```

### 训练模型
```bash
# 使用脚本
python scripts/train_helmet_detection.py --data path/to/data.yaml

# 使用 Web UI
# 访问 http://localhost:8000/training
```

### 推理测试
```bash
# 使用 Web UI
# 访问 http://localhost:8000/inference

# 使用 API
curl -X POST http://localhost:8000/api/v1/inference/image \
  -F "file=@test.jpg" \
  -F "model_name=yolo11n.pt"
```

### 更新代码
```bash
# 开发模式（无需操作，自动重载）
# 保存代码后等待 1-2 秒

# 生产模式
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

## 💡 常见问题

### Q: 如何在开发和生产环境之间切换？

```bash
# 开发 -> 生产
./dev.sh stop
docker-compose -f docker-compose.prod.yml up -d

# 生产 -> 开发
docker-compose -f docker-compose.prod.yml down
./dev.sh up-d
```

### Q: GPU 支持如何配置？

编辑 `docker-compose.*.yml`:
```yaml
services:
  opencv-platform:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

### Q: 如何备份训练好的模型？

```bash
# 复制模型文件
cp runs/detect/helmet_detection_v1/weights/best.pt backups/

# 或打包整个训练输出
tar -czf helmet_detection_v1.tar.gz runs/detect/helmet_detection_v1/
```

---

**需要帮助？** 查看详细文档或提交 Issue
