# IPCC Tier 1 详细计算过程总结

## 修改内容

根据用户要求，代码已修改为清晰展示IPCC Tier 1方法的所有计算步骤和中间变量。

## 计算流程展示

### 1. CO2排放计算 (< 20年)

**步骤1：从排放因子开始**
- `EF_CO2`: 排放因子EF (tCO₂-C ha⁻¹ y⁻¹)
- `F_CO2_annual`: 年均排放量 (tCO₂-C y⁻¹) = 水库面积 × (EF_CO2 / 100)
- `E_CO2_20yr`: 20年CO2总排放量 (tCO₂-C) = F_CO2_annual × min(20, 水库年龄)
- `E_CO2_total`: CO2总排放量 (tCO₂) = E_CO2_20yr × (M_CO2 / M_C)

### 2. CH4排放计算 (贯穿两个阶段)

**步骤2：水库自身排放**
- `trophic_factor`: 营养状态调整系数 αᵢ
- `EF_CH4_le_20`: ≤20年排放因子EF (kgCH₄ ha⁻¹ y⁻¹)
- `EF_CH4_gt_20`: >20年排放因子EF (kgCH₄ ha⁻¹ y⁻¹)
- `F_CH4_res_le_20_annual`: ≤20年年均排放量 (tCH₄ y⁻¹) = αᵢ × (EF_CH4_le_20 × 水库面积)
- `F_CH4_res_gt_20_annual`: >20年年均排放量 (tCH₄ y⁻¹) = αᵢ × (EF_CH4_gt_20 × 水库面积)
- `E_CH4_res_le_20`: <20年总排放量 (tCH₄) = F_CH4_res_le_20_annual × min(20, 水库年龄)
- `E_CH4_res_gt_20`: >20年总排放量 (tCH₄) = F_CH4_res_gt_20_annual × max(0, 水库年龄-20)

**步骤3：下游排放**
- `R_d_i`: flux CH4 downstream, R d,i = 0.09
- `F_CH4_downstream_le_20_annual`: ≤20年下游年均排放量 (tCH₄ y⁻¹) = F_CH4_res_le_20_annual × R_d_i
- `F_CH4_downstream_gt_20_annual`: >20年下游年均排放量 (tCH₄ y⁻¹) = F_CH4_res_gt_20_annual × R_d_i
- `E_CH4_downstream_le_20`: 20年迁移排放量 (tCH₄) = F_CH4_downstream_le_20_annual × min(20, 水库年龄)
- `E_CH4_downstream_gt_20`: 20年后总排放量 (tCH₄) = F_CH4_downstream_gt_20_annual × max(0, 水库年龄-20)

### 3. 汇总与最终结果

**步骤4：CH4总排放量转换**
- `E_CH4_le_20_total`: 20年CH4总排放量 (tCO₂eq) = (E_CH4_res_le_20 + E_CH4_downstream_le_20) × GWP_100yr_CH4 / 1000
- `E_CH4_gt_20_total`: >20年CH4总排放量 (tCO₂eq) = (E_CH4_res_gt_20 + E_CH4_downstream_gt_20) × GWP_100yr_CH4 / 1000
- `E_CH4_total`: CH4总排放量 (tCO₂eq) = E_CH4_le_20_total + E_CH4_gt_20_total

**步骤5：分阶段汇总**
- `E_le_20_total`: <20年总排放量 (tCO₂eq) = E_CO2_total + E_CH4_le_20_total
- `E_gt_20_total`: >20年总排放量 (tCO₂eq) = E_CH4_gt_20_total
- `E_total`: 总排放量 (tCO₂eq) = E_CO2_total + E_CH4_total

## 展示的变量

### 输入参数
- `surface_area_ha`: 水库面积 (ha)
- `reservoir_age`: 水库年龄 (年)
- `trophic_status`: 营养状态
- `climate_region`: 气候区
- `trophic_factor`: 营养状态调整系数 αᵢ

### CO2排放变量
- `EF_CO2`: 排放因子EF (tCO₂-C ha⁻¹ y⁻¹)
- `F_CO2_annual`: 年均排放量 (tCO₂-C y⁻¹)
- `E_CO2_20yr`: 20年CO2总排放量 (tCO₂-C)
- `E_CO2_total`: CO2总排放量 (tCO₂)

### CH4排放变量
- `EF_CH4_le_20`: ≤20年排放因子EF (kgCH₄ ha⁻¹ y⁻¹)
- `EF_CH4_gt_20`: >20年排放因子EF (kgCH₄ ha⁻¹ y⁻¹)
- `R_d_i`: flux CH4 downstream, R d,i
- `F_CH4_res_le_20_annual`: ≤20年年均排放量 (tCH₄ y⁻¹)
- `F_CH4_res_gt_20_annual`: >20年年均排放量 (tCH₄ y⁻¹)
- `E_CH4_res_le_20`: <20年总排放量 (tCH₄)
- `E_CH4_res_gt_20`: >20年总排放量 (tCH₄)
- `F_CH4_downstream_le_20_annual`: ≤20年下游年均排放量 (tCH₄ y⁻¹)
- `F_CH4_downstream_gt_20_annual`: >20年下游年均排放量 (tCH₄ y⁻¹)
- `E_CH4_downstream_le_20`: 20年迁移排放量 (tCH₄)
- `E_CH4_downstream_gt_20`: 20年后总排放量 (tCH₄)

### 汇总变量
- `E_CH4_le_20_total`: 20年CH4总排放量 (tCO₂eq)
- `E_CH4_gt_20_total`: >20年CH4总排放量 (tCO₂eq)
- `E_CH4_total`: CH4总排放量 (tCO₂eq)
- `E_le_20_total`: <20年总排放量 (tCO₂eq)
- `E_gt_20_total`: >20年总排放量 (tCO₂eq)
- `E_total`: 总排放量 (tCO₂eq)

### 年均排放量
- `annual_CO2`: 年均CO2排放量 (kgCO2eq/yr)
- `annual_CH4_le_20`: ≤20年CH4年均排放量 (kgCO2eq/yr)
- `annual_CH4_gt_20`: >20年CH4年均排放量 (kgCO2eq/yr)

### 分源CH4排放
- `annual_CH4_res_surface_le_20`: ≤20年水库表面CH4排放 (kgCO2eq/yr)
- `annual_CH4_res_surface_gt_20`: >20年水库表面CH4排放 (kgCO2eq/yr)
- `annual_CH4_downstream_le_20`: ≤20年下游CH4排放 (kgCO2eq/yr)
- `annual_CH4_downstream_gt_20`: >20年下游CH4排放 (kgCO2eq/yr)

## 计算示例

### 5年水库示例
- **CO2排放**: 只在前5年，总排放量 = 98,144.44 tCO₂
- **CH4排放**: 前5年使用高排放因子，总排放量 = 56,701.80 tCO₂eq
- **总排放量**: 154,846.24 tCO₂eq

### 30年水库示例
- **CO2排放**: 只在前20年，总排放量 = 392,577.78 tCO₂
- **CH4排放**: 前20年高排放 + 后10年低排放，总排放量 = 298,229.23 tCO₂eq
- **总排放量**: 690,807.01 tCO₂eq

## 关键特点

1. **CO2排放限制**: 只在前20年发生
2. **CH4分阶段**: 前20年高排放，20年后低排放
3. **营养状态调整**: 通过αᵢ系数调整
4. **下游排放**: 通过R_d_i系数计算
5. **完整追踪**: 所有中间变量都可查看和验证

## 文件更新

- `app/ipcc_tier1.py` - 重新组织了计算逻辑，添加了所有中间变量
- 确保计算过程完全透明和可验证

现在代码完全符合IPCC Tier 1方法，并清晰展示了所有计算步骤和中间变量！