#!/bin/bash

echo "🚀 启动修复后的水库碳核算系统..."

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

# 显示修复的问题
echo "5. 已修复的问题："
echo "   ✅ 更新了requirements.txt，使用PyJWT替代python-jose"
echo "   ✅ 修复了JWT模块导入错误"
echo "   ✅ 优化了Docker配置"

# 重新构建并启动
echo "6. 重新构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "7. 等待服务启动（这可能需要几分钟）..."
echo "   正在安装依赖和启动服务..."

# 显示进度
for i in {1..30}; do
    echo -n "."
    sleep 2
done
echo ""

# 检查状态
echo "8. 检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "🎉 修复成功！服务已启动"
    echo ""
    echo "🌐 访问地址："
    echo "   主页: http://localhost:8080"
    echo "   API文档: http://localhost:8080/docs"
    echo "   健康检查: http://localhost:8080/health"
    echo ""
    echo "📋 功能页面："
    echo "   登录: http://localhost:8080/login"
    echo "   注册: http://localhost:8080/register"
    echo "   我的项目: http://localhost:8080/projects"
    echo "   方法学说明: http://localhost:8080/methodology"
    echo "   帮助中心: http://localhost:8080/help"
    echo ""
    echo "🔑 演示账户："
    echo "   用户名: demo"
    echo "   密码: demo123"
    echo ""
    echo "📊 查看日志: docker-compose logs -f"
    echo "🛑 停止服务: docker-compose down"
else
    echo ""
    echo "❌ 服务启动失败"
    echo ""
    echo "📋 查看详细日志："
    docker-compose logs web
    echo ""
    echo "🔧 如果问题仍然存在，请尝试："
    echo "   1. 等待更长时间（首次启动需要下载依赖）"
    echo "   2. 检查Docker内存是否足够（建议至少2GB）"
    echo "   3. 检查网络连接（需要下载Python包）"
    echo "   4. 尝试手动启动: docker-compose up --build"
fi