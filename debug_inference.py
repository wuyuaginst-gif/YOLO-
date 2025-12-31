#!/usr/bin/env python3
"""
推理接口调试脚本
用于诊断 /api/v1/inference/image 接口的 500 错误
"""
import sys
import traceback
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def check_imports():
    """检查必要的包导入"""
    print("=" * 60)
    print("1. 检查包导入...")
    print("=" * 60)
    
    try:
        import torch
        print(f"✅ PyTorch 已安装: {torch.__version__}")
        print(f"   CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU 设备: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"❌ PyTorch 导入失败: {e}")
    
    try:
        import ultralytics
        print(f"✅ Ultralytics 已安装: {ultralytics.__version__}")
    except ImportError as e:
        print(f"❌ Ultralytics 导入失败: {e}")
    
    try:
        from ultralytics import YOLO
        print(f"✅ YOLO 类导入成功")
    except ImportError as e:
        print(f"❌ YOLO 类导入失败: {e}")
    
    try:
        import cv2
        print(f"✅ OpenCV 已安装: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV 导入失败: {e}")
    
    try:
        from PIL import Image
        print(f"✅ PIL/Pillow 已安装")
    except ImportError as e:
        print(f"❌ PIL/Pillow 导入失败: {e}")
    
    print()


def check_directories():
    """检查必要的目录"""
    print("=" * 60)
    print("2. 检查目录结构...")
    print("=" * 60)
    
    from config.config import settings
    
    dirs = {
        "数据目录": settings.DATA_DIR,
        "模型目录": settings.MODELS_DIR,
        "上传目录": settings.UPLOADS_DIR,
        "数据集目录": settings.DATASETS_DIR,
        "导出目录": settings.EXPORTS_DIR,
    }
    
    for name, path in dirs.items():
        if path.exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (不存在)")
    
    print()


def check_models():
    """检查可用模型"""
    print("=" * 60)
    print("3. 检查可用模型...")
    print("=" * 60)
    
    from config.config import settings
    
    models_dir = settings.MODELS_DIR
    pt_files = list(models_dir.glob("**/*.pt"))
    
    if pt_files:
        print(f"找到 {len(pt_files)} 个模型文件:")
        for model_file in pt_files:
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"  - {model_file.name} ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  在 {models_dir} 中未找到 .pt 模型文件")
        print(f"   将尝试下载默认模型: {settings.DEFAULT_MODEL}")
    
    print()


def test_yolo_service():
    """测试 YOLO 服务"""
    print("=" * 60)
    print("4. 测试 YOLO 服务...")
    print("=" * 60)
    
    try:
        from backend.services.yolo_service import yolo_service, ULTRALYTICS_AVAILABLE
        
        if not ULTRALYTICS_AVAILABLE:
            print("❌ Ultralytics 不可用")
            return False
        
        if yolo_service is None:
            print("❌ YOLO 服务未初始化")
            return False
        
        print("✅ YOLO 服务已初始化")
        
        # 测试模型加载
        from config.config import settings
        default_model = settings.DEFAULT_MODEL
        print(f"\n尝试加载默认模型: {default_model}")
        
        try:
            model = yolo_service.load_model(default_model)
            print(f"✅ 模型加载成功")
            print(f"   模型任务类型: {model.task}")
            print(f"   类别数量: {len(model.names)}")
            print(f"   类别列表: {list(model.names.values())[:10]}...")  # 只显示前10个
            return True
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ YOLO 服务测试失败: {e}")
        traceback.print_exc()
        return False
    
    print()


def test_inference():
    """测试推理功能"""
    print("=" * 60)
    print("5. 测试推理功能...")
    print("=" * 60)
    
    try:
        import numpy as np
        from PIL import Image
        from config.config import settings
        from backend.services.yolo_service import yolo_service
        
        # 创建测试图片
        test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        test_img_path = settings.UPLOADS_DIR / "test_image.jpg"
        
        img = Image.fromarray(test_img)
        img.save(test_img_path)
        print(f"✅ 创建测试图片: {test_img_path}")
        
        # 执行推理
        print(f"\n执行推理...")
        result = yolo_service.infer(
            image_path=str(test_img_path),
            model_name=None,  # 使用默认模型
            confidence=0.25,
            iou_threshold=0.45,
            img_size=640
        )
        
        if result.success:
            print(f"✅ 推理成功")
            print(f"   检测到 {len(result.detections)} 个对象")
            print(f"   推理时间: {result.inference_time:.4f} 秒")
            print(f"   图片尺寸: {result.image_shape}")
            
            if result.detections:
                print(f"\n   检测结果:")
                for i, det in enumerate(result.detections[:5], 1):  # 只显示前5个
                    print(f"     {i}. {det.class_name} (置信度: {det.confidence:.2f})")
            
            return True
        else:
            print(f"❌ 推理失败: {result.message}")
            return False
            
    except Exception as e:
        print(f"❌ 推理测试失败: {e}")
        traceback.print_exc()
        return False
    finally:
        # 清理测试文件
        if test_img_path.exists():
            test_img_path.unlink()
            print(f"\n清理测试文件")
    
    print()


def check_error_logs():
    """检查可能的错误日志"""
    print("=" * 60)
    print("6. 常见问题诊断...")
    print("=" * 60)
    
    issues = []
    
    # 检查内存
    try:
        import psutil
        mem = psutil.virtual_memory()
        print(f"内存使用: {mem.percent}% ({mem.used / (1024**3):.2f} GB / {mem.total / (1024**3):.2f} GB)")
        if mem.percent > 90:
            issues.append("⚠️  内存使用过高，可能导致推理失败")
    except ImportError:
        print("未安装 psutil，无法检查内存")
    
    # 检查磁盘空间
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        print(f"磁盘空间: {free_gb:.2f} GB 可用")
        if free_gb < 1:
            issues.append("⚠️  磁盘空间不足，可能影响模型加载")
    except:
        print("无法检查磁盘空间")
    
    if issues:
        print("\n发现的问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ 未发现明显问题")
    
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("OpenCV Platform - 推理接口诊断工具")
    print("=" * 60 + "\n")
    
    # 运行所有检查
    check_imports()
    check_directories()
    check_models()
    
    yolo_ok = test_yolo_service()
    
    if yolo_ok:
        test_inference()
    else:
        print("⚠️  YOLO 服务未就绪，跳过推理测试")
    
    check_error_logs()
    
    print("=" * 60)
    print("诊断完成")
    print("=" * 60)
    print("\n如果所有测试都通过，但 API 仍然返回 500 错误，")
    print("请检查:")
    print("1. 上传的图片文件是否有效")
    print("2. 模型文件是否完整（未损坏）")
    print("3. 查看应用日志获取详细错误信息")
    print()


if __name__ == "__main__":
    main()
