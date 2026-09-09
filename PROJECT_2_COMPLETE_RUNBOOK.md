# Project 2 Complete Runbook
## Production-Grade Customer Support AI Agent with Amazon Bedrock AgentCore

**Udacity AWS AI Engineering Nanodegree — Course 2**  
**Region:** `us-east-1`  
**Repository:** `Swapnil2095/cd14763-project-starter`

This file is the end-to-end command and verification runbook for Project 2.

> **Important:** Run commands in the order shown. Do not recreate an AWS resource that already exists. The deployment project is separate from the original `starter/` project so the starter repository remains available for submission.

---

# 0. Project Architecture

```text
Customer
   |
   v
AgentCore Runtime: CustomerSupportAgent
   |
   +--> Strands Agent
   |      |
   |      +--> Knowledge Base tool
   |      +--> Loyalty / Code Interpreter tool
   |      +--> AgentCore Browser
   |      +--> AgentCore Memory hooks
   |      +--> MCP Gateway tools
   |
   +--> CustomerSupportGateway
   |      |
   |      +--> CustomerSupportOrdersTarget
   |      |       |
   |      |       +--> API Gateway
   |      |               |
   |      |               +--> customer-order-tracker Lambda
   |      |
   |      +--> CustomerSupportRefundTarget
   |              |
   |              +--> customer-refund-processor Lambda
   |
   +--> CustomerSupportKB
   |      |
   |      +--> S3 product catalog
   |
   +--> CustomerSupportMemory
          |
          +--> SEMANTIC
          +--> USER_PREFERENCE
```

---

# 1. Start / Restart Codespace

Run these after opening or restarting the Codespace.

## 1.1 Go to repository

```bash
cd /workspaces/cd14763-project-starter
```

## 1.2 Verify tools

```bash
python --version
uv --version
aws --version
node --version
git --version
agentcore --version
```

Expected working environment:

```text
Python 3.14.2
uv 0.12.11
AWS CLI 2.x
Node 24.x
Git 2.x
AgentCore CLI 0.28.1
```

Exact patch versions can differ if the commands work.

## 1.3 Verify AWS identity

```bash
aws sts get-caller-identity
```

## 1.4 Verify region

```bash
aws configure get region
```

If necessary:

```bash
aws configure set region us-east-1
```

Verify:

```bash
aws configure get region
```

---

# 2. Project 2 Paths

Original starter:

```text
/workspaces/cd14763-project-starter/starter
```

Deployment project:

```text
/workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

Deployed application:

```text
/workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent
```

Go to deployment project:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

Verify:

```bash
pwd
ls
```

Expected:

```text
agentcore
app
README.md
AGENTS.md
```

---

# 3. Git Status

Run:

```bash
git status
```

Do not accidentally commit:

- AWS credential files
- downloaded AWS CLI ZIP files
- Python `__pycache__`
- local virtual environments
- temporary files
- secrets

---

# 4. Original Starter Environment

Go to the starter:

```bash
cd /workspaces/cd14763-project-starter/starter
```

If a Python environment is needed:

```bash
uv sync
```

Verify:

```bash
uv run python --version
```

Test imports:

```bash
uv run python -c "import boto3, strands, bedrock_agentcore, mcp; print('Starter imports OK')"
```

Return to deployment project:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

---

# 5. Project 2 Deployment Environment

Go to:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent
```

Install/synchronize dependencies:

```bash
uv sync
```

Verify Python:

```bash
uv run python --version
```

Verify imports:

```bash
uv run python -c "import boto3, strands, bedrock_agentcore, mcp; print('Project 2 imports OK')"
```

Verify important packages:

```bash
uv run python -c "import strands_tools, nest_asyncio; print('Strands tools and nest-asyncio OK')"
```

---

# 6. Verify Completed main.py

Check file size:

```bash
wc -l main.py
```

Current completed deployment file is approximately 685 lines.

Find the major implementation sections:

```bash
grep -n "app = BedrockAgentCoreApp\|GATEWAY_URL =\|KB_ID =\|MEMORY_ID =\|class MemoryHook\|def search_knowledge_base\|def calculate_loyalty_discount\|async def invoke" main.py
```

Compile:

```bash
python -m py_compile main.py
```

No output means compilation succeeded.

---

# 7. Required main.py Configuration

The deployment `main.py` should contain the actual resource values:

```python
GATEWAY_URL = "https://customersupportgateway-bi9wbwaick.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
KB_ID = "48BT8JT5TB"
REGION = "us-east-1"
MEMORY_ID = "CustomerSupportMemory-mXkuh4BqSK"
```

Verify from terminal:

```bash
grep -n "GATEWAY_URL\|KB_ID\|REGION\|MEMORY_ID" main.py
```

---

# 8. AgentCore Project Configuration

Return to project root:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

Validate configuration:

```bash
agentcore validate
```

Check deployment status:

```bash
agentcore status
```

---

# 9. If Creating the AgentCore Deployment Project From Scratch

Only use this section if the deployment project does not exist.

Create a separate project:

```bash
mkdir -p /workspaces/cd14763-project-starter/agentcore-deployment
cd /workspaces/cd14763-project-starter/agentcore-deployment
```

Create:

```bash
agentcore create \
  --project-name customersupport \
  --name CustomerSupportAgent \
  --language Python \
  --framework Strands \
  --model-provider Bedrock \
  --memory longAndShortTerm \
  --protocol HTTP \
  --build CodeZip
```

Then:

```bash
cd customersupport/app/CustomerSupportAgent
```

Copy the completed starter implementation:

```bash
cp ../../../../starter/main.py main.py
```

Check:

```bash
wc -l main.py
```

Install dependencies:

```bash
uv sync
```

Compile:

```bash
python -m py_compile main.py
```

> Do not run `agentcore create` again when the project already exists.

---

# 10. pyproject.toml Dependencies

The deployed application needs the following dependency categories:

```text
aws-opentelemetry-distro
bedrock-agentcore
botocore[crt]
mcp
strands-agents
strands-agents-tools
boto3
nest-asyncio
```

Inspect:

```bash
cat pyproject.toml
```

If dependencies were changed:

```bash
uv lock
uv sync
```

Then:

```bash
python -m py_compile main.py
```

---

# 11. Lambda Verification

## 11.1 Order tracker

```bash
aws lambda get-function \
  --function-name customer-order-tracker \
  --region us-east-1 \
  --query 'Configuration.FunctionArn'
```

## 11.2 Refund processor

```bash
aws lambda get-function \
  --function-name customer-refund-processor \
  --region us-east-1 \
  --query 'Configuration.FunctionArn'
```

Expected refund Lambda ARN:

```text
arn:aws:lambda:us-east-1:177819261628:function:customer-refund-processor
```

---

# 12. Order Lambda Direct Test

Test `ORD-001`:

```bash
aws lambda invoke \
  --function-name customer-order-tracker \
  --region us-east-1 \
  --payload '{"httpMethod":"GET","pathParameters":{"order_id":"ORD-001"}}' \
  /tmp/order-test.json
```

Display:

```bash
cat /tmp/order-test.json
```

Expected data includes:

```text
ORD-001
CUST-123
SHIPPED
TRK987654321
UPS
```

---

# 13. API Gateway Verification

API:

```text
CustomerSupportOrdersAPI
```

API ID:

```text
vyr6af1wee
```

Stage:

```text
prod
```

Base URL:

```text
https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod
```

Check REST API:

```bash
aws apigateway get-rest-api \
  --rest-api-id vyr6af1wee \
  --region us-east-1
```

Check resources:

```bash
aws apigateway get-resources \
  --rest-api-id vyr6af1wee \
  --region us-east-1
```

Expected routes:

```text
GET /orders/{order_id}
GET /customers/{customer_id}/orders
GET /customers/{customer_id}
```

---

# 14. Direct API Gateway Tests

## 14.1 Order

```bash
curl -s \
  "https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod/orders/ORD-001"
```

## 14.2 Customer orders

```bash
curl -s \
  "https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod/customers/CUST-123/orders"
```

## 14.3 Customer

```bash
curl -s \
  "https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod/customers/CUST-123"
```

---

# 15. AgentCore Gateway

Gateway:

```text
CustomerSupportGateway
```

MCP URL:

```text
https://customersupportgateway-bi9wbwaick.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp
```

Gateway targets:

```text
CustomerSupportOrdersTarget
CustomerSupportRefundTarget
```

Expected tools:

```text
get_customer
get_customer_orders
get_order
initiate_refund
check_refund_status
get_return_label
```

---

# 16. Gateway IAM Permissions

Gateway execution role:

```text
AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768
```

## 16.1 API Gateway permission

Verify:

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerSupportOrdersAPI
```

Required action:

```text
execute-api:Invoke
```

Required resource:

```text
arn:aws:execute-api:us-east-1:177819261628:vyr6af1wee/prod/*/*
```

## 16.2 Refund Lambda permission

Verify:

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerRefundProcessor
```

If missing, add it:

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

Verify again:

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerRefundProcessor
```

---

# 17. S3 Product Catalog

Bucket:

```text
customer-support-kb-177819261628
```

Check:

```bash
aws s3 ls s3://customer-support-kb-177819261628/
```

Expected:

```text
product_catalog.txt
```

Upload if required:

```bash
aws s3 cp \
  /workspaces/cd14763-project-starter/starter/product_catalog.txt \
  s3://customer-support-kb-177819261628/product_catalog.txt
```

Verify:

```bash
aws s3api head-object \
  --bucket customer-support-kb-177819261628 \
  --key product_catalog.txt
```

---

# 18. Knowledge Base

Knowledge Base:

```text
CustomerSupportKB
```

ID:

```text
48BT8JT5TB
```

Region:

```text
us-east-1
```

Test retrieval directly:

```bash
aws bedrock-agent-runtime retrieve \
  --knowledge-base-id 48BT8JT5TB \
  --retrieval-query '{"text":"What is the return policy for electronics?"}' \
  --region us-east-1
```

The response should contain relevant product/support information.

Expected electronics return window:

```text
15 days
```

---

# 19. AgentCore Memory

Memory:

```text
CustomerSupportMemory
```

Memory ID:

```text
CustomerSupportMemory-mXkuh4BqSK
```

Get memory:

```bash
aws bedrock-agentcore-control get-memory \
  --memory-id CustomerSupportMemory-mXkuh4BqSK \
  --region us-east-1
```

Expected strategies:

```text
SEMANTIC
USER_PREFERENCE
```

Expected namespaces:

```text
cs_agent/{actorId}/facts
cs_agent/{actorId}/preferences
```

---

# 20. Verify Memory Namespace Code

From the deployed application:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent
```

Find namespace implementation:

```bash
grep -n "def get_namespaces\|namespaceTemplates\|retrieve_memories\|create_event\|class MemoryHook" main.py
```

Compile:

```bash
python -m py_compile main.py
```

---

# 21. Knowledge Base Tool Verification

Find the implementation:

```bash
grep -n "def search_knowledge_base\|knowledgeBaseId\|retrievalQuery\|retrievalResults" main.py
```

The implementation should use:

```text
_bedrock_runtime.retrieve()
```

Compile:

```bash
python -m py_compile main.py
```

---

# 22. Loyalty / Code Interpreter Verification

Find the implementation:

```bash
grep -n "def calculate_loyalty_discount\|code_session\|executeCode" main.py
```

Compile:

```bash
python -m py_compile main.py
```

---

# 23. Agent Entrypoint Verification

Find:

```bash
grep -n "async def invoke\|MCPClient\|streamable_http_client\|AgentCoreBrowser\|gateway_tools" main.py
```

Compile:

```bash
python -m py_compile main.py
```

---

# 24. Deploy AgentCore Runtime

Go to deployment root:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

Validate:

```bash
agentcore validate
```

Deploy:

```bash
agentcore deploy
```

Check:

```bash
agentcore status
```

Expected:

```text
CustomerSupportAgent: Deployed - Runtime: READY
```

---

# 25. Runtime Logs

```bash
agentcore logs \
  --runtime CustomerSupportAgent \
  --since 30m \
  -n 100
```

For troubleshooting:

```bash
agentcore logs \
  --runtime CustomerSupportAgent \
  --since 10m \
  -n 300
```

---

# 26. Basic Agent Test

```bash
agentcore invoke \
'{"prompt":"Hello, what can you help me with?","customer_id":"CUST-123","session_id":"basic-test"}'
```

---

# 27. Functional Test 1 — Order Tracking

```bash
agentcore invoke \
'{"prompt":"What is the status of order ORD-001? Please give me the tracking number, carrier, and estimated delivery date.","customer_id":"CUST-123","session_id":"evidence-order-1"}'
```

Expected:

```text
ORD-001
SHIPPED
TRK987654321
UPS
September 11, 2026
```

---

# 28. Functional Test 2 — Customer Orders

```bash
agentcore invoke \
'{"prompt":"Show me my orders.","customer_id":"CUST-123","session_id":"customer-orders-test"}'
```

The agent should use the Gateway customer-order tool.

---

# 29. Functional Test 3 — Refund Initiation

First verify refund permission:

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerRefundProcessor
```

Then:

```bash
agentcore invoke \
'{"prompt":"I want to return my Kindle Paperwhite (ORD-002). Please initiate a refund.","customer_id":"CUST-123","session_id":"evidence-refund-1"}'
```

Expected behaviour:

```text
Gateway refund tool is called
Refund result is returned
```

Do not accept a response that merely claims a refund was created without tool-backed information.

---

# 30. Functional Test 4 — Refund Status

```bash
agentcore invoke \
'{"prompt":"Please check the refund status for my order ORD-002.","customer_id":"CUST-123","session_id":"evidence-refund-status"}'
```

Expected:

```text
Refund status/reference returned by refund processor
```

---

# 31. Functional Test 5 — Return Label

```bash
agentcore invoke \
'{"prompt":"Please get the return label for my order ORD-002.","customer_id":"CUST-123","session_id":"evidence-return-label"}'
```

Expected:

```text
Return-label information returned by the Gateway tool
```

---

# 32. Functional Test 6 — Knowledge Base / RAG

```bash
agentcore invoke \
'{"prompt":"What are the benefits of the Platinum loyalty tier?","customer_id":"CUST-123","session_id":"evidence-kb-1"}'
```

Expected product/support information should come from the Knowledge Base.

---

# 33. Functional Test 7 — Electronics Return Policy

```bash
agentcore invoke \
'{"prompt":"What is the return policy for electronics?","customer_id":"CUST-123","session_id":"evidence-kb-2"}'
```

Expected:

```text
15-day electronics return window
```

---

# 34. Functional Test 8 — Memory

## Session A

```bash
agentcore invoke \
'{"prompt":"Hi, I am Jane. I prefer concise responses.","customer_id":"CUST-123","session_id":"memory-evidence-A"}'
```

## Session B

Use a new session:

```bash
agentcore invoke \
'{"prompt":"Do you remember my name and communication preference?","customer_id":"CUST-123","session_id":"memory-evidence-B"}'
```

Expected:

```text
Jane
concise responses
```

The second invocation must use a different session ID but the same customer ID.

---

# 35. Functional Test 9 — Simple Memory Preference

Session A:

```bash
agentcore invoke \
'{"prompt":"My preferred delivery method is standard shipping.","customer_id":"CUST-999","session_id":"memory-test-A"}'
```

Session B:

```bash
agentcore invoke \
'{"prompt":"What is my preferred delivery method?","customer_id":"CUST-999","session_id":"memory-test-B"}'
```

Expected:

```text
standard shipping
```

---

# 36. Functional Test 10 — Loyalty / Code Interpreter

Use the completed loyalty calculation:

```bash
agentcore invoke \
'{"prompt":"I have 4250 loyalty points. My order total is $220. I am a Gold member and the order contains fresh groceries. Calculate my loyalty discount and tell me my final total, total savings, points earned, and remaining points.","customer_id":"CUST-123","session_id":"evidence-loyalty-1"}'
```

Expected calculation:

| Result | Expected |
|---|---:|
| Points redeemed | 4,000 |
| Points discount | $40 |
| Tier discount | $18 |
| Final total | $162 |
| Total savings | $58 |
| Points earned | 1,100 |
| Remaining points | 250 |

---

# 37. Functional Test 11 — Browser

Use:

```bash
agentcore invoke \
'{"prompt":"Use the browser to open https://www.udacity.com and tell me the title of the page.","customer_id":"CUST-123","session_id":"evidence-browser-1"}'
```

Expected:

```text
Current page title obtained through the browser tool
```

The answer should not simply be a guessed title.

---

# 38. Final Runtime Status

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

Run:

```bash
agentcore status
```

Expected:

```text
CustomerSupportAgent: Deployed - Runtime: READY
CustomerSupportMemory: Deployed
```

---

# 39. Final Runtime Logs

```bash
agentcore logs \
  --runtime CustomerSupportAgent \
  --since 30m \
  -n 100
```

---

# 40. CloudWatch Verification

Find AgentCore log groups:

```bash
aws logs describe-log-groups \
  --region us-east-1 \
  --query 'logGroups[].logGroupName'
```

Filter for AgentCore:

```bash
aws logs describe-log-groups \
  --region us-east-1 \
  --query 'logGroups[?contains(logGroupName, `agentcore`) || contains(logGroupName, `bedrock`)].logGroupName'
```

Use the AWS Console for the final CloudWatch metric-filter and alarm configuration.

Required alarm concept:

```text
Metric filter: ERROR
Alarm threshold: > 5 errors
Evaluation window: 5 minutes
```

---

# 41. Evidence Collection Checklist

Create a folder:

```bash
cd /workspaces/cd14763-project-starter
mkdir -p Test_Evidences
```

Suggested evidence files:

```text
Test_Evidences/
├── Evidence-1A-Project-Configuration.png
├── Evidence-1B-Memory-Implementation.png
├── Evidence-1C-KB-Loyalty-Implementation.png
├── Evidence-2A-AgentCore-Gateway.png
├── Evidence-2B-Gateway-Orders-Tools.png
├── Evidence-2C-Gateway-Refund-Tools.png
├── Evidence-3A-Knowledge-Base.png
├── Evidence-3B1-KB-Data-Source.png
├── Evidence-3B2-KB-Retrieval-Test.png
├── Evidence-4A-AgentCore-Memory.png
├── Evidence-4B-Memory-Strategies.png
├── Evidence-4C-Memory-Functional-Test.png
├── Evidence-5A-Order-Tracking.png
├── Evidence-6A-Refund-Initiation.png
├── Evidence-6B1-Refund-Status.png
├── Evidence-6B2-Return-Label.png
├── Evidence-7A-Loyalty-Calculation.png
├── Evidence-8A-Browser-Test.png
├── Evidence-9A-AgentCore-Deployment-Status.png
├── Evidence-9B-AgentCore-Runtime-Logs.png
├── Evidence-10A-Final-End-to-End-Test.png
└── Evidence-CloudWatch-Alarm.png
```

---

# 42. Evidence Rules

For every screenshot:

- Show the relevant AWS resource or terminal command.
- Keep text readable.
- Avoid unnecessary empty screen space.
- Do not expose credentials, access keys, tokens, or secrets.
- For functional tests, show both the command and the successful response.
- Prefer actual tool-backed results over explanatory text.
- Do not submit screenshots containing failed tests as successful evidence.
- Keep the evidence names consistent with the checklist.

---

# 43. Final Code Verification

From deployment application:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent
```

Run:

```bash
python -m py_compile main.py
```

Then:

```bash
wc -l main.py
```

Then:

```bash
grep -n "BedrockAgentCoreApp\|GATEWAY_URL\|KB_ID\|MEMORY_ID\|MemoryHook\|search_knowledge_base\|calculate_loyalty_discount\|MCPClient\|AgentCoreBrowser\|async def invoke" main.py
```

---

# 44. Final Deployment Verification

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

Run:

```bash
agentcore validate
```

Then:

```bash
agentcore status
```

Then:

```bash
agentcore logs --runtime CustomerSupportAgent --since 30m -n 100
```

---

# 45. Final Git Verification

Go to repository root:

```bash
cd /workspaces/cd14763-project-starter
```

Check:

```bash
git status
```

Review:

```bash
git diff
```

Check evidence folder:

```bash
ls -lah Test_Evidences
```

---

# 46. Commit Project 2 Work

Before committing, inspect what will be committed:

```bash
git status
```

Add only intended files:

```bash
git add README.md
git add Test_Evidences/
```

If the deployment project is intentionally part of the repository:

```bash
git add agentcore-deployment/
```

Review:

```bash
git status
```

Commit:

```bash
git commit -m "Complete Project 2 AI Support Agent"
```

Push:

```bash
git push origin main
```

---

# 47. Final GitHub Verification

```bash
git status
```

Expected:

```text
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

If the deployment project or evidence files are not intended for GitHub, do not add them.

---

# 48. Final Submission Checklist

## Implementation

- [ ] `starter/main.py` completed
- [ ] Deployment `main.py` completed
- [ ] `pyproject.toml` contains required dependencies
- [ ] `uv.lock` updated
- [ ] Python compilation passes

## AWS

- [ ] Order Lambda deployed
- [ ] Refund Lambda deployed
- [ ] Orders API Gateway configured
- [ ] AgentCore Gateway configured
- [ ] All 6 Gateway tools available
- [ ] Knowledge Base available
- [ ] Product catalog synchronized
- [ ] AgentCore Memory deployed
- [ ] Semantic strategy configured
- [ ] User preference strategy configured
- [ ] AgentCore Runtime READY

## Functional Tests

- [ ] Order tracking
- [ ] Customer order lookup
- [ ] Refund initiation
- [ ] Refund status
- [ ] Return label
- [ ] Knowledge Base RAG
- [ ] Memory across sessions
- [ ] Loyalty / Code Interpreter
- [ ] Browser

## Monitoring

- [ ] CloudWatch log group identified
- [ ] ERROR metric filter created
- [ ] Alarm configured for more than 5 errors in 5 minutes
- [ ] Alarm screenshot captured

## Evidence

- [ ] Code evidence
- [ ] Gateway evidence
- [ ] Gateway tool evidence
- [ ] Knowledge Base evidence
- [ ] Memory evidence
- [ ] Functional test screenshots
- [ ] Runtime status evidence
- [ ] CloudWatch evidence

## Submission

- [ ] README updated
- [ ] Evidence folder complete
- [ ] Reflection prepared: 200–400 words
- [ ] No secrets committed
- [ ] Git status reviewed
- [ ] Changes pushed to GitHub

---

# 49. Quick Restart Command Block

For a normal Codespace restart, use this shorter sequence:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
```

```bash
aws sts get-caller-identity
```

```bash
aws configure get region
```

```bash
agentcore --version
```

```bash
cd app/CustomerSupportAgent
```

```bash
uv sync
```

```bash
uv run python -c "import boto3, strands, bedrock_agentcore, mcp; print('Project 2 imports OK')"
```

```bash
python -m py_compile main.py
```

```bash
cd ../..
```

```bash
agentcore validate
```

```bash
agentcore status
```

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerSupportOrdersAPI
```

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerRefundProcessor
```

```bash
agentcore logs --runtime CustomerSupportAgent --since 30m -n 100
```

Then begin functional testing.

---

# 50. Important Troubleshooting Rules

## Runtime initialization timeout

Run:

```bash
agentcore logs --runtime CustomerSupportAgent --since 10m -n 300
```

Look for the first actual Python exception.

Do not randomly change dependencies before reading the logs.

## 403 Forbidden from Gateway

Verify:

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerSupportOrdersAPI
```

and:

```bash
aws iam get-role-policy \
  --role-name AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768 \
  --policy-name InvokeCustomerRefundProcessor
```

## Missing refund policy

Restore:

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

## Code import failure

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent
uv sync
python -m py_compile main.py
```

## After changing deployment code

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport
agentcore validate
agentcore deploy
agentcore status
```

Then test again.

---

# 51. Current Known AWS Resource Values

Keep these values together for Project 2 verification:

```text
Region:
us-east-1

Gateway:
CustomerSupportGateway

Gateway URL:
https://customersupportgateway-bi9wbwaick.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp

Knowledge Base:
CustomerSupportKB

Knowledge Base ID:
48BT8JT5TB

Memory:
CustomerSupportMemory

Memory ID:
CustomerSupportMemory-mXkuh4BqSK

Orders API:
CustomerSupportOrdersAPI

Orders API ID:
vyr6af1wee

Orders API stage:
prod

Order Lambda:
customer-order-tracker

Refund Lambda:
customer-refund-processor

AgentCore Runtime:
CustomerSupportAgent

Gateway IAM Role:
AmazonBedrockAgentCoreGatewayDefaultServiceRole1788949194768
```

---

# 52. Final Principle

**Do not recreate working AWS resources.**

Before creating or changing anything:

```bash
agentcore status
```

and verify the relevant AWS resource.

For troubleshooting:

```bash
agentcore logs --runtime CustomerSupportAgent --since 10m -n 300
```

For code:

```bash
python -m py_compile main.py
```

For dependencies:

```bash
uv sync
```

For deployment:

```bash
agentcore validate
agentcore deploy
agentcore status
```

For functional verification:

```bash
agentcore invoke '...'
```

This sequence keeps Project 2 reproducible, auditable, and ready for final rubric submission.
