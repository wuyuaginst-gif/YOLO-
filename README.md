# OpenCV Platform - 开源计算机视觉平台

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**基于 Ultralytics YOLO 和 Supervision 的开源计算机视觉平台**

提供数据标注、模型训练、API 部署的完整工作流

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用文档](#使用文档) • [架构设计](#架构设计)

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
  - [方式一：Docker 开发环境](#方式一docker-开发环境)
  - [方式二：Docker 生产环境](#方式二docker-生产环境)
  - [方式三：本地开发](#方式三本地开发)
- [使用文档](#使用文档)
- [API 文档](#api-文档)
- [架构设计](#架构设计)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 🎯 项目简介

**OpenCV Platform** 是一个基于 Ultralytics YOLO 和 Supervision 的开源计算机视觉平台，提供从数据标注到模型部署的完整工作流。

### 核心特性

```
数据标注 (Supervision) → 模型训练 (YOLO) → API 部署 (FastAPI)
```

**v2.0 更新：**
- ✅ 使用 `supervision` 库替代 Label Studio，提供更强大的标注和可视化功能
- ✅ 简化架构，移除外部依赖服务
- ✅ 优化 Docker 部署配置
- ✅ 新增自动标注功能

---

## ✨ 功能特性

### 🎨 数据标注
- ✅ 基于 Supervision 的智能标注系统
- ✅ 自动标注：使用预训练模型快速标注
- ✅ 手动标注：支持目标检测框标注
- ✅ 标注可视化：实时查看标注结果
- ✅ 一键导出为 YOLO 格式数据集

### 🚀 模型训练
- ✅ 基于 Ultralytics YOLO (最新版本)
- ✅ 支持自定义训练参数配置
- ✅ 实时训练进度监控
- ✅ 自动保存最佳模型权重
- ✅ 支持 CPU/GPU 训练

### 🔌 模型部署
- ✅ RESTful API 接口
- ✅ 单张图片推理
- ✅ 批量图片推理
- ✅ 实时检测结果可视化
- ✅ 多种模型格式导出 (ONNX, TorchScript 等)

### 🎯 Ultralytics Solutions
- ✅ **对象计数** - 统计进出区域的对象数量
- ✅ **热图生成** - 可视化检测密度热点
- ✅ **速度估算** - 计算对象移动速度
- ✅ **距离计算** - 测量对象之间距离
- ✅ **对象模糊** - 隐私保护（人脸/车牌模糊）
- ✅ **对象裁剪** - 自动提取检测对象
- ✅ **队列管理** - 监控队列长度和等待时间

### 📦 平台管理
- ✅ 模型管理（上传、列表、删除）
- ✅ 数据集管理（上传、列表、统计）
- ✅ 系统监控（GPU 状态、资源使用）
- ✅ Web UI 管理界面

---

## 🛠 技术栈

### 后端
- **FastAPI** - 高性能 Web 框架
- **Ultralytics YOLO** - 最新计算机视觉模型库
- **Supervision** - 强大的计算机视觉工具库
- **PyTorch** - 深度学习框架
- **OpenCV** - 图像处理库

### 前端
- **原生 JavaScript** - 轻量级前端
- **HTML5 + CSS3** - 现代化 UI
- **Responsive Design** - 响应式设计

### 部署
- **Docker** - 容器化部署
- **Docker Compose** - 服务编排
- **Uvicorn** - ASGI 服务器

---

## 📁 项目结构

```
webapp/
├── app.py                      # FastAPI 主应用
├── requirements.txt            # Python 依赖
├── Dockerfile                  # Docker 镜像配置
├── Dockerfile.prod             # 生产环境 Docker 配置
├── docker-compose.dev.yml      # 开发环境编排
├── docker-compose.prod.yml     # 生产环境编排
├── .env.example                # 环境配置示例
├── .gitignore                  # Git 忽略文件
│
├── backend/                    # 后端代码
│   ├── api/                    # API 路由
│   │   └── routes.py           # 路由定义
│   ├── models/                 # 数据模型
│   │   └── schemas.py          # Pydantic 模型
│   ├── services/               # 业务逻辑
│   │   ├── yolo_service.py     # YOLO 服务
│   │   ├── supervision_service.py  # Supervision 服务
│   │   ├── annotation_service.py   # 标注服务
│   │   └── solutions_service.py    # Solutions 服务
│   └── utils/                  # 工具函数
│       └── file_utils.py       # 文件处理工具
│
├── frontend/                   # 前端代码
│   ├── index.html              # 首页
│   ├── inference.html          # 推理页面
│   ├── training.html           # 训练页面
│   ├── models.html             # 模型管理页面
│   ├── datasets.html           # 数据集页面
│   ├── annotation.html         # 标注页面
│   └── static/                 # 静态资源
│       ├── css/                # 样式文件
│       └── js/                 # JavaScript
│
├── config/                     # 配置文件
│   └── config.py               # 应用配置
│
├── data/                       # 数据目录
│   ├── datasets/               # 数据集
│   ├── models/                 # 模型文件
│   ├── exports/                # 导出文件
│   ├── uploads/                # 上传文件
│   └── annotation_projects/    # 标注项目
│
└── scripts/                    # 脚本工具
    ├── setup.sh                # 环境设置
    ├── start.sh                # 启动服务
    └── stop.sh                 # 停止服务
```

---

## 🚀 快速开始

### 前置要求

- **Docker & Docker Compose** (Docker 部署)
- **Python 3.8+** (本地开发)

### 方式一：Docker 开发环境

适合开发和调试，支持代码热重载。

```bash
# 1. 克隆项目
git clone <repository-url>
cd webapp

# 2. 配置环境变量（可选）
cp .env.example .env

# 3. 启动开发环境（首次需要构建镜像）
docker compose -f docker-compose.dev.yml up -d --build

# 4. 验证部署（可选）
./scripts/verify_deployment.sh

# 5. 查看日志
docker compose -f docker-compose.dev.yml logs -f

# 6. 停止服务
docker compose -f docker-compose.dev.yml down
```

**访问应用：**
- **OpenCV Platform**: http://localhost:8000
- **API 文档**: http://localhost:8000/api/docs

**⚠️ 首次使用注意事项：**
- 首次推理时模型会自动下载（约 6 MB），需要网络连接
- 如遇到问题，查看 [故障排查指南](TROUBLESHOOTING.md)

### 方式二：Docker 生产环境

适合生产部署，性能优化。

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要参数

# 2. 构建并启动生产环境
docker compose -f docker-compose.prod.yml up -d

# 3. 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 4. 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 5. 停止服务
docker compose -f docker-compose.prod.yml down
```

### 方式三：本地开发

```bash
# 1. 设置环境
./scripts/setup.sh

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python app.py

# 或使用 uvicorn 启动（支持热重载）
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

---

## 📖 使用文档

### 1. 数据标注工作流

#### 创建标注项目
1. 访问标注页面
2. 创建新项目，输入项目名称和描述
3. 上传待标注图片

#### 自动标注（推荐）
1. 选择预训练模型（如 yolov8n.pt）
2. 设置置信度阈值
3. 点击"自动标注"
4. 系统自动标注所有图片

#### 手动标注
1. 选择图片
2. 绘制检测框
3. 选择类别
4. 保存标注

#### 导出数据集
1. 检查标注结果
2. 点击"导出为 YOLO 格式"
3. 数据集保存到 `data/datasets/` 目录

### 2. 模型训练工作流

#### 准备数据集
确保数据集符合 YOLO 格式：
```
dataset/
├── data.yaml          # 数据集配置
├── images/
│   ├── train/         # 训练图片
│   └── val/           # 验证图片
└── labels/
    ├── train/         # 训练标签
    └── val/           # 验证标签
```

#### 配置训练参数
- 项目名称
- 数据集路径
- 模型类型 (YOLO11n/s/m/l/x)
- 训练轮数
- 批次大小
- 图像尺寸

#### 开始训练
点击"开始训练"按钮，训练任务将在后台运行。

#### 监控进度
在训练任务列表中查看训练进度、当前轮数和指标。

### 3. 模型推理工作流

#### 单张图片推理
```bash
# 使用 curl
curl -X POST "http://localhost:8000/api/v1/inference/image" \
  -F "file=@image.jpg" \
  -F "model_name=yolov8n.pt" \
  -F "confidence=0.25"
```

#### Python SDK
```python
import requests

# 推理请求
files = {'file': open('image.jpg', 'rb')}
data = {
    'model_name': 'yolov8n.pt',
    'confidence': 0.25
}
response = requests.post(
    'http://localhost:8000/api/v1/inference/image',
    files=files,
    data=data
)
result = response.json()
print(result)
```

### 4. Supervision 功能使用

#### 标注可视化
```python
# 使用 API 可视化标注
GET /api/v1/annotation/visualize/{project_id}/{image_name}
```

#### 对象追踪
Supervision 提供强大的对象追踪功能，可用于视频分析。

#### 区域检测
设置多边形区域，统计区域内的对象数量。

---

## 📚 API 文档

### 系统信息

#### GET `/api/v1/system/info`
获取系统信息

**响应示例：**
```json
{
  "app_name": "OpenCV Platform",
  "version": "2.0.0",
  "python_version": "3.9.0",
  "ultralytics_version": "8.0.0",
  "total_models": 5,
  "total_datasets": 3,
  "gpu_available": true,
  "gpu_info": "NVIDIA GeForce RTX 3080"
}
```

### 标注接口

#### POST `/api/v1/annotation/auto-annotate/{project_id}`
使用 YOLO 模型自动标注项目

**请求参数：**
- `model_name`: 模型名称 (可选，默认 yolov8n.pt)
- `confidence`: 置信度阈值 (可选，默认 0.25)
- `iou_threshold`: IOU 阈值 (可选，默认 0.45)

**响应示例：**
```json
{
  "success": true,
  "message": "Auto annotation completed",
  "total_images": 100,
  "total_detections": 350,
  "classes": ["person", "car", "dog"]
}
```

### 推理接口

#### POST `/api/v1/inference/image`
单张图片推理

**响应示例：**
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
  "inference_time": 0.023
}
```

完整 API 文档请访问：http://localhost:8000/api/docs

---

## 🏗 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│                  (Frontend UI)                          │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Application                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Routes     │  │   Services   │  │    Models    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼─────────┐ ┌▼──────────────┐
│ Ultralytics  │ │ Supervision│ │  File System  │
│    YOLO      │ │   Library  │ │   Storage     │
└──────────────┘ └────────────┘ └───────────────┘
```

### 数据流

```
原始图片
    ↓
自动/手动标注 (Supervision)
    ↓
导出为 YOLO 格式
    ↓
存储到数据集目录
    ↓
加载数据集进行训练
    ↓
保存训练好的模型
    ↓
通过 API 提供推理服务
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - 强大的目标检测框架
- [Supervision](https://github.com/roboflow/supervision) - 优秀的计算机视觉工具库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Web 框架

---

<div align="center">

⭐ 如果这个项目对你有帮助，请给它一个 Star！⭐

Made with ❤️ by OpenCV Platform Team

</div>
