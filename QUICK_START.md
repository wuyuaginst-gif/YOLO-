# ⚡ 快速开始 - OpenCV Platform

## 🚀 30秒部署（CentOS 7.5）

```bash
# 克隆项目
git clone https://github.com/wuyuaginst-gif/YOLO-.git
cd YOLO-/webapp

# 一键部署
chmod +x scripts/deploy-centos7.sh
./scripts/deploy-centos7.sh

# 测试验证
./scripts/test-deployment.sh
```

**访问**: `http://your-server-ip:8000`

---

## 📋 系统要求

| 项目 | 最低要求 | 推荐配置 |
|-----|---------|---------|
| OS | CentOS 7.5+ | CentOS 7.5+ |
| CPU | 4 核 | 8 核 |
| 内存 | 8GB | 16GB |
| 硬盘 | 50GB | 100GB |

---

## 🛠️ 主要功能

| 功能 | 说明 | 路径 |
|-----|------|------|
| 🎨 数据标注 | 本地化标注工具 | `/annotation` |
| 🚀 模型训练 | YOLO训练平台 | `/training` |
| 🔍 模型推理 | 图像检测推理 | `/inference` |
| 📦 模型管理 | 模型上传/导出 | `/models` |
| 📊 数据集管理 | 数据集管理 | `/datasets` |
| 📖 API文档 | 交互式文档 | `/api/docs` |

---

## 🎯 常用命令

```bash
# 查看状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志  
docker-compose -f docker-compose.prod.yml logs -f

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 停止服务
docker-compose -f docker-compose.prod.yml down
```

---

## 📚 详细文档

- 📘 [完整部署指南](DEPLOY_CENTOS7.md)
- 📗 [Docker部署文档](DOCKER_README.md)
- 📙 [部署检查清单](DEPLOYMENT_CHECKLIST.md)
- 📕 [项目README](README.md)

---

## 🆘 遇到问题？

1. 查看日志: `docker-compose -f docker-compose.prod.yml logs -f`
2. 运行测试: `./scripts/test-deployment.sh`
3. 查看文档: [DEPLOY_CENTOS7.md](DEPLOY_CENTOS7.md)
4. 提交Issue: https://github.com/wuyuaginst-gif/YOLO-/issues

---

**开始您的AI视觉之旅！** 🎉
