#!/usr/bin/env python3
"""
修复训练失败问题的诊断和修复脚本
"""

import os
import sys
from pathlib import Path
import yaml

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def check_dataset_path():
    """检查数据集路径问题"""
    print("=" * 80)
    print("  检查数据集路径")
    print("=" * 80)
    
    # 可能的数据集路径
    dataset_paths = [
        "data/datasets/testdata/COCO8.yaml",
        "datasets/testdata/COCO8.yaml",
        "datasets/coco8/data.yaml",
        "datasets/coco8.yaml",
        "/home/user/webapp/datasets/coco8.yaml"
    ]
    
    for path in dataset_paths:
        full_path = Path(path)
        print(f"\n检查: {path}")
        if full_path.exists():
            print(f"  ✓ 文件存在")
            try:
                with open(full_path, 'r') as f:
                    data = yaml.safe_load(f)
                print(f"  ✓ YAML 格式正确")
                print(f"  - 类别数: {len(data.get('names', []))}")
                print(f"  - 路径: {data.get('path', 'N/A')}")
                print(f"  - 训练集: {data.get('train', 'N/A')}")
                print(f"  - 验证集: {data.get('val', 'N/A')}")
            except Exception as e:
                print(f"  ✗ 读取失败: {e}")
        else:
            print(f"  ✗ 文件不存在")
    
    # 检查 testdata 目录
    print("\n" + "=" * 80)
    print("  检查 testdata 目录结构")
    print("=" * 80)
    
    testdata_paths = [
        "data/datasets/testdata",
        "datasets/testdata"
    ]
    
    for path in testdata_paths:
        test_path = Path(path)
        if test_path.exists():
            print(f"\n✓ {path} 存在")
            print("  内容:")
            for item in test_path.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(test_path)
                    size = item.stat().st_size
                    print(f"    - {rel_path} ({size} bytes)")


def create_test_dataset():
    """创建测试数据集"""
    print("\n" + "=" * 80)
    print("  创建测试数据集")
    print("=" * 80)
    
    # 确保目录存在
    dataset_dir = Path("data/datasets/testdata")
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建 COCO8.yaml
    coco8_yaml = dataset_dir / "COCO8.yaml"
    
    yaml_content = {
        'path': str(Path.cwd() / 'datasets' / 'coco8'),  # 使用 coco8 数据集
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/val',
        'nc': 80,
        'names': [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
            'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
            'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
    }
    
    with open(coco8_yaml, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
    
    print(f"✓ 创建数据集配置: {coco8_yaml}")
    print(f"  - 路径: {yaml_content['path']}")
    print(f"  - 类别数: {yaml_content['nc']}")
    
    # 检查 coco8 数据集是否存在
    coco8_path = Path('datasets/coco8')
    if coco8_path.exists():
        print(f"\n✓ COCO8 数据集存在: {coco8_path}")
        
        # 统计图片数量
        train_images = list((coco8_path / 'images' / 'train').glob('*.jpg'))
        val_images = list((coco8_path / 'images' / 'val').glob('*.jpg'))
        
        print(f"  - 训练图片: {len(train_images)}")
        print(f"  - 验证图片: {len(val_images)}")
    else:
        print(f"\n✗ COCO8 数据集不存在，将在训练时自动下载")
    
    return str(coco8_yaml)


def test_training():
    """测试训练功能"""
    print("\n" + "=" * 80)
    print("  测试训练功能")
    print("=" * 80)
    
    try:
        from ultralytics import YOLO
        from backend.models.schemas import TrainingConfig
        from backend.services.yolo_service import yolo_service
        
        # 创建测试数据集
        dataset_path = create_test_dataset()
        
        # 创建训练配置
        config = TrainingConfig(
            project_name="test_training",
            dataset_path=dataset_path,
            model_type="yolo11n",
            epochs=1,  # 只训练1轮用于测试
            batch_size=16,
            img_size=640,
            device="cpu",
            pretrained=True
        )
        
        print(f"\n训练配置:")
        print(f"  - 项目名: {config.project_name}")
        print(f"  - 数据集: {config.dataset_path}")
        print(f"  - 模型: {config.model_type}")
        print(f"  - 训练轮数: {config.epochs}")
        
        # 直接测试模型加载和数据集
        print(f"\n测试模型加载...")
        model = YOLO(f"{config.model_type}.pt")
        print(f"✓ 模型加载成功")
        
        print(f"\n测试数据集加载...")
        # 尝试验证数据集
        import yaml
        with open(dataset_path, 'r') as f:
            data = yaml.safe_load(f)
        print(f"✓ 数据集配置正确")
        print(f"  - path: {data.get('path')}")
        print(f"  - train: {data.get('train')}")
        
        # 检查路径是否存在
        dataset_root = Path(data.get('path', ''))
        if dataset_root.exists():
            print(f"✓ 数据集根目录存在: {dataset_root}")
        else:
            print(f"⚠️ 数据集根目录不存在，将自动下载")
        
        print("\n" + "=" * 80)
        print("  诊断完成")
        print("=" * 80)
        print("\n建议:")
        print("1. 使用创建的数据集配置文件:")
        print(f"   {dataset_path}")
        print("\n2. 或者使用完整的 coco8.yaml 路径:")
        print("   datasets/coco8.yaml")
        print("\n3. 确保数据集路径正确且可访问")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def check_training_task_status():
    """检查训练任务状态"""
    print("\n" + "=" * 80)
    print("  检查训练任务状态")
    print("=" * 80)
    
    try:
        from backend.services.yolo_service import yolo_service
        
        tasks = yolo_service.training_tasks
        print(f"\n共有 {len(tasks)} 个训练任务")
        
        for task_id, status in tasks.items():
            print(f"\n任务 ID: {task_id}")
            print(f"  状态: {status.status}")
            print(f"  进度: {status.progress}%")
            print(f"  当前轮数: {status.current_epoch}/{status.total_epochs}")
            
            if status.error_message:
                print(f"  ✗ 错误: {status.error_message}")
            
            print(f"  创建时间: {status.created_at}")
            print(f"  更新时间: {status.updated_at}")
    
    except Exception as e:
        print(f"✗ 无法检查任务: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  YOLO 训练问题诊断和修复工具")
    print("=" * 80)
    
    # 1. 检查数据集路径
    check_dataset_path()
    
    # 2. 创建测试数据集
    dataset_path = create_test_dataset()
    
    # 3. 检查训练任务状态
    check_training_task_status()
    
    # 4. 测试训练功能
    test_training()
    
    print("\n" + "=" * 80)
    print("  诊断完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
