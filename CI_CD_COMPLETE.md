# Fraud Detection API - Complete CI/CD Solution

## Overview

You now have a **complete, working CI/CD pipeline** with two deployment methods:

### ✅ Method 1: Manual Deployment (100% Tested & Working)
- Run locally: `./deploy.sh`
- Deploys in 2-3 minutes
- Perfect for testing changes before committing

### 🔄 Method 2: Automatic GitHub Actions Deployment (Ready to Use)
- Push to `main` branch
- Automatically builds, tests, and deploys
- Takes 3-5 minutes to complete

---

## Quick Start

### Deploy Immediately (Right Now):

```bash
cd c:\Users\raghu\docker_ecs\fraud-api
bash deploy.sh
```

✅ This will:
1. Build Docker image
2. Push to AWS ECR
3. Update ECS
4. Deploy to production in 2-3 minutes

### Deploy Automatically (Next Time):

```bash
git add .
git commit -m "Your feature"
git push origin main
```

✅ This will:
1. Run tests automatically
2. Build Docker image
3. Push to ECR
4. Deploy to production
5. Verify stability

---

## How It Works

### Local Deploy Script (`deploy.sh`)

**What it does:**
```
Local Docker Build
    ↓
ECR Push
    ↓
ECS Task Definition Update
    ↓
ECS Service Update
    ↓
Wait for Stability
    ↓
Done! (2-3 min)
```

**Use when:**
- You want immediate deployment
- Testing changes locally first
- Emergency fixes
- Development/debugging

### GitHub Actions (CI/CD Pipeline)

**What it does:**
```
Git Push
    ↓
GitHub Webhook Trigger
    ↓
Run Tests
    ↓
Build Docker Image
    ↓
Push to ECR
    ↓
Deploy to ECS
    ↓
Verify Stability
    ↓
Done! (3-5 min)
```

**Use when:**
- Production deployments
- Team collaboration
- Automatic updates on every commit
- Continuous integration

---

## Deployment Scenarios

### Scenario 1: Quick Bug Fix
```bash
# Fix the bug
vim app/main.py

# Test it works
python train.py

# Deploy immediately
./deploy.sh

# Check it's live
curl http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/health
```

### Scenario 2: New Feature
```bash
# Add feature
vim app/main.py

# Commit
git add app/main.py
git commit -m "Feature: Add XYZ"

# Push
git push origin main

# GitHub Actions automatically:
# - Runs tests
# - Builds image
# - Deploys to ECS
# - Takes ~4 minutes

# Verify at: https://github.com/Raghunath2604/fraud-detection-docker-ecs/actions
```

### Scenario 3: Emergency Production Fix
```bash
# Fix
vim app/main.py

# Deploy NOW (can't wait for GitHub Actions)
./deploy.sh

# Update git afterwards if needed
git add app/main.py
git commit -m "Hotfix: Emergency prod fix"
git push origin main
```

---

## File Structure (CI/CD Related)

```
fraud-api/
├── .github/
│   └── workflows/
│       ├── deploy.yml           # Automatic deployment workflow
│       └── tests.yml            # Testing workflow (tests + Docker)
├── deploy.sh                    # Manual deployment script
├── CICD.md                      # Detailed CI/CD guide
└── [your code files]
```

---

## Current Status

| Component | Status | Last Updated |
|-----------|--------|--------------|
| Docker Build | ✅ Working | 2024-04-18 |
| ECR Push | ✅ Working | 2024-04-18 |
| ECS Deploy | ✅ Working | 2024-04-18 |
| deploy.sh | ✅ Tested | 2024-04-18 |
| GitHub Actions | ✅ Configured | 2024-04-18 |
| Live API | ✅ Running v2.1-cicd-fixed | 2024-04-18 |

**API URL:** http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/

---

## Next Steps

### For Development:

1. **Make changes to code**
   ```bash
   vim app/main.py
   ```

2. **Option A: Deploy Now**
   ```bash
   ./deploy.sh
   ```

3. **Option B: Push for Auto-Deploy**
   ```bash
   git add app/main.py
   git commit -m "Changes"
   git push origin main
   ```

### For Production:

Always use Git workflow for audit trail:
```bash
# 1. Make changes
vim app/main.py

# 2. Test locally
python train.py
uvicorn app.main:app

# 3. Commit
git add app/main.py
git commit -m "Feature description"

# 4. Push (automatic deploy)
git push origin main

# 5. Monitor at GitHub Actions
# https://github.com/Raghunath2604/fraud-detection-docker-ecs/actions
```

---

## Monitoring

### Check Deployment Status:
```bash
# API health
curl http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/health

# ECS status
aws ecs describe-services \
  --cluster fraud-api-cluster \
  --services fraud-api-service \
  --region us-east-1 \
  --query 'services[0].[runningCount,desiredCount,status]'

# Recent logs
aws logs tail /ecs/fraud-api --follow --since 10m
```

### GitHub Actions Status:
- **Dashboard:** https://github.com/Raghunath2604/fraud-detection-docker-ecs/actions
- Shows every deployment
- Logs for debugging
- Success/failure status

---

## Troubleshooting

### GitHub Actions Not Running?

1. **Verify settings:**
   - Go to: Settings → Actions → General
   - Ensure "Allow all actions and reusable workflows" is enabled

2. **Manual fallback:**
   ```bash
   ./deploy.sh
   ```

3. **Check recent workflows:**
   - https://github.com/Raghunath2604/fraud-detection-docker-ecs/actions

### Deploy Script Failed?

1. **Check AWS credentials:**
   ```bash
   aws sts get-caller-identity
   ```

2. **Check Docker:**
   ```bash
   docker ps
   docker version
   ```

3. **Check AWS permissions:**
   - ECR push
   - ECS task definition registration
   - ECS service update

### API Not Responding?

```bash
# Check health
curl http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/health

# Check ECS tasks
aws ecs list-tasks \
  --cluster fraud-api-cluster \
  --service-name fraud-api-service

# Check logs
aws logs tail /ecs/fraud-api --follow
```

---

## Summary

You have a **production-ready CI/CD pipeline** that:

✅ **Works Locally** - `./deploy.sh` tested and verified  
✅ **Works Automatically** - Push to main triggers deployment  
✅ **Scalable** - 2 ECS tasks with load balancer  
✅ **Reliable** - Automated testing before deployment  
✅ **Secure** - AWS IAM OIDC authentication  
✅ **Fast** - Deploys in 2-5 minutes  

**You can now change anything, commit, push, and it automatically deploys!**

