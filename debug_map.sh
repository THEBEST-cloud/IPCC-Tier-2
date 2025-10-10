#!/bin/bash

echo "🔍 地图功能诊断脚本"
echo "===================="
echo ""

# 检查服务状态
echo "1. 检查服务状态..."
if docker compose -f docker-compose.china.yml ps | grep -q "Up"; then
    echo "✅ 服务正在运行"
else
    echo "❌ 服务未运行"
    echo "请先启动服务: docker compose -f docker-compose.china.yml up -d"
    exit 1
fi

echo ""
echo "2. 检查地图相关文件..."

# 检查HTML文件
if [ -f "/workspace/app/templates/index.html" ]; then
    echo "✅ index.html 存在"
    
    # 检查Leaflet CSS
    if grep -q "leaflet@1.9.4/dist/leaflet.css" /workspace/app/templates/index.html; then
        echo "✅ Leaflet CSS 已包含"
    else
        echo "❌ Leaflet CSS 未找到"
    fi
    
    # 检查Leaflet JS
    if grep -q "leaflet@1.9.4/dist/leaflet.js" /workspace/app/templates/index.html; then
        echo "✅ Leaflet JS 已包含"
    else
        echo "❌ Leaflet JS 未找到"
    fi
    
    # 检查地图容器
    if grep -q 'id="map"' /workspace/app/templates/index.html; then
        echo "✅ 地图容器已定义"
    else
        echo "❌ 地图容器未找到"
    fi
else
    echo "❌ index.html 不存在"
fi

# 检查CSS文件
if [ -f "/workspace/app/static/style.css" ]; then
    echo "✅ style.css 存在"
    
    if grep -q ".interactive-map" /workspace/app/static/style.css; then
        echo "✅ 地图样式已定义"
    else
        echo "❌ 地图样式未找到"
    fi
else
    echo "❌ style.css 不存在"
fi

# 检查JS文件
if [ -f "/workspace/app/static/app.js" ]; then
    echo "✅ app.js 存在"
    
    if grep -q "initializeMap" /workspace/app/static/app.js; then
        echo "✅ 地图初始化函数已定义"
    else
        echo "❌ 地图初始化函数未找到"
    fi
else
    echo "❌ app.js 不存在"
fi

echo ""
echo "3. 测试地图功能..."

# 创建测试页面
echo "创建地图测试页面..."
cat > /workspace/map_test.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>地图测试</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        #map { height: 300px; width: 100%; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h2>地图加载测试</h2>
    <div id="map"></div>
    <div id="status"></div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const status = document.getElementById('status');
        
        if (typeof L === 'undefined') {
            status.innerHTML = '<p style="color: red;">❌ Leaflet库加载失败</p>';
        } else {
            status.innerHTML = '<p style="color: green;">✅ Leaflet库加载成功</p>';
            
            try {
                const map = L.map('map').setView([39.9042, 116.4074], 10);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                L.marker([39.9042, 116.4074]).addTo(map).bindPopup('北京').openPopup();
                status.innerHTML += '<p style="color: green;">✅ 地图创建成功</p>';
            } catch (error) {
                status.innerHTML += '<p style="color: red;">❌ 地图创建失败: ' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>
EOF

echo "✅ 测试页面已创建: /workspace/map_test.html"

echo ""
echo "4. 诊断建议..."
echo ""
echo "如果地图仍然不显示，请尝试以下步骤："
echo ""
echo "🔧 修复步骤："
echo "1. 重启服务:"
echo "   docker compose -f docker-compose.china.yml restart"
echo ""
echo "2. 检查浏览器控制台:"
echo "   - 打开浏览器开发者工具 (F12)"
echo "   - 查看Console标签页的错误信息"
echo "   - 查看Network标签页确认Leaflet库是否加载成功"
echo ""
echo "3. 测试地图功能:"
echo "   - 访问 http://localhost:8080/map_test.html"
echo "   - 如果测试页面正常显示地图，说明Leaflet库工作正常"
echo ""
echo "4. 检查网络连接:"
echo "   - 确保服务器能访问 unpkg.com"
echo "   - 尝试使用国内CDN镜像"
echo ""
echo "5. 清除浏览器缓存:"
echo "   - 按 Ctrl+F5 强制刷新页面"
echo "   - 或清除浏览器缓存后重新访问"
echo ""
echo "📋 常见问题："
echo "   - Leaflet库加载失败 → 检查网络连接"
echo "   - 地图容器高度为0 → 检查CSS样式"
echo "   - JavaScript错误 → 检查控制台错误信息"
echo "   - 地图显示空白 → 检查瓦片服务连接"