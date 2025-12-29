"""
API 路由定义
"""
import sys
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config import settings
from backend.models.schemas import (
    InferenceRequest, InferenceResponse, TrainingConfig,
    TrainingStatus, ModelInfo, DatasetInfo, ExportConfig,
    LabelStudioProject, SystemInfo
)
from backend.services.yolo_service import yolo_service
from backend.services.labelstudio_service import labelstudio_service
from backend.utils.file_utils import allowed_file, save_uploaded_file, get_unique_filename

router = APIRouter()


# ==================== 系统信息 ====================
@router.get("/system/info", response_model=SystemInfo)
async def get_system_info():
    """获取系统信息"""
    import platform
    
    # 获取模型和数据集数量
    models = yolo_service.list_models() if yolo_service else []
    datasets = list(settings.DATASETS_DIR.glob("*/data.yaml"))
    
    # 获取 GPU 信息
    gpu_available, gpu_info = (False, None)
    if yolo_service:
        gpu_available, gpu_info = yolo_service.get_device_info()
    
    # 获取 ultralytics 版本
    ultralytics_version = "N/A"
    try:
        import ultralytics
        ultralytics_version = ultralytics.__version__
    except:
        pass
    
    return SystemInfo(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        python_version=platform.python_version(),
        ultralytics_version=ultralytics_version,
        total_models=len(models),
        total_datasets=len(datasets),
        gpu_available=gpu_available,
        gpu_info=gpu_info
    )


@router.get("/system/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "yolo_service": yolo_service is not None,
        "labelstudio_available": True
    }


# ==================== 推理相关 ====================
@router.post("/inference/image", response_model=InferenceResponse)
async def infer_image(
    file: UploadFile = File(...),
    model_name: Optional[str] = Form(None),
    confidence: Optional[float] = Form(None),
    iou_threshold: Optional[float] = Form(None),
    img_size: Optional[int] = Form(None)
):
    """图像推理"""
    if not yolo_service:
        raise HTTPException(status_code=500, detail="YOLO service not available")
    
    # 验证文件类型
    if not allowed_file(file.filename, ["jpg", "jpeg", "png", "bmp"]):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        # 保存上传文件
        filename = get_unique_filename(str(settings.UPLOADS_DIR), file.filename)
        file_path = settings.UPLOADS_DIR / filename
        save_uploaded_file(file, str(file_path))
        
        # 执行推理
        result = yolo_service.infer(
            image_path=str(file_path),
            model_name=model_name,
            confidence=confidence,
            iou_threshold=iou_threshold,
            img_size=img_size
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inference/batch")
async def infer_batch(
    files: List[UploadFile] = File(...),
    model_name: Optional[str] = Form(None),
    confidence: Optional[float] = Form(None)
):
    """批量推理"""
    if not yolo_service:
        raise HTTPException(status_code=500, detail="YOLO service not available")
    
    results = []
    for file in files:
        if not allowed_file(file.filename, ["jpg", "jpeg", "png", "bmp"]):
            continue
        
        try:
            filename = get_unique_filename(str(settings.UPLOADS_DIR), file.filename)
            file_path = settings.UPLOADS_DIR / filename
            save_uploaded_file(file, str(file_path))
            
            result = yolo_service.infer(
                image_path=str(file_path),
                model_name=model_name,
                confidence=confidence
            )
            results.append({
                "filename": file.filename,
                "result": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"results": results}


# ==================== 训练相关 ====================
@router.post("/training/start")
async def start_training(config: TrainingConfig):
    """开始训练"""
    if not yolo_service:
        raise HTTPException(status_code=500, detail="YOLO service not available")
    
    try:
        task_id = yolo_service.train(config)
        return {
            "success": True,
            "task_id": task_id,
            "message": "Training started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/status/{task_id}", response_model=TrainingStatus)
async def get_training_status(task_id: str):
    """获取训练状态"""
    if not yolo_service:
        raise HTTPException(status_code=500, detail="YOLO service not available")
    
    status = yolo_service.get_training_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return status


@router.get("/training/tasks")
async def list_training_tasks():
    """列出所有训练任务"""
    if not yolo_service:
        raise HTTPException(status_code=500, detail="YOLO service not available")
    
    return {"tasks": list(yolo_service.training_tasks.values())}


# ==================== 模型相关 ====================
@router.get("/models/list", response_model=List[ModelInfo])
async def list_models():
    """列出所有模型"""
    if not yolo_service:
        raise HTTPException(status_code=500, detail="YOLO service not available")
    
    return yolo_service.list_models()


@router.post("/models/export")
async def export_model(config: ExportConfig):
    """导出模型"""
    if not yolo_service:
        raise HTTPException(status_code=500, detail="YOLO service not available")
    
    result = yolo_service.export_model(config)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result


@router.post("/models/upload")
async def upload_model(file: UploadFile = File(...)):
    """上传模型文件"""
    if not file.filename.endswith('.pt'):
        raise HTTPException(status_code=400, detail="Only .pt files are allowed")
    
    try:
        filename = get_unique_filename(str(settings.MODELS_DIR), file.filename)
        file_path = settings.MODELS_DIR / filename
        save_uploaded_file(file, str(file_path))
        
        return {
            "success": True,
            "message": "Model uploaded successfully",
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 数据集相关 ====================
@router.get("/datasets/list")
async def list_datasets():
    """列出所有数据集"""
    datasets = []
    
    for dataset_dir in settings.DATASETS_DIR.iterdir():
        if dataset_dir.is_dir():
            data_yaml = dataset_dir / "data.yaml"
            if data_yaml.exists():
                try:
                    import yaml
                    with open(data_yaml, 'r') as f:
                        data = yaml.safe_load(f)
                    
                    # 统计图像数量
                    num_images = 0
                    images_dir = dataset_dir / "images"
                    if images_dir.exists():
                        num_images = len(list(images_dir.rglob("*.jpg"))) + \
                                    len(list(images_dir.rglob("*.png")))
                    
                    dataset_info = {
                        "name": dataset_dir.name,
                        "path": str(dataset_dir),
                        "num_images": num_images,
                        "num_classes": len(data.get("names", {})),
                        "classes": list(data.get("names", {}).values()),
                        "created_at": datetime.fromtimestamp(dataset_dir.stat().st_ctime).isoformat()
                    }
                    datasets.append(dataset_info)
                except Exception as e:
                    print(f"Error reading dataset {dataset_dir}: {e}")
    
    return {"datasets": datasets}


@router.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """上传数据集（zip 格式）"""
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")
    
    try:
        import zipfile
        
        # 保存上传的 zip 文件
        zip_path = settings.UPLOADS_DIR / file.filename
        save_uploaded_file(file, str(zip_path))
        
        # 解压到数据集目录
        dataset_name = file.filename.replace('.zip', '')
        dataset_path = settings.DATASETS_DIR / dataset_name
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dataset_path)
        
        # 删除 zip 文件
        zip_path.unlink()
        
        return {
            "success": True,
            "message": "Dataset uploaded successfully",
            "dataset_name": dataset_name,
            "path": str(dataset_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Label Studio 集成 ====================
@router.get("/labelstudio/check")
async def check_labelstudio():
    """检查 Label Studio 连接"""
    return labelstudio_service.check_connection()


@router.get("/labelstudio/projects", response_model=List[LabelStudioProject])
async def list_labelstudio_projects():
    """列出 Label Studio 项目"""
    return labelstudio_service.list_projects()


@router.post("/labelstudio/projects/create")
async def create_labelstudio_project(title: str, description: str = ""):
    """创建 Label Studio 项目"""
    project_id = labelstudio_service.create_project(title, description)
    if project_id:
        return {
            "success": True,
            "project_id": project_id,
            "message": "Project created successfully"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to create project")


@router.post("/labelstudio/export/{project_id}")
async def export_labelstudio_annotations(
    project_id: int,
    dataset_name: str,
    format: str = "YOLO"
):
    """导出 Label Studio 标注为 YOLO 格式"""
    dataset_info = labelstudio_service.convert_to_yolo_format(
        project_id,
        str(settings.DATASETS_DIR),
        dataset_name
    )
    
    if dataset_info:
        return {
            "success": True,
            "message": "Annotations exported successfully",
            "dataset": dataset_info
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to export annotations")
