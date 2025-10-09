#!/bin/bash

echo "🇨🇳 使用国内镜像源启动水库碳核算系统..."

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

# 停止现有容器
echo "1. 停止现有容器..."
docker-compose -f docker-compose.china.yml down 2>/dev/null || true

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
chmod 644 Dockerfile.china 2>/dev/null || true

# 显示镜像源配置
echo "5. 镜像源配置："
echo "   📦 APT源: 中科大镜像 (mirrors.ustc.edu.cn)"
echo "   🐍 PyPI源: 清华大学镜像 (pypi.tuna.tsinghua.edu.cn)"
echo "   🔄 备用源: 阿里云镜像 (mirrors.aliyun.com)"
echo "   📚 备用源: 豆瓣镜像 (pypi.douban.com)"

# 构建并启动服务
echo "6. 构建并启动服务（使用国内镜像源）..."
docker-compose -f docker-compose.china.yml up --build -d

# 等待服务启动
echo "7. 等待服务启动..."
echo "   ⏳ 正在下载依赖包（使用国内镜像源，速度更快）..."

# 显示进度
for i in {1..20}; do
    echo -n "."
    sleep 3
done
echo ""

# 检查状态
echo "8. 检查服务状态..."
if docker-compose -f docker-compose.china.yml ps | grep -q "Up"; then
    echo ""
    echo "🎉 启动成功！使用国内镜像源构建完成"
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
    echo "📊 查看日志: docker-compose -f docker-compose.china.yml logs -f"
    echo "🛑 停止服务: docker-compose -f docker-compose.china.yml down"
    echo ""
    echo "✅ 使用国内镜像源的优势："
    echo "   🚀 构建速度提升 3-5 倍"
    echo "   🌐 网络连接更稳定"
    echo "   💰 节省带宽成本"
else
    echo ""
    echo "❌ 服务启动失败"
    echo ""
    echo "📋 查看详细日志："
    docker-compose -f docker-compose.china.yml logs web
    echo ""
    echo "🔧 如果问题仍然存在，请尝试："
    echo "   1. 检查网络连接"
    echo "   2. 等待更长时间（首次构建需要下载依赖）"
    echo "   3. 检查Docker内存是否足够"
    echo "   4. 尝试使用原始Dockerfile: docker-compose up --build -d"
fi