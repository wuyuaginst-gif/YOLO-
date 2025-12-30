# OpenCV Platform 更新指南

## 🔄 问题说明

您的本地 Docker 部署遇到两个问题：
1. ❌ **公司 Logo 不显示**
2. ❌ **模型选择列表还是 YOLOv8，没有 YOLO11 选项**

## ✅ 原因分析

这两个问题的根本原因是：**本地 Docker 镜像是旧版本**

代码库已经更新（包含以下改进）：
- ✅ 所有页面已更新到 YOLO11
- ✅ Dockerfile.prod 已优化静态文件处理
- ✅ 新增 7 个 Ultralytics Solutions
- ✅ Logo 显示问题已修复

但是您的 Docker 容器还在使用旧的镜像缓存。

## 🚀 完整解决方案（推荐）

### 步骤 1: 拉取最新代码

```bash
# 进入项目目录
cd /path/to/your/webapp

# 拉取最新代码
git pull origin main

# 验证更新
git log --oneline -5
```

**预期看到的最新提交**：
```
1ed03f5 fix: 修复 Docker 部署中 Logo 不显示的问题
2044141 test: 添加 Solutions 综合测试和测试报告
15c4658 docs: 添加 Solutions 功能集成总结文档
4bd12c6 feat: 集成 Ultralytics Solutions - 添加 7 种智能解决方案
```

### 步骤 2: 使用自动修复脚本（推荐）⭐

```bash
# 运行一键修复脚本
./fix-logo.sh
```

这个脚本会自动：
- ✅ 停止旧容器
- ✅ 清理 Docker 缓存
- ✅ 重新构建镜像（使用最新代码）
- ✅ 验证文件是否存在
- ✅ 测试静态文件访问
- ✅ 启动新容器

### 步骤 3: 验证更新

打开浏览器访问：`http://localhost:8000`

检查以下内容：
- ✅ Logo 是否显示在左上角
- ✅ 点击"模型推理"，模型选择列表应该有 YOLO11n/s/m/l/x
- ✅ 访问 Solutions 页面，查看 7 个新功能

---

## 📋 手动更新步骤（详细版）

如果自动脚本不可用，请按以下步骤手动更新：

### 1. 拉取最新代码

```bash
cd /path/to/your/webapp
git pull origin main
```

### 2. 停止现有容器

```bash
docker-compose -f docker-compose.prod.yml down
```

### 3. 清理 Docker 缓存

```bash
# 清理所有未使用的镜像和容器
docker system prune -af

# 或者只删除项目镜像
docker rmi opencv-platform:latest
```

### 4. 重新构建镜像（不使用缓存）

```bash
docker-compose -f docker-compose.prod.yml build --no-cache
```

**⏰ 预计时间**: 5-10 分钟（取决于网络速度）

### 5. 启动新容器

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 6. 查看日志

```bash
docker-compose -f docker-compose.prod.yml logs -f
```

按 `Ctrl+C` 退出日志查看

### 7. 验证文件

```bash
# 检查容器内 Logo 文件
docker exec opencv-platform-prod ls -lh /app/frontend/static/company-logo.png

# 检查模型选择页面
docker exec opencv-platform-prod cat /app/frontend/inference.html | grep -A5 "model-select"
```

---

## 🔍 验证清单

完成更新后，请逐项检查：

### ✅ Logo 显示

- [ ] 主页左上角显示公司 Logo
- [ ] 所有页面导航栏都显示 Logo
- [ ] Logo 图片加载正常（无 404 错误）

**测试方法**：
```bash
# 浏览器访问
http://localhost:8000/static/company-logo.png

# 或命令行测试
curl -I http://localhost:8000/static/company-logo.png
# 应该返回: HTTP/1.1 200 OK
```

### ✅ YOLO11 模型选项

访问：http://localhost:8000/inference

模型选择下拉列表应该包含：
- [ ] ⭐ YOLO11n (nano) - 默认选中
- [ ] YOLO11s (small)
- [ ] YOLO11m (medium)
- [ ] YOLO11l (large)
- [ ] YOLO11x (extra large)
- [ ] ─────────────
- [ ] YOLOv8n (nano)
- [ ] YOLOv8s (small)
- [ ] ...

### ✅ 训练页面

访问：http://localhost:8000/training

模型类型选择应该包含：
- [ ] YOLO11n (nano) ⭐ - 默认选中
- [ ] YOLO11s (small)
- [ ] ...

### ✅ Solutions 功能

访问：http://localhost:8000/solutions

应该看到：
- [ ] 7 个 Solutions 卡片
- [ ] 对象计数 📊
- [ ] 热图生成 🔥
- [ ] 速度估算 🚗
- [ ] 距离计算 📏
- [ ] 对象模糊 🔒
- [ ] 对象裁剪 ✂️
- [ ] 队列管理 👥

---

## 🛠️ 常见问题

### Q1: 执行 git pull 时提示冲突

**解决方法**：
```bash
# 保存本地修改
git stash

# 拉取最新代码
git pull origin main

# 如需要，恢复本地修改
git stash pop
```

### Q2: Docker 构建很慢

**原因**：需要下载 PyTorch 和依赖包

**解决方法**：
```bash
# 使用国内镜像加速
# 编辑 Dockerfile.prod，在 pip install 前添加：
# RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 构建后仍然看不到 YOLO11

**检查步骤**：
```bash
# 1. 确认代码已更新
git log --oneline -1

# 2. 确认使用了 --no-cache
docker-compose -f docker-compose.prod.yml build --no-cache

# 3. 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete, 选择"缓存的图片和文件"

# 4. 硬刷新页面
# Chrome: Ctrl+F5
# Firefox: Ctrl+Shift+R
```

### Q4: Logo 还是不显示

**执行诊断**：
```bash
# 运行诊断脚本
./fix-logo.sh

# 或手动检查
docker exec opencv-platform-prod ls -la /app/frontend/static/
docker exec opencv-platform-prod cat /app/app.py | grep -A5 "static"
```

---

## 📊 更新前后对比

### 模型选择列表

| 项目 | 更新前 | 更新后 |
|------|--------|--------|
| **默认模型** | YOLOv8n | YOLO11n ⭐ |
| **可选模型** | YOLOv8 系列 (5个) | YOLO11 (5个) + YOLOv8 (5个) |
| **分隔线** | ❌ 无 | ✅ 有 |
| **标记** | ❌ 无 | ✅ ⭐ 推荐 |

### 功能数量

| 功能类别 | 更新前 | 更新后 |
|---------|--------|--------|
| **基础功能** | 4 个 | 4 个 |
| **Solutions** | 0 个 | 7 个 ✨ |
| **总计** | 4 个 | 11 个 (+175%) |

---

## 🎯 快速命令参考

```bash
# 完整更新流程（一键执行）
git pull origin main && ./fix-logo.sh

# 或分步执行
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker system prune -af
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 验证更新
docker exec opencv-platform-prod ls -lh /app/frontend/static/company-logo.png
curl -I http://localhost:8000/static/company-logo.png

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 📞 获取帮助

如果更新后仍有问题，请提供以下信息：

```bash
# 1. Git 版本
git log --oneline -5

# 2. Docker 镜像
docker images | grep opencv-platform

# 3. 容器状态
docker-compose -f docker-compose.prod.yml ps

# 4. 容器内文件
docker exec opencv-platform-prod ls -la /app/frontend/

# 5. 应用日志
docker logs opencv-platform-prod | tail -50
```

---

## ✅ 完成确认

更新完成后，您应该看到：

1. ✅ **Logo 显示正常**
   - 所有页面左上角都有公司 Logo
   - Logo 图片清晰，无加载错误

2. ✅ **YOLO11 模型可用**
   - 推理页面默认选择 YOLO11n
   - 训练页面默认选择 YOLO11n
   - Solutions 页面使用 YOLO11

3. ✅ **新功能可用**
   - Solutions 页面显示 7 个解决方案
   - 所有 Solutions API 可正常调用

4. ✅ **性能正常**
   - 页面加载速度快
   - API 响应正常
   - 无错误日志

---

**更新日期**: 2025-12-30  
**版本**: v1.0.0 → v1.1.0  
**重要性**: 🔴 高（包含功能更新和 Bug 修复）
