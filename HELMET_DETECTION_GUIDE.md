# 工地安全帽检测模型训练指南

## 📋 项目概述

本指南将帮助您训练一个 YOLO11 模型，用于检测工地人员是否佩戴安全帽。

## 🎯 检测目标

- **类别 1**: `person-with-helmet` (佩戴安全帽的人)
- **类别 2**: `person-without-helmet` (未佩戴安全帽的人)
- **可选类别**: `helmet` (单独的安全帽)

## 📊 数据准备流程

### 方案一：使用公开数据集（推荐快速开始）

#### 1. Roboflow 公开数据集
```bash
# 搜索关键词：
# - "safety helmet detection"
# - "hard hat detection"
# - "construction helmet"

# 推荐数据集：
# https://universe.roboflow.com/search?q=safety+helmet
```

#### 2. Kaggle 数据集
```bash
# 推荐数据集：
# - "Hard Hat Detection Dataset"
# - "Construction Site Safety Images"

# 下载并转换为 YOLO 格式
```

### 方案二：自己标注数据（推荐生产环境）

#### 步骤 1: 收集图片
```bash
# 建议收集数量：
# - 最少：500 张图片
# - 推荐：1000-2000 张图片
# - 理想：3000+ 张图片

# 图片要求：
# ✓ 多角度：正面、侧面、远景、近景
# ✓ 多场景：室内、室外、不同光照
# ✓ 多样性：不同肤色、不同安全帽颜色
# ✓ 高质量：分辨率至少 640x640
```

#### 步骤 2: 使用 Label Studio 标注

1. **启动 Label Studio**
```bash
# 使用 Docker Compose
cd /home/user/webapp
docker-compose up -d labelstudio

# 或手动启动
pip install label-studio
label-studio start --port 8080
```

2. **创建标注项目**
```python
# 访问 http://localhost:8080
# 或使用平台内置功能：http://localhost:8000/labelstudio

# 项目配置：
{
    "title": "安全帽检测数据集",
    "description": "检测工地人员是否佩戴安全帽",
    "label_config": """
    <View>
      <Image name="image" value="$image"/>
      <RectangleLabels name="label" toName="image">
        <Label value="person-with-helmet" background="green"/>
        <Label value="person-without-helmet" background="red"/>
        <Label value="helmet" background="blue"/>
      </RectangleLabels>
    </View>
    """
}
```

3. **导出为 YOLO 格式**
```bash
# 通过 API
curl -X POST http://localhost:8000/api/v1/labelstudio/export/PROJECT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "format": "YOLO",
    "dataset_name": "helmet_detection"
  }'
```

#### 步骤 3: 组织数据集结构

```
data/datasets/helmet_detection/
├── data.yaml              # 数据集配置文件
├── images/
│   ├── train/            # 训练集图片 (70%)
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   ├── val/              # 验证集图片 (20%)
│   │   ├── img101.jpg
│   │   └── ...
│   └── test/             # 测试集图片 (10%)
│       ├── img201.jpg
│       └── ...
└── labels/
    ├── train/            # 训练集标注
    │   ├── img001.txt
    │   ├── img002.txt
    │   └── ...
    ├── val/              # 验证集标注
    │   ├── img101.txt
    │   └── ...
    └── test/             # 测试集标注
        ├── img201.txt
        └── ...
```

#### 步骤 4: 创建 data.yaml

```yaml
# data.yaml
path: /app/data/datasets/helmet_detection
train: images/train
val: images/val
test: images/test

# 类别数量
nc: 2

# 类别名称
names:
  0: person-with-helmet
  1: person-without-helmet
```

## 🚀 模型训练

### 方法一：通过 Web UI 训练

1. **访问训练页面**
```
http://localhost:8000/training
```

2. **填写训练参数**
```
项目名称: helmet_detection_v1
数据集路径: /app/data/datasets/helmet_detection
模型类型: yolo11n (快速测试) 或 yolo11m (更高精度)
训练轮数: 100
批次大小: 16
图片尺寸: 640
设备: cpu 或 cuda (如果有 GPU)
```

3. **开始训练并监控进度**

### 方法二：通过 API 训练

```python
import requests

# 训练配置
config = {
    "project_name": "helmet_detection_v1",
    "dataset_path": "/app/data/datasets/helmet_detection",
    "model_type": "yolo11n",
    "epochs": 100,
    "batch_size": 16,
    "img_size": 640,
    "device": "cpu",
    "patience": 50,
    "save_period": 10,
    "pretrained": True,
    "optimizer": "auto",
    "lr0": 0.01,
    "lrf": 0.01
}

# 启动训练
response = requests.post(
    "http://localhost:8000/api/v1/training/start",
    json=config
)

task_id = response.json()["task_id"]
print(f"训练任务已启动: {task_id}")

# 监控训练进度
status = requests.get(
    f"http://localhost:8000/api/v1/training/status/{task_id}"
)
print(status.json())
```

### 方法三：使用 Python 脚本直接训练

```python
from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolo11n.pt')

# 训练模型
results = model.train(
    data='/app/data/datasets/helmet_detection/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='helmet_detection_v1',
    patience=50,
    save_period=10,
    device='cpu',  # 或 'cuda' 如果有 GPU
    
    # 数据增强参数
    hsv_h=0.015,      # 色调增强
    hsv_s=0.7,        # 饱和度增强
    hsv_v=0.4,        # 明度增强
    degrees=10.0,     # 旋转角度
    translate=0.1,    # 平移
    scale=0.5,        # 缩放
    shear=0.0,        # 剪切
    perspective=0.0,  # 透视
    flipud=0.0,       # 上下翻转
    fliplr=0.5,       # 左右翻转
    mosaic=1.0,       # Mosaic 增强
    mixup=0.0,        # Mixup 增强
)

# 查看训练结果
print(results)
```

## 📈 训练参数优化建议

### 基础配置（快速测试）
```yaml
model_type: yolo11n
epochs: 50
batch_size: 16
img_size: 640
device: cpu
```

### 推荐配置（生产环境）
```yaml
model_type: yolo11m
epochs: 100-200
batch_size: 16-32 (根据显存调整)
img_size: 640
device: cuda (强烈推荐 GPU)
patience: 50
save_period: 10
```

### 高精度配置
```yaml
model_type: yolo11l 或 yolo11x
epochs: 200-300
batch_size: 8-16
img_size: 1280
device: cuda
patience: 100
```

## 🎯 训练监控指标

训练过程中关注以下指标：

```
✓ mAP50: 目标是 > 0.85
✓ mAP50-95: 目标是 > 0.60
✓ Precision: 目标是 > 0.85
✓ Recall: 目标是 > 0.80
✓ Loss: 应该持续下降
```

## 🔍 模型评估

### 1. 使用验证集评估
```python
from ultralytics import YOLO

# 加载训练好的模型
model = YOLO('runs/detect/helmet_detection_v1/weights/best.pt')

# 在验证集上评估
metrics = model.val(
    data='/app/data/datasets/helmet_detection/data.yaml',
    split='val'
)

print(f"mAP50: {metrics.box.map50}")
print(f"mAP50-95: {metrics.box.map}")
```

### 2. 测试单张图片
```python
# 推理
results = model.predict(
    source='test_image.jpg',
    conf=0.25,
    iou=0.45,
    save=True
)

# 查看结果
for r in results:
    print(f"检测到 {len(r.boxes)} 个对象")
    for box in r.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        print(f"类别: {model.names[cls]}, 置信度: {conf:.2f}")
```

## 📦 模型部署

### 1. 上传模型到平台
```bash
# 通过 Web UI
http://localhost:8000/models

# 或通过 API
curl -X POST http://localhost:8000/api/v1/models/upload \
  -F "file=@runs/detect/helmet_detection_v1/weights/best.pt"
```

### 2. 使用模型进行推理
```python
import requests

# 上传图片进行推理
files = {'file': open('construction_site.jpg', 'rb')}
data = {
    'model_name': 'helmet_detection_v1_best.pt',
    'confidence': 0.25,
    'iou_threshold': 0.45
}

response = requests.post(
    'http://localhost:8000/api/v1/inference/image',
    files=files,
    data=data
)

result = response.json()
print(f"检测结果: {result}")
```

### 3. 批量处理
```python
# 批量推理
import os
from pathlib import Path

image_dir = Path('construction_images')
for img_path in image_dir.glob('*.jpg'):
    results = model.predict(
        source=str(img_path),
        conf=0.25,
        save=True,
        project='helmet_detection_results',
        name='batch_inference'
    )
```

## 🚨 实际应用场景

### 场景一：实时监控
```python
from ultralytics import YOLO
import cv2

model = YOLO('helmet_detection_v1_best.pt')

# 打开摄像头或视频流
cap = cv2.VideoCapture(0)  # 或视频文件路径

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 推理
    results = model(frame, conf=0.25)
    
    # 绘制结果
    annotated_frame = results[0].plot()
    
    # 检查是否有人未戴安全帽
    for box in results[0].boxes:
        cls = int(box.cls[0])
        if model.names[cls] == 'person-without-helmet':
            # 触发警报
            print("⚠️ 警告：检测到未佩戴安全帽的人员！")
            cv2.putText(annotated_frame, "WARNING: No Helmet!", 
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (0, 0, 255), 2)
    
    cv2.imshow('Helmet Detection', annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### 场景二：自动报警系统
```python
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def send_alert(image_path, detection_info):
    """发送警报邮件"""
    msg = MIMEText(f"""
    检测时间: {datetime.now()}
    位置: {detection_info['location']}
    违规人员数量: {detection_info['violation_count']}
    图片: {image_path}
    """)
    
    msg['Subject'] = '⚠️ 安全帽违规警报'
    msg['From'] = 'safety@company.com'
    msg['To'] = 'manager@company.com'
    
    # 发送邮件
    # smtp = smtplib.SMTP('smtp.gmail.com', 587)
    # smtp.send_message(msg)
    print(f"警报已发送: {detection_info}")

# 使用示例
results = model.predict('site_image.jpg')
violation_count = sum(1 for box in results[0].boxes 
                     if model.names[int(box.cls[0])] == 'person-without-helmet')

if violation_count > 0:
    send_alert('site_image.jpg', {
        'location': '工地A区',
        'violation_count': violation_count
    })
```

## 📊 性能优化建议

### 1. 数据增强
```python
# 在 data.yaml 中添加增强配置
augment: True
hsv_h: 0.015
hsv_s: 0.7
hsv_v: 0.4
degrees: 10.0
translate: 0.1
scale: 0.5
flipud: 0.0
fliplr: 0.5
mosaic: 1.0
```

### 2. 处理类别不平衡
```python
# 如果未戴安全帽的样本较少，可以使用：
# - 数据增强
# - 调整类别权重
# - 过采样少数类
```

### 3. 优化推理速度
```python
# 导出为 ONNX 格式
model.export(format='onnx', dynamic=True, simplify=True)

# 导出为 TensorRT（如果有 NVIDIA GPU）
model.export(format='engine', half=True)
```

## 🛠️ 故障排查

### 问题 1: 训练 Loss 不下降
```
解决方案：
✓ 检查数据集标注质量
✓ 降低学习率 (lr0=0.001)
✓ 增加训练轮数
✓ 使用预训练模型
```

### 问题 2: mAP 过低
```
解决方案：
✓ 增加数据集大小
✓ 提高图片质量
✓ 检查标注准确性
✓ 使用更大的模型 (yolo11m/l/x)
✓ 增加训练轮数
```

### 问题 3: 推理速度慢
```
解决方案：
✓ 使用更小的模型 (yolo11n)
✓ 降低输入图片尺寸
✓ 导出为 ONNX/TensorRT
✓ 使用 GPU 加速
```

## 📚 相关资源

- [Ultralytics YOLO11 文档](https://docs.ultralytics.com/)
- [Label Studio 文档](https://labelstud.io/guide/)
- [OpenCV Platform API 文档](http://localhost:8000/api/docs)
- [项目 README](./README.md)
- [Solutions 功能](./ULTRALYTICS_SOLUTIONS.md)

## 💡 最佳实践总结

1. **数据质量优先**: 高质量的标注数据比大量低质量数据更重要
2. **从小模型开始**: 先用 yolo11n 快速迭代，确认方向后再用大模型
3. **持续监控**: 定期检查模型在实际场景中的表现
4. **定期更新**: 收集误检案例，补充到训练集中重新训练
5. **版本管理**: 保存每个版本的模型和训练参数，便于回溯

## 🎯 快速开始检查清单

- [ ] 准备数据集（至少 500 张图片）
- [ ] 使用 Label Studio 标注数据
- [ ] 创建 data.yaml 配置文件
- [ ] 选择合适的模型大小（推荐从 yolo11n 开始）
- [ ] 配置训练参数
- [ ] 开始训练并监控指标
- [ ] 评估模型性能
- [ ] 部署模型到生产环境
- [ ] 设置自动报警系统
- [ ] 持续收集反馈并优化

---

**需要帮助？** 查看 [API 文档](http://localhost:8000/api/docs) 或提交 Issue
