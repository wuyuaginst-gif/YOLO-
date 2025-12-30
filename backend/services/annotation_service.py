#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地数据标注服务
"""
import os
import json
import shutil
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from config.config import settings


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


# 全局服务实例
annotation_service = AnnotationService()
