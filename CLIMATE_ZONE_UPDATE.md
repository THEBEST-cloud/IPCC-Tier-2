# 气候区判断功能更新说明

## 概述

已成功更新水库温室气体排放计算系统，现在支持基于Beck-Köppen-Geiger气候分类的精确气候区判断，并包含6种IPCC聚合气候区的完整排放因子表。

## 主要更新

### 1. 新增气候区判断模块 (`app/climate_zones.py`)

- **精确气候区判断**: 使用`Beck_KG_V1_present_0p0083.tif`文件进行基于经纬度的精确气候区判断
- **6种IPCC聚合气候区**: 支持北方、冷温带、暖温带干旱、暖温带湿润、热带干旱/山地、热带湿润/潮湿
- **后备机制**: 当气候区文件不可用时，自动使用基于纬度的简单判断

### 2. 更新排放因子表

根据IPCC指南更新了6种气候区的排放因子：

#### 时长大于20年
| 气候带 | CO2-C (t/ha·yr) | CH4地表排放 (kg/ha·yr) | CH4下游排放比率 |
|--------|----------------|----------------------|----------------|
| 北方 | - | 13.6 | 0.09 |
| 冷温带 | - | 54.0 | 0.09 |
| 暖温带干旱 | - | 150.9 | 0.09 |
| 暖温带湿润 | - | 80.3 | 0.09 |
| 热带干旱/山地 | - | 283.7 | 0.09 |
| 热带湿润/潮湿 | - | 141.1 | 0.09 |

#### 时长小于等于20年
| 气候带 | CO2-C (t/ha·yr) | CH4地表排放 (kg/ha·yr) | CH4下游排放比率 |
|--------|----------------|----------------------|----------------|
| 北方 | 0.94 | 27.7 | 0.09 |
| 冷温带 | 1.02 | 84.7 | 0.09 |
| 暖温带干旱 | 1.70 | 195.6 | 0.09 |
| 暖温带湿润 | 1.46 | 127.5 | 0.09 |
| 热带干旱/山地 | 2.95 | 392.3 | 0.09 |
| 热带湿润/潮湿 | 2.77 | 251.6 | 0.09 |

### 3. 更新核心计算模块 (`app/ipcc_tier1.py`)

- **经纬度输入**: `calculate_ipcc_tier1_emissions`函数现在需要经纬度参数
- **自动气候区判断**: 根据经纬度自动确定气候区
- **完整排放因子支持**: 支持所有6种气候区的排放因子

### 4. 更新API接口 (`app/main.py`)

- **经度参数**: API现在要求提供经度参数
- **自动气候区检测**: 系统自动根据经纬度确定气候区

## 使用方法

### 1. 准备气候区文件

将`Beck_KG_V1_present_0p0083.tif`文件放置在`app/static/`目录下。

### 2. API调用示例

```python
import requests

# 分析请求
analysis_request = {
    "latitude": 35.7,
    "longitude": 139.6,
    "surface_area": 10.0,  # km²
    "reservoir_age": 20,
    "water_quality": {
        "total_phosphorus": 0.05,  # mg/L
        "total_nitrogen": 0.8,     # mg/L
        "chlorophyll_a": 5.0,      # μg/L
        "secchi_depth": 2.0        # m
    }
}

response = requests.post("http://localhost:8000/api/analyze", json=analysis_request)
```

### 3. 直接使用气候区判断

```python
from app.climate_zones import get_ipcc_aggregated_zone_in_chinese

# 获取气候区
climate_zone = get_ipcc_aggregated_zone_in_chinese(35.7, 139.6)
print(f"气候区: {climate_zone}")
```

## 技术细节

### 柯本代码映射

系统将Beck-Köppen-Geiger分类的柯本代码映射到IPCC标准气候区，然后聚合为6种IPCC聚合气候区：

- **北方**: Boreal dry, Boreal moist, Polar dry, Polar moist
- **冷温带**: Cool temperate dry, Cool temperate moist
- **暖温带干旱**: Warm temperate dry
- **暖温带湿润**: Warm temperate moist
- **热带干旱/山地**: Tropical dry, Tropical montane
- **热带湿润/潮湿**: Tropical moist, Tropical wet

### 后备机制

当气候区文件不可用时，系统使用基于纬度的简单判断：
- 纬度 ≤ 25°: 热带湿润/潮湿
- 25° < 纬度 ≤ 50°: 暖温带湿润
- 纬度 > 50°: 北方

## 测试验证

系统已通过以下测试：
- ✅ 6种气候区排放因子完整性验证
- ✅ 基于经纬度的气候区判断功能测试
- ✅ 完整排放计算流程测试
- ✅ API接口兼容性测试

## 注意事项

1. **文件依赖**: 需要`Beck_KG_V1_present_0p0083.tif`文件才能进行精确的气候区判断
2. **经度参数**: 所有API调用现在都需要提供经度参数
3. **向后兼容**: 当气候区文件不可用时，系统会自动使用基于纬度的后备判断
4. **排放因子**: 所有排放因子都基于最新的IPCC指南

## 文件结构

```
app/
├── climate_zones.py          # 新增：气候区判断模块
├── ipcc_tier1.py            # 更新：支持6种气候区
├── main.py                  # 更新：API接口
├── schemas.py               # 已包含经度字段
└── static/
    └── Beck_KG_V1_present_0p0083.tif  # 需要添加的气候区文件
```