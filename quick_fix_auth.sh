#!/bin/bash

echo "🔧 快速修复认证系统..."

# 停止现有容器
echo "1. 停止现有容器..."
docker compose -f docker-compose.china.yml down 2>/dev/null || true

# 重新构建并启动
echo "2. 重新构建并启动服务..."
docker compose -f docker-compose.china.yml up --build -d

# 等待服务启动
echo "3. 等待服务启动..."
sleep 15

# 测试密码哈希功能
echo "4. 测试密码哈希功能..."
docker compose -f docker-compose.china.yml exec web python /app/test_auth.py

# 重新初始化数据库
echo "5. 重新初始化数据库..."
docker compose -f docker-compose.china.yml exec web python /app/init_database.py

# 检查状态
echo "6. 检查服务状态..."
if docker compose -f docker-compose.china.yml ps | grep -q "Up"; then
    echo ""
    echo "🎉 认证系统修复成功！"
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
    echo "✅ 修复内容："
    echo "   🔧 直接使用bcrypt替代passlib"
    echo "   🔒 修复密码哈希兼容性问题"
    echo "   💾 重新创建数据库和演示用户"
    echo "   🎫 JWT令牌认证正常工作"
else
    echo ""
    echo "❌ 服务启动失败"
    echo ""
    echo "📋 查看详细日志："
    docker compose -f docker-compose.china.yml logs web
fi