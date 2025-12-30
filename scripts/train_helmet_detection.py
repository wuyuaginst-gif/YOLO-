#!/usr/bin/env python3
"""
安全帽检测模型训练脚本
Author: OpenCV Platform Team
Date: 2025-12-30

使用方法:
    python scripts/train_helmet_detection.py --data path/to/data.yaml --epochs 100
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from ultralytics import YOLO
    import yaml
except ImportError as e:
    print(f"❌ 缺少必要的依赖包: {e}")
    print("请运行: pip install ultralytics pyyaml")
    sys.exit(1)


def validate_dataset(data_yaml_path):
    """验证数据集配置和文件"""
    if not os.path.exists(data_yaml_path):
        raise FileNotFoundError(f"数据集配置文件不存在: {data_yaml_path}")
    
    with open(data_yaml_path, 'r') as f:
        data_config = yaml.safe_load(f)
    
    required_keys = ['path', 'train', 'val', 'nc', 'names']
    for key in required_keys:
        if key not in data_config:
            raise ValueError(f"数据集配置缺少必要字段: {key}")
    
    # 检查数据集路径
    dataset_path = Path(data_config['path'])
    train_path = dataset_path / data_config['train']
    val_path = dataset_path / data_config['val']
    
    if not train_path.exists():
        raise FileNotFoundError(f"训练集路径不存在: {train_path}")
    if not val_path.exists():
        raise FileNotFoundError(f"验证集路径不存在: {val_path}")
    
    # 统计图片数量
    train_images = list(train_path.glob('*.jpg')) + list(train_path.glob('*.png'))
    val_images = list(val_path.glob('*.jpg')) + list(val_path.glob('*.png'))
    
    print("📊 数据集信息:")
    print(f"  - 类别数量: {data_config['nc']}")
    print(f"  - 类别名称: {data_config['names']}")
    print(f"  - 训练集图片: {len(train_images)}")
    print(f"  - 验证集图片: {len(val_images)}")
    
    if len(train_images) < 100:
        print("⚠️  警告: 训练集图片数量较少，建议至少 500 张")
    
    return data_config


def train_helmet_detection(args):
    """训练安全帽检测模型"""
    
    print("=" * 60)
    print("🎯 安全帽检测模型训练")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 验证数据集
    print("1️⃣ 验证数据集...")
    try:
        data_config = validate_dataset(args.data)
        print("✅ 数据集验证通过\n")
    except Exception as e:
        print(f"❌ 数据集验证失败: {e}")
        return False
    
    # 加载模型
    print(f"2️⃣ 加载模型: {args.model}")
    try:
        model = YOLO(args.model)
        print(f"✅ 模型加载成功\n")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return False
    
    # 训练参数
    print("3️⃣ 训练参数:")
    print(f"  - 模型: {args.model}")
    print(f"  - 训练轮数: {args.epochs}")
    print(f"  - 批次大小: {args.batch}")
    print(f"  - 图片尺寸: {args.imgsz}")
    print(f"  - 设备: {args.device}")
    print(f"  - 项目名称: {args.name}")
    print(f"  - 耐心值: {args.patience}")
    print()
    
    # 开始训练
    print("4️⃣ 开始训练...")
    try:
        results = model.train(
            data=args.data,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            name=args.name,
            patience=args.patience,
            save_period=args.save_period,
            device=args.device,
            workers=args.workers,
            
            # 优化器参数
            optimizer=args.optimizer,
            lr0=args.lr0,
            lrf=args.lrf,
            momentum=args.momentum,
            weight_decay=args.weight_decay,
            
            # 数据增强参数
            hsv_h=args.hsv_h,
            hsv_s=args.hsv_s,
            hsv_v=args.hsv_v,
            degrees=args.degrees,
            translate=args.translate,
            scale=args.scale,
            shear=args.shear,
            perspective=args.perspective,
            flipud=args.flipud,
            fliplr=args.fliplr,
            mosaic=args.mosaic,
            mixup=args.mixup,
            
            # 其他参数
            verbose=True,
            seed=args.seed,
            deterministic=args.deterministic,
            single_cls=False,
            rect=False,
            cos_lr=args.cos_lr,
            close_mosaic=args.close_mosaic,
            amp=args.amp,
            fraction=args.fraction,
            profile=args.profile,
            overlap_mask=True,
            mask_ratio=4,
            dropout=args.dropout,
            val=True,
            plots=True,
        )
        
        print("\n✅ 训练完成!")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示训练结果
        print("\n📊 训练结果:")
        print(f"  - 最佳模型: runs/detect/{args.name}/weights/best.pt")
        print(f"  - 最后模型: runs/detect/{args.name}/weights/last.pt")
        
        # 运行验证
        if args.val:
            print("\n5️⃣ 运行验证...")
            metrics = model.val(data=args.data)
            print(f"\n📈 验证指标:")
            print(f"  - mAP50: {metrics.box.map50:.4f}")
            print(f"  - mAP50-95: {metrics.box.map:.4f}")
            print(f"  - Precision: {metrics.box.mp:.4f}")
            print(f"  - Recall: {metrics.box.mr:.4f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='训练安全帽检测模型',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 必需参数
    parser.add_argument('--data', type=str, required=True,
                       help='数据集配置文件路径 (data.yaml)')
    
    # 模型参数
    parser.add_argument('--model', type=str, default='yolo11n.pt',
                       choices=['yolo11n.pt', 'yolo11s.pt', 'yolo11m.pt', 
                               'yolo11l.pt', 'yolo11x.pt'],
                       help='预训练模型')
    
    # 训练参数
    parser.add_argument('--epochs', type=int, default=100,
                       help='训练轮数')
    parser.add_argument('--batch', type=int, default=16,
                       help='批次大小')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='输入图片尺寸')
    parser.add_argument('--device', type=str, default='cpu',
                       help='训练设备 (cpu, 0, 0,1,2,3 等)')
    parser.add_argument('--workers', type=int, default=8,
                       help='数据加载线程数')
    parser.add_argument('--name', type=str, default='helmet_detection',
                       help='项目名称')
    parser.add_argument('--patience', type=int, default=50,
                       help='早停耐心值')
    parser.add_argument('--save-period', type=int, default=10,
                       help='模型保存周期')
    
    # 优化器参数
    parser.add_argument('--optimizer', type=str, default='auto',
                       choices=['SGD', 'Adam', 'AdamW', 'NAdam', 'RAdam', 'RMSProp', 'auto'],
                       help='优化器类型')
    parser.add_argument('--lr0', type=float, default=0.01,
                       help='初始学习率')
    parser.add_argument('--lrf', type=float, default=0.01,
                       help='最终学习率 (lr0 * lrf)')
    parser.add_argument('--momentum', type=float, default=0.937,
                       help='SGD 动量/Adam beta1')
    parser.add_argument('--weight-decay', type=float, default=0.0005,
                       help='权重衰减')
    parser.add_argument('--cos-lr', action='store_true',
                       help='使用余弦学习率调度')
    
    # 数据增强参数
    parser.add_argument('--hsv-h', type=float, default=0.015,
                       help='HSV 色调增强')
    parser.add_argument('--hsv-s', type=float, default=0.7,
                       help='HSV 饱和度增强')
    parser.add_argument('--hsv-v', type=float, default=0.4,
                       help='HSV 明度增强')
    parser.add_argument('--degrees', type=float, default=10.0,
                       help='旋转角度 (±度)')
    parser.add_argument('--translate', type=float, default=0.1,
                       help='平移 (±图片尺寸的比例)')
    parser.add_argument('--scale', type=float, default=0.5,
                       help='缩放 (±增益)')
    parser.add_argument('--shear', type=float, default=0.0,
                       help='剪切 (±度)')
    parser.add_argument('--perspective', type=float, default=0.0,
                       help='透视变换')
    parser.add_argument('--flipud', type=float, default=0.0,
                       help='上下翻转概率')
    parser.add_argument('--fliplr', type=float, default=0.5,
                       help='左右翻转概率')
    parser.add_argument('--mosaic', type=float, default=1.0,
                       help='Mosaic 增强概率')
    parser.add_argument('--mixup', type=float, default=0.0,
                       help='MixUp 增强概率')
    parser.add_argument('--close-mosaic', type=int, default=10,
                       help='在最后 N 轮禁用 Mosaic')
    
    # 其他参数
    parser.add_argument('--seed', type=int, default=0,
                       help='随机种子')
    parser.add_argument('--deterministic', action='store_true',
                       help='确定性训练')
    parser.add_argument('--amp', action='store_true', default=True,
                       help='自动混合精度训练')
    parser.add_argument('--fraction', type=float, default=1.0,
                       help='训练集使用比例')
    parser.add_argument('--profile', action='store_true',
                       help='性能分析')
    parser.add_argument('--dropout', type=float, default=0.0,
                       help='Dropout 率')
    parser.add_argument('--val', action='store_true', default=True,
                       help='训练后运行验证')
    
    args = parser.parse_args()
    
    # 运行训练
    success = train_helmet_detection(args)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 训练成功完成!")
        print("=" * 60)
        print("\n下一步:")
        print("1. 查看训练结果: runs/detect/" + args.name)
        print("2. 使用最佳模型进行推理:")
        print(f"   python -c \"from ultralytics import YOLO; model = YOLO('runs/detect/{args.name}/weights/best.pt'); results = model('test.jpg')\"")
        print("3. 上传模型到平台:")
        print(f"   访问 http://localhost:8000/models 上传 runs/detect/{args.name}/weights/best.pt")
        print("4. 开始推理:")
        print("   访问 http://localhost:8000/inference")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ 训练失败")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
