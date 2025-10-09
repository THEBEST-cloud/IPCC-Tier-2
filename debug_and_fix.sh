#!/bin/bash

echo "🔍 诊断Docker Compose问题..."

# 检查Docker是否运行
echo "1. 检查Docker状态..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请启动Docker服务"
    exit 1
else
    echo "✅ Docker正在运行"
fi

# 检查端口占用
echo "2. 检查端口8080占用情况..."
if lsof -i :8080 > /dev/null 2>&1; then
    echo "⚠️  端口8080被占用，尝试释放..."
    # 尝试停止可能占用端口的容器
    docker stop $(docker ps -q --filter "publish=8080") 2>/dev/null || true
    sleep 2
fi

# 停止现有容器
echo "3. 停止现有容器..."
docker-compose down 2>/dev/null || true

# 清理可能的残留容器
echo "4. 清理残留容器..."
docker container prune -f 2>/dev/null || true

# 检查Dockerfile
echo "5. 检查Dockerfile..."
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile不存在"
    exit 1
fi

# 检查requirements.txt
echo "6. 检查依赖文件..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt不存在"
    exit 1
fi

# 创建必要的目录
echo "7. 创建必要目录..."
mkdir -p data
mkdir -p app/static

# 修复可能的权限问题
echo "8. 修复权限问题..."
chmod -R 755 app/
chmod 644 requirements.txt
chmod 644 Dockerfile

# 重新构建并启动
echo "9. 重新构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "10. 等待服务启动..."
sleep 15

# 检查容器状态
echo "11. 检查容器状态..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "🌐 访问地址："
    echo "   主页: http://localhost:8080"
    echo "   API文档: http://localhost:8080/docs"
    echo "   健康检查: http://localhost:8080/health"
    echo ""
    echo "📋 如果仍然无法访问，请尝试："
    echo "   1. 检查防火墙设置"
    echo "   2. 尝试其他端口: 修改docker-compose.yml中的端口映射"
    echo "   3. 查看日志: docker-compose logs"
else
    echo "❌ 服务启动失败"
    echo ""
    echo "📋 查看详细日志："
    docker-compose logs
    echo ""
    echo "🔧 常见解决方案："
    echo "   1. 检查端口是否被占用: lsof -i :8080"
    echo "   2. 检查Docker内存是否足够"
    echo "   3. 尝试重启Docker服务"
    echo "   4. 检查防火墙设置"
fi