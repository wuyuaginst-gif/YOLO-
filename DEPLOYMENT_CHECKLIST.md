# 🚀 OpenCV Platform - 部署检查清单

在 CentOS 7.5 服务器上部署前，请确保完成以下检查项。

## ✅ 部署前检查

### 1. 服务器环境

- [ ] 操作系统: CentOS 7.5 或以上
- [ ] CPU: 最少 4 核心（推荐 8 核心）
- [ ] 内存: 最少 8GB（推荐 16GB）
- [ ] 硬盘: 最少 50GB 可用空间
- [ ] 网络: 可以访问外网（用于下载镜像和依赖）

### 2. 权限检查

- [ ] 有 sudo 权限或 root 权限
- [ ] 可以执行 shell 脚本
- [ ] 可以安装软件包

### 3. 端口检查

```bash
# 检查 8000 端口是否被占用
netstat -tuln | grep 8000
# 或
ss -tuln | grep 8000
```

- [ ] 端口 8000 未被占用
- [ ] 防火墙允许 8000 端口访问

### 4. 网络检查

```bash
# 测试网络连接
ping -c 4 github.com
ping -c 4 pypi.org
```

- [ ] 可以访问 GitHub
- [ ] 可以访问 PyPI

## 📦 一键部署步骤

### 方式一：使用自动化脚本（推荐）

```bash
# 1. 克隆代码
git clone https://github.com/wuyuaginst-gif/YOLO-.git
cd YOLO-/webapp

# 2. 运行一键部署脚本
chmod +x scripts/deploy-centos7.sh
./scripts/deploy-centos7.sh
```

**脚本会自动完成：**
- ✅ 安装 Docker
- ✅ 安装 Docker Compose
- ✅ 配置防火墙
- ✅ 构建镜像（Python 3.12）
- ✅ 启动服务
- ✅ 健康检查

### 方式二：手动部署

参考 [DEPLOY_CENTOS7.md](DEPLOY_CENTOS7.md) 文档。

## 🧪 部署后验证

### 1. 运行测试脚本

```bash
./scripts/test-deployment.sh
```

测试项包括：
- [x] Docker 服务状态
- [x] 容器运行状态
- [x] 容器健康状态
- [x] 端口监听状态
- [x] 健康检查 API
- [x] 系统信息 API
- [x] Web UI 访问

### 2. 手动验证

```bash
# 检查容器状态
docker ps | grep opencv-platform-prod

# 检查健康状态
curl http://localhost:8000/api/v1/system/health

# 查看系统信息
curl http://localhost:8000/api/v1/system/info

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. 浏览器访问

- [ ] Web UI 可访问: `http://your-server-ip:8000`
- [ ] API 文档可访问: `http://your-server-ip:8000/api/docs`
- [ ] 数据标注页面可访问: `http://your-server-ip:8000/annotation`

### 4. 功能测试

- [ ] 可以创建标注项目
- [ ] 可以上传图片
- [ ] 可以进行标注
- [ ] 可以导出 YOLO 格式数据集

## 🔧 常见问题解决

### 问题 1: Docker 安装失败

```bash
# 检查系统版本
cat /etc/centos-release

# 手动添加 Docker 仓库
sudo yum-config-manager --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 重新安装
sudo yum install -y docker-ce docker-ce-cli containerd.io
```

### 问题 2: 端口被占用

```bash
# 查找占用进程
sudo netstat -tulpn | grep 8000

# 停止占用进程
sudo kill -9 <PID>

# 或修改端口（编辑 docker-compose.prod.yml）
ports:
  - "8888:8000"  # 改为其他端口
```

### 问题 3: 镜像构建失败

```bash
# 清理 Docker 缓存
docker system prune -a

# 使用国内镜像源
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}

# 重启 Docker
sudo systemctl restart docker

# 重新构建
docker-compose -f docker-compose.prod.yml build --no-cache
```

### 问题 4: 容器启动失败

```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs opencv-platform

# 检查配置文件
cat .env

# 进入容器调试
docker exec -it opencv-platform-prod /bin/bash
```

### 问题 5: 内存不足

```bash
# 检查内存使用
free -h

# 降低资源限制（编辑 docker-compose.prod.yml）
deploy:
  resources:
    limits:
      memory: 4G  # 从 8G 降低到 4G
```

## 📊 性能基准

部署成功后，预期性能指标：

- **启动时间**: < 60 秒
- **内存占用**: 2-4 GB
- **CPU 占用**: 10-30%（空闲时）
- **响应时间**: < 100ms（API 请求）

## 🔒 安全检查

- [ ] 修改默认端口（可选）
- [ ] 配置防火墙规则
- [ ] 限制访问 IP（可选）
- [ ] 定期更新系统和 Docker
- [ ] 定期备份数据目录

## 📝 部署记录

**部署日期**: _______________

**服务器信息**:
- IP 地址: _______________
- 操作系统: _______________
- Docker 版本: _______________
- Docker Compose 版本: _______________

**部署结果**:
- [ ] 成功
- [ ] 失败（原因: _______________）

**访问地址**:
- Web UI: http://_______________:8000
- API Docs: http://_______________:8000/api/docs

**备注**: 
_______________________________________________
_______________________________________________
_______________________________________________

---

## 📞 技术支持

如有问题，请：

1. 查看文档: [DEPLOY_CENTOS7.md](DEPLOY_CENTOS7.md)
2. 查看日志: `docker-compose -f docker-compose.prod.yml logs -f`
3. 提交 Issue: https://github.com/wuyuaginst-gif/YOLO-/issues

---

**准备好了吗？开始部署吧！** 🚀
