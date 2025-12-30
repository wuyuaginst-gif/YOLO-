# Docker 部署中 Logo 不显示问题修复指南

## 🔍 问题诊断

### 问题描述
使用 `docker-compose -f docker-compose.prod.yml build` 部署后，公司 logo (`company-logo.png`) 没有显示。

### 可能原因

1. **文件权限问题** - Docker 容器内用户权限不足
2. **文件路径问题** - 静态文件未正确复制到容器
3. **静态文件挂载问题** - FastAPI 静态文件路径配置错误
4. **缓存问题** - 浏览器或 Docker 缓存

## ✅ 解决方案

### 方案 1：验证文件是否在容器中（推荐先做）

```bash
# 1. 构建镜像
docker-compose -f docker-compose.prod.yml build

# 2. 启动容器
docker-compose -f docker-compose.prod.yml up -d

# 3. 进入容器检查文件
docker exec -it opencv-platform-prod ls -la /app/frontend/static/

# 4. 检查文件是否存在
docker exec -it opencv-platform-prod ls -lh /app/frontend/static/company-logo.png
```

**预期输出**：
```
-rw-r--r-- 1 appuser appuser 419K Dec 30 10:21 /app/frontend/static/company-logo.png
```

### 方案 2：修复 Dockerfile.prod 权限问题

如果文件存在但无法访问，修改 `Dockerfile.prod`：

```dockerfile
# 在 USER appuser 之前添加
RUN chmod -R 755 /app && \
    chmod -R 755 /app/frontend/static && \
    chmod 644 /app/frontend/static/company-logo.png && \
    chown -R appuser:appuser /app
```

### 方案 3：优化 Dockerfile.prod 文件复制

在 `Dockerfile.prod` 中明确复制静态文件：

```dockerfile
# 复制应用代码
COPY . .

# 确保静态文件被复制
COPY frontend/static /app/frontend/static

# 设置正确的文件权限
RUN chmod -R 755 /app && \
    chmod -R 755 /app/frontend/static && \
    chmod 644 /app/frontend/static/*.png && \
    chmod -R 777 /app/data && \
    chmod -R 777 /app/logs
```

### 方案 4：检查 .dockerignore 文件

确保 `.dockerignore` 没有忽略静态文件：

```bash
# 检查是否误忽略了静态文件
cat .dockerignore | grep -i "static\|frontend\|\.png"
```

如果发现问题，从 `.dockerignore` 中移除相关规则。

### 方案 5：清理 Docker 缓存重新构建

```bash
# 1. 停止并删除容器
docker-compose -f docker-compose.prod.yml down

# 2. 清理 Docker 缓存
docker system prune -af

# 3. 重新构建（不使用缓存）
docker-compose -f docker-compose.prod.yml build --no-cache

# 4. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 5. 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 方案 6：添加调试日志

在 `app.py` 中添加调试信息：

```python
# 挂载静态文件
static_dir = project_root / "frontend" / "static"
print(f"[DEBUG] Static directory path: {static_dir}")
print(f"[DEBUG] Static directory exists: {static_dir.exists()}")

if static_dir.exists():
    # 列出静态文件
    print(f"[DEBUG] Files in static dir: {list(static_dir.glob('*'))}")
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    print("[DEBUG] Static files mounted successfully")
else:
    print("[ERROR] Static directory not found!")
```

## 🚀 完整修复版 Dockerfile.prod

```dockerfile
# OpenCV Platform Production Dockerfile
# Python 3.12 + 静态文件优化版本
FROM python:3.12-slim-bookworm

LABEL maintainer="OpenCV Platform"
LABEL description="基于 Ultralytics YOLO 的开源计算机视觉平台 (Python 3.12 生产版)"
LABEL version="1.0.0"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    curl \
    wget \
    git \
    gcc \
    g++ \
    libxcb1 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建必要的目录结构
RUN mkdir -p \
    /app/data/datasets \
    /app/data/models \
    /app/data/exports \
    /app/data/uploads \
    /app/data/annotation_projects \
    /app/logs \
    /app/frontend/static

# 复制依赖文件
COPY requirements.txt .

# 升级 pip 并安装 Python 依赖
RUN pip install --upgrade pip setuptools wheel && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt && \
    pip install \
    opencv-python-headless>=4.8.0 \
    ultralytics>=8.0.0 \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    python-multipart>=0.0.6 \
    jinja2>=3.1.2 \
    pyyaml>=6.0 \
    requests>=2.31.0 \
    Pillow>=10.0.0 \
    numpy>=1.24.0

# 复制应用代码（分层复制以利用缓存）
COPY backend /app/backend
COPY config /app/config
COPY frontend /app/frontend
COPY app.py /app/
COPY *.py /app/

# 确保静态文件目录存在且有正确权限
RUN ls -la /app/frontend/static/ && \
    test -f /app/frontend/static/company-logo.png || echo "WARNING: Logo file not found!"

# 设置正确的文件权限
RUN chmod -R 755 /app && \
    chmod -R 755 /app/frontend && \
    chmod -R 755 /app/frontend/static && \
    chmod 644 /app/frontend/static/*.png 2>/dev/null || true && \
    chmod -R 777 /app/data && \
    chmod -R 777 /app/logs

# 创建非 root 用户运行应用
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/system/health').read()" || exit 1

# 启动命令
CMD ["python3", "app.py"]
```

## 🔧 测试步骤

### 1. 本地测试

```bash
# 测试静态文件访问
curl -I http://localhost:8000/static/company-logo.png

# 预期响应
HTTP/1.1 200 OK
content-type: image/png
```

### 2. 容器内测试

```bash
# 进入容器
docker exec -it opencv-platform-prod bash

# 检查文件
ls -lh /app/frontend/static/company-logo.png

# 检查权限
stat /app/frontend/static/company-logo.png

# 测试访问
curl -I http://localhost:8000/static/company-logo.png
```

### 3. 浏览器测试

1. 打开浏览器
2. 访问：`http://your-server:8000`
3. 打开开发者工具 (F12)
4. 查看 Network 标签
5. 检查 `company-logo.png` 的加载状态

## 📝 常见错误及解决

### 错误 1: 404 Not Found

**原因**: 静态文件路径不正确

**解决**:
```bash
# 检查 FastAPI 日志
docker logs opencv-platform-prod | grep static

# 确认路径
docker exec opencv-platform-prod python3 -c "from pathlib import Path; print(Path('/app/frontend/static').exists())"
```

### 错误 2: 403 Forbidden

**原因**: 文件权限问题

**解决**:
```bash
# 修复权限
docker exec -u root opencv-platform-prod chmod 644 /app/frontend/static/company-logo.png
docker exec -u root opencv-platform-prod chown appuser:appuser /app/frontend/static/company-logo.png
```

### 错误 3: 图片损坏

**原因**: 文件复制过程中损坏

**解决**:
```bash
# 对比文件大小
ls -lh frontend/static/company-logo.png
docker exec opencv-platform-prod ls -lh /app/frontend/static/company-logo.png

# 重新复制
docker cp frontend/static/company-logo.png opencv-platform-prod:/app/frontend/static/
```

## 🎯 快速修复脚本

创建 `fix-logo.sh`:

```bash
#!/bin/bash

echo "🔧 修复 Docker 部署中的 Logo 问题..."

# 1. 停止容器
echo "1. 停止现有容器..."
docker-compose -f docker-compose.prod.yml down

# 2. 清理缓存
echo "2. 清理 Docker 缓存..."
docker system prune -f

# 3. 重新构建（不使用缓存）
echo "3. 重新构建镜像..."
docker-compose -f docker-compose.prod.yml build --no-cache

# 4. 启动服务
echo "4. 启动服务..."
docker-compose -f docker-compose.prod.yml up -d

# 5. 等待服务启动
echo "5. 等待服务启动..."
sleep 10

# 6. 检查文件
echo "6. 检查 Logo 文件..."
docker exec opencv-platform-prod ls -lh /app/frontend/static/company-logo.png

# 7. 测试访问
echo "7. 测试静态文件访问..."
docker exec opencv-platform-prod curl -I http://localhost:8000/static/company-logo.png

echo "✅ 修复完成！请访问 http://localhost:8000 查看效果"
```

运行修复：
```bash
chmod +x fix-logo.sh
./fix-logo.sh
```

## 📌 最佳实践

1. **始终使用 --no-cache 重新构建**
   ```bash
   docker-compose -f docker-compose.prod.yml build --no-cache
   ```

2. **验证文件权限**
   ```bash
   # 构建前检查
   ls -la frontend/static/company-logo.png
   
   # 构建后检查
   docker exec opencv-platform-prod ls -la /app/frontend/static/company-logo.png
   ```

3. **使用多阶段构建优化镜像**
4. **添加健康检查日志**
5. **定期清理 Docker 缓存**

## 🔗 相关链接

- [FastAPI 静态文件文档](https://fastapi.tiangolo.com/tutorial/static-files/)
- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [Dockerfile 参考](https://docs.docker.com/engine/reference/builder/)
