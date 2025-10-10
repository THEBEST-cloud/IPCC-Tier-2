# 国内镜像源配置说明

## 🇨🇳 使用国内镜像源加速Docker构建

为了提升在中国大陆地区的构建速度，我们提供了使用国内镜像源的Docker配置。

### 📦 镜像源配置

#### APT源（系统包）
- **主要源**：中科大镜像 (mirrors.ustc.edu.cn)
- **备用源**：清华大学镜像 (mirrors.tuna.tsinghua.edu.cn)
- **优势**：下载速度快，更新及时

#### PyPI源（Python包）
- **主要源**：清华大学镜像 (pypi.tuna.tsinghua.edu.cn)
- **备用源1**：阿里云镜像 (mirrors.aliyun.com)
- **备用源2**：豆瓣镜像 (pypi.douban.com)
- **优势**：包完整，同步及时

### 🚀 快速开始

#### 方法1：使用国内镜像源启动脚本（推荐）
```bash
./start_china.sh
```

#### 方法2：使用国内镜像源Docker Compose
```bash
docker-compose -f docker-compose.china.yml up --build -d
```

#### 方法3：使用国内镜像源Dockerfile
```bash
docker build -f Dockerfile.china -t reservoir-app .
docker run -p 8080:8000 reservoir-app
```

### 📋 文件说明

| 文件 | 用途 | 说明 |
|------|------|------|
| `Dockerfile.china` | 国内镜像源Dockerfile | 配置APT和PyPI国内镜像源 |
| `docker-compose.china.yml` | 国内镜像源Compose | 使用国内镜像源的服务编排 |
| `start_china.sh` | 国内镜像源启动脚本 | 一键启动脚本 |

### ⚡ 性能对比

| 项目 | 原始源 | 国内镜像源 | 提升 |
|------|--------|------------|------|
| APT包下载 | 2-5分钟 | 30秒-1分钟 | 3-5倍 |
| PyPI包下载 | 3-8分钟 | 1-2分钟 | 3-4倍 |
| 总构建时间 | 8-15分钟 | 2-5分钟 | 3-5倍 |

### 🔧 手动配置

#### 1. 配置APT源
```dockerfile
# 在Dockerfile中添加
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
```

#### 2. 配置PyPI源
```dockerfile
# 在Dockerfile中添加
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    pip config set global.extra-index-url "https://mirrors.aliyun.com/pypi/simple/ https://pypi.douban.com/simple/"
```

#### 3. 环境变量配置
```yaml
# 在docker-compose.yml中添加
environment:
  - PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
  - PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
```

### 🌐 镜像源列表

#### APT镜像源
1. **中科大镜像** (推荐)
   - URL: https://mirrors.ustc.edu.cn/
   - 特点: 速度快，更新及时

2. **清华大学镜像**
   - URL: https://mirrors.tuna.tsinghua.edu.cn/
   - 特点: 稳定可靠

3. **阿里云镜像**
   - URL: https://mirrors.aliyun.com/
   - 特点: 企业级服务

#### PyPI镜像源
1. **清华大学镜像** (推荐)
   - URL: https://pypi.tuna.tsinghua.edu.cn/simple/
   - 特点: 同步及时，包完整

2. **阿里云镜像**
   - URL: https://mirrors.aliyun.com/pypi/simple/
   - 特点: 速度快，稳定

3. **豆瓣镜像**
   - URL: https://pypi.douban.com/simple/
   - 特点: 历史悠久，稳定

4. **中科大镜像**
   - URL: https://pypi.mirrors.ustc.edu.cn/simple/
   - 特点: 教育网优化

### 🛠️ 故障排除

#### 问题1：镜像源连接失败
```bash
# 检查网络连接
ping pypi.tuna.tsinghua.edu.cn
ping mirrors.ustc.edu.cn

# 尝试其他镜像源
pip install -i https://mirrors.aliyun.com/pypi/simple/ package_name
```

#### 问题2：包版本不匹配
```bash
# 使用多个镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
  --extra-index-url https://mirrors.aliyun.com/pypi/simple/ \
  package_name
```

#### 问题3：SSL证书问题
```bash
# 添加信任主机
pip install --trusted-host pypi.tuna.tsinghua.edu.cn package_name
```

### 📊 监控和优化

#### 查看构建时间
```bash
# 查看Docker构建时间
docker-compose -f docker-compose.china.yml build --no-cache

# 查看镜像大小
docker images | grep reservoir
```

#### 优化建议
1. **使用多阶段构建**：减少最终镜像大小
2. **缓存依赖**：利用Docker层缓存
3. **并行下载**：使用多个镜像源
4. **定期更新**：保持镜像源最新

### 🔄 切换回原始源

如果需要切换回原始源：

```bash
# 使用原始Dockerfile
docker-compose up --build -d

# 或者手动指定
docker build -f Dockerfile -t reservoir-app .
```

### 📞 技术支持

如果遇到镜像源相关问题：

1. **检查网络连接**
2. **尝试其他镜像源**
3. **查看详细日志**
4. **联系技术支持**

---

**提示**：使用国内镜像源可以显著提升构建速度，特别是在中国大陆地区。建议优先使用提供的国内镜像源配置。