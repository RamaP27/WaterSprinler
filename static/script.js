// API Base URL
const API_BASE = window.location.origin;

// State
let featureColumns = [];
let modelLoaded = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await checkModelStatus();
    await loadFeatures();
    
    // Setup form handlers
    document.getElementById('prediction-form').addEventListener('submit', handlePrediction);
    document.getElementById('training-form').addEventListener('submit', handleTraining);
});

// Check model status
async function checkModelStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();
        
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        
        if (data.model_loaded) {
            statusIndicator.className = 'status-indicator ready';
            statusText.textContent = '✓ Model loaded and ready';
            modelLoaded = true;
        } else {
            statusIndicator.className = 'status-indicator error';
            statusText.textContent = '✗ Model not loaded. Please train a model first.';
            modelLoaded = false;
        }
    } catch (error) {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        statusIndicator.className = 'status-indicator error';
        statusText.textContent = '✗ Error checking model status';
        console.error('Error checking model status:', error);
    }
}

// Load feature columns
async function loadFeatures() {
    try {
        const response = await fetch(`${API_BASE}/api/features`);
        const data = await response.json();
        
        if (data.features && data.features.length > 0) {
            featureColumns = data.features;
            renderFeatureInputs();
        } else {
            const container = document.getElementById('features-container');
            container.innerHTML = '<p class="info-text">No features available. Please train a model first.</p>';
        }
    } catch (error) {
        console.error('Error loading features:', error);
        const container = document.getElementById('features-container');
        container.innerHTML = '<p class="info-text error">Error loading features. Please refresh the page.</p>';
    }
}

// Render feature input fields
function renderFeatureInputs() {
    const container = document.getElementById('features-container');
    container.innerHTML = '';
    
    featureColumns.forEach((feature, index) => {
        const div = document.createElement('div');
        div.className = 'form-group';
        div.innerHTML = `
            <label for="feature-${index}">${feature}:</label>
            <input type="number" 
                   id="feature-${index}" 
                   name="${feature}" 
                   step="any" 
                   required 
                   placeholder="Enter ${feature}">
        `;
        container.appendChild(div);
    });
}

// Handle prediction form submission
async function handlePrediction(e) {
    e.preventDefault();
    
    if (!modelLoaded) {
        showResult('prediction-result', 'error', 'Model not loaded. Please train a model first.');
        return;
    }
    
    const predictBtn = document.getElementById('predict-btn');
    const originalText = predictBtn.textContent;
    predictBtn.disabled = true;
    predictBtn.innerHTML = '<span class="loading-spinner"></span>Predicting...';
    
    try {
        const features = featureColumns.map(feature => {
            const input = document.querySelector(`input[name="${feature}"]`);
            return parseFloat(input.value);
        });
        
        const response = await fetch(`${API_BASE}/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ features })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            const probability = (data.probability * 100).toFixed(2);
            const confidence = (data.confidence * 100).toFixed(2);
            const statusClass = data.status.toLowerCase().includes('on') ? 'on' : 'off';
            
            showResult('prediction-result', 'success', `
                <div class="prediction-details">
                    <h3>Prediction Result</h3>
                    <p><strong>Status:</strong> <span class="status-badge ${statusClass}">${data.status}</span></p>
                    <p><strong>Probability:</strong> ${probability}%</p>
                    <p><strong>Confidence:</strong> ${confidence}%</p>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${probability}%">${probability}%</div>
                    </div>
                </div>
            `);
        } else {
            showResult('prediction-result', 'error', data.error || 'Prediction failed');
        }
    } catch (error) {
        showResult('prediction-result', 'error', `Error: ${error.message}`);
    } finally {
        predictBtn.disabled = false;
        predictBtn.textContent = originalText;
    }
}

// Handle training form submission
async function handleTraining(e) {
    e.preventDefault();
    
    const trainBtn = document.getElementById('train-btn');
    const originalText = trainBtn.textContent;
    trainBtn.disabled = true;
    trainBtn.innerHTML = '<span class="loading-spinner"></span>Training...';
    
    const resultDiv = document.getElementById('training-result');
    resultDiv.className = 'result-card info';
    resultDiv.innerHTML = '<p>Training model... This may take several minutes. Please wait.</p>';
    resultDiv.classList.remove('hidden');
    
    try {
        const formData = new FormData();
        const fileInput = document.getElementById('csv-file');
        const epochs = document.getElementById('epochs').value;
        const batchSize = document.getElementById('batch-size').value;
        
        formData.append('file', fileInput.files[0]);
        formData.append('epochs', epochs);
        formData.append('batch_size', batchSize);
        
        const response = await fetch(`${API_BASE}/api/train`, {
            method: 'POST',
            body: formData
        });
        
        // Check if response is JSON before parsing
        let data;
        const contentType = response.headers.get("content-type") || "";
        
        if (contentType.includes("application/json")) {
            try {
                data = await response.json();
            } catch (parseError) {
                // If JSON parsing fails, try to get text
                const text = await response.clone().text();
                throw new Error(`Failed to parse JSON response (${response.status}): ${text.substring(0, 200)}`);
            }
        } else {
            // If not JSON, read as text to get error message
            const text = await response.text();
            let errorMsg = `Server returned non-JSON response (${response.status})`;
            if (text.includes("Service Unavailable") || response.status === 503) {
                errorMsg = "Training request timed out. The training process takes too long. Please try with fewer epochs or a smaller dataset.";
            } else if (text.length > 0) {
                errorMsg += `: ${text.substring(0, 200)}`;
            }
            throw new Error(errorMsg);
        }
        
        if (response.ok && data.success) {
            showResult('training-result', 'success', `
                <div class="prediction-details">
                    <h3>Training Complete!</h3>
                    <p><strong>Accuracy:</strong> ${(data.accuracy * 100).toFixed(2)}%</p>
                    <p><strong>Precision:</strong> ${(data.precision * 100).toFixed(2)}%</p>
                    <p><strong>Recall:</strong> ${(data.recall * 100).toFixed(2)}%</p>
                    <p><strong>AUC Score:</strong> ${data.auc.toFixed(4)}</p>
                    <p><strong>Features:</strong> ${data.feature_columns.join(', ')}</p>
                </div>
            `);
            
            // Reload model status and features
            await checkModelStatus();
            await loadFeatures();
        } else {
            showResult('training-result', 'error', data.error || 'Training failed');
        }
    } catch (error) {
        showResult('training-result', 'error', `Error: ${error.message}`);
    } finally {
        trainBtn.disabled = false;
        trainBtn.textContent = originalText;
    }
}

// Show result message
function showResult(elementId, type, message) {
    const resultDiv = document.getElementById(elementId);
    resultDiv.className = `result-card ${type}`;
    resultDiv.innerHTML = message;
    resultDiv.classList.remove('hidden');
}

