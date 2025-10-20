"""
IPCC Tier 1 Methodology for Reservoir Greenhouse Gas Emissions
严格遵循IPCC指南的Tier 1方法
"""

import numpy as np
import math
from typing import Tuple, Optional, Dict
from .climate_zones import get_ipcc_aggregated_zone_in_chinese, get_climate_zone_emission_factors

# IPCC Tier 1 常量定义
M_CO2 = 44  # CO2的相对分子质量
M_C = 12    # C元素的相对原子质量
R_d_i = 0.09  # 大坝下游CH4通量与水库表面CH4通量的比值
GWP_100yr_CH4 = 27.2  # 非化石源CH4的100年全球变暖潜势

# 气候区定义（基于经纬度和Beck-Köppen-Geiger分类）
def get_climate_region(latitude: float, longitude: float) -> str:
    """
    根据经纬度确定气候区（使用Beck-Köppen-Geiger分类）
    
    Args:
        latitude: 纬度（度）
        longitude: 经度（度）
    
    Returns:
        气候区名称
    """
    climate_zone = get_ipcc_aggregated_zone_in_chinese(latitude, longitude)
    if climate_zone:
        return climate_zone
    else:
        # 如果无法从文件获取，使用基于纬度的简单判断作为后备
        abs_lat = abs(latitude)
        if abs_lat <= 25:
            return "热带湿润/潮湿"  # 默认热带湿润
        elif abs_lat <= 50:
            return "暖温带湿润"  # 默认暖温带湿润
        else:
            return "北方"  # 默认北方

# IPCC Tier 1 排放因子表（6种IPCC聚合气候区）
EMISSION_FACTORS = get_climate_zone_emission_factors()

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
        climate_region = "暖温带湿润"  # 默认暖温带湿润区
    
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
    
    # 转换单位：tCO2-C/(ha·yr) -> kgCO2/(km²/yr) 碳转二氧化碳
    co2_ef = co2_ef * 100 * (M_CO2 / M_C)  # 100 ha/km² * 分子量转换
    
    # 转换单位：kgCH4/(ha·yr) -> kgCH4/(km²/yr)
    ch4_ef = ch4_ef * 100  # 100 ha/km²
    
    # N2O排放因子（IPCC Tier 1方法中通常忽略）
    n2o_ef = 0
    
    return ch4_ef, co2_ef, n2o_ef

def calculate_ipcc_tier1_emissions(
    surface_area_ha: float,
    latitude: float,
    longitude: float,
    trophic_status: str = "Mesotrophic",
    reservoir_age: float = 100,
    climate_region_override: Optional[str] = None
) -> Dict[str, float]:
    """
    按照IPCC Tier 1方法计算水库温室气体排放
    
    Args:
        surface_area_ha: 水库面积（公顷）
        latitude: 纬度
        longitude: 经度
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
        climate_region = get_climate_region(latitude, longitude)
    
    # # 第2步：获取排放因子
    # ch4_ef, co2_ef, n2o_ef = get_emission_factors(
    #     climate_region, trophic_status, reservoir_age
    # )
    
    # 第3步：CO2排放计算 (< 20年)
    # 从排放因子开始计算
    factors = EMISSION_FACTORS.get(climate_region, EMISSION_FACTORS["暖温带湿润"])
    EF_CO2_original = factors["EF_CO2_age_le_20"]  # 1.46 tCO₂-C/(ha·yr) 注意这是吨的单位，和甲烷kg不一样
    F_CO2_annual = surface_area_ha * EF_CO2_original
    E_CO2_total =  F_CO2_annual * min(20, reservoir_age)  # 20年CO2总排放量 (tCO₂-C)
    E_CO2_total = E_CO2_total * (M_CO2 / M_C)  # 转换为二氧化碳 (tCO₂)
    # 第4步：CH4排放计算 (贯穿两个阶段)
    # 获取不同年龄段的CH4排放因子
    factors = EMISSION_FACTORS.get(climate_region, EMISSION_FACTORS["暖温带湿润"])
    trophic_factor = TROPHIC_ADJUSTMENT_FACTORS.get(trophic_status, 3)  # 营养状态调整系数 αᵢ
    
    # 水库自身排放计算
    EF_CH4_le_20 = factors["EF_CH4_age_le_20"]  # ≤20年排放因子EF (kgCH₄ ha⁻¹ y⁻¹)
    EF_CH4_gt_20 = factors["EF_CH4_age_gt_20"]  # >20年排放因子EF (kgCH₄ ha⁻¹ y⁻¹)
    
    F_CH4_res_le_20_annual = trophic_factor * (EF_CH4_le_20 * surface_area_ha) / 1000  # ≤20年年均排放量 (tCH₄ y⁻¹)
    F_CH4_res_gt_20_annual = trophic_factor * (EF_CH4_gt_20 * surface_area_ha) / 1000 # >20年年均排放量 (tCH₄ y⁻¹)
    print(f"trophic_factor: {trophic_factor}")
    print(f"surface_area_ha: {surface_area_ha}")
    print(f"EF_CH4_le_20: {EF_CH4_le_20}")
    print(f"EF_CH4_gt_20: {EF_CH4_gt_20}")
    print(f"F_CH4_res_le_20_annual: {F_CH4_res_le_20_annual}")
    E_CH4_res_le_20 = F_CH4_res_le_20_annual * min(20, reservoir_age)  # <20年总排放量 (t CH₄)
    E_CH4_res_gt_20 = F_CH4_res_gt_20_annual * max(0, reservoir_age - 20) if reservoir_age > 20 else 0  # >20年总排放量 (t CH₄)
    
    # 下游排放计算
    R_d_i = 0.09  # flux CH4 downstream, R d,i
    F_CH4_downstream_le_20_annual = F_CH4_res_le_20_annual * R_d_i  # ≤20年下游年均排放量 (tCH₄ y⁻¹)
    F_CH4_downstream_gt_20_annual = F_CH4_res_gt_20_annual * R_d_i  # >20年下游年均排放量 (tCH₄ y⁻¹)
    
    E_CH4_downstream_le_20 = F_CH4_downstream_le_20_annual * min(20, reservoir_age)  # 20年迁移排放量 (tCH₄)
    E_CH4_downstream_gt_20 = F_CH4_downstream_gt_20_annual * max(0, reservoir_age - 20)  if reservoir_age > 20 else 0  # 20年后总排放量 (tCH₄)
    
    # 第5步：汇总与最终结果
    # CH4总排放量转换为CO2当量
    E_CH4_le_20_total = (E_CH4_res_le_20 + E_CH4_downstream_le_20) * GWP_100yr_CH4   # 20年CH4总排放量 (tCO₂eq)
    E_CH4_gt_20_total = (E_CH4_res_gt_20 + E_CH4_downstream_gt_20) * GWP_100yr_CH4   # >20年CH4总排放量 (tCO₂eq)
    E_CH4_total = E_CH4_le_20_total + E_CH4_gt_20_total  # CH4总排放量 (tCO₂eq)
    
    # 水库生命周期碳排放总量
    E_total = E_CO2_total + E_CH4_total  # 总排放量 (tCO₂eq)
    print(f"E_CO2_total: {E_CO2_total}")
    print(f"E_CH4_total: {E_CH4_total}")
    print(f"E_total: {E_total}")
    # 分阶段汇总
    E_le_20_total = E_CO2_total + E_CH4_le_20_total  # <20年总排放量 (tCO₂eq)
    E_gt_20_total = E_CH4_gt_20_total  # >20年总排放量 (tCO₂eq)
    
    # 计算年均排放量
    if reservoir_age <= 20:
        annual_CO2_kg = F_CO2_annual * (M_CO2 / M_C) * 1000  # kgCO2eq/yr
        annual_CH4_le_20_kg = F_CH4_res_le_20_annual * 1000 + F_CH4_downstream_le_20_annual * 1000  # kgCH₄ y⁻¹
        annual_CH4_gt_20_kg = 0
    else:
        annual_CO2_kg = F_CO2_annual * (M_CO2 / M_C) * 1000  # CO2排放已停止
        annual_CH4_le_20_kg = F_CH4_res_le_20_annual * 1000 + F_CH4_downstream_le_20_annual * 1000  # kgCH₄ y⁻¹
        annual_CH4_gt_20_kg = F_CH4_res_gt_20_annual * 1000 + F_CH4_downstream_gt_20_annual * 1000  # kgCH₄ y⁻¹
    
    # 水库表面和下游CH4排放的年均排放量
    annual_CH4_res_surface_le_20 = F_CH4_res_le_20_annual * 1000 # kgCH₄ y⁻¹
    annual_CH4_downstream_le_20 = F_CH4_downstream_le_20_annual * 1000  # kgCH₄ y⁻¹
    
    if reservoir_age > 20:
        annual_CH4_res_surface_gt_20 = F_CH4_res_gt_20_annual  * 1000  # kgCH₄ y⁻¹
        annual_CH4_downstream_gt_20 = F_CH4_downstream_gt_20_annual  * 1000  # kgCH₄ y⁻¹
    else:
        annual_CH4_res_surface_gt_20 = 0
        annual_CH4_downstream_gt_20 = 0
    
    return {
        # 主要结果
        "E_total": clean_numeric_value(E_total),  # 水库生命周期碳排放总量 (tCO2eq)
        "E_le_20_total": clean_numeric_value(E_le_20_total),  # <20年总排放量 (tCO2eq)
        "E_gt_20_total": clean_numeric_value(E_gt_20_total),  # >20年总排放量 (tCO2eq)
        
        # CO2排放计算 (< 20年)
        "EF_CO2": clean_numeric_value(EF_CO2_original),  # 排放因子EF (tCO₂-C ha⁻¹ y⁻¹)
        "F_CO2_annual": clean_numeric_value(F_CO2_annual),  # 年均排放量 (tCO₂-C y⁻¹)
        "E_CO2_20yr": clean_numeric_value(E_CO2_total),  # 20年CO2总排放量 (tCO₂-C)
        "E_CO2_total": clean_numeric_value(E_CO2_total),  # CO2总排放量 (tCO₂)
        
        # CH4排放计算 (贯穿两个阶段)
        "trophic_factor": clean_numeric_value(trophic_factor),  # 营养状态调整系数 αᵢ
        "EF_CH4_le_20": clean_numeric_value(EF_CH4_le_20),  # ≤20年排放因子EF (kgCH₄ ha⁻¹ y⁻¹)
        "EF_CH4_gt_20": clean_numeric_value(EF_CH4_gt_20),  # >20年排放因子EF (kgCH₄ ha⁻¹ y⁻¹)
        "R_d_i": clean_numeric_value(R_d_i),  # flux CH4 downstream, R d,i
        
        # 水库自身排放
        "F_CH4_res_le_20_annual": clean_numeric_value(F_CH4_res_le_20_annual),  # ≤20年年均排放量 (tCH₄ y⁻¹)
        "F_CH4_res_gt_20_annual": clean_numeric_value(F_CH4_res_gt_20_annual),  # >20年年均排放量 (tCH₄ y⁻¹)
        "E_CH4_res_le_20": clean_numeric_value(E_CH4_res_le_20),  # <20年总排放量 (tCH₄)
        "E_CH4_res_gt_20": clean_numeric_value(E_CH4_res_gt_20),  # >20年总排放量 (tCH₄)
        
        # 下游排放
        "F_CH4_downstream_le_20_annual": clean_numeric_value(F_CH4_downstream_le_20_annual),  # ≤20年下游年均排放量 (tCH₄ y⁻¹)
        "F_CH4_downstream_gt_20_annual": clean_numeric_value(F_CH4_downstream_gt_20_annual),  # >20年下游年均排放量 (tCH₄ y⁻¹)
        "E_CH4_downstream_le_20": clean_numeric_value(E_CH4_downstream_le_20),  # 20年迁移排放量 (tCH₄)
        "E_CH4_downstream_gt_20": clean_numeric_value(E_CH4_downstream_gt_20),  # 20年后总排放量 (tCH₄)
        
        # CH4总排放量
        "E_CH4_le_20_total": clean_numeric_value(E_CH4_le_20_total),  # 20年CH4总排放量 (tCO₂eq)
        "E_CH4_gt_20_total": clean_numeric_value(E_CH4_gt_20_total),  # >20年CH4总排放量 (tCO₂eq)
        "E_CH4_total": clean_numeric_value(E_CH4_total),  # CH4总排放量 (tCO₂eq)
        
        # 年均排放量
        "annual_CO2": clean_numeric_value(annual_CO2_kg),  # 年均CO2排放量 (kgCO2eq/yr)
        "annual_CH4_le_20": clean_numeric_value(annual_CH4_le_20_kg),  # ≤20年CH4年均排放量 (kgCO2eq/yr)
        "annual_CH4_gt_20": clean_numeric_value(annual_CH4_gt_20_kg),  # >20年CH4年均排放量 (kgCO2eq/yr)
        
        # 分源CH4排放
        "annual_CH4_res_surface_le_20": clean_numeric_value(annual_CH4_res_surface_le_20),  # ≤20年水库表面CH4排放 (kgCO2eq/yr)
        "annual_CH4_res_surface_gt_20": clean_numeric_value(annual_CH4_res_surface_gt_20),  # >20年水库表面CH4排放 (kgCO2eq/yr)
        "annual_CH4_downstream_le_20": clean_numeric_value(annual_CH4_downstream_le_20),  # ≤20年下游CH4排放 (kgCO2eq/yr)
        "annual_CH4_downstream_gt_20": clean_numeric_value(annual_CH4_downstream_gt_20),  # >20年下游CH4排放 (kgCO2eq/yr)
        
        # 输入参数
        "climate_region": climate_region,
        "trophic_status": trophic_status,
        "reservoir_age": clean_numeric_value(reservoir_age),
        "surface_area_ha": clean_numeric_value(surface_area_ha),
        
        # 排放因子
        "EF_CO2_age_le_20": clean_numeric_value(factors["EF_CO2_age_le_20"]),  # CO2排放因子 (tCO2-C/(ha·yr))
        "EF_CH4_age_le_20": clean_numeric_value(factors["EF_CH4_age_le_20"]),  # ≤20年CH4排放因子 (kgCH4/(ha·yr))
        "EF_CH4_age_gt_20": clean_numeric_value(factors["EF_CH4_age_gt_20"]),  # >20年CH4排放因子 (kgCH4/(ha·yr))
        "trophic_factor": clean_numeric_value(trophic_factor),  # 营养状态调整系数
        
        # 中间计算值
        "F_CO2_annual": clean_numeric_value(F_CO2_annual),  # 年均CO2排放总量 (tCO2-C/yr)
        "F_CH4_res_le_20_annual": clean_numeric_value(F_CH4_res_le_20_annual),  # ≤20年水库表面CH4排放 (tCH4/yr)
        "F_CH4_downstream_le_20_annual": clean_numeric_value(F_CH4_downstream_le_20_annual),  # ≤20年下游CH4排放 (tCH4/yr)
        "F_CH4_res_gt_20_annual": clean_numeric_value(F_CH4_res_gt_20_annual),  # >20年水库表面CH4排放 (tCH4/yr)
        "F_CH4_downstream_gt_20_annual": clean_numeric_value(F_CH4_downstream_gt_20_annual),  # >20年下游CH4排放 (tCH4/yr)
        
        # 分阶段CH4排放总量
        "E_CH4_le_20_total": clean_numeric_value(E_CH4_le_20_total),  # ≤20年CH4排放总量 (tCO2eq)
        "E_CH4_gt_20_total": clean_numeric_value(E_CH4_gt_20_total),  # >20年CH4排放总量 (tCO2eq)
        
        # 常量
        "M_CO2": M_CO2,  # CO2相对分子质量
        "M_C": M_C,  # C相对原子质量
        "R_d_i": R_d_i,  # 下游CH4通量比值
        "GWP_100yr_CH4": GWP_100yr_CH4,  # CH4全球变暖潜势
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