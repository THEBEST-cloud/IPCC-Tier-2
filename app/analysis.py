"""
Uncertainty and Sensitivity Analysis for Reservoir Emissions
"""

import numpy as np
import math
from scipy import stats
from typing import Dict, List, Tuple
from .ipcc_tier1 import (
    calculate_ipcc_tier1_emissions, 
    EMISSION_FACTORS, 
    TROPHIC_ADJUSTMENT_FACTORS,
    M_CO2, 
    M_C, 
    R_d_i, 
    GWP_100yr_CH4,
    get_climate_region,
    clean_numeric_value
)

def beta_pert_sample(min_val, mode_val, max_val, size=1):
    """
    生成Beta-PERT分布的随机样本
    
    Args:
        min_val: 最小值
        mode_val: 众数（最可能值）
        max_val: 最大值
        size: 样本数量
    
    Returns:
        Beta-PERT分布的随机样本
    """
    # Beta-PERT分布参数计算
    # 使用标准的Beta-PERT公式
    mean = (min_val + 4 * mode_val + max_val) / 6
    
    # 计算Beta分布的alpha和beta参数
    if max_val == min_val:
        return np.full(size, mode_val)
    
    # 标准化到[0,1]区间
    mode_norm = (mode_val - min_val) / (max_val - min_val)
    mean_norm = (mean - min_val) / (max_val - min_val)
    
    # 计算Beta分布参数
    if mode_norm == 0.5:
        alpha = beta = 4
    else:
        alpha = (mean_norm * (2 * mode_norm - mean_norm)) / (mode_norm - mean_norm)
        beta = alpha * (1 - mean_norm) / mean_norm
    
    # 确保参数为正
    alpha = max(alpha, 0.1)
    beta = max(beta, 0.1)
    
    # 生成Beta分布样本并转换回原始范围
    beta_samples = np.random.beta(alpha, beta, size)
    return min_val + beta_samples * (max_val - min_val)

class UncertaintyAnalysis:
    """Monte Carlo uncertainty analysis based on IPCC parameter table"""
    
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations
    
    def run(
        self,
        surface_area_ha: float,
        latitude: float,
        longitude: float,
        trophic_status: str = "Mesotrophic",
        reservoir_age: float = 100,
        climate_region_override: str = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Run Monte Carlo uncertainty analysis using IPCC parameter distributions
        基于IPCC Tier 1方法的蒙特卡洛不确定性分析
        
        Args:
            surface_area_ha: 水库面积（公顷）- 固定值，不考虑不确定性
            latitude: 纬度
            longitude: 经度
            trophic_status: 营养状态
            reservoir_age: 水库年龄（年）
            climate_region_override: 手动指定的气候区
        
        Returns:
            Dictionary with statistics for each emission type
        """
        
        # 确定气候区
        if climate_region_override:
            climate_region = climate_region_override
        else:
            climate_region = get_climate_region(latitude, longitude)
        
        # 获取基础排放因子
        factors = EMISSION_FACTORS.get(climate_region, EMISSION_FACTORS["暖温带湿润"])
        trophic_factor = TROPHIC_ADJUSTMENT_FACTORS.get(trophic_status, 3)
        
        # 1. 水面面积 - 固定值，不考虑不确定性
        area_samples = np.full(self.iterations, surface_area_ha)
        
        # 2. CO2排放因子 - Beta-PERT分布
        # From IPCC table: mode=1.46, 95% CI: 1.44-1.48
        co2_ef_samples = beta_pert_sample(1.44, 1.46, 1.48, self.iterations)
        
        # 3. CH4排放因子 - Beta-PERT分布（年龄相关）
        if reservoir_age < 20:
            # <20 years: mode=128, 95% CI: 121.5-133.4
            ch4_ef_le_20_samples = beta_pert_sample(121.5, 128, 133.4, self.iterations)
            ch4_ef_gt_20_samples = beta_pert_sample(74, 80.3, 86, self.iterations)  # 为了计算一致性
        else:
            # ≥20 years: mode=80.3, 95% CI: 74-86
            ch4_ef_le_20_samples = beta_pert_sample(121.5, 128, 133.4, self.iterations)
            ch4_ef_gt_20_samples = beta_pert_sample(74, 80.3, 86, self.iterations)
        
        # 4. 营养状态调整系数α - 均匀分布
        if trophic_factor == 3:
            # Mesotrophic: 95% CI: 0.7-5.3
            alpha_samples = np.random.uniform(0.7, 5.3, self.iterations)
        elif trophic_factor == 10:
            # Eutrophic: 95% CI: 5.3-14.5
            alpha_samples = np.random.uniform(5.3, 14.5, self.iterations)
        elif trophic_factor == 25:
            # Hypereutrophic: 95% CI: 14.5-39.4
            alpha_samples = np.random.uniform(14.5, 39.4, self.iterations)
        elif trophic_factor == 0.7:
            # Oligotrophic: 假设95% CI: 0.2-1.2
            alpha_samples = np.random.uniform(0.2, 1.2, self.iterations)
        else:
            # Default: use the provided value with ±20% uncertainty
            alpha_std = trophic_factor * 0.2
            alpha_samples = np.random.normal(trophic_factor, alpha_std, self.iterations)
            alpha_samples = np.maximum(alpha_samples, 0.1)
        
        # 5. 下游CH4通量比值 - Beta-PERT分布
        # From IPCC table: mode=0.09, 95% CI: 0.05-0.22
        flux_ratio_samples = beta_pert_sample(0.05, 0.09, 0.22, self.iterations)
        
        # 6. CH4的GWP - 均匀分布
        # From IPCC table: mode=27.2, 95% CI: 16.2-38.2
        gwp_ch4_samples = np.random.uniform(16.2, 38.2, self.iterations)
        
        # 按照IPCC Tier 1方法计算排放量
        results = []
        
        for i in range(self.iterations):
            # 使用当前迭代的参数值
            current_area = area_samples[i]
            current_co2_ef = co2_ef_samples[i]
            current_ch4_ef_le_20 = ch4_ef_le_20_samples[i]
            current_ch4_ef_gt_20 = ch4_ef_gt_20_samples[i]
            current_alpha = alpha_samples[i]
            current_flux_ratio = flux_ratio_samples[i]
            current_gwp_ch4 = gwp_ch4_samples[i]
            
            # CO2排放计算（仅前20年）
            F_CO2_annual = current_area * current_co2_ef
            E_CO2_total = F_CO2_annual * min(20, reservoir_age)
            E_CO2_total = E_CO2_total * (M_CO2 / M_C)  # 转换为CO2
            
            # CH4排放计算
            # 水库表面排放
            F_CH4_res_le_20_annual = current_alpha * (current_ch4_ef_le_20 * current_area) / 1000  # tCH4/yr
            F_CH4_res_gt_20_annual = current_alpha * (current_ch4_ef_gt_20 * current_area) / 1000  # tCH4/yr
            
            E_CH4_res_le_20 = F_CH4_res_le_20_annual * min(20, reservoir_age)
            E_CH4_res_gt_20 = F_CH4_res_gt_20_annual * max(0, reservoir_age - 20) if reservoir_age > 20 else 0
            
            # 下游排放
            F_CH4_downstream_le_20_annual = F_CH4_res_le_20_annual * current_flux_ratio
            F_CH4_downstream_gt_20_annual = F_CH4_res_gt_20_annual * current_flux_ratio
            
            E_CH4_downstream_le_20 = F_CH4_downstream_le_20_annual * min(20, reservoir_age)
            E_CH4_downstream_gt_20 = F_CH4_downstream_gt_20_annual * max(0, reservoir_age - 20) if reservoir_age > 20 else 0
            
            # CH4总排放量（转换为CO2当量）
            E_CH4_surface_total = (E_CH4_res_le_20 + E_CH4_res_gt_20) * current_gwp_ch4
            E_CH4_downstream_total = (E_CH4_downstream_le_20 + E_CH4_downstream_gt_20) * current_gwp_ch4
            E_CH4_total = E_CH4_surface_total + E_CH4_downstream_total
            
            # 总排放量
            E_total = E_CO2_total + E_CH4_total
            
            results.append({
                'CH4_surface': E_CH4_surface_total,
                'CH4_downstream': E_CH4_downstream_total,
                'CH4_total': E_CH4_total,
                'CO2': E_CO2_total,
                'CO2_equivalent': E_total
            })
        
        # 转换为numpy数组并计算统计量
        ch4_surface_results = np.array([r['CH4_surface'] for r in results])
        ch4_downstream_results = np.array([r['CH4_downstream'] for r in results])
        ch4_total_results = np.array([r['CH4_total'] for r in results])
        co2_results = np.array([r['CO2'] for r in results])
        co2eq_results = np.array([r['CO2_equivalent'] for r in results])
        
        # 计算统计量
        uncertainty_results = {
            "CH4_surface": self._calculate_statistics(ch4_surface_results),
            "CH4_downstream": self._calculate_statistics(ch4_downstream_results),
            "CH4_total": self._calculate_statistics(ch4_total_results),
            "CO2": self._calculate_statistics(co2_results),
            "CO2_equivalent": self._calculate_statistics(co2eq_results)
        }
        
        # 添加实际的模拟数据点用于绘制真实分布图
        # 为了减少数据传输量，我们只返回CO2当量的数据点，并进行采样
        sample_size = min(1000, len(co2eq_results))  # 最多返回1000个数据点
        sample_indices = np.random.choice(len(co2eq_results), sample_size, replace=False)
        uncertainty_results["CO2_equivalent"]["raw_data"] = [float(co2eq_results[i]) for i in sorted(sample_indices)]
        
        return uncertainty_results
    
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
    
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations
    
    def run(
        self,
        surface_area_ha: float,
        latitude: float,
        longitude: float,
        trophic_status: str = "Mesotrophic",
        reservoir_age: float = 100,
        climate_region_override: str = None
    ) -> List[Dict[str, any]]:
        """
        Run sensitivity analysis to identify most influential parameters
        基于IPCC Tier 1方法的敏感性分析
        
        Args:
            surface_area_ha: 水库面积（公顷）
            latitude: 纬度
            longitude: 经度
            trophic_status: 营养状态
            reservoir_age: 水库年龄（年）
            climate_region_override: 手动指定的气候区
        
        Returns:
            List of sensitivity results sorted by importance
        """
        
        # 确定气候区
        if climate_region_override:
            climate_region = climate_region_override
        else:
            climate_region = get_climate_region(latitude, longitude)
        
        # 获取基础排放因子
        factors = EMISSION_FACTORS.get(climate_region, EMISSION_FACTORS["暖温带湿润"])
        trophic_factor = TROPHIC_ADJUSTMENT_FACTORS.get(trophic_status, 3)
        
        # 生成参数样本（与不确定性分析使用相同的分布）
        # 1. 水面面积 - 固定值，不考虑不确定性
        area_samples = np.full(self.iterations, surface_area_ha)
        
        # 2. CO2排放因子
        co2_ef_samples = beta_pert_sample(1.44, 1.46, 1.48, self.iterations)
        
        # 3. CH4排放因子（年龄相关）
        if reservoir_age < 20:
            ch4_ef_le_20_samples = beta_pert_sample(121.5, 128, 133.4, self.iterations)
            ch4_ef_gt_20_samples = beta_pert_sample(74, 80.3, 86, self.iterations)
        else:
            ch4_ef_le_20_samples = beta_pert_sample(121.5, 128, 133.4, self.iterations)
            ch4_ef_gt_20_samples = beta_pert_sample(74, 80.3, 86, self.iterations)
        
        # 4. 营养状态调整系数
        if trophic_factor == 3:
            alpha_samples = np.random.uniform(0.7, 5.3, self.iterations)
        elif trophic_factor == 10:
            alpha_samples = np.random.uniform(5.3, 14.5, self.iterations)
        elif trophic_factor == 25:
            alpha_samples = np.random.uniform(14.5, 39.4, self.iterations)
        elif trophic_factor == 0.7:
            alpha_samples = np.random.uniform(0.2, 1.2, self.iterations)
        else:
            alpha_std = trophic_factor * 0.2
            alpha_samples = np.random.normal(trophic_factor, alpha_std, self.iterations)
            alpha_samples = np.maximum(alpha_samples, 0.1)
        
        # 5. 下游通量比值
        flux_ratio_samples = beta_pert_sample(0.05, 0.09, 0.22, self.iterations)
        
        # 6. CH4的GWP
        gwp_ch4_samples = np.random.uniform(16.2, 38.2, self.iterations)
        
        # 计算总CO2当量排放量
        co2eq_results = []
        
        for i in range(self.iterations):
            current_area = area_samples[i]
            current_co2_ef = co2_ef_samples[i]
            current_ch4_ef_le_20 = ch4_ef_le_20_samples[i]
            current_ch4_ef_gt_20 = ch4_ef_gt_20_samples[i]
            current_alpha = alpha_samples[i]
            current_flux_ratio = flux_ratio_samples[i]
            current_gwp_ch4 = gwp_ch4_samples[i]
            
            # CO2排放计算
            F_CO2_annual = current_area * current_co2_ef
            E_CO2_total = F_CO2_annual * min(20, reservoir_age)
            E_CO2_total = E_CO2_total * (M_CO2 / M_C)
            
            # CH4排放计算
            F_CH4_res_le_20_annual = current_alpha * (current_ch4_ef_le_20 * current_area) / 1000
            F_CH4_res_gt_20_annual = current_alpha * (current_ch4_ef_gt_20 * current_area) / 1000
            
            E_CH4_res_le_20 = F_CH4_res_le_20_annual * min(20, reservoir_age)
            E_CH4_res_gt_20 = F_CH4_res_gt_20_annual * max(0, reservoir_age - 20) if reservoir_age > 20 else 0
            
            F_CH4_downstream_le_20_annual = F_CH4_res_le_20_annual * current_flux_ratio
            F_CH4_downstream_gt_20_annual = F_CH4_res_gt_20_annual * current_flux_ratio
            
            E_CH4_downstream_le_20 = F_CH4_downstream_le_20_annual * min(20, reservoir_age)
            E_CH4_downstream_gt_20 = F_CH4_downstream_gt_20_annual * max(0, reservoir_age - 20) if reservoir_age > 20 else 0
            
            E_CH4_total = (E_CH4_res_le_20 + E_CH4_res_gt_20 + E_CH4_downstream_le_20 + E_CH4_downstream_gt_20) * current_gwp_ch4
            
            # 总排放量
            E_total = E_CO2_total + E_CH4_total
            co2eq_results.append(E_total)
        
        co2eq_results = np.array(co2eq_results)
        
        # 创建参数矩阵
        parameters = {
            "CO2 Emission Factor": co2_ef_samples,
            "CH4 Emission Factor (≤20yr)": ch4_ef_le_20_samples,
            "CH4 Emission Factor (>20yr)": ch4_ef_gt_20_samples,
            "Trophic Alpha": alpha_samples,
            "Downstream Flux Ratio": flux_ratio_samples,
            "GWP CH4": gwp_ch4_samples,
        }
        
        # 计算相关性
        results = []
        for param_name, param_values in parameters.items():
            # Pearson相关系数
            pearson_corr, _ = stats.pearsonr(param_values, co2eq_results)
            
            # Spearman等级相关系数（更稳健）
            spearman_corr, _ = stats.spearmanr(param_values, co2eq_results)
            
            results.append({
                "parameter": param_name,
                "correlation": clean_numeric_value(pearson_corr),
                "rank_correlation": clean_numeric_value(spearman_corr),
            })
        
        # 按绝对相关性排序（影响最大的在前）
        results.sort(key=lambda x: abs(x["rank_correlation"]), reverse=True)
        
        return results


def run_full_analysis(
    surface_area_ha: float,
    latitude: float,
    longitude: float,
    trophic_status: str = "Mesotrophic",
    reservoir_age: float = 100,
    climate_region_override: str = None,
    run_uncertainty: bool = True,
    run_sensitivity: bool = True,
    iterations: int = 10000
) -> Tuple[Dict, List]:
    """
    Run complete uncertainty and sensitivity analysis
    运行完整的不确定性和敏感性分析
    
    Args:
        surface_area_ha: 水库面积（公顷）
        latitude: 纬度
        longitude: 经度
        trophic_status: 营养状态
        reservoir_age: 水库年龄（年）
        climate_region_override: 手动指定的气候区
        run_uncertainty: 是否运行不确定性分析
        run_sensitivity: 是否运行敏感性分析
        iterations: 蒙特卡洛迭代次数
    
    Returns:
        Tuple of (uncertainty_results, sensitivity_results)
    """
    uncertainty_results = {}
    sensitivity_results = []
    
    if run_uncertainty:
        uncertainty_analysis = UncertaintyAnalysis(iterations=iterations)
        uncertainty_results = uncertainty_analysis.run(
            surface_area_ha=surface_area_ha,
            latitude=latitude,
            longitude=longitude,
            trophic_status=trophic_status,
            reservoir_age=reservoir_age,
            climate_region_override=climate_region_override
        )
    
    if run_sensitivity:
        sensitivity_analysis = SensitivityAnalysis(iterations=iterations)
        sensitivity_results = sensitivity_analysis.run(
            surface_area_ha=surface_area_ha,
            latitude=latitude,
            longitude=longitude,
            trophic_status=trophic_status,
            reservoir_age=reservoir_age,
            climate_region_override=climate_region_override
        )
    
    return uncertainty_results, sensitivity_results
