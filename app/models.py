from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from datetime import datetime
from .database import Base

class ReservoirAnalysis(Base):
    """Model to store reservoir analysis data"""
    __tablename__ = "reservoir_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Location data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    climate_region = Column(String, nullable=True)
    
    # Water quality parameters
    total_phosphorus = Column(Float, nullable=True)  # mg/L
    total_nitrogen = Column(Float, nullable=True)    # mg/L
    chlorophyll_a = Column(Float, nullable=True)     # μg/L
    secchi_depth = Column(Float, nullable=True)      # m
    trophic_status = Column(String, nullable=True)
    
    # Reservoir characteristics
    surface_area = Column(Float, nullable=False)      # km²
    reservoir_age = Column(Float, nullable=True)      # years
    mean_depth = Column(Float, nullable=True)         # m
    
    # IPCC Tier 1 parameters
    ch4_emission_factor = Column(Float, nullable=True)  # kg CH4/km²/yr
    co2_emission_factor = Column(Float, nullable=True)  # kg CO2/km²/yr
    n2o_emission_factor = Column(Float, nullable=True)  # kg N2O/km²/yr
    
    # Calculated emissions
    total_ch4_emissions = Column(Float, nullable=True)  # kg CH4/yr
    total_co2_emissions = Column(Float, nullable=True)  # kg CO2/yr
    total_n2o_emissions = Column(Float, nullable=True)  # kg N2O/yr
    co2_equivalent = Column(Float, nullable=True)       # kg CO2-eq/yr
    
    # Analysis settings
    uncertainty_analysis = Column(JSON, nullable=True)
    sensitivity_analysis = Column(JSON, nullable=True)
    
    # User inputs (stored as JSON)
    user_inputs = Column(JSON, nullable=True)
