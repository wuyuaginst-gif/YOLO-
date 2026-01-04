#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地数据标注服务 - 集成 Supervision
"""
import os
import json
import shutil
import zipfile
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import supervision as sv

from config.config import settings
from backend.services.supervision_service import supervision_service


class AnnotationService:
    """本地数据标注服务"""
    
    def __init__(self):
        self.projects_dir = Path(settings.DATA_DIR) / "annotation_projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.projects_file = self.projects_dir / "projects.json"
        
        # 初始化projects文件
        if not self.projects_file.exists():
            self._save_projects_index([])
    
    def _load_projects_index(self) -> List[Dict[str, Any]]:
        """加载项目索引"""
        try:
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading projects index: {e}")
            return []
    
    def _save_projects_index(self, projects: List[Dict[str, Any]]):
        """保存项目索引"""
        try:
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(projects, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving projects index: {e}")
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """列出所有项目"""
        return self._load_projects_index()
    
    def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        """创建新项目"""
        project_id = str(uuid.uuid4())
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建项目目录结构
        (project_dir / "images").mkdir(exist_ok=True)
        (project_dir / "annotations").mkdir(exist_ok=True)
        
        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "path": str(project_dir)
        }
        
        # 保存项目配置
        project_config_file = project_dir / "project.json"
        with open(project_config_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        
        # 更新项目索引
        projects = self._load_projects_index()
        projects.append(project)
        self._save_projects_index(projects)
        
        return project
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目详情"""
        project_dir = self.projects_dir / project_id
        project_config_file = project_dir / "project.json"
        
        if not project_config_file.exists():
            return None
        
        try:
            with open(project_config_file, 'r', encoding='utf-8') as f:
                project = json.load(f)
            
            # 加载图片列表
            images_dir = project_dir / "images"
            images = []
            for img_path in images_dir.glob("*"):
                if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
                    images.append({
                        "name": img_path.name,
                        "url": f"/api/v1/annotation/image/{project_id}/{img_path.name}",
                        "path": str(img_path)
                    })
            
            # 加载标注数据
            annotations_file = project_dir / "annotations" / "annotations.json"
            annotations = {}
            if annotations_file.exists():
                with open(annotations_file, 'r', encoding='utf-8') as f:
                    annotations = json.load(f)
            
            # 加载类别
            classes_file = project_dir / "annotations" / "classes.json"
            classes = ['person', 'car', 'dog', 'cat']  # 默认类别
            if classes_file.exists():
                with open(classes_file, 'r', encoding='utf-8') as f:
                    classes = json.load(f)
            
            project['images'] = images
            project['annotations'] = annotations
            project['classes'] = classes
            
            return project
        except Exception as e:
            print(f"Error loading project: {e}")
            return None
    
    def upload_images(self, project_id: str, files: List[Any]) -> Dict[str, Any]:
        """上传图片到项目"""
        project_dir = self.projects_dir / project_id
        if not project_dir.exists():
            return {"success": False, "message": "Project not found"}
        
        images_dir = project_dir / "images"
        uploaded = 0
        
        try:
            for file in files:
                # 保存文件
                file_path = images_dir / file.filename
                with open(file_path, 'wb') as f:
                    content = file.file.read()
                    f.write(content)
                uploaded += 1
            
            # 更新项目时间
            self._update_project_timestamp(project_id)
            
            return {
                "success": True,
                "uploaded": uploaded,
                "message": f"Successfully uploaded {uploaded} images"
            }
        except Exception as e:
            print(f"Error uploading images: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def save_annotations(
        self,
        project_id: str,
        annotations: Dict[str, List[Dict[str, Any]]],
        classes: List[str]
    ) -> Dict[str, Any]:
        """保存标注数据"""
        project_dir = self.projects_dir / project_id
        if not project_dir.exists():
            return {"success": False, "message": "Project not found"}
        
        try:
            annotations_dir = project_dir / "annotations"
            annotations_dir.mkdir(exist_ok=True)
            
            # 保存标注数据
            annotations_file = annotations_dir / "annotations.json"
            with open(annotations_file, 'w', encoding='utf-8') as f:
                json.dump(annotations, f, ensure_ascii=False, indent=2)
            
            # 保存类别
            classes_file = annotations_dir / "classes.json"
            with open(classes_file, 'w', encoding='utf-8') as f:
                json.dump(classes, f, ensure_ascii=False, indent=2)
            
            # 更新项目时间
            self._update_project_timestamp(project_id)
            
            return {
                "success": True,
                "message": "Annotations saved successfully"
            }
        except Exception as e:
            print(f"Error saving annotations: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def export_to_yolo(self, project_id: str) -> Optional[Path]:
        """导出为YOLO格式"""
        project_dir = self.projects_dir / project_id
        if not project_dir.exists():
            return None
        
        try:
            # 创建临时导出目录
            export_dir = project_dir / "export_yolo"
            if export_dir.exists():
                shutil.rmtree(export_dir)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建YOLO目录结构
            images_train_dir = export_dir / "images" / "train"
            images_val_dir = export_dir / "images" / "val"
            labels_train_dir = export_dir / "labels" / "train"
            labels_val_dir = export_dir / "labels" / "val"
            
            for dir_path in [images_train_dir, images_val_dir, labels_train_dir, labels_val_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # 加载标注数据
            annotations_file = project_dir / "annotations" / "annotations.json"
            if not annotations_file.exists():
                return None
            
            with open(annotations_file, 'r', encoding='utf-8') as f:
                annotations = json.load(f)
            
            # 加载类别
            classes_file = project_dir / "annotations" / "classes.json"
            classes = ['person', 'car', 'dog', 'cat']
            if classes_file.exists():
                with open(classes_file, 'r', encoding='utf-8') as f:
                    classes = json.load(f)
            
            # 分割数据集 (80% train, 20% val)
            images_dir = project_dir / "images"
            image_files = list(images_dir.glob("*"))
            image_files = [f for f in image_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']]
            
            import random
            random.shuffle(image_files)
            split_idx = int(len(image_files) * 0.8)
            train_images = image_files[:split_idx]
            val_images = image_files[split_idx:]
            
            # 处理训练集
            for img_path in train_images:
                self._process_image_for_yolo(
                    img_path,
                    images_train_dir,
                    labels_train_dir,
                    annotations.get(img_path.name, []),
                    classes
                )
            
            # 处理验证集
            for img_path in val_images:
                self._process_image_for_yolo(
                    img_path,
                    images_val_dir,
                    labels_val_dir,
                    annotations.get(img_path.name, []),
                    classes
                )
            
            # 创建data.yaml
            data_yaml_content = f"""# YOLO Dataset
path: {export_dir.absolute()}
train: images/train
val: images/val

# Classes
names:
"""
            for i, cls in enumerate(classes):
                data_yaml_content += f"  {i}: {cls}\n"
            
            data_yaml_path = export_dir / "data.yaml"
            with open(data_yaml_path, 'w', encoding='utf-8') as f:
                f.write(data_yaml_content)
            
            # 创建README
            readme_content = f"""# YOLO Dataset Export

Project: {project_id}
Export Date: {datetime.now().isoformat()}

## Statistics
- Total Images: {len(image_files)}
- Training Images: {len(train_images)}
- Validation Images: {len(val_images)}
- Classes: {len(classes)}

## Classes
{chr(10).join(f'{i}. {cls}' for i, cls in enumerate(classes))}

## Usage
Use this dataset with Ultralytics YOLO:

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.train(data='data.yaml', epochs=100)
```
"""
            readme_path = export_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # 压缩为zip
            zip_path = project_dir / f"{project_id}_yolo.zip"
            if zip_path.exists():
                zip_path.unlink()
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(export_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(export_dir)
                        zipf.write(file_path, arcname)
            
            # 清理临时目录
            shutil.rmtree(export_dir)
            
            return zip_path
            
        except Exception as e:
            print(f"Error exporting to YOLO: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _process_image_for_yolo(
        self,
        img_path: Path,
        target_images_dir: Path,
        target_labels_dir: Path,
        annotations: List[Dict[str, Any]],
        classes: List[str]
    ):
        """处理单张图片为YOLO格式"""
        # 复制图片
        shutil.copy(img_path, target_images_dir / img_path.name)
        
        # 创建标签文件
        label_path = target_labels_dir / f"{img_path.stem}.txt"
        
        if not annotations:
            # 创建空标签文件
            label_path.touch()
            return
        
        # 写入YOLO格式标注
        with open(label_path, 'w', encoding='utf-8') as f:
            for ann in annotations:
                class_id = classes.index(ann['class']) if ann['class'] in classes else 0
                
                # YOLO格式: class_id center_x center_y width height (归一化坐标)
                center_x = ann['x'] + ann['width'] / 2
                center_y = ann['y'] + ann['height'] / 2
                width = ann['width']
                height = ann['height']
                
                f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
    
    def _update_project_timestamp(self, project_id: str):
        """更新项目时间戳"""
        project_dir = self.projects_dir / project_id
        project_config_file = project_dir / "project.json"
        
        if project_config_file.exists():
            try:
                with open(project_config_file, 'r', encoding='utf-8') as f:
                    project = json.load(f)
                
                project['updated_at'] = datetime.now().isoformat()
                
                with open(project_config_file, 'w', encoding='utf-8') as f:
                    json.dump(project, f, ensure_ascii=False, indent=2)
                
                # 更新索引
                projects = self._load_projects_index()
                for i, p in enumerate(projects):
                    if p['id'] == project_id:
                        projects[i] = project
                        break
                self._save_projects_index(projects)
            except Exception as e:
                print(f"Error updating project timestamp: {e}")
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """删除项目"""
        project_dir = self.projects_dir / project_id
        
        if not project_dir.exists():
            return {"success": False, "message": "Project not found"}
        
        try:
            # 删除项目目录
            shutil.rmtree(project_dir)
            
            # 更新索引
            projects = self._load_projects_index()
            projects = [p for p in projects if p['id'] != project_id]
            self._save_projects_index(projects)
            
            return {
                "success": True,
                "message": "Project deleted successfully"
            }
        except Exception as e:
            print(f"Error deleting project: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_image_path(self, project_id: str, image_name: str) -> Optional[Path]:
        """获取图片路径"""
        project_dir = self.projects_dir / project_id
        image_path = project_dir / "images" / image_name
        
        if image_path.exists():
            return image_path
        return None
    
    def auto_annotate_with_model(
        self,
        project_id: str,
        model_path: str,
        confidence: float = 0.25,
        iou_threshold: float = 0.45,
        filter_classes: Optional[List[str]] = None,
        merge_mode: str = "replace"  # replace, append, or smart_merge
    ) -> Dict[str, Any]:
        """
        使用 YOLO 模型自动标注项目图片 (增强版)
        
        参考 Roboflow 的自动标注功能:
        - 支持类别过滤
        - 支持多种合并模式
        - 智能去重
        - 批量处理优化
        
        Args:
            project_id: 项目ID
            model_path: YOLO 模型路径
            confidence: 置信度阈值
            iou_threshold: IOU 阈值
            filter_classes: 只保留指定类别的检测结果
            merge_mode: 标注合并模式 (replace: 替换, append: 追加, smart_merge: 智能合并)
            
        Returns:
            标注结果统计
        """
        project_dir = self.projects_dir / project_id
        if not project_dir.exists():
            return {"success": False, "message": "Project not found"}
        
        try:
            from ultralytics import YOLO
            
            # 加载模型
            model = YOLO(model_path)
            
            # 获取所有图片
            images_dir = project_dir / "images"
            image_files = list(images_dir.glob("*"))
            image_files = [f for f in image_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']]
            
            # 加载现有标注（如果需要合并）
            existing_annotations = {}
            if merge_mode in ["append", "smart_merge"]:
                annotations_file = project_dir / "annotations" / "annotations.json"
                if annotations_file.exists():
                    with open(annotations_file, 'r', encoding='utf-8') as f:
                        existing_annotations = json.load(f)
            
            annotations_dict = {}
            total_detections = 0
            skipped_detections = 0
            class_stats = {}
            
            # 批量推理优化 - 使用更大的batch处理
            print(f"🚀 开始自动标注 {len(image_files)} 张图片...")
            
            # 对每张图片进行推理
            for idx, img_path in enumerate(image_files):
                if (idx + 1) % 10 == 0:
                    print(f"进度: {idx + 1}/{len(image_files)} 张图片已处理")
                
                # YOLO 推理
                results = model.predict(
                    str(img_path),
                    conf=confidence,
                    iou=iou_threshold,
                    verbose=False
                )
                
                # 转换为 supervision Detections
                detections, _ = supervision_service.yolo_results_to_detections(
                    results,
                    class_names=model.names
                )
                
                # 转换为标注格式
                image = cv2.imread(str(img_path))
                h, w = image.shape[:2]
                
                image_annotations = []
                
                for i in range(len(detections)):
                    class_id = detections.class_id[i]
                    class_name = model.names[class_id]
                    
                    # 类别过滤
                    if filter_classes and class_name not in filter_classes:
                        skipped_detections += 1
                        continue
                    
                    xyxy = detections.xyxy[i]
                    confidence_score = detections.confidence[i]
                    
                    # 转换为归一化坐标
                    x = float(xyxy[0] / w)
                    y = float(xyxy[1] / h)
                    width = float((xyxy[2] - xyxy[0]) / w)
                    height = float((xyxy[3] - xyxy[1]) / h)
                    
                    annotation = {
                        'class': class_name,
                        'class_id': int(class_id),
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'confidence': float(confidence_score),
                        'auto_annotated': True  # 标记为自动标注
                    }
                    image_annotations.append(annotation)
                    total_detections += 1
                    
                    # 统计类别
                    class_stats[class_name] = class_stats.get(class_name, 0) + 1
                
                # 合并模式处理
                if merge_mode == "append" and img_path.name in existing_annotations:
                    # 追加模式：保留现有标注，添加新标注
                    image_annotations = existing_annotations[img_path.name] + image_annotations
                elif merge_mode == "smart_merge" and img_path.name in existing_annotations:
                    # 智能合并：去除重复的框，保留高置信度的
                    image_annotations = self._smart_merge_annotations(
                        existing_annotations[img_path.name],
                        image_annotations,
                        iou_threshold=0.5
                    )
                
                annotations_dict[img_path.name] = image_annotations
            
            # 保存标注
            classes = list(model.names.values())
            if filter_classes:
                classes = [c for c in classes if c in filter_classes]
            
            self.save_annotations(project_id, annotations_dict, classes)
            
            return {
                "success": True,
                "message": "Auto annotation completed successfully",
                "total_images": len(image_files),
                "total_detections": total_detections,
                "skipped_detections": skipped_detections,
                "classes": classes,
                "class_statistics": class_stats,
                "merge_mode": merge_mode
            }
            
        except Exception as e:
            print(f"Error in auto annotation: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": str(e)
            }
    
    def _smart_merge_annotations(
        self,
        existing: List[Dict[str, Any]],
        new: List[Dict[str, Any]],
        iou_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        智能合并标注 - 去除重复框，保留高置信度的
        
        Args:
            existing: 现有标注
            new: 新标注
            iou_threshold: IOU阈值，超过此值认为是重复
            
        Returns:
            合并后的标注列表
        """
        def calculate_iou(box1: Dict, box2: Dict) -> float:
            """计算两个框的IOU"""
            x1_min = box1['x']
            y1_min = box1['y']
            x1_max = box1['x'] + box1['width']
            y1_max = box1['y'] + box1['height']
            
            x2_min = box2['x']
            y2_min = box2['y']
            x2_max = box2['x'] + box2['width']
            y2_max = box2['y'] + box2['height']
            
            # 计算交集
            x_min = max(x1_min, x2_min)
            y_min = max(y1_min, y2_min)
            x_max = min(x1_max, x2_max)
            y_max = min(y1_max, y2_max)
            
            if x_max < x_min or y_max < y_min:
                return 0.0
            
            intersection = (x_max - x_min) * (y_max - y_min)
            
            # 计算并集
            area1 = box1['width'] * box1['height']
            area2 = box2['width'] * box2['height']
            union = area1 + area2 - intersection
            
            return intersection / union if union > 0 else 0.0
        
        # 合并后的结果
        merged = list(existing)
        
        for new_ann in new:
            # 检查是否与现有标注重复
            is_duplicate = False
            for i, exist_ann in enumerate(merged):
                # 只比较同类别的框
                if exist_ann['class'] == new_ann['class']:
                    iou = calculate_iou(exist_ann, new_ann)
                    if iou > iou_threshold:
                        is_duplicate = True
                        # 保留置信度更高的
                        if new_ann.get('confidence', 0) > exist_ann.get('confidence', 0):
                            merged[i] = new_ann
                        break
            
            # 如果不是重复的，添加到结果中
            if not is_duplicate:
                merged.append(new_ann)
        
        return merged
    
    def batch_auto_annotate(
        self,
        project_id: str,
        image_names: List[str],
        model_path: str,
        confidence: float = 0.25,
        iou_threshold: float = 0.45
    ) -> Dict[str, Any]:
        """
        批量自动标注指定图片（增量标注）
        
        Args:
            project_id: 项目ID
            image_names: 要标注的图片名称列表
            model_path: 模型路径
            confidence: 置信度阈值
            iou_threshold: IOU阈值
            
        Returns:
            标注结果
        """
        project_dir = self.projects_dir / project_id
        if not project_dir.exists():
            return {"success": False, "message": "Project not found"}
        
        try:
            from ultralytics import YOLO
            
            model = YOLO(model_path)
            images_dir = project_dir / "images"
            
            # 加载现有标注
            project = self.get_project(project_id)
            if not project:
                return {"success": False, "message": "Failed to load project"}
            
            annotations_dict = project.get('annotations', {})
            total_detections = 0
            
            for img_name in image_names:
                img_path = images_dir / img_name
                if not img_path.exists():
                    continue
                
                # YOLO推理
                results = model.predict(
                    str(img_path),
                    conf=confidence,
                    iou=iou_threshold,
                    verbose=False
                )
                
                detections, _ = supervision_service.yolo_results_to_detections(
                    results,
                    class_names=model.names
                )
                
                # 转换标注
                image = cv2.imread(str(img_path))
                h, w = image.shape[:2]
                
                image_annotations = []
                for i in range(len(detections)):
                    class_id = detections.class_id[i]
                    xyxy = detections.xyxy[i]
                    confidence_score = detections.confidence[i]
                    
                    x = float(xyxy[0] / w)
                    y = float(xyxy[1] / h)
                    width = float((xyxy[2] - xyxy[0]) / w)
                    height = float((xyxy[3] - xyxy[1]) / h)
                    
                    annotation = {
                        'class': model.names[class_id],
                        'class_id': int(class_id),
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'confidence': float(confidence_score),
                        'auto_annotated': True
                    }
                    image_annotations.append(annotation)
                    total_detections += 1
                
                annotations_dict[img_name] = image_annotations
            
            # 保存标注
            classes = list(model.names.values())
            self.save_annotations(project_id, annotations_dict, classes)
            
            return {
                "success": True,
                "message": f"Annotated {len(image_names)} images",
                "total_detections": total_detections
            }
            
        except Exception as e:
            print(f"Error in batch auto annotation: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_annotation_statistics(self, project_id: str) -> Dict[str, Any]:
        """
        获取标注统计信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            统计信息
        """
        project = self.get_project(project_id)
        if not project:
            return {"success": False, "message": "Project not found"}
        
        annotations = project.get('annotations', {})
        classes = project.get('classes', [])
        
        total_images = len(project.get('images', []))
        annotated_images = len([k for k, v in annotations.items() if v])
        total_annotations = sum(len(anns) for anns in annotations.values())
        
        # 类别统计
        class_counts = {cls: 0 for cls in classes}
        auto_annotated_count = 0
        manual_annotated_count = 0
        
        for anns in annotations.values():
            for ann in anns:
                class_name = ann.get('class', 'unknown')
                if class_name in class_counts:
                    class_counts[class_name] += 1
                
                if ann.get('auto_annotated', False):
                    auto_annotated_count += 1
                else:
                    manual_annotated_count += 1
        
        return {
            "success": True,
            "total_images": total_images,
            "annotated_images": annotated_images,
            "unannotated_images": total_images - annotated_images,
            "total_annotations": total_annotations,
            "auto_annotated": auto_annotated_count,
            "manual_annotated": manual_annotated_count,
            "class_distribution": class_counts,
            "completion_rate": f"{(annotated_images / total_images * 100):.1f}%" if total_images > 0 else "0%"
        }
    
    def visualize_annotations(
        self,
        project_id: str,
        image_name: str,
        output_dir: Optional[str] = None
    ) -> Optional[Path]:
        """
        使用 supervision 可视化标注
        
        Args:
            project_id: 项目ID
            image_name: 图片名称
            output_dir: 输出目录（可选）
            
        Returns:
            可视化图片路径
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        try:
            # 加载图片
            image_path = self.get_image_path(project_id, image_name)
            if not image_path:
                return None
            
            image = cv2.imread(str(image_path))
            h, w = image.shape[:2]
            
            # 获取标注
            annotations = project['annotations'].get(image_name, [])
            if not annotations:
                return None
            
            # 转换为 supervision Detections
            xyxy_list = []
            class_ids = []
            confidences = []
            
            for ann in annotations:
                # 从归一化坐标转换回像素坐标
                x = ann['x'] * w
                y = ann['y'] * h
                width = ann['width'] * w
                height = ann['height'] * h
                
                x1 = x
                y1 = y
                x2 = x + width
                y2 = y + height
                
                xyxy_list.append([x1, y1, x2, y2])
                class_ids.append(ann.get('class_id', 0))
                confidences.append(ann.get('confidence', 1.0))
            
            detections = sv.Detections(
                xyxy=np.array(xyxy_list),
                class_id=np.array(class_ids),
                confidence=np.array(confidences)
            )
            
            # 生成标签
            labels = [
                f"{project['classes'][class_id]} {conf:.2f}"
                for class_id, conf in zip(class_ids, confidences)
            ]
            
            # 可视化
            annotated_image = supervision_service.annotate_image(
                image,
                detections,
                labels
            )
            
            # 保存
            if output_dir is None:
                output_dir = self.projects_dir / project_id / "visualizations"
            else:
                output_dir = Path(output_dir)
            
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"annotated_{image_name}"
            cv2.imwrite(str(output_path), annotated_image)
            
            return output_path
            
        except Exception as e:
            print(f"Error visualizing annotations: {e}")
            import traceback
            traceback.print_exc()
            return None


# 全局服务实例
annotation_service = AnnotationService()
