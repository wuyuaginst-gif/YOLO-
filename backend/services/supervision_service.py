#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Supervision 标注服务 - 使用 supervision 库进行数据标注和可视化
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import supervision as sv
from ultralytics import YOLO


class SupervisionService:
    """Supervision 标注和可视化服务"""
    
    def __init__(self):
        # 初始化标注工具
        self.box_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        self.mask_annotator = sv.MaskAnnotator()
        self.polygon_annotator = sv.PolygonAnnotator()
        
        # 追踪器
        self.tracker = sv.ByteTrack()
        
    def annotate_image(
        self,
        image: np.ndarray,
        detections: sv.Detections,
        labels: Optional[List[str]] = None,
        show_labels: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """
        在图像上标注检测结果
        
        Args:
            image: 输入图像
            detections: supervision Detections 对象
            labels: 标签列表
            show_labels: 是否显示标签
            show_confidence: 是否显示置信度
            
        Returns:
            标注后的图像
        """
        annotated_image = image.copy()
        
        # 绘制检测框
        annotated_image = self.box_annotator.annotate(
            scene=annotated_image,
            detections=detections
        )
        
        # 绘制标签
        if show_labels and labels:
            annotated_image = self.label_annotator.annotate(
                scene=annotated_image,
                detections=detections,
                labels=labels
            )
        
        return annotated_image
    
    def annotate_with_masks(
        self,
        image: np.ndarray,
        detections: sv.Detections
    ) -> np.ndarray:
        """
        使用掩码标注图像（用于实例分割）
        
        Args:
            image: 输入图像
            detections: 包含掩码的 Detections 对象
            
        Returns:
            标注后的图像
        """
        annotated_image = image.copy()
        
        # 绘制掩码
        if detections.mask is not None:
            annotated_image = self.mask_annotator.annotate(
                scene=annotated_image,
                detections=detections
            )
        
        # 绘制边界框
        annotated_image = self.box_annotator.annotate(
            scene=annotated_image,
            detections=detections
        )
        
        return annotated_image
    
    def yolo_results_to_detections(
        self,
        results,
        class_names: Optional[List[str]] = None
    ) -> Tuple[sv.Detections, List[str]]:
        """
        将 YOLO 结果转换为 supervision Detections 对象
        
        Args:
            results: YOLO 推理结果
            class_names: 类别名称列表
            
        Returns:
            (detections, labels) 元组
        """
        # 转换为 supervision Detections
        detections = sv.Detections.from_ultralytics(results[0])
        
        # 生成标签
        labels = []
        if class_names:
            for class_id, confidence in zip(detections.class_id, detections.confidence):
                class_name = class_names[class_id] if class_id < len(class_names) else f"class_{class_id}"
                label = f"{class_name} {confidence:.2f}"
                labels.append(label)
        
        return detections, labels
    
    def track_objects(
        self,
        detections: sv.Detections
    ) -> sv.Detections:
        """
        对象追踪
        
        Args:
            detections: 当前帧的检测结果
            
        Returns:
            包含追踪 ID 的 Detections 对象
        """
        return self.tracker.update_with_detections(detections)
    
    def create_zone(
        self,
        polygon: List[Tuple[int, int]],
        frame_resolution_wh: Tuple[int, int]
    ) -> sv.PolygonZone:
        """
        创建多边形区域（用于区域检测）
        
        Args:
            polygon: 多边形顶点坐标列表 [(x1,y1), (x2,y2), ...]
            frame_resolution_wh: 帧分辨率 (width, height)
            
        Returns:
            PolygonZone 对象
        """
        polygon_np = np.array(polygon, dtype=np.int32)
        return sv.PolygonZone(
            polygon=polygon_np,
            frame_resolution_wh=frame_resolution_wh
        )
    
    def count_objects_in_zone(
        self,
        detections: sv.Detections,
        zone: sv.PolygonZone
    ) -> int:
        """
        统计区域内的对象数量
        
        Args:
            detections: 检测结果
            zone: 多边形区域
            
        Returns:
            区域内对象数量
        """
        mask = zone.trigger(detections)
        return int(np.sum(mask))
    
    def create_line_zone(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int]
    ) -> sv.LineZone:
        """
        创建线区域（用于计数进出）
        
        Args:
            start: 起点坐标 (x, y)
            end: 终点坐标 (x, y)
            
        Returns:
            LineZone 对象
        """
        line_start = sv.Point(*start)
        line_end = sv.Point(*end)
        return sv.LineZone(start=line_start, end=line_end)
    
    def filter_detections(
        self,
        detections: sv.Detections,
        class_ids: Optional[List[int]] = None,
        confidence_threshold: Optional[float] = None
    ) -> sv.Detections:
        """
        过滤检测结果
        
        Args:
            detections: 原始检测结果
            class_ids: 要保留的类别 ID 列表
            confidence_threshold: 置信度阈值
            
        Returns:
            过滤后的检测结果
        """
        mask = np.ones(len(detections), dtype=bool)
        
        # 按类别过滤
        if class_ids is not None:
            class_mask = np.isin(detections.class_id, class_ids)
            mask = mask & class_mask
        
        # 按置信度过滤
        if confidence_threshold is not None:
            conf_mask = detections.confidence >= confidence_threshold
            mask = mask & conf_mask
        
        return detections[mask]
    
    def export_detections_to_yolo(
        self,
        detections: sv.Detections,
        image_path: str,
        output_dir: str,
        class_names: List[str]
    ) -> bool:
        """
        将检测结果导出为 YOLO 格式
        
        Args:
            detections: 检测结果
            image_path: 图像路径
            output_dir: 输出目录
            class_names: 类别名称列表
            
        Returns:
            是否成功
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 获取图像尺寸
            image = cv2.imread(image_path)
            h, w = image.shape[:2]
            
            # 创建标签文件
            image_name = Path(image_path).stem
            label_file = output_path / f"{image_name}.txt"
            
            with open(label_file, 'w') as f:
                for i in range(len(detections)):
                    class_id = detections.class_id[i]
                    xyxy = detections.xyxy[i]
                    
                    # 转换为 YOLO 格式 (class_id, center_x, center_y, width, height)
                    # 坐标归一化到 [0, 1]
                    x_center = ((xyxy[0] + xyxy[2]) / 2) / w
                    y_center = ((xyxy[1] + xyxy[3]) / 2) / h
                    width = (xyxy[2] - xyxy[0]) / w
                    height = (xyxy[3] - xyxy[1]) / h
                    
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            return True
        except Exception as e:
            print(f"Error exporting detections: {e}")
            return False
    
    def create_dataset_from_detections(
        self,
        image_dir: str,
        detections_dict: Dict[str, sv.Detections],
        output_dir: str,
        class_names: List[str],
        train_split: float = 0.8
    ) -> Dict[str, Any]:
        """
        从检测结果创建 YOLO 数据集
        
        Args:
            image_dir: 图像目录
            detections_dict: {image_name: detections} 字典
            output_dir: 输出目录
            class_names: 类别名称列表
            train_split: 训练集比例
            
        Returns:
            数据集信息字典
        """
        try:
            output_path = Path(output_dir)
            
            # 创建目录结构
            (output_path / "images" / "train").mkdir(parents=True, exist_ok=True)
            (output_path / "images" / "val").mkdir(parents=True, exist_ok=True)
            (output_path / "labels" / "train").mkdir(parents=True, exist_ok=True)
            (output_path / "labels" / "val").mkdir(parents=True, exist_ok=True)
            
            # 分割数据集
            image_names = list(detections_dict.keys())
            np.random.shuffle(image_names)
            split_idx = int(len(image_names) * train_split)
            train_images = image_names[:split_idx]
            val_images = image_names[split_idx:]
            
            # 处理训练集
            for img_name in train_images:
                self._process_image_for_dataset(
                    img_name,
                    detections_dict[img_name],
                    image_dir,
                    str(output_path / "images" / "train"),
                    str(output_path / "labels" / "train"),
                    class_names
                )
            
            # 处理验证集
            for img_name in val_images:
                self._process_image_for_dataset(
                    img_name,
                    detections_dict[img_name],
                    image_dir,
                    str(output_path / "images" / "val"),
                    str(output_path / "labels" / "val"),
                    class_names
                )
            
            # 创建 data.yaml
            data_yaml_content = f"""# YOLO Dataset
path: {output_path.absolute()}
train: images/train
val: images/val

# Classes
names:
"""
            for i, name in enumerate(class_names):
                data_yaml_content += f"  {i}: {name}\n"
            
            with open(output_path / "data.yaml", 'w') as f:
                f.write(data_yaml_content)
            
            return {
                "success": True,
                "dataset_path": str(output_path),
                "num_classes": len(class_names),
                "num_train": len(train_images),
                "num_val": len(val_images),
                "classes": class_names
            }
            
        except Exception as e:
            print(f"Error creating dataset: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_image_for_dataset(
        self,
        image_name: str,
        detections: sv.Detections,
        src_image_dir: str,
        dst_image_dir: str,
        dst_label_dir: str,
        class_names: List[str]
    ):
        """处理单张图像和标注"""
        import shutil
        
        # 复制图像
        src_image = Path(src_image_dir) / image_name
        dst_image = Path(dst_image_dir) / image_name
        shutil.copy(src_image, dst_image)
        
        # 保存标注
        image = cv2.imread(str(src_image))
        h, w = image.shape[:2]
        
        label_file = Path(dst_label_dir) / f"{Path(image_name).stem}.txt"
        
        with open(label_file, 'w') as f:
            for i in range(len(detections)):
                class_id = detections.class_id[i]
                xyxy = detections.xyxy[i]
                
                # YOLO 格式
                x_center = ((xyxy[0] + xyxy[2]) / 2) / w
                y_center = ((xyxy[1] + xyxy[3]) / 2) / h
                width = (xyxy[2] - xyxy[0]) / w
                height = (xyxy[3] - xyxy[1]) / h
                
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")


# 全局服务实例
supervision_service = SupervisionService()
