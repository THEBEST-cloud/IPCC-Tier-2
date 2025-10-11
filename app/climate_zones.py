"""
基于Beck-Köppen-Geiger气候分类的IPCC聚合气候区判断模块
使用Beck_KG_V1_present_0p0083.tif文件进行精确的气候区判断
"""

import rasterio
from typing import Optional, Tuple, Dict
import os

def get_ipcc_aggregated_zone_in_chinese(lat: float, lon: float, geotiff_path: str = './app/static/Beck_KG_V1_present_0p0083.tif') -> Optional[str]:
    """
    输入经纬度，直接返回其对应的IPCC六大聚合气候区的中文名称。

    参数:
    lat (float): 要查询的纬度
    lon (float): 要查询的经度
    geotiff_path (str, optional): 气候数据文件的路径. 默认为 './app/static/Beck_KG_V1_present_0p0083.tif'

    返回:
    str: IPCC聚合气候区的中文名称，如果失败则返回 None
    """
    # 检查文件是否存在
    if not os.path.exists(geotiff_path):
        print(f"气候区文件不存在: {geotiff_path}")
        return None
    
    # 内部辅助函数：从本地文件获取气候代码
    def _get_climate_code_from_local_file(lat: float, lon: float, path: str) -> Optional[int]:
        try:
            with rasterio.open(path) as src:
                value = next(src.sample([(lon, lat)]))[0]
                return int(value)
        except Exception as e:
            print(f"读取文件 '{path}' 时出错: {e}")
            return None

    # 内部辅助函数：将柯本代码映射到IPCC气候区
    def _map_koppen_code_to_ipcc_zone(koppen_code: int) -> Tuple[str, str, int]:
        # 柯本代码到IPCC标准气候区的映射（基于Beck-Köppen-Geiger分类）
        koppen_to_standard_ipcc = {
            # 热带气候 (A)
            1: "Tropical moist", 2: "Tropical moist", 3: "Tropical dry",
            
            # 干旱气候 (B)
            4: "Warm temperate dry", 5: "Warm temperate dry", 6: "Warm temperate dry", 
            7: "Warm temperate dry", 8: "Warm temperate dry",
            
            # 温带气候 (C)
            9: "Cool temperate moist", 10: "Cool temperate moist", 11: "Warm temperate moist", 
            12: "Cool temperate moist", 13: "Cool temperate moist", 14: "Warm temperate moist", 
            15: "Cool temperate moist", 16: "Cool temperate moist", 17: "Warm temperate moist", 
            18: "Cool temperate moist", 19: "Cool temperate moist", 20: "Cool temperate moist", 
            21: "Warm temperate moist", 22: "Cool temperate moist", 25: "Warm temperate moist", 
            26: "Cool temperate moist",
            
            # 大陆性气候 (D)
            23: "Boreal moist", 24: "Boreal moist", 27: "Boreal moist", 28: "Boreal moist", 
            29: "Polar moist", 30: "Polar moist",
            
            # 极地气候 (E)
            31: "Boreal", 32: "Boreal", 33: "Boreal", 34: "Boreal", 35: "Boreal", 36: "Boreal",
            
            # 高原气候和其他特殊情况
            37: "Tropical dry/montane", 38: "Tropical dry/montane", 39: "Tropical dry/montane",
            40: "Tropical dry/montane", 41: "Tropical dry/montane", 42: "Tropical dry/montane",
            43: "Tropical dry/montane", 44: "Tropical dry/montane", 45: "Tropical dry/montane",
            46: "Tropical dry/montane", 47: "Tropical dry/montane", 48: "Tropical dry/montane",
            49: "Tropical dry/montane", 50: "Tropical dry/montane"
        }
        
        # IPCC标准气候区到聚合气候区的映射
        standard_to_aggregated = {
            "Boreal dry": "Boreal", "Boreal moist": "Boreal", 
            "Polar dry": "Boreal", "Polar moist": "Boreal",
            "Cool temperate dry": "Cool temperate", "Cool temperate moist": "Cool temperate",
            "Warm temperate dry": "Warm temperate dry",
            "Warm temperate moist": "Warm temperate moist",
            "Tropical dry": "Tropical dry/montane", "Tropical montane": "Tropical dry/montane",
            "Tropical moist": "Tropical moist/wet", "Tropical wet": "Tropical moist/wet"
        }
        
        standard_zone = koppen_to_standard_ipcc.get(koppen_code, "Unknown")
        if standard_zone == "Unknown": 
            raise ValueError(f"未知的柯本代码: {koppen_code}")
        
        aggregated_zone = standard_to_aggregated.get(standard_zone, "未找到对应的IPCC聚合气候区")
        if aggregated_zone == "未找到对应的IPCC聚合气候区":
            raise ValueError(f"未找到对应的IPCC聚合气候区: {standard_zone}")
        
        return aggregated_zone, standard_zone, koppen_code

    # 中英文翻译字典
    TRANSLATION_DICT = {
        "Boreal": "北方",
        "Cool temperate": "冷温带",
        "Warm temperate dry": "暖温带干旱",
        "Warm temperate moist": "暖温带湿润",
        "Tropical dry/montane": "热带干旱/山地",
        "Tropical moist/wet": "热带湿润/潮湿"
    }

    # 函数执行体
    try:
        koppen_code = _get_climate_code_from_local_file(lat, lon, geotiff_path)
        if koppen_code is None: 
            return None
        
        result = _map_koppen_code_to_ipcc_zone(koppen_code)
        aggregated_zone_en, _, _ = result
        
        # 返回中文翻译
        return TRANSLATION_DICT.get(aggregated_zone_en, "翻译失败")
        
    except Exception as e:
        print(f"气候区判断失败: {e}")
        return None

def get_climate_zone_emission_factors() -> Dict[str, Dict[str, float]]:
    """
    获取6种IPCC聚合气候区的排放因子
    
    返回:
        Dict: 包含6种气候区排放因子的字典
    """
    return {
        "北方": {
            "EF_CO2_age_le_20": 0.94,  # tCO2-C/(ha·yr)
            "EF_CH4_age_le_20": 27.7,  # kgCH4/(ha·yr)
            "EF_CH4_age_gt_20": 13.6,  # kgCH4/(ha·yr)
        },
        "冷温带": {
            "EF_CO2_age_le_20": 1.02,  # tCO2-C/(ha·yr)
            "EF_CH4_age_le_20": 84.7,  # kgCH4/(ha·yr)
            "EF_CH4_age_gt_20": 54.0,  # kgCH4/(ha·yr)
        },
        "暖温带干旱": {
            "EF_CO2_age_le_20": 1.70,  # tCO2-C/(ha·yr)
            "EF_CH4_age_le_20": 195.6,  # kgCH4/(ha·yr)
            "EF_CH4_age_gt_20": 150.9,  # kgCH4/(ha·yr)
        },
        "暖温带湿润": {
            "EF_CO2_age_le_20": 1.46,  # tCO2-C/(ha·yr)
            "EF_CH4_age_le_20": 127.5,  # kgCH4/(ha·yr)
            "EF_CH4_age_gt_20": 80.3,  # kgCH4/(ha·yr)
        },
        "热带干旱/山地": {
            "EF_CO2_age_le_20": 2.95,  # tCO2-C/(ha·yr)
            "EF_CH4_age_le_20": 392.3,  # kgCH4/(ha·yr)
            "EF_CH4_age_gt_20": 283.7,  # kgCH4/(ha·yr)
        },
        "热带湿润/潮湿": {
            "EF_CO2_age_le_20": 2.77,  # tCO2-C/(ha·yr)
            "EF_CH4_age_le_20": 251.6,  # kgCH4/(ha·yr)
            "EF_CH4_age_gt_20": 141.1,  # kgCH4/(ha·yr)
        }
    }

def get_available_climate_zones() -> list:
    """
    获取所有可用的气候区列表
    
    返回:
        list: 包含所有6种气候区名称的列表
    """
    return [
        "北方",
        "冷温带", 
        "暖温带干旱",
        "暖温带湿润",
        "热带干旱/山地",
        "热带湿润/潮湿"
    ]

# 使用示例
if __name__ == "__main__":
    # 测试坐标
    latitude = 35.7
    longitude = 139.6
    
    print(f"正在查询坐标 (纬度: {latitude}, 经度: {longitude}) 对应的IPCC聚合气候带...")
    
    # 调用封装好的主函数
    final_zone_chinese = get_ipcc_aggregated_zone_in_chinese(latitude, longitude)
    
    # 打印最终的中文结果
    if final_zone_chinese:
        print("\n----------------------------------------------------")
        print(f"查询成功！\n最终结果: '{final_zone_chinese}'")
        print("----------------------------------------------------")
        
        # 显示对应的排放因子
        factors = get_climate_zone_emission_factors()
        if final_zone_chinese in factors:
            print(f"\n{final_zone_chinese}气候区的排放因子:")
            for key, value in factors[final_zone_chinese].items():
                print(f"  {key}: {value}")
    else:
        print("\n查询失败，请检查上方的错误提示。")