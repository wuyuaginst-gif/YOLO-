"""
YOLO 模型服务
"""
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from PIL import Image

try:
    from ultralytics import YOLO
    import torch
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    print("Warning: ultralytics not installed. Install with: pip install ultralytics")

from config.config import settings
from backend.models.schemas import (
    DetectionResult, InferenceResponse, TrainingConfig,
    TrainingStatus, ModelInfo, ExportConfig
)


class YOLOService:
    """YOLO 模型服务"""
    
    def __init__(self):
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError("Ultralytics YOLO is not installed")
        
        self.models: Dict[str, YOLO] = {}
        self.training_tasks: Dict[str, TrainingStatus] = {}
        
    def load_model(self, model_name: str) -> YOLO:
        """加载模型"""
        if model_name in self.models:
            return self.models[model_name]
        
        model_path = settings.MODELS_DIR / model_name
        
        # 如果本地不存在,尝试下载预训练模型
        if not model_path.exists():
            try:
                print(f"Downloading pretrained model: {model_name}")
                model = YOLO(model_name)
                self.models[model_name] = model
                return model
            except Exception as e:
                raise FileNotFoundError(f"Model {model_name} not found and download failed: {e}")
        
        model = YOLO(str(model_path))
        self.models[model_name] = model
        return model
    
    def infer(
        self,
        image_path: str,
        model_name: str = None,
        confidence: float = None,
        iou_threshold: float = None,
        img_size: int = None
    ) -> InferenceResponse:
        """执行推理"""
        try:
            start_time = time.time()
            
            # 使用默认值
            model_name = model_name or settings.DEFAULT_MODEL
            confidence = confidence or settings.CONFIDENCE_THRESHOLD
            iou_threshold = iou_threshold or settings.IOU_THRESHOLD
            img_size = img_size or settings.DEFAULT_IMG_SIZE
            
            # 加载模型
            model = self.load_model(model_name)
            
            # 执行推理
            results = model.predict(
                source=image_path,
                conf=confidence,
                iou=iou_threshold,
                imgsz=img_size,
                verbose=False
            )
            
            # 解析结果
            detections = []
            if len(results) > 0:
                result = results[0]
                boxes = result.boxes
                
                for i in range(len(boxes)):
                    box = boxes[i]
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()
                    
                    detection = DetectionResult(
                        class_id=cls_id,
                        class_name=model.names[cls_id],
                        confidence=conf,
                        bbox=xyxy
                    )
                    detections.append(detection)
            
            inference_time = time.time() - start_time
            
            # 获取图像尺寸
            img = Image.open(image_path)
            image_shape = [img.height, img.width, 3]
            
            return InferenceResponse(
                success=True,
                message="Inference completed successfully",
                detections=detections,
                inference_time=inference_time,
                image_shape=image_shape
            )
            
        except Exception as e:
            return InferenceResponse(
                success=False,
                message=f"Inference failed: {str(e)}",
                detections=[],
                inference_time=0.0,
                image_shape=[0, 0, 0]
            )
    
    def train(self, config: TrainingConfig) -> str:
        """开始训练"""
        task_id = f"train_{int(time.time())}"
        
        # 创建训练状态
        status = TrainingStatus(
            task_id=task_id,
            status="pending",
            progress=0.0,
            current_epoch=0,
            total_epochs=config.epochs,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.training_tasks[task_id] = status
        
        try:
            # 加载基础模型
            model_type = config.model_type or "yolov8n"
            if config.pretrained:
                model = YOLO(f"{model_type}.pt")
            else:
                model = YOLO(f"{model_type}.yaml")
            
            # 更新状态
            status.status = "running"
            status.updated_at = datetime.now()
            
            # 开始训练
            results = model.train(
                data=config.dataset_path,
                epochs=config.epochs,
                batch=config.batch_size,
                imgsz=config.img_size,
                device=config.device,
                patience=config.patience,
                save_period=config.save_period,
                project=str(settings.MODELS_DIR / config.project_name),
                name="train",
                exist_ok=True,
                pretrained=config.pretrained,
                optimizer=config.optimizer,
                lr0=config.lr0,
                lrf=config.lrf,
                verbose=True
            )
            
            # 训练完成
            status.status = "completed"
            status.progress = 100.0
            status.current_epoch = config.epochs
            status.metrics = {
                "final_metrics": results.results_dict if hasattr(results, 'results_dict') else {}
            }
            status.updated_at = datetime.now()
            
        except Exception as e:
            status.status = "failed"
            status.error_message = str(e)
            status.updated_at = datetime.now()
        
        return task_id
    
    def get_training_status(self, task_id: str) -> Optional[TrainingStatus]:
        """获取训练状态"""
        return self.training_tasks.get(task_id)
    
    def export_model(self, config: ExportConfig) -> Dict[str, Any]:
        """导出模型"""
        try:
            model = YOLO(config.model_path)
            
            export_path = model.export(
                format=config.format,
                imgsz=config.img_size,
                batch=config.batch_size,
                optimize=config.optimize,
                half=config.half,
                simplify=config.simplify,
                dynamic=config.dynamic,
                opset=config.opset
            )
            
            return {
                "success": True,
                "message": "Model exported successfully",
                "export_path": str(export_path)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Export failed: {str(e)}",
                "export_path": None
            }
    
    def list_models(self) -> List[ModelInfo]:
        """列出所有模型"""
        models = []
        models_dir = settings.MODELS_DIR
        
        for model_file in models_dir.glob("**/*.pt"):
            try:
                stat = model_file.stat()
                
                # 尝试加载模型获取信息
                try:
                    model = YOLO(str(model_file))
                    task = model.task
                    classes = list(model.names.values()) if hasattr(model, 'names') else []
                except:
                    task = "unknown"
                    classes = []
                
                info = ModelInfo(
                    name=model_file.name,
                    path=str(model_file),
                    size=stat.st_size,
                    created_at=datetime.fromtimestamp(stat.st_ctime),
                    model_type="yolo",
                    task=task,
                    classes=classes
                )
                models.append(info)
            except Exception as e:
                print(f"Error reading model {model_file}: {e}")
                continue
        
        return models
    
    def get_device_info(self) -> Tuple[bool, Optional[str]]:
        """获取设备信息"""
        try:
            gpu_available = torch.cuda.is_available()
            gpu_info = None
            if gpu_available:
                gpu_info = torch.cuda.get_device_name(0)
            return gpu_available, gpu_info
        except:
            return False, None


# 全局服务实例
yolo_service = YOLOService() if ULTRALYTICS_AVAILABLE else None
