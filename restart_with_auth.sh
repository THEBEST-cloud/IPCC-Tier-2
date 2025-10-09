#!/bin/bash

echo "🔄 重启服务并初始化用户认证系统..."

# 停止现有容器
echo "1. 停止现有容器..."
docker compose -f docker-compose.china.yml down 2>/dev/null || true

# 重新构建并启动
echo "2. 重新构建并启动服务..."
docker compose -f docker-compose.china.yml up --build -d

# 等待服务启动
echo "3. 等待服务启动..."
sleep 15

# 初始化数据库
echo "4. 初始化数据库和用户..."
docker compose -f docker-compose.china.yml exec web python /app/init_database.py

# 检查状态
echo "5. 检查服务状态..."
if docker compose -f docker-compose.china.yml ps | grep -q "Up"; then
    echo ""
    echo "🎉 用户认证系统部署成功！"
    echo ""
    echo "🌐 访问地址："
    echo "   登录页面: http://localhost:8080"
    echo "   注册页面: http://localhost:8080/register"
    echo "   主计算页面: http://localhost:8080/dashboard"
    echo ""
    echo "🔑 演示账户："
    echo "   用户名: demo"
    echo "   密码: demo123"
    echo "   邮箱: demo@example.com"
    echo ""
    echo "✅ 新功能："
    echo "   🔐 真实的用户注册和登录系统"
    echo "   💾 用户数据保存到数据库"
    echo "   🔒 密码加密存储"
    echo "   🎫 JWT令牌认证"
    echo "   👤 用户会话管理"
    echo ""
    echo "📋 测试步骤："
    echo "   1. 访问 http://localhost:8080"
    echo "   2. 使用 demo/demo123 登录"
    echo "   3. 或者注册新账户"
    echo "   4. 所有数据现在都会保存到数据库中"
else
    echo ""
    echo "❌ 服务启动失败"
    echo ""
    echo "📋 查看详细日志："
    docker compose -f docker-compose.china.yml logs web
fi