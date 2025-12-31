# 🔍 文件上传问题排查指南

## 问题描述
前端显示"✓ 已选择: AI.png"，但容器内 `/app/data/uploads/` 目录看不到文件。

## 🎯 可能原因

### 1️⃣ 文件还未上传到服务器
**最可能的原因！**

前端代码显示"已选择"只是表示**浏览器本地选择了文件**，但：
- ❌ **文件还没有发送到服务器**
- ❌ **还没有调用 API**
- ❌ **只有点击"开始推理"按钮才会上传文件**

**验证方法：**
```bash
# 查看前端代码 inference.html 第 155-182 行
# 文件上传发生在点击"开始推理"按钮时
inferBtn.addEventListener('click', async () => {
    // ... 这里才会调用 API.inferImage(currentFile, options)
})
```

**流程：**
```
1. 选择文件 → 前端显示 "✓ 已选择: AI.png" → 文件在浏览器内存中
2. 点击"开始推理" → 调用 API → 上传到服务器 → 保存到 uploads 目录
```

### 2️⃣ API 请求失败但没有显示错误
文件上传后立即被删除或保存失败。

### 3️⃣ 目录权限问题
容器内的用户没有写权限。

### 4️⃣ 文件保存到了错误的位置
可能保存到了容器内其他目录而不是挂载的 `data/uploads/`。

---

## ✅ 立即排查步骤

### 步骤 1：确认文件上传时机

**前端操作流程：**
```
1. ✓ 已选择: AI.png  ← 你现在在这里（文件还在浏览器中）
2. 点击"开始推理" ← 这一步才会上传文件到服务器
3. 文件保存到 /app/data/uploads/
4. 执行推理
5. 返回结果
```

**测试方法：**
1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签
3. 点击"开始推理"按钮
4. 查看 **POST /api/v1/inference/image** 请求
5. 检查：
   - Request Headers
   - Form Data（应该包含 file: AI.png）
   - Response（状态码和返回内容）

### 步骤 2：查看容器日志

```bash
# 实时查看日志
docker logs opencv-platform-dev -f

# 然后在前端点击"开始推理"
# 观察日志输出
```

**应该看到：**
```
INFO: 192.168.2.93:64787 - "POST /api/v1/inference/image HTTP/1.1" 200 OK
```

**如果看到 500：**
```
INFO: 192.168.2.93:64787 - "POST /api/v1/inference/image HTTP/1.1" 500 Internal Server Error
```

说明上传成功但推理失败，查看详细错误。

### 步骤 3：运行上传调试脚本

```bash
./debug_upload.sh
```

这会检查：
- uploads 目录状态和权限
- 文件写入测试
- API 文件保存流程测试
- 实时监控目录变化

### 步骤 4：检查目录权限

```bash
# 检查 uploads 目录权限
docker exec opencv-platform-dev ls -la /app/data/

# 应该看到：
# drwxrwxrwx 2 appuser appuser 4096 ... uploads
```

**如果权限不对，修复：**
```bash
docker exec -u root opencv-platform-dev chown -R appuser:appuser /app/data
docker exec -u root opencv-platform-dev chmod -R 777 /app/data/uploads
```

---

## 🔧 常见问题和解决方案

### 问题 1：点击"开始推理"后立即报错

**可能原因：**
- 模型下载失败
- 文件保存失败
- 推理服务异常

**解决方案：**
```bash
# 1. 先下载模型
docker exec opencv-platform-dev python3 -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"

# 2. 修复权限
docker exec -u root opencv-platform-dev chmod -R 777 /app/data

# 3. 重试
```

### 问题 2：文件上传成功但看不到

**可能原因：**
文件被保存后立即删除（推理完成后可能清理）。

**验证方法：**
```bash
# 监控文件变化
watch -n 1 'docker exec opencv-platform-dev ls -lh /app/data/uploads/'

# 然后点击"开始推理"
# 观察文件是否出现又消失
```

**检查代码：**
查看 `backend/api/routes.py` 第 99-116 行，文件保存后没有删除逻辑。

### 问题 3：文件名包含中文或特殊字符

**问题：**
`AI.png` 这个文件名没问题，但如果是中文文件名可能有编码问题。

**解决方案：**
后端已处理（`get_unique_filename` 函数会生成唯一文件名）。

---

## 📊 调试检查清单

在你的**本地环境**执行：

### ✓ 基础检查
```bash
# 1. 容器是否运行
docker ps | grep opencv-platform-dev

# 2. 查看日志
docker logs opencv-platform-dev --tail 50

# 3. 检查 uploads 目录
docker exec opencv-platform-dev ls -la /app/data/uploads/
```

### ✓ 权限检查
```bash
# 检查目录权限
docker exec opencv-platform-dev stat /app/data/uploads/

# 测试写入
docker exec opencv-platform-dev touch /app/data/uploads/test.txt
docker exec opencv-platform-dev rm /app/data/uploads/test.txt
```

### ✓ 前端检查
1. 打开浏览器开发者工具（F12）
2. Network 标签
3. 点击"开始推理"
4. 查看请求详情

### ✓ 运行诊断脚本
```bash
./debug_upload.sh
```

---

## 🎯 最可能的情况

根据你的描述"**已选择: AI.png**"：

### 90% 可能性：文件还没上传
- ✓ 文件已在浏览器中选择
- ❌ 但还没点击"开始推理"
- ❌ 文件还没发送到服务器

**解决方案：**
1. 点击"开始推理"按钮
2. 查看是否返回错误
3. 检查浏览器 Network 标签的请求

### 10% 可能性：上传失败或文件被删除
- ✓ 点击了"开始推理"
- ❌ API 请求失败（500 错误）
- ❌ 文件保存失败

**解决方案：**
1. 查看容器日志找到真实错误
2. 运行 `./debug_upload.sh`
3. 修复权限或模型问题

---

## 🚀 立即测试

### 方法 1：使用浏览器测试（推荐）

1. **打开浏览器开发者工具（F12）**
2. **切换到 Network 标签**
3. **在前端选择图片（你已经做了）**
4. **点击"开始推理"按钮**
5. **观察：**
   - 是否发送了 POST 请求
   - 请求状态码（200 或 500）
   - 响应内容（成功或错误信息）

### 方法 2：使用 curl 直接测试

```bash
# 创建测试图片
docker exec opencv-platform-dev python3 -c "
import numpy as np
from PIL import Image
img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
Image.fromarray(img).save('/tmp/test.jpg')
"

# 从容器内部测试 API
docker exec opencv-platform-dev curl -X POST \
  "http://localhost:8000/api/v1/inference/image" \
  -F "file=@/tmp/test.jpg" \
  -F "model_name=yolo11n.pt" \
  -F "confidence=0.25"
```

### 方法 3：运行完整测试

```bash
./test_api.sh
```

---

## 📞 下一步

**请提供以下信息：**

1. **点击"开始推理"后发生了什么？**
   - 有错误提示吗？
   - 浏览器 Console 有错误吗？
   - 按钮一直显示"推理中..."吗？

2. **浏览器 Network 标签显示什么？**
   - POST /api/v1/inference/image 请求的状态码
   - 响应内容

3. **容器日志显示什么？**
   ```bash
   docker logs opencv-platform-dev --tail 100
   ```

有了这些信息，我能立即找到问题所在！🎯
