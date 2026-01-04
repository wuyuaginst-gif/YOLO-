#!/usr/bin/env python3
"""
YOLO11 模型训练测试脚本
使用 COCO8 数据集测试训练功能
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from ultralytics import YOLO
import torch

# 配置
DATA_DIR = Path("data")
MODELS_DIR = DATA_DIR / "models"
DATASETS_DIR = DATA_DIR / "datasets"

# 创建必要的目录
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATASETS_DIR.mkdir(parents=True, exist_ok=True)


def print_section(title):
    """打印分隔线和标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def check_environment():
    """检查环境"""
    print_section("环境检查")
    
    print(f"Python 版本: {sys.version}")
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"CUDA 可用: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA 版本: {torch.version.cuda}")
        print(f"GPU 设备: {torch.cuda.get_device_name(0)}")
        print(f"GPU 数量: {torch.cuda.device_count()}")
    else:
        print("将使用 CPU 进行训练")
    
    # 检查 ultralytics
    try:
        from ultralytics import __version__
        print(f"Ultralytics 版本: {__version__}")
    except:
        print("无法获取 Ultralytics 版本")


def prepare_coco8_dataset():
    """准备 COCO8 数据集"""
    print_section("准备 COCO8 数据集")
    
    # COCO8 是 ultralytics 自带的示例数据集
    # 在第一次训练时会自动下载
    print("COCO8 数据集将在首次训练时自动下载")
    print("数据集位置: ultralytics 自动管理")
    
    return "coco8.yaml"


def test_model_loading():
    """测试模型加载"""
    print_section("测试 YOLO11 模型加载")
    
    model_variants = ["yolo11n.pt", "yolo11s.pt"]
    
    for model_name in model_variants:
        try:
            print(f"\n尝试加载模型: {model_name}")
            start_time = time.time()
            
            model = YOLO(model_name)
            load_time = time.time() - start_time
            
            print(f"✓ 模型加载成功！")
            print(f"  - 加载时间: {load_time:.2f}s")
            print(f"  - 模型任务: {model.task}")
            print(f"  - 类别数量: {len(model.names)}")
            print(f"  - 前5个类别: {list(model.names.values())[:5]}")
            
            # 只测试前两个模型
            break
            
        except Exception as e:
            print(f"✗ 模型加载失败: {e}")
    
    return model


def train_yolo11_model(dataset_path, epochs=3, img_size=640):
    """训练 YOLO11 模型"""
    print_section(f"开始训练 YOLO11 模型 (Epochs: {epochs})")
    
    try:
        # 使用 YOLO11n (最轻量级的模型)
        print("初始化 YOLO11n 模型...")
        model = YOLO("yolo11n.pt")
        
        # 设置训练参数
        project_name = f"yolo11_coco8_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n训练配置:")
        print(f"  - 数据集: {dataset_path}")
        print(f"  - 模型: YOLO11n")
        print(f"  - Epochs: {epochs}")
        print(f"  - 图像尺寸: {img_size}")
        print(f"  - 批次大小: 16")
        print(f"  - 设备: {'cuda' if torch.cuda.is_available() else 'cpu'}")
        print(f"  - 项目名称: {project_name}")
        
        print("\n开始训练...\n")
        start_time = time.time()
        
        # 开始训练
        results = model.train(
            data=dataset_path,
            epochs=epochs,
            batch=16,
            imgsz=img_size,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            project=str(MODELS_DIR / project_name),
            name="train",
            exist_ok=True,
            pretrained=True,
            patience=50,
            save_period=1,
            verbose=True,
            plots=True
        )
        
        training_time = time.time() - start_time
        
        print(f"\n✓ 训练完成！")
        print(f"  - 总耗时: {training_time:.2f}s ({training_time/60:.2f}min)")
        print(f"  - 平均每轮: {training_time/epochs:.2f}s")
        
        # 显示训练结果
        if hasattr(results, 'results_dict'):
            print(f"\n最终指标:")
            for key, value in results.results_dict.items():
                if isinstance(value, (int, float)):
                    print(f"  - {key}: {value:.4f}")
        
        # 保存路径
        weights_dir = MODELS_DIR / project_name / "train" / "weights"
        best_model = weights_dir / "best.pt"
        last_model = weights_dir / "last.pt"
        
        print(f"\n模型保存位置:")
        print(f"  - 最佳模型: {best_model}")
        print(f"  - 最后模型: {last_model}")
        
        if best_model.exists():
            print(f"  - 最佳模型大小: {best_model.stat().st_size / 1024 / 1024:.2f} MB")
        
        return {
            "success": True,
            "model_path": str(best_model),
            "training_time": training_time,
            "project_dir": str(MODELS_DIR / project_name / "train")
        }
        
    except Exception as e:
        print(f"\n✗ 训练失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


def test_trained_model(model_path):
    """测试训练好的模型"""
    print_section("测试训练好的模型")
    
    try:
        if not Path(model_path).exists():
            print(f"✗ 模型文件不存在: {model_path}")
            return
        
        print(f"加载模型: {model_path}")
        model = YOLO(model_path)
        
        print(f"✓ 模型加载成功！")
        print(f"  - 模型任务: {model.task}")
        print(f"  - 类别数量: {len(model.names)}")
        
        # 使用 COCO8 数据集的一个样本图片进行测试
        print("\n正在进行推理测试...")
        
        # 创建一个简单的测试图片
        import numpy as np
        from PIL import Image
        
        # 创建一个测试图片
        test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        test_img_path = DATA_DIR / "test_image.jpg"
        Image.fromarray(test_img).save(test_img_path)
        
        # 推理
        results = model.predict(
            source=str(test_img_path),
            conf=0.25,
            verbose=False
        )
        
        print(f"✓ 推理测试成功！")
        print(f"  - 检测到 {len(results[0].boxes)} 个对象")
        
        # 清理测试图片
        test_img_path.unlink()
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  YOLO11 模型训练测试 - COCO8 数据集")
    print("=" * 80)
    
    # 1. 环境检查
    check_environment()
    
    # 2. 准备数据集
    dataset_path = prepare_coco8_dataset()
    
    # 3. 测试模型加载
    test_model_loading()
    
    # 4. 训练模型 (使用较少的 epochs 快速测试)
    print("\n提示: 使用 3 个 epochs 进行快速测试")
    result = train_yolo11_model(
        dataset_path=dataset_path,
        epochs=3,
        img_size=640
    )
    
    # 5. 测试训练好的模型
    if result["success"]:
        test_trained_model(result["model_path"])
        
        # 显示总结
        print_section("测试总结")
        print("✓ YOLO11 模型训练功能测试成功！")
        print(f"✓ 训练时间: {result['training_time']:.2f}s")
        print(f"✓ 模型保存路径: {result['model_path']}")
        print(f"✓ 项目目录: {result['project_dir']}")
        
        print("\n后续步骤:")
        print("  1. 查看训练结果图表:")
        print(f"     {result['project_dir']}")
        print("  2. 使用训练好的模型进行推理")
        print("  3. 导出模型为其他格式 (ONNX, TensorRT 等)")
    else:
        print_section("测试失败")
        print(f"✗ 训练失败: {result.get('error', 'Unknown error')}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
