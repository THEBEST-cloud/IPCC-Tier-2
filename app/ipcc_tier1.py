"""
IPCC Tier 1 Methodology for Reservoir Greenhouse Gas Emissions
严格遵循IPCC指南的Tier 1方法
"""

import numpy as np
import math
from typing import Tuple, Optional, Dict

# IPCC Tier 1 常量定义
M_CO2 = 44  # CO2的相对分子质量
M_C = 12    # C元素的相对原子质量
R_d_i = 0.09  # 大坝下游CH4通量与水库表面CH4通量的比值
GWP_100yr_CH4 = 27.2  # 非化石源CH4的100年全球变暖潜势

# 气候区定义（基于纬度）
def get_climate_region(latitude: float) -> str:
    """
    根据纬度确定气候区
    
    Args:
        latitude: 纬度（度）
    
    Returns:
        气候区名称
    """
    abs_lat = abs(latitude)
    
    if abs_lat <= 25:
        return "炎热潮湿区"  # Tropical_Moist
    elif abs_lat <= 50:
        return "温暖区"  # Warm_Temperate（需要进一步确认湿润/干燥）
    else:
        return "其他区域"  # Other

# IPCC Tier 1 排放因子表
EMISSION_FACTORS = {
    "温暖干燥区": {  # Warm_Dry
        "EF_CO2_age_le_20": 1.7,  # tCO2-C/(ha·yr)
        "EF_CH4_age_le_20": 195.6,  # kgCH4/(ha·yr)
        "EF_CH4_age_gt_20": 150.9,  # kgCH4/(ha·yr)
    },
    "温暖湿润区": {  # Warm_Moist
        "EF_CO2_age_le_20": 1.46,  # tCO2-C/(ha·yr)
        "EF_CH4_age_le_20": 127.5,  # kgCH4/(ha·yr)
        "EF_CH4_age_gt_20": 80.3,  # kgCH4/(ha·yr)
    },
    "炎热潮湿区": {  # Tropical_Moist
        "EF_CO2_age_le_20": 2.77,  # tCO2-C/(ha·yr)
        "EF_CH4_age_le_20": 251.6,  # kgCH4/(ha·yr)
        "EF_CH4_age_gt_20": 141.1,  # kgCH4/(ha·yr)
    }
}

# 营养状态调整系数
TROPHIC_ADJUSTMENT_FACTORS = {
    "Oligotrophic": 0.7,    # 贫营养型
    "Mesotrophic": 3,       # 中营养型
    "Eutrophic": 10,        # 富营养型
    "Hypereutrophic": 25,   # 超富营养型
}

def clean_numeric_value(value):
    """
    清理数值，确保JSON兼容
    """
    if value is None:
        return 0.0
    if math.isnan(value) or math.isinf(value):
        return 0.0
    return float(value)

def assess_trophic_status(
    total_phosphorus: Optional[float] = None,
    total_nitrogen: Optional[float] = None,
    chlorophyll_a: Optional[float] = None,
    secchi_depth: Optional[float] = None
) -> str:
    """
    根据水质参数评估营养状态
    
    Args:
        total_phosphorus: 总磷浓度 (mg/L)
        total_nitrogen: 总氮浓度 (mg/L)
        chlorophyll_a: 叶绿素a浓度 (μg/L)
        secchi_depth: 透明度 (m)
    
    Returns:
        营养状态分类
    """
    scores = []
    
    if total_phosphorus is not None:
        tp_ug = total_phosphorus * 1000  # 转换为μg/L
        if tp_ug < 10:
            scores.append(1)
        elif tp_ug < 30:
            scores.append(2)
        elif tp_ug < 100:
            scores.append(3)
        else:
            scores.append(4)
    
    if total_nitrogen is not None:
        tn_ug = total_nitrogen * 1000  # 转换为μg/L
        if tn_ug < 350:
            scores.append(1)
        elif tn_ug < 650:
            scores.append(2)
        elif tn_ug < 1200:
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
        return "Mesotrophic"  # 默认中营养型
    
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
    trophic_status: str = "Mesotrophic",
    reservoir_age: float = 100
) -> Tuple[float, float, float]:
    """
    根据气候区和营养状态获取排放因子
    
    Args:
        climate_region: 气候区
        trophic_status: 营养状态
        reservoir_age: 水库年龄（年）
    
    Returns:
        (CH4_EF, CO2_EF, N2O_EF) in kg/km²/yr
    """
    # 获取基础排放因子
    if climate_region not in EMISSION_FACTORS:
        climate_region = "温暖湿润区"  # 默认温暖湿润区
    
    factors = EMISSION_FACTORS[climate_region]
    
    # 根据水库年龄选择CH4排放因子
    if reservoir_age <= 20:
        ch4_ef = factors["EF_CH4_age_le_20"]
    else:
        ch4_ef = factors["EF_CH4_age_gt_20"]
    
    co2_ef = factors["EF_CO2_age_le_20"]
    
    # 应用营养状态调整系数
    trophic_factor = TROPHIC_ADJUSTMENT_FACTORS.get(trophic_status, 3)
    ch4_ef *= trophic_factor
    
    # 转换单位：tCO2-C/(ha·yr) -> kgCO2/(km²/yr)
    co2_ef = co2_ef * 100 * (M_CO2 / M_C)  # 100 ha/km² * 分子量转换
    
    # 转换单位：kgCH4/(ha·yr) -> kgCH4/(km²/yr)
    ch4_ef = ch4_ef * 100  # 100 ha/km²
    
    # N2O排放因子（IPCC Tier 1方法中通常忽略）
    n2o_ef = 0
    
    return ch4_ef, co2_ef, n2o_ef

def calculate_ipcc_tier1_emissions(
    surface_area_ha: float,
    latitude: float,
    trophic_status: str = "Mesotrophic",
    reservoir_age: float = 100,
    climate_region_override: Optional[str] = None
) -> Dict[str, float]:
    """
    按照IPCC Tier 1方法计算水库温室气体排放
    
    Args:
        surface_area_ha: 水库面积（公顷）
        latitude: 纬度
        trophic_status: 营养状态
        reservoir_age: 水库年龄（年）
        climate_region_override: 手动指定的气候区
    
    Returns:
        包含所有排放指标的字典
    """
    # 第1步：确定气候区
    if climate_region_override:
        climate_region = climate_region_override
    else:
        climate_region = get_climate_region(latitude)
    
    # 第2步：获取排放因子
    ch4_ef, co2_ef, n2o_ef = get_emission_factors(
        climate_region, trophic_status, reservoir_age
    )
    
    # 第3步：计算年均CO2排放总量 (F_CO2,tot)
    # 注意：这里使用≤20年的CO2排放因子，因为IPCC方法中CO2排放因子不区分年龄
    F_CO2_tot = surface_area_ha * (co2_ef / 100)  # 转换为tCO2-C/yr
    
    # 第4步：计算CH4排放
    # 获取不同年龄段的CH4排放因子
    factors = EMISSION_FACTORS.get(climate_region, EMISSION_FACTORS["Warm_Moist"])
    trophic_factor = TROPHIC_ADJUSTMENT_FACTORS.get(trophic_status, 3)
    
    # 库龄≤20年的CH4排放
    F_CH4_res_age_le_20 = trophic_factor * (factors["EF_CH4_age_le_20"] * surface_area_ha)
    F_CH4_downstream_age_le_20 = F_CH4_res_age_le_20 * R_d_i
    
    # 库龄>20年的CH4排放
    F_CH4_res_age_gt_20 = trophic_factor * (factors["EF_CH4_age_gt_20"] * surface_area_ha)
    F_CH4_downstream_age_gt_20 = F_CH4_res_age_gt_20 * R_d_i
    
    # 第5步：计算生命周期总排放量
    # 库龄≤20年的CH4排放总量
    E_CH4_age_le_20 = ((F_CH4_res_age_le_20 + F_CH4_downstream_age_le_20) * 
                       GWP_100yr_CH4 / 1000) * min(20, reservoir_age)
    
    # 库龄>20年的CH4排放总量
    if reservoir_age > 20:
        E_CH4_age_gt_20 = ((F_CH4_res_age_gt_20 + F_CH4_downstream_age_gt_20) * 
                           GWP_100yr_CH4 / 1000) * (reservoir_age - 20)
    else:
        E_CH4_age_gt_20 = 0
    
    # 水库寿命内CO2排放总量
    E_CO2 = F_CO2_tot * (M_CO2 / M_C) * reservoir_age
    
    # 水库寿命内CH4排放总量
    E_CH4 = E_CH4_age_le_20 + E_CH4_age_gt_20
    
    # 水库生命周期碳排放总量
    E_total = E_CO2 + E_CH4
    
    # 计算年均排放量
    annual_CO2_kg = F_CO2_tot * (M_CO2 / M_C) * 1000  # kgCO2eq/yr
    
    # 分阶段年均CH4排放量
    if reservoir_age <= 20:
        annual_CH4_age_le_20_kg = (E_CH4_age_le_20 / reservoir_age) * 1000
        annual_CH4_age_gt_20_kg = 0
    else:
        annual_CH4_age_le_20_kg = (E_CH4_age_le_20 / 20) * 1000
        annual_CH4_age_gt_20_kg = (E_CH4_age_gt_20 / (reservoir_age - 20)) * 1000
    
    # 水库表面和下游CH4排放的年均排放量
    annual_CH4_res_surface_le_20 = F_CH4_res_age_le_20 * GWP_100yr_CH4
    annual_CH4_downstream_le_20 = F_CH4_downstream_age_le_20 * GWP_100yr_CH4
    
    if reservoir_age > 20:
        annual_CH4_res_surface_gt_20 = F_CH4_res_age_gt_20 * GWP_100yr_CH4
        annual_CH4_downstream_gt_20 = F_CH4_downstream_age_gt_20 * GWP_100yr_CH4
    else:
        annual_CH4_res_surface_gt_20 = 0
        annual_CH4_downstream_gt_20 = 0
    
    return {
        # 主要结果
        "E_total": clean_numeric_value(E_total),  # 水库生命周期碳排放总量 (tCO2eq)
        "E_CO2": clean_numeric_value(E_CO2),  # 水库寿命内CO2排放总量 (tCO2eq)
        "E_CH4": clean_numeric_value(E_CH4),  # 水库寿命内CH4排放总量 (tCO2eq)
        
        # 年均排放量
        "annual_CO2": clean_numeric_value(annual_CO2_kg),  # 年均CO2排放量 (kgCO2eq/yr)
        "annual_CH4_age_le_20": clean_numeric_value(annual_CH4_age_le_20_kg),  # ≤20年CH4年均排放量 (kgCO2eq/yr)
        "annual_CH4_age_gt_20": clean_numeric_value(annual_CH4_age_gt_20_kg),  # >20年CH4年均排放量 (kgCO2eq/yr)
        
        # 分源CH4排放
        "annual_CH4_res_surface_le_20": clean_numeric_value(annual_CH4_res_surface_le_20),  # ≤20年水库表面CH4排放 (kgCO2eq/yr)
        "annual_CH4_res_surface_gt_20": clean_numeric_value(annual_CH4_res_surface_gt_20),  # >20年水库表面CH4排放 (kgCO2eq/yr)
        "annual_CH4_downstream_le_20": clean_numeric_value(annual_CH4_downstream_le_20),  # ≤20年下游CH4排放 (kgCO2eq/yr)
        "annual_CH4_downstream_gt_20": clean_numeric_value(annual_CH4_downstream_gt_20),  # >20年下游CH4排放 (kgCO2eq/yr)
        
        # 中间计算值
        "climate_region": climate_region,
        "trophic_status": trophic_status,
        "reservoir_age": clean_numeric_value(reservoir_age),
        "surface_area_ha": clean_numeric_value(surface_area_ha),
        "F_CO2_tot": clean_numeric_value(F_CO2_tot),  # 年均CO2排放总量 (tCO2-C/yr)
    }

# 保持向后兼容的函数
def calculate_emissions(
    surface_area: float,
    ch4_ef: float,
    co2_ef: float,
    n2o_ef: float
) -> Tuple[float, float, float, float]:
    """
    计算总排放量（向后兼容函数）
    
    Args:
        surface_area: 水库面积 (km²)
        ch4_ef: CH4排放因子 (kg/km²/yr)
        co2_ef: CO2排放因子 (kg/km²/yr)
        n2o_ef: N2O排放因子 (kg/km²/yr)
    
    Returns:
        (CH4排放量, CO2排放量, N2O排放量, CO2当量) in kg/yr
    """
    ch4_total = surface_area * ch4_ef
    co2_total = surface_area * co2_ef
    n2o_total = surface_area * n2o_ef
    
    # 计算CO2当量
    co2_eq = co2_total + (ch4_total * GWP_100yr_CH4) + (n2o_total * 265)
    
    return ch4_total, co2_total, n2o_total, co2_eq

# 不确定性范围（作为均值的百分比）
UNCERTAINTY_RANGES = {
    "CH4": 0.50,  # ±50%
    "CO2": 0.40,  # ±40%
    "N2O": 0.60,  # ±60%
}