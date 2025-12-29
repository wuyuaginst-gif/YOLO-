// API 请求工具类
const API_BASE = '/api/v1';

class API {
    // 系统信息
    static async getSystemInfo() {
        const response = await fetch(`${API_BASE}/system/info`);
        return response.json();
    }

    static async healthCheck() {
        const response = await fetch(`${API_BASE}/system/health`);
        return response.json();
    }

    // 推理相关
    static async inferImage(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        if (options.model_name) formData.append('model_name', options.model_name);
        if (options.confidence) formData.append('confidence', options.confidence);
        if (options.iou_threshold) formData.append('iou_threshold', options.iou_threshold);
        if (options.img_size) formData.append('img_size', options.img_size);

        const response = await fetch(`${API_BASE}/inference/image`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    }

    static async inferBatch(files, options = {}) {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        
        if (options.model_name) formData.append('model_name', options.model_name);
        if (options.confidence) formData.append('confidence', options.confidence);

        const response = await fetch(`${API_BASE}/inference/batch`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    }

    // 训练相关
    static async startTraining(config) {
        const response = await fetch(`${API_BASE}/training/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        return response.json();
    }

    static async getTrainingStatus(taskId) {
        const response = await fetch(`${API_BASE}/training/status/${taskId}`);
        return response.json();
    }

    static async listTrainingTasks() {
        const response = await fetch(`${API_BASE}/training/tasks`);
        return response.json();
    }

    // 模型相关
    static async listModels() {
        const response = await fetch(`${API_BASE}/models/list`);
        return response.json();
    }

    static async uploadModel(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/models/upload`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    }

    static async exportModel(config) {
        const response = await fetch(`${API_BASE}/models/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        return response.json();
    }

    // 数据集相关
    static async listDatasets() {
        const response = await fetch(`${API_BASE}/datasets/list`);
        return response.json();
    }

    static async uploadDataset(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/datasets/upload`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    }

    // Label Studio 相关
    static async checkLabelStudio() {
        const response = await fetch(`${API_BASE}/labelstudio/check`);
        return response.json();
    }

    static async listLabelStudioProjects() {
        const response = await fetch(`${API_BASE}/labelstudio/projects`);
        return response.json();
    }

    static async createLabelStudioProject(title, description = '') {
        const params = new URLSearchParams({ title, description });
        const response = await fetch(`${API_BASE}/labelstudio/projects/create?${params}`, {
            method: 'POST'
        });
        return response.json();
    }

    static async exportLabelStudioAnnotations(projectId, datasetName, format = 'YOLO') {
        const params = new URLSearchParams({ dataset_name: datasetName, format });
        const response = await fetch(`${API_BASE}/labelstudio/export/${projectId}?${params}`, {
            method: 'POST'
        });
        return response.json();
    }
}

// 工具函数
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}
