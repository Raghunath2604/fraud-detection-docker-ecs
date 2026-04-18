#!/bin/bash
# Quick deployment script for Fraud Detection API
# Usage: ./deploy.sh

set -e

echo "🚀 Deploying Fraud Detection API..."
echo ""

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY="fraud-api"
ECS_CLUSTER="fraud-api-cluster"
ECS_SERVICE="fraud-api-service"
ECS_TASK_DEFINITION="fraud-api"

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t fraud-api:latest .

# Get ECR registry
echo "🔑 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Tag image
ECR_REGISTRY=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com
BUILD_TAG=$(date +%Y%m%d-%H%M%S)
docker tag fraud-api:latest $ECR_REGISTRY/$ECR_REPOSITORY:latest
docker tag fraud-api:latest $ECR_REGISTRY/$ECR_REPOSITORY:$BUILD_TAG

# Push to ECR
echo "📤 Pushing to ECR..."
docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
docker push $ECR_REGISTRY/$ECR_REPOSITORY:$BUILD_TAG

# Get current task definition
echo "📋 Getting task definition..."
aws ecs describe-task-definition \
  --task-definition $ECS_TASK_DEFINITION \
  --region $AWS_REGION \
  --query 'taskDefinition' > task-def.json

# Update image in task definition
echo "🔄 Updating task definition..."
export ECR_REGISTRY
python3 << 'EOF'
import json
import os

with open('task-def.json', 'r') as f:
    task_def = json.load(f)

# Remove non-editable fields
for field in ['taskDefinitionArn', 'revision', 'status', 'requiresAttributes',
              'compatibilities', 'registeredAt', 'registeredBy']:
    task_def.pop(field, None)

# Update image to use latest
ecr_registry = os.environ.get('ECR_REGISTRY', '')
task_def['containerDefinitions'][0]['image'] = f"{ecr_registry}/fraud-api:latest"

with open('task-def-updated.json', 'w') as f:
    json.dump(task_def, f)

print("[OK] Task definition updated")
EOF

# Register new task definition
echo "📝 Registering new task definition..."
REVISION=$(aws ecs register-task-definition \
  --cli-input-json file://task-def-updated.json \
  --region $AWS_REGION \
  --query 'taskDefinition.revision' \
  --output text)

echo "   Revision: $REVISION"

# Update service
echo "🔄 Deploying to ECS..."
aws ecs update-service \
  --cluster $ECS_CLUSTER \
  --service $ECS_SERVICE \
  --task-definition $ECS_TASK_DEFINITION:$REVISION \
  --force-new-deployment \
  --region $AWS_REGION > /dev/null

# Wait for deployment
echo "⏳ Waiting for deployment to stabilize (this may take 2-3 minutes)..."
aws ecs wait services-stable \
  --cluster $ECS_CLUSTER \
  --services $ECS_SERVICE \
  --region $AWS_REGION

echo ""
echo "✅ Deployment complete!"
echo "   API: http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com/"
echo ""

# Cleanup
rm -f task-def.json task-def-updated.json
