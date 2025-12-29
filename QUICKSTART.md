# 快速开始指南

5 分钟快速上手 OpenCV Platform！

## 🚀 使用 Docker（最简单）

### 1. 启动服务

```bash
# 克隆项目
git clone <repository-url>
cd webapp

# 启动所有服务
./scripts/start.sh
```

### 2. 访问应用

- **OpenCV Platform**: http://localhost:8000
- **API 文档**: http://localhost:8000/api/docs
- **Label Studio**: http://localhost:8080

### 3. 测试推理

1. 打开 http://localhost:8000/inference
2. 上传一张图片
3. 点击"开始推理"
4. 查看检测结果

---

## 🔧 本地开发

### 1. 环境设置

```bash
# 运行设置脚本
./scripts/setup.sh

# 激活虚拟环境
source venv/bin/activate
```

### 2. 启动开发服务器

```bash
python app.py
```

### 3. 访问应用

打开浏览器访问 http://localhost:8000

---

## 📝 完整工作流示例

### 场景：训练一个自定义目标检测模型

#### 第 1 步：准备数据

```bash
# 创建数据集目录
mkdir -p data/datasets/my_dataset/{images,labels}/{train,val}

# 上传图片到对应目录
# images/train/ - 训练图片
# images/val/ - 验证图片
```

#### 第 2 步：数据标注

1. 访问 http://localhost:8080 (Label Studio)
2. 创建新项目 "My Detection Project"
3. 导入图片
4. 开始标注（绘制边界框）
5. 完成标注后导出为 YOLO 格式

#### 第 3 步：训练模型

1. 访问 http://localhost:8000/training
2. 填写训练配置：
   - 项目名称: `my_model`
   - 数据集路径: `data/datasets/my_dataset/data.yaml`
   - 模型类型: `yolov8n`
   - 训练轮数: `100`
3. 点击"开始训练"
4. 等待训练完成

#### 第 4 步：测试模型

1. 访问 http://localhost:8000/inference
2. 选择训练好的模型
3. 上传测试图片
4. 查看检测结果

---

## 🎯 API 使用示例

### Python 示例

```python
import requests

# 图片推理
url = "http://localhost:8000/api/v1/inference/image"
files = {"file": open("test.jpg", "rb")}
data = {"model_name": "yolov8n.pt", "confidence": 0.25}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"检测到 {len(result['detections'])} 个对象")
for det in result['detections']:
    print(f"- {det['class_name']}: {det['confidence']:.2f}")
```

### cURL 示例

```bash
# 推理请求
curl -X POST "http://localhost:8000/api/v1/inference/image" \
  -F "file=@test.jpg" \
  -F "model_name=yolov8n.pt" \
  -F "confidence=0.25"

# 获取系统信息
curl "http://localhost:8000/api/v1/system/info"

# 列出模型
curl "http://localhost:8000/api/v1/models/list"
```

---

## ⚠️ 常见问题

### Q1: 端口被占用怎么办？

编辑 `.env` 文件修改端口：
```env
API_PORT=8001
LABEL_STUDIO_PORT=8081
```

### Q2: 如何使用 GPU 训练？

在训练配置中设置：
```json
{
  "device": "cuda"  // 或 "0" 指定第一块 GPU
}
```

### Q3: Label Studio 连接失败？

检查 Label Studio 是否运行：
```bash
docker-compose ps labelstudio
docker-compose logs labelstudio
```

---

## 📚 下一步

- 阅读完整文档: [README.md](README.md)
- 探索 API: http://localhost:8000/api/docs

---

祝使用愉快！如有问题请提交 Issue。
