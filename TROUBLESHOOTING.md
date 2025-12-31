# 故障排查指南

## 🔴 常见问题

### 1. 推理接口返回 500 错误

#### 问题现象
```
POST /api/v1/inference/image HTTP/1.1" 500 Internal Server Error
```

#### 可能原因

**A. 目录权限问题**（最常见）
- 容器内 `/app/data/uploads/` 目录没有写权限
- 文件无法保存导致推理失败

**解决方案：**
```bash
# 已在 Dockerfile.prod 中修复
# 如果仍有问题，手动修复：
docker exec -u root opencv-platform-dev chown -R appuser:appuser /app/data
docker exec -u root opencv-platform-dev chmod -R 777 /app/data

# 重启容器
docker compose -f docker-compose.dev.yml restart
```

**B. 模型文件缺失**
- 首次使用时模型需要下载
- 网络问题导致下载失败

**解决方案：**
```bash
# 手动下载模型
docker exec opencv-platform-dev python3 -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"

# 模型下载完成后立即可用，无需重启容器
```

**C. 依赖包缺失**
- Docker 镜像使用了旧的缓存
- 缺少 PyTorch 或 Ultralytics

**解决方案：**
```bash
# 重新构建镜像（不使用缓存）
docker compose -f docker-compose.dev.yml down --rmi all
docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up -d
```

---

### 2. 文件上传问题

#### 问题现象
- 前端显示"已选择文件"
- 但容器内 `/app/data/uploads/` 目录为空

#### 原因
**前端"已选择"≠ 已上传**

文件上传流程：
1. 选择文件 → 显示"✓ 已选择: xxx.png" → 文件在浏览器内存
2. 点击"开始推理" → 上传到服务器 → 保存到 `/app/data/uploads/`

#### 解决方案
1. 确保点击了"开始推理"按钮
2. 打开浏览器开发者工具（F12）→ Network 标签
3. 查看 POST 请求是否成功
4. 检查响应状态码和错误信息

---

### 3. Docker 镜像依赖问题

#### 问题现象
- 修改了 Dockerfile
- 但容器内依赖包没有更新

#### 原因
Docker Compose 默认使用已存在的镜像，不会自动重新构建。

#### 解决方案
```bash
# 强制重新构建
docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up -d
```

---

## 🔍 诊断步骤

### 1. 查看容器日志
```bash
# 实时日志
docker logs opencv-platform-dev -f

# 最近 100 行
docker logs opencv-platform-dev --tail 100
```

### 2. 检查容器状态
```bash
# 查看运行状态
docker ps | grep opencv-platform

# 查看资源使用
docker stats opencv-platform-dev --no-stream
```

### 3. 验证依赖安装
```bash
# 检查关键包
docker exec opencv-platform-dev pip list | grep -E "(torch|ultralytics|opencv)"
```

### 4. 测试推理功能
```bash
# 在容器内直接测试
docker exec opencv-platform-dev python3 << 'EOF'
import sys
sys.path.insert(0, '/app')

from backend.services.yolo_service import yolo_service
import numpy as np
from PIL import Image

# 创建测试图片
img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
Image.fromarray(img).save('/tmp/test.jpg')

# 执行推理
result = yolo_service.infer('/tmp/test.jpg', model_name='yolo11n.pt')
print(f"Success: {result.success}")
print(f"Detections: {len(result.detections)}")
EOF
```

---

## 📝 最佳实践

### 开发环境部署
```bash
# 1. 启动服务
docker compose -f docker-compose.dev.yml up -d

# 2. 查看日志
docker compose -f docker-compose.dev.yml logs -f

# 3. 重启服务
docker compose -f docker-compose.dev.yml restart
```

### 依赖更新
```bash
# 修改 requirements.txt 或 Dockerfile 后
docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up -d
```

### 数据持久化
- `data/` 目录已挂载到宿主机
- 模型、数据集、上传文件会保留
- 容器重启不会丢失数据

---

## 🆘 获取帮助

如果问题仍未解决，请提供：

1. **容器日志**
   ```bash
   docker logs opencv-platform-dev --tail 100 > logs.txt
   ```

2. **错误截图**
   - 浏览器控制台错误
   - Network 标签的请求详情

3. **系统信息**
   ```bash
   docker --version
   docker compose version
   ```

---

## 📚 相关文档

- [README.md](README.md) - 项目介绍和快速开始
- [DEPLOY.md](DEPLOY.md) - 详细部署指南
- [API 文档](http://localhost:8000/api/docs) - 交互式 API 文档
