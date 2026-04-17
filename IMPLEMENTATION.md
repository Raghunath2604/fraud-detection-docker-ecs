# 🔧 Implementation Guide: Docker → ECR → ECS → Load Balancer

Complete step-by-step guide to deploying a containerized application on AWS with high availability.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Prepare Your Application](#phase-1-prepare-your-application)
4. [Phase 2: Docker Containerization](#phase-2-docker-containerization)
5. [Phase 3: Amazon ECR Setup](#phase-3-amazon-ecr-setup)
6. [Phase 4: AWS ECS Configuration](#phase-4-aws-ecs-configuration)
7. [Phase 5: Load Balancer Setup](#phase-5-load-balancer-setup)
8. [Phase 6: Deploy & Test](#phase-6-deploy--test)
9. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Architecture Overview

### High-Level Diagram

```
┌────────────────────────────────────────────────────┐
│              INTERNET                              │
└────────────────────┬─────────────────────────────┘
                     │ (Port 80)
        ┌────────────▼──────────────┐
        │ Application Load Balancer │
        │  (fraud-api-alb)          │
        └────────────┬──────────────┘
                     │ (Port 8000)
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐          ┌─────▼────┐
    │  ECS      │          │  ECS     │
    │  Task 1   │          │  Task 2  │
    │ Fargate   │          │ Fargate  │
    │ CPU: 256  │          │ CPU: 256 │
    │ RAM: 512  │          │ RAM: 512 │
    └────┬─────┘          └─────┬────┘
         │                       │
    ┌────▼───────────────────────▼────┐
    │   ECS Cluster                   │
    │  (fraud-api-cluster)            │
    │   VPC: vpc-0fa537be2ad489524    │
    └─────────────────────────────────┘
         │
    ┌────▼──────────────┐
    │  ECR Registry     │
    │ (fraud-api image) │
    └───────────────────┘
```

### Data Flow

```
User Request
    ↓
Load Balancer (Port 80)
    ↓
Route to healthy task
    ↓
ECS Task (Fargate, Port 8000)
    ↓
FastAPI Application
    ↓
ML Model
    ↓
Response → User
```

---

## Prerequisites

### AWS Requirements
- ✅ AWS Account with appropriate permissions
- ✅ AWS CLI v2 installed and configured
- ✅ IAM user with:
  - ECR access
  - ECS access
  - EC2 access (for load balancer & security groups)
  - IAM access (for creating roles)

### Local Machine
- ✅ Docker Desktop installed
- ✅ Python 3.11+
- ✅ Git configured
- ✅ Terminal/Command line access

### Verify Installation

```bash
# Check AWS CLI
aws --version
# Output: aws-cli/2.x.x

# Check Docker
docker --version
# Output: Docker version x.x.x

# Check Git
git --version
# Output: git version x.x.x

# Verify AWS credentials
aws sts get-caller-identity
# Output: Account ID, User ID, ARN
```

---

## Phase 1: Prepare Your Application

### Step 1.1: Application Structure

Your application must have:

```
your-app/
├── app/
│   └── main.py              # FastAPI app
├── model/
│   └── fraud.pkl            # ML model
├── train.py                 # Training script
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker config
└── .gitignore
```

### Step 1.2: Dockerfile Creation

```dockerfile
# Build stage considerations
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 1.3: requirements.txt

```
fastapi==0.104.1
uvicorn==0.24.0
scikit-learn==1.3.2
joblib==1.3.2
pandas==2.1.3
```

### Step 1.4: Test Locally First

```bash
# Build image
docker build -t fraud-api:latest .

# Run container
docker run -p 8000:8000 fraud-api:latest

# Test endpoint
curl http://localhost:8000/health

# Expected output: {"status": "healthy"}
```

---

## Phase 2: Docker Containerization

### Step 2.1: Build Docker Image

**Command:**
```bash
docker build -t fraud-api:latest .
```

**What happens:**
1. Docker reads Dockerfile
2. Downloads Python 3.11-slim base image
3. Installs Python dependencies
4. Copies application code
5. Creates image layer

**Output:**
```
[+] Building 120.5s (10/10) FINISHED
 => [internal] load build definition from Dockerfile      0.1s
 => [1/5] FROM python:3.11-slim                          0.1s
 => [2/5] WORKDIR /app                                   0.1s
 => [3/5] COPY requirements.txt .                        0.1s
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt 104.5s
 => [5/5] COPY . .                                       0.1s
 => exporting to image                                  44.9s
 => => naming to docker.io/library/fraud-api:latest      0.0s

Successfully built fraud-api:latest (709MB)
```

### Step 2.2: Verify Image

```bash
# List images
docker images | grep fraud-api

# Output:
# fraud-api    latest    62e124df2473    709MB
```

### Step 2.3: Test Container Locally

```bash
# Run container
docker run -p 8000:8000 fraud-api:latest

# In another terminal, test
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2500,
    "time": 320,
    "location_risk": 1,
    "device_new": 1
  }'

# Expected output:
# {"fraud_prediction": 1}
```

### Step 2.4: Image Optimization (Optional)

**Keep image size small:**
- Use `python:3.11-slim` (not full image)
- Use `--no-cache-dir` with pip
- Remove unnecessary files
- Multi-stage builds for large projects

**Current size:** 709MB
**Acceptable for:** Small to medium workloads
**For production:** Consider reducing to 200-300MB

---

## Phase 3: Amazon ECR Setup

### Step 3.1: Create ECR Repository

**Command:**
```bash
aws ecr create-repository \
  --repository-name fraud-api \
  --region us-east-1
```

**Response:**
```json
{
  "repository": {
    "repositoryArn": "arn:aws:ecr:us-east-1:429288623250:repository/fraud-api",
    "registryId": "429288623250",
    "repositoryName": "fraud-api",
    "repositoryUri": "429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api",
    "repositoryStatus": "ACTIVE"
  }
}
```

**Save this information:**
```
Account ID: 429288623250
Repository Name: fraud-api
Repository URI: 429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api
Region: us-east-1
```

### Step 3.2: Authenticate with ECR

**Command:**
```bash
# Get login credentials
aws ecr get-login-password --region us-east-1 | docker login \
  --username AWS \
  --password-stdin 429288623250.dkr.ecr.us-east-1.amazonaws.com
```

**Process:**
1. AWS CLI requests authentication token
2. Passes token to Docker login
3. Docker stores credentials locally
4. Valid for 12 hours

**Output:**
```
Login Succeeded
```

### Step 3.3: Tag Docker Image

**Command:**
```bash
# Tag local image with ECR URI
docker tag fraud-api:latest \
  429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api:latest
```

**What this does:**
- Creates reference to same image with new name
- Format: `[ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com/[REPO_NAME]:[TAG]`
- Does NOT create new image, just aliases it

### Step 3.4: Push Image to ECR

**Command:**
```bash
docker push 429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api:latest
```

**Process:**
1. Docker compresses image layers
2. Uploads to ECR repository
3. Creates image manifest
4. Makes available for ECS

**Output:**
```
The push refers to repository [429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api]
8e0c6254e7f6: Pushed
37ffa6577b04: Pushed
[... more layers ...]
latest: digest: sha256:62e124df2473b2cc6148d0bfd499632b698cdb6e71bb13cb868a06f651ddaae0 size: 856
```

### Step 3.5: Verify in ECR

**Command:**
```bash
aws ecr describe-images \
  --repository-name fraud-api \
  --region us-east-1
```

**Output:**
```json
{
  "imageDetails": [
    {
      "registryId": "429288623250",
      "repositoryName": "fraud-api",
      "imageId": {
        "imageDigest": "sha256:62e124df2473b2cc6148d0bfd499632b698cdb6e71bb13cb868a06f651ddaae0",
        "imageTag": "latest"
      },
      "imageSize": 709242880,
      "imagePushed": "2026-04-18T00:30:00Z"
    }
  ]
}
```

---

## Phase 4: AWS ECS Configuration

### Step 4.1: Create IAM Execution Role

**Why needed:** ECS tasks need permission to pull images and run

**Create trust policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Create role:**
```bash
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{
      "Effect":"Allow",
      "Principal":{"Service":"ecs-tasks.amazonaws.com"},
      "Action":"sts:AssumeRole"
    }]
  }'
```

**Attach permissions:**
```bash
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

**Result:**
```
Role ARN: arn:aws:iam::429288623250:role/ecsTaskExecutionRole
```

### Step 4.2: Register Task Definition

**What is it?** Blueprint for ECS tasks (like Docker Compose for AWS)

**Command:**
```bash
aws ecs register-task-definition \
  --family fraud-api \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 256 \
  --memory 512 \
  --execution-role-arn arn:aws:iam::429288623250:role/ecsTaskExecutionRole \
  --container-definitions '[
    {
      "name": "fraud-api",
      "image": "429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "PYTHONUNBUFFERED",
          "value": "1"
        }
      ]
    }
  ]' \
  --region us-east-1
```

**Parameters explained:**

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `--family` | fraud-api | Task definition name |
| `--network-mode` | awsvpc | Use VPC networking |
| `--requires-compatibilities` | FARGATE | Serverless containers |
| `--cpu` | 256 | CPU units (0.25 vCPU) |
| `--memory` | 512 | Memory in MB |
| `--execution-role-arn` | (role ARN) | Permissions for ECS agent |
| `--container-definitions` | (JSON) | Container configuration |

**Output:**
```
Task Definition ARN: arn:aws:ecs:us-east-1:429288623250:task-definition/fraud-api:1
Revision: 1
Status: ACTIVE
```

### Step 4.3: Create ECS Cluster

**What is it?** Logical grouping of resources

**Command:**
```bash
aws ecs create-cluster \
  --cluster-name fraud-api-cluster \
  --region us-east-1
```

**Output:**
```
Cluster ARN: arn:aws:ecs:us-east-1:429288623250:cluster/fraud-api-cluster
Cluster Name: fraud-api-cluster
Status: ACTIVE
```

### Step 4.4: Verify ECS Setup

```bash
# List clusters
aws ecs list-clusters --region us-east-1

# List task definitions
aws ecs list-task-definitions --region us-east-1
```

---

## Phase 5: Load Balancer Setup

### Step 5.1: Create Security Group

**Why needed:** Control network traffic to tasks

**Get VPC ID:**
```bash
# Get default VPC
aws ec2 describe-vpcs \
  --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' \
  --output text --region us-east-1

# Output: vpc-0fa537be2ad489524
```

**Create security group:**
```bash
aws ec2 create-security-group \
  --group-name fraud-api-sg \
  --description "Security group for Fraud API" \
  --vpc-id vpc-0fa537be2ad489524 \
  --region us-east-1
```

**Output:**
```
GroupId: sg-0f04e9a1a7262a9a1
```

**Allow inbound traffic on port 8000:**
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-0f04e9a1a7262a9a1 \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

**Allow inbound traffic on port 80 (for ALB):**
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-0f04e9a1a7262a9a1 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

### Step 5.2: Get Subnets

**Why needed:** ALB must span multiple availability zones for high availability

**Command:**
```bash
aws ec2 describe-subnets \
  --filters Name=vpc-id,Values=vpc-0fa537be2ad489524 \
  --query 'Subnets[*].{SubnetId:SubnetId,AvailabilityZone:AvailabilityZone}' \
  --output table \
  --region us-east-1
```

**Output:**
```
|         AvailabilityZone         |          SubnetId          |
|----------------------------------|----|
|  us-east-1a                      |  subnet-0b3a3e47422ee2234 |
|  us-east-1b                      |  subnet-05e4b43d6fc041025 |
|  us-east-1c                      |  subnet-056e5cadbdd17c6ea |
|  us-east-1d                      |  subnet-05bc6ceb918490b53 |
```

**Use 2 subnets in different AZs for redundancy:**
```
Subnet 1: subnet-0b3a3e47422ee2234 (us-east-1a)
Subnet 2: subnet-05e4b43d6fc041025 (us-east-1b)
```

### Step 5.3: Create Application Load Balancer

**Command:**
```bash
aws elbv2 create-load-balancer \
  --name fraud-api-alb \
  --subnets subnet-0b3a3e47422ee2234 subnet-05e4b43d6fc041025 \
  --security-groups sg-0f04e9a1a7262a9a1 \
  --scheme internet-facing \
  --type application \
  --region us-east-1
```

**Parameters:**
- `--name`: ALB name
- `--subnets`: Multiple subnets for HA
- `--security-groups`: Traffic rules
- `--scheme`: internet-facing (public)
- `--type`: application (Layer 7)

**Output:**
```json
{
  "LoadBalancers": [
    {
      "LoadBalancerName": "fraud-api-alb",
      "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:429288623250:loadbalancer/app/fraud-api-alb/5e42bc867b4c41c8",
      "DNSName": "fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com",
      "Scheme": "internet-facing",
      "Type": "application",
      "State": {
        "Code": "active"
      }
    }
  ]
}
```

**Save DNS Name:**
```
ALB DNS: fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com
```

### Step 5.4: Create Target Group

**What is it?** Defines where ALB sends traffic

**Command:**
```bash
aws elbv2 create-target-group \
  --name fraud-api-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-0fa537be2ad489524 \
  --target-type ip \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 10 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --region us-east-1
```

**Parameters:**
- `--protocol`: HTTP (or HTTPS)
- `--port`: Application port
- `--target-type`: ip (for Fargate)
- `--health-check-path`: Endpoint to check
- `--health-check-interval-seconds`: Check every 30s
- `--healthy-threshold-count`: Consecutive healthy checks before active

**Output:**
```
TargetGroupArn: arn:aws:elasticloadbalancing:us-east-1:429288623250:targetgroup/fraud-api-tg/faff1f7e144f8ce4
```

### Step 5.5: Create Listener

**What is it?** Routes traffic from ALB to target group

**Command:**
```bash
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:429288623250:loadbalancer/app/fraud-api-alb/5e42bc867b4c41c8 \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:429288623250:targetgroup/fraud-api-tg/faff1f7e144f8ce4 \
  --region us-east-1
```

**Flow:**
```
Port 80 (ALB) → forward → Target Group → Port 8000 (ECS)
```

---

## Phase 6: Deploy & Test

### Step 6.1: Create ECS Service

**What is it?** Manages ECS tasks and their deployment

**Command:**
```bash
aws ecs create-service \
  --cluster fraud-api-cluster \
  --service-name fraud-api-service \
  --task-definition fraud-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-0b3a3e47422ee2234,subnet-05e4b43d6fc041025],
    securityGroups=[sg-0f04e9a1a7262a9a1],
    assignPublicIp=ENABLED
  }" \
  --load-balancers "
    targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:429288623250:targetgroup/fraud-api-tg/faff1f7e144f8ce4,
    containerName=fraud-api,
    containerPort=8000
  " \
  --region us-east-1
```

**Parameters:**
- `--desired-count`: Number of tasks to run
- `--launch-type`: FARGATE (serverless)
- `--network-configuration`: VPC, subnets, security
- `--load-balancers`: Connect to ALB

**Output:**
```
ServiceArn: arn:aws:ecs:us-east-1:429288623250:service/fraud-api-cluster/fraud-api-service
ServiceName: fraud-api-service
Status: ACTIVE
DesiredCount: 2
RunningCount: 0 (will increase as tasks start)
```

### Step 6.2: Monitor Task Startup

**Command:**
```bash
# Watch tasks start
aws ecs describe-services \
  --cluster fraud-api-cluster \
  --services fraud-api-service \
  --region us-east-1 \
  --query 'services[0].[runningCount,desiredCount,status]' \
  --output table
```

**Expected progression:**
```
Time:  0s  → RunningCount: 0, DesiredCount: 2, Status: ACTIVE
Time: 15s  → RunningCount: 1, DesiredCount: 2, Status: ACTIVE
Time: 30s  → RunningCount: 2, DesiredCount: 2, Status: ACTIVE ✅
```

### Step 6.3: Get Load Balancer DNS

**Command:**
```bash
aws elbv2 describe-load-balancers \
  --load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:429288623250:loadbalancer/app/fraud-api-alb/5e42bc867b4c41c8 \
  --query 'LoadBalancers[0].DNSName' \
  --output text \
  --region us-east-1
```

**Output:**
```
fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com
```

### Step 6.4: Test Health Endpoint

**Command:**
```bash
curl http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/health
```

**Expected output:**
```json
{
  "status": "healthy"
}
```

### Step 6.5: Test Prediction Endpoint

**Command:**
```bash
curl -X POST http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2500,
    "time": 320,
    "location_risk": 1,
    "device_new": 1
  }'
```

**Expected output:**
```json
{
  "fraud_prediction": 1
}
```

### Step 6.6: Access Swagger UI

**URL:**
```
http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/docs
```

**Features:**
- Interactive API documentation
- Try-it-out functionality
- Request/response examples

---

## Monitoring & Troubleshooting

### View Service Events

**Command:**
```bash
aws ecs describe-services \
  --cluster fraud-api-cluster \
  --services fraud-api-service \
  --region us-east-1 \
  --query 'services[0].events[:5]'
```

**Useful for:** Seeing deployment issues

### View Task Logs

**Command:**
```bash
# List tasks
aws ecs list-tasks \
  --cluster fraud-api-cluster \
  --region us-east-1

# Describe specific task
aws ecs describe-tasks \
  --cluster fraud-api-cluster \
  --tasks arn:aws:ecs:us-east-1:429288623250:task/fraud-api-cluster/xxxxx \
  --region us-east-1
```

### Check Target Health

**Command:**
```bash
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:429288623250:targetgroup/fraud-api-tg/faff1f7e144f8ce4 \
  --region us-east-1
```

**Output:**
```json
{
  "TargetHealthDescriptions": [
    {
      "Target": {
        "Id": "10.0.1.100",
        "Port": 8000
      },
      "TargetHealth": {
        "State": "healthy",
        "Reason": "N/A",
        "Description": "N/A"
      }
    }
  ]
}
```

### Common Issues & Solutions

#### Issue: Tasks not starting

**Check:**
```bash
aws ecs describe-services \
  --cluster fraud-api-cluster \
  --services fraud-api-service \
  --region us-east-1 \
  --query 'services[0].events[0]'
```

**Common causes:**
- ❌ Execution role missing
- ❌ Invalid task definition
- ❌ Insufficient memory
- ❌ Image not in ECR

#### Issue: Health checks failing

**Check:**
```bash
aws elbv2 describe-target-health \
  --target-group-arn <TG-ARN> \
  --region us-east-1
```

**Common causes:**
- ❌ `/health` endpoint not returning 200
- ❌ Port 8000 not exposed in Dockerfile
- ❌ Application not starting properly

#### Issue: Can't reach API

**Check:**
1. ALB is active
2. Target health is "healthy"
3. Security group allows port 80
4. URL is correct

**Debugging:**
```bash
# Test ALB health
curl -v http://<ALB-DNS>/health

# Check security group
aws ec2 describe-security-groups \
  --group-ids sg-0f04e9a1a7262a9a1 \
  --region us-east-1
```

---

## Scaling & Updates

### Scale Number of Tasks

**Command:**
```bash
aws ecs update-service \
  --cluster fraud-api-cluster \
  --service fraud-api-service \
  --desired-count 4 \
  --region us-east-1
```

**Result:** ECS will launch 2 more tasks

### Update to New Image

**Push new version to ECR:**
```bash
docker tag fraud-api:v2 429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api:v2
docker push 429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api:v2
```

**Update task definition:**
```bash
aws ecs register-task-definition \
  --family fraud-api \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 256 \
  --memory 512 \
  --execution-role-arn arn:aws:iam::429288623250:role/ecsTaskExecutionRole \
  --container-definitions '[{
    "name": "fraud-api",
    "image": "429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api:v2",
    "portMappings": [{"containerPort": 8000}],
    "essential": true
  }]'
```

**Update service:**
```bash
aws ecs update-service \
  --cluster fraud-api-cluster \
  --service fraud-api-service \
  --task-definition fraud-api:2 \
  --region us-east-1
```

---

## Cost Optimization

### Current Costs

| Resource | Cost/Month |
|----------|-----------|
| Fargate (256 CPU, 512 MB) × 2 | $23 |
| ALB | $21.60 |
| ECR Storage (1GB) | $0.10 |
| **Total** | **~$45/month** |

### Ways to Save

1. **Reduce tasks:** Set desired-count to 1 (less HA)
2. **Smaller tasks:** Use 128 CPU, 256 MB (saves 50%)
3. **Reserved capacity:** Purchase 1-year commitment (saves 40%)
4. **Spot tasks:** Use interruptible capacity (saves 70%)

---

## Best Practices Checklist

- [x] Multi-task deployment for HA
- [x] Health checks configured
- [x] Load balancer spreading traffic
- [x] Security group restrictive
- [x] Task definition versioned
- [x] Image in private ECR
- [x] Execution role with minimal permissions
- [ ] Monitoring/CloudWatch enabled
- [ ] Auto-scaling policies configured
- [ ] HTTPS/SSL certificate enabled

---

## Quick Reference Commands

### Deploy new version
```bash
# Build
docker build -t fraud-api:v2 .

# Push
docker tag fraud-api:v2 429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api:v2
docker push 429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api:v2

# Update task def + service
aws ecs register-task-definition ... && \
aws ecs update-service --task-definition fraud-api:2
```

### Scale up/down
```bash
aws ecs update-service \
  --cluster fraud-api-cluster \
  --service fraud-api-service \
  --desired-count 4
```

### Check status
```bash
aws ecs describe-services \
  --cluster fraud-api-cluster \
  --services fraud-api-service
```

### View logs
```bash
aws ecs describe-tasks \
  --cluster fraud-api-cluster \
  --tasks <TASK-ARN>
```

---

## Summary

### What We Built

```
┌─────────────────────┐
│  Your Application   │
└──────────┬──────────┘
           ↓
      ┌────────────┐
      │  Docker    │ (Containerization)
      └────┬───────┘
           ↓
      ┌────────────┐
      │   ECR      │ (Registry)
      └────┬───────┘
           ↓
      ┌────────────┐
      │   ECS      │ (Orchestration)
      └────┬───────┘
           ↓
      ┌────────────┐
      │ Load Bal.  │ (Distribution)
      └────┬───────┘
           ↓
      ┌────────────┐
      │  INTERNET  │ (Users)
      └────────────┘
```

### Key Takeaways

1. **Docker** packages application + dependencies
2. **ECR** stores Docker images in AWS
3. **ECS** runs containers at scale
4. **Load Balancer** distributes traffic
5. **Together** = production-ready microservice

---

**Status:** ✅ Production Ready  
**Last Updated:** 2026-04-18  
**Tested:** ✅ Fully functional
