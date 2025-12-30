#!/usr/bin/env python3
"""
Ultralytics Solutions 测试脚本
测试所有新增的 Solutions API 端点
"""
import requests
import json
from pathlib import Path

# API 基础 URL
API_BASE = "https://8000-if9qna3nrnlvvcghl27z2-dfc00ec5.sandbox.novita.ai/api/v1"

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_system_health():
    """测试系统健康检查"""
    print_section("1. 测试系统健康检查")
    
    response = requests.get(f"{API_BASE}/system/health")
    data = response.json()
    
    print(f"✅ 状态: {data['status']}")
    print(f"✅ YOLO 服务: {'可用' if data['yolo_service'] else '不可用'}")
    print(f"✅ 时间戳: {data['timestamp']}")
    
    return response.status_code == 200

def test_system_info():
    """测试系统信息"""
    print_section("2. 测试系统信息")
    
    response = requests.get(f"{API_BASE}/system/info")
    data = response.json()
    
    print(f"✅ 应用名称: {data['app_name']}")
    print(f"✅ 版本: {data['version']}")
    print(f"✅ Python 版本: {data['python_version']}")
    print(f"✅ Ultralytics 版本: {data['ultralytics_version']}")
    print(f"✅ GPU 可用: {'是' if data['gpu_available'] else '否'}")
    
    return response.status_code == 200

def test_solutions_list():
    """测试 Solutions 列表"""
    print_section("3. 测试 Solutions 列表")
    
    response = requests.get(f"{API_BASE}/solutions/list")
    data = response.json()
    
    print(f"✅ 总共 {data['total']} 个解决方案:")
    for i, solution in enumerate(data['solutions'], 1):
        print(f"\n  {i}. {solution['title']} ({solution['name']})")
        print(f"     描述: {solution['description']}")
        print(f"     输入类型: {', '.join(solution['input_types'])}")
        print(f"     特性: {', '.join(solution['features'])}")
    
    return response.status_code == 200 and data['total'] == 7

def test_inference():
    """测试基础推理"""
    print_section("4. 测试基础推理 API")
    
    test_image = "data/uploads/test_image.jpg"
    
    if not Path(test_image).exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return False
    
    with open(test_image, 'rb') as f:
        files = {'file': f}
        data = {
            'model_name': 'yolo11n.pt',
            'confidence': 0.25
        }
        
        response = requests.post(
            f"{API_BASE}/inference/image",
            files=files,
            data=data
        )
    
    result = response.json()
    
    print(f"✅ 推理成功: {result['success']}")
    print(f"✅ 推理时间: {result['inference_time']:.4f} 秒")
    print(f"✅ 图像尺寸: {result['image_shape']}")
    print(f"✅ 检测对象数: {len(result['detections'])}")
    
    return response.status_code == 200 and result['success']

def test_distance_calculation():
    """测试距离计算"""
    print_section("5. 测试距离计算 API")
    
    test_image = "data/uploads/test_image.jpg"
    
    if not Path(test_image).exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return False
    
    with open(test_image, 'rb') as f:
        files = {'file': f}
        data = {
            'model_name': 'yolo11n.pt',
            'conf': 0.25
        }
        
        response = requests.post(
            f"{API_BASE}/solutions/distance-calculation",
            files=files,
            data=data
        )
    
    result = response.json()
    
    print(f"✅ 处理成功: {result['success']}")
    print(f"✅ 消息: {result['message']}")
    
    if result.get('results'):
        distances = result['results'].get('distances', [])
        print(f"✅ 距离计算数: {len(distances)}")
        for i, dist in enumerate(distances[:3], 1):  # 只显示前3个
            print(f"   {i}. 对象 {dist['object1_index']} → {dist['object2_index']}: "
                  f"{dist['pixel_distance']:.2f} 像素")
    
    return response.status_code == 200

def test_models_list():
    """测试模型列表"""
    print_section("6. 测试模型列表")
    
    response = requests.get(f"{API_BASE}/models/list")
    models = response.json()
    
    print(f"✅ 找到 {len(models)} 个模型")
    for i, model in enumerate(models[:5], 1):  # 只显示前5个
        print(f"   {i}. {model['name']}")
        print(f"      路径: {model['path']}")
        print(f"      大小: {model['size'] / 1024 / 1024:.2f} MB")
        print(f"      任务类型: {model['task']}")
    
    return response.status_code == 200

def test_datasets_list():
    """测试数据集列表"""
    print_section("7. 测试数据集列表")
    
    response = requests.get(f"{API_BASE}/datasets/list")
    data = response.json()
    
    print(f"✅ 找到 {len(data['datasets'])} 个数据集")
    
    if data['datasets']:
        for i, dataset in enumerate(data['datasets'][:5], 1):
            print(f"   {i}. {dataset['name']}")
            print(f"      图片数: {dataset['num_images']}")
            print(f"      类别数: {dataset['num_classes']}")
    else:
        print("   (暂无数据集)")
    
    return response.status_code == 200

def main():
    """主测试函数"""
    print("\n" + "🚀"*30)
    print("  OpenCV Platform - Ultralytics Solutions 测试")
    print("🚀"*30)
    
    tests = [
        ("系统健康检查", test_system_health),
        ("系统信息", test_system_info),
        ("Solutions 列表", test_solutions_list),
        ("基础推理", test_inference),
        ("距离计算", test_distance_calculation),
        ("模型列表", test_models_list),
        ("数据集列表", test_datasets_list),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ 测试失败: {str(e)}")
            results.append((name, False))
    
    # 打印测试总结
    print_section("测试总结")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n测试结果: {passed}/{total} 通过\n")
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status}  {name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查日志")
    
    print("\n访问以下 URL 查看完整功能：")
    print(f"  🌐 主页: {API_BASE.replace('/api/v1', '')}")
    print(f"  🎯 Solutions: {API_BASE.replace('/api/v1', '/solutions')}")
    print(f"  📖 API 文档: {API_BASE.replace('/api/v1', '/api/docs')}")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
