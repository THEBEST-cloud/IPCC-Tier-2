"""
IPCC Tier 1 Methodology for Reservoir Greenhouse Gas Emissions
Based on IPCC Guidelines and scientific literature
"""

import numpy as np
from typing import Tuple, Optional

# Global Warming Potential (GWP) for 100-year time horizon
GWP_CH4 = 28  # IPCC AR5
GWP_N2O = 265  # IPCC AR5

# Climate region definitions based on latitude
def get_climate_region(latitude: float) -> str:
    """
    Determine climate region based on latitude
    
    Tropical: 0° to 23.5°
    Subtropical: 23.5° to 35°
    Temperate: 35° to 60°
    Boreal/Polar: 60° to 90°
    """
    abs_lat = abs(latitude)
    
    if abs_lat <= 23.5:
        return "Tropical"
    elif abs_lat <= 35:
        return "Subtropical"
    elif abs_lat <= 60:
        return "Temperate"
    else:
        return "Boreal"

# Default emission factors based on climate regions (kg/km²/yr)
# These are representative values based on IPCC guidance and scientific literature
EMISSION_FACTORS = {
    "Tropical": {
        "CH4": 150000,  # Higher emissions in tropical regions
        "CO2": 500000,
        "N2O": 80,
    },
    "Subtropical": {
        "CH4": 100000,
        "CO2": 350000,
        "N2O": 60,
    },
    "Temperate": {
        "CH4": 70000,
        "CO2": 250000,
        "N2O": 40,
    },
    "Boreal": {
        "CH4": 40000,
        "CO2": 150000,
        "N2O": 25,
    }
}

# Uncertainty ranges (as percentage of the mean)
UNCERTAINTY_RANGES = {
    "CH4": 0.50,  # ±50%
    "CO2": 0.40,  # ±40%
    "N2O": 0.60,  # ±60%
}

def assess_trophic_status(
    total_phosphorus: Optional[float] = None,
    total_nitrogen: Optional[float] = None,
    chlorophyll_a: Optional[float] = None,
    secchi_depth: Optional[float] = None
) -> str:
    """
    Assess trophic status based on water quality parameters
    
    Criteria (simplified):
    - Oligotrophic: TP < 10 μg/L, TN < 350 μg/L, Chl-a < 2.5 μg/L, Secchi > 4m
    - Mesotrophic: TP 10-30 μg/L, TN 350-650 μg/L, Chl-a 2.5-8 μg/L, Secchi 2-4m
    - Eutrophic: TP 30-100 μg/L, TN 650-1200 μg/L, Chl-a 8-25 μg/L, Secchi 1-2m
    - Hypereutrophic: TP > 100 μg/L, TN > 1200 μg/L, Chl-a > 25 μg/L, Secchi < 1m
    """
    scores = []
    
    if total_phosphorus is not None:
        tp_mg = total_phosphorus * 1000  # Convert mg/L to μg/L
        if tp_mg < 10:
            scores.append(1)
        elif tp_mg < 30:
            scores.append(2)
        elif tp_mg < 100:
            scores.append(3)
        else:
            scores.append(4)
    
    if total_nitrogen is not None:
        tn_mg = total_nitrogen * 1000  # Convert mg/L to μg/L
        if tn_mg < 350:
            scores.append(1)
        elif tn_mg < 650:
            scores.append(2)
        elif tn_mg < 1200:
            scores.append(3)
        else:
            scores.append(4)
    
    if chlorophyll_a is not None:
        if chlorophyll_a < 2.5:
            scores.append(1)
        elif chlorophyll_a < 8:
            scores.append(2)
        elif chlorophyll_a < 25:
            scores.append(3)
        else:
            scores.append(4)
    
    if secchi_depth is not None:
        if secchi_depth > 4:
            scores.append(1)
        elif secchi_depth > 2:
            scores.append(2)
        elif secchi_depth > 1:
            scores.append(3)
        else:
            scores.append(4)
    
    if not scores:
        return "Unknown"
    
    avg_score = np.mean(scores)
    
    if avg_score < 1.5:
        return "Oligotrophic"
    elif avg_score < 2.5:
        return "Mesotrophic"
    elif avg_score < 3.5:
        return "Eutrophic"
    else:
        return "Hypereutrophic"

def get_emission_factors(
    climate_region: str,
    trophic_status: Optional[str] = None,
    reservoir_age: Optional[float] = None
) -> Tuple[float, float, float]:
    """
    Get emission factors based on climate region and optional modifiers
    
    Returns: (CH4_EF, CO2_EF, N2O_EF) in kg/km²/yr
    """
    base_factors = EMISSION_FACTORS.get(climate_region, EMISSION_FACTORS["Temperate"])
    
    ch4_ef = base_factors["CH4"]
    co2_ef = base_factors["CO2"]
    n2o_ef = base_factors["N2O"]
    
    # Adjust based on trophic status (higher productivity → higher emissions)
    if trophic_status:
        trophic_multipliers = {
            "Oligotrophic": 0.7,
            "Mesotrophic": 1.0,
            "Eutrophic": 1.3,
            "Hypereutrophic": 1.6,
        }
        multiplier = trophic_multipliers.get(trophic_status, 1.0)
        ch4_ef *= multiplier
        co2_ef *= multiplier
        n2o_ef *= multiplier
    
    # Adjust based on reservoir age (emissions decrease over time)
    if reservoir_age is not None:
        if reservoir_age < 5:
            age_multiplier = 1.5
        elif reservoir_age < 10:
            age_multiplier = 1.2
        elif reservoir_age < 20:
            age_multiplier = 1.0
        else:
            age_multiplier = 0.8
        
        ch4_ef *= age_multiplier
        co2_ef *= age_multiplier
    
    return ch4_ef, co2_ef, n2o_ef

def calculate_emissions(
    surface_area: float,
    ch4_ef: float,
    co2_ef: float,
    n2o_ef: float
) -> Tuple[float, float, float, float]:
    """
    Calculate total emissions
    
    Args:
        surface_area: Reservoir surface area (km²)
        ch4_ef: CH4 emission factor (kg/km²/yr)
        co2_ef: CO2 emission factor (kg/km²/yr)
        n2o_ef: N2O emission factor (kg/km²/yr)
    
    Returns:
        (CH4 emissions, CO2 emissions, N2O emissions, CO2-equivalent) in kg/yr
    """
    ch4_total = surface_area * ch4_ef
    co2_total = surface_area * co2_ef
    n2o_total = surface_area * n2o_ef
    
    # Calculate CO2 equivalent
    co2_eq = co2_total + (ch4_total * GWP_CH4) + (n2o_total * GWP_N2O)
    
    return ch4_total, co2_total, n2o_total, co2_eq
