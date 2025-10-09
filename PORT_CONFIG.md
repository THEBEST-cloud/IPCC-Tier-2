# 端口配置说明 / Port Configuration

## 当前配置 / Current Configuration

- **宿主机端口 / Host Port**: `8080`
- **容器内部端口 / Container Port**: `8000`
- **端口映射 / Port Mapping**: `8080:8000` (宿主机:容器 / Host:Container)

## Docker Compose 配置

在 `docker-compose.yml` 文件中：

```yaml
services:
  web:
    ports:
      - "8080:8000"  # 宿主机端口:容器端口
```

## 访问方式 / Access

### Web 界面 / Web Interface
```
http://localhost:8080
```

### API 文档 / API Documentation
```
http://localhost:8080/docs
```

### API 端点 / API Endpoints
```
http://localhost:8080/api/analyze
http://localhost:8080/api/analyses
http://localhost:8080/health
```

## 说明 / Notes

1. **容器内部**: FastAPI 应用运行在端口 8000
   - **Inside Container**: FastAPI app runs on port 8000

2. **宿主机访问**: 通过端口 8080 访问应用
   - **Host Access**: Access the app via port 8080

3. **端口映射**: Docker 将宿主机的 8080 端口映射到容器的 8000 端口
   - **Port Mapping**: Docker maps host port 8080 to container port 8000

## 修改端口 / Change Port

如果需要修改宿主机端口，编辑 `docker-compose.yml`:
If you need to change the host port, edit `docker-compose.yml`:

```yaml
services:
  web:
    ports:
      - "9000:8000"  # 修改左边的端口号 / Change the left port number
```

然后重启容器 / Then restart the container:
```bash
docker-compose down
docker-compose up -d
```

## 防火墙配置 / Firewall Configuration

如果使用 UFW 防火墙 / If using UFW firewall:

```bash
# 允许端口 8080 / Allow port 8080
sudo ufw allow 8080/tcp

# 查看状态 / Check status
sudo ufw status
```

## 端口检查 / Port Check

检查端口是否被占用 / Check if port is in use:

```bash
# 检查端口 8080 / Check port 8080
sudo lsof -i :8080

# 或使用 netstat / Or use netstat
netstat -tuln | grep 8080
```

## 故障排查 / Troubleshooting

### 端口已被占用 / Port Already in Use

```bash
# 查找占用端口的进程 / Find process using the port
sudo lsof -i :8080

# 停止进程或修改端口配置
# Stop the process or change port configuration
```

### 无法访问应用 / Cannot Access Application

1. 检查容器是否运行 / Check if container is running:
   ```bash
   docker ps | grep reservoir-emissions-tool
   ```

2. 查看容器日志 / View container logs:
   ```bash
   docker-compose logs -f
   ```

3. 测试健康检查 / Test health check:
   ```bash
   curl http://localhost:8080/health
   ```

---

**配置日期 / Configuration Date**: October 8, 2025  
**状态 / Status**: ✅ 已配置 / Configured
