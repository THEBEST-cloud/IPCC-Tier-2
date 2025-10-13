# 前端键名修复总结

## 问题描述

前端JavaScript出现错误：`TypeError: Cannot read properties of undefined (reading 'toFixed')`，这是因为前端仍在使用旧的键名，而后端已经更新为新的键名结构。

## 错误信息

```
app.js:246 Error: TypeError: Cannot read properties of undefined (reading 'toFixed')
    at formatNumber (app.js:853:20)
    at generateIPCCResultsHTML (app.js:595:59)
```

## 问题根源

在重新组织IPCC Tier 1计算代码时，后端返回的键名发生了变化，但前端JavaScript仍在使用旧的键名，导致`undefined`值被传递给`formatNumber`函数。

## 修复内容

### 1. 主要排放量键名更新

**修复前：**
```javascript
ipccResults.E_CO2
ipccResults.E_CH4
```

**修复后：**
```javascript
ipccResults.E_CO2_total
ipccResults.E_CH4_total
```

### 2. 分阶段排放量键名更新

**修复前：**
```javascript
ipccResults.E_CH4_age_le_20
ipccResults.E_CH4_age_gt_20
```

**修复后：**
```javascript
ipccResults.E_CH4_le_20_total
ipccResults.E_CH4_gt_20_total
```

### 3. 年均排放量键名更新

**修复前：**
```javascript
ipccResults.annual_CH4_age_le_20
ipccResults.annual_CH4_age_gt_20
```

**修复后：**
```javascript
ipccResults.annual_CH4_le_20
ipccResults.annual_CH4_gt_20
```

### 4. 中间计算值键名更新

**修复前：**
```javascript
ipccResults.F_CO2_tot
ipccResults.F_CH4_res_age_le_20
ipccResults.F_CH4_downstream_age_le_20
ipccResults.F_CH4_res_age_gt_20
ipccResults.F_CH4_downstream_age_gt_20
```

**修复后：**
```javascript
ipccResults.F_CO2_annual
ipccResults.F_CH4_res_le_20_annual
ipccResults.F_CH4_downstream_le_20_annual
ipccResults.F_CH4_res_gt_20_annual
ipccResults.F_CH4_downstream_gt_20_annual
```

## 修复结果

### 测试验证
- ✅ 所有前端需要的键都存在
- ✅ 关键值不为undefined
- ✅ 计算函数正常工作

### 数据示例
```
E_total: 154,846.24 tCO2eq
E_CO2_total: 98,144.44 tCO2eq
E_CH4_total: 56,701.80 tCO2eq
```

## 更新的键名映射

| 前端显示 | 旧键名 | 新键名 | 说明 |
|----------|--------|--------|------|
| CO₂排放总量 | E_CO2 | E_CO2_total | CO2总排放量 |
| CH₄排放总量 | E_CH4 | E_CH4_total | CH4总排放量 |
| ≤20年CH₄排放 | E_CH4_age_le_20 | E_CH4_le_20_total | ≤20年CH4总排放量 |
| >20年CH₄排放 | E_CH4_age_gt_20 | E_CH4_gt_20_total | >20年CH4总排放量 |
| ≤20年CH₄年均 | annual_CH4_age_le_20 | annual_CH4_le_20 | ≤20年CH4年均排放量 |
| >20年CH₄年均 | annual_CH4_age_gt_20 | annual_CH4_gt_20 | >20年CH4年均排放量 |
| 年均CO₂排放 | F_CO2_tot | F_CO2_annual | 年均CO2排放量 |
| ≤20年水库CH₄ | F_CH4_res_age_le_20 | F_CH4_res_le_20_annual | ≤20年水库CH4年均排放量 |
| ≤20年下游CH₄ | F_CH4_downstream_age_le_20 | F_CH4_downstream_le_20_annual | ≤20年下游CH4年均排放量 |
| >20年水库CH₄ | F_CH4_res_age_gt_20 | F_CH4_res_gt_20_annual | >20年水库CH4年均排放量 |
| >20年下游CH₄ | F_CH4_downstream_age_gt_20 | F_CH4_downstream_gt_20_annual | >20年下游CH4年均排放量 |

## 文件更新

- `app/static/app.js` - 更新了所有键名引用
- 确保前后端键名完全一致

## 总结

前端键名问题已成功修复，现在：
- ✅ 所有键名与后端一致
- ✅ 不再出现undefined错误
- ✅ 前端可以正常显示计算结果
- ✅ 详细计算过程完整展示

修复确保了前后端数据的一致性和前端功能的正常运行。