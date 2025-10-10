from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Boolean
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
    
    # IPCC Tier 1 parameters
    ch4_emission_factor = Column(Float, nullable=True)  # kg CH4/km²/yr
    co2_emission_factor = Column(Float, nullable=True)  # kg CO2/km²/yr
    
    # Calculated emissions
    total_ch4_emissions = Column(Float, nullable=True)  # kg CH4/yr
    total_co2_emissions = Column(Float, nullable=True)  # kg CO2/yr
    co2_equivalent = Column(Float, nullable=True)       # kg CO2-eq/yr
    
    # Analysis settings
    uncertainty_analysis = Column(JSON, nullable=True)
    sensitivity_analysis = Column(JSON, nullable=True)
    
    # User inputs (stored as JSON)
    user_inputs = Column(JSON, nullable=True)
    
    # User relationship
    user_id = Column(Integer, nullable=True)  # Will be foreign key to users table

class User(Base):
    """Model to store user account data"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    organization = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User preferences (stored as JSON)
    preferences = Column(JSON, nullable=True)
