#!/bin/bash
# 诊断 500 错误的真实原因

echo "=========================================="
echo "推理接口 500 错误深度诊断"
echo "=========================================="
echo ""

echo "1. 检查容器日志（最近 50 行）："
echo "----------------------------------------"
docker logs opencv-platform-dev --tail 50
echo ""

echo "=========================================="
echo "2. 测试容器内 YOLO 服务："
echo "----------------------------------------"
docker exec opencv-platform-dev python3 -c "
import sys
sys.path.insert(0, '/app')

try:
    print('✅ 导入 ultralytics...')
    from ultralytics import YOLO
    
    print('✅ 导入 YOLO 服务...')
    from backend.services.yolo_service import yolo_service, ULTRALYTICS_AVAILABLE
    
    print(f'✅ ULTRALYTICS_AVAILABLE: {ULTRALYTICS_AVAILABLE}')
    print(f'✅ yolo_service is None: {yolo_service is None}')
    
    if yolo_service:
        print('✅ YOLO 服务已初始化')
        
        # 尝试加载模型
        print('✅ 尝试加载默认模型...')
        try:
            model = yolo_service.load_model('yolo11n.pt')
            print(f'✅ 模型加载成功: {model.task}')
        except Exception as e:
            print(f'❌ 模型加载失败: {e}')
    else:
        print('❌ YOLO 服务未初始化')
        
except Exception as e:
    import traceback
    print(f'❌ 错误: {e}')
    traceback.print_exc()
"

echo ""
echo "=========================================="
echo "3. 检查数据目录权限："
echo "----------------------------------------"
docker exec opencv-platform-dev ls -la /app/data/
docker exec opencv-platform-dev ls -la /app/data/models/
docker exec opencv-platform-dev ls -la /app/data/uploads/

echo ""
echo "=========================================="
echo "4. 检查健康检查状态："
echo "----------------------------------------"
docker inspect opencv-platform-dev | grep -A 10 "Health"

echo ""
echo "=========================================="
echo "5. 测试推理接口（使用测试图片）："
echo "----------------------------------------"
echo "创建测试图片..."
docker exec opencv-platform-dev python3 -c "
import numpy as np
from PIL import Image
img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
Image.fromarray(img).save('/app/data/uploads/test.jpg')
print('✅ 测试图片已创建: /app/data/uploads/test.jpg')
"

echo ""
echo "测试推理功能..."
docker exec opencv-platform-dev python3 -c "
import sys
sys.path.insert(0, '/app')

try:
    from backend.services.yolo_service import yolo_service
    
    result = yolo_service.infer(
        image_path='/app/data/uploads/test.jpg',
        model_name='yolo11n.pt',
        confidence=0.25
    )
    
    print(f'Success: {result.success}')
    print(f'Message: {result.message}')
    print(f'Detections: {len(result.detections)}')
    print(f'Inference time: {result.inference_time:.4f}s')
    
except Exception as e:
    import traceback
    print(f'❌ 推理失败: {e}')
    traceback.print_exc()
"

echo ""
echo "=========================================="
echo "6. 检查 API 路由是否正常："
echo "----------------------------------------"
docker exec opencv-platform-dev python3 -c "
import sys
sys.path.insert(0, '/app')

try:
    from backend.api.routes import router
    print(f'✅ API 路由加载成功')
    print(f'✅ 路由数量: {len(router.routes)}')
    
    # 列出所有路由
    for route in router.routes:
        if hasattr(route, 'path'):
            print(f'  - {route.methods} {route.path}')
    
except Exception as e:
    import traceback
    print(f'❌ 路由加载失败: {e}')
    traceback.print_exc()
"

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
