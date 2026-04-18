from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import joblib
import os

app = FastAPI(title="Fraud Detection API")

model_path = os.path.join(os.path.dirname(__file__), "..", "model", "fraud.pkl")
model = joblib.load(model_path)

class Transaction(BaseModel):
    amount: float
    time: float
    location_risk: float
    device_new: float

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fraud Detection API</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 500px;
                width: 100%;
                padding: 40px;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                text-align: center;
                font-size: 28px;
            }
            .subtitle {
                color: #666;
                text-align: center;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
                font-size: 14px;
            }
            input, select {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            input:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            .help-text {
                font-size: 12px;
                color: #999;
                margin-top: 5px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
                margin-top: 10px;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            .result {
                margin-top: 30px;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                display: none;
                font-weight: 600;
            }
            .result.fraud {
                background-color: #fee;
                color: #c33;
                border: 2px solid #c33;
            }
            .result.legitimate {
                background-color: #efe;
                color: #3c3;
                border: 2px solid #3c3;
            }
            .result h2 {
                font-size: 20px;
                margin-bottom: 10px;
            }
            .result p {
                font-size: 14px;
            }
            .error {
                background-color: #fee;
                color: #c33;
                padding: 12px;
                border-radius: 8px;
                margin-top: 20px;
                display: none;
            }
            .loading {
                display: none;
                text-align: center;
                margin-top: 20px;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #999;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Fraud Detection</h1>
            <p class="subtitle">Check if a transaction is fraudulent</p>

            <form id="fraudForm">
                <div class="form-group">
                    <label for="amount">Transaction Amount ($)</label>
                    <input type="number" id="amount" name="amount" step="0.01" min="0" placeholder="e.g., 2500" required>
                    <p class="help-text">Amount of the transaction in dollars</p>
                </div>

                <div class="form-group">
                    <label for="time">Transaction Time (Hour)</label>
                    <input type="number" id="time" name="time" min="0" max="23" placeholder="e.g., 14" required>
                    <p class="help-text">Hour of day (0-23)</p>
                </div>

                <div class="form-group">
                    <label for="location_risk">Location Risk</label>
                    <select id="location_risk" name="location_risk" required>
                        <option value="">-- Select Risk Level --</option>
                        <option value="0">Low Risk (0)</option>
                        <option value="0.5">Medium Risk (0.5)</option>
                        <option value="1">High Risk (1)</option>
                    </select>
                    <p class="help-text">Risk level based on location</p>
                </div>

                <div class="form-group">
                    <label for="device_new">Device Status</label>
                    <select id="device_new" name="device_new" required>
                        <option value="">-- Select --</option>
                        <option value="0">Known Device (0)</option>
                        <option value="1">New Device (1)</option>
                    </select>
                    <p class="help-text">Is this a new or known device?</p>
                </div>

                <button type="submit">Check for Fraud</button>
            </form>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 10px; color: #999;">Analyzing transaction...</p>
            </div>

            <div class="error" id="error"></div>

            <div class="result" id="result">
                <h2 id="resultTitle"></h2>
                <p id="resultMessage"></p>
            </div>

            <div class="footer">
                <p>92.7% accuracy • Powered by Machine Learning</p>
            </div>
        </div>

        <script>
            document.getElementById('fraudForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const amount = parseFloat(document.getElementById('amount').value);
                const time = parseFloat(document.getElementById('time').value);
                const location_risk = parseFloat(document.getElementById('location_risk').value);
                const device_new = parseFloat(document.getElementById('device_new').value);

                document.getElementById('loading').style.display = 'block';
                document.getElementById('error').style.display = 'none';
                document.getElementById('result').style.display = 'none';

                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            amount: amount,
                            time: time,
                            location_risk: location_risk,
                            device_new: device_new
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Request failed');
                    }

                    const data = await response.json();
                    const prediction = data.fraud_prediction;

                    document.getElementById('loading').style.display = 'none';

                    const resultEl = document.getElementById('result');
                    const titleEl = document.getElementById('resultTitle');
                    const messageEl = document.getElementById('resultMessage');

                    if (prediction === 1) {
                        resultEl.classList.remove('legitimate');
                        resultEl.classList.add('fraud');
                        titleEl.textContent = '⚠️ FRAUD DETECTED';
                        messageEl.textContent = 'This transaction is likely fraudulent. Please review immediately.';
                    } else {
                        resultEl.classList.remove('fraud');
                        resultEl.classList.add('legitimate');
                        titleEl.textContent = '✅ LEGITIMATE TRANSACTION';
                        messageEl.textContent = 'This transaction appears to be legitimate.';
                    }

                    resultEl.style.display = 'block';

                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').textContent = 'Error: Unable to analyze transaction. Please try again.';
                    console.error('Error:', error);
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/predict")
def predict(data: Transaction):
    features = [[
        data.amount,
        data.time,
        data.location_risk,
        data.device_new
    ]]

    pred = model.predict(features)[0]

    return {"fraud_prediction": int(pred)}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.1-cicd-fixed"}
