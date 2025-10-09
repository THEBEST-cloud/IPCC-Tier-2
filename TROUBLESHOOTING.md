# Docker Compose 问题诊断和解决方案

## 问题：`docker-compose up --build -d` 后无法访问 http://localhost:8080

### 🔍 诊断步骤

#### 1. 检查容器状态
```bash
# 查看容器是否正在运行
docker ps

# 查看docker-compose服务状态
docker-compose ps
```

#### 2. 检查端口占用
```bash
# 检查端口8080是否被占用
lsof -i :8080
# 或者
netstat -tulpn | grep :8080
```

#### 3. 查看容器日志
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs web
```

### 🛠️ 解决方案

#### 方案1：清理并重新启动
```bash
# 停止所有容器
docker-compose down

# 清理未使用的容器和镜像
docker system prune -f

# 重新构建并启动
docker-compose up --build -d
```

#### 方案2：检查端口冲突
如果端口8080被占用，修改端口映射：

1. 编辑 `docker-compose.yml`：
```yaml
services:
  web:
    build: .
    ports:
      - "8081:8000"  # 改为8081端口
    # ... 其他配置
```

2. 重新启动：
```bash
docker-compose up --build -d
```

3. 访问新端口：http://localhost:8081

#### 方案3：使用简化的docker-compose配置
创建 `docker-compose-simple.yml`：
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/reservoir_emissions.db
      - SECRET_KEY=your-secret-key-change-in-production
      - PYTHONPATH=/app
    restart: unless-stopped
    container_name: reservoir-carbon-accounting
```

使用简化配置启动：
```bash
docker-compose -f docker-compose-simple.yml up --build -d
```

#### 方案4：检查Docker资源
```bash
# 检查Docker内存使用
docker system df

# 检查Docker磁盘空间
df -h

# 如果空间不足，清理Docker缓存
docker system prune -a
```

#### 方案5：手动启动调试
```bash
# 构建镜像
docker build -t reservoir-app .

# 手动运行容器
docker run -p 8080:8000 \
  -e DATABASE_URL=sqlite:///./data/reservoir_emissions.db \
  -e SECRET_KEY=your-secret-key-change-in-production \
  -e PYTHONPATH=/app \
  -v $(pwd)/data:/app/data \
  reservoir-app
```

### 🔧 常见问题解决

#### 问题1：容器启动失败
**症状**：容器状态显示为 "Exited"
**解决**：
```bash
# 查看详细错误日志
docker-compose logs web

# 检查Dockerfile语法
docker build -t test-build .

# 检查Python依赖
pip install -r requirements.txt
```

#### 问题2：端口无法访问
**症状**：容器运行但无法访问端口
**解决**：
```bash
# 检查防火墙设置
sudo ufw status
sudo ufw allow 8080

# 检查Docker网络
docker network ls
docker network inspect bridge
```

#### 问题3：权限问题
**症状**：文件权限错误
**解决**：
```bash
# 修复文件权限
chmod -R 755 app/
chmod 644 requirements.txt
chmod 644 Dockerfile

# 重新构建
docker-compose up --build -d
```

#### 问题4：内存不足
**症状**：容器启动缓慢或失败
**解决**：
```bash
# 清理Docker缓存
docker system prune -a

# 增加Docker内存限制（在Docker Desktop中设置）
# 或使用更轻量的基础镜像
```

### 📋 完整诊断脚本

创建并运行诊断脚本：
```bash
#!/bin/bash
echo "🔍 开始诊断..."

# 1. 检查Docker状态
echo "1. 检查Docker状态..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行"
    exit 1
fi
echo "✅ Docker正在运行"

# 2. 检查端口占用
echo "2. 检查端口8080..."
if lsof -i :8080 > /dev/null 2>&1; then
    echo "⚠️  端口8080被占用"
    docker stop $(docker ps -q --filter "publish=8080") 2>/dev/null || true
fi

# 3. 清理并重启
echo "3. 清理并重启..."
docker-compose down 2>/dev/null || true
docker-compose up --build -d

# 4. 等待并检查
echo "4. 等待服务启动..."
sleep 15

if docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    echo "访问: http://localhost:8080"
else
    echo "❌ 服务启动失败"
    echo "查看日志: docker-compose logs"
fi
```

### 🚀 快速修复命令

如果以上方案都不行，尝试这个一键修复：
```bash
# 停止所有相关容器
docker stop $(docker ps -q) 2>/dev/null || true

# 清理Docker
docker system prune -f

# 重新构建并启动
docker-compose up --build -d

# 等待30秒
sleep 30

# 检查状态
docker-compose ps
```

### 📞 获取帮助

如果问题仍然存在，请提供以下信息：
1. `docker-compose logs` 的输出
2. `docker ps` 的输出
3. 操作系统和Docker版本
4. 错误信息截图

这样我可以提供更具体的解决方案。