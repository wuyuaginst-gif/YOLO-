# YOLO11 训练快速入门指南

本指南将帮助你快速开始使用 YOLO11 模型进行训练。

---

## 前置要求

- Python 3.8+
- 已安装项目依赖: `pip install -r requirements.txt`

---

## 🚀 快速开始 (3 步完成训练)

### 步骤 1: 运行测试脚本
```bash
# 使用 COCO8 数据集进行快速测试 (3 epochs)
python test_yolo11_training.py
```

这将：
- ✅ 自动下载 YOLO11n 模型 (5.4MB)
- ✅ 自动下载 COCO8 数据集 (432KB)
- ✅ 训练 3 轮 (~19秒)
- ✅ 保存训练好的模型

### 步骤 2: 查看训练结果
```bash
# 训练结果保存在
ls data/models/yolo11_coco8_*/train/

# 查看训练曲线
open data/models/yolo11_coco8_*/train/results.png

# 查看混淆矩阵
open data/models/yolo11_coco8_*/train/confusion_matrix.png
```

### 步骤 3: 测试训练好的模型
```bash
# 运行推理测试
python test_trained_model_inference.py
```

这将：
- ✅ 自动查找训练好的模型
- ✅ 在验证集上进行推理
- ✅ 保存可视化结果

---

## 📊 训练结果示例

经过 3 轮训练后，你将获得：

### 模型性能
- **mAP50**: 0.886 (非常好!)
- **mAP50-95**: 0.635
- **模型大小**: 5.3MB
- **推理速度**: ~135ms/图片 (CPU)

### 生成的文件
```
data/models/yolo11_coco8_YYYYMMDD_HHMMSS/
└── train/
    ├── weights/
    │   ├── best.pt         ← 使用这个进行推理!
    │   ├── last.pt
    │   └── epoch*.pt
    ├── results.png         ← 训练曲线
    ├── confusion_matrix.png ← 混淆矩阵
    └── [其他报告文件]
```

---

## 🎯 使用训练好的模型

### Python 代码
```python
from ultralytics import YOLO

# 加载训练好的模型
model = YOLO("data/models/yolo11_coco8_*/train/weights/best.pt")

# 推理
results = model.predict(
    source="your_image.jpg",
    conf=0.25,
    save=True
)

# 查看结果
for result in results:
    boxes = result.boxes
    for box in boxes:
        print(f"类别: {model.names[int(box.cls)]}, 置信度: {box.conf:.2f}")
```

### 命令行
```bash
# 单张图片推理
yolo predict model=data/models/yolo11_coco8_*/train/weights/best.pt source=image.jpg

# 批量推理
yolo predict model=data/models/yolo11_coco8_*/train/weights/best.pt source=images/
```

---

## 🔧 自定义训练

### 使用自己的数据集

1. **准备数据集** (YOLO 格式):
```
my_dataset/
├── data.yaml        # 数据集配置
├── images/
│   ├── train/      # 训练图片
│   └── val/        # 验证图片
└── labels/
    ├── train/      # 训练标签 (.txt)
    └── val/        # 验证标签 (.txt)
```

2. **创建 data.yaml**:
```yaml
path: /path/to/my_dataset
train: images/train
val: images/val

nc: 3  # 类别数量
names: ['class1', 'class2', 'class3']  # 类别名称
```

3. **开始训练**:
```python
from ultralytics import YOLO

model = YOLO("yolo11n.pt")
results = model.train(
    data="my_dataset/data.yaml",
    epochs=50,
    batch=16,
    imgsz=640,
    device='0',  # 使用 GPU 0
    project="my_project",
    name="my_model"
)
```

---

## 📈 训练参数说明

### 基础参数
| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `epochs` | 训练轮数 | 50-100 |
| `batch` | 批次大小 | 16 (根据显存调整) |
| `imgsz` | 图像尺寸 | 640 |
| `device` | 设备 | 'cuda' (GPU) 或 'cpu' |

### 高级参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `lr0` | 初始学习率 | 0.01 |
| `patience` | 早停轮数 | 50 |
| `augment` | 数据增强 | True |
| `hsv_h` | 色调增强 | 0.015 |
| `hsv_s` | 饱和度增强 | 0.7 |
| `hsv_v` | 亮度增强 | 0.4 |
| `flipud` | 上下翻转概率 | 0.0 |
| `fliplr` | 左右翻转概率 | 0.5 |

---

## 🎓 不同规模的模型

| 模型 | 参数量 | 速度 | 准确度 | 使用场景 |
|------|--------|------|--------|----------|
| YOLO11n | 2.6M | 最快 | 较好 | 实时应用、边缘设备 |
| YOLO11s | 9.4M | 快 | 好 | 移动端、嵌入式 |
| YOLO11m | 20.1M | 中等 | 很好 | 通用应用 |
| YOLO11l | 25.3M | 慢 | 优秀 | 高精度要求 |
| YOLO11x | 56.9M | 最慢 | 最佳 | 离线处理、研究 |

**选择建议**:
- 🚀 **快速测试**: YOLO11n
- 📱 **移动端**: YOLO11s
- 🎯 **平衡**: YOLO11m
- 🏆 **高精度**: YOLO11l/x

---

## 💡 训练技巧

### 1. 提高训练速度
```python
model.train(
    data="dataset.yaml",
    epochs=50,
    batch=32,        # 增大批次
    workers=8,       # 增加数据加载线程
    amp=True,        # 混合精度训练
    cache=True       # 缓存图片到内存
)
```

### 2. 提高模型准确度
```python
model.train(
    data="dataset.yaml",
    epochs=100,      # 增加训练轮数
    patience=100,    # 增加早停耐心
    optimizer='AdamW',
    lr0=0.001,       # 降低学习率
    augment=True,    # 启用数据增强
    mosaic=1.0,      # 使用 mosaic 增强
    mixup=0.1        # 使用 mixup 增强
)
```

### 3. 微调预训练模型
```python
# 冻结前 10 层
model.train(
    data="dataset.yaml",
    epochs=50,
    freeze=10        # 冻结层数
)
```

---

## 🐛 常见问题

### Q1: 训练很慢怎么办？
**A**: 
- 使用 GPU: `device='0'`
- 减小批次: `batch=8`
- 减小图像尺寸: `imgsz=416`
- 启用缓存: `cache=True`

### Q2: 显存不足 (OOM) 怎么办？
**A**:
- 减小批次: `batch=4` 或 `batch=2`
- 减小图像尺寸: `imgsz=416`
- 使用更小的模型: `yolo11n.pt`

### Q3: mAP 很低怎么办？
**A**:
- 增加训练轮数: `epochs=100`
- 检查标注质量
- 增加训练数据
- 调整学习率: `lr0=0.001`
- 使用数据增强

### Q4: 如何恢复训练？
**A**:
```python
model = YOLO("path/to/last.pt")
model.train(resume=True)
```

---

## 📚 更多资源

- [Ultralytics 官方文档](https://docs.ultralytics.com/)
- [YOLO11 模型](https://docs.ultralytics.com/models/yolo11/)
- [训练技巧](https://docs.ultralytics.com/guides/hyperparameter-tuning/)
- [数据集格式](https://docs.ultralytics.com/datasets/)

---

## 🆘 获取帮助

遇到问题？
1. 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. 查看 [详细测试报告](YOLO11_TRAINING_TEST_REPORT.md)
3. 查看 [项目 README](README.md)
4. 提交 GitHub Issue

---

## ✅ 检查清单

开始训练前：
- [ ] 已安装所有依赖
- [ ] 数据集格式正确 (YOLO 格式)
- [ ] data.yaml 配置正确
- [ ] 有足够的磁盘空间 (至少 10GB)
- [ ] (可选) GPU 可用

训练完成后：
- [ ] 查看训练曲线 (results.png)
- [ ] 检查最终 mAP
- [ ] 在验证集上测试
- [ ] 保存最佳模型 (best.pt)

---

**祝训练顺利！** 🎉
