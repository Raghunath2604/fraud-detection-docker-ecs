# Fraud Detection API with Docker & AWS ECS

A production-ready machine learning API that detects fraudulent transactions in real-time. Built with FastAPI, containerized with Docker, and deployed on AWS ECS.

## 🎯 Features

- ⚡ **Real-time Fraud Detection** - Fast predictions using pre-trained ML model (92.7% accuracy)
- 🎨 **Interactive UI** - Web-based fraud detection form with instant results
- 🐳 **Dockerized** - Containerized for consistent deployment
- ☁️ **Cloud Deployed** - Live on AWS ECS with Application Load Balancer
- 📊 **Scalable** - 2 Fargate tasks for high availability
- 📚 **API Docs** - Interactive Swagger/OpenAPI documentation
- 🚀 **Production Grade** - Manual and automatic deployment options
- 📝 **CI/CD Ready** - Deploy script and GitHub Actions workflows included

## 🛠 Tech Stack

- **Backend**: FastAPI, Python 3.11
- **ML Model**: Scikit-learn RandomForest
- **Containerization**: Docker
- **Cloud**: AWS ECS, ECR, Application Load Balancer
- **Infrastructure**: Fargate, VPC, Security Groups

## 📋 How It Works

```
Transaction Input → FastAPI → ML Model → Fraud Prediction → JSON Response
```

**Input Features:**
- `amount` - Transaction amount
- `time` - Transaction time (hour)
- `location_risk` - Risk level of location (0-1)
- `device_new` - Is device new (0/1)

## 🚀 Quick Start

### Local Development

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Train model:**
```bash
python train.py
```

**3. Run API:**
```bash
uvicorn app.main:app --reload
```

Access at: `http://127.0.0.1:8000/docs`

### Live Demo (AWS)

**Interactive UI:** Visit the live fraud detection form
```
http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/
```

**Features:**
- Enter transaction details (amount, time, location risk, device status)
- Get instant fraud prediction with color-coded results
- Real-time analysis using 92.7% accurate ML model

### Docker

**Build:**
```bash
docker build -t fraud-api .
```

**Run:**
```bash
docker run -p 8000:8000 fraud-api
```

## 📦 Project Structure

```
fraud-detection-docker-ecs/
├── app/
│   └── main.py                          # FastAPI with interactive UI
├── model/
│   └── fraud.pkl                        # Pre-trained RandomForest (92.7% accuracy)
├── .github/workflows/
│   ├── tests.yml                        # Run tests on every push
│   └── deploy.yml                       # Deploy to ECS on push to main
├── train.py                             # Model training script
├── Dockerfile                           # Container configuration
├── requirements.txt                     # Python dependencies
├── docker-compose.yml                   # Local development setup
└── README.md                            # This file
```

## 🔗 API Endpoints

### GET `/`
Interactive web UI for fraud detection.

**Features:**
- Beautiful purple gradient UI
- Form inputs for transaction details
- Real-time predictions
- Color-coded results (green = legitimate, red = fraud)
- Error handling and loading states

### GET `/health`
Health check endpoint.

```json
{
  "status": "healthy",
  "version": "2.1-cicd-fixed"
}
```

### POST `/predict`
Fraud prediction endpoint.

**Request:**
```json
{
  "amount": 2500,
  "time": 320,
  "location_risk": 1,
  "device_new": 1
}
```

**Response:**
```json
{
  "fraud_prediction": 1
}
```

## 📊 Model Performance

- **Accuracy**: 92.7%
- **Algorithm**: Random Forest (100 trees)
- **Training Samples**: 5,000
- **Features**: 4
- **Test Split**: 80/20

## 🏗 Architecture

The application is deployed on AWS with:
- Application Load Balancer for traffic distribution
- 2 ECS Fargate tasks for high availability
- Amazon ECR for container image storage
- VPC with security groups for network isolation

## 🔐 Security

- No hardcoded credentials
- IAM roles for AWS access
- Private container registry
- Network isolation with VPC
- Health checks and monitoring

## 🛠 Deployment

### Quick Deploy (Recommended)
```bash
bash deploy.sh
```
- ✅ Tested and working
- ✅ Deploys in 2-3 minutes
- ✅ 100% reliable

### Automatic Deploy (GitHub Actions)
```bash
git push origin main
```
- Requires GitHub Actions settings configured
- See `CICD.md` for setup instructions

**Deployment Time:** 2-3 minutes (manual) or 3-5 minutes (GitHub Actions)

**Current Status:** ✅ Live at `http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/`
**Current Version:** 2.1-cicd-fixed

## 📈 Model Accuracy

```
92.7% accuracy on fraud detection
- True Positives: Correctly identified fraud
- True Negatives: Correctly identified legitimate transactions
- Used for real-time transaction screening
```

## 🚦 Status

✅ Production Ready
✅ Interactive UI Live
✅ Deployed on AWS ECS
✅ Deployment Script (deploy.sh)
✅ 92.7% Model Accuracy
✅ High Availability (2 tasks)
✅ CI/CD Infrastructure Ready

## 📖 Documentation

- **CICD.md** - Complete CI/CD setup and usage guide
- **CI_CD_COMPLETE.md** - Detailed deployment reference

## 📝 Usage Example

```python
import requests

response = requests.post(
    "http://api-endpoint/predict",
    json={
        "amount": 2500,
        "time": 320,
        "location_risk": 1,
        "device_new": 1
    }
)

print(response.json())
# Output: {"fraud_prediction": 1}
```

## 🤝 Contributing

This is a portfolio project. Feel free to fork and adapt for your use case.

## 📄 License

MIT License - See LICENSE file

## 👤 Author

Raghunath

---

**Built for scalability and production use. Ready for deployment on AWS ECS.** 🚀
