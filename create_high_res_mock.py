#!/usr/bin/env python3
"""
创建高分辨率的模拟GeoTIFF文件
"""

import numpy as np
import rasterio
from rasterio.transform import from_bounds
import os

def create_high_res_mock_geotiff():
    """创建一个高分辨率的模拟GeoTIFF文件"""
    # 创建高分辨率全球网格 (0.1度分辨率)
    width, height = 3600, 1800  # 0.1度分辨率
    data = np.zeros((height, width), dtype=np.uint8)
    
    print(f"创建 {width}x{height} 分辨率的模拟GeoTIFF文件...")
    
    # 根据纬度和经度分配不同的气候区代码
    for i in range(height):
        lat = 90 - (i / height) * 180  # 从90度北纬到-90度南纬
        abs_lat = abs(lat)
        
        for j in range(width):
            lon = -180 + (j / width) * 360  # 从-180度到180度
            
            # 根据纬度和经度分配气候区代码
            if abs_lat > 70:
                # 极地气候
                data[i, j] = 31 + (i % 6)  # 31-36
            elif abs_lat > 50:
                # 北方/大陆性气候
                if lat > 0:  # 北半球
                    data[i, j] = 23 + (i % 8)  # 23-30
                else:  # 南半球
                    data[i, j] = 23 + (i % 8)  # 23-30
            elif abs_lat > 30:
                # 温带气候
                if lat > 0:  # 北半球
                    if lon > 0:  # 东半球
                        data[i, j] = 9 + (i % 18)  # 9-26
                    else:  # 西半球
                        data[i, j] = 9 + (i % 18)  # 9-26
                else:  # 南半球
                    if lon > 0:  # 东半球
                        data[i, j] = 9 + (i % 18)  # 9-26
                    else:  # 西半球
                        data[i, j] = 9 + (i % 18)  # 9-26
            elif abs_lat > 15:
                # 亚热带/暖温带
                if lat > 0:  # 北半球
                    if lon > 0:  # 东半球
                        data[i, j] = 4 + (i % 5)  # 4-8 (干旱)
                    else:  # 西半球
                        data[i, j] = 4 + (i % 5)  # 4-8 (干旱)
                else:  # 南半球
                    if lon > 0:  # 东半球
                        data[i, j] = 4 + (i % 5)  # 4-8 (干旱)
                    else:  # 西半球
                        data[i, j] = 4 + (i % 5)  # 4-8 (干旱)
            else:
                # 热带气候
                if abs_lat < 5:
                    # 赤道附近 - 热带湿润
                    data[i, j] = 1 + (i % 2)  # 1-2
                else:
                    # 热带其他地区
                    data[i, j] = 3  # 热带干旱
    
    # 设置地理变换
    transform = from_bounds(-180, -90, 180, 90, width, height)
    
    # 确保目录存在
    os.makedirs('./app/static', exist_ok=True)
    
    # 写入GeoTIFF文件
    with rasterio.open(
        './app/static/Beck_KG_V1_present_0p0083.tif',
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=data.dtype,
        crs='EPSG:4326',
        transform=transform,
        compress='lzw'  # 压缩以减小文件大小
    ) as dst:
        dst.write(data, 1)
    
    print(f"✓ 创建了高分辨率GeoTIFF文件: {width}x{height}")
    print(f"  分辨率: {180/height:.3f}度 x {360/width:.3f}度")
    print(f"  文件大小: {os.path.getsize('./app/static/Beck_KG_V1_present_0p0083.tif') / 1024 / 1024:.2f} MB")

def test_climate_zones():
    """测试气候区判断"""
    print("\n测试气候区判断...")
    
    try:
        from app.climate_zones import get_ipcc_aggregated_zone_in_chinese
        
        # 测试不同坐标
        test_coordinates = [
            (35.7, 139.6, "东京"),
            (39.9, 116.4, "北京"),
            (1.3, 103.8, "新加坡"),
            (55.7, 12.6, "哥本哈根"),
            (64.1, -21.9, "雷克雅未克"),
            (-22.9, -43.2, "里约热内卢"),
            (40.7, -74.0, "纽约"),
            (51.5, -0.1, "伦敦"),
            (-33.9, 18.4, "开普敦"),
            (35.0, 105.0, "中国中部"),
        ]
        
        for lat, lon, city in test_coordinates:
            try:
                climate_zone = get_ipcc_aggregated_zone_in_chinese(lat, lon)
                if climate_zone:
                    print(f"✓ {city} ({lat}, {lon}) -> {climate_zone}")
                else:
                    print(f"✗ {city} ({lat}, {lon}) -> 无法确定气候区")
            except Exception as e:
                print(f"✗ {city} ({lat}, {lon}) -> 错误: {e}")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")

def main():
    """主函数"""
    print("创建高分辨率模拟GeoTIFF文件...")
    create_high_res_mock_geotiff()
    
    print("\n测试气候区判断功能...")
    test_climate_zones()
    
    print("\n=== 完成 ===")

if __name__ == "__main__":
    main()