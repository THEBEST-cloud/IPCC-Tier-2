// 全局变量
let currentAnalysis = null;
let map = null;
let marker = null;

// 坐标标准化函数
function normalizeCoordinates(lat, lng) {
    // 标准化纬度到-90到90范围
    let normalizedLat = lat;
    if (normalizedLat > 90) {
        normalizedLat = 90 - (normalizedLat - 90);
    } else if (normalizedLat < -90) {
        normalizedLat = -90 + (-90 - normalizedLat);
    }
    
    // 标准化经度到-180到180范围
    let normalizedLng = lng;
    while (normalizedLng > 180) {
        normalizedLng -= 360;
    }
    while (normalizedLng < -180) {
        normalizedLng += 360;
    }
    
    return { lat: normalizedLat, lng: normalizedLng };
}

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    setupEventListeners();
    setupToggleSwitches();
    setupAnalysisOptions();
    setupCoordinateInputs();
    
    // 延迟初始化地图，确保DOM完全加载
    setTimeout(initializeMap, 500);
}

// 设置事件监听器
function setupEventListeners() {
    // 计算按钮
    document.getElementById('calculateBtn').addEventListener('click', handleCalculate);
    
    // 保存草稿按钮
    document.getElementById('saveDraftBtn').addEventListener('click', handleSaveDraft);
    
    // 表单输入变化
    document.getElementById('latitude').addEventListener('input', function() {
        updateClimateRegion();
        updateMapFromCoordinates();
    });
    document.getElementById('longitude').addEventListener('input', function() {
        updateClimateRegion();
        updateMapFromCoordinates();
    });
    
    // 水质参数变化
    document.getElementById('totalPhosphorus').addEventListener('input', updateTrophicStatus);
    document.getElementById('totalNitrogen').addEventListener('input', updateTrophicStatus);
    document.getElementById('chlorophyllA').addEventListener('input', updateTrophicStatus);
    
    // 营养状态选择变化
    document.getElementById('trophicStatusSelect').addEventListener('change', updateTrophicStatus);

    // 气候区域下拉选择变化（用户可覆盖自动识别）
    const climateSelect = document.getElementById('climateRegionSelect');
    if (climateSelect) {
        climateSelect.addEventListener('change', function() {
            climateSelect.dataset.autoSelected = 'false';
            const selected = climateSelect.value;
            if (selected) {
                // 用户选择柯本代码时，直接映射到IPCC六类中文
                const mappedCN = KOPPEN_CODE_TO_AGG_CN && KOPPEN_CODE_TO_AGG_CN[selected] ? KOPPEN_CODE_TO_AGG_CN[selected] : null;
                if (mappedCN) {
                    selectedAggregatedOverride = mappedCN;
                } else {
                    const lat = parseFloat(document.getElementById('latitude').value);
                    const rawStd = latestClimateInfo && latestClimateInfo.raw_standard_en ? latestClimateInfo.raw_standard_en : null;
                    const autoAggCN = latestClimateInfo && latestClimateInfo.aggregated_cn ? latestClimateInfo.aggregated_cn : null;
                    selectedAggregatedOverride = mapFiveToAggregatedCN(selected, rawStd, lat, autoAggCN) || null;
                }
                updateDefaultValues(selectedAggregatedOverride || '暖温带湿润');
            } else {
                // 恢复为基于自动识别的默认值
                selectedAggregatedOverride = null;
                updateClimateRegion();
            }
        });
    }
}

// 设置切换开关
function setupToggleSwitches() {
    const toggles = document.querySelectorAll('.toggle-switch input');
    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const input = this.closest('.form-group').querySelector('.form-input');
            if (this.checked) {
                input.readOnly = true;
                input.style.backgroundColor = '#f8fafc';
                input.style.color = '#6b7280';
                setDefaultValue(input.id);
            } else {
                input.readOnly = false;
                input.style.backgroundColor = 'white';
                input.style.color = '#334155';
            }
        });
    });
}

// 设置分析选项
function setupAnalysisOptions() {
    const uncertaintyCheckbox = document.getElementById('enableUncertainty');
    const sensitivityCheckbox = document.getElementById('enableSensitivity');
    const monteCarloSelect = document.getElementById('monteCarloRuns');
    const sensitivityOptions = document.querySelector('.checkbox-group');

    if (uncertaintyCheckbox && monteCarloSelect) {
        uncertaintyCheckbox.addEventListener('change', function() {
            monteCarloSelect.style.display = this.checked ? 'block' : 'none';
        });
        
        // 初始状态
        monteCarloSelect.style.display = 'block';
    }

    if (sensitivityCheckbox && sensitivityOptions) {
        sensitivityCheckbox.addEventListener('change', function() {
            sensitivityOptions.style.display = this.checked ? 'block' : 'none';
        });
        
        // 初始状态
        sensitivityOptions.style.display = 'block';
    }
}

// 设置坐标输入
function setupCoordinateInputs() {
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');
    
    // 示例坐标（北京）
    latitudeInput.value = '39.9042';
    longitudeInput.value = '116.4074';
    updateClimateRegion();
}

// 保存最近一次自动识别结果与用户覆盖
let latestClimateInfo = null;
let selectedAggregatedOverride = null;

// 标准英文到中文聚合气候区映射（用于默认值显示）
const STANDARD_TO_AGGREGATED_CN = {
    'Boreal dry': '北方',
    'Boreal moist': '北方',
    'Polar dry': '北方',
    'Polar moist': '北方',
    'Cool temperate dry': '冷温带',
    'Cool temperate moist': '冷温带',
    'Warm temperate dry': '暖温带干旱',
    'Warm temperate moist': '暖温带湿润',
    'Tropical dry': '热带干旱/山地',
    'Tropical montane': '热带干旱/山地',
    'Tropical moist': '热带湿润/潮湿',
    'Tropical wet': '热带湿润/潮湿'
};

// 将中文5类主气候带映射为IPCC六类中文聚合
function mapFiveToAggregatedCN(fiveCN, rawStandard, latitude, autoAggregatedCN) {
    if (!fiveCN) return autoAggregatedCN || null;
    const byStd = rawStandard ? STANDARD_TO_AGGREGATED_CN[rawStandard] : null;
    switch (fiveCN) {
        case '寒带':
            return '北方';
        case '亚寒带/温带':
            return '冷温带';
        case '温暖带':
            if (rawStandard && rawStandard.includes('Warm temperate')) {
                return rawStandard.includes('dry') ? '暖温带干旱' : '暖温带湿润';
            }
            if (autoAggregatedCN && (autoAggregatedCN === '暖温带干旱' || autoAggregatedCN === '暖温带湿润')) {
                return autoAggregatedCN;
            }
            return '暖温带湿润';
        case '热带':
            if (rawStandard && rawStandard.startsWith('Tropical')) {
                return (rawStandard.includes('dry') || rawStandard.includes('montane')) ? '热带干旱/山地' : '热带湿润/潮湿';
            }
            if (autoAggregatedCN && (autoAggregatedCN === '热带干旱/山地' || autoAggregatedCN === '热带湿润/潮湿')) {
                return autoAggregatedCN;
            }
            return '热带湿润/潮湿';
        case '干旱带':
            if (byStd) return byStd;
            if (rawStandard) {
                if (rawStandard.includes('Warm temperate dry')) return '暖温带干旱';
                if (rawStandard.includes('Cool temperate dry')) return '冷温带';
                if (rawStandard.includes('Boreal') || rawStandard.includes('Polar')) return '北方';
            }
            if (typeof latitude === 'number') {
                const absLat = Math.abs(latitude);
                if (absLat < 23.5) return '热带干旱/山地';
                if (absLat < 40) return '暖温带干旱';
                return '冷温带';
            }
            return autoAggregatedCN || '暖温带干旱';
        default:
            return autoAggregatedCN || null;
    }
}

// 柯本代码到中文名称（下拉显示）
const KOPPEN_CODE_TO_CN = {
    Af: '热带雨林',
    Am: '热带季风',
    Aw: '热带草原',
    BWh: '热沙漠',
    BWk: '冷沙漠',
    BSh: '热草原（半干旱）',
    BSk: '冷草原（半干旱）',
    Csa: '地中海炎热夏季',
    Csb: '地中海暖夏',
    Csc: '地中海冷夏',
    Cwa: '温带冬季干燥·炎热夏季',
    Cwb: '温带冬季干燥·温暖夏季',
    Cwc: '温带冬季干燥·寒冷夏季',
    Cfa: '温带无干季·炎热夏季',
    Cfb: '温带无干季·温和夏季',
    Cfc: '温带无干季·寒冷夏季',
    Dsa: '冷带夏季干燥·炎热夏季',
    Dsb: '冷带夏季干燥·温暖夏季',
    Dsc: '冷带夏季干燥·寒冷夏季',
    Dsd: '冷带夏季干燥·严寒冬季',
    Dwa: '冷带冬季干燥·炎热夏季',
    Dwb: '冷带冬季干燥·温暖夏季',
    Dwc: '冷带冬季干燥·寒冷夏季',
    Dwd: '冷带冬季干燥·严寒冬季',
    Dfa: '冷带无干季·炎热夏季',
    Dfb: '冷带无干季·温暖夏季',
    Dfc: '冷带无干季·寒冷夏季',
    Dfd: '冷带无干季·严寒冬季',
    ET: '苔原',
    EF: '冰原'
};

// 柯本代码到IPCC六类中文聚合映射（提交）
const KOPPEN_CODE_TO_AGG_CN = {
    Af: '热带湿润/潮湿',
    Am: '热带湿润/潮湿',
    Aw: '热带干旱/山地',
    BWh: '暖温带干旱',
    BSh: '暖温带干旱',
    BWk: '冷温带',
    BSk: '冷温带',
    Csa: '暖温带干旱',
    Csb: '暖温带干旱',
    Csc: '暖温带干旱',
    Cwa: '暖温带湿润',
    Cfa: '暖温带湿润',
    Cwb: '冷温带',
    Cwc: '冷温带',
    Cfb: '冷温带',
    Cfc: '冷温带',
    Dsa: '冷温带',
    Dsb: '冷温带',
    Dsc: '冷温带',
    Dsd: '冷温带',
    Dwa: '冷温带',
    Dwb: '冷温带',
    Dwc: '冷温带',
    Dwd: '冷温带',
    Dfa: '冷温带',
    Dfb: '冷温带',
    Dfc: '北方',
    Dfd: '北方',
    ET: '北方',
    EF: '北方'
};

// 填充中文5大主气候带到下拉框（只执行一次）
function populateClimateSelect() {
    const select = document.getElementById('climateRegionSelect');
    if (!select) return;

    // 如果已经填充过（除了第一个“自动识别”外还有选项），则不重复填充
    if (select.options.length > 1) return;

    // 柯本30类，值为代码；显示中文
    const koppenEntries = Object.entries(KOPPEN_CODE_TO_CN);

    // 确保第一个选项是“自动识别（推荐）”
    if (select.options.length === 0) {
        const auto = document.createElement('option');
        auto.value = '';
        auto.textContent = '自动识别（推荐）';
        select.appendChild(auto);
    } else {
        // 将第一个选项文本修正为“自动识别（推荐）”
        select.options[0].value = '';
        select.options[0].textContent = '自动识别（推荐）';
    }

    koppenEntries.forEach(([code, name]) => {
        const opt = document.createElement('option');
        opt.value = code;
        opt.textContent = name;
        select.appendChild(opt);
    });
}

// 更新气候区域
async function updateClimateRegion() {
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);
    
    if (isNaN(latitude) || isNaN(longitude)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/climate-region/${latitude}/${longitude}`);
        const data = await response.json();
        latestClimateInfo = data;
        const aggregatedCN = data.aggregated_cn || '';
        const select = document.getElementById('climateRegionSelect');
        if (select) {
            // 确保下拉已填充为柯本30类
            populateClimateSelect();
            // 自动识别后展示识别的柯本代码，不作为覆盖
            if (data.koppen_code_str && KOPPEN_CODE_TO_CN[data.koppen_code_str]) {
                select.value = data.koppen_code_str;
            } else {
                select.value = '';
            }
            select.dataset.autoSelected = 'true';
        }
        // 默认值仍按聚合中文区分类
        updateDefaultValues(aggregatedCN);
    } catch (error) {
        console.error('Error fetching climate region:', error);
    }
}

// 更新默认值
function updateDefaultValues(climateRegionCN) {
    // 若页面不存在默认值展示元素，则直接返回，避免空引用
    const areaEl = document.getElementById('defaultArea');
    const depthEl = document.getElementById('defaultDepth');
    if (!areaEl || !depthEl) return;

    // 根据中文聚合气候区设定默认值
    const defaultsCN = {
        '热带湿润/潮湿': { area: 15.0, depth: 25.0 },
        '热带干旱/山地': { area: 14.0, depth: 22.0 },
        '暖温带湿润': { area: 10.0, depth: 20.0 },
        '暖温带干旱': { area: 9.0, depth: 18.0 },
        '冷温带': { area: 8.0, depth: 15.0 },
        '北方': { area: 7.0, depth: 12.0 }
    };

    const regionDefaults = defaultsCN[climateRegionCN] || defaultsCN['暖温带湿润'];
    areaEl.textContent = regionDefaults.area;
    depthEl.textContent = regionDefaults.depth;
}

// 设置默认值
function setDefaultValue(inputId) {
    const defaults = {
        'surfaceArea': 10.0,
        'reservoirAge': 20.0
    };
    
    const input = document.getElementById(inputId);
    if (input && defaults[inputId]) {
        input.value = defaults[inputId];
    }
}

// 更新营养状态
function updateTrophicStatus() {
    const trophicSelect = document.getElementById('trophicStatusSelect');
    const selectedStatus = trophicSelect.value;
    
    // 如果用户选择了具体的营养状态，直接使用
    if (selectedStatus) {
        const statusText = trophicSelect.options[trophicSelect.selectedIndex].text;
        const statusDiv = document.getElementById('trophicStatus');
        const statusTextSpan = document.getElementById('trophicStatusText');
        
        statusDiv.className = `trophic-status trophic-${selectedStatus.toLowerCase()}`;
        statusTextSpan.textContent = statusText;
        statusDiv.style.display = 'inline-block';
        return;
    }
    
    // 否则通过水质参数自动评估
    const tp = parseFloat(document.getElementById('totalPhosphorus').value);
    const tn = parseFloat(document.getElementById('totalNitrogen').value);
    const chla = parseFloat(document.getElementById('chlorophyllA').value);
    
    if (isNaN(tp) && isNaN(tn) && isNaN(chla)) {
        document.getElementById('trophicStatus').style.display = 'none';
        return;
    }
    
    // 简单的营养状态评估
    let status = 'Oligotrophic';
    let statusText = '贫营养型 (Oligotrophic)';
    
    if (tp > 30 || tn > 1.5 || chla > 10) {
        status = 'Eutrophic';
        statusText = '富营养型 (Eutrophic)';
    } else if (tp > 15 || tn > 1.0 || chla > 5) {
        status = 'Mesotrophic';
        statusText = '中营养型 (Mesotrophic)';
    }
    
    const statusDiv = document.getElementById('trophicStatus');
    const statusTextSpan = document.getElementById('trophicStatusText');
    
    statusDiv.className = `trophic-status trophic-${status.toLowerCase()}`;
    statusTextSpan.textContent = statusText;
    statusDiv.style.display = 'inline-block';
}

// 处理计算
async function handleCalculate() {
    if (!validateForm()) {
        return;
    }
    
    showLoading();
    
    try {
        const formData = collectFormData();
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        currentAnalysis = result;
        displayResults(result);
        
    } catch (error) {
        console.error('Error:', error);
        showError('计算失败，请检查输入数据并重试');
    } finally {
        hideLoading();
    }
}

// 处理保存草稿
function handleSaveDraft() {
    if (!validateForm()) {
        return;
    }
    
    const formData = collectFormData();
    const draftData = {
        ...formData,
        saved_at: new Date().toISOString(),
        status: 'draft'
    };
    
    // 保存到本地存储
    const drafts = JSON.parse(localStorage.getItem('drafts') || '[]');
    drafts.push(draftData);
    localStorage.setItem('drafts', JSON.stringify(drafts));
    
    showSuccess('草稿已保存');
}

// 验证表单
function validateForm() {
    const requiredFields = ['projectName', 'latitude', 'longitude', 'surfaceArea'];
    let isValid = true;
    
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (!field.value.trim()) {
            field.style.borderColor = '#ef4444';
            isValid = false;
        } else {
            field.style.borderColor = '#e2e8f0';
        }
    });
    
    if (!isValid) {
        showError('请填写所有必填字段');
    }
    
    return isValid;
}

// 收集表单数据
function collectFormData() {
    return {
        project_name: document.getElementById('projectName').value,
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value),
        surface_area: parseFloat(document.getElementById('surfaceArea').value),
        reservoir_age: parseFloat(document.getElementById('reservoirAge').value) || null,
        water_quality: {
            total_phosphorus: parseFloat(document.getElementById('totalPhosphorus').value) || null,
            total_nitrogen: parseFloat(document.getElementById('totalNitrogen').value) || null,
            chlorophyll_a: parseFloat(document.getElementById('chlorophyllA').value) || null,
            secchi_depth: null
        },
        trophic_status: document.getElementById('trophicStatusSelect').value || null,
        // 用户覆盖的气候区域（始终传中文聚合气候区）
        climate_region_override: (function() {
            const sel = document.getElementById('climateRegionSelect');
            if (!sel || !sel.value) return null;
            // 若选择为柯本代码，则用代码→IPCC六类映射；否则回退到旧的五类中文逻辑
            const code = sel.value;
            if (sel.dataset && sel.dataset.autoSelected === 'true') {
                // 自动选择的情况下，不视为覆盖
                return null;
            }
            if (KOPPEN_CODE_TO_AGG_CN && KOPPEN_CODE_TO_AGG_CN[code]) {
                return KOPPEN_CODE_TO_AGG_CN[code];
            }
            const lat = parseFloat(document.getElementById('latitude').value);
            const rawStd = latestClimateInfo && latestClimateInfo.raw_standard_en ? latestClimateInfo.raw_standard_en : null;
            const autoAggCN = latestClimateInfo && latestClimateInfo.aggregated_cn ? latestClimateInfo.aggregated_cn : null;
            return mapFiveToAggregatedCN(code, rawStd, lat, autoAggCN);
        })(),
        run_uncertainty: document.getElementById('enableUncertainty').checked,
        run_sensitivity: document.getElementById('enableSensitivity').checked,
        uncertainty_iterations: parseInt(document.getElementById('monteCarloRuns').value)
    };
}

// 显示结果
function displayResults(result) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = generateResultsHTML(result);
    container.style.display = 'block';
    
    // 绘制图表
    setTimeout(() => {
        if (result.uncertainty) {
            drawUncertaintyChart(result.uncertainty);
        }
    }, 100);
    
    // 滚动到结果区域
    container.scrollIntoView({ behavior: 'smooth' });
}

// 生成结果HTML
function generateResultsHTML(result) {
    const emissions = result.emissions;
    const uncertainty = result.uncertainty;
    const sensitivity = result.sensitivity;
    
    // 调试信息
    console.log('Result data:', result);
    console.log('Uncertainty data:', uncertainty);
    console.log('Sensitivity data:', sensitivity);
    
    return `
        <div class="results-header">
            <h2 class="results-title">计算结果：${document.getElementById('projectName').value}</h2>
            <p class="results-subtitle">基于IPCC Tier 1方法的水库温室气体排放分析</p>
        </div>
        
        <div class="emissions-summary">
            <div class="emission-card ch4">
                <div class="emission-icon">
                    <i class="fas fa-fire"></i>
                </div>
                <div class="emission-label">甲烷 (CH₄)</div>
                <div class="emission-value">${formatNumber(emissions.total_ch4_emissions)}</div>
                <div class="emission-unit">t CO₂-当量</div>
            </div>
            <div class="emission-card co2">
                <div class="emission-icon">
                    <i class="fas fa-smog"></i>
                </div>
                <div class="emission-label">二氧化碳 (CO₂)</div>
                <div class="emission-value">${formatNumber(emissions.total_co2_emissions)}</div>
                <div class="emission-unit">t CO₂-当量</div>
            </div>
        </div>
        
        <div class="total-emissions">
            <div class="total-value">${formatNumber(emissions.co2_equivalent)}</div>
            <div class="total-label">总温室气体排放量 (t CO₂-当量)</div>
        </div>
        
        ${emissions.ipcc_tier1_results ? generateIPCCResultsHTML(emissions.ipcc_tier1_results) : ''}
        ${uncertainty ? generateUncertaintyHTML(uncertainty) : ''}
        ${sensitivity ? generateSensitivityHTML(sensitivity) : ''}
        
        <div class="action-buttons">
            <button class="btn btn-primary" onclick="downloadReport()">
                <i class="fas fa-download" style="margin-right: 8px;"></i>
                下载报告 (PDF)
            </button>
            <button class="btn btn-secondary" onclick="saveResults()">
                <i class="fas fa-save" style="margin-right: 8px;"></i>
                保存结果
            </button>
        </div>
    `;
}

// 生成不确定性分析HTML
function generateUncertaintyHTML(uncertainty) {
    if (!uncertainty || !uncertainty.CO2_equivalent) return '';
    
    const stats = uncertainty.CO2_equivalent;
    
    return `
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">
                    <i class="fas fa-chart-line"></i>
                    不确定度分析结果
                </h2>
                <p class="card-subtitle">基于蒙特卡洛模拟的概率分布分析</p>
            </div>
            <div class="card-body">
                <!-- 概率分布图 -->
                <div class="chart-container">
                    <h3 class="chart-title">总排放量概率分布图（基于真实模拟数据）</h3>
                    <div class="chart-description">
                        <p>下图显示了基于${uncertainty.CO2_equivalent.raw_data ? uncertainty.CO2_equivalent.raw_data.length : 1000}次蒙特卡洛模拟的真实数据分布，红色虚线为均值，绿色虚线为95%置信区间边界</p>
                    </div>
                    <div id="uncertaintyChart" class="uncertainty-chart"></div>
                </div>
                
                <!-- 置信区间可视化 -->
                <div class="chart-container">
                    <h3 class="chart-title">95%置信区间可视化</h3>
                    <div class="confidence-interval">
                        <div class="ci-bar">
                            <div class="ci-label">95% 置信区间</div>
                            <div class="ci-range">
                                <div class="ci-line">
                                    <div class="ci-point ci-lower">${formatNumber(stats.ci_lower)}</div>
                                    <div class="ci-line-segment"></div>
                                    <div class="ci-point ci-mean">${formatNumber(stats.mean)}</div>
                                    <div class="ci-line-segment"></div>
                                    <div class="ci-point ci-upper">${formatNumber(stats.ci_upper)}</div>
                                </div>
                            </div>
                        </div>
                        <div class="ci-stats">
                            <div class="ci-stat">
                                <span class="ci-stat-label">区间范围</span>
                                <span class="ci-stat-value">${formatNumber(stats.ci_upper - stats.ci_lower)} kg CO₂-当量/年</span>
                            </div>
                            <div class="ci-stat">
                                <span class="ci-stat-label">相对不确定性</span>
                                <span class="ci-stat-value">${(((stats.ci_upper - stats.ci_lower) / stats.mean) * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 统计摘要表格 -->
                <div class="chart-container">
                    <h3 class="chart-title">统计摘要</h3>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-calculator"></i>
                            </div>
                            <div class="stat-content">
                                <div class="stat-label">均值</div>
                                <div class="stat-value">${formatNumber(stats.mean)}</div>
                                <div class="stat-unit">kg CO₂-当量/年</div>
                            </div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-chart-bar"></i>
                            </div>
                            <div class="stat-content">
                                <div class="stat-label">中位数</div>
                                <div class="stat-value">${formatNumber(stats.percentile_50)}</div>
                                <div class="stat-unit">kg CO₂-当量/年</div>
                            </div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-ruler"></i>
                            </div>
                            <div class="stat-content">
                                <div class="stat-label">标准差</div>
                                <div class="stat-value">${formatNumber(stats.std)}</div>
                                <div class="stat-unit">kg CO₂-当量/年</div>
                            </div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-percentage"></i>
                            </div>
                            <div class="stat-content">
                                <div class="stat-label">变异系数</div>
                                <div class="stat-value">${((stats.std / stats.mean) * 100).toFixed(1)}%</div>
                                <div class="stat-unit">相对变异性</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 分位数表 -->
                <div class="chart-container">
                    <h3 class="chart-title">分位数分析</h3>
                    <table class="stats-table">
                        <thead>
                            <tr>
                                <th>分位数</th>
                                <th>数值</th>
                                <th>累积概率</th>
                                <th>解释</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>P5</td>
                                <td>${formatNumber(stats.percentile_5)}</td>
                                <td>5%</td>
                                <td>排放量有5%的概率不超过此值</td>
                            </tr>
                            <tr>
                                <td>P25</td>
                                <td>${formatNumber(stats.percentile_25)}</td>
                                <td>25%</td>
                                <td>第一四分位数，排放量有25%的概率不超过此值</td>
                            </tr>
                            <tr>
                                <td>P50</td>
                                <td>${formatNumber(stats.percentile_50)}</td>
                                <td>50%</td>
                                <td>中位数，排放量有50%的概率不超过此值</td>
                            </tr>
                            <tr>
                                <td>P75</td>
                                <td>${formatNumber(stats.percentile_75)}</td>
                                <td>75%</td>
                                <td>第三四分位数，排放量有75%的概率不超过此值</td>
                            </tr>
                            <tr>
                                <td>P95</td>
                                <td>${formatNumber(stats.percentile_95)}</td>
                                <td>95%</td>
                                <td>排放量有95%的概率不超过此值</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// 生成IPCC Tier 1详细结果HTML
function generateIPCCResultsHTML(ipccResults) {
    if (!ipccResults) return '';
    
    return `
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">
                    <i class="fas fa-calculator"></i>
                    IPCC Tier 1 详细计算结果
                </h2>
                <p class="card-subtitle">严格遵循IPCC指南的Tier 1方法计算结果</p>
            </div>
            <div class="card-body">
                <!-- 基本信息 -->
                <div class="chart-container">
                    <h3 class="chart-title">计算参数</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">气候区</span>
                            <span class="info-value">${getClimateRegionLabel(ipccResults.climate_region)}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">营养状态</span>
                            <span class="info-value">${getTrophicStatusLabel(ipccResults.trophic_status)}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">水库年龄</span>
                            <span class="info-value">${ipccResults.reservoir_age} 年</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">水库面积</span>
                            <span class="info-value">${formatNumber(ipccResults.surface_area_ha)} 公顷</span>
                        </div>
                    </div>
                </div>
                
                <!-- 生命周期排放总量 -->
                <div class="chart-container">
                    <h3 class="chart-title">水库生命周期碳排放总量</h3>
                    <div class="emissions-grid">
                        <div class="emission-item total">
                            <div class="emission-label">总排放量 (E)</div>
                            <div class="emission-value">${formatNumber(ipccResults.E_total)}</div>
                            <div class="emission-unit">tCO₂-当量</div>
                        </div>
                        <div class="emission-item co2">
                            <div class="emission-label">CO₂排放总量 (E_CO₂)</div>
                            <div class="emission-value">${formatNumber(ipccResults.E_CO2_total)}</div>
                            <div class="emission-unit">tCO₂-当量</div>
                        </div>
                        <div class="emission-item ch4">
                            <div class="emission-label">CH₄排放总量 (E_CH₄)</div>
                            <div class="emission-value">${formatNumber(ipccResults.E_CH4_total)}</div>
                            <div class="emission-unit">tCO₂-当量</div>
                        </div>
                    </div>
                </div>
                
                <!-- 年均排放量 -->
                <div class="chart-container">
                    <h3 class="chart-title">年均排放量</h3>
                    <div class="annual-emissions">
                        <div class="annual-item">
                            <div class="annual-label">≤20年CO₂年均CO₂排放量</div>
                            <div class="annual-value">${formatNumber(ipccResults.annual_CO2)}</div>
                            <div class="annual-unit">kg CO₂-当量/年</div>
                        </div>
                        <div class="annual-item">
                            <div class="annual-label">≤20年CH₄年均排放量</div>
                            <div class="annual-value">${formatNumber(ipccResults.annual_CH4_le_20)}</div>
                            <div class="annual-unit">kg CH₄/年</div>
                        </div>
                        <div class="annual-item">
                            <div class="annual-label">>20年CH₄年均排放量</div>
                            <div class="annual-value">${formatNumber(ipccResults.annual_CH4_gt_20)}</div>
                            <div class="annual-unit">kg CH₄/年</div>
                        </div>
                    </div>
                </div>
                
                <!-- 分源CH₄排放 -->
                <div class="chart-container">
                    <h3 class="chart-title">甲烷分源排放分析</h3>
                    <div class="ch4-sources">
                        <div class="source-group">
                            <h4>库龄≤20年阶段</h4>
                            <div class="source-items">
                                <div class="source-item">
                                    <div class="source-label">水库表面CH₄排放</div>
                                    <div class="source-value">${formatNumber(ipccResults.annual_CH4_res_surface_le_20)}</div>
                                    <div class="source-unit">kg CH₄/年</div>
                                </div>
                                <div class="source-item">
                                    <div class="source-label">大坝下游CH₄排放</div>
                                    <div class="source-value">${formatNumber(ipccResults.annual_CH4_downstream_le_20)}</div>
                                    <div class="source-unit">kg CH₄/年</div>
                                </div>
                            </div>
                        </div>
                        ${ipccResults.reservoir_age > 20 ? `
                        <div class="source-group">
                            <h4>库龄>20年阶段</h4>
                            <div class="source-items">
                                <div class="source-item">
                                    <div class="source-label">水库表面CH₄排放</div>
                                    <div class="source-value">${formatNumber(ipccResults.annual_CH4_res_surface_gt_20)}</div>
                                    <div class="source-unit">kg CO₂-当量/年</div>
                                </div>
                                <div class="source-item">
                                    <div class="source-label">大坝下游CH₄排放</div>
                                    <div class="source-value">${formatNumber(ipccResults.annual_CH4_downstream_gt_20)}</div>
                                    <div class="source-unit">kg CO₂-当量/年</div>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- 详细计算过程 -->
                <div class="chart-container">
                    <h3 class="chart-title">详细计算过程</h3>
                    <div class="calculation-details">
                        <div class="detail-section">
                            <h4>输入参数</h4>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <span class="detail-label">气候区</span>
                                    <span class="detail-value">${ipccResults.climate_region}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">营养状态</span>
                                    <span class="detail-value">${ipccResults.trophic_status}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">水库年龄</span>
                                    <span class="detail-value">${ipccResults.reservoir_age} 年</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">水库面积</span>
                                    <span class="detail-value">${formatNumber(ipccResults.surface_area_ha)} 公顷</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <h4>排放因子</h4>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <span class="detail-label">CO₂排放因子</span>
                                    <span class="detail-value">${formatNumber(ipccResults.EF_CO2_age_le_20)} tCO₂-C/(ha·yr)</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">≤20年CH₄排放因子</span>
                                    <span class="detail-value">${formatNumber(ipccResults.EF_CH4_age_le_20)} kgCH₄/(ha·yr)</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">>20年CH₄排放因子</span>
                                    <span class="detail-value">${formatNumber(ipccResults.EF_CH4_age_gt_20)} kgCH₄/(ha·yr)</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">营养状态调整系数</span>
                                    <span class="detail-value">${formatNumber(ipccResults.trophic_factor)}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <h4>中间计算值</h4>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <span class="detail-label">年均CO₂排放总量</span>
                                    <span class="detail-value">${formatNumber(ipccResults.F_CO2_annual)} tCO₂-C/yr</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">≤20年水库表面CH₄排放</span>
                                    <span class="detail-value">${formatNumber(ipccResults.F_CH4_res_le_20_annual)} kg CH₄/年</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">≤20年下游CH₄排放</span>
                                    <span class="detail-value">${formatNumber(ipccResults.F_CH4_downstream_le_20_annual)} kg CH₄/年</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">>20年水库表面CH₄排放</span>
                                    <span class="detail-value">${formatNumber(ipccResults.F_CH4_res_gt_20_annual)} kg CH₄/年</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">>20年下游CH₄排放</span>
                                    <span class="detail-value">${formatNumber(ipccResults.F_CH4_downstream_gt_20_annual)} kg CH₄/年</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <h4>分阶段CH₄排放总量</h4>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <span class="detail-label">≤20年CH₄排放总量</span>
                                    <span class="detail-value">${formatNumber(ipccResults.E_CH4_le_20_total)} tCO₂-当量</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">>20年CH₄排放总量</span>
                                    <span class="detail-value">${formatNumber(ipccResults.E_CH4_gt_20_total)} tCO₂-当量</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <h4>常量</h4>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <span class="detail-label">CO₂相对分子质量</span>
                                    <span class="detail-value">${ipccResults.M_CO2}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">C相对原子质量</span>
                                    <span class="detail-value">${ipccResults.M_C}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">下游CH₄通量比值</span>
                                    <span class="detail-value">${ipccResults.R_d_i}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">CH₄全球变暖潜势</span>
                                    <span class="detail-value">${ipccResults.GWP_100yr_CH4}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 获取气候区标签
function getClimateRegionLabel(region) {
    // 现在气候区已经是中文，直接返回
    return region || '未知区域';
}

// 获取营养状态标签
function getTrophicStatusLabel(status) {
    const labels = {
        'Oligotrophic': '贫营养型',
        'Mesotrophic': '中营养型',
        'Eutrophic': '富营养型',
        'Hypereutrophic': '超富营养型'
    };
    return labels[status] || status;
}

// 生成敏感性分析HTML
function generateSensitivityHTML(sensitivity) {
    if (!sensitivity || !Array.isArray(sensitivity) || sensitivity.length === 0) return '';
    
    const sortedParams = sensitivity.sort((a, b) => Math.abs(b.rank_correlation) - Math.abs(a.rank_correlation));
    
    return `
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">敏感性分析结果</h2>
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <h3 class="chart-title">参数敏感性分析</h3>
                    <div class="tornado-chart">
                        ${sortedParams.map((data) => `
                            <div class="tornado-item">
                                <div class="tornado-label">${getParameterLabel(data.parameter)}</div>
                                <div class="tornado-bar" style="width: ${Math.abs(data.rank_correlation) * 100}%;">
                                    ${(Math.abs(data.rank_correlation) * 100).toFixed(1)}%
                                </div>
                                <div class="tornado-value">${data.rank_correlation.toFixed(3)}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 获取参数标签
function getParameterLabel(param) {
    const labels = {
        'Surface Area': '水库面积',
        'CH4 Emission Factor': '甲烷排放因子',
        'CO2 Emission Factor': '二氧化碳排放因子',
        'surface_area': '水库面积',
        'reservoir_age': '水库年龄',
        'total_phosphorus': '总磷浓度',
        'total_nitrogen': '总氮浓度',
        'chlorophyll_a': '叶绿素a'
    };
    return labels[param] || param;
}

// 格式化数字
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(2) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(2) + 'K';
    } else {
        return num.toFixed(2);
    }
}

// 显示加载状态
function showLoading() {
    document.getElementById('loadingContainer').style.display = 'block';
    document.getElementById('calculateBtn').disabled = true;
}

// 隐藏加载状态
function hideLoading() {
    document.getElementById('loadingContainer').style.display = 'none';
    document.getElementById('calculateBtn').disabled = false;
}

// 显示成功消息
function showSuccess(message) {
    showAlert(message, 'success');
}

// 显示错误消息
function showError(message) {
    showAlert(message, 'error');
}

// 显示警告消息
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    document.querySelector('.main-content').insertBefore(alertDiv, document.querySelector('.main-content').firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// 下载报告
function downloadReport() {
    if (!currentAnalysis) {
        showError('没有可下载的结果');
        return;
    }
    
    // 这里应该调用后端API生成PDF报告
    showSuccess('报告下载功能正在开发中');
}

// 保存结果
function saveResults() {
    if (!currentAnalysis) {
        showError('没有可保存的结果');
        return;
    }
    
    // 这里应该调用后端API保存结果
    showSuccess('结果保存功能正在开发中');
}

// 已移除头像与下拉菜单相关功能

// 初始化交互式地图
function initializeMap() {
    console.log('Initializing map...');
    
    // 检查地图容器是否存在
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.error('Map container not found');
        return;
    }
    
    console.log('Map container found:', mapContainer);
    console.log('Map container dimensions:', mapContainer.offsetWidth, 'x', mapContainer.offsetHeight);
    
    // 检查Leaflet是否已加载
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded, retrying in 1 second...');
        setTimeout(initializeMap, 1000);
        return;
    }
    
    console.log('Leaflet loaded successfully, version:', L.version);
    console.log('Creating map...');
    
    try {
        // 如果地图已经存在，先销毁它
        if (map) {
            map.remove();
            map = null;
        }
        
        // 创建地图实例，默认显示中国
        map = L.map('map', {
            center: [35.0, 105.0],
            zoom: 4,
            zoomControl: true,
            attributionControl: true
        });
        
        console.log('Map created successfully');
        
        // 立即刷新地图尺寸
        map.invalidateSize();
        console.log('Map size invalidated after creation');
        
        // 添加地图图层 - 使用多个备用源
        const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18,
            minZoom: 2
        });
        
        // 添加错误处理
        tileLayer.on('tileerror', function(error) {
            console.warn('Tile loading error:', error);
        });
        
        tileLayer.addTo(map);
        
        console.log('Tile layer added');
        
        // 地图点击事件
        map.on('click', function(e) {
            const lat = e.latlng.lat;
            const lng = e.latlng.lng;
            
            // 标准化坐标
            const normalized = normalizeCoordinates(lat, lng);
            
            console.log('Map clicked:', lat, lng, '-> normalized:', normalized);
            
            // 更新坐标输入框
            const latInput = document.getElementById('latitude');
            const lngInput = document.getElementById('longitude');
            
            if (latInput && lngInput) {
                latInput.value = normalized.lat.toFixed(4);
                lngInput.value = normalized.lng.toFixed(4);
                
                // 触发输入事件以更新气候区域
                latInput.dispatchEvent(new Event('input'));
                lngInput.dispatchEvent(new Event('input'));
            }
            
            // 更新标记
            updateMapMarker(normalized.lat, normalized.lng);
        });
        
        // 添加地图加载完成事件
        map.whenReady(function() {
            console.log('Map is ready');
            
            // 强制刷新地图尺寸
            setTimeout(function() {
                map.invalidateSize();
                console.log('Map size invalidated');
            }, 100);
            
            // 添加默认标记（北京）
            updateMapMarker(39.9042, 116.4074);
            
            // 设置初始坐标
            const latInput = document.getElementById('latitude');
            const lngInput = document.getElementById('longitude');
            if (latInput && lngInput) {
                latInput.value = '39.9042';
                lngInput.value = '116.4074';
            }
        });
        
        console.log('Map initialized successfully');
        
    } catch (error) {
        console.error('Error initializing map:', error);
        // 显示错误信息
        mapContainer.innerHTML = `
            <div style="
                display: flex; 
                align-items: center; 
                justify-content: center; 
                height: 400px; 
                color: #666; 
                font-size: 14px;
                background: #f8fafc;
                border: 2px dashed #e2e8f0;
                border-radius: 8px;
                flex-direction: column;
                gap: 8px;
            ">
                <i class="fas fa-exclamation-triangle" style="font-size: 24px; color: #f59e0b;"></i>
                <div>地图加载失败，请检查网络连接或刷新页面重试</div>
                <button onclick="initializeMap()" style="
                    padding: 8px 16px;
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 12px;
                ">重新加载地图</button>
            </div>
        `;
    }
}

// 更新地图标记的辅助函数
function updateMapMarker(lat, lng) {
    if (!map) return;
    
    try {
        // 移除现有标记
        if (marker) {
            map.removeLayer(marker);
        }
        
        // 添加新标记
        marker = L.marker([lat, lng]).addTo(map);
        marker.bindPopup(`位置: ${lat.toFixed(4)}, ${lng.toFixed(4)}`).openPopup();
        
        console.log('Marker updated:', lat, lng);
    } catch (error) {
        console.error('Error updating marker:', error);
    }
}

// 从坐标输入框更新地图标记
function updateMapFromCoordinates() {
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    
    if (!latInput || !lngInput) return;
    
    const lat = parseFloat(latInput.value);
    const lng = parseFloat(lngInput.value);
    
    if (!isNaN(lat) && !isNaN(lng) && map) {
        // 标准化坐标
        const normalized = normalizeCoordinates(lat, lng);
        
        // 如果坐标被标准化了，更新输入框
        if (normalized.lat !== lat || normalized.lng !== lng) {
            latInput.value = normalized.lat.toFixed(4);
            lngInput.value = normalized.lng.toFixed(4);
        }
        
        try {
            // 更新地图视图
            map.setView([normalized.lat, normalized.lng], 10);
            
            // 更新标记
            updateMapMarker(normalized.lat, normalized.lng);
        } catch (error) {
            console.error('Error updating map from coordinates:', error);
        }
    }
}

// 绘制不确定性分析图表
function drawUncertaintyChart(uncertainty) {
    if (!uncertainty || !uncertainty.CO2_equivalent) return;
    
    const stats = uncertainty.CO2_equivalent;
    const chartContainer = document.getElementById('uncertaintyChart');
    if (!chartContainer) return;
    
    // 使用真实的模拟数据绘制直方图
    const rawData = stats.raw_data;
    if (!rawData || rawData.length === 0) {
        console.warn('No raw data available for uncertainty chart');
        return;
    }
    
    const mean = stats.mean;
    const std = stats.std;
    const ci_lower = stats.ci_lower;
    const ci_upper = stats.ci_upper;
    
    // 计算直方图的分组 - 增加分组数量以更好地显示分布
    const numBins = Math.min(80, Math.max(30, Math.floor(Math.sqrt(rawData.length) * 1.5)));
    const dataMin = Math.min(...rawData);
    const dataMax = Math.max(...rawData);
    const binWidth = (dataMax - dataMin) / numBins;
    
    // 创建直方图数据
    const bins = new Array(numBins).fill(0);
    const binCenters = [];
    
    for (let i = 0; i < numBins; i++) {
        binCenters.push(dataMin + (i + 0.5) * binWidth);
    }
    
    // 统计每个分组的频次
    rawData.forEach(value => {
        const binIndex = Math.min(numBins - 1, Math.floor((value - dataMin) / binWidth));
        bins[binIndex]++;
    });
    
    // 转换为概率密度
    const totalCount = rawData.length;
    const probabilities = bins.map(count => count / (totalCount * binWidth));
    
    // 创建SVG图表 - 增加高度和改进布局
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '400');
    svg.setAttribute('viewBox', '0 0 900 400');
    svg.style.border = '1px solid #e2e8f0';
    svg.style.borderRadius = '12px';
    svg.style.backgroundColor = '#ffffff';
    svg.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
    
    // 增加边距以防止标签重叠
    const margin = { top: 40, right: 40, bottom: 80, left: 80 };
    const width = 900 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    // 缩放函数
    const xScale = (x) => margin.left + ((x - dataMin) / (dataMax - dataMin)) * width;
    const yScale = (y) => margin.top + height - (y / Math.max(...probabilities)) * height;
    
    // 创建渐变定义
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    
    // 柱状图渐变
    const barGradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
    barGradient.setAttribute('id', 'barGradient');
    barGradient.setAttribute('x1', '0%');
    barGradient.setAttribute('y1', '0%');
    barGradient.setAttribute('x2', '0%');
    barGradient.setAttribute('y2', '100%');
    
    const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop1.setAttribute('offset', '0%');
    stop1.setAttribute('stop-color', '#3b82f6');
    stop1.setAttribute('stop-opacity', '0.9');
    
    const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop2.setAttribute('offset', '100%');
    stop2.setAttribute('stop-color', '#1e40af');
    stop2.setAttribute('stop-opacity', '0.7');
    
    barGradient.appendChild(stop1);
    barGradient.appendChild(stop2);
    defs.appendChild(barGradient);
    svg.appendChild(defs);
    
    // 绘制网格线
    const maxProb = Math.max(...probabilities);
    const numYTicks = 6;
    for (let i = 1; i < numYTicks; i++) {
        const y = margin.top + height - (i / numYTicks) * height;
        const gridLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        gridLine.setAttribute('x1', margin.left);
        gridLine.setAttribute('y1', y);
        gridLine.setAttribute('x2', margin.left + width);
        gridLine.setAttribute('y2', y);
        gridLine.setAttribute('stroke', '#f3f4f6');
        gridLine.setAttribute('stroke-width', '1');
        svg.appendChild(gridLine);
    }
    
    // 绘制95%置信区间阴影
    const ciRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    ciRect.setAttribute('x', xScale(ci_lower));
    ciRect.setAttribute('y', margin.top);
    ciRect.setAttribute('width', xScale(ci_upper) - xScale(ci_lower));
    ciRect.setAttribute('height', height);
    ciRect.setAttribute('fill', 'rgba(16, 185, 129, 0.15)');
    ciRect.setAttribute('stroke', 'none');
    svg.appendChild(ciRect);
    
    // 绘制直方图柱状图
    binCenters.forEach((center, i) => {
        const barWidth = (width / numBins) * 0.9; // 增加柱子宽度
        const barHeight = height * (probabilities[i] / Math.max(...probabilities));
        const x = xScale(center) - barWidth / 2;
        const y = margin.top + height - barHeight;
        
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', x);
        rect.setAttribute('y', y);
        rect.setAttribute('width', barWidth);
        rect.setAttribute('height', barHeight);
        rect.setAttribute('fill', 'url(#barGradient)');
        rect.setAttribute('stroke', '#1e40af');
        rect.setAttribute('stroke-width', '0.5');
        rect.setAttribute('rx', '1'); // 圆角
        svg.appendChild(rect);
    });
    
    // 计算并绘制正态分布拟合曲线
    const normalCurve = [];
    const numCurvePoints = 200;
    for (let i = 0; i <= numCurvePoints; i++) {
        const x = dataMin + (dataMax - dataMin) * i / numCurvePoints;
        const y = (1 / (std * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / std, 2));
        normalCurve.push({ x, y });
    }
    
    // 绘制正态分布曲线
    const curvePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    let pathData = `M ${xScale(normalCurve[0].x)} ${yScale(normalCurve[0].y)}`;
    for (let i = 1; i < normalCurve.length; i++) {
        pathData += ` L ${xScale(normalCurve[i].x)} ${yScale(normalCurve[i].y)}`;
    }
    curvePath.setAttribute('d', pathData);
    curvePath.setAttribute('fill', 'none');
    curvePath.setAttribute('stroke', '#f59e0b');
    curvePath.setAttribute('stroke-width', '3');
    curvePath.setAttribute('stroke-linecap', 'round');
    svg.appendChild(curvePath);
    
    // 绘制均值线
    const meanLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    meanLine.setAttribute('x1', xScale(mean));
    meanLine.setAttribute('y1', margin.top);
    meanLine.setAttribute('x2', xScale(mean));
    meanLine.setAttribute('y2', margin.top + height);
    meanLine.setAttribute('stroke', '#ef4444');
    meanLine.setAttribute('stroke-width', '3');
    meanLine.setAttribute('stroke-dasharray', '8,4');
    svg.appendChild(meanLine);
    
    // 绘制置信区间边界线
    const ciLowerLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    ciLowerLine.setAttribute('x1', xScale(ci_lower));
    ciLowerLine.setAttribute('y1', margin.top);
    ciLowerLine.setAttribute('x2', xScale(ci_lower));
    ciLowerLine.setAttribute('y2', margin.top + height);
    ciLowerLine.setAttribute('stroke', '#10b981');
    ciLowerLine.setAttribute('stroke-width', '2');
    ciLowerLine.setAttribute('stroke-dasharray', '6,3');
    svg.appendChild(ciLowerLine);
    
    const ciUpperLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    ciUpperLine.setAttribute('x1', xScale(ci_upper));
    ciUpperLine.setAttribute('y1', margin.top);
    ciUpperLine.setAttribute('x2', xScale(ci_upper));
    ciUpperLine.setAttribute('y2', margin.top + height);
    ciUpperLine.setAttribute('stroke', '#10b981');
    ciUpperLine.setAttribute('stroke-width', '2');
    ciUpperLine.setAttribute('stroke-dasharray', '6,3');
    svg.appendChild(ciUpperLine);
    
    // 添加坐标轴
    const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    xAxis.setAttribute('x1', margin.left);
    xAxis.setAttribute('y1', margin.top + height);
    xAxis.setAttribute('x2', margin.left + width);
    xAxis.setAttribute('y2', margin.top + height);
    xAxis.setAttribute('stroke', '#374151');
    xAxis.setAttribute('stroke-width', '2');
    svg.appendChild(xAxis);
    
    const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    yAxis.setAttribute('x1', margin.left);
    yAxis.setAttribute('y1', margin.top);
    yAxis.setAttribute('x2', margin.left);
    yAxis.setAttribute('y2', margin.top + height);
    yAxis.setAttribute('stroke', '#374151');
    yAxis.setAttribute('stroke-width', '2');
    svg.appendChild(yAxis);
    
    // 添加X轴刻度
    const numXTicks = 6;
    for (let i = 0; i <= numXTicks; i++) {
        const value = dataMin + (dataMax - dataMin) * i / numXTicks;
        const x = xScale(value);
        
        // 刻度线
        const tick = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        tick.setAttribute('x1', x);
        tick.setAttribute('y1', margin.top + height);
        tick.setAttribute('x2', x);
        tick.setAttribute('y2', margin.top + height + 8);
        tick.setAttribute('stroke', '#374151');
        tick.setAttribute('stroke-width', '2');
        svg.appendChild(tick);
        
        // 刻度标签
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', x);
        label.setAttribute('y', margin.top + height + 25);
        label.setAttribute('text-anchor', 'middle');
        label.setAttribute('font-size', '12');
        label.setAttribute('font-weight', '500');
        label.setAttribute('fill', '#374151');
        label.textContent = formatNumber(value);
        svg.appendChild(label);
    }
    
    // 添加Y轴刻度
    for (let i = 0; i <= numYTicks; i++) {
        const value = maxProb * i / numYTicks;
        const y = margin.top + height - (value / maxProb) * height;
        
        // 刻度线
        const tick = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        tick.setAttribute('x1', margin.left - 8);
        tick.setAttribute('y1', y);
        tick.setAttribute('x2', margin.left);
        tick.setAttribute('y2', y);
        tick.setAttribute('stroke', '#374151');
        tick.setAttribute('stroke-width', '2');
        svg.appendChild(tick);
        
        // 刻度标签
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', margin.left - 12);
        label.setAttribute('y', y + 4);
        label.setAttribute('text-anchor', 'end');
        label.setAttribute('font-size', '11');
        label.setAttribute('font-weight', '500');
        label.setAttribute('fill', '#374151');
        label.textContent = value > 0 ? value.toExponential(1) : '0';
        svg.appendChild(label);
    }
    
    // 添加轴标签
    const xLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    xLabel.setAttribute('x', margin.left + width / 2);
    xLabel.setAttribute('y', margin.top + height + 55);
    xLabel.setAttribute('text-anchor', 'middle');
    xLabel.setAttribute('font-size', '14');
    xLabel.setAttribute('font-weight', '600');
    xLabel.setAttribute('fill', '#374151');
    xLabel.textContent = '总排放量 (kg CO₂-当量/年)';
    svg.appendChild(xLabel);
    
    const yLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    yLabel.setAttribute('x', 20);
    yLabel.setAttribute('y', margin.top + height / 2);
    yLabel.setAttribute('text-anchor', 'middle');
    yLabel.setAttribute('font-size', '14');
    yLabel.setAttribute('font-weight', '600');
    yLabel.setAttribute('fill', '#374151');
    yLabel.setAttribute('transform', 'rotate(-90, 20, ' + (margin.top + height / 2) + ')');
    yLabel.textContent = '概率密度';
    svg.appendChild(yLabel);
    
    // 添加标题
    const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    title.setAttribute('x', margin.left + width / 2);
    title.setAttribute('y', 25);
    title.setAttribute('text-anchor', 'middle');
    title.setAttribute('font-size', '16');
    title.setAttribute('font-weight', '700');
    title.setAttribute('fill', '#1f2937');
    title.textContent = `蒙特卡洛模拟结果分布 (${rawData.length} 次模拟)`;
    svg.appendChild(title);
    
    // 重新设计图例 - 移到底部
    const legend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    legend.setAttribute('transform', 'translate(' + (margin.left + 20) + ', ' + (margin.top + height + 65) + ')');
    
    // 图例背景
    const legendBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    legendBg.setAttribute('x', -10);
    legendBg.setAttribute('y', -5);
    legendBg.setAttribute('width', width - 20);
    legendBg.setAttribute('height', 25);
    legendBg.setAttribute('fill', '#f9fafb');
    legendBg.setAttribute('stroke', '#e5e7eb');
    legendBg.setAttribute('stroke-width', '1');
    legendBg.setAttribute('rx', '6');
    legend.appendChild(legendBg);
    
    // 直方图图例
    const histLegend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    const histLegendRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    histLegendRect.setAttribute('x', 0);
    histLegendRect.setAttribute('y', 0);
    histLegendRect.setAttribute('width', 16);
    histLegendRect.setAttribute('height', 12);
    histLegendRect.setAttribute('fill', 'url(#barGradient)');
    histLegendRect.setAttribute('stroke', '#1e40af');
    histLegendRect.setAttribute('stroke-width', '1');
    histLegendRect.setAttribute('rx', '2');
    histLegend.appendChild(histLegendRect);
    
    const histLegendText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    histLegendText.setAttribute('x', 22);
    histLegendText.setAttribute('y', 9);
    histLegendText.setAttribute('font-size', '12');
    histLegendText.setAttribute('font-weight', '500');
    histLegendText.setAttribute('fill', '#374151');
    histLegendText.textContent = '模拟数据分布';
    histLegend.appendChild(histLegendText);
    legend.appendChild(histLegend);
    
    // 正态分布曲线图例
    const normalLegend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    normalLegend.setAttribute('transform', 'translate(140, 0)');
    const normalLegendLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    normalLegendLine.setAttribute('x1', 0);
    normalLegendLine.setAttribute('y1', 6);
    normalLegendLine.setAttribute('x2', 16);
    normalLegendLine.setAttribute('y2', 6);
    normalLegendLine.setAttribute('stroke', '#f59e0b');
    normalLegendLine.setAttribute('stroke-width', '3');
    normalLegend.appendChild(normalLegendLine);
    
    const normalLegendText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    normalLegendText.setAttribute('x', 22);
    normalLegendText.setAttribute('y', 9);
    normalLegendText.setAttribute('font-size', '12');
    normalLegendText.setAttribute('font-weight', '500');
    normalLegendText.setAttribute('fill', '#374151');
    normalLegendText.textContent = '正态分布拟合';
    normalLegend.appendChild(normalLegendText);
    legend.appendChild(normalLegend);
    
    // 均值线图例
    const meanLegend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    meanLegend.setAttribute('transform', 'translate(270, 0)');
    const meanLegendLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    meanLegendLine.setAttribute('x1', 0);
    meanLegendLine.setAttribute('y1', 6);
    meanLegendLine.setAttribute('x2', 16);
    meanLegendLine.setAttribute('y2', 6);
    meanLegendLine.setAttribute('stroke', '#ef4444');
    meanLegendLine.setAttribute('stroke-width', '3');
    meanLegendLine.setAttribute('stroke-dasharray', '8,4');
    meanLegend.appendChild(meanLegendLine);
    
    const meanLegendText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    meanLegendText.setAttribute('x', 22);
    meanLegendText.setAttribute('y', 9);
    meanLegendText.setAttribute('font-size', '12');
    meanLegendText.setAttribute('font-weight', '500');
    meanLegendText.setAttribute('fill', '#374151');
    meanLegendText.textContent = `均值 (${formatNumber(mean)})`;
    meanLegend.appendChild(meanLegendText);
    legend.appendChild(meanLegend);
    
    // 置信区间图例
    const ciLegend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    ciLegend.setAttribute('transform', 'translate(450, 0)');
    const ciLegendRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    ciLegendRect.setAttribute('x', 0);
    ciLegendRect.setAttribute('y', 0);
    ciLegendRect.setAttribute('width', 16);
    ciLegendRect.setAttribute('height', 12);
    ciLegendRect.setAttribute('fill', 'rgba(16, 185, 129, 0.15)');
    ciLegendRect.setAttribute('stroke', '#10b981');
    ciLegendRect.setAttribute('stroke-width', '1');
    ciLegendRect.setAttribute('rx', '2');
    ciLegend.appendChild(ciLegendRect);
    
    const ciLegendText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    ciLegendText.setAttribute('x', 22);
    ciLegendText.setAttribute('y', 9);
    ciLegendText.setAttribute('font-size', '12');
    ciLegendText.setAttribute('font-weight', '500');
    ciLegendText.setAttribute('fill', '#374151');
    ciLegendText.textContent = '95% 置信区间';
    ciLegend.appendChild(ciLegendText);
    legend.appendChild(ciLegend);
    
    svg.appendChild(legend);
    
    // 清空容器并添加SVG
    chartContainer.innerHTML = '';
    chartContainer.appendChild(svg);
    
    // 确保图表容器可以显示所有元素，包括横坐标和图例
    chartContainer.style.overflow = 'visible';
    chartContainer.style.position = 'relative';
    chartContainer.style.zIndex = '1';
    chartContainer.style.marginBottom = '80px'; // 为横坐标和图例预留足够空间
}