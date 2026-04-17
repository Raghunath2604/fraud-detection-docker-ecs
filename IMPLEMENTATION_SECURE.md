# 🔧 Implementation Guide: Docker → ECR → ECS → Load Balancer

Complete step-by-step guide to deploying a containerized application on AWS with high availability.

⚠️ **SECURITY NOTE:** This guide uses placeholder values for all sensitive information:
- Account IDs: Use `<YOUR_ACCOUNT_ID>`
- Regions: Use `<YOUR_REGION>` (e.g., us-east-1)
- Resource names: Use your own naming
- Endpoints: Never commit real URLs to public repos
- ARNs: Will be generated during deployment

---

## Prerequisites

### Verify AWS Setup
```bash
# Get your actual account ID (keep this secret!)
aws sts get-caller-identity --query Account --output text

# Save it as variable for use below
export AWS_ACCOUNT_ID=<your-account-id-here>
export AWS_REGION=us-east-1
```

---

## Phase 3: ECR Setup (PUSH DOCKER TO ECR)

### Step 3.1: Create ECR Repository

```bash
aws ecr create-repository \
  --repository-name fraud-api \
  --region ${AWS_REGION}
```

Output will give you:
```
"repositoryUri": "<YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fraud-api"
```

**SAVE THIS** - but don't commit it to public repos!

### Step 3.2: Authenticate

```bash
# This token is temporary - changes every time
aws ecr get-login-password --region ${AWS_REGION} | docker login \
  --username AWS \
  --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
```

### Step 3.3: Tag & Push

```bash
# Tag your image
docker tag fraud-api:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/fraud-api:latest

# Push to ECR
docker push \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/fraud-api:latest
```

---

## Phase 4: ECS Setup (SETUP ECS)

### Step 4.1: Create IAM Role

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

# Attach policy
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Get role ARN (save for next step)
export ROLE_ARN=$(aws iam get-role --role-name ecsTaskExecutionRole \
  --query 'Role.Arn' --output text)
```

### Step 4.2: Register Task Definition

```bash
aws ecs register-task-definition \
  --family fraud-api \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 256 \
  --memory 512 \
  --execution-role-arn ${ROLE_ARN} \
  --container-definitions "[{
    \"name\": \"fraud-api\",
    \"image\": \"${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/fraud-api:latest\",
    \"portMappings\": [{\"containerPort\": 8000}],
    \"essential\": true
  }]" \
  --region ${AWS_REGION}
```

### Step 4.3: Create ECS Cluster

```bash
aws ecs create-cluster \
  --cluster-name fraud-api-cluster \
  --region ${AWS_REGION}
```

---

## Phase 5: Load Balancer Setup

### Get Your VPC & Subnets

```bash
# Get default VPC
export VPC_ID=$(aws ec2 describe-vpcs \
  --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' \
  --output text --region ${AWS_REGION})

# Get 2 subnets
export SUBNET_IDS=$(aws ec2 describe-subnets \
  --filters Name=vpc-id,Values=${VPC_ID} \
  --query 'Subnets[0:2].SubnetId' \
  --output text --region ${AWS_REGION})

echo "VPC: ${VPC_ID}"
echo "Subnets: ${SUBNET_IDS}"
```

### Create Security Group

```bash
export SG_ID=$(aws ec2 create-security-group \
  --group-name fraud-api-sg \
  --description "Security group for Fraud API" \
  --vpc-id ${VPC_ID} \
  --region ${AWS_REGION} \
  --query 'GroupId' --output text)

# Allow traffic
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp --port 80 --cidr 0.0.0.0/0 \
  --region ${AWS_REGION}

aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0 \
  --region ${AWS_REGION}
```

### Create Load Balancer

```bash
export ALB_ARN=$(aws elbv2 create-load-balancer \
  --name fraud-api-alb \
  --subnets ${SUBNET_IDS} \
  --security-groups ${SG_ID} \
  --scheme internet-facing \
  --type application \
  --region ${AWS_REGION} \
  --query 'LoadBalancers[0].LoadBalancerArn' --output text)

# Get DNS name (this is your endpoint)
export ALB_DNS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns ${ALB_ARN} \
  --region ${AWS_REGION} \
  --query 'LoadBalancers[0].DNSName' --output text)

echo "Your ALB endpoint: ${ALB_DNS}"
# ⚠️ KEEP THIS PRIVATE - Don't share or commit!
```

### Create Target Group

```bash
export TG_ARN=$(aws elbv2 create-target-group \
  --name fraud-api-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id ${VPC_ID} \
  --target-type ip \
  --region ${AWS_REGION} \
  --query 'TargetGroups[0].TargetGroupArn' --output text)
```

### Create Listener

```bash
aws elbv2 create-listener \
  --load-balancer-arn ${ALB_ARN} \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=${TG_ARN} \
  --region ${AWS_REGION}
```

---

## Phase 6: Deploy Service

```bash
aws ecs create-service \
  --cluster fraud-api-cluster \
  --service-name fraud-api-service \
  --task-definition fraud-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS}],securityGroups=[${SG_ID}],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=${TG_ARN},containerName=fraud-api,containerPort=8000" \
  --region ${AWS_REGION}
```

---

## Testing Your API

```bash
# Wait for tasks to start (~30 seconds)
sleep 30

# Test health endpoint
curl http://${ALB_DNS}/health

# Test prediction
curl -X POST http://${ALB_DNS}/predict \
  -H "Content-Type: application/json" \
  -d '{"amount": 2500, "time": 320, "location_risk": 1, "device_new": 1}'
```

---

## ⚠️ Security Best Practices

### DO ✅
- Use environment variables for sensitive data
- Rotate IAM credentials regularly
- Use private ECR repositories
- Enable CloudTrail logging
- Use VPC endpoints
- Implement least privilege IAM roles
- Keep documentation generic (use placeholders)

### DON'T ❌
- Commit AWS credentials to Git
- Expose account IDs in public repos
- Share ALB endpoints publicly
- Use root AWS account
- Store secrets in code
- Use overly permissive IAM policies
- Push real infrastructure URLs to GitHub

---

## Secrets Management

Store your sensitive data locally:

```bash
# Create .env file (NEVER commit this!)
cat > .env << 'SECRETS'
AWS_ACCOUNT_ID=<your-actual-id>
AWS_REGION=us-east-1
ALB_ENDPOINT=<your-alb-endpoint>
ROLE_ARN=<your-role-arn>
SECRETS

# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

---

## Cleanup (When Done)

```bash
# Delete service
aws ecs delete-service \
  --cluster fraud-api-cluster \
  --service fraud-api-service \
  --force

# Delete cluster
aws ecs delete-cluster \
  --cluster fraud-api-cluster

# Delete load balancer
aws elbv2 delete-load-balancer --load-balancer-arn ${ALB_ARN}

# Delete other resources as needed
```

---

**Remember:** Never commit real AWS credentials, endpoints, or infrastructure details to public repositories!

