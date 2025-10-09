# Reservoir GHG Emissions Tool

A comprehensive web-based software tool for estimating greenhouse gas emissions from reservoirs using the **IPCC Tier 1 methodology**, with integrated uncertainty and sensitivity analyses.

## 🌟 Features

- **IPCC Tier 1 Methodology**: Standard methodology for reservoir GHG emission calculations
- **Automatic Climate Region Detection**: Based on geographical coordinates (latitude/longitude)
- **Trophic Status Assessment**: Automatic assessment from water quality parameters
- **Uncertainty Analysis**: Monte Carlo simulation with 100-10,000 iterations
- **Sensitivity Analysis**: Identifies most influential parameters using correlation methods
- **Database Storage**: Persistent storage of all analyses using SQLite
- **Modern Web Interface**: Responsive, user-friendly interface with real-time results
- **REST API**: Full RESTful API for programmatic access
- **Docker Deployment**: Containerized deployment for easy installation

## 📊 Methodology

### Greenhouse Gases Calculated
- **Methane (CH₄)**: Major GHG from anaerobic decomposition
- **Carbon Dioxide (CO₂)**: From organic matter oxidation
- **Nitrous Oxide (N₂O)**: From nitrogen cycling processes

### Climate Regions
The tool automatically determines the climate region based on latitude:
- **Tropical**: 0° to 23.5°
- **Subtropical**: 23.5° to 35°
- **Temperate**: 35° to 60°
- **Boreal**: 60° to 90°

Each region has default emission factors that can be overridden by the user.

### Trophic Status Assessment
Water quality parameters are used to assess trophic status:
- **Oligotrophic**: Low nutrient levels
- **Mesotrophic**: Moderate nutrient levels
- **Eutrophic**: High nutrient levels
- **Hypereutrophic**: Very high nutrient levels

Trophic status adjusts emission factors accordingly.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed on Ubuntu 22.04
- At least 512MB RAM available
- Port 8080 available

### Installation and Launch

1. **Clone or download the project files to your system**

2. **Navigate to the project directory:**
   ```bash
   cd /path/to/reservoir-emissions-tool
   ```

3. **Create the data directory:**
   ```bash
   mkdir -p data
   ```

4. **Build and start the Docker container:**
   ```bash
   docker-compose up --build -d
   ```

5. **Access the application:**
   Open your web browser and navigate to:
   ```
   http://localhost:8080
   ```

### Launch Commands

```bash
# Build and start the container (first time or after code changes)
docker-compose up --build -d

# Start existing container
docker-compose start

# Stop the container
docker-compose stop

# View logs
docker-compose logs -f

# Stop and remove container
docker-compose down

# Rebuild from scratch
docker-compose down
docker-compose up --build -d
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
