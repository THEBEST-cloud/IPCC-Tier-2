# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Docker (if not already installed)

```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER
```

**Note:** After adding yourself to the docker group, log out and log back in for changes to take effect.

### Step 2: Start the Application

#### Option A: Using the startup script (Recommended)
```bash
./start.sh
```

#### Option B: Using Docker Compose directly
```bash
# Create data directory
mkdir -p data

# Build and start
docker-compose up --build -d
```

### Step 3: Access the Application

Open your web browser and go to:
```
http://localhost:8000
```

## 📝 Example Usage

### Basic Analysis

1. **Enter Location:**
   - Latitude: `45.5`
   - Longitude: `-73.5`

2. **Enter Reservoir Characteristics:**
   - Surface Area: `100` km²

3. **Click "Run Analysis"**

### Advanced Analysis with Water Quality

1. **Enter Location:** (as above)

2. **Enter Reservoir Characteristics:** (as above)

3. **Enter Water Quality Data:**
   - Total Phosphorus: `0.02` mg/L
   - Chlorophyll-a: `5.0` μg/L

4. **Enable Analysis Options:**
   - ✅ Uncertainty Analysis
   - ✅ Sensitivity Analysis
   - Iterations: `1000`

5. **Click "Run Analysis"**

## 🎯 Expected Results

You will see:
- Climate region (automatically determined)
- Trophic status (if water quality provided)
- Emission factors for CH₄, CO₂, and N₂O
- Total annual emissions
- CO₂ equivalent emissions
- Uncertainty ranges (if enabled)
- Parameter sensitivity rankings (if enabled)

## 🛠️ Common Commands

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose stop

# View logs
docker-compose logs -f

# Restart the application
docker-compose restart

# Rebuild after changes
docker-compose up --build -d

# Complete removal
docker-compose down
```

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 8000
sudo lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

### Container Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose up --build -d
```

### Permission Denied
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

## 📊 API Usage Examples

### Using curl

```bash
# Analyze a reservoir
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 45.5,
    "longitude": -73.5,
    "surface_area": 100.0,
    "run_uncertainty": true,
    "run_sensitivity": true
  }'

# Get all analyses
curl http://localhost:8000/api/analyses

# Health check
curl http://localhost:8000/health
```

### Using Python

```python
import requests

# Analyze reservoir
response = requests.post(
    'http://localhost:8000/api/analyze',
    json={
        'latitude': 45.5,
        'longitude': -73.5,
        'surface_area': 100.0,
        'reservoir_age': 10,
        'water_quality': {
            'total_phosphorus': 0.02,
            'chlorophyll_a': 5.0
        },
        'run_uncertainty': True,
        'run_sensitivity': True,
        'uncertainty_iterations': 1000
    }
)

results = response.json()
print(f"Total CO2 equivalent: {results['emissions']['co2_equivalent']} kg/yr")
```

## 🎓 For Educational Use

### Student Exercise

1. Analyze the same reservoir with different trophic conditions
2. Compare emissions between tropical and temperate regions
3. Examine which parameters have the most influence (sensitivity analysis)
4. Understand uncertainty ranges in emission estimates

### Research Applications

- Site-specific emission calculations
- Regional emission inventories
- Impact of reservoir aging on emissions
- Comparison of different water quality scenarios

## 📖 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Experiment with different parameter combinations
- Export results for further analysis

---

**Need help?** Check the [README.md](README.md) for comprehensive documentation.
