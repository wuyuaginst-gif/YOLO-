# Docker 构建优化指南

## 🎯 问题描述

每次更新代码都需要重新构建 Docker 镜像，导致重复安装 Python 依赖，非常耗时。

## 💡 解决方案

### 方案一：优化 Dockerfile 分层（推荐）⭐

**原理**: Docker 使用分层缓存机制，只有当某一层的内容发生变化时，才会重新构建该层及后续层。

#### 1. 优化后的 Dockerfile.prod

```dockerfile
# 关键优化：将依赖安装和代码复制分离
# 1. 先复制依赖文件
COPY requirements.txt .

# 2. 安装依赖（这一层会被缓存）
RUN pip install --no-cache-dir -r requirements.txt

# 3. 最后复制应用代码（代码变化不会触发依赖重装）
COPY . .
```

#### 2. 现有问题分析

```dockerfile
# ❌ 问题：代码和依赖在同一层
COPY . .
RUN pip install -r requirements.txt

# 当代码变化时，COPY . . 层失效
# 导致后续的 pip install 也要重新执行
```

#### 3. 立即应用优化

我已经在 `Dockerfile.prod` 中应用了这个优化：
- 第 44 行：先复制 `requirements.txt`
- 第 47-70 行：安装所有依赖（这一层会被缓存）
- 第 73 行：最后复制应用代码

**效果**：
- ✅ 首次构建：~5-10 分钟
- ✅ 代码更新后重新构建：~30 秒-1 分钟（跳过依赖安装）

### 方案二：使用 Docker Compose 开发模式 ⭐⭐⭐

**原理**: 将代码目录挂载到容器中，修改代码后无需重新构建。

#### 1. 创建开发版 docker-compose

创建 `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  opencv-platform-dev:
    build:
      context: .
      dockerfile: Dockerfile.prod
    image: opencv-platform:latest
    container_name: opencv-platform-dev
    ports:
      - "8000:8000"
    
    # 🔥 关键：挂载代码目录
    volumes:
      - ./backend:/app/backend           # 挂载后端代码
      - ./frontend:/app/frontend         # 挂载前端代码
      - ./config:/app/config             # 挂载配置
      - ./app.py:/app/app.py             # 挂载主程序
      - ./data:/app/data                 # 数据目录
      - ./logs:/app/logs                 # 日志目录
      - ./.env:/app/.env:ro              # 环境变量
    
    environment:
      - DEBUG=True                        # 开发模式
      - PYTHONUNBUFFERED=1
      - RELOAD=True                       # 启用热重载
    
    # 🔥 使用热重载命令
    command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    
    networks:
      - opencv-network
    
    restart: unless-stopped

networks:
  opencv-network:
    driver: bridge
```

#### 2. 使用方法

```bash
# 首次构建镜像（只需一次）
docker-compose -f docker-compose.dev.yml build

# 启动开发容器
docker-compose -f docker-compose.dev.yml up

# 修改代码后，容器会自动重载，无需重新构建！
```

**优势**：
- ✅ 代码修改立即生效（1-2 秒热重载）
- ✅ 无需重新构建镜像
- ✅ 支持断点调试
- ✅ 适合开发调试

### 方案三：多阶段构建 + 基础镜像

**原理**: 将依赖打包成基础镜像，应用代码使用基础镜像构建。

#### 1. 创建基础镜像 Dockerfile

`Dockerfile.base`:

```dockerfile
FROM python:3.12-slim-bookworm

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
```

#### 2. 应用 Dockerfile

`Dockerfile.app`:

```dockerfile
FROM opencv-platform-base:latest

# 只复制应用代码
COPY . /app

# 设置权限
RUN chmod -R 755 /app

EXPOSE 8000
CMD ["python3", "app.py"]
```

#### 3. 构建流程

```bash
# 1. 首次构建基础镜像（只需一次）
docker build -f Dockerfile.base -t opencv-platform-base:latest .

# 2. 构建应用镜像（非常快）
docker build -f Dockerfile.app -t opencv-platform:latest .

# 3. 更新代码后只需重新构建应用镜像
docker build -f Dockerfile.app -t opencv-platform:latest .
```

**优势**：
- ✅ 基础镜像只需构建一次
- ✅ 应用镜像构建非常快（~10-20 秒）
- ✅ 适合 CI/CD 流程

### 方案四：使用 BuildKit 缓存挂载

**原理**: Docker BuildKit 提供高级缓存功能。

#### 1. 优化的 Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.12-slim-bookworm

# 使用 BuildKit 缓存挂载
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install -r /tmp/requirements.txt
```

#### 2. 启用 BuildKit

```bash
# 设置环境变量
export DOCKER_BUILDKIT=1

# 或在 docker-compose 中
DOCKER_BUILDKIT=1 docker-compose build
```

### 方案五：.dockerignore 优化

**原理**: 排除不必要的文件，减少构建上下文大小。

#### 当前 .dockerignore 已优化

```
# 已排除的内容
__pycache__/
*.pyc
.git/
.vscode/
*.log
data/datasets/*
data/models/*
```

**建议添加**：

```
# 开发文件
*.md
!README.md
docs/
tests/
.pytest_cache/

# 临时文件
*.tmp
*.cache
tmp/

# IDE 文件
.idea/
*.swp
```

## 📊 性能对比

| 方案 | 首次构建 | 代码更新后 | 开发体验 | 适用场景 |
|------|---------|-----------|----------|---------|
| 优化分层（方案一） | 5-10 分钟 | 30-60 秒 | ⭐⭐⭐ | 生产部署 |
| 开发模式挂载（方案二） | 5-10 分钟 | 1-2 秒（热重载） | ⭐⭐⭐⭐⭐ | 本地开发 |
| 多阶段构建（方案三） | 5-10 分钟 | 10-20 秒 | ⭐⭐⭐⭐ | CI/CD |
| BuildKit 缓存（方案四） | 5-10 分钟 | 20-40 秒 | ⭐⭐⭐⭐ | 高级用户 |
| .dockerignore（方案五） | 3-8 分钟 | 减少 20-30% | ⭐⭐⭐ | 辅助优化 |

## 🚀 推荐使用组合

### 开发阶段（推荐）

```bash
# 使用方案二：开发模式
docker-compose -f docker-compose.dev.yml up
```

**优势**：
- 代码修改立即生效
- 无需重新构建
- 最佳开发体验

### 生产部署

```bash
# 使用方案一：优化的 Dockerfile.prod
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

**优势**：
- 镜像大小优化
- 分层缓存加速
- 适合生产环境

## 🛠️ 实际操作示例

### 场景一：日常开发

```bash
# 1. 首次设置（只需一次）
docker-compose -f docker-compose.dev.yml build

# 2. 启动开发环境
docker-compose -f docker-compose.dev.yml up

# 3. 修改代码（backend/api/routes.py）
# 保存后，容器自动重载（1-2 秒）

# 4. 修改依赖（requirements.txt）
# 需要重新构建
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up
```

### 场景二：测试部署

```bash
# 使用优化的生产 Dockerfile
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 场景三：快速迭代

```bash
# 方法 1：使用开发模式（推荐）
docker-compose -f docker-compose.dev.yml up

# 方法 2：使用生产模式 + 缓存
docker-compose -f docker-compose.prod.yml build  # 利用缓存
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 最佳实践建议

### 1. 开发阶段
- ✅ 使用 `docker-compose.dev.yml` 开发模式
- ✅ 挂载代码目录，启用热重载
- ✅ 定期清理 Docker 缓存

### 2. 测试/预发布
- ✅ 使用优化的 `Dockerfile.prod`
- ✅ 利用分层缓存
- ✅ 运行完整测试套件

### 3. 生产部署
- ✅ 使用多阶段构建
- ✅ 固定依赖版本
- ✅ 使用健康检查

### 4. CI/CD 流程
- ✅ 使用基础镜像方案
- ✅ 启用 BuildKit
- ✅ 缓存 pip 包

## 🔍 故障排查

### 问题 1: 缓存未生效

```bash
# 清理所有缓存，重新构建
docker system prune -af
docker-compose -f docker-compose.prod.yml build --no-cache
```

### 问题 2: 开发模式代码不更新

```bash
# 检查挂载是否正确
docker-compose -f docker-compose.dev.yml config

# 重启容器
docker-compose -f docker-compose.dev.yml restart
```

### 问题 3: 依赖冲突

```bash
# 使用虚拟环境测试依赖
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
```

## 📦 清理 Docker 资源

```bash
# 停止所有容器
docker-compose -f docker-compose.prod.yml down

# 清理未使用的镜像
docker image prune -a

# 清理所有资源（谨慎使用）
docker system prune -af --volumes
```

## 🎯 总结

### 最快的开发流程（推荐）

1. **首次设置**：
```bash
docker-compose -f docker-compose.dev.yml build
```

2. **日常开发**：
```bash
docker-compose -f docker-compose.dev.yml up
# 修改代码，自动重载（1-2 秒）
```

3. **依赖更新时**：
```bash
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up
```

### 生产部署（已优化）

```bash
# 利用分层缓存，30-60 秒完成代码更新
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

**关键文件**：
- `Dockerfile.prod` - 已优化的生产 Dockerfile
- `docker-compose.dev.yml` - 开发模式配置（需要创建）
- `.dockerignore` - 排除不必要的文件

**下一步**：
1. 创建 `docker-compose.dev.yml`（见方案二）
2. 使用开发模式进行日常开发
3. 生产部署时使用已优化的 `docker-compose.prod.yml`
