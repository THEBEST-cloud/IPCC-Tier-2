#!/bin/bash

echo "🔧 修复页面导航链接..."

# 更新所有HTML文件中的导航链接
echo "1. 更新导航链接..."

# 更新my-projects.html
sed -i 's|href="index.html"|href="/dashboard"|g' /workspace/app/templates/my-projects.html
sed -i 's|href="my-projects.html"|href="/projects"|g' /workspace/app/templates/my-projects.html
sed -i 's|href="methodology.html"|href="/methodology"|g' /workspace/app/templates/my-projects.html
sed -i 's|href="help.html"|href="/help"|g' /workspace/app/templates/my-projects.html

# 更新methodology.html
sed -i 's|href="index.html"|href="/dashboard"|g' /workspace/app/templates/methodology.html
sed -i 's|href="my-projects.html"|href="/projects"|g' /workspace/app/templates/methodology.html
sed -i 's|href="methodology.html"|href="/methodology"|g' /workspace/app/templates/methodology.html
sed -i 's|href="help.html"|href="/help"|g' /workspace/app/templates/methodology.html

# 更新help.html
sed -i 's|href="index.html"|href="/dashboard"|g' /workspace/app/templates/help.html
sed -i 's|href="my-projects.html"|href="/projects"|g' /workspace/app/templates/help.html
sed -i 's|href="methodology.html"|href="/methodology"|g' /workspace/app/templates/help.html
sed -i 's|href="help.html"|href="/help"|g' /workspace/app/templates/help.html

# 更新profile.html
sed -i 's|href="index.html"|href="/dashboard"|g' /workspace/app/templates/profile.html
sed -i 's|href="my-projects.html"|href="/projects"|g' /workspace/app/templates/profile.html
sed -i 's|href="methodology.html"|href="/methodology"|g' /workspace/app/templates/profile.html
sed -i 's|href="help.html"|href="/help"|g' /workspace/app/templates/profile.html

# 更新results.html
sed -i 's|href="index.html"|href="/dashboard"|g' /workspace/app/templates/results.html
sed -i 's|href="my-projects.html"|href="/projects"|g' /workspace/app/templates/results.html
sed -i 's|href="methodology.html"|href="/methodology"|g' /workspace/app/templates/results.html
sed -i 's|href="help.html"|href="/help"|g' /workspace/app/templates/results.html

# 更新register.html
sed -i 's|href="login.html"|href="/login"|g' /workspace/app/templates/register.html
sed -i 's|href="index.html"|href="/dashboard"|g' /workspace/app/templates/register.html

# 更新login.html
sed -i 's|href="register.html"|href="/register"|g' /workspace/app/templates/login.html
sed -i 's|href="index.html"|href="/dashboard"|g' /workspace/app/templates/login.html

echo "2. 更新用户下拉菜单链接..."

# 更新所有页面的用户下拉菜单
for file in /workspace/app/templates/*.html; do
    if [ -f "$file" ]; then
        sed -i 's|href="profile.html"|href="/profile"|g' "$file"
        sed -i 's|href="my-projects.html"|href="/projects"|g' "$file"
        sed -i 's|href="settings.html"|href="/settings"|g' "$file"
        sed -i 's|href="login.html"|href="/login"|g' "$file"
    fi
done

echo "3. 更新快速链接..."

# 更新help.html中的快速链接
sed -i 's|href="index.html"|href="/dashboard"|g' /workspace/app/templates/help.html
sed -i 's|href="methodology.html"|href="/methodology"|g' /workspace/app/templates/help.html
sed -i 's|href="my-projects.html"|href="/projects"|g' /workspace/app/templates/help.html
sed -i 's|href="results.html"|href="/results"|g' /workspace/app/templates/help.html

echo "✅ 导航链接修复完成！"
echo ""
echo "📋 修复内容："
echo "   ✅ 更新了所有页面的导航链接"
echo "   ✅ 修复了用户下拉菜单链接"
echo "   ✅ 更新了快速链接"
echo "   ✅ 统一使用相对路径"
echo ""
echo "🔄 请重新启动服务以应用更改："
echo "   docker-compose -f docker-compose.china.yml restart"