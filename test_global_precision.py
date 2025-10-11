#!/usr/bin/env python3
"""
测试全球气候区判断精度
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_global_climate_zones():
    """测试全球不同地区的气候区判断"""
    print("测试全球气候区判断精度...")
    
    try:
        from app.climate_zones import get_ipcc_aggregated_zone_in_chinese
        
        # 全球测试坐标
        test_coordinates = [
            # 亚洲
            (35.7, 139.6, "东京", "暖温带湿润"),
            (39.9, 116.4, "北京", "暖温带干旱"),
            (1.3, 103.8, "新加坡", "热带湿润/潮湿"),
            (22.3, 114.2, "香港", "热带湿润/潮湿"),
            (28.6, 77.2, "新德里", "热带干旱/山地"),
            (55.7, 37.6, "莫斯科", "北方"),
            (35.0, 105.0, "中国中部", "暖温带湿润"),
            
            # 欧洲
            (51.5, -0.1, "伦敦", "冷温带"),
            (48.9, 2.3, "巴黎", "冷温带"),
            (55.7, 12.6, "哥本哈根", "冷温带"),
            (64.1, -21.9, "雷克雅未克", "北方"),
            (52.5, 13.4, "柏林", "冷温带"),
            (41.9, 12.5, "罗马", "暖温带湿润"),
            (40.4, -3.7, "马德里", "暖温带干旱"),
            
            # 北美洲
            (40.7, -74.0, "纽约", "冷温带"),
            (34.1, -118.2, "洛杉矶", "暖温带干旱"),
            (41.9, -87.6, "芝加哥", "冷温带"),
            (49.3, -123.1, "温哥华", "冷温带"),
            (25.8, -80.3, "迈阿密", "热带湿润/潮湿"),
            (29.8, -95.4, "休斯顿", "暖温带湿润"),
            (45.5, -73.6, "蒙特利尔", "冷温带"),
            
            # 南美洲
            (-22.9, -43.2, "里约热内卢", "热带湿润/潮湿"),
            (-34.6, -58.4, "布宜诺斯艾利斯", "暖温带湿润"),
            (-12.0, -77.0, "利马", "热带干旱/山地"),
            (-33.9, 18.4, "开普敦", "暖温带干旱"),
            (4.6, -74.1, "波哥大", "热带干旱/山地"),
            (-15.8, -47.9, "巴西利亚", "热带湿润/潮湿"),
            
            # 非洲
            (30.0, 31.2, "开罗", "暖温带干旱"),
            (-1.3, 36.8, "内罗毕", "热带干旱/山地"),
            (6.5, 3.4, "拉各斯", "热带湿润/潮湿"),
            (-26.2, 28.0, "约翰内斯堡", "暖温带干旱"),
            (14.7, -17.5, "达喀尔", "热带干旱/山地"),
            (9.0, 38.8, "亚的斯亚贝巴", "热带干旱/山地"),
            
            # 大洋洲
            (-33.9, 151.2, "悉尼", "暖温带湿润"),
            (-37.8, 145.0, "墨尔本", "冷温带"),
            (-12.5, 130.8, "达尔文", "热带干旱/山地"),
            (-31.9, 115.9, "珀斯", "暖温带干旱"),
            (-36.8, 174.8, "奥克兰", "冷温带"),
            (-25.3, 152.9, "布里斯班", "暖温带湿润"),
        ]
        
        success_count = 0
        total_count = len(test_coordinates)
        
        print(f"\n测试 {total_count} 个全球坐标点...")
        print("=" * 80)
        
        for lat, lon, city, expected in test_coordinates:
            try:
                climate_zone = get_ipcc_aggregated_zone_in_chinese(lat, lon)
                if climate_zone:
                    # 简单的合理性检查
                    is_reasonable = check_climate_reasonableness(lat, lon, climate_zone)
                    status = "✓" if is_reasonable else "?"
                    print(f"{status} {city:15} ({lat:6.1f}, {lon:7.1f}) -> {climate_zone:15} (预期: {expected})")
                    if is_reasonable:
                        success_count += 1
                else:
                    print(f"✗ {city:15} ({lat:6.1f}, {lon:7.1f}) -> 无法确定气候区")
            except Exception as e:
                print(f"✗ {city:15} ({lat:6.1f}, {lon:7.1f}) -> 错误: {e}")
        
        print("=" * 80)
        print(f"测试结果: {success_count}/{total_count} 通过 ({success_count/total_count*100:.1f}%)")
        
        return success_count, total_count
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return 0, 0

def check_climate_reasonableness(lat, lon, climate_zone):
    """检查气候区判断的合理性"""
    abs_lat = abs(lat)
    
    # 基于纬度的合理性检查
    if abs_lat > 60:
        # 高纬度应该是北方或冷温带
        return climate_zone in ["北方", "冷温带"]
    elif abs_lat > 40:
        # 中纬度可能是冷温带、暖温带或北方
        return climate_zone in ["冷温带", "暖温带湿润", "暖温带干旱", "北方"]
    elif abs_lat > 20:
        # 低中纬度可能是暖温带或热带
        return climate_zone in ["暖温带湿润", "暖温带干旱", "热带湿润/潮湿", "热带干旱/山地"]
    else:
        # 低纬度应该是热带
        return climate_zone in ["热带湿润/潮湿", "热带干旱/山地"]

def test_resolution_accuracy():
    """测试分辨率精度"""
    print("\n测试分辨率精度...")
    
    try:
        from app.climate_zones import get_ipcc_aggregated_zone_in_chinese
        
        # 测试相近坐标的气候区一致性
        base_lat, base_lon = 35.7, 139.6  # 东京
        offsets = [0.01, 0.05, 0.1, 0.2, 0.5]  # 不同距离偏移
        
        print(f"以东京 ({base_lat}, {base_lon}) 为中心测试...")
        
        for offset in offsets:
            coords = [
                (base_lat + offset, base_lon, f"北{offset}度"),
                (base_lat - offset, base_lon, f"南{offset}度"),
                (base_lat, base_lon + offset, f"东{offset}度"),
                (base_lat, base_lon - offset, f"西{offset}度"),
            ]
            
            zones = []
            for lat, lon, desc in coords:
                try:
                    zone = get_ipcc_aggregated_zone_in_chinese(lat, lon)
                    zones.append(zone)
                    print(f"  {desc:8} ({lat:6.2f}, {lon:7.2f}) -> {zone}")
                except Exception as e:
                    print(f"  {desc:8} ({lat:6.2f}, {lon:7.2f}) -> 错误: {e}")
            
            # 检查一致性
            unique_zones = set(zones)
            if len(unique_zones) == 1:
                print(f"  ✓ {offset}度范围内气候区一致: {list(unique_zones)[0]}")
            else:
                print(f"  ? {offset}度范围内气候区不一致: {unique_zones}")
        
    except Exception as e:
        print(f"✗ 分辨率测试失败: {e}")

def main():
    """主函数"""
    print("=== 全球气候区判断精度测试 ===\n")
    
    # 测试全球气候区
    success, total = test_global_climate_zones()
    
    # 测试分辨率精度
    test_resolution_accuracy()
    
    print(f"\n=== 测试完成 ===")
    print(f"总体通过率: {success}/{total} ({success/total*100:.1f}%)")
    
    if success/total >= 0.8:
        print("✅ 气候区判断精度良好")
    elif success/total >= 0.6:
        print("⚠️  气候区判断精度一般，需要改进")
    else:
        print("❌ 气候区判断精度较差，需要大幅改进")

if __name__ == "__main__":
    main()