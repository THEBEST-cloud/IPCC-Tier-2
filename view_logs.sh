#!/bin/bash

echo "📋 后端日志查看工具"
echo "===================="
echo ""

# 检查服务状态
echo "🔍 检查服务状态..."
if docker compose -f docker-compose.china.yml ps | grep -q "Up"; then
    echo "✅ 服务正在运行"
    echo ""
    
    # 显示菜单
    echo "请选择要查看的日志类型："
    echo "1. 实时日志（推荐）"
    echo "2. 最近100行日志"
    echo "3. 最近50行日志"
    echo "4. 最近30分钟日志"
    echo "5. 最近1小时日志"
    echo "6. 查看容器状态"
    echo "7. 进入容器内部"
    echo "8. 退出"
    echo ""
    
    read -p "请输入选项 (1-8): " choice
    
    case $choice in
        1)
            echo "📊 显示实时日志（按 Ctrl+C 退出）..."
            echo "=========================================="
            docker compose -f docker-compose.china.yml logs -f web
            ;;
        2)
            echo "📊 显示最近100行日志..."
            echo "=========================================="
            docker compose -f docker-compose.china.yml logs --tail=100 web
            ;;
        3)
            echo "📊 显示最近50行日志..."
            echo "=========================================="
            docker compose -f docker-compose.china.yml logs --tail=50 web
            ;;
        4)
            echo "📊 显示最近30分钟日志..."
            echo "=========================================="
            docker compose -f docker-compose.china.yml logs --since=30m web
            ;;
        5)
            echo "📊 显示最近1小时日志..."
            echo "=========================================="
            docker compose -f docker-compose.china.yml logs --since=1h web
            ;;
        6)
            echo "📊 容器状态..."
            echo "=========================================="
            docker compose -f docker-compose.china.yml ps
            ;;
        7)
            echo "📊 进入容器内部..."
            echo "=========================================="
            echo "提示：在容器内可以使用以下命令："
            echo "  - ps aux | grep python    # 查看Python进程"
            echo "  - netstat -tlnp           # 查看端口监听"
            echo "  - cat /app/logs/*.log     # 查看日志文件（如果有）"
            echo "  - exit                    # 退出容器"
            echo ""
            docker compose -f docker-compose.china.yml exec web bash
            ;;
        8)
            echo "👋 退出日志查看工具"
            exit 0
            ;;
        *)
            echo "❌ 无效选项，请重新运行脚本"
            exit 1
            ;;
    esac
else
    echo "❌ 服务未运行"
    echo ""
    echo "请先启动服务："
    echo "  docker compose -f docker-compose.china.yml up -d"
    echo ""
    echo "或者使用启动脚本："
    echo "  ./quick_restart.sh"
fi