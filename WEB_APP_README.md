# 水库碳核算Web应用程序

基于IPCC Tier 1方法的水库温室气体排放计算系统，提供现代化的Web界面和完整的用户管理功能。

## 🌟 主要功能

### 核心功能
- **温室气体排放计算**：基于IPCC Tier 1方法计算CH₄、CO₂、N₂O排放
- **不确定性分析**：蒙特卡洛模拟评估计算不确定性
- **敏感性分析**：识别对结果影响最大的参数
- **营养状态评估**：基于水质参数自动评估水库营养状态

### 用户系统
- **用户注册/登录**：完整的用户认证系统
- **项目管理**：创建、保存、管理多个计算项目
- **个人信息管理**：用户资料和偏好设置
- **结果导出**：支持PDF报告下载

### 界面特色
- **现代化设计**：基于原型图的专业UI设计
- **响应式布局**：支持桌面和移动设备
- **交互式地图**：可视化位置选择
- **实时反馈**：表单验证和计算进度显示

## 🚀 快速开始

### 使用Docker（推荐）

1. **启动应用**
   ```bash
   ./start_app.sh
   ```

2. **访问应用**
   - 主页：http://localhost:8080
   - API文档：http://localhost:8080/docs

3. **演示账户**
   - 用户名：`demo`
   - 密码：`demo123`

### 手动启动

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动服务**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **访问应用**
   - 主页：http://localhost:8000

## 📱 页面导航

### 主要页面
- **首页** (`/`) - 新建计算项目
- **登录** (`/login`) - 用户登录
- **注册** (`/register`) - 用户注册
- **我的项目** (`/projects`) - 项目管理
- **方法学说明** (`/methodology`) - IPCC方法学文档
- **帮助中心** (`/help`) - 使用帮助和FAQ

### 功能页面
- **个人信息** (`/profile`) - 用户资料管理
- **计算结果** (`/results/{id}`) - 查看分析结果

## 🔧 API接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册

### 分析接口
- `POST /api/analyze` - 执行温室气体排放分析
- `GET /api/analyses` - 获取分析列表
- `GET /api/analyses/{id}` - 获取特定分析结果
- `DELETE /api/analyses/{id}` - 删除分析结果

### 工具接口
- `GET /api/climate-region/{latitude}` - 获取气候区域
- `GET /health` - 健康检查

## 💻 技术栈

### 后端
- **FastAPI** - 现代Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **Pydantic** - 数据验证和序列化
- **JWT** - 用户认证
- **NumPy/SciPy** - 科学计算

### 前端
- **HTML5/CSS3** - 现代化界面
- **JavaScript** - 交互功能
- **Lato字体** - 专业字体
- **Font Awesome** - 图标库
- **Chart.js** - 数据可视化

### 部署
- **Docker** - 容器化部署
- **Docker Compose** - 服务编排
- **SQLite** - 轻量级数据库

## 📊 使用指南

### 1. 创建新项目
1. 访问主页或点击"新建计算"
2. 输入项目名称
3. 选择水库位置（地图或坐标）
4. 填写水质参数（可选）
5. 设置IPCC模型参数
6. 选择分析类型
7. 点击"计算温室气体排放"

### 2. 查看结果
- 排放总量：CH₄、CO₂、N₂O排放量
- 不确定性分析：概率分布和置信区间
- 敏感性分析：参数影响程度排序
- 导出报告：PDF格式下载

### 3. 管理项目
- 在"我的项目"页面查看所有项目
- 按状态筛选（全部、已完成、草稿、进行中）
- 编辑、删除或重新计算项目

## 🔒 安全特性

- **JWT认证**：安全的用户身份验证
- **密码加密**：使用bcrypt加密存储
- **输入验证**：严格的表单数据验证
- **CORS保护**：跨域请求安全控制

## 📈 性能优化

- **异步处理**：FastAPI异步请求处理
- **数据库优化**：SQLAlchemy查询优化
- **静态文件缓存**：CSS/JS文件缓存
- **Docker多阶段构建**：减小镜像体积

## 🐛 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   # 检查Docker状态
   docker-compose ps
   
   # 查看日志
   docker-compose logs
   ```

2. **数据库错误**
   ```bash
   # 重新创建数据库
   rm -rf data/
   docker-compose up --build
   ```

3. **端口冲突**
   ```bash
   # 修改docker-compose.yml中的端口映射
   ports:
     - "8081:8000"  # 改为其他端口
   ```

### 日志查看
```bash
# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs web
```

## 🔄 更新和维护

### 更新应用
```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up --build -d
```

### 数据备份
```bash
# 备份数据库
cp data/reservoir_emissions.db backup/

# 恢复数据库
cp backup/reservoir_emissions.db data/
```

## 📞 技术支持

- **文档**：查看`/help`页面获取详细帮助
- **API文档**：访问`/docs`查看完整API文档
- **问题反馈**：通过GitHub Issues报告问题

## 📄 许可证

本项目基于MIT许可证开源，详见LICENSE文件。

---

**水库碳核算系统 v1.0.0**  
基于IPCC Tier 1方法的专业温室气体排放计算工具