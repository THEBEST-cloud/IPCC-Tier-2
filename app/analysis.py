"""
Uncertainty and Sensitivity Analysis for Reservoir Emissions
"""

import numpy as np
import math
from scipy import stats
from typing import Dict, List, Tuple
from .ipcc_tier1 import calculate_emissions, UNCERTAINTY_RANGES

# 定义GWP常量
GWP_CH4 = 28  # IPCC AR5
GWP_N2O = 265  # IPCC AR5

def clean_numeric_value(value):
    """
    清理数值，确保JSON兼容
    """
    if value is None:
        return 0.0
    if math.isnan(value) or math.isinf(value):
        return 0.0
    return float(value)

class UncertaintyAnalysis:
    """Monte Carlo uncertainty analysis"""
    
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations
    
    def run(
        self,
        surface_area: float,
        ch4_ef: float,
        co2_ef: float,
        n2o_ef: float,
        uncertainty_ranges: Dict[str, float] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Run Monte Carlo uncertainty analysis
        
        Args:
            surface_area: Reservoir surface area (km²)
            ch4_ef: CH4 emission factor (kg/km²/yr)
            co2_ef: CO2 emission factor (kg/km²/yr)
            n2o_ef: N2O emission factor (kg/km²/yr)
            uncertainty_ranges: Custom uncertainty ranges (optional)
        
        Returns:
            Dictionary with statistics for each emission type
        """
        if uncertainty_ranges is None:
            uncertainty_ranges = UNCERTAINTY_RANGES
        
        # Generate random samples assuming lognormal distribution
        # Lognormal is appropriate for emission factors (positive, right-skewed)
        
        # Surface area uncertainty (±10%)
        area_std = surface_area * 0.1
        area_samples = np.random.normal(surface_area, area_std, self.iterations)
        area_samples = np.maximum(area_samples, 0.01)  # Ensure positive
        
        # Emission factor uncertainties
        ch4_std = ch4_ef * uncertainty_ranges.get("CH4", 0.5)
        co2_std = co2_ef * uncertainty_ranges.get("CO2", 0.4)
        n2o_std = n2o_ef * uncertainty_ranges.get("N2O", 0.6)
        
        # 处理CH4排放因子
        if ch4_ef > 0:
            ch4_ef_samples = np.random.lognormal(
                np.log(ch4_ef) - 0.5 * (ch4_std/ch4_ef)**2,
                ch4_std/ch4_ef,
                self.iterations
            )
        else:
            ch4_ef_samples = np.zeros(self.iterations)
        
        # 处理CO2排放因子
        if co2_ef > 0:
            co2_ef_samples = np.random.lognormal(
                np.log(co2_ef) - 0.5 * (co2_std/co2_ef)**2,
                co2_std/co2_ef,
                self.iterations
            )
        else:
            co2_ef_samples = np.zeros(self.iterations)
        
        # 处理N2O排放因子（IPCC Tier 1通常为0）
        if n2o_ef > 0:
            n2o_ef_samples = np.random.lognormal(
                np.log(n2o_ef) - 0.5 * (n2o_std/n2o_ef)**2,
                n2o_std/n2o_ef,
                self.iterations
            )
        else:
            n2o_ef_samples = np.zeros(self.iterations)
        
        # Calculate emissions for each iteration
        ch4_results = area_samples * ch4_ef_samples
        co2_results = area_samples * co2_ef_samples
        n2o_results = area_samples * n2o_ef_samples
        co2eq_results = co2_results + (ch4_results * GWP_CH4) + (n2o_results * GWP_N2O)
        
        # Calculate statistics
        return {
            "CH4": self._calculate_statistics(ch4_results),
            "CO2": self._calculate_statistics(co2_results),
            "N2O": self._calculate_statistics(n2o_results),
            "CO2_equivalent": self._calculate_statistics(co2eq_results),
        }
    
    def _calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate statistical measures from sample data"""
        return {
            "mean": clean_numeric_value(np.mean(data)),
            "std": clean_numeric_value(np.std(data)),
            "ci_lower": clean_numeric_value(np.percentile(data, 2.5)),
            "ci_upper": clean_numeric_value(np.percentile(data, 97.5)),
            "percentile_5": clean_numeric_value(np.percentile(data, 5)),
            "percentile_25": clean_numeric_value(np.percentile(data, 25)),
            "percentile_50": clean_numeric_value(np.percentile(data, 50)),
            "percentile_75": clean_numeric_value(np.percentile(data, 75)),
            "percentile_95": clean_numeric_value(np.percentile(data, 95)),
        }


class SensitivityAnalysis:
    """Global sensitivity analysis using correlation-based methods"""
    
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations
    
    def run(
        self,
        surface_area: float,
        ch4_ef: float,
        co2_ef: float,
        n2o_ef: float,
        uncertainty_ranges: Dict[str, float] = None
    ) -> List[Dict[str, any]]:
        """
        Run sensitivity analysis to identify most influential parameters
        
        Returns:
            List of sensitivity results sorted by importance
        """
        if uncertainty_ranges is None:
            uncertainty_ranges = UNCERTAINTY_RANGES
        
        # Generate parameter samples
        area_std = surface_area * 0.1
        area_samples = np.random.normal(surface_area, area_std, self.iterations)
        area_samples = np.maximum(area_samples, 0.01)
        
        ch4_std = ch4_ef * uncertainty_ranges.get("CH4", 0.5)
        co2_std = co2_ef * uncertainty_ranges.get("CO2", 0.4)
        n2o_std = n2o_ef * uncertainty_ranges.get("N2O", 0.6)
        
        # 处理CH4排放因子
        if ch4_ef > 0:
            ch4_ef_samples = np.random.lognormal(
                np.log(ch4_ef) - 0.5 * (ch4_std/ch4_ef)**2,
                ch4_std/ch4_ef,
                self.iterations
            )
        else:
            ch4_ef_samples = np.zeros(self.iterations)
        
        # 处理CO2排放因子
        if co2_ef > 0:
            co2_ef_samples = np.random.lognormal(
                np.log(co2_ef) - 0.5 * (co2_std/co2_ef)**2,
                co2_std/co2_ef,
                self.iterations
            )
        else:
            co2_ef_samples = np.zeros(self.iterations)
        
        # 处理N2O排放因子（IPCC Tier 1通常为0）
        if n2o_ef > 0:
            n2o_ef_samples = np.random.lognormal(
                np.log(n2o_ef) - 0.5 * (n2o_std/n2o_ef)**2,
                n2o_std/n2o_ef,
                self.iterations
            )
        else:
            n2o_ef_samples = np.zeros(self.iterations)
        
        # Calculate CO2 equivalent for sensitivity
        co2eq_results = (
            area_samples * co2_ef_samples +
            area_samples * ch4_ef_samples * GWP_CH4 +
            area_samples * n2o_ef_samples * GWP_N2O
        )
        
        # Create parameter matrix
        parameters = {
            "Surface Area": area_samples,
            "CH4 Emission Factor": ch4_ef_samples,
            "CO2 Emission Factor": co2_ef_samples,
            "N2O Emission Factor": n2o_ef_samples,
        }
        
        # Calculate correlations
        results = []
        for param_name, param_values in parameters.items():
            # Pearson correlation
            pearson_corr, _ = stats.pearsonr(param_values, co2eq_results)
            
            # Spearman rank correlation (more robust)
            spearman_corr, _ = stats.spearmanr(param_values, co2eq_results)
            
            results.append({
                "parameter": param_name,
                "correlation": clean_numeric_value(pearson_corr),
                "rank_correlation": clean_numeric_value(spearman_corr),
            })
        
        # Sort by absolute correlation (most influential first)
        results.sort(key=lambda x: abs(x["rank_correlation"]), reverse=True)
        
        return results


def run_full_analysis(
    surface_area: float,
    ch4_ef: float,
    co2_ef: float,
    n2o_ef: float,
    run_uncertainty: bool = True,
    run_sensitivity: bool = True,
    iterations: int = 1000
) -> Tuple[Dict, List]:
    """
    Run complete uncertainty and sensitivity analysis
    
    Returns:
        (uncertainty_results, sensitivity_results)
    """
    uncertainty_results = None
    sensitivity_results = None
    
    if run_uncertainty:
        ua = UncertaintyAnalysis(iterations=iterations)
        uncertainty_results = ua.run(surface_area, ch4_ef, co2_ef, n2o_ef)
    
    if run_sensitivity:
        sa = SensitivityAnalysis(iterations=iterations)
        sensitivity_results = sa.run(surface_area, ch4_ef, co2_ef, n2o_ef)
    
    return uncertainty_results, sensitivity_results
