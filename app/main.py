from fastapi import FastAPI
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

@app.get("/")
def root():
    return {"message": "Fraud Detection API Running"}

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
    return {"status": "healthy"}
