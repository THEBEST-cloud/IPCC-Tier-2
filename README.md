# 水库温室气体排放计算工具 (IPCC Tier-2)

基于IPCC Tier-2方法的水库温室气体排放计算工具，集成了不确定性分析和敏感性分析功能。

## 🌟 主要功能

- **IPCC Tier-2方法**: 基于IPCC指南的水库温室气体排放计算
- **自动气候区域识别**: 根据地理坐标（纬度/经度）自动确定气候区域
- **营养状态评估**: 支持不同营养状态的排放计算
- **不确定性分析**: 基于蒙特卡洛模拟的不确定性分析
- **敏感性分析**: 使用相关性方法识别最具影响力的参数
- **现代化Web界面**: 响应式、用户友好的界面，实时显示结果
- **Docker部署**: 容器化部署，便于安装和使用

## 📊 方法学

### 计算的温室气体
- **甲烷 (CH₄)**: 厌氧分解产生的主要温室气体
- **二氧化碳 (CO₂)**: 有机物氧化产生

### 气候区域
工具根据纬度自动确定气候区域:
- **热带**: 0° 至 23.5°
- **亚热带**: 23.5° 至 35°
- **温带**: 35° 至 60°
- **寒带**: 60° 至 90°

### 营养状态
支持不同的营养状态评估:
- **贫营养**: 低营养水平
- **中营养**: 中等营养水平
- **富营养**: 高营养水平
- **超富营养**: 极高营养水平

## 🚀 快速开始

### 前提条件
- 安装了Docker和Docker Compose
- 至少512MB可用RAM
- 端口8000可用

### 安装和启动

1. **克隆或下载项目文件**

2. **进入项目目录:**
   ```bash
   cd /path/to/IPCC-Tier-2
   ```

3. **构建并启动Docker容器:**
   ```bash
   docker-compose up --build -d
   ```

4. **访问应用程序:**
   打开浏览器并访问:
   ```
   http://localhost:8000
   ```

### 常用命令

```bash
# 构建并启动容器（首次或代码更改后）
docker-compose up --build -d

# 启动现有容器
docker-compose start

# 停止容器
docker-compose stop

# 查看日志
docker-compose logs -f

# 停止并移除容器
docker-compose down
```

## 📖 Usage Guide

### 1. Basic Analysis

**Required Inputs:**
- Latitude (-90 to 90)
- Longitude (-180 to 180)
- Surface Area (km²)

**Optional Inputs:**
- Reservoir age (years)
- Mean depth (m)

### 2. Water Quality Data (Optional)

Provide any of the following to improve trophic status assessment:
- Total Phosphorus (mg/L)
- Total Nitrogen (mg/L)
- Chlorophyll-a (μg/L)
- Secchi Depth (m)

### 3. Custom Emission Factors (Optional)

Override default emission factors:
- CH₄ Emission Factor (kg/km²/yr)
- CO₂ Emission Factor (kg/km²/yr)
- N₂O Emission Factor (kg/km²/yr)

### 4. Analysis Options

- **Uncertainty Analysis**: Enable Monte Carlo simulation (checked by default)
- **Sensitivity Analysis**: Identify influential parameters (checked by default)
- **Iterations**: Set number of Monte Carlo iterations (100-10,000, default: 1,000)

## 🔬 Analysis Results

### Emission Calculations
- Total annual emissions for CH₄, CO₂, and N₂O
- CO₂ equivalent emissions using GWP values (CH₄: 28, N₂O: 265)
- Emission factors used for calculations

### Uncertainty Analysis
- Mean and standard deviation
- 95% confidence intervals
- Percentiles (5th, 25th, 50th, 75th, 95th)
- Detailed statistics for all gases

### Sensitivity Analysis
- Parameter rankings by influence
- Pearson and Spearman correlation coefficients
- Visual representation of parameter importance

## 🌐 API Documentation

### Endpoints

#### Analyze Reservoir
```http
POST /api/analyze
Content-Type: application/json

{
  "latitude": 45.5,
  "longitude": -73.5,
  "surface_area": 100.0,
  "reservoir_age": 10,
  "water_quality": {
    "total_phosphorus": 0.02,
    "chlorophyll_a": 5.0
  },
  "run_uncertainty": true,
  "run_sensitivity": true,
  "uncertainty_iterations": 1000
}
```

#### Get All Analyses
```http
GET /api/analyses?skip=0&limit=100
```

#### Get Specific Analysis
```http
GET /api/analyses/{analysis_id}
```

#### Delete Analysis
```http
DELETE /api/analyses/{analysis_id}
```

#### Get Climate Region
```http
GET /api/climate-region/{latitude}
```

#### Health Check
```http
GET /health
```

### API Documentation (Swagger)
Once the application is running, access interactive API documentation at:
```
http://localhost:8080/docs
```

## 📁 Project Structure

```
reservoir-emissions-tool/
├── app/
│   ├── __init__.py           # Application initialization
│   ├── main.py               # FastAPI application and routes
│   ├── database.py           # Database configuration
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── ipcc_tier1.py         # IPCC Tier 1 calculations
│   ├── analysis.py           # Uncertainty & sensitivity analysis
│   ├── static/
│   │   ├── style.css         # CSS styling
│   │   └── app.js            # Frontend JavaScript
│   └── templates/
│       └── index.html        # Main web interface
├── data/                     # Database storage (created automatically)
├── Dockerfile                # Docker container definition
├── docker-compose.yml        # Docker Compose configuration
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🛠️ Technical Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Scientific Libraries**: NumPy, SciPy, Pandas
- **Containerization**: Docker
- **Web Server**: Uvicorn (ASGI)

## 🔒 Data Storage

All analyses are stored in a SQLite database located at:
```
./data/reservoir_emissions.db
```

The database persists across container restarts using Docker volumes.

## 📊 Default Emission Factors

Default emission factors by climate region (kg/km²/yr):

| Climate Region | CH₄      | CO₂       | N₂O |
|---------------|----------|-----------|-----|
| Tropical      | 150,000  | 500,000   | 80  |
| Subtropical   | 100,000  | 350,000   | 60  |
| Temperate     | 70,000   | 250,000   | 40  |
| Boreal        | 40,000   | 150,000   | 25  |

*Note: These are representative values based on IPCC guidance and scientific literature. Users can override with site-specific values.*

## 🔍 Troubleshooting

### Container won't start
```bash
# Check if port 8080 is in use
sudo lsof -i :8080

# View container logs
docker-compose logs -f
```

### Database issues
```bash
# Reset database (WARNING: deletes all data)
rm -rf data/reservoir_emissions.db
docker-compose restart
```

### Permission issues
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

## 📝 Citation

If you use this tool in your research, please cite:

```
Reservoir GHG Emissions Tool v1.0.0
IPCC Tier 1 Methodology Implementation
[Your Institution/Name], 2024
```

## 👨‍🏫 For Professors and Researchers

This tool is designed for:
- Teaching IPCC methodologies
- Research on reservoir emissions
- Environmental impact assessments
- Policy analysis and decision support
- Student projects and assignments

## 🤝 Contributing

This is an educational and research tool. Contributions, suggestions, and improvements are welcome.

## 📄 License

This software is provided for educational and research purposes.

## 📧 Support

For questions, issues, or feature requests, please refer to the application documentation or contact the development team.

## 🔄 Version History

### v1.0.0 (2024)
- Initial release
- IPCC Tier 1 methodology implementation
- Uncertainty and sensitivity analysis
- Web-based user interface
- Docker deployment
- REST API

---

**Built with ❤️ for reservoir greenhouse gas emission research**
