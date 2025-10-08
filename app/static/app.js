// Reservoir GHG Emissions Tool - Frontend JavaScript

// API Base URL
const API_BASE = '/api';

// Form submission handler
document.getElementById('analysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading state
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = 'Analyzing<span class="spinner"></span>';
    submitBtn.disabled = true;
    
    // Hide previous results
    document.getElementById('resultsContainer').classList.add('hidden');
    
    try {
        // Collect form data
        const formData = collectFormData();
        
        // Send request to API
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }
        
        const results = await response.json();
        
        // Display results
        displayResults(results);
        
        // Scroll to results
        document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Analysis error:', error);
    } finally {
        // Restore button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
});

// Collect form data
function collectFormData() {
    const data = {
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value),
        surface_area: parseFloat(document.getElementById('surfaceArea').value),
        reservoir_age: parseFloatOrNull(document.getElementById('reservoirAge').value),
        mean_depth: parseFloatOrNull(document.getElementById('meanDepth').value),
        run_uncertainty: document.getElementById('runUncertainty').checked,
        run_sensitivity: document.getElementById('runSensitivity').checked,
        uncertainty_iterations: parseInt(document.getElementById('uncertaintyIterations').value)
    };
    
    // Water quality data
    const totalP = parseFloatOrNull(document.getElementById('totalPhosphorus').value);
    const totalN = parseFloatOrNull(document.getElementById('totalNitrogen').value);
    const chlorophyll = parseFloatOrNull(document.getElementById('chlorophyllA').value);
    const secchi = parseFloatOrNull(document.getElementById('secchiDepth').value);
    
    if (totalP || totalN || chlorophyll || secchi) {
        data.water_quality = {
            total_phosphorus: totalP,
            total_nitrogen: totalN,
            chlorophyll_a: chlorophyll,
            secchi_depth: secchi
        };
    }
    
    // Custom emission factors
    const customCH4 = parseFloatOrNull(document.getElementById('customCH4').value);
    const customCO2 = parseFloatOrNull(document.getElementById('customCO2').value);
    const customN2O = parseFloatOrNull(document.getElementById('customN2O').value);
    
    if (customCH4) data.custom_ch4_ef = customCH4;
    if (customCO2) data.custom_co2_ef = customCO2;
    if (customN2O) data.custom_n2o_ef = customN2O;
    
    return data;
}

// Helper function to parse float or return null
function parseFloatOrNull(value) {
    if (value === '' || value === null || value === undefined) {
        return null;
    }
    const parsed = parseFloat(value);
    return isNaN(parsed) ? null : parsed;
}

// Display results
function displayResults(results) {
    const container = document.getElementById('resultsContainer');
    container.classList.remove('hidden');
    
    // Basic Information
    document.getElementById('resLatitude').textContent = results.latitude.toFixed(4);
    document.getElementById('resLongitude').textContent = results.longitude.toFixed(4);
    document.getElementById('resClimateRegion').textContent = results.climate_region;
    
    if (results.trophic_status) {
        document.getElementById('resTrophicStatus').textContent = results.trophic_status;
        document.getElementById('trophicStatusRow').classList.remove('hidden');
    } else {
        document.getElementById('trophicStatusRow').classList.add('hidden');
    }
    
    // Emission Factors
    document.getElementById('efCH4').textContent = formatNumber(results.emissions.ch4_emission_factor);
    document.getElementById('efCO2').textContent = formatNumber(results.emissions.co2_emission_factor);
    document.getElementById('efN2O').textContent = formatNumber(results.emissions.n2o_emission_factor);
    
    // Total Emissions
    document.getElementById('totalCH4').textContent = formatNumber(results.emissions.total_ch4_emissions);
    document.getElementById('totalCO2').textContent = formatNumber(results.emissions.total_co2_emissions);
    document.getElementById('totalN2O').textContent = formatNumber(results.emissions.total_n2o_emissions);
    document.getElementById('totalCO2eq').textContent = formatNumber(results.emissions.co2_equivalent);
    
    // Uncertainty Analysis
    if (results.uncertainty) {
        displayUncertaintyResults(results.uncertainty);
        document.getElementById('uncertaintyResults').classList.remove('hidden');
    } else {
        document.getElementById('uncertaintyResults').classList.add('hidden');
    }
    
    // Sensitivity Analysis
    if (results.sensitivity) {
        displaySensitivityResults(results.sensitivity);
        document.getElementById('sensitivityResults').classList.remove('hidden');
    } else {
        document.getElementById('sensitivityResults').classList.add('hidden');
    }
}

// Display uncertainty results
function displayUncertaintyResults(uncertainty) {
    const co2eq = uncertainty.CO2_equivalent;
    
    document.getElementById('uncMean').textContent = formatNumber(co2eq.mean);
    document.getElementById('uncStd').textContent = formatNumber(co2eq.std);
    document.getElementById('uncCI').textContent = 
        `${formatNumber(co2eq.ci_lower)} - ${formatNumber(co2eq.ci_upper)}`;
    document.getElementById('uncMedian').textContent = formatNumber(co2eq.percentile_50);
    
    // Create detailed table
    const tbody = document.getElementById('uncertaintyTableBody');
    tbody.innerHTML = '';
    
    const gases = ['CH4', 'CO2', 'N2O', 'CO2_equivalent'];
    const gasNames = {
        'CH4': 'Methane (CH₄)',
        'CO2': 'Carbon Dioxide (CO₂)',
        'N2O': 'Nitrous Oxide (N₂O)',
        'CO2_equivalent': 'CO₂ Equivalent'
    };
    
    gases.forEach(gas => {
        const data = uncertainty[gas];
        const row = `
            <tr>
                <td><strong>${gasNames[gas]}</strong></td>
                <td>${formatNumber(data.mean)}</td>
                <td>${formatNumber(data.std)}</td>
                <td>${formatNumber(data.percentile_50)}</td>
                <td>${formatNumber(data.ci_lower)}</td>
                <td>${formatNumber(data.ci_upper)}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// Display sensitivity results
function displaySensitivityResults(sensitivity) {
    const tbody = document.getElementById('sensitivityTableBody');
    tbody.innerHTML = '';
    
    sensitivity.forEach(item => {
        const row = `
            <tr>
                <td><strong>${item.parameter}</strong></td>
                <td>${item.correlation.toFixed(3)}</td>
                <td>${item.rank_correlation.toFixed(3)}</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${Math.abs(item.rank_correlation) * 100}%"></div>
                    </div>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// Format number with thousands separator
function formatNumber(num) {
    if (num === null || num === undefined) return 'N/A';
    return num.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

// Update climate region when latitude changes
document.getElementById('latitude').addEventListener('blur', async function() {
    const latitude = parseFloat(this.value);
    if (!isNaN(latitude) && latitude >= -90 && latitude <= 90) {
        try {
            const response = await fetch(`${API_BASE}/climate-region/${latitude}`);
            const data = await response.json();
            
            // Show climate region hint
            const hint = document.createElement('div');
            hint.className = 'alert alert-info';
            hint.textContent = `Climate Region: ${data.climate_region}`;
            hint.style.marginTop = '0.5rem';
            
            // Remove previous hint if exists
            const existingHint = this.parentElement.querySelector('.alert');
            if (existingHint) {
                existingHint.remove();
            }
            
            this.parentElement.appendChild(hint);
        } catch (error) {
            console.error('Error fetching climate region:', error);
        }
    }
});

// Toggle analysis options
document.getElementById('runUncertainty').addEventListener('change', function() {
    const iterationsGroup = document.getElementById('iterationsGroup');
    if (this.checked) {
        iterationsGroup.classList.remove('hidden');
    } else {
        iterationsGroup.classList.add('hidden');
    }
});

// Reset form
function resetForm() {
    document.getElementById('analysisForm').reset();
    document.getElementById('resultsContainer').classList.add('hidden');
}

// Export results as JSON
function exportResults() {
    // This would typically export the current results
    alert('Export functionality - Download results as JSON');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Reservoir GHG Emissions Tool initialized');
    
    // Check if uncertainty analysis is checked by default
    const runUncertainty = document.getElementById('runUncertainty');
    if (runUncertainty.checked) {
        document.getElementById('iterationsGroup').classList.remove('hidden');
    }
});
