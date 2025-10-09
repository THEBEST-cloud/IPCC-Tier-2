// 全局变量
let currentAnalysis = null;

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
}

// 设置事件监听器
function setupEventListeners() {
    // 计算按钮
    document.getElementById('calculateBtn').addEventListener('click', handleCalculate);
    
    // 保存草稿按钮
    document.getElementById('saveDraftBtn').addEventListener('click', handleSaveDraft);
    
    // 表单输入变化
    document.getElementById('latitude').addEventListener('input', updateClimateRegion);
    document.getElementById('longitude').addEventListener('input', updateClimateRegion);
    
    // 水质参数变化
    document.getElementById('totalPhosphorus').addEventListener('input', updateTrophicStatus);
    document.getElementById('totalNitrogen').addEventListener('input', updateTrophicStatus);
    document.getElementById('chlorophyllA').addEventListener('input', updateTrophicStatus);
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
        'reservoirAge': 20.0,
        'meanDepth': 20.0
    };
    
    const input = document.getElementById(inputId);
    if (input && defaults[inputId]) {
        input.value = defaults[inputId];
    }
}

// 更新营养状态
function updateTrophicStatus() {
    const tp = parseFloat(document.getElementById('totalPhosphorus').value);
    const tn = parseFloat(document.getElementById('totalNitrogen').value);
    const chla = parseFloat(document.getElementById('chlorophyllA').value);
    
    if (isNaN(tp) && isNaN(tn) && isNaN(chla)) {
        document.getElementById('trophicStatus').style.display = 'none';
        return;
    }
    
    // 简单的营养状态评估
    let status = 'Oligotrophic';
    let statusText = '贫营养 (Oligotrophic)';
    
    if (tp > 30 || tn > 1.5 || chla > 10) {
        status = 'Eutrophic';
        statusText = '富营养 (Eutrophic)';
    } else if (tp > 15 || tn > 1.0 || chla > 5) {
        status = 'Mesotrophic';
        statusText = '中营养 (Mesotrophic)';
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
        mean_depth: parseFloat(document.getElementById('meanDepth').value) || null,
        water_quality: {
            total_phosphorus: parseFloat(document.getElementById('totalPhosphorus').value) || null,
            total_nitrogen: parseFloat(document.getElementById('totalNitrogen').value) || null,
            chlorophyll_a: parseFloat(document.getElementById('chlorophyllA').value) || null,
            secchi_depth: null
        },
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
    
    // 滚动到结果区域
    container.scrollIntoView({ behavior: 'smooth' });
}

// 生成结果HTML
function generateResultsHTML(result) {
    const emissions = result.emissions;
    const uncertainty = result.uncertainty;
    const sensitivity = result.sensitivity;
    
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
            <div class="emission-card n2o">
                <div class="emission-icon">
                    <i class="fas fa-wind"></i>
                </div>
                <div class="emission-label">氧化亚氮 (N₂O)</div>
                <div class="emission-value">${formatNumber(emissions.total_n2o_emissions)}</div>
                <div class="emission-unit">kg/年</div>
            </div>
        </div>
        
        <div class="total-emissions">
            <div class="total-value">${formatNumber(emissions.co2_equivalent)}</div>
            <div class="total-label">总温室气体排放量 (kg CO₂-当量/年)</div>
        </div>
        
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
    if (!uncertainty || !uncertainty.co2_equivalent) return '';
    
    const stats = uncertainty.co2_equivalent;
    
    return `
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">不确定性分析结果</h2>
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <h3 class="chart-title">总排放量概率分布</h3>
                    <div id="uncertaintyChart" style="height: 300px;"></div>
                </div>
                
                <div class="chart-container">
                    <h3 class="chart-title">关键统计数据</h3>
                    <table class="stats-table">
                        <thead>
                            <tr>
                                <th>统计指标</th>
                                <th>数值</th>
                                <th>单位</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>均值</td>
                                <td>${formatNumber(stats.mean)}</td>
                                <td>kg CO₂-当量/年</td>
                            </tr>
                            <tr>
                                <td>中位数</td>
                                <td>${formatNumber(stats.median)}</td>
                                <td>kg CO₂-当量/年</td>
                            </tr>
                            <tr>
                                <td>标准差</td>
                                <td>${formatNumber(stats.std)}</td>
                                <td>kg CO₂-当量/年</td>
                            </tr>
                            <tr>
                                <td>95% 置信区间下限</td>
                                <td>${formatNumber(stats.ci_lower)}</td>
                                <td>kg CO₂-当量/年</td>
                            </tr>
                            <tr>
                                <td>95% 置信区间上限</td>
                                <td>${formatNumber(stats.ci_upper)}</td>
                                <td>kg CO₂-当量/年</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// 生成敏感性分析HTML
function generateSensitivityHTML(sensitivity) {
    if (!sensitivity || !sensitivity.parameters) return '';
    
    const params = sensitivity.parameters;
    const sortedParams = Object.entries(params)
        .sort(([,a], [,b]) => Math.abs(b.correlation) - Math.abs(a.correlation));
    
    return `
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">敏感性分析结果</h2>
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <h3 class="chart-title">参数敏感性分析</h3>
                    <div class="tornado-chart">
                        ${sortedParams.map(([param, data]) => `
                            <div class="tornado-item">
                                <div class="tornado-label">${getParameterLabel(param)}</div>
                                <div class="tornado-bar" style="width: ${Math.abs(data.correlation) * 100}%;">
                                    ${(Math.abs(data.correlation) * 100).toFixed(1)}%
                                </div>
                                <div class="tornado-value">${data.correlation.toFixed(3)}</div>
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
        'surface_area': '水库面积',
        'reservoir_age': '水库年龄',
        'mean_depth': '平均水深',
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