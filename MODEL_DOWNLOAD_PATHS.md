# 模型自动下载路径说明

## 📍 模型下载位置

当在项目页面上运行模型训练或推理时，YOLO 模型会自动下载到以下位置：

### 1. 首次加载预训练模型

**下载位置**: 项目根目录 `/home/user/webapp/`

当你在代码中使用 `YOLO("yolo11n.pt")` 加载模型时：

```python
from ultralytics import YOLO
model = YOLO("yolo11n.pt")  # 首次会下载到当前工作目录
```

**实际路径**:
```
/home/user/webapp/yolo11n.pt  (5.4 MB)
```

### 2. 训练生成的模型

**保存位置**: `data/models/项目名称/train/weights/`

训练完成后的模型保存在：

```
/home/user/webapp/data/models/{project_name}/train/weights/
├── best.pt      # 最佳模型
├── last.pt      # 最后一轮模型
└── epoch*.pt    # 各轮检查点
```

**示例**:
```
/home/user/webapp/data/models/yolo11_coco8_20260104_025041/train/weights/best.pt
```

### 3. 用于推理的模型

如果你在项目中将训练好的模型复制到 `data/models/` 用于 API 推理：

```
/home/user/webapp/data/models/yolo11_coco8_trained.pt
```

---

## 🔍 完整路径映射

### Ultralytics 配置

根据 Ultralytics 的配置，路径如下：

| 配置项 | 路径 |
|--------|------|
| **数据集根目录** | `/home/user/webapp/datasets` |
| **权重目录** | `weights` (相对路径) |
| **运行目录** | `runs` (相对路径) |
| **配置文件** | `~/.config/Ultralytics/settings.json` |

### 当前项目中的模型文件

```
/home/user/webapp/
│
├── yolo11n.pt                    # 自动下载的预训练模型 (5.4MB)
│
└── data/models/
    ├── yolo11_coco8_trained.pt   # 用于API的训练模型 (5.3MB)
    │
    └── yolo11_coco8_20260104_025041/
        └── train/
            └── weights/
                ├── best.pt       # 最佳模型 (5.3MB)
                ├── last.pt       # 最后模型 (5.3MB)
                └── epoch*.pt     # 检查点 (16MB each)
```

---

## 🎯 不同场景的模型路径

### 场景 1: 使用预训练模型进行推理

```python
# 模型会下载到项目根目录
model = YOLO("yolo11n.pt")  
# 路径: /home/user/webapp/yolo11n.pt
```

### 场景 2: 训练自定义模型

```python
model = YOLO("yolo11n.pt")
results = model.train(
    data="dataset.yaml",
    project="data/models/my_project",  # 项目保存路径
    name="train"
)
# 模型保存在: /home/user/webapp/data/models/my_project/train/weights/best.pt
```

### 场景 3: 通过 Web API 使用模型

在 `backend/services/yolo_service.py` 中：

```python
def load_model(self, model_name: str) -> YOLO:
    model_path = settings.MODELS_DIR / model_name
    # settings.MODELS_DIR = /home/user/webapp/data/models
    
    if not model_path.exists():
        # 如果本地不存在，下载预训练模型
        model = YOLO(model_name)  # 下载到当前目录
    else:
        model = YOLO(str(model_path))
    
    return model
```

**模型查找顺序**:
1. 先查找 `/home/user/webapp/data/models/{model_name}`
2. 如果不存在，下载到项目根目录 `/home/user/webapp/{model_name}`

---

## 📋 配置说明

### 在 config/config.py 中配置

```python
# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"  # /home/user/webapp/data/models

# 默认模型
DEFAULT_MODEL: str = "yolo11n.pt"
```

### 在 Docker 环境中

如果使用 Docker 运行项目：

```yaml
# docker-compose.dev.yml
volumes:
  - ./data:/app/data  # 数据目录映射
```

**容器内路径**: `/app/data/models/`
**主机路径**: `./data/models/` (项目目录下)

---

## 🔧 如何管理模型文件

### 查看所有模型

```bash
# 查看预训练模型
ls -lh /home/user/webapp/*.pt

# 查看训练模型
ls -lh /home/user/webapp/data/models/*.pt

# 查看所有模型文件
find /home/user/webapp -name "*.pt" -type f
```

### 清理不需要的模型

```bash
# 删除根目录的预训练模型（会重新下载）
rm /home/user/webapp/yolo11n.pt

# 删除特定训练项目
rm -rf /home/user/webapp/data/models/yolo11_coco8_*

# 保留最佳模型，删除检查点
find /home/user/webapp/data/models -name "epoch*.pt" -delete
```

### 移动模型到正确位置

```bash
# 将下载的模型移到 data/models 目录
mv /home/user/webapp/yolo11n.pt /home/user/webapp/data/models/

# 将训练好的模型用于 API
cp /home/user/webapp/data/models/project/train/weights/best.pt \
   /home/user/webapp/data/models/my_model.pt
```

---

## 💡 最佳实践

### 1. 预训练模型管理

建议将预训练模型放在 `data/models/` 目录：

```python
# 在训练脚本中
model = YOLO("data/models/yolo11n.pt")  # 使用已下载的模型
```

### 2. 训练模型命名

使用有意义的项目名称：

```python
results = model.train(
    data="dataset.yaml",
    project="data/models/my_project_name",  # 清晰的项目名
    name="train_v1"                          # 版本号
)
```

### 3. 模型版本控制

为重要的模型添加日期和版本：

```bash
# 重命名最佳模型
cp best.pt my_model_v1_20260104.pt

# 或在 Git 中记录模型信息
git add data/models/my_model_info.json
```

### 4. Docker 部署时的模型管理

```dockerfile
# 在 Dockerfile 中预下载模型
RUN python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"

# 或者在构建时复制本地模型
COPY models/yolo11n.pt /app/data/models/
```

---

## 🚨 常见问题

### Q1: 为什么模型下载到了根目录？

**A**: Ultralytics 默认下载到当前工作目录。在运行脚本时：
```bash
cd /home/user/webapp && python script.py
# 模型会下载到 /home/user/webapp/
```

### Q2: 如何指定模型下载位置？

**A**: 两种方法：

1. **使用绝对路径**:
```python
model = YOLO("data/models/yolo11n.pt")
```

2. **修改工作目录**:
```python
import os
os.chdir("/home/user/webapp/data/models")
model = YOLO("yolo11n.pt")
```

### Q3: 训练时模型保存在哪里？

**A**: 由 `project` 和 `name` 参数决定：
```python
model.train(
    project="data/models/my_project",  # 项目目录
    name="train"                        # 子目录
)
# 保存在: data/models/my_project/train/weights/
```

### Q4: Docker 容器中的模型会丢失吗？

**A**: 如果没有挂载卷，容器删除后模型会丢失。需要：
```yaml
volumes:
  - ./data:/app/data  # 持久化 data 目录
```

---

## 📊 磁盘空间管理

### 模型文件大小参考

| 模型 | 大小 |
|------|------|
| YOLO11n.pt (预训练) | ~5.4 MB |
| YOLO11s.pt (预训练) | ~9.7 MB |
| YOLO11m.pt (预训练) | ~20 MB |
| 训练检查点 (epoch*.pt) | ~16 MB each |
| 优化后模型 (best.pt) | ~5.3 MB |

### 定期清理建议

```bash
# 只保留最佳模型，删除检查点（可节省大量空间）
find data/models -name "epoch*.pt" -delete

# 删除超过30天的旧训练项目
find data/models -type d -name "train" -mtime +30 -exec rm -rf {} \;
```

---

## 🔗 相关配置文件

- **项目配置**: `config/config.py`
- **YOLO 服务**: `backend/services/yolo_service.py`
- **Ultralytics 配置**: `~/.config/Ultralytics/settings.json`

---

**更新日期**: 2026-01-04  
**版本**: 1.0
