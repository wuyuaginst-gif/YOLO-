#!/bin/bash
# 测试推理 API 接口

echo "=========================================="
echo "推理 API 测试脚本"
echo "=========================================="
echo ""

# 检查容器是否运行
if ! docker ps | grep -q opencv-platform-dev; then
    echo "❌ 容器 opencv-platform-dev 未运行"
    echo "请先启动容器: docker compose -f docker-compose.dev.yml up -d"
    exit 1
fi

echo "✅ 容器正在运行"
echo ""

# 创建测试图片
echo "1. 创建测试图片..."
docker exec opencv-platform-dev python3 << 'PYTHON'
import numpy as np
from PIL import Image
import os

# 创建测试图片
img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
test_img_path = '/app/data/uploads/test_inference.jpg'
Image.fromarray(img).save(test_img_path)
print(f"✅ 测试图片已创建: {test_img_path}")

# 验证文件存在
if os.path.exists(test_img_path):
    size = os.path.getsize(test_img_path)
    print(f"✅ 文件大小: {size} bytes")
else:
    print(f"❌ 文件不存在: {test_img_path}")
PYTHON

echo ""
echo "2. 直接测试 YOLO 服务（容器内）..."
docker exec opencv-platform-dev python3 << 'PYTHON'
import sys
sys.path.insert(0, '/app')

try:
    from backend.services.yolo_service import yolo_service
    
    if not yolo_service:
        print("❌ YOLO 服务未初始化")
        sys.exit(1)
    
    print("✅ YOLO 服务已初始化")
    
    # 执行推理
    print("执行推理...")
    result = yolo_service.infer(
        image_path='/app/data/uploads/test_inference.jpg',
        model_name='yolo11n.pt',
        confidence=0.25
    )
    
    if result.success:
        print(f"✅ 推理成功")
        print(f"   检测到 {len(result.detections)} 个对象")
        print(f"   推理时间: {result.inference_time:.4f}秒")
        
        if result.detections:
            print("   检测结果:")
            for i, det in enumerate(result.detections[:5], 1):
                print(f"     {i}. {det.class_name} (置信度: {det.confidence:.2f})")
    else:
        print(f"❌ 推理失败: {result.message}")
        sys.exit(1)
        
except Exception as e:
    import traceback
    print(f"❌ 错误: {e}")
    traceback.print_exc()
    sys.exit(1)
PYTHON

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ YOLO 服务测试失败，停止测试"
    exit 1
fi

echo ""
echo "3. 测试 HTTP API 接口..."

# 获取容器的 IP 或使用 localhost
API_URL="http://localhost:8000/api/v1/inference/image"

echo "   API URL: $API_URL"
echo ""

# 从容器中复制测试图片到本地（如果需要）
# 或使用 curl 直接从容器内部测试

echo "   方式 A: 从容器内部测试 API"
docker exec opencv-platform-dev python3 << 'PYTHON'
import requests
import os

try:
    # 测试健康检查接口
    print("测试健康检查接口...")
    health_response = requests.get('http://localhost:8000/api/v1/system/health')
    print(f"健康检查: {health_response.status_code} - {health_response.text}")
    print()
    
    # 测试推理接口
    print("测试推理接口...")
    test_img_path = '/app/data/uploads/test_inference.jpg'
    
    if not os.path.exists(test_img_path):
        print(f"❌ 测试图片不存在: {test_img_path}")
        exit(1)
    
    with open(test_img_path, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        data = {
            'model_name': 'yolo11n.pt',
            'confidence': '0.25'
        }
        
        response = requests.post(
            'http://localhost:8000/api/v1/inference/image',
            files=files,
            data=data,
            timeout=30
        )
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API 调用成功！")
        print(f"成功: {result.get('success')}")
        print(f"消息: {result.get('message')}")
        print(f"检测数量: {len(result.get('detections', []))}")
        print(f"推理时间: {result.get('inference_time')}秒")
    else:
        print(f"❌ API 调用失败")
        print(f"响应内容: {response.text}")
        
except Exception as e:
    import traceback
    print(f"❌ 请求失败: {e}")
    traceback.print_exc()
PYTHON

echo ""
echo "=========================================="
echo "   方式 B: 使用 curl 测试（如果有真实图片）"
echo "=========================================="
echo ""
echo "如果你有真实图片，可以在宿主机运行："
echo ""
echo "curl -X POST \"http://localhost:8000/api/v1/inference/image\" \\"
echo "  -F \"file=@your_image.jpg\" \\"
echo "  -F \"model_name=yolo11n.pt\" \\"
echo "  -F \"confidence=0.25\""
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
