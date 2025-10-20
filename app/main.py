"""
Main FastAPI application for Reservoir Emissions Tool
"""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import jwt
from datetime import datetime, timedelta

from . import models, schemas, auth
from .database import engine, get_db
from .ipcc_tier1 import (
    get_climate_region,
    assess_trophic_status,
    calculate_emissions,
    calculate_ipcc_tier1_emissions,
    clean_numeric_value
)
from .analysis import run_full_analysis

# Create database tables
models.Base.metadata.create_all(bind=engine)

# JWT Configuration (moved to auth.py)

# Initialize FastAPI app
app = FastAPI(
    title="Reservoir Carbon Accounting",
    description="水库碳核算系统 - IPCC Tier 1 Methodology for Reservoir Greenhouse Gas Emissions",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# JWT Token verification function
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    username = auth.verify_token(credentials.credentials)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return username

# Setup templates
templates = Jinja2Templates(directory="/app/app/templates")

# Serve static files
app.mount("/static", StaticFiles(directory="/app/app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Redirect to login page"""
    return RedirectResponse(url="/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze", response_model=schemas.AnalysisResponse)
async def analyze_reservoir(
    reservoir_input: schemas.ReservoirInput,
    db: Session = Depends(get_db)
):
    """
    Analyze reservoir emissions using IPCC Tier 1 methodology
    """
    # Determine climate region
    climate_region = get_climate_region(reservoir_input.latitude, reservoir_input.longitude)
    
    # Assess trophic status
    trophic_status = None
    if reservoir_input.trophic_status:
        # 用户直接选择了营养状态
        trophic_status = reservoir_input.trophic_status
    elif reservoir_input.water_quality:
        # 通过水质参数自动评估
        wq = reservoir_input.water_quality
        trophic_status = assess_trophic_status(
            total_phosphorus=wq.total_phosphorus,
            total_nitrogen=wq.total_nitrogen,
            chlorophyll_a=wq.chlorophyll_a,
            secchi_depth=wq.secchi_depth
        )
    
    # 使用IPCC Tier 1方法计算排放
    # 转换面积单位：km² -> ha
    surface_area_ha = reservoir_input.surface_area * 100
    
    # 执行IPCC Tier 1计算
    ipcc_results = calculate_ipcc_tier1_emissions(
        surface_area_ha=surface_area_ha,
        latitude=reservoir_input.latitude,
        longitude=reservoir_input.longitude,
        trophic_status=trophic_status,
        reservoir_age=reservoir_input.reservoir_age
    )
    
    # 提取主要结果
    ch4_total = clean_numeric_value(ipcc_results["E_CH4_total"])  # tCO2eq
    co2_total = clean_numeric_value(ipcc_results["E_CO2_total"])  # tCO2eq
    n2o_total = 0  # IPCC Tier 1中N2O忽略
    co2_eq = clean_numeric_value(ipcc_results["E_total"])  # tCO2eq
    print(f"co2_eq: {co2_eq}")

    
    # Run uncertainty and sensitivity analysis
    uncertainty_results, sensitivity_results = run_full_analysis(
        surface_area_ha=surface_area_ha,  # 使用公顷为单位
        latitude=reservoir_input.latitude,
        longitude=reservoir_input.longitude,
        trophic_status=trophic_status,
        reservoir_age=reservoir_input.reservoir_age or 100,  # 默认100年
        climate_region_override=climate_region,
        run_uncertainty=reservoir_input.run_uncertainty,
        run_sensitivity=reservoir_input.run_sensitivity,
        iterations=reservoir_input.uncertainty_iterations
    )
    
    # Store in database
    db_analysis = models.ReservoirAnalysis(
        latitude=reservoir_input.latitude,
        longitude=reservoir_input.longitude,
        climate_region=climate_region,
        total_phosphorus=reservoir_input.water_quality.total_phosphorus if reservoir_input.water_quality else None,
        total_nitrogen=reservoir_input.water_quality.total_nitrogen if reservoir_input.water_quality else None,
        chlorophyll_a=reservoir_input.water_quality.chlorophyll_a if reservoir_input.water_quality else None,
        secchi_depth=reservoir_input.water_quality.secchi_depth if reservoir_input.water_quality else None,
        trophic_status=trophic_status,
        surface_area=reservoir_input.surface_area,
        reservoir_age=reservoir_input.reservoir_age,
        ch4_emission_factor=clean_numeric_value(ipcc_results["EF_CH4_age_le_20"]),
        co2_emission_factor=clean_numeric_value(ipcc_results["EF_CO2_age_le_20"]),
        total_ch4_emissions=ch4_total,
        total_co2_emissions=co2_total,
        co2_equivalent=co2_eq,
        uncertainty_analysis=uncertainty_results,
        sensitivity_analysis=sensitivity_results,
        user_inputs=reservoir_input.dict()
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    # Prepare response with detailed IPCC Tier 1 results
    emission_results = schemas.EmissionResults(
        total_ch4_emissions=ch4_total,
        total_co2_emissions=co2_total,
        total_n2o_emissions=n2o_total,
        co2_equivalent=co2_eq,
        ch4_emission_factor=clean_numeric_value(ipcc_results["EF_CH4_age_le_20"]),
        co2_emission_factor=clean_numeric_value(ipcc_results["EF_CO2_age_le_20"]),
        n2o_emission_factor=0.0,  # IPCC Tier 1中N2O忽略
        climate_region=ipcc_results["climate_region"],
        trophic_status=trophic_status,
        # 添加IPCC Tier 1详细结果
        ipcc_tier1_results=ipcc_results
    )
    
    return schemas.AnalysisResponse(
        id=db_analysis.id,
        created_at=db_analysis.created_at,
        latitude=reservoir_input.latitude,
        longitude=reservoir_input.longitude,
        surface_area=reservoir_input.surface_area,
        climate_region=climate_region,
        trophic_status=trophic_status,
        emissions=emission_results,
        uncertainty=uncertainty_results,
        sensitivity=sensitivity_results
    )


@app.get("/api/analyses", response_model=List[schemas.AnalysisListItem])
async def list_analyses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of all analyses
    """
    analyses = db.query(models.ReservoirAnalysis).order_by(
        models.ReservoirAnalysis.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return analyses


@app.get("/api/analyses/{analysis_id}", response_model=schemas.AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Get specific analysis by ID
    """
    analysis = db.query(models.ReservoirAnalysis).filter(
        models.ReservoirAnalysis.id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    emission_results = schemas.EmissionResults(
        total_ch4_emissions=analysis.total_ch4_emissions,
        total_co2_emissions=analysis.total_co2_emissions,
        total_n2o_emissions=analysis.total_n2o_emissions,
        co2_equivalent=analysis.co2_equivalent,
        ch4_emission_factor=analysis.ch4_emission_factor,
        co2_emission_factor=analysis.co2_emission_factor,
        n2o_emission_factor=analysis.n2o_emission_factor,
        climate_region=analysis.climate_region,
        trophic_status=analysis.trophic_status
    )
    
    return schemas.AnalysisResponse(
        id=analysis.id,
        created_at=analysis.created_at,
        latitude=analysis.latitude,
        longitude=analysis.longitude,
        surface_area=analysis.surface_area,
        climate_region=analysis.climate_region,
        trophic_status=analysis.trophic_status,
        emissions=emission_results,
        uncertainty=analysis.uncertainty_analysis,
        sensitivity=analysis.sensitivity_analysis
    )


@app.delete("/api/analyses/{analysis_id}")
async def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Delete specific analysis
    """
    analysis = db.query(models.ReservoirAnalysis).filter(
        models.ReservoirAnalysis.id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "Analysis deleted successfully"}


@app.get("/api/climate-region/{latitude}/{longitude}")
async def get_climate_info(latitude: float, longitude: float):
    """
    Get climate region for given latitude and longitude
    """
    climate_region = get_climate_region(latitude, longitude)
    return {"latitude": latitude, "longitude": longitude, "climate_region": climate_region}


# User Authentication Routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve register page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Serve profile page"""
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/api/user/profile")
async def get_user_profile(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get current user profile"""
    user = db.query(models.User).filter(models.User.username == token).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "organization": user.organization,
        "created_at": user.created_at
    }

@app.put("/api/user/profile")
async def update_user_profile(
    profile_data: dict,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    user = db.query(models.User).filter(models.User.username == token).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 更新允许的字段
    if "first_name" in profile_data:
        user.first_name = profile_data["first_name"]
    if "last_name" in profile_data:
        user.last_name = profile_data["last_name"]
    if "organization" in profile_data:
        user.organization = profile_data["organization"]
    
    db.commit()
    db.refresh(user)
    
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "organization": user.organization,
        "created_at": user.created_at
    }

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Serve user settings page"""
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    """Serve projects page"""
    return templates.TemplateResponse("my-projects.html", {"request": request})

@app.get("/methodology", response_class=HTMLResponse)
async def methodology_page(request: Request):
    """Serve methodology page"""
    return templates.TemplateResponse("methodology.html", {"request": request})

@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    """Serve help page"""
    return templates.TemplateResponse("help.html", {"request": request})

@app.get("/results/{analysis_id}", response_class=HTMLResponse)
async def results_page(request: Request, analysis_id: int):
    """Serve results page"""
    return templates.TemplateResponse("results.html", {
        "request": request, 
        "analysis_id": analysis_id
    })

# User Authentication API
@app.post("/api/auth/login")
async def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    """User login"""
    user = auth.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/register")
async def register(user_data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """User registration"""
    try:
        user = auth.create_user(db, user_data)
        access_token = auth.create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
