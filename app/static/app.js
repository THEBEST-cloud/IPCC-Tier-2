// 全局变量
let currentAnalysis = null;
let map = null;
let marker = null;

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

    uncertaintyCheckbox.addEventListener('change', function() {
        monteCarloSelect.style.display = this.checked ? 'block' : 'none';
    });

    sensitivityCheckbox.addEventListener('change', function() {
        sensitivityOptions.style.display = this.checked ? 'block' : 'none';
    });

    // 初始状态
    monteCarloSelect.style.display = 'block';
    sensitivityOptions.style.display = 'block';
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

// 更新气候区域
async function updateClimateRegion() {
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);
    
    if (isNaN(latitude) || isNaN(longitude)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/climate-region/${latitude}`);
        const data = await response.json();
        
        document.getElementById('climateRegion').value = data.climate_region;
        
        // 更新默认值
        updateDefaultValues(data.climate_region);
    } catch (error) {
        console.error('Error fetching climate region:', error);
    }
}

// 更新默认值
function updateDefaultValues(climateRegion) {
    const defaults = {
        'Tropical': { area: 15.0, depth: 25.0 },
        'Temperate': { area: 10.0, depth: 20.0 },
        'Boreal': { area: 8.0, depth: 15.0 },
        'Polar': { area: 5.0, depth: 10.0 }
    };
    
    const regionDefaults = defaults[climateRegion] || defaults['Temperate'];
    
    document.getElementById('defaultArea').textContent = regionDefaults.area;
    document.getElementById('defaultDepth').textContent = regionDefaults.depth;
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
                <div class="emission-unit">kg/年</div>
            </div>
            <div class="emission-card co2">
                <div class="emission-icon">
                    <i class="fas fa-smog"></i>
                </div>
                <div class="emission-label">二氧化碳 (CO₂)</div>
                <div class="emission-value">${formatNumber(emissions.total_co2_emissions)}</div>
                <div class="emission-unit">kg/年</div>
            </div>
        </div>
        
        <div class="total-emissions">
            <div class="total-value">${formatNumber(emissions.co2_equivalent)}</div>
            <div class="total-label">总温室气体排放量 (kg CO₂-当量/年)</div>
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
                    不确定性分析结果
                </h2>
                <p class="card-subtitle">基于蒙特卡洛模拟的概率分布分析</p>
            </div>
            <div class="card-body">
                <!-- 概率分布图 -->
                <div class="chart-container">
                    <h3 class="chart-title">总排放量概率分布图</h3>
                    <div class="chart-description">
                        <p>下图显示了基于蒙特卡洛模拟的总排放量概率分布，阴影区域表示95%置信区间</p>
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
                                <td>5%概率低于此值</td>
                            </tr>
                            <tr>
                                <td>P25</td>
                                <td>${formatNumber(stats.percentile_25)}</td>
                                <td>25%</td>
                                <td>第一四分位数</td>
                            </tr>
                            <tr>
                                <td>P50</td>
                                <td>${formatNumber(stats.percentile_50)}</td>
                                <td>50%</td>
                                <td>中位数</td>
                            </tr>
                            <tr>
                                <td>P75</td>
                                <td>${formatNumber(stats.percentile_75)}</td>
                                <td>75%</td>
                                <td>第三四分位数</td>
                            </tr>
                            <tr>
                                <td>P95</td>
                                <td>${formatNumber(stats.percentile_95)}</td>
                                <td>95%</td>
                                <td>95%概率低于此值</td>
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
                            <div class="emission-value">${formatNumber(ipccResults.E_CO2)}</div>
                            <div class="emission-unit">tCO₂-当量</div>
                        </div>
                        <div class="emission-item ch4">
                            <div class="emission-label">CH₄排放总量 (E_CH₄)</div>
                            <div class="emission-value">${formatNumber(ipccResults.E_CH4)}</div>
                            <div class="emission-unit">tCO₂-当量</div>
                        </div>
                    </div>
                </div>
                
                <!-- 年均排放量 -->
                <div class="chart-container">
                    <h3 class="chart-title">年均排放量</h3>
                    <div class="annual-emissions">
                        <div class="annual-item">
                            <div class="annual-label">年均CO₂排放量</div>
                            <div class="annual-value">${formatNumber(ipccResults.annual_CO2)}</div>
                            <div class="annual-unit">kg CO₂-当量/年</div>
                        </div>
                        <div class="annual-item">
                            <div class="annual-label">≤20年CH₄年均排放量</div>
                            <div class="annual-value">${formatNumber(ipccResults.annual_CH4_age_le_20)}</div>
                            <div class="annual-unit">kg CO₂-当量/年</div>
                        </div>
                        <div class="annual-item">
                            <div class="annual-label">>20年CH₄年均排放量</div>
                            <div class="annual-value">${formatNumber(ipccResults.annual_CH4_age_gt_20)}</div>
                            <div class="annual-unit">kg CO₂-当量/年</div>
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
                                    <div class="source-unit">kg CO₂-当量/年</div>
                                </div>
                                <div class="source-item">
                                    <div class="source-label">大坝下游CH₄排放</div>
                                    <div class="source-value">${formatNumber(ipccResults.annual_CH4_downstream_le_20)}</div>
                                    <div class="source-unit">kg CO₂-当量/年</div>
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
                                    <span class="detail-value">${formatNumber(ipccResults.F_CO2_tot)} tCO₂-C/yr</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">≤20年水库表面CH₄排放</span>
                                    <span class="detail-value">${formatNumber(ipccResults.F_CH4_res_age_le_20)} kgCH₄/yr</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">≤20年下游CH₄排放</span>
                                    <span class="detail-value">${formatNumber(ipccResults.F_CH4_downstream_age_le_20)} kgCH₄/yr</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">>20年水库表面CH₄排放</span>
                                    <span class="detail-value">${formatNumber(ipccResults.F_CH4_res_age_gt_20)} kgCH₄/yr</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">>20年下游CH₄排放</span>
                                    <span class="detail-value">${formatNumber(ipccResults.F_CH4_downstream_age_gt_20)} kgCH₄/yr</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <h4>分阶段CH₄排放总量</h4>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <span class="detail-label">≤20年CH₄排放总量</span>
                                    <span class="detail-value">${formatNumber(ipccResults.E_CH4_age_le_20)} tCO₂-当量</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">>20年CH₄排放总量</span>
                                    <span class="detail-value">${formatNumber(ipccResults.E_CH4_age_gt_20)} tCO₂-当量</span>
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
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    } else {
        return num.toFixed(1);
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

// 用户下拉菜单功能
function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('show');
}

// 点击外部关闭下拉菜单
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('userDropdown');
    const avatar = document.querySelector('.user-avatar');
    
    if (!avatar.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

// 初始化交互式地图
function initializeMap() {
    console.log('Initializing map...');
    
    // 检查地图容器是否存在
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.error('Map container not found');
        return;
    }
    
    // 检查Leaflet是否已加载
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded, retrying in 1 second...');
        setTimeout(initializeMap, 1000);
        return;
    }
    
    console.log('Leaflet loaded, creating map...');
    
    try {
        // 创建地图实例，默认显示中国
        map = L.map('map', {
            center: [35.0, 105.0],
            zoom: 4,
            zoomControl: true
        });
        
        console.log('Map created successfully');
        
        // 添加地图图层
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(map);
        
        console.log('Tile layer added');
        
        // 地图点击事件
        map.on('click', function(e) {
            const lat = e.latlng.lat;
            const lng = e.latlng.lng;
            
            console.log('Map clicked:', lat, lng);
            
            // 更新坐标输入框
            document.getElementById('latitude').value = lat.toFixed(4);
            document.getElementById('longitude').value = lng.toFixed(4);
            
            // 更新标记
            if (marker) {
                map.removeLayer(marker);
            }
            
            marker = L.marker([lat, lng]).addTo(map);
            marker.bindPopup(`位置: ${lat.toFixed(4)}, ${lng.toFixed(4)}`).openPopup();
            
            // 更新气候区域
            updateClimateRegion();
        });
        
        // 添加默认标记（北京）
        marker = L.marker([39.9042, 116.4074]).addTo(map);
        marker.bindPopup('默认位置: 北京').openPopup();
        
        // 设置初始坐标
        document.getElementById('latitude').value = '39.9042';
        document.getElementById('longitude').value = '116.4074';
        
        console.log('Map initialized successfully');
        
    } catch (error) {
        console.error('Error initializing map:', error);
        // 显示错误信息
        mapContainer.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666; font-size: 14px;"><i class="fas fa-exclamation-triangle" style="margin-right: 8px;"></i>地图加载失败，请刷新页面重试</div>';
    }
}

// 从坐标输入框更新地图标记
function updateMapFromCoordinates() {
    const lat = parseFloat(document.getElementById('latitude').value);
    const lng = parseFloat(document.getElementById('longitude').value);
    
    if (!isNaN(lat) && !isNaN(lng) && map) {
        // 更新地图视图
        map.setView([lat, lng], 10);
        
        // 更新标记
        if (marker) {
            map.removeLayer(marker);
        }
        
        marker = L.marker([lat, lng]).addTo(map);
        marker.bindPopup(`位置: ${lat.toFixed(4)}, ${lng.toFixed(4)}`).openPopup();
    }
}

// 绘制不确定性分析图表
function drawUncertaintyChart(uncertainty) {
    if (!uncertainty || !uncertainty.CO2_equivalent) return;
    
    const stats = uncertainty.CO2_equivalent;
    const chartContainer = document.getElementById('uncertaintyChart');
    if (!chartContainer) return;
    
    // 生成模拟数据用于绘制分布图
    const mean = stats.mean;
    const std = stats.std;
    const ci_lower = stats.ci_lower;
    const ci_upper = stats.ci_upper;
    
    // 生成正态分布数据点
    const xMin = Math.max(0, mean - 4 * std);
    const xMax = mean + 4 * std;
    const xPoints = [];
    const yPoints = [];
    
    for (let i = 0; i <= 100; i++) {
        const x = xMin + (xMax - xMin) * i / 100;
        const y = Math.exp(-0.5 * Math.pow((x - mean) / std, 2)) / (std * Math.sqrt(2 * Math.PI));
        xPoints.push(x);
        yPoints.push(y);
    }
    
    // 创建SVG图表
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '300');
    svg.setAttribute('viewBox', '0 0 800 300');
    svg.style.border = '1px solid #e2e8f0';
    svg.style.borderRadius = '8px';
    svg.style.backgroundColor = '#fafafa';
    
    // 绘制坐标轴
    const margin = { top: 20, right: 20, bottom: 40, left: 60 };
    const width = 800 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;
    
    // X轴
    const xScale = (x) => margin.left + ((x - xMin) / (xMax - xMin)) * width;
    const yScale = (y) => margin.top + height - (y / Math.max(...yPoints)) * height;
    
    // 绘制分布曲线
    const pathData = xPoints.map((x, i) => {
        const xPos = xScale(x);
        const yPos = yScale(yPoints[i]);
        return `${i === 0 ? 'M' : 'L'} ${xPos} ${yPos}`;
    }).join(' ');
    
    const curve = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    curve.setAttribute('d', pathData);
    curve.setAttribute('fill', 'none');
    curve.setAttribute('stroke', '#3b82f6');
    curve.setAttribute('stroke-width', '2');
    svg.appendChild(curve);
    
    // 绘制95%置信区间阴影
    const ciStart = xPoints.findIndex(x => x >= ci_lower);
    const ciEnd = xPoints.findIndex(x => x >= ci_upper);
    
    if (ciStart >= 0 && ciEnd >= 0) {
        const ciPath = `M ${xScale(xPoints[ciStart])} ${yScale(yPoints[ciStart])} ` +
                      xPoints.slice(ciStart, ciEnd + 1).map((x, i) => 
                          `L ${xScale(x)} ${yScale(yPoints[ciStart + i])}`
                      ).join(' ') +
                      ` L ${xScale(xPoints[ciEnd])} ${margin.top + height} ` +
                      `L ${xScale(xPoints[ciStart])} ${margin.top + height} Z`;
        
        const ciArea = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        ciArea.setAttribute('d', ciPath);
        ciArea.setAttribute('fill', 'rgba(59, 130, 246, 0.2)');
        ciArea.setAttribute('stroke', 'none');
        svg.insertBefore(ciArea, curve);
    }
    
    // 绘制均值线
    const meanLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    meanLine.setAttribute('x1', xScale(mean));
    meanLine.setAttribute('y1', margin.top);
    meanLine.setAttribute('x2', xScale(mean));
    meanLine.setAttribute('y2', margin.top + height);
    meanLine.setAttribute('stroke', '#ef4444');
    meanLine.setAttribute('stroke-width', '2');
    meanLine.setAttribute('stroke-dasharray', '5,5');
    svg.appendChild(meanLine);
    
    // 绘制置信区间边界线
    const ciLowerLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    ciLowerLine.setAttribute('x1', xScale(ci_lower));
    ciLowerLine.setAttribute('y1', margin.top);
    ciLowerLine.setAttribute('x2', xScale(ci_lower));
    ciLowerLine.setAttribute('y2', margin.top + height);
    ciLowerLine.setAttribute('stroke', '#10b981');
    ciLowerLine.setAttribute('stroke-width', '1');
    ciLowerLine.setAttribute('stroke-dasharray', '3,3');
    svg.appendChild(ciLowerLine);
    
    const ciUpperLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    ciUpperLine.setAttribute('x1', xScale(ci_upper));
    ciUpperLine.setAttribute('y1', margin.top);
    ciUpperLine.setAttribute('x2', xScale(ci_upper));
    ciUpperLine.setAttribute('y2', margin.top + height);
    ciUpperLine.setAttribute('stroke', '#10b981');
    ciUpperLine.setAttribute('stroke-width', '1');
    ciUpperLine.setAttribute('stroke-dasharray', '3,3');
    svg.appendChild(ciUpperLine);
    
    // 添加坐标轴
    const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    xAxis.setAttribute('x1', margin.left);
    xAxis.setAttribute('y1', margin.top + height);
    xAxis.setAttribute('x2', margin.left + width);
    xAxis.setAttribute('y2', margin.top + height);
    xAxis.setAttribute('stroke', '#374151');
    xAxis.setAttribute('stroke-width', '1');
    svg.appendChild(xAxis);
    
    const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    yAxis.setAttribute('x1', margin.left);
    yAxis.setAttribute('y1', margin.top);
    yAxis.setAttribute('x2', margin.left);
    yAxis.setAttribute('y2', margin.top + height);
    yAxis.setAttribute('stroke', '#374151');
    yAxis.setAttribute('stroke-width', '1');
    svg.appendChild(yAxis);
    
    // 添加标签
    const xLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    xLabel.setAttribute('x', margin.left + width / 2);
    xLabel.setAttribute('y', margin.top + height + 30);
    xLabel.setAttribute('text-anchor', 'middle');
    xLabel.setAttribute('font-size', '12');
    xLabel.setAttribute('fill', '#374151');
    xLabel.textContent = '总排放量 (kg CO₂-当量/年)';
    svg.appendChild(xLabel);
    
    const yLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    yLabel.setAttribute('x', 10);
    yLabel.setAttribute('y', margin.top + height / 2);
    yLabel.setAttribute('text-anchor', 'middle');
    yLabel.setAttribute('font-size', '12');
    yLabel.setAttribute('fill', '#374151');
    yLabel.setAttribute('transform', 'rotate(-90, 10, ' + (margin.top + height / 2) + ')');
    yLabel.textContent = '概率密度';
    svg.appendChild(yLabel);
    
    // 添加图例
    const legend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    legend.setAttribute('transform', 'translate(' + (margin.left + width - 200) + ', ' + (margin.top + 20) + ')');
    
    // 均值线图例
    const meanLegend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    const meanLegendLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    meanLegendLine.setAttribute('x1', 0);
    meanLegendLine.setAttribute('y1', 0);
    meanLegendLine.setAttribute('x2', 20);
    meanLegendLine.setAttribute('y2', 0);
    meanLegendLine.setAttribute('stroke', '#ef4444');
    meanLegendLine.setAttribute('stroke-width', '2');
    meanLegendLine.setAttribute('stroke-dasharray', '5,5');
    meanLegend.appendChild(meanLegendLine);
    
    const meanLegendText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    meanLegendText.setAttribute('x', 25);
    meanLegendText.setAttribute('y', 5);
    meanLegendText.setAttribute('font-size', '12');
    meanLegendText.setAttribute('fill', '#374151');
    meanLegendText.textContent = '均值';
    meanLegend.appendChild(meanLegendText);
    legend.appendChild(meanLegend);
    
    // 置信区间图例
    const ciLegend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    ciLegend.setAttribute('transform', 'translate(0, 20)');
    
    const ciLegendRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    ciLegendRect.setAttribute('x', 0);
    ciLegendRect.setAttribute('y', -5);
    ciLegendRect.setAttribute('width', 20);
    ciLegendRect.setAttribute('height', 10);
    ciLegendRect.setAttribute('fill', 'rgba(59, 130, 246, 0.2)');
    ciLegendRect.setAttribute('stroke', '#3b82f6');
    ciLegendRect.setAttribute('stroke-width', '1');
    ciLegend.appendChild(ciLegendRect);
    
    const ciLegendText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    ciLegendText.setAttribute('x', 25);
    ciLegendText.setAttribute('y', 5);
    ciLegendText.setAttribute('font-size', '12');
    ciLegendText.setAttribute('fill', '#374151');
    ciLegendText.textContent = '95% 置信区间';
    ciLegend.appendChild(ciLegendText);
    legend.appendChild(ciLegend);
    
    svg.appendChild(legend);
    
    // 清空容器并添加SVG
    chartContainer.innerHTML = '';
    chartContainer.appendChild(svg);
}