#!/bin/bash

# 水库碳核算系统启动脚本

echo "🌊 启动水库碳核算系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建数据目录
mkdir -p data

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
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
    echo "❌ 服务启动失败，请检查日志："
    docker-compose logs
    exit 1
fi