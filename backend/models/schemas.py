"""
数据模型定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DetectionResult(BaseModel):
    """检测结果"""
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float] = Field(..., description="[x1, y1, x2, y2]")


class InferenceRequest(BaseModel):
    """推理请求"""
    model_name: Optional[str] = "yolo11n.pt"
    confidence: Optional[float] = 0.25
    iou_threshold: Optional[float] = 0.45
    img_size: Optional[int] = 640


class InferenceResponse(BaseModel):
    """推理响应"""
    success: bool
    message: str
    detections: List[DetectionResult] = []
    inference_time: float
    image_shape: List[int]


class TrainingConfig(BaseModel):
    """训练配置"""
    project_name: str
    dataset_path: str
    model_type: str = "yolo11n"
    epochs: int = 100
    batch_size: int = 16
    img_size: int = 640
    device: str = "cpu"  # cpu 或 cuda
    patience: int = 50
    save_period: int = 10
    pretrained: bool = True
    optimizer: str = "auto"
    lr0: float = 0.01
    lrf: float = 0.01


class TrainingStatus(BaseModel):
    """训练状态"""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float
    current_epoch: int
    total_epochs: int
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class ModelInfo(BaseModel):
    """模型信息"""
    name: str
    path: str
    size: int
    created_at: datetime
    model_type: str
    task: str  # detect, segment, classify, pose
    input_shape: Optional[List[int]] = None
    classes: Optional[List[str]] = None


class DatasetInfo(BaseModel):
    """数据集信息"""
    name: str
    path: str
    num_images: int
    num_classes: int
    classes: List[str]
    split: Dict[str, int] = Field(default_factory=dict)  # train/val/test 数量
    created_at: datetime


class ExportConfig(BaseModel):
    """模型导出配置"""
    model_path: str
    format: str = "onnx"  # onnx, torchscript, coreml, saved_model, pb, tflite, edgetpu, tfjs
    img_size: List[int] = [640, 640]
    batch_size: int = 1
    optimize: bool = False
    half: bool = False  # FP16 量化
    simplify: bool = True  # ONNX 简化
    dynamic: bool = False  # 动态输入
    opset: int = 12  # ONNX opset 版本


class LabelStudioProject(BaseModel):
    """Label Studio 项目"""
    id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    created_at: Optional[datetime] = None


class SystemInfo(BaseModel):
    """系统信息"""
    app_name: str
    version: str
    python_version: str
    ultralytics_version: str
    total_models: int
    total_datasets: int
    gpu_available: bool
    gpu_info: Optional[str] = None
