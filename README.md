# 🔐 Fraud Detection API with Docker + AWS ECS

A **production-ready** machine learning API that detects fraudulent transactions in real time. Built with FastAPI, containerized with Docker, and deployed on AWS ECS for **scalable cloud inference**.

## ✨ Features

- ⚡ **Real-time Fraud Detection** - Predict fraud status instantly
- 🐳 **Dockerized Deployment** - Consistent environment across all stages
- ☁️ **AWS ECS Hosting** - Scalable, managed container orchestration
- 📊 **Swagger API Docs** - Interactive API documentation
- 📈 **Load Balanced** - Application Load Balancer for high availability
- 🚀 **Production Ready** - Fargate tasks with auto-restart

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **API Framework** | FastAPI |
| **ML Model** | Scikit-learn RandomForest |
| **Containerization** | Docker |
| **Cloud Platform** | AWS ECS (Fargate) |
| **Container Registry** | Amazon ECR |
| **Load Balancing** | Application Load Balancer |
| **Language** | Python 3.11 |

## 📋 How It Works

```
Transaction Input 
    ↓
FastAPI Endpoint (/predict)
    ↓
Pre-trained ML Model
    ↓
Fraud / Not Fraud Prediction
    ↓
JSON Response
```

**Input Features:**
- `amount` - Transaction amount
- `time` - Transaction time (hour)
- `location_risk` - Risk level of location (0-1)
- `device_new` - Is device new (0/1)

## 🎯 Live Demo

**API is now live on AWS!**

- 🌐 **API Endpoint:** http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com
- 📚 **Swagger UI:** http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/docs
- 🏥 **Health Check:** http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/health

### Test the API

```bash
# Health check
curl http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/health

# Make a prediction
curl -X POST http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2500,
    "time": 320,
    "location_risk": 1,
    "device_new": 1
  }'

# Expected Response
{
  "fraud_prediction": 1  # 1 = Fraud, 0 = Legitimate
}
```

## 📁 Project Structure

```
fraud-detection-docker-ecs/
│
├── app/
│   └── main.py                 # FastAPI application
│
├── model/
│   └── fraud.pkl              # Pre-trained RandomForest model (92.7% accuracy)
│
├── train.py                    # Model training script
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                 # Git ignore rules
└── screenshots/               # Proof of deployment
    ├── swagger-ui.png
    ├── ecs-deployment.png
    └── api-response.png
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Desktop
- AWS Account (for ECS deployment)

### Run Locally

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Train the model (one-time):**
```bash
python train.py
```
Output: `Model accuracy: 0.9270`

**3. Start the API:**
```bash
uvicorn app.main:app --reload
```

**4. Access the API:**
- API Docs: http://127.0.0.1:8000/docs
- Prediction: `http://127.0.0.1:8000/predict`

### Run with Docker

**Build the image:**
```bash
docker build -t fraud-api:latest .
```

**Run the container:**
```bash
docker run -p 8000:8000 fraud-api:latest
```

**Test it:**
```bash
curl http://localhost:8000/health
```

## ☁️ AWS ECS Deployment

### Infrastructure Stack

```
┌─────────────────────────────────────────┐
│     Application Load Balancer           │
│  (fraud-api-alb-1872682528)            │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
  ┌───▼───┐     ┌───▼───┐
  │ Task 1│     │ Task 2│
  │Fargate│     │Fargate│
  └───────┘     └───────┘
      │             │
      └──────┬──────┘
             │
       ┌─────▼─────┐
       │  ECS      │
       │ Cluster   │
       └───────────┘
```

### Deployment Steps

**1. Push to ECR:**
```bash
aws ecr create-repository --repository-name fraud-api --region us-east-1
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
docker tag fraud-api:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fraud-api:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fraud-api:latest
```

**2. Register Task Definition:**
```bash
aws ecs register-task-definition \
  --family fraud-api \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 256 --memory 512 \
  --execution-role-arn arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole \
  --container-definitions '[{"name":"fraud-api","image":"<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fraud-api:latest","portMappings":[{"containerPort":8000}],"essential":true}]'
```

**3. Create Service:**
```bash
aws ecs create-service \
  --cluster fraud-api-cluster \
  --service-name fraud-api-service \
  --task-definition fraud-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=fraud-api,containerPort=8000"
```

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| **Accuracy** | 92.7% |
| **Training Samples** | 5,000 |
| **Features** | 4 |
| **Algorithm** | Random Forest (100 trees) |
| **Test Split** | 20% |

## 🔗 API Endpoints

### GET `/`
Returns API status.

```json
{
  "message": "Fraud Detection API Running"
}
```

### GET `/health`
Health check endpoint.

```json
{
  "status": "healthy"
}
```

### POST `/predict`
Predict if transaction is fraudulent.

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

## 🐳 Docker Info

- **Base Image:** `python:3.11-slim`
- **Image Size:** ~709MB
- **Port:** 8000
- **Entry Point:** Uvicorn server

## 📸 Screenshots

### 1. Swagger API Documentation
![Swagger UI](screenshots/swagger-ui.png)

### 2. ECS Deployment
![ECS Service](screenshots/ecs-deployment.png)

### 3. Live Prediction
![API Response](screenshots/api-response.png)

## 💡 Resume Impact

✅ **Deployed scalable ML inference API using Docker & AWS ECS**
✅ **Built production-ready FastAPI with Swagger documentation**
✅ **Containerized application with 92.7% accuracy fraud detection model**
✅ **Configured AWS infrastructure (ECR, ECS, Load Balancer, IAM roles)**
✅ **Implemented auto-scaling with Fargate tasks**

## 🛡️ Production Features

- ✅ Load-balanced traffic distribution
- ✅ Auto-restart on task failure
- ✅ AWS-managed infrastructure
- ✅ Scalable Fargate containers
- ✅ ECR image registry
- ✅ Health checks
- ✅ Swagger API docs

## 📚 Learning Outcomes

This project demonstrates:
- **Machine Learning** - Training & deploying ML models
- **DevOps** - Docker containerization
- **Cloud** - AWS ECS, ECR, load balancing
- **API Design** - FastAPI best practices
- **Scalability** - Containerized microservices
- **Cloud Architecture** - Production deployment patterns

## 🔧 Configuration

### Environment Variables
Add to `.env` if needed:
```
MODEL_PATH=model/fraud.pkl
API_PORT=8000
```

### Requirements
- Python 3.11+
- 512MB RAM (ECS task)
- Docker 20.10+
- AWS CLI v2

## 🐛 Troubleshooting

**Model not found error:**
```bash
python train.py  # Generate the model
```

**Port already in use:**
```bash
docker run -p 8001:8000 fraud-api:latest
```

**ECS task failing:**
```bash
aws ecs describe-services --cluster fraud-api-cluster --services fraud-api-service
```

## 📖 Next Steps

- [ ] Add authentication (API key)
- [ ] Implement rate limiting
- [ ] Add CloudWatch monitoring
- [ ] Setup CI/CD with GitHub Actions
- [ ] Add unit tests
- [ ] Enable HTTPS with ACM

## 👨‍💻 Author

**Raghunath**
- Portfolio: [Your Portfolio URL]
- LinkedIn: [Your LinkedIn URL]
- GitHub: [Your GitHub URL]

## 📄 License

This project is open source and available under the MIT License.

---

**Made with ❤️ | Deployed on AWS ECS | Built for Scale**
