# GitHub Actions CI/CD Setup Guide

This project includes automated CI/CD pipelines for testing and deployment.

## 🔄 Workflows Included

### 1. **tests.yml** - Code Quality & Testing
Runs on every push and pull request:
- ✅ Linting with flake8
- ✅ Code formatting check with black
- ✅ Train model
- ✅ Test API endpoints
- ✅ Build Docker image
- ✅ Test Docker container
- ✅ Security checks (no secrets exposed)

### 2. **deploy.yml** - Build & Deploy to AWS ECS
Runs on every push to main branch:
- ✅ Build Docker image
- ✅ Push to Amazon ECR
- ✅ Update ECS task definition
- ✅ Deploy to ECS service
- ✅ Wait for deployment to stabilize

## 🔐 Setup Required

### Step 1: Create AWS IAM Role for GitHub Actions

```bash
# Create trust policy for GitHub
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:Raghunath2604/fraud-detection-docker-ecs:*"
        }
      }
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name GitHubActionsDeployRole \
  --assume-role-policy-document file://trust-policy.json
```

### Step 2: Add Required Permissions

```bash
# Create inline policy
cat > policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "arn:aws:ecr:us-east-1:<ACCOUNT_ID>:repository/fraud-api"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:DescribeTasks",
        "ecs:ListTasks",
        "ecs:RegisterTaskDefinition"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole"
    }
  ]
}
EOF

# Attach policy
aws iam put-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-name GitHubActionsPolicy \
  --policy-document file://policy.json
```

### Step 3: Get Role ARN

```bash
aws iam get-role \
  --role-name GitHubActionsDeployRole \
  --query 'Role.Arn' \
  --output text
```

### Step 4: Add GitHub Secret

1. Go to GitHub repository
2. Settings → Secrets and variables → Actions
3. Create new secret: `AWS_ROLE_ARN`
4. Paste the role ARN from Step 3

Example:
```
arn:aws:iam::429288623250:role/GitHubActionsDeployRole
```

## 📋 How It Works

### Automatic Testing (Every Push)
```
You push code
    ↓
GitHub Actions tests.yml runs
    ↓
Linting & formatting checks
    ↓
Train model
    ↓
Test API locally
    ↓
Build Docker image
    ↓
Test Docker container
    ↓
✅ Pass → Ready for deployment
❌ Fail → Shows errors in GitHub
```

### Automatic Deployment (Push to main)
```
You push to main
    ↓
GitHub Actions deploy.yml runs
    ↓
Build Docker image
    ↓
Push to ECR
    ↓
Update ECS task definition
    ↓
Deploy to ECS
    ↓
Wait for service to stabilize
    ↓
✅ New version live!
```

## 🚀 Usage

### Add a Feature

1. Create a new branch:
   ```bash
   git checkout -b feature/new-feature
   ```

2. Make changes to code:
   ```bash
   # Edit app/main.py or other files
   ```

3. Push to GitHub:
   ```bash
   git push origin feature/new-feature
   ```

4. GitHub Actions automatically:
   - ✅ Runs tests
   - ✅ Checks code quality
   - ✅ Shows status on pull request

5. Create pull request (optional for code review)

6. Merge to main:
   ```bash
   git checkout main
   git merge feature/new-feature
   git push origin main
   ```

7. GitHub Actions automatically:
   - ✅ Tests new code
   - ✅ Builds Docker image
   - ✅ Pushes to ECR
   - ✅ Deploys to ECS
   - ✅ Your live API is updated! 🚀

## 📊 Check Status

### In GitHub:
- Go to repository
- Click "Actions" tab
- See workflow status
- Click workflow to see logs

### View deployments:
```bash
# Check ECS service status
aws ecs describe-services \
  --cluster fraud-api-cluster \
  --services fraud-api-service \
  --query 'services[0].[runningCount,desiredCount,status]'
```

## 🔧 Customization

### Change deployment trigger
Edit `.github/workflows/deploy.yml`:
```yaml
on:
  push:
    branches:
      - main
      - develop  # Add other branches
```

### Add more tests
Edit `.github/workflows/tests.yml`:
```yaml
- name: My custom test
  run: |
    # Add your test commands
```

### Change AWS region
Edit both workflow files:
```yaml
env:
  AWS_REGION: us-west-2  # Change region
```

## ⚠️ Security Notes

- GitHub Actions uses OIDC for AWS authentication (no credentials stored)
- Role has minimal permissions (least privilege)
- All secrets stored in GitHub Secrets
- Workflows are visible in GitHub (best practice)
- Don't expose AWS credentials in workflow logs

## 📝 Example: Add a New Feature

### Scenario: Add email notifications

1. **Create branch:**
   ```bash
   git checkout -b feature/email-notifications
   ```

2. **Update app/main.py:**
   ```python
   # Add email notification logic
   ```

3. **Add tests:**
   ```python
   # Add tests in tests.yml
   ```

4. **Push:**
   ```bash
   git push origin feature/email-notifications
   ```

5. **GitHub Actions runs automatically:**
   - Tests pass ✅
   - Code quality OK ✅

6. **Merge to main:**
   ```bash
   git checkout main
   git merge feature/email-notifications
   git push origin main
   ```

7. **Automatic deployment:**
   - Docker image built with new feature
   - Pushed to ECR
   - ECS updated
   - Live in production in ~2 minutes! 🚀

## 🎯 Next Steps

1. Set up AWS IAM role (see steps above)
2. Add AWS_ROLE_ARN to GitHub Secrets
3. Test by making a small change to app/main.py
4. Watch workflow run in GitHub Actions tab
5. See your changes deployed to ECS automatically!

---

**CI/CD is now ready! Every push = Automatic testing & deployment 🚀**
