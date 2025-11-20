"""
基于Beck-Köppen-Geiger气候分类的IPCC聚合气候区判断模块
使用Beck_KG_V1_present_0p0083.tif文件进行精确的气候区判断
"""

import rasterio
import numpy as np
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
        # 检查坐标是否在有效范围内
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            print(f"坐标超出范围: ({lat}, {lon})")
            return None
            
        try:
            with rasterio.open(path) as src:
                value = next(src.sample([(lon, lat)]))[0]
                # 检查值是否有效
                if value is None or np.isnan(value) or value == 0:
                    print(f"无效的气候代码: {value} at ({lat}, {lon})")
                    return None
                return int(value)
        except Exception as e:
            print(f"读取文件 '{path}' 时出错: {e}")
            return None

    # 内部辅助函数：将柯本代码映射到IPCC气候区
    def _map_koppen_code_to_ipcc_zone(koppen_code: int) -> Tuple[str, str, int]:
        # 柯本代码到IPCC标准气候区的映射（基于Beck-Köppen-Geiger分类）
        koppen_to_standard_ipcc = {
            # 无效或海洋区域
            0: "Tropical moist",  # 默认处理为热带湿润
            
            # 热带气候 (A)
            1: "Tropical moist", 2: "Tropical moist", 3: "Tropical dry",
            
            # 干旱气候 (B)
            4: "Warm temperate dry", 5: "Warm temperate dry", 6: "Warm temperate dry", 
            7: "Warm temperate dry", 8: "Warm temperate dry",
            
            # 温带气候 (C)
            9: "Warm temperate moist",   # Cfa - 温暖湿润气候
            10: "Cool temperate moist",  # Cfb - 海洋性气候
            11: "Cool temperate moist",  # Cfc - 亚极地海洋性气候
            12: "Warm temperate moist",  # Csa - 地中海气候
            13: "Warm temperate moist",  # Csb - 地中海气候
            14: "Warm temperate moist",  # Csc - 地中海气候
            15: "Warm temperate moist",  # Cwa - 温暖湿润气候
            16: "Cool temperate moist",  # Cwb - 海洋性气候
            17: "Cool temperate moist",  # Cwc - 亚极地海洋性气候
            18: "Warm temperate moist",  # Cfa - 温暖湿润气候
            19: "Cool temperate moist",  # Cfb - 海洋性气候
            20: "Cool temperate moist",  # Cfc - 亚极地海洋性气候
            21: "Warm temperate moist",  # Csa - 地中海气候
            22: "Warm temperate moist",  # Csb - 地中海气候
            23: "Warm temperate moist",  # Csc - 地中海气候
            24: "Warm temperate moist",  # Cwa - 温暖湿润气候
            25: "Cool temperate moist",  # Cwb - 海洋性气候
            26: "Cool temperate moist",  # Cwc - 亚极地海洋性气候
            
            # 大陆性气候 (D)
            27: "Cool temperate moist",  # Dfa - 温暖大陆性气候
            28: "Cool temperate moist",  # Dfb - 冷大陆性气候
            29: "Boreal moist",          # Dfc - 亚极地气候
            30: "Boreal moist",          # Dfd - 极地气候
            
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

def get_climate_zone_details(lat: float, lon: float, geotiff_path: str = './app/static/Beck_KG_V1_present_0p0083.tif') -> Optional[Dict[str, str]]:
    """
    返回映射前与映射后的气候带详细信息：
    - koppen_code: Beck-Köppen-Geiger 原始代码（数值）
    - standard_zone_en: IPCC标准气候区（英文，映射前）
    - aggregated_zone_en: IPCC聚合气候区（英文，映射后）
    - aggregated_zone_cn: IPCC聚合气候区（中文，映射后，供前端/报告显示）

    若查询失败返回 None。
    """
    if not os.path.exists(geotiff_path):
        print(f"气候区文件不存在: {geotiff_path}")
        return None

    # 复用内部辅助函数：从本地文件获取气候代码
    def _get_climate_code_from_local_file(lat: float, lon: float, path: str) -> Optional[int]:
        try:
            with rasterio.open(path) as dataset:
                # 将经纬度转换为栅格坐标
                row, col = dataset.index(lon, lat)
                # 读取该像素的值
                value = dataset.read(1)[row, col]
                if np.isnan(value):
                    return None
                return int(value)
        except Exception as e:
            print(f"读取气候区文件失败: {e}")
            return None

    # 复用映射函数：将柯本代码映射到IPCC标准/聚合气候区
    def _map_koppen_code_to_ipcc_zone(koppen_code: int) -> Tuple[str, str, int]:
        koppen_to_standard_ipcc = {
            0: "Tropical moist",
            1: "Tropical moist", 2: "Tropical moist", 3: "Tropical dry",
            4: "Warm temperate dry", 5: "Warm temperate dry", 6: "Warm temperate dry", 
            7: "Warm temperate dry", 8: "Warm temperate dry",
            9: "Warm temperate moist", 10: "Cool temperate moist", 11: "Cool temperate moist",
            12: "Warm temperate moist", 13: "Warm temperate moist", 14: "Warm temperate moist",
            15: "Warm temperate moist", 16: "Cool temperate moist", 17: "Cool temperate moist",
            18: "Warm temperate moist", 19: "Cool temperate moist", 20: "Cool temperate moist",
            21: "Warm temperate moist", 22: "Warm temperate moist", 23: "Warm temperate moist",
            24: "Warm temperate moist", 25: "Cool temperate moist", 26: "Cool temperate moist",
            27: "Cool temperate moist", 28: "Cool temperate moist", 29: "Boreal moist",
            30: "Boreal moist", 31: "Boreal", 32: "Boreal", 33: "Boreal", 34: "Boreal",
            35: "Boreal", 36: "Boreal",
            37: "Tropical dry/montane", 38: "Tropical dry/montane", 39: "Tropical dry/montane",
            40: "Tropical dry/montane", 41: "Tropical dry/montane", 42: "Tropical dry/montane",
            43: "Tropical dry/montane", 44: "Tropical dry/montane", 45: "Tropical dry/montane",
            46: "Tropical dry/montane", 47: "Tropical dry/montane", 48: "Tropical dry/montane",
            49: "Tropical dry/montane", 50: "Tropical dry/montane"
        }

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

    TRANSLATION_DICT = {
        "Boreal": "北方",
        "Cool temperate": "冷温带",
        "Warm temperate dry": "暖温带干旱",
        "Warm temperate moist": "暖温带湿润",
        "Tropical dry/montane": "热带干旱/山地",
        "Tropical moist/wet": "热带湿润/潮湿"
    }

    # 额外补充：数值代码 → 柯本字母代码 & 中文名称（覆盖常见30类）
    KOPPEN_NUM_TO_STR = {
        1: 'Af', 2: 'Am', 3: 'Aw',
        4: 'BWh', 5: 'BWk', 6: 'BSh', 7: 'BSk',
        8: 'Csa', 9: 'Csb', 10: 'Csc',
        11: 'Cwa', 12: 'Cwb', 13: 'Cwc',
        14: 'Cfa', 15: 'Cfb', 16: 'Cfc',
        17: 'Dsa', 18: 'Dsb', 19: 'Dsc', 20: 'Dsd',
        21: 'Dwa', 22: 'Dwb', 23: 'Dwc', 24: 'Dwd',
        25: 'Dfa', 26: 'Dfb', 27: 'Dfc', 28: 'Dfd',
        29: 'ET', 30: 'EF'
    }

    KOPPEN_STR_TO_CN = {
        'Af': '热带雨林',
        'Am': '热带季风',
        'Aw': '热带草原',
        'BWh': '热沙漠',
        'BWk': '冷沙漠',
        'BSh': '热草原（半干旱）',
        'BSk': '冷草原（半干旱）',
        'Csa': '地中海炎热夏季',
        'Csb': '地中海暖夏',
        'Csc': '地中海冷夏',
        'Cwa': '温带冬季干燥·炎热夏季',
        'Cwb': '温带冬季干燥·温暖夏季',
        'Cwc': '温带冬季干燥·寒冷夏季',
        'Cfa': '温带无干季·炎热夏季（湿润亚热带）',
        'Cfb': '温带无干季·温和夏季（海洋性）',
        'Cfc': '温带无干季·寒冷夏季（亚极地海洋性）',
        'Dsa': '冷带夏季干燥·炎热夏季',
        'Dsb': '冷带夏季干燥·温暖夏季',
        'Dsc': '冷带夏季干燥·寒冷夏季',
        'Dsd': '冷带夏季干燥·严寒冬季',
        'Dwa': '冷带冬季干燥·炎热夏季',
        'Dwb': '冷带冬季干燥·温暖夏季',
        'Dwc': '冷带冬季干燥·寒冷夏季',
        'Dwd': '冷带冬季干燥·严寒冬季',
        'Dfa': '冷带无干季·炎热夏季',
        'Dfb': '冷带无干季·温暖夏季',
        'Dfc': '冷带无干季·寒冷夏季',
        'Dfd': '冷带无干季·严寒冬季',
        'ET': '苔原',
        'EF': '冰原'
    }

    try:
        code = _get_climate_code_from_local_file(lat, lon, geotiff_path)
        if code is None:
            return None
        aggregated_en, standard_en, koppen_code = _map_koppen_code_to_ipcc_zone(code)
        aggregated_cn = TRANSLATION_DICT.get(aggregated_en, "翻译失败")
        koppen_code_str = KOPPEN_NUM_TO_STR.get(koppen_code)
        koppen_cn_name = KOPPEN_STR_TO_CN.get(koppen_code_str) if koppen_code_str else None
        return {
            "koppen_code": str(koppen_code),
            "koppen_code_str": koppen_code_str,
            "koppen_cn_name": koppen_cn_name,
            "standard_zone_en": standard_en,
            "aggregated_zone_en": aggregated_en,
            "aggregated_zone_cn": aggregated_cn,
        }
    except Exception as e:
        print(f"气候区详细信息获取失败: {e}")
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

def map_standard_to_aggregated_cn(standard_en: str) -> Optional[str]:
    """
    将IPCC标准气候区（英文，映射前）映射到聚合气候区（中文，供计算使用）。

    支持的标准气候区示例：
    - "Tropical moist"
    - "Tropical dry"
    - "Warm temperate dry"
    - "Warm temperate moist"
    - "Cool temperate moist"
    - "Boreal moist"
    - "Boreal"

    返回中文聚合气候区名称，如 "暖温带湿润"、"冷温带" 等。
    """
    if not standard_en:
        return None

    standard_to_aggregated = {
        "Boreal dry": "Boreal",
        "Boreal moist": "Boreal",
        "Polar dry": "Boreal",
        "Polar moist": "Boreal",
        "Cool temperate dry": "Cool temperate",
        "Cool temperate moist": "Cool temperate",
        "Warm temperate dry": "Warm temperate dry",
        "Warm temperate moist": "Warm temperate moist",
        "Tropical dry": "Tropical dry/montane",
        "Tropical montane": "Tropical dry/montane",
        "Tropical moist": "Tropical moist/wet",
        "Tropical wet": "Tropical moist/wet",
        # 一些数据源可能直接给出合并后的标准（聚合英文）
        "Boreal": "Boreal",
        "Cool temperate": "Cool temperate",
        "Warm temperate dry": "Warm temperate dry",
        "Warm temperate moist": "Warm temperate moist",
        "Tropical dry/montane": "Tropical dry/montane",
        "Tropical moist/wet": "Tropical moist/wet",
    }

    TRANSLATION_DICT = {
        "Boreal": "北方",
        "Cool temperate": "冷温带",
        "Warm temperate dry": "暖温带干旱",
        "Warm temperate moist": "暖温带湿润",
        "Tropical dry/montane": "热带干旱/山地",
        "Tropical moist/wet": "热带湿润/潮湿",
    }

    aggregated_en = standard_to_aggregated.get(standard_en)
    if not aggregated_en:
        # 标准化大小写和空格以提高兼容性
        key = standard_en.strip()
        aggregated_en = standard_to_aggregated.get(key)
    if not aggregated_en:
        # 直接将聚合英文映射为中文（如果输入已是聚合英文）
        direct = TRANSLATION_DICT.get(key)
        if direct:
            return direct
        return None
    return TRANSLATION_DICT.get(aggregated_en)

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