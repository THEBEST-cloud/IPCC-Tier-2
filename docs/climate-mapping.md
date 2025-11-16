# 前端5类气候带到IPCC六类聚合的映射说明

本文档说明当前前端显示的中文5类气候带（A/B/C/D/E）如何在提交与默认值计算时映射为IPCC规定的6种聚合气候带（中文）。

## 前端展示的5类（中文）
- 热带
- 干旱带
- 温暖带
- 亚寒带/温带
- 寒带

这些5类对应柯本气候的主气候带：A（热带）、B（干旱带）、C（温暖带/温带）、D（亚寒带/温带）、E（寒带）。

## IPCC六类聚合（中文，后端使用）
- 北方
- 冷温带
- 暖温带干旱
- 暖温带湿润
- 热带干旱/山地
- 热带湿润/潮湿

## 映射规则概述
映射在 `app/static/app.js` 中完成（函数 `mapFiveToAggregatedCN`）。它结合接口 `/api/climate-region/{lat}/{lng}` 返回的：
- `raw_standard_en`：IPCC标准气候区（英文，细分干/湿/山地）
- `aggregated_cn`：自动识别的聚合中文（供默认值与回退使用）

### 具体规则
- 热带 →
  - 若 `raw_standard_en` 为 `Tropical dry` 或 `Tropical montane`，映射为 `热带干旱/山地`
  - 若为 `Tropical moist` 或 `Tropical wet`，映射为 `热带湿润/潮湿`
  - 无标准信息时，回退使用自动识别的 `aggregated_cn`，仍不确定则默认 `热带湿润/潮湿`

- 干旱带 →
  - 优先依据 `raw_standard_en` 的干湿与纬度带：
    - `Warm temperate dry` → `暖温带干旱`
    - `Cool temperate dry` → `冷温带`
    - `Boreal/Polar` 相关干型 → `北方`
  - 无标准信息时按纬度粗略分配：
    - 纬度 |lat| < 23.5 → `热带干旱/山地`
    - 23.5 ≤ |lat| < 40 → `暖温带干旱`
    - 其余 → `冷温带`
  - 有自动识别则优先 `aggregated_cn`

- 温暖带 →
  - 若 `raw_standard_en` 包含 `Warm temperate dry/moist`，映射为 `暖温带干旱/暖温带湿润`
  - 否则用自动识别 `aggregated_cn`（若为两者之一），再不确定默认 `暖温带湿润`

- 亚寒带/温带 → `冷温带`

- 寒带 → `北方`

## 数据流与提交
- 下拉显示：前端仅显示上述5类中文。
- 自动识别：根据坐标调用 `/api/climate-region`，默认值展示使用返回的 `aggregated_cn`。
- 用户选择：当用户在下拉中选中某一5类时，前端使用上述映射得到中文聚合值，并将其作为 `climate_region_override` 提交给后端（始终为中文聚合标签）。

## 修改位置
- JS 逻辑：`app/static/app.js`
  - `populateClimateSelect`：改为填充中文5类
  - `mapFiveToAggregatedCN`：五类到六类中文聚合映射
  - `collectFormData`：总是提交聚合中文覆盖值

## 说明
该映射遵循 IPCC 推荐的区域合并方案，并利用标准英文标签细分干/湿与山地。因 5→6 的聚合存在跨带的情况（尤其 B 干旱带），在缺少标准标签时采取纬度与自动识别作为回退，以保证工程稳健与一致性。