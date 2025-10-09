#!/bin/bash

echo "🔧 修复JWT模块错误..."

# 停止现有容器
echo "1. 停止现有容器..."
docker-compose down 2>/dev/null || true

# 清理Docker缓存
echo "2. 清理Docker缓存..."
docker system prune -f 2>/dev/null || true

# 创建必要目录
echo "3. 创建必要目录..."
mkdir -p data
mkdir -p app/static

# 修复权限
echo "4. 修复文件权限..."
chmod -R 755 app/ 2>/dev/null || true
chmod 644 requirements.txt 2>/dev/null || true
chmod 644 Dockerfile 2>/dev/null || true

# 重新构建并启动
echo "5. 重新构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "6. 等待服务启动..."
sleep 30

# 检查状态
echo "7. 检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ 修复成功！服务已启动"
    echo ""
    echo "🌐 访问地址："
    echo "   主页: http://localhost:8080"
    echo "   API文档: http://localhost:8080/docs"
    echo "   健康检查: http://localhost:8080/health"
    echo ""
    echo "🔑 演示账户："
    echo "   用户名: demo"
    echo "   密码: demo123"
else
    echo ""
    echo "❌ 服务启动失败，查看详细日志："
    docker-compose logs web
    echo ""
    echo "🔧 如果问题仍然存在，请尝试："
    echo "   1. 检查Docker内存是否足够"
    echo "   2. 尝试重启Docker服务"
    echo "   3. 检查系统资源使用情况"
fi