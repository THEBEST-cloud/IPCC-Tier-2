#!/bin/bash

echo "🔄 快速重启服务以应用设置页面..."

# 停止现有容器
echo "1. 停止现有容器..."
docker compose -f docker-compose.china.yml down 2>/dev/null || true

# 重新启动（不重新构建）
echo "2. 重新启动服务..."
docker compose -f docker-compose.china.yml up -d

# 等待服务启动
echo "3. 等待服务启动..."
sleep 10

# 检查状态
echo "4. 检查服务状态..."
if docker compose -f docker-compose.china.yml ps | grep -q "Up"; then
    echo ""
    echo "🎉 服务重启成功！"
    echo ""
    echo "🌐 新增页面："
    echo "   设置页面: http://localhost:8080/settings"
    echo ""
    echo "📋 所有可用页面："
    echo "   登录: http://localhost:8080/login"
    echo "   注册: http://localhost:8080/register"
    echo "   主计算: http://localhost:8080/dashboard"
    echo "   我的项目: http://localhost:8080/projects"
    echo "   方法学说明: http://localhost:8080/methodology"
    echo "   帮助中心: http://localhost:8080/help"
    echo "   个人信息: http://localhost:8080/profile"
    echo "   用户设置: http://localhost:8080/settings"
    echo ""
    echo "✅ 设置页面功能："
    echo "   🔧 账户设置（用户名、邮箱、姓名、机构）"
    echo "   🔒 密码设置（密码强度检测）"
    echo "   ⚙️ 偏好设置（语言、时区、默认分析选项）"
    echo "   🔔 通知设置（邮件通知选项）"
    echo "   💾 保存和重置功能"
else
    echo ""
    echo "❌ 服务启动失败"
    echo ""
    echo "📋 查看详细日志："
    docker compose -f docker-compose.china.yml logs web
fi