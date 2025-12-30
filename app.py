"""
OpenCV Platform - 主应用入口
基于 Ultralytics YOLO 的开源计算机视觉平台
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from config.config import settings
from backend.api.routes import router

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于 Ultralytics YOLO 的开源计算机视觉平台，提供数据标注、模型训练、API 部署的完整工作流",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_dir = project_root / "frontend" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 模板引擎
templates_dir = project_root / "frontend"
templates = Jinja2Templates(directory=str(templates_dir))

# 注册 API 路由
app.include_router(router, prefix="/api/v1", tags=["API"])


# ==================== 前端路由 ====================
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/inference", response_class=HTMLResponse)
async def inference_page(request: Request):
    """推理页面"""
    return templates.TemplateResponse("inference.html", {"request": request})


@app.get("/training", response_class=HTMLResponse)
async def training_page(request: Request):
    """训练页面"""
    return templates.TemplateResponse("training.html", {"request": request})


@app.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    """模型管理页面"""
    return templates.TemplateResponse("models.html", {"request": request})


@app.get("/datasets", response_class=HTMLResponse)
async def datasets_page(request: Request):
    """数据集管理页面"""
    return templates.TemplateResponse("datasets.html", {"request": request})


@app.get("/labelstudio", response_class=HTMLResponse)
async def labelstudio_page(request: Request):
    """Label Studio 集成页面"""
    return templates.TemplateResponse("labelstudio.html", {"request": request})


@app.get("/annotation", response_class=HTMLResponse)
async def annotation_page(request: Request):
    """本地数据标注页面"""
    return templates.TemplateResponse("annotation.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║         OpenCV Platform - YOLO Edition                   ║
    ║         开源计算机视觉平台                                ║
    ║                                                          ║
    ╠══════════════════════════════════════════════════════════╣
    ║                                                          ║
    ║  🚀 Server starting...                                   ║
    ║  📍 API: http://localhost:{settings.API_PORT}                       ║
    ║  📖 Docs: http://localhost:{settings.API_PORT}/api/docs            ║
    ║  🏷️  Label Studio: {settings.LABEL_STUDIO_URL}       ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
