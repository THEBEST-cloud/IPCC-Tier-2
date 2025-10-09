# Reservoir GHG Emissions Tool - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Using the Web Interface](#using-the-web-interface)
5. [Understanding Results](#understanding-results)
6. [API Reference](#api-reference)
7. [Scientific Background](#scientific-background)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Introduction

The Reservoir GHG Emissions Tool is a scientific software application designed to estimate greenhouse gas (GHG) emissions from freshwater reservoirs using the IPCC Tier 1 methodology. This tool is intended for:

- **Researchers** conducting environmental impact assessments
- **Students** learning about reservoir emissions and IPCC methodologies
- **Policy Makers** estimating regional emissions from reservoirs
- **Environmental Consultants** performing emission inventories

### Key Capabilities

- ✅ IPCC Tier 1 compliant emission calculations
- ✅ Automatic climate region classification
- ✅ Trophic status assessment from water quality data
- ✅ Monte Carlo uncertainty analysis
- ✅ Global sensitivity analysis
- ✅ Database storage of all analyses
- ✅ RESTful API for automation

## System Requirements

### Minimum Requirements
- **Operating System:** Ubuntu 22.04 LTS (or compatible Linux distribution)
- **RAM:** 512 MB available
- **Disk Space:** 500 MB
- **Docker:** Version 20.10 or higher
- **Docker Compose:** Version 1.29 or higher
- **Network:** Port 8000 available

### Recommended Requirements
- **RAM:** 2 GB available
- **Disk Space:** 2 GB
- **CPU:** 2 cores or more (for faster uncertainty analysis)

## Installation

### Step 1: Install Docker

```bash
# Update package list
sudo apt update

# Install Docker and Docker Compose
sudo apt install docker.io docker-compose -y

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
```

### Step 2: Download the Application

Place all application files in a directory, for example:
```bash
mkdir -p ~/reservoir-emissions-tool
cd ~/reservoir-emissions-tool
# Copy all files here
```

### Step 3: Launch the Application

#### Method 1: Using the Startup Script
```bash
chmod +x start.sh
./start.sh
```

#### Method 2: Using Docker Compose
```bash
mkdir -p data
docker-compose up --build -d
```

### Step 4: Verify Installation

1. Open browser and navigate to: `http://localhost:8080`
2. You should see the application interface
3. Check API documentation at: `http://localhost:8080/docs`

## Using the Web Interface

### Input Parameters

#### 1. Location Information (Required)

**Latitude** (-90 to 90)
- Enter the reservoir's latitude in decimal degrees
- Positive values for Northern Hemisphere
- Negative values for Southern Hemisphere
- Example: `45.5` for 45.5°N

**Longitude** (-180 to 180)
- Enter the reservoir's longitude in decimal degrees
- Positive values for Eastern Hemisphere
- Negative values for Western Hemisphere
- Example: `-73.5` for 73.5°W

*The climate region is automatically determined from latitude.*

#### 2. Reservoir Characteristics

**Surface Area (Required)**
- Enter in square kilometers (km²)
- Must be greater than 0
- Example: `100` for a 100 km² reservoir

**Reservoir Age (Optional)**
- Years since the reservoir was created
- Affects emission factors (newer reservoirs emit more)
- Example: `10` for a 10-year-old reservoir

**Mean Depth (Optional)**
- Average depth in meters
- Currently informational (may be used in future versions)
- Example: `15.5` meters

#### 3. Water Quality Data (Optional)

Providing water quality data improves emission estimates by determining trophic status:

**Total Phosphorus (mg/L)**
- Indicator of nutrient enrichment
- Typical range: 0.001 - 0.5 mg/L
- Example: `0.02` mg/L

**Total Nitrogen (mg/L)**
- Nitrogen concentration
- Typical range: 0.1 - 2.0 mg/L
- Example: `0.5` mg/L

**Chlorophyll-a (μg/L)**
- Measure of algal biomass
- Typical range: 1 - 100 μg/L
- Example: `5.0` μg/L

**Secchi Depth (m)**
- Water transparency measure
- Typical range: 0.5 - 10 m
- Example: `3.5` m

#### 4. Custom Emission Factors (Optional)

Override default emission factors with site-specific values:

**CH₄ Emission Factor (kg/km²/yr)**
- Default: Based on climate region (40,000 - 150,000)
- Use if you have site-specific data

**CO₂ Emission Factor (kg/km²/yr)**
- Default: Based on climate region (150,000 - 500,000)
- Use if you have site-specific data

**N₂O Emission Factor (kg/km²/yr)**
- Default: Based on climate region (25 - 80)
- Use if you have site-specific data

#### 5. Analysis Options

**Uncertainty Analysis**
- Uses Monte Carlo simulation
- Provides confidence intervals and uncertainty ranges
- Iterations: 100 - 10,000 (default: 1,000)
- More iterations = more accurate but slower

**Sensitivity Analysis**
- Identifies most influential parameters
- Uses correlation-based methods
- Helps understand which inputs matter most

### Running an Analysis

1. Fill in required fields (location and surface area)
2. Optionally add water quality and other data
3. Select analysis options
4. Click **"Run Analysis"** button
5. Wait for results (typically 1-5 seconds)
6. Review results below the form

## Understanding Results

### Basic Information

**Climate Region**
- Automatically determined from latitude
- Options: Tropical, Subtropical, Temperate, Boreal
- Affects default emission factors

**Trophic Status** (if water quality provided)
- Oligotrophic: Low nutrients, low productivity
- Mesotrophic: Moderate nutrients
- Eutrophic: High nutrients, high productivity
- Hypereutrophic: Very high nutrients

### Emission Results

**Emission Factors**
- Shows the factors used in calculations
- Units: kg/km²/yr for each gas

**Total Annual Emissions**
- Calculated by: Emission Factor × Surface Area
- Separate values for CH₄, CO₂, and N₂O
- Units: kg/year

**CO₂ Equivalent**
- Combines all gases using Global Warming Potential (GWP)
- GWP values: CH₄ = 28, N₂O = 265 (100-year horizon)
- Formula: CO₂-eq = CO₂ + (CH₄ × 28) + (N₂O × 265)

### Uncertainty Analysis Results

**Statistical Measures:**

- **Mean:** Average of all Monte Carlo iterations
- **Standard Deviation:** Measure of variability
- **Median (50th percentile):** Middle value
- **95% Confidence Interval:** Range containing 95% of results
- **Percentiles:** 5th, 25th, 75th, 95th percentiles

**Interpretation:**
- Wider confidence intervals = higher uncertainty
- Use CI range for conservative estimates
- Median often more robust than mean for skewed distributions

### Sensitivity Analysis Results

**Parameters Ranked by Influence:**

1. Parameters with higher correlation have more influence on results
2. **Pearson Correlation:** Linear relationship (-1 to 1)
3. **Rank Correlation:** Monotonic relationship (more robust)

**Interpretation:**
- Focus data collection efforts on high-influence parameters
- Low-influence parameters can use default values
- Helps prioritize field measurements

## API Reference

### Base URL
```
http://localhost:8080/api
```

### Endpoints

#### 1. Analyze Reservoir
```http
POST /api/analyze
Content-Type: application/json

{
  "latitude": 45.5,
  "longitude": -73.5,
  "surface_area": 100.0,
  "reservoir_age": 10,
  "mean_depth": 15.5,
  "water_quality": {
    "total_phosphorus": 0.02,
    "total_nitrogen": 0.5,
    "chlorophyll_a": 5.0,
    "secchi_depth": 3.5
  },
  "custom_ch4_ef": null,
  "custom_co2_ef": null,
  "custom_n2o_ef": null,
  "run_uncertainty": true,
  "run_sensitivity": true,
  "uncertainty_iterations": 1000
}
```

#### 2. List All Analyses
```http
GET /api/analyses?skip=0&limit=100
```

#### 3. Get Specific Analysis
```http
GET /api/analyses/{id}
```

#### 4. Delete Analysis
```http
DELETE /api/analyses/{id}
```

#### 5. Get Climate Region
```http
GET /api/climate-region/{latitude}
```

### Using the API with Python

```python
import requests
import json

# Prepare data
data = {
    "latitude": 45.5,
    "longitude": -73.5,
    "surface_area": 100.0,
    "run_uncertainty": True,
    "run_sensitivity": True,
    "uncertainty_iterations": 1000
}

# Send request
response = requests.post(
    "http://localhost:8080/api/analyze",
    json=data
)

# Get results
results = response.json()

# Print CO2 equivalent
print(f"CO2 Equivalent: {results['emissions']['co2_equivalent']:,.0f} kg/yr")

# Print uncertainty range if available
if results.get('uncertainty'):
    unc = results['uncertainty']['CO2_equivalent']
    print(f"95% CI: {unc['ci_lower']:,.0f} - {unc['ci_upper']:,.0f} kg/yr")
```

## Scientific Background

### IPCC Tier 1 Methodology

The IPCC provides three tiers of methodologies:
- **Tier 1:** Uses default emission factors (this tool)
- **Tier 2:** Uses country-specific factors
- **Tier 3:** Uses detailed models and measurements

Tier 1 is suitable when:
- Site-specific data is limited
- Regional estimates are needed
- Initial assessments are required

### Emission Mechanisms

**Methane (CH₄)**
- Produced by anaerobic decomposition of organic matter
- Ebullition (bubbling) is major pathway
- Higher in warm, productive waters

**Carbon Dioxide (CO₂)**
- From aerobic decomposition
- Diffusion across water-air interface
- Photosynthesis can reduce net emissions

**Nitrous Oxide (N₂O)**
- From nitrogen cycling (nitrification/denitrification)
- Usually smallest contribution by mass
- High GWP makes it significant

### Climate Region Effects

**Tropical Regions:**
- Higher temperatures increase microbial activity
- Year-round emissions
- Highest emission factors

**Temperate Regions:**
- Seasonal variation in emissions
- Moderate emission factors
- Ice cover reduces winter emissions

**Boreal Regions:**
- Cold temperatures slow decomposition
- Extended ice cover
- Lowest emission factors

### Trophic Status Effects

Higher trophic status (more nutrients) leads to:
- Increased organic matter production
- More substrate for decomposition
- Higher GHG emissions

## Best Practices

### Data Collection Priorities

1. **Always Required:**
   - Accurate coordinates
   - Surface area measurement

2. **High Priority:**
   - Reservoir age
   - At least one water quality parameter

3. **Nice to Have:**
   - Complete water quality suite
   - Site-specific emission factors

### Improving Accuracy

1. **Use Multiple Water Quality Parameters:**
   - More parameters → better trophic assessment
   - Sample during growing season

2. **Consider Temporal Variation:**
   - Run seasonal analyses if data available
   - Note that results represent annual averages

3. **Validate with Measurements:**
   - Compare with chamber measurements if available
   - Use results as screening-level estimates

### Uncertainty Management

1. **Always Run Uncertainty Analysis:**
   - Provides realistic estimate ranges
   - Essential for decision-making

2. **Use Conservative Estimates:**
   - Consider upper confidence interval for risk assessment
   - Use median for best estimate

3. **Document Assumptions:**
   - Note any custom emission factors
   - Record data sources

## Troubleshooting

### Application Issues

**Container Won't Start**
```bash
# Check Docker service
sudo systemctl status docker

# View detailed logs
docker-compose logs -f

# Rebuild from scratch
docker-compose down
docker-compose up --build -d
```

**Port 8000 Already in Use**
```bash
# Find what's using the port
sudo lsof -i :8000

# Option 1: Kill the process
sudo kill -9 <PID>

# Option 2: Change port in docker-compose.yml
# Change "8000:8000" to "8080:8000"
# Then access at http://localhost:8080
```

**Database Errors**
```bash
# Reset database (WARNING: Deletes all data)
docker-compose down
rm -rf data/reservoir_emissions.db
docker-compose up -d
```

### Input Validation Errors

**"Latitude must be between -90 and 90"**
- Check coordinate format
- Use decimal degrees, not DMS

**"Surface area must be greater than 0"**
- Ensure positive value
- Use km² units

**"Invalid water quality values"**
- All values must be positive
- Use correct units (mg/L or μg/L)

### Performance Issues

**Slow Uncertainty Analysis**
```
- Reduce iterations (minimum 100)
- Run on faster hardware
- Disable sensitivity analysis if not needed
```

**Large Database**
```bash
# Export important analyses first
# Then delete old analyses through API or UI
# Or reset database (see above)
```

## Frequently Asked Questions

**Q: Can I use this for salt water or estuarine systems?**
A: This tool is designed for freshwater reservoirs. Results may not be accurate for saline systems.

**Q: How accurate are the emission estimates?**
A: Tier 1 estimates typically have uncertainty of ±50-100%. They are suitable for screening and regional inventories, not for carbon credit calculations.

**Q: Can I export results?**
A: Yes, all results are stored in the database and accessible via API. You can write scripts to export to CSV, Excel, etc.

**Q: What if I have site-specific emission measurements?**
A: Use the custom emission factor inputs to override defaults with your measured values.

**Q: How do I cite this tool?**
A: See the README.md for citation information.

---

**For additional support or questions, please refer to the comprehensive README.md or contact the development team.**
