"""
Label Studio 集成服务
"""
import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not installed. Install with: pip install requests")

from config.config import settings
from backend.models.schemas import LabelStudioProject, DatasetInfo


class LabelStudioService:
    """Label Studio 服务"""
    
    def __init__(self):
        self.base_url = settings.LABEL_STUDIO_URL
        self.api_key = settings.LABEL_STUDIO_API_KEY
        self.headers = {
            "Authorization": f"Token {self.api_key}" if self.api_key else ""
        }
    
    def check_connection(self) -> Dict[str, Any]:
        """检查 Label Studio 连接"""
        if not REQUESTS_AVAILABLE:
            return {"success": False, "message": "requests library not available"}
        
        try:
            response = requests.get(
                f"{self.base_url}/api/health",
                timeout=5
            )
            return {
                "success": response.status_code == 200,
                "message": "Connected to Label Studio" if response.status_code == 200 else "Connection failed",
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }
    
    def list_projects(self) -> List[LabelStudioProject]:
        """列出所有项目"""
        if not REQUESTS_AVAILABLE:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/api/projects",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                projects_data = response.json()
                projects = []
                for proj in projects_data:
                    project = LabelStudioProject(
                        id=proj.get("id"),
                        title=proj.get("title", ""),
                        description=proj.get("description", ""),
                        created_at=datetime.fromisoformat(proj.get("created_at", "").replace("Z", "+00:00")) if proj.get("created_at") else None
                    )
                    projects.append(project)
                return projects
            else:
                print(f"Failed to fetch projects: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []
    
    def create_project(self, title: str, description: str = "") -> Optional[int]:
        """创建项目"""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            data = {
                "title": title,
                "description": description,
                "label_config": self._get_default_label_config()
            }
            
            response = requests.post(
                f"{self.base_url}/api/projects",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                project = response.json()
                return project.get("id")
            else:
                print(f"Failed to create project: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error creating project: {e}")
            return None
    
    def export_annotations(self, project_id: int, export_format: str = "YOLO") -> Optional[bytes]:
        """导出标注数据"""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/api/projects/{project_id}/export",
                headers=self.headers,
                params={"exportType": export_format},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to export annotations: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error exporting annotations: {e}")
            return None
    
    def convert_to_yolo_format(
        self,
        project_id: int,
        output_dir: str,
        dataset_name: str
    ) -> Optional[DatasetInfo]:
        """将 Label Studio 导出转换为 YOLO 格式"""
        try:
            # 导出标注
            export_data = self.export_annotations(project_id, "YOLO")
            if not export_data:
                return None
            
            # 创建数据集目录
            dataset_path = Path(output_dir) / dataset_name
            dataset_path.mkdir(parents=True, exist_ok=True)
            
            # 保存导出数据
            export_file = dataset_path / "export.zip"
            with open(export_file, "wb") as f:
                f.write(export_data)
            
            # 解压
            import zipfile
            with zipfile.ZipFile(export_file, "r") as zip_ref:
                zip_ref.extractall(dataset_path)
            
            # 删除 zip 文件
            export_file.unlink()
            
            # 创建 YOLO 数据集结构
            for split in ["train", "val"]:
                (dataset_path / "images" / split).mkdir(parents=True, exist_ok=True)
                (dataset_path / "labels" / split).mkdir(parents=True, exist_ok=True)
            
            # 统计信息
            num_images = len(list(dataset_path.glob("**/*.jpg"))) + \
                        len(list(dataset_path.glob("**/*.png")))
            
            # 创建 data.yaml
            classes = self._get_classes_from_export(dataset_path)
            data_yaml = {
                "path": str(dataset_path),
                "train": "images/train",
                "val": "images/val",
                "names": {i: name for i, name in enumerate(classes)}
            }
            
            yaml_path = dataset_path / "data.yaml"
            import yaml
            with open(yaml_path, "w") as f:
                yaml.dump(data_yaml, f)
            
            dataset_info = DatasetInfo(
                name=dataset_name,
                path=str(dataset_path),
                num_images=num_images,
                num_classes=len(classes),
                classes=classes,
                split={"train": 0, "val": 0},
                created_at=datetime.now()
            )
            
            return dataset_info
            
        except Exception as e:
            print(f"Error converting to YOLO format: {e}")
            return None
    
    def _get_default_label_config(self) -> str:
        """获取默认标注配置"""
        return """
        <View>
          <Image name="image" value="$image"/>
          <RectangleLabels name="label" toName="image">
            <Label value="object" background="green"/>
          </RectangleLabels>
        </View>
        """
    
    def _get_classes_from_export(self, dataset_path: Path) -> List[str]:
        """从导出数据中提取类别"""
        # 简化版本,实际需要解析标注文件
        classes_file = dataset_path / "classes.txt"
        if classes_file.exists():
            with open(classes_file, "r") as f:
                return [line.strip() for line in f.readlines()]
        return ["object"]


# 全局服务实例
labelstudio_service = LabelStudioService()
