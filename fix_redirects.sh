#!/bin/bash

echo "🔧 修复页面重定向链接..."

# 修复所有HTML文件中的硬编码链接
echo "1. 修复登录页面重定向..."
sed -i 's|window.location.href = '\''index.html'\''|window.location.href = '\''/dashboard'\''|g' /workspace/app/templates/login.html

echo "2. 修复注册页面重定向..."
sed -i 's|window.location.href = '\''login.html'\''|window.location.href = '\''/login'\''|g' /workspace/app/templates/register.html

echo "3. 修复其他可能的硬编码链接..."
# 修复所有页面中的.html链接
for file in /workspace/app/templates/*.html; do
    if [ -f "$file" ]; then
        # 修复相对路径的.html链接
        sed -i 's|href="index.html"|href="/dashboard"|g' "$file"
        sed -i 's|href="login.html"|href="/login"|g' "$file"
        sed -i 's|href="register.html"|href="/register"|g' "$file"
        sed -i 's|href="profile.html"|href="/profile"|g' "$file"
        sed -i 's|href="my-projects.html"|href="/projects"|g' "$file"
        sed -i 's|href="methodology.html"|href="/methodology"|g' "$file"
        sed -i 's|href="help.html"|href="/help"|g' "$file"
        sed -i 's|href="results.html"|href="/results"|g' "$file"
        
        # 修复JavaScript中的重定向
        sed -i 's|window.location.href = '\''index.html'\''|window.location.href = '\''/dashboard'\''|g' "$file"
        sed -i 's|window.location.href = '\''login.html'\''|window.location.href = '\''/login'\''|g' "$file"
        sed -i 's|window.location.href = '\''register.html'\''|window.location.href = '\''/register'\''|g' "$file"
        sed -i 's|window.location.href = '\''profile.html'\''|window.location.href = '\''/profile'\''|g' "$file"
        sed -i 's|window.location.href = '\''my-projects.html'\''|window.location.href = '\''/projects'\''|g' "$file"
        sed -i 's|window.location.href = '\''methodology.html'\''|window.location.href = '\''/methodology'\''|g' "$file"
        sed -i 's|window.location.href = '\''help.html'\''|window.location.href = '\''/help'\''|g' "$file"
        sed -i 's|window.location.href = '\''results.html'\''|window.location.href = '\''/results'\''|g' "$file"
    fi
done

echo "✅ 重定向链接修复完成！"
echo ""
echo "📋 修复内容："
echo "   ✅ 登录成功后跳转到 /dashboard"
echo "   ✅ 注册成功后跳转到 /login"
echo "   ✅ 修复所有硬编码的.html链接"
echo "   ✅ 修复JavaScript中的重定向"
echo ""
echo "🔄 请重新启动服务以应用更改："
echo "   docker compose -f docker compose.china.yml restart"