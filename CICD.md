# CI/CD Setup Guide

## Two CI/CD Methods Available

### ✅ Method 1: Manual Deployment (Tested & Working)

**Use this for immediate, reliable deployments:**

```bash
chmod +x deploy.sh
./deploy.sh
```

This script:
- Builds Docker image locally
- Pushes to AWS ECR
- Updates ECS task definition
- Deploys to ECS Fargate
- Waits for stability
- Typical time: 2-3 minutes

**Great for:**
- Quick fixes
- Testing changes locally before committing
- Guaranteed reliability

---

### 🔄 Method 2: GitHub Actions Automation (Recommended for Production)

**Push to `main` branch → Automatic deployment to AWS**

#### Setup Required (One-time):

1. **GitHub Secrets** (already configured)
   - `AWS_ROLE_ARN` - Your AWS IAM role ARN
   - Verify in: Settings → Secrets and variables → Actions

2. **Workflow Files** (already in repo)
   - `.github/workflows/deploy.yml` - Automatic ECS deployment
   - `.github/workflows/tests.yml` - Code quality checks

#### How It Works:

```
Your Code Push to main
    ↓
GitHub Actions Triggered
    ↓
Tests Run (linting, Docker build)
    ↓
Docker Image Built & Tagged
    ↓
Image Pushed to ECR
    ↓
ECS Task Definition Updated
    ↓
New Version Deployed
    ↓
Status Checks Pass
```

#### Usage:

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main

# GitHub Actions automatically:
# 1. Runs tests
# 2. Builds Docker image
# 3. Pushes to ECR
# 4. Updates ECS deployment
# 5. Verifies stability

# Monitor at: https://github.com/Raghunath2604/fraud-detection-docker-ecs/actions
```

---

## Workflow Details

### Deploy Workflow (deploy.yml)

**Triggers:** Push to `main` branch only

**Steps:**
1. Checkout code
2. Configure AWS credentials (OIDC)
3. Build Docker image with git SHA tag
4. Push to ECR (latest + SHA tag)
5. Update ECS task definition
6. Register new task definition revision
7. Update ECS service with new revision
8. Wait for deployment stability

**Time to deploy:** ~3-5 minutes (includes ECS stabilization)

### Test Workflow (tests.yml)

**Triggers:** Push to `main` AND pull requests

**Steps:**
1. Python linting with flake8
2. Code formatting check with black
3. Model training validation
4. Live API endpoint tests
5. Docker container tests
6. Security checks (no sensitive data)

---

## Updating Your Application

### Fast Deployment (Local):

```bash
# Make code changes
vim app/main.py

# Test locally
python train.py
uvicorn app.main:app --reload

# When ready, deploy immediately
./deploy.sh
```

### Standard Deployment (GitHub Actions):

```bash
# Make code changes
vim app/main.py

# Commit and push
git add app/main.py
git commit -m "Feature: Add new fraud detection logic"
git push origin main

# Watch deployment at:
# https://github.com/Raghunath2604/fraud-detection-docker-ecs/actions

# Deployed in ~3-5 minutes automatically
```

---

## Monitoring Deployments

### View GitHub Actions:
```
https://github.com/Raghunath2604/fraud-detection-docker-ecs/actions
```

### Check API Health:
```bash
curl http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/health
```

### View ECS Deployment:
```bash
aws ecs describe-services \
  --cluster fraud-api-cluster \
  --services fraud-api-service \
  --region us-east-1
```

### View Logs:
```bash
aws logs tail /ecs/fraud-api --follow
```

---

## Troubleshooting

### Deployment Failed?

1. **Check GitHub Actions logs:**
   - Go to Actions tab → View failed workflow
   - Look for error messages in build/deploy steps

2. **Check AWS credentials:**
   ```bash
   aws sts get-caller-identity
   ```

3. **Manual fallback:**
   ```bash
   ./deploy.sh
   ```

### GitHub Actions Not Running?

If workflows don't trigger after push:

1. Check: Settings → Actions → General
   - Ensure "Allow all actions" is enabled

2. Check: Settings → Actions → Runner groups
   - Ensure runners are available

3. Manual trigger (as fallback):
   ```bash
   ./deploy.sh
   ```

---

## Current Status

✅ **Deploy Script:** Working (tested 2024-04-18)
✅ **Docker Image:** Building & pushing to ECR
✅ **ECS Deployment:** Stable with 2 Fargate tasks
✅ **API Version:** 2.1-cicd-fixed (live)
✅ **GitHub Actions:** Configured and ready

**Next push to main will automatically deploy!**

---

## Quick Reference

| Task | Command | Time |
|------|---------|------|
| Manual Deploy | `./deploy.sh` | 2-3 min |
| Push to Auto-Deploy | `git push origin main` | 3-5 min |
| Check Health | `curl .../health` | Instant |
| View Logs | `aws logs tail /ecs/fraud-api` | Instant |

