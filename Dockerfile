# OpenCV Platform Dockerfile
FROM python:3.9-slim

LABEL maintainer="OpenCV Platform"
LABEL description="基于 Ultralytics YOLO 的开源计算机视觉平台"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 升级 pip 并安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    requests \
    pyyaml \
    jinja2

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p data/datasets data/models data/exports data/uploads

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/system/health')" || exit 1

# 启动命令
CMD ["python", "app.py"]
