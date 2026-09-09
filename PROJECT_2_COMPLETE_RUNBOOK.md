# Project 2 Complete Command Runbook

This is the operational runbook for the completed Project 2 submission.

## 1. Codespace Restart

```bash
cd /workspaces/cd14763-project-starter
python --version
uv --version
aws --version
node --version
git --version
agentcore --version
```

Verify AWS:

```bash
aws sts get-caller-identity
aws configure get region
```

If required:

```bash
aws configure set region us-east-1
```

## 2. Deployment Project

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

```bash
agentcore status
agentcore validate
```

## 3. Application Dependencies

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent
uv sync
python -m py_compile main.py
```

Verify imports:

```bash
uv run python -c "import boto3, strands, bedrock_agentcore, mcp, strands_tools, nest_asyncio; print('Project 2 imports OK')"
```

Verify implementation:

```bash
grep -n "BedrockAgentCoreApp\|GATEWAY_URL\|KB_ID\|MEMORY_ID\|MemoryHook\|search_knowledge_base\|calculate_loyalty_discount\|MCPClient\|AgentCoreBrowser\|async def invoke" main.py
```

## 4. Lambda Verification

```bash
aws lambda get-function \
  --function-name customer-order-tracker \
  --region us-east-1 \
  --query 'Configuration.FunctionArn'
```

```bash
aws lambda get-function \
  --function-name customer-refund-processor \
  --region us-east-1 \
  --query 'Configuration.FunctionArn'
```

## 5. Orders API Verification

```bash
aws apigateway get-rest-api \
  --rest-api-id vyr6af1wee \
  --region us-east-1
```

```bash
aws apigateway get-resources \
  --rest-api-id vyr6af1wee \
  --region us-east-1
```

Direct tests:

```bash
curl -s "https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod/orders/ORD-001"
```

```bash
curl -s "https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod/customers/CUST-123/orders"
```

```bash
curl -s "https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod/customers/CUST-123"
```

## 6. Gateway IAM Verification

Orders API permission:

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerSupportOrdersAPI
```

Refund Lambda permission:

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerRefundProcessor
```

If the refund permission is missing:

```bash
aws iam put-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerRefundProcessor \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "InvokeCustomerRefundProcessor",
        "Effect": "Allow",
        "Action": "lambda:InvokeFunction",
        "Resource": "arn:aws:lambda:us-east-1:177819261628:function:customer-refund-processor"
      }
    ]
  }'
```

## 7. Knowledge Base Verification

```bash
aws bedrock-agent-runtime retrieve \
  --knowledge-base-id 48BT8JT5TB \
  --retrieval-query '{"text":"What is the return policy for electronics?"}' \
  --region us-east-1
```

Expected information includes the electronics return policy.

## 8. S3 Verification

```bash
aws s3 ls s3://customer-support-kb-177819261628/
```

Expected:

```text
product_catalog.txt
```

## 9. Memory Verification

```bash
aws bedrock-agentcore-control get-memory \
  --memory-id CustomerSupportMemory-mXkuh4BqSK \
  --region us-east-1
```

Expected active strategies include:

```text
SEMANTIC
USER_PREFERENCE
```

## 10. Deploy / Redeploy

From:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

Run:

```bash
agentcore validate
agentcore deploy
agentcore status
```

## 11. Runtime Logs

```bash
agentcore logs --runtime CustomerSupportAgent --since 30m -n 100
```

For troubleshooting:

```bash
agentcore logs --runtime CustomerSupportAgent --since 10m -n 300
```

Always inspect the first actual exception before changing dependencies or configuration.

## 12. Functional Tests

### Order tracking

```bash
agentcore invoke '{"prompt":"Can you track order ORD-001?","customer_id":"CUST-123","session_id":"t1"}'
```

### Refund initiation

```bash
agentcore invoke '{"prompt":"I want to return my Kindle Paperwhite (ORD-002). Please initiate a refund.","customer_id":"CUST-123","session_id":"t2"}'
```

### Refund status

```bash
agentcore invoke '{"prompt":"Please check the refund status for my order ORD-002.","customer_id":"CUST-123","session_id":"refund-status"}'
```

### Return label

```bash
agentcore invoke '{"prompt":"Please get the return label for my order ORD-002.","customer_id":"CUST-123","session_id":"return-label"}'
```

### RAG

```bash
agentcore invoke '{"prompt":"What are the benefits of the Platinum loyalty tier?","customer_id":"CUST-123","session_id":"t3"}'
```

### Memory session A

```bash
agentcore invoke '{"prompt":"Hi, I am Jane. I prefer concise responses.","customer_id":"CUST-123","session_id":"s-A"}'
```

### Memory session B

```bash
agentcore invoke '{"prompt":"Do you remember my name and communication preference?","customer_id":"CUST-123","session_id":"s-B"}'
```

### Loyalty

```bash
agentcore invoke '{"prompt":"I am a Gold member with 4250 points. Calculate my discount on a $150 standard order.","customer_id":"CUST-123","session_id":"t5"}'
```

Expected:

```text
Points redeemed: 4000
Points discount: $40
Tier discount: $11
Final total: $99
Total savings: $51
Points earned: 150
Remaining points: 250
```

### Browser

```bash
agentcore invoke '{"prompt":"Go to https://www.amazon.com and tell me the page title.","customer_id":"CUST-123","session_id":"t6"}'
```

## 13. CloudWatch

Find log groups:

```bash
aws logs describe-log-groups \
  --region us-east-1 \
  --query 'logGroups[].logGroupName'
```

Identify the AgentCore runtime log group in the AWS Console.

Create:

```text
Metric filter: ERROR
Alarm: error count > 5
Evaluation period: 5 minutes
```

Capture the final alarm configuration as:

```text
Test_Evidences/Evidence-CloudWatch-Alarm.jpg
```

## 14. Final Code Verification

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent
python -m py_compile main.py
```

## 15. Final Deployment Verification

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
agentcore validate
agentcore status
agentcore logs --runtime CustomerSupportAgent --since 30m -n 100
```

## 16. Git Verification

```bash
cd /workspaces/cd14763-project-starter
git status
git diff
```

Before committing, ensure no credentials, tokens, temporary archives, or local caches are present.

Commit:

```bash
git add README.md PROJECT_2_COMPLETE_RUNBOOK.md PROJECT_2_REFLECTION.md Test_Evidences/ starter/ agentcore-deployment/
git status
git commit -m "Finalize Project 2 submission"
git push origin main
```

After pushing:

```bash
git status
```

Expected:

```text
nothing to commit, working tree clean
```
