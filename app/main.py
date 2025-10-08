"""
Main FastAPI application for Reservoir Emissions Tool
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
import os

from . import models, schemas
from .database import engine, get_db
from .ipcc_tier1 import (
    get_climate_region,
    assess_trophic_status,
    get_emission_factors,
    calculate_emissions
)
from .analysis import run_full_analysis

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Reservoir GHG Emissions Tool",
    description="IPCC Tier 1 Methodology for Reservoir Greenhouse Gas Emissions with Uncertainty and Sensitivity Analysis",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
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
    climate_region = get_climate_region(reservoir_input.latitude)
    
    # Assess trophic status if water quality data provided
    trophic_status = None
    if reservoir_input.water_quality:
        wq = reservoir_input.water_quality
        trophic_status = assess_trophic_status(
            total_phosphorus=wq.total_phosphorus,
            total_nitrogen=wq.total_nitrogen,
            chlorophyll_a=wq.chlorophyll_a,
            secchi_depth=wq.secchi_depth
        )
    
    # Get emission factors
    if reservoir_input.custom_ch4_ef and reservoir_input.custom_co2_ef and reservoir_input.custom_n2o_ef:
        ch4_ef = reservoir_input.custom_ch4_ef
        co2_ef = reservoir_input.custom_co2_ef
        n2o_ef = reservoir_input.custom_n2o_ef
    else:
        ch4_ef, co2_ef, n2o_ef = get_emission_factors(
            climate_region,
            trophic_status,
            reservoir_input.reservoir_age
        )
    
    # Calculate base emissions
    ch4_total, co2_total, n2o_total, co2_eq = calculate_emissions(
        reservoir_input.surface_area,
        ch4_ef,
        co2_ef,
        n2o_ef
    )
    
    # Run uncertainty and sensitivity analysis
    uncertainty_results, sensitivity_results = run_full_analysis(
        surface_area=reservoir_input.surface_area,
        ch4_ef=ch4_ef,
        co2_ef=co2_ef,
        n2o_ef=n2o_ef,
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
        mean_depth=reservoir_input.mean_depth,
        ch4_emission_factor=ch4_ef,
        co2_emission_factor=co2_ef,
        n2o_emission_factor=n2o_ef,
        total_ch4_emissions=ch4_total,
        total_co2_emissions=co2_total,
        total_n2o_emissions=n2o_total,
        co2_equivalent=co2_eq,
        uncertainty_analysis=uncertainty_results,
        sensitivity_analysis=sensitivity_results,
        user_inputs=reservoir_input.dict()
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    # Prepare response
    emission_results = schemas.EmissionResults(
        total_ch4_emissions=ch4_total,
        total_co2_emissions=co2_total,
        total_n2o_emissions=n2o_total,
        co2_equivalent=co2_eq,
        ch4_emission_factor=ch4_ef,
        co2_emission_factor=co2_ef,
        n2o_emission_factor=n2o_ef,
        climate_region=climate_region,
        trophic_status=trophic_status
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


@app.get("/api/climate-region/{latitude}")
async def get_climate_info(latitude: float):
    """
    Get climate region for a given latitude
    """
    climate_region = get_climate_region(latitude)
    return {"latitude": latitude, "climate_region": climate_region}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
