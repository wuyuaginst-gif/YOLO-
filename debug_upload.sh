#!/bin/bash
# 调试文件上传问题

echo "=========================================="
echo "文件上传调试脚本"
echo "=========================================="
echo ""

echo "1. 检查 uploads 目录状态："
echo "----------------------------------------"
docker exec opencv-platform-dev ls -la /app/data/uploads/
echo ""

echo "2. 检查目录权限："
echo "----------------------------------------"
docker exec opencv-platform-dev stat /app/data/uploads/
echo ""

echo "3. 测试文件写入权限："
echo "----------------------------------------"
docker exec opencv-platform-dev python3 << 'PYTHON'
import os
import sys

uploads_dir = '/app/data/uploads/'

print(f"目录: {uploads_dir}")
print(f"存在: {os.path.exists(uploads_dir)}")
print(f"是目录: {os.path.isdir(uploads_dir)}")

# 测试写入
test_file = os.path.join(uploads_dir, 'test_write.txt')
try:
    with open(test_file, 'w') as f:
        f.write('test')
    print(f"✅ 写入测试成功: {test_file}")
    
    # 删除测试文件
    os.remove(test_file)
    print(f"✅ 删除测试文件成功")
except Exception as e:
    print(f"❌ 写入测试失败: {e}")
    import traceback
    traceback.print_exc()

# 检查当前用户
import pwd
uid = os.getuid()
user_info = pwd.getpwuid(uid)
print(f"\n当前用户: {user_info.pw_name} (UID: {uid})")
print(f"主目录: {user_info.pw_dir}")
PYTHON

echo ""
echo "4. 查看容器日志（最近 50 行，查找上传相关）："
echo "----------------------------------------"
docker logs opencv-platform-dev --tail 50 | grep -i -E "(upload|file|save|AI\.png)" || echo "没有找到相关日志"

echo ""
echo "5. 查看所有文件（递归查找 AI.png）："
echo "----------------------------------------"
docker exec opencv-platform-dev find /app/data -name "AI.png" -o -name "*AI*" 2>/dev/null || echo "未找到 AI.png"

echo ""
echo "6. 检查 data 目录的所有子目录："
echo "----------------------------------------"
docker exec opencv-platform-dev find /app/data -type f -name "*.png" -o -name "*.jpg" 2>/dev/null | head -20

echo ""
echo "7. 测试 API 文件上传流程："
echo "----------------------------------------"
docker exec opencv-platform-dev python3 << 'PYTHON'
import sys
sys.path.insert(0, '/app')

try:
    from config.config import settings
    from backend.utils.file_utils import save_uploaded_file, get_unique_filename
    
    print(f"✅ 配置加载成功")
    print(f"   UPLOADS_DIR: {settings.UPLOADS_DIR}")
    print(f"   目录存在: {settings.UPLOADS_DIR.exists()}")
    
    # 模拟文件上传
    import io
    from fastapi import UploadFile
    
    # 创建模拟文件
    content = b"fake image content"
    fake_file = UploadFile(
        filename="test_upload.jpg",
        file=io.BytesIO(content)
    )
    
    # 测试文件保存
    unique_filename = get_unique_filename(str(settings.UPLOADS_DIR), "test_upload.jpg")
    print(f"   生成文件名: {unique_filename}")
    
    file_path = settings.UPLOADS_DIR / unique_filename
    print(f"   保存路径: {file_path}")
    
    # 实际保存
    save_uploaded_file(fake_file, str(file_path))
    
    if file_path.exists():
        print(f"✅ 文件保存成功: {file_path}")
        print(f"   文件大小: {file_path.stat().st_size} bytes")
        # 删除测试文件
        file_path.unlink()
        print(f"✅ 测试文件已清理")
    else:
        print(f"❌ 文件保存失败")
        
except Exception as e:
    import traceback
    print(f"❌ 测试失败: {e}")
    traceback.print_exc()
PYTHON

echo ""
echo "=========================================="
echo "8. 实时监控 uploads 目录（10秒）："
echo "=========================================="
echo "现在请在前端上传一个文件，我会监控目录变化..."
echo ""

# 记录初始文件列表
docker exec opencv-platform-dev ls -1 /app/data/uploads/ > /tmp/before.txt 2>/dev/null

echo "等待 10 秒..."
sleep 10

# 记录新文件列表
docker exec opencv-platform-dev ls -1 /app/data/uploads/ > /tmp/after.txt 2>/dev/null

# 比较
echo "新增的文件："
diff /tmp/before.txt /tmp/after.txt | grep ">" | sed 's/> /  - /' || echo "  没有新文件"

echo ""
echo "=========================================="
echo "调试建议："
echo "=========================================="
echo "如果上传文件后仍然看不到："
echo "1. 检查浏览器开发者工具的 Network 标签"
echo "2. 查看 POST /api/v1/inference/image 请求"
echo "3. 查看请求的 Form Data 是否包含 file"
echo "4. 查看响应状态码和错误信息"
echo ""
echo "运行这个命令查看详细日志："
echo "  docker logs opencv-platform-dev -f"
