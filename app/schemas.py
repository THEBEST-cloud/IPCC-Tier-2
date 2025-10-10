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
    trophic_status: Optional[str] = Field(None, description="Trophic status (Oligotrophic, Mesotrophic, Eutrophic, Hypereutrophic)")
    
    # Reservoir characteristics
    surface_area: float = Field(..., gt=0, description="Surface area (km²)")
    reservoir_age: Optional[float] = Field(None, ge=0, description="Reservoir age (years)")
    
    # Custom emission factors (optional)
    custom_ch4_ef: Optional[float] = Field(None, description="Custom CH4 emission factor (kg/km²/yr)")
    custom_co2_ef: Optional[float] = Field(None, description="Custom CO2 emission factor (kg/km²/yr)")
    
    # Analysis options
    run_uncertainty: bool = Field(True, description="Run uncertainty analysis")
    run_sensitivity: bool = Field(True, description="Run sensitivity analysis")
    uncertainty_iterations: int = Field(1000, ge=100, le=10000, description="Monte Carlo iterations")

class EmissionResults(BaseModel):
    """Emission calculation results"""
    total_ch4_emissions: float = Field(..., description="Total CH4 emissions (kg/yr)")
    total_co2_emissions: float = Field(..., description="Total CO2 emissions (kg/yr)")
    co2_equivalent: float = Field(..., description="Total CO2 equivalent (kg CO2-eq/yr)")
    
    ch4_emission_factor: float
    co2_emission_factor: float
    
    climate_region: str
    trophic_status: Optional[str] = None
    
    # IPCC Tier 1 详细结果
    ipcc_tier1_results: Optional[Dict] = Field(None, description="Detailed IPCC Tier 1 calculation results")

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

# User Authentication Schemas
class LoginRequest(BaseModel):
    """User login request"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

class RegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=20, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    organization: Optional[str] = Field(None, description="Organization")

class UserProfile(BaseModel):
    """User profile information"""
    username: str
    email: str
    first_name: str
    last_name: str
    organization: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str
