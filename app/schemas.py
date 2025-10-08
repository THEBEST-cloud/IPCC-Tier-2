from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class WaterQualityInput(BaseModel):
    """Water quality parameters for trophic status assessment"""
    total_phosphorus: Optional[float] = Field(None, description="Total Phosphorus (mg/L)")
    total_nitrogen: Optional[float] = Field(None, description="Total Nitrogen (mg/L)")
    chlorophyll_a: Optional[float] = Field(None, description="Chlorophyll-a (μg/L)")
    secchi_depth: Optional[float] = Field(None, description="Secchi Depth (m)")

class ReservoirInput(BaseModel):
    """Input data for reservoir analysis"""
    # Location
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    
    # Water quality
    water_quality: Optional[WaterQualityInput] = None
    
    # Reservoir characteristics
    surface_area: float = Field(..., gt=0, description="Surface area (km²)")
    reservoir_age: Optional[float] = Field(None, ge=0, description="Reservoir age (years)")
    mean_depth: Optional[float] = Field(None, gt=0, description="Mean depth (m)")
    
    # Custom emission factors (optional)
    custom_ch4_ef: Optional[float] = Field(None, description="Custom CH4 emission factor (kg/km²/yr)")
    custom_co2_ef: Optional[float] = Field(None, description="Custom CO2 emission factor (kg/km²/yr)")
    custom_n2o_ef: Optional[float] = Field(None, description="Custom N2O emission factor (kg/km²/yr)")
    
    # Analysis options
    run_uncertainty: bool = Field(True, description="Run uncertainty analysis")
    run_sensitivity: bool = Field(True, description="Run sensitivity analysis")
    uncertainty_iterations: int = Field(1000, ge=100, le=10000, description="Monte Carlo iterations")

class EmissionResults(BaseModel):
    """Emission calculation results"""
    total_ch4_emissions: float = Field(..., description="Total CH4 emissions (kg/yr)")
    total_co2_emissions: float = Field(..., description="Total CO2 emissions (kg/yr)")
    total_n2o_emissions: float = Field(..., description="Total N2O emissions (kg/yr)")
    co2_equivalent: float = Field(..., description="Total CO2 equivalent (kg CO2-eq/yr)")
    
    ch4_emission_factor: float
    co2_emission_factor: float
    n2o_emission_factor: float
    
    climate_region: str
    trophic_status: Optional[str] = None

class UncertaintyResults(BaseModel):
    """Uncertainty analysis results"""
    mean: float
    std: float
    ci_lower: float  # 95% confidence interval lower bound
    ci_upper: float  # 95% confidence interval upper bound
    percentile_5: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_95: float

class SensitivityResults(BaseModel):
    """Sensitivity analysis results"""
    parameter: str
    correlation: float
    rank_correlation: float

class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    id: int
    created_at: datetime
    
    # Input data
    latitude: float
    longitude: float
    surface_area: float
    climate_region: str
    trophic_status: Optional[str] = None
    
    # Emission results
    emissions: EmissionResults
    
    # Uncertainty analysis
    uncertainty: Optional[Dict[str, UncertaintyResults]] = None
    
    # Sensitivity analysis
    sensitivity: Optional[List[SensitivityResults]] = None

class AnalysisListItem(BaseModel):
    """Summary item for analysis list"""
    id: int
    created_at: datetime
    latitude: float
    longitude: float
    surface_area: float
    climate_region: str
    co2_equivalent: float
    
    class Config:
        from_attributes = True
