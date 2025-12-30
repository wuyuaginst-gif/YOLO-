# 🐳 Docker构建指南

## 常见构建问题与解决方案

### 问题1: `libgthread-2.0-0` 包不存在

**错误信息**:
```
E: Unable to locate package libgthread-2.0-0
E: Couldn't find any package by glob 'libgthread-2.0-0'
```

**原因**: 
在 Debian Bookworm (Python 3.12 基础镜像) 中，`libgthread-2.0-0` 已被合并到 `libglib2.0-0` 包中。

**解决方案**:
已在最新的 `Dockerfile.prod` 中移除此依赖。

---

### 问题2: 构建时间过长

**现象**: Docker镜像构建超过10分钟

**原因**:
1. PyTorch下载较大（~200MB）
2. 安装Ultralytics和其他依赖
3. 网络速度慢

**解决方案**:

#### 方案1: 使用国内镜像源（推荐）

创建或编辑 `/etc/docker/daemon.json`:

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

重启Docker:
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

#### 方案2: 使用构建缓存

```bash
# 首次构建（不使用缓存）
docker compose -f docker-compose.prod.yml build --no-cache

# 后续构建（使用缓存，更快）
docker compose -f docker-compose.prod.yml build
```

#### 方案3: 分阶段验证

使用测试镜像验证系统依赖：

```bash
# 构建测试镜像（只包含系统依赖，更快）
docker build -f Dockerfile.test -t opencv-test:latest .

# 验证测试镜像
docker run --rm opencv-test:latest
```

---

### 问题3: Docker Compose命令不存在

**错误信息**:
```
bash: docker-compose: 未找到命令
```

**原因**:
Docker Compose有两种安装方式：
- **V2 (插件)**: `docker compose` (推荐)
- **V1 (独立)**: `docker-compose`

**解决方案**:

检查安装方式：
```bash
# 检查 V2 插件
docker compose version

# 检查 V1 独立版本
docker-compose --version
```

如果都不存在，安装 Docker Compose：

```bash
# 安装 V2 插件（推荐）
sudo yum install -y docker-compose-plugin

# 或安装 V1 独立版本
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

我们的脚本已自动检测并使用正确的命令。

---

### 问题4: 权限错误

**错误信息**:
```
permission denied while trying to connect to the Docker daemon socket
```

**解决方案**:

```bash
# 添加当前用户到docker组
sudo usermod -aG docker $USER

# 注销并重新登录，或运行：
newgrp docker

# 验证
docker ps
```

---

### 问题5: 磁盘空间不足

**错误信息**:
```
no space left on device
```

**解决方案**:

```bash
# 检查磁盘空间
df -h

# 清理 Docker 资源
docker system prune -a --volumes

# 查看 Docker 占用空间
docker system df
```

---

## 📋 推荐构建流程

### 快速构建（使用缓存）

```bash
# 1. 进入项目目录
cd /path/to/YOLO-/webapp

# 2. 确保有.env文件
cp .env.example .env

# 3. 构建镜像（使用缓存，约5-10分钟）
docker compose -f docker-compose.prod.yml build

# 4. 启动服务
docker compose -f docker-compose.prod.yml up -d

# 5. 查看日志
docker compose -f docker-compose.prod.yml logs -f
```

### 完全重建（无缓存）

```bash
# 清理旧镜像
docker compose -f docker-compose.prod.yml down --rmi all

# 清理构建缓存
docker builder prune -a

# 重新构建（约15-25分钟）
docker compose -f docker-compose.prod.yml build --no-cache

# 启动服务
docker compose -f docker-compose.prod.yml up -d
```

### 自动化部署（推荐）

```bash
# 使用一键部署脚本
chmod +x scripts/deploy-centos7.sh
./scripts/deploy-centos7.sh
```

脚本会自动处理：
- ✅ Docker安装检测
- ✅ Docker Compose安装检测
- ✅ 环境配置
- ✅ 镜像构建
- ✅ 服务启动
- ✅ 健康检查

---

## 🔍 构建验证

### 验证镜像是否成功构建

```bash
# 查看镜像
docker images | grep opencv-platform

# 应该看到类似输出：
# opencv-platform   latest   abc123def456   2 minutes ago   2.1GB
```

### 验证容器是否正常运行

```bash
# 查看容器状态
docker compose -f docker-compose.prod.yml ps

# 应该看到状态为 "Up"
```

### 验证服务是否响应

```bash
# 健康检查
curl http://localhost:8000/api/v1/system/health

# 系统信息
curl http://localhost:8000/api/v1/system/info

# 或运行测试脚本
./scripts/test-deployment.sh
```

---

## ⚙️ 高级配置

### 自定义镜像构建参数

```bash
# 指定构建参数
docker compose -f docker-compose.prod.yml build \
    --build-arg HTTP_PROXY=http://proxy:8080 \
    --build-arg HTTPS_PROXY=http://proxy:8080

# 并行构建（如果有多个服务）
docker compose -f docker-compose.prod.yml build --parallel
```

### 构建特定服务

```bash
# 只构建主服务
docker compose -f docker-compose.prod.yml build opencv-platform
```

### 查看构建日志

```bash
# 实时查看构建输出
docker compose -f docker-compose.prod.yml build --progress=plain

# 保存构建日志
docker compose -f docker-compose.prod.yml build --no-cache 2>&1 | tee build.log
```

---

## 📊 构建时间参考

| 场景 | 预计时间 | 网络要求 |
|------|---------|----------|
| 首次构建（无缓存） | 15-25分钟 | 良好 |
| 使用缓存构建 | 5-10分钟 | 一般 |
| 测试镜像构建 | 2-5分钟 | 良好 |
| 代码更新重建 | 3-8分钟 | 一般 |

---

## 🚨 紧急问题排查

### 构建卡住不动

1. 检查网络连接
2. 使用 `Ctrl+C` 中断
3. 清理缓存：`docker builder prune -a`
4. 重新构建

### 构建失败

1. 查看详细错误信息
2. 检查磁盘空间：`df -h`
3. 检查Docker服务：`sudo systemctl status docker`
4. 清理Docker：`docker system prune -a`
5. 参考本文档对应问题的解决方案

### 获取帮助

1. 查看构建日志
2. 检查 GitHub Issues
3. 提交新的 Issue 并附上：
   - 错误信息
   - `docker version` 输出
   - `docker compose version` 输出
   - 操作系统信息

---

## 📚 相关文档

- [部署指南](DEPLOY_CENTOS7.md)
- [Docker部署文档](DOCKER_README.md)
- [快速开始](QUICK_START.md)

---

**构建愉快！** 🎉
