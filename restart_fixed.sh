#!/bin/bash

echo "🔄 重启修复后的服务..."

# 停止现有容器
echo "1. 停止现有容器..."
docker compose -f docker compose.china.yml down 2>/dev/null || true

# 重新构建并启动
echo "2. 重新构建并启动服务..."
docker compose -f docker compose.china.yml up --build -d

# 等待服务启动
echo "3. 等待服务启动..."
sleep 15

# 检查状态
echo "4. 检查服务状态..."
if docker compose -f docker compose.china.yml ps | grep -q "Up"; then
    echo ""
    echo "🎉 服务重启成功！"
    echo ""
    echo "🌐 访问地址："
    echo "   登录页面: http://localhost:8080"
    echo "   主计算页面: http://localhost:8080/dashboard"
    echo "   API文档: http://localhost:8080/docs"
    echo ""
    echo "📋 功能页面："
    echo "   登录: http://localhost:8080/login"
    echo "   注册: http://localhost:8080/register"
    echo "   我的项目: http://localhost:8080/projects"
    echo "   方法学说明: http://localhost:8080/methodology"
    echo "   帮助中心: http://localhost:8080/help"
    echo "   个人信息: http://localhost:8080/profile"
    echo ""
    echo "🔑 演示账户："
    echo "   用户名: demo"
    echo "   密码: demo123"
    echo ""
    echo "✅ 修复内容："
    echo "   🏠 首页现在重定向到登录页面"
    echo "   🔗 所有导航链接已修复"
    echo "   📁 模板文件路径已修复"
    echo "   🎯 404错误已解决"
else
    echo ""
    echo "❌ 服务启动失败"
    echo ""
    echo "📋 查看详细日志："
    docker compose -f docker compose.china.yml logs web
fi