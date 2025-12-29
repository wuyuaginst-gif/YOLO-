# OpenCV Platform - 开源计算机视觉平台

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**基于 Ultralytics YOLO 的开源计算机视觉平台**

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
  - [方式一：Docker 部署（推荐）](#方式一docker-部署推荐)
  - [方式二：本地开发](#方式二本地开发)
- [使用文档](#使用文档)
- [API 文档](#api-文档)
- [架构设计](#架构设计)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 🎯 项目简介

**OpenCV Platform** 是一个基于 Ultralytics YOLO 的开源计算机视觉平台，旨在提供一个完整的 CV 项目开发工作流，类似于海康开放平台（Open Hikvision）或 Brain++ AI 平台。

### MVP 核心功能

本项目是一个 **最小可行产品 (MVP)**，专注于实现从数据标注到模型部署的完整闭环：

```
数据标注 (Label Studio) → 模型训练 (YOLO) → API 部署 (FastAPI)
```

---

## ✨ 功能特性

### 🎨 数据标注
- ✅ 集成 Label Studio 标注平台
- ✅ 支持目标检测、图像分割等多种任务
- ✅ 一键导出为 YOLO 格式数据集
- ✅ 可视化标注管理界面

### 🚀 模型训练
- ✅ 基于 Ultralytics YOLO (v8)
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

### 📦 平台管理
- ✅ 模型管理（上传、列表、删除）
- ✅ 数据集管理（上传、列表、统计）
- ✅ 系统监控（GPU 状态、资源使用）
- ✅ Web UI 管理界面

---

## 🛠 技术栈

### 后端
- **FastAPI** - 高性能 Web 框架
- **Ultralytics YOLO** - 计算机视觉模型库
- **PyTorch** - 深度学习框架
- **OpenCV** - 图像处理库

### 前端
- **原生 JavaScript** - 轻量级前端
- **HTML5 + CSS3** - 现代化 UI
- **Responsive Design** - 响应式设计

### 数据标注
- **Label Studio** - 开源数据标注平台

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
├── docker-compose.yml          # Docker 编排配置
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
│   │   └── labelstudio_service.py  # Label Studio 集成
│   └── utils/                  # 工具函数
│       └── file_utils.py       # 文件处理工具
│
├── frontend/                   # 前端代码
│   ├── index.html              # 首页
│   ├── inference.html          # 推理页面
│   ├── training.html           # 训练页面
│   ├── models.html             # 模型管理页面
│   ├── datasets.html           # 数据集页面
│   ├── labelstudio.html        # 标注页面
│   └── static/                 # 静态资源
│       ├── css/                # 样式文件
│       │   └── style.css
│       └── js/                 # JavaScript
│           └── api.js          # API 调用
│
├── config/                     # 配置文件
│   └── config.py               # 应用配置
│
├── data/                       # 数据目录
│   ├── datasets/               # 数据集
│   ├── models/                 # 模型文件
│   ├── exports/                # 导出文件
│   └── uploads/                # 上传文件
│
└── scripts/                    # 脚本工具
    ├── setup.sh                # 环境设置
    ├── start.sh                # 启动服务
    ├── stop.sh                 # 停止服务
    └── dev.sh                  # 开发模式
```

---

## 🚀 快速开始

### 前置要求

- **Python 3.8+** (本地开发)
- **Docker & Docker Compose** (Docker 部署)
- **Label Studio** (已安装或使用 Docker 版本)

### 方式一：Docker 部署（推荐）

1️⃣ **克隆项目**
```bash
git clone <repository-url>
cd webapp
```

2️⃣ **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要参数
```

3️⃣ **启动服务**
```bash
./scripts/start.sh
```

4️⃣ **访问应用**
- **OpenCV Platform**: http://localhost:8000
- **API 文档**: http://localhost:8000/api/docs
- **Label Studio**: http://localhost:8080

### 方式二：本地开发

1️⃣ **设置环境**
```bash
./scripts/setup.sh
```

2️⃣ **启动开发服务器**
```bash
./scripts/dev.sh
```

或者手动启动：
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

---

## 📖 使用文档

### 1. 数据标注工作流

#### 步骤 1：创建标注项目
1. 访问 Label Studio: http://localhost:8080
2. 创建新项目，配置标注任务
3. 上传待标注图片
4. 开始标注工作

#### 步骤 2：导出标注数据
1. 在 OpenCV Platform 的"数据标注"页面
2. 选择 Label Studio 项目
3. 点击"导出为 YOLO 格式"
4. 数据集将保存到 `data/datasets/` 目录

### 2. 模型训练工作流

#### 步骤 1：准备数据集
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

#### 步骤 2：配置训练参数
在"模型训练"页面配置：
- 项目名称
- 数据集路径
- 模型类型 (YOLOv8n/s/m/l/x)
- 训练轮数
- 批次大小
- 图像尺寸

#### 步骤 3：开始训练
点击"开始训练"按钮，训练任务将在后台运行。

#### 步骤 4：监控进度
在训练任务列表中查看训练进度、当前轮数和指标。

### 3. 模型推理工作流

#### 单张图片推理
1. 访问"模型推理"页面
2. 选择模型和参数
3. 上传图片
4. 点击"开始推理"
5. 查看检测结果和可视化

#### API 调用示例
```python
import requests

# 推理请求
files = {'file': open('image.jpg', 'rb')}
data = {
    'model_name': 'yolov8n.pt',
    'confidence': 0.25
}
response = requests.post('http://localhost:8000/api/v1/inference/image', 
                        files=files, data=data)
result = response.json()
print(result)
```

---

## 📚 API 文档

### 系统信息

#### GET `/api/v1/system/info`
获取系统信息

**响应示例：**
```json
{
  "app_name": "OpenCV Platform",
  "version": "1.0.0",
  "python_version": "3.9.0",
  "ultralytics_version": "8.0.0",
  "total_models": 5,
  "total_datasets": 3,
  "gpu_available": true,
  "gpu_info": "NVIDIA GeForce RTX 3080"
}
```

### 推理接口

#### POST `/api/v1/inference/image`
单张图片推理

**请求参数：**
- `file`: 图片文件 (multipart/form-data)
- `model_name`: 模型名称 (可选)
- `confidence`: 置信度阈值 (可选)
- `iou_threshold`: IOU 阈值 (可选)

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
  "inference_time": 0.023,
  "image_shape": [640, 480, 3]
}
```

### 训练接口

#### POST `/api/v1/training/start`
开始训练任务

**请求体：**
```json
{
  "project_name": "my_project",
  "dataset_path": "data/datasets/my_dataset/data.yaml",
  "model_type": "yolov8n",
  "epochs": 100,
  "batch_size": 16,
  "img_size": 640,
  "device": "cpu"
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
│ Ultralytics  │ │   Label    │ │  File System  │
│    YOLO      │ │   Studio   │ │   Storage     │
└──────────────┘ └────────────┘ └───────────────┘
```

### 数据流

```
标注数据 (Label Studio)
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

## ❓ 常见问题

### Q: 如何使用 GPU 训练？
A: 确保安装了 CUDA 和 PyTorch GPU 版本，然后在训练配置中设置 `device: "cuda"`。

### Q: Label Studio 无法连接？
A: 检查 Label Studio 是否正常运行，确认 `.env` 文件中的 `LABEL_STUDIO_URL` 配置正确。

### Q: 如何添加自定义模型？
A: 将 `.pt` 模型文件上传到 `data/models/` 目录，或通过"模型管理"页面上传。

### Q: Python 3.6 兼容性问题？
A: 本项目推荐使用 Python 3.8+。如果必须使用 Python 3.6，可能需要降低某些依赖库的版本。

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

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 加入讨论群

---

## 🙏 致谢

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - 强大的目标检测框架
- [Label Studio](https://labelstud.io/) - 优秀的数据标注平台
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Web 框架

---

<div align="center">

⭐ 如果这个项目对你有帮助，请给它一个 Star！⭐

Made with ❤️ by OpenCV Platform Team

</div>
