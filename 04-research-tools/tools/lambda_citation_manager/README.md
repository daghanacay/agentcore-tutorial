# Lambda Deployment for Research Agent

This directory contains files for deploying the research agent to AWS Lambda.

## Deployment Options

### Option 1: Using the Deploy Script (Recommended for Quick Setup)

```bash
# Set environment variables
export AWS_REGION=us-east-1
export LAMBDA_ROLE_ARN=arn:aws:iam::123456789012:role/lambda-execution-role

# Deploy
./deploy.sh
```

**What it does:**
- Creates ECR repository if needed
- Builds Docker image
- Pushes to ECR
- Creates/updates Lambda function
- Tests the deployment

### Option 2: Using AWS SAM (Recommended for Production)

```bash
# Build
sam build

# Deploy (first time - guided)
sam deploy --guided

# Deploy (subsequent)
sam deploy
```

**What it creates:**
- Lambda function with container image
- API Gateway with API key authentication
- CloudWatch log group
- IAM roles and permissions

### Option 3: Using AgentCore CLI (Simplest)

```bash
# From the agents directory
cd ../../agents

# Deploy to AgentCore Runtime
agentcore deploy \
  --runtime-name research-agent \
  --model anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --memory 2048 \
  --timeout 300
```

**Benefits:**
- No Docker or ECR setup needed
- Automatic scaling and observability
- Integrated with AgentCore services

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Container image definition |
| `lambda_handler.py` | Lambda function handler |
| `requirements.txt` | Python dependencies |
| `deploy.sh` | Deployment script |
| `template.yaml` | AWS SAM template |
| `README.md` | This file |

## Prerequisites

### For Deploy Script or SAM:
- AWS CLI installed and configured
- Docker installed and running
- IAM permissions for:
  - ECR (create repository, push images)
  - Lambda (create/update functions)
  - IAM (create roles)
  - API Gateway (create APIs) - SAM only

### For AgentCore CLI:
- AgentCore CLI installed: `pip install bedrock-agentcore-toolkit`
- AWS credentials configured
- Bedrock model access

## Configuration

### Lambda Function Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Memory | 2048 MB | Adjust based on workload |
| Timeout | 300s (5 min) | Max Lambda timeout |
| Architecture | x86_64 | Use ARM64 for cost savings |
| Storage | 1024 MB | Ephemeral storage |

### Environment Variables

The Lambda function supports these environment variables:

```yaml
ENVIRONMENT: dev | staging | prod
LOG_LEVEL: INFO | DEBUG | WARNING | ERROR
PYTHONPATH: /var/task
```

## Testing

### Test with AWS CLI

```bash
aws lambda invoke \
  --function-name research-agent \
  --payload '{"message": "Research multi-agent systems"}' \
  response.json

cat response.json
```

### Test with API Gateway

```bash
# Get API endpoint from SAM outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name research-agent-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Make request
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"message": "Research RAG systems"}'
```

## Monitoring

### View Logs

```bash
# Real-time logs
aws logs tail /aws/lambda/research-agent --follow

# Recent logs
aws logs tail /aws/lambda/research-agent --since 1h
```

### Metrics

```bash
# Get invocation count
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=research-agent \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Get error rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=research-agent \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## Cost Optimization

1. **Right-size Memory**: Monitor actual usage and adjust
   ```bash
   # View memory usage
   aws logs filter-pattern "/aws/lambda/research-agent" "Max Memory Used"
   ```

2. **Use ARM64**: 20% cost savings
   ```yaml
   # In template.yaml
   Architectures:
     - arm64
   ```

3. **Reserved Concurrency**: For predictable workloads
   ```bash
   aws lambda put-function-concurrency \
     --function-name research-agent \
     --reserved-concurrent-executions 10
   ```

## Troubleshooting

### Issue: Cold start timeout

**Solution**: Increase memory or use provisioned concurrency

```bash
aws lambda put-provisioned-concurrency-config \
  --function-name research-agent \
  --provisioned-concurrent-executions 2 \
  --qualifier LATEST
```

### Issue: Out of memory

**Solution**: Check CloudWatch logs for memory usage

```bash
aws logs filter-pattern "/aws/lambda/research-agent" "Memory"
```

### Issue: Container image too large

**Solution**: Optimize Docker image

```dockerfile
# Use multi-stage build
FROM python:3.11-slim as builder
# ... build dependencies

FROM public.ecr.aws/lambda/python:3.11
COPY --from=builder /app /var/task
```

### Issue: Import errors

**Solution**: Verify PYTHONPATH is set correctly

```bash
aws lambda update-function-configuration \
  --function-name research-agent \
  --environment Variables={PYTHONPATH=/var/task}
```

## Security

### IAM Role Permissions

Minimum required permissions for Lambda execution role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

### Secrets Management

Store API keys in AWS Secrets Manager:

```bash
# Create secret
aws secretsmanager create-secret \
  --name research-agent/api-keys \
  --secret-string '{"pubmed_key":"xxx","arxiv_key":"yyy"}'

# Update Lambda to access secrets
aws lambda update-function-configuration \
  --function-name research-agent \
  --environment Variables={SECRET_ARN=arn:aws:secretsmanager:...}
```

## Next Steps

- Add custom domain with Route53
- Set up CI/CD with CodePipeline
- Implement canary deployments with Lambda aliases
- Add X-Ray tracing for performance insights
- Configure VPC for private resource access

## Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [AgentCore Runtime Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-runtime.html)
