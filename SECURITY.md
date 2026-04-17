# 🔐 Security & Best Practices Guide

**IMPORTANT:** Never commit sensitive information to public GitHub repositories!

---

## ⚠️ Sensitive Information to NEVER Share

### 1. AWS Account IDs
```bash
❌ WRONG: 429288623250
✅ RIGHT: <YOUR_ACCOUNT_ID>
```

### 2. AWS Endpoints
```bash
❌ WRONG: http://fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com
✅ RIGHT: http://<YOUR_ALB_ENDPOINT>
```

### 3. IAM Role ARNs
```bash
❌ WRONG: arn:aws:iam::429288623250:role/ecsTaskExecutionRole
✅ RIGHT: arn:aws:iam::<YOUR_ACCOUNT_ID>:role/<ROLE_NAME>
```

### 4. ECR Repository URIs
```bash
❌ WRONG: 429288623250.dkr.ecr.us-east-1.amazonaws.com/fraud-api
✅ RIGHT: <YOUR_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com/<REPO_NAME>
```

### 5. Task Definition ARNs
```bash
❌ WRONG: arn:aws:ecs:us-east-1:429288623250:task-definition/fraud-api:1
✅ RIGHT: arn:aws:ecs:<REGION>:<ACCOUNT_ID>:task-definition/<TASK>:<VERSION>
```

### 6. Load Balancer ARNs
```bash
❌ WRONG: arn:aws:elasticloadbalancing:us-east-1:429288623250:loadbalancer/...
✅ RIGHT: arn:aws:elasticloadbalancing:<REGION>:<ACCOUNT_ID>:loadbalancer/...
```

### 7. AWS Credentials
```bash
❌ WRONG: 
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

✅ RIGHT: 
Use IAM roles, environment variables, or AWS credential files
NEVER commit credentials!
```

---

## ✅ What CAN Be Public

✅ Architecture diagrams (without real IDs)
✅ Code structure and logic
✅ General AWS commands (with placeholders)
✅ Documentation and guides
✅ Placeholder values and examples
✅ Configuration templates

---

## 🛡️ Security Checklist

### Before Committing to GitHub
- [ ] Remove all AWS account IDs
- [ ] Replace endpoints with placeholders
- [ ] Remove real ARNs and role names
- [ ] No AWS credentials in code
- [ ] No API keys or secrets
- [ ] Check `.gitignore` is comprehensive
- [ ] Review all commits before pushing

### GitHub Repository Settings
- [ ] Set to public (if sharing) or private
- [ ] Enable branch protection
- [ ] Require pull request reviews
- [ ] Enable secret scanning
- [ ] Disable force pushes to main

### AWS Security
- [ ] Use IAM roles, not root account
- [ ] Enable MFA on root account
- [ ] Implement least privilege policies
- [ ] Use temporary credentials
- [ ] Rotate access keys regularly
- [ ] Enable CloudTrail logging
- [ ] Enable VPC Flow Logs

### Application Security
- [ ] Use HTTPS in production
- [ ] Validate all inputs
- [ ] Use secrets manager for sensitive data
- [ ] Implement rate limiting
- [ ] Enable logging and monitoring
- [ ] Keep dependencies updated

---

## 📋 Using Placeholders in Documentation

### Example: Good Documentation Pattern

```markdown
# Deploy to AWS ECR

## Push Docker Image

1. Get your AWS Account ID:
   ```bash
   aws sts get-caller-identity --query Account --output text
   ```

2. Create ECR repository:
   ```bash
   aws ecr create-repository \
     --repository-name <YOUR_APP_NAME> \
     --region <YOUR_REGION>
   ```

3. Tag and push image:
   ```bash
   docker tag <YOUR_APP>:latest \
     <YOUR_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com/<YOUR_APP>:latest
   
   docker push \
     <YOUR_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com/<YOUR_APP>:latest
   ```

Replace:
- `<YOUR_ACCOUNT_ID>` with your AWS account ID
- `<YOUR_REGION>` with your AWS region (e.g., us-east-1)
- `<YOUR_APP>` with your application name
- `<YOUR_APP_NAME>` with your ECR repository name
```

---

## 🔧 Managing Secrets Locally

### Option 1: Environment Variables

```bash
# Create local .env file (NOT committed to Git)
cat > .env << 'EOF'
AWS_ACCOUNT_ID=429288623250
AWS_REGION=us-east-1
ALB_ENDPOINT=fraud-api-alb-1872682528.us-east-1.elb.amazonaws.com
ROLE_ARN=arn:aws:iam::429288623250:role/ecsTaskExecutionRole
EOF

# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

### Option 2: AWS Credentials File

```bash
# ~/.aws/credentials (never committed)
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# ~/.aws/config (never committed)
[default]
region = us-east-1
output = json
```

### Option 3: AWS Vault (Recommended)

```bash
# Use aws-vault to manage credentials securely
aws-vault add default
aws-vault exec default -- aws s3 ls
```

---

## 📝 Updating Documentation Safely

### When Creating Guides:
1. Use placeholders for all values
2. Add notes like "Replace with your value"
3. Never show real infrastructure details
4. Test locally with real values, but don't commit them

### Example Template:

```bash
# ✅ GOOD - Use this pattern in documentation

# Replace these with your actual values:
export AWS_ACCOUNT_ID=<your-account-id>
export AWS_REGION=<your-region>
export APP_NAME=<your-app-name>

# Then use in commands:
docker tag ${APP_NAME}:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}:latest
```

---

## 🚨 If You Accidentally Committed Secrets

### Immediate Action:

1. **Rotate credentials immediately**
   ```bash
   # Generate new AWS credentials
   # Deactivate old ones
   ```

2. **Remove from Git history**
   ```bash
   # Option A: Use git-filter-branch
   git filter-branch --tree-filter 'rm -f .env' -- --all
   
   # Option B: Use BFG Repo-Cleaner
   bfg --delete-files .env
   ```

3. **Force push to remove history**
   ```bash
   git push origin --force
   ```

4. **Notify your team**

---

## 📚 Security Resources

### AWS Security
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

### Git Security
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/best-practices-for-repository-security)

### Tools
- [AWS Vault](https://github.com/99designs/aws-vault)
- [git-secrets](https://github.com/awslabs/git-secrets)
- [TruffleHog](https://github.com/trufflesecurity/truffleHog)

---

## ✅ Final Checklist Before Pushing

```bash
# Run these checks before pushing to public repos:

# 1. Check for secrets
git secrets --scan

# 2. Review recent commits
git log --oneline -10

# 3. Check for sensitive files
grep -r "aws_access_key" .
grep -r "AWS_SECRET" .
grep -r ".dkr.ecr" .
grep -r "account_id" .

# 4. Verify .gitignore
cat .gitignore

# 5. Test push is safe
git push --dry-run origin main
```

---

**Remember:** Public repositories are accessible to everyone. Treat them as if the whole world can see them!

**Your security is your responsibility. Code secure, push safe! 🔐**
