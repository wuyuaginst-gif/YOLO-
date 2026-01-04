#!/usr/bin/env python3
"""
使用训练好的 YOLO11 模型进行推理测试
"""

import sys
import time
from pathlib import Path
from PIL import Image
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from ultralytics import YOLO


def find_trained_model():
    """查找最新训练的模型"""
    models_dir = Path("data/models")
    
    # 查找所有训练项目
    trained_projects = sorted(
        models_dir.glob("yolo11_coco8_*/train/weights/best.pt"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    if not trained_projects:
        print("❌ 未找到训练好的模型！请先运行 test_yolo11_training.py")
        return None
    
    return str(trained_projects[0])


def test_inference_on_coco8():
    """使用 COCO8 验证集图片进行推理测试"""
    print("\n" + "=" * 80)
    print("  YOLO11 训练模型推理测试")
    print("=" * 80 + "\n")
    
    # 查找训练好的模型
    model_path = find_trained_model()
    if not model_path:
        return
    
    print(f"✓ 找到训练模型: {model_path}")
    print(f"  模型大小: {Path(model_path).stat().st_size / 1024 / 1024:.2f} MB\n")
    
    # 加载模型
    print("正在加载模型...")
    start_time = time.time()
    model = YOLO(model_path)
    load_time = time.time() - start_time
    
    print(f"✓ 模型加载成功！(耗时 {load_time:.2f}s)")
    print(f"  - 任务类型: {model.task}")
    print(f"  - 类别数量: {len(model.names)}")
    print()
    
    # 查找 COCO8 验证集图片
    coco8_val_dir = Path("datasets/coco8/images/val")
    if not coco8_val_dir.exists():
        print("❌ COCO8 验证集不存在！")
        return
    
    # 获取所有验证图片
    val_images = list(coco8_val_dir.glob("*.jpg"))
    print(f"找到 {len(val_images)} 张验证图片\n")
    
    # 创建输出目录
    output_dir = Path("data/inference_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 对每张图片进行推理
    total_detections = 0
    total_inference_time = 0
    
    print("开始推理...")
    print("-" * 80)
    
    for i, img_path in enumerate(val_images, 1):
        print(f"\n[{i}/{len(val_images)}] 图片: {img_path.name}")
        
        # 推理
        start_time = time.time()
        results = model.predict(
            source=str(img_path),
            conf=0.25,
            iou=0.45,
            save=False,
            verbose=False
        )
        inference_time = time.time() - start_time
        total_inference_time += inference_time
        
        # 解析结果
        result = results[0]
        boxes = result.boxes
        num_detections = len(boxes)
        total_detections += num_detections
        
        print(f"  ⏱️  推理时间: {inference_time*1000:.1f}ms")
        print(f"  🎯 检测数量: {num_detections}")
        
        if num_detections > 0:
            # 显示每个检测
            for j, box in enumerate(boxes):
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                cls_name = model.names[cls_id]
                xyxy = box.xyxy[0].tolist()
                
                print(f"    [{j+1}] {cls_name} - 置信度: {conf:.3f} - BBox: {[int(x) for x in xyxy]}")
            
            # 保存可视化结果
            output_path = output_dir / f"result_{img_path.name}"
            result.save(filename=str(output_path))
            print(f"  💾 保存结果: {output_path}")
        else:
            print(f"  ℹ️  未检测到任何对象")
    
    # 统计信息
    print("\n" + "=" * 80)
    print("  推理统计")
    print("=" * 80)
    print(f"  总图片数: {len(val_images)}")
    print(f"  总检测数: {total_detections}")
    print(f"  平均每张图片检测数: {total_detections / len(val_images):.1f}")
    print(f"  平均推理时间: {total_inference_time / len(val_images) * 1000:.1f}ms")
    print(f"  总推理时间: {total_inference_time:.2f}s")
    print(f"\n✓ 结果已保存到: {output_dir}/")
    print("=" * 80 + "\n")


def test_inference_with_api():
    """测试通过项目 API 进行推理"""
    print("\n" + "=" * 80)
    print("  通过项目 API 测试推理")
    print("=" * 80 + "\n")
    
    try:
        from backend.services.yolo_service import yolo_service
        from config.config import settings
        
        # 查找训练好的模型
        model_path = find_trained_model()
        if not model_path:
            return
        
        # 复制模型到 models 目录
        import shutil
        dest_path = settings.MODELS_DIR / "yolo11_coco8_trained.pt"
        shutil.copy(model_path, dest_path)
        print(f"✓ 模型已复制到: {dest_path}\n")
        
        # 使用项目的 YOLO 服务进行推理
        test_img = Path("datasets/coco8/images/val").glob("*.jpg")
        test_img = next(test_img, None)
        
        if not test_img:
            print("❌ 未找到测试图片")
            return
        
        print(f"测试图片: {test_img.name}")
        print("正在推理...\n")
        
        response = yolo_service.infer(
            image_path=str(test_img),
            model_name="yolo11_coco8_trained.pt",
            confidence=0.25,
            iou_threshold=0.45
        )
        
        if response.success:
            print("✓ API 推理成功！")
            print(f"  推理时间: {response.inference_time*1000:.1f}ms")
            print(f"  检测数量: {len(response.detections)}")
            print(f"  图像尺寸: {response.image_shape}")
            
            for i, det in enumerate(response.detections, 1):
                print(f"  [{i}] {det.class_name} - 置信度: {det.confidence:.3f}")
        else:
            print(f"❌ API 推理失败: {response.message}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    # 1. 使用 COCO8 验证集测试
    test_inference_on_coco8()
    
    # 2. 通过项目 API 测试
    test_inference_with_api()
    
    print("\n✅ 所有推理测试完成！\n")


if __name__ == "__main__":
    main()
