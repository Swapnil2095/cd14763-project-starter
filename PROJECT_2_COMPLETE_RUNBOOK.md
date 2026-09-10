# Project 2 Complete Command Runbook

This runbook contains the final verification, evidence, deployment, and Git commands for Project 2.

## 1. Repository and Environment

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

Set the required region if necessary:

```bash
aws configure set region us-east-1
```

## 2. Deployment Project

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport

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

## 4. Synchronize Starter Code

The deployed application copy should be synchronized to the starter copy before final submission:

```bash
cd /workspaces/cd14763-project-starter

cp agentcore-deployment/customersupport/app/CustomerSupportAgent/main.py starter/main.py

python -m py_compile starter/main.py
```

Verify the Gateway error handling:

```bash
grep -n -A25 -B5 "Gateway connected successfully" starter/main.py
```

Verify the live-data instructions:

```bash
grep -n -A25 -B5 "LIVE DATA AND MEMORY PRIORITY" starter/main.py
```

## 5. Lambda Verification

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

## 6. Orders API Verification

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

Direct order test:

```bash
curl -s "https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod/orders/ORD-001"
```

Customer orders:

```bash
curl -s "https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod/customers/CUST-123/orders"
```

Customer profile:

```bash
curl -s "https://vyr6af1wee.execute-api.us-east-1.amazonaws.com/prod/customers/CUST-123"
```

## 7. Gateway IAM Verification

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

## 8. Knowledge Base Verification

```bash
aws bedrock-agent-runtime retrieve \
  --knowledge-base-id 48BT8JT5TB \
  --retrieval-query '{"text":"What is the return policy for electronics?"}' \
  --region us-east-1
```

Expected: Knowledge Base results containing the electronics return policy.

S3 verification:

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

Expected active strategies:

```text
SEMANTIC
USER_PREFERENCE
```

## 10. Deployment Verification

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport

agentcore validate
agentcore status
```

If the application has changed and needs redeployment:

```bash
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

Inspect the first actual exception before changing dependencies or configuration.

## 12. Final RAG Evidence Test

Use a clean customer and session so unrelated memory does not appear:

```bash
agentcore invoke '{"prompt":"Use the search_knowledge_base tool to answer this question. What is the return policy for electronics? Base your answer only on the information returned by the Knowledge Base. Report only the electronics return window, required item condition, accessories requirement, and Prime member return benefit. Do not mention any customer, order, refund, return-label, memory, or other information.","customer_id":"CUST-RAG-CLEAN-EVIDENCE-001","session_id":"rag-clean-evidence-001"}'
```

Evidence filename:

```text
Test_Evidences/New Tests/TEST 3 - KNOWLEDGE BASE (RAG).jpg
```

The evidence should clearly show the question and a successful Knowledge Base-based answer.

## 13. Final MCP API Evidence Test

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent

uv run python - <<'PY'
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamable_http_client

GATEWAY_URL = "https://customersupportgateway-bi9wbwaick.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"

def create_transport():
    return streamable_http_client(GATEWAY_URL)

client = MCPClient(create_transport)

with client:
    tools = client.list_tools_sync()
    print("Gateway tools loaded:", len(tools))
    for tool in tools:
        print("-", getattr(tool, "tool_name", getattr(tool, "name", "unknown")))

    result = client.call_tool_sync(
        "CustomerSupportOrdersTarget___get_order",
        {"order_id": "ORD-001"}
    )

    print("\nMCP API TOOL RESULT")
    print(result)
PY
```

Evidence filename:

```text
Test_Evidences/New Tests/Test 4 - MCP API Tool.jpg
```

Required evidence characteristics:

```text
CustomerSupportOrdersTarget___get_order
ORD-001
Successful result
SHIPPED
UPS
TRK987654321
isError: False
```

## 14. Final MCP Lambda Evidence Test

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent

uv run python - <<'PY'
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamable_http_client

GATEWAY_URL = "https://customersupportgateway-bi9wbwaick.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"

def create_transport():
    return streamable_http_client(GATEWAY_URL)

client = MCPClient(create_transport)

with client:
    tools = client.list_tools_sync()
    print("Gateway tools loaded:", len(tools))

    result = client.call_tool_sync(
        "CustomerSupportRefundTarget___initiate_refund",
        {
            "order_id": "ORD-001",
            "amount": 89.99
        }
    )

    print("\nMCP LAMBDA TOOL RESULT")
    print(result)
PY
```

Evidence filename:

```text
Test_Evidences/New Tests/Test 5 - MCP Lambda Tool.jpg
```

Required evidence characteristics:

```text
CustomerSupportRefundTarget___initiate_refund
statusCode: 200
status: APPROVED
amount: 89.99
isError: False
```

## 15. Gateway Error Handling Evidence

```bash
cd /workspaces/cd14763-project-starter

grep -n -A25 -B5 "Gateway connected successfully" starter/main.py
```

The output should show:

```text
try:
    gateway_tools = gateway_client.list_tools_sync()
    ...
except TimeoutError:
    ...
except ConnectionError:
    ...
except Exception as exc:
    ...
```

The evidence demonstrates that Gateway loading failures are explicitly handled and logged.

## 16. Order Tracking Test

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport

agentcore invoke '{"prompt":"Can you track order ORD-001?","customer_id":"CUST-123","session_id":"final-order-tracking-001"}'
```

## 17. Refund Initiation Test

```bash
agentcore invoke '{"prompt":"I want to request a refund for order ORD-001. Please use the Gateway refund tool to initiate the refund for the full order amount of $89.99. Give me the refund ID, status, amount, and refund timeline.","customer_id":"CUST-123","session_id":"final-refund-initiation-001"}'
```

## 18. Refund Status Test

```bash
agentcore invoke '{"prompt":"Please check the refund status for my order ORD-002.","customer_id":"CUST-123","session_id":"final-refund-status-001"}'
```

## 19. Return Label Test

```bash
agentcore invoke '{"prompt":"Please get the return label for my order ORD-002.","customer_id":"CUST-123","session_id":"final-return-label-001"}'
```

## 20. Memory Test

Session A:

```bash
agentcore invoke '{"prompt":"Hi, I am Jane. I prefer concise responses.","customer_id":"CUST-MEMORY-EVIDENCE-001","session_id":"memory-A-final"}'
```

Session B:

```bash
agentcore invoke '{"prompt":"Do you remember my name and communication preference?","customer_id":"CUST-MEMORY-EVIDENCE-001","session_id":"memory-B-final"}'
```

## 21. Loyalty Test

```bash
agentcore invoke '{"prompt":"I am a Gold member with 4250 points. Calculate my discount on a $150 standard order.","customer_id":"CUST-LOYALTY-EVIDENCE-001","session_id":"loyalty-final-001"}'
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

## 22. Browser Test

```bash
agentcore invoke '{"prompt":"Go to https://www.amazon.com and tell me the page title.","customer_id":"CUST-BROWSER-EVIDENCE-001","session_id":"browser-final-001"}'
```

## 23. CloudWatch Verification

List log groups:

```bash
aws logs describe-log-groups \
  --region us-east-1 \
  --query 'logGroups[].logGroupName'
```

Identify the AgentCore runtime log group in the AWS Console.

Final monitoring evidence should show:

```text
Metric filter: ERROR
Alarm: error count > 5
Evaluation period: 5 minutes
```

Recommended screenshot:

```text
Test_Evidences/Evidence-CloudWatch-Alarm.jpg
```

Only mark this item complete after the screenshot has actually been captured and committed.

## 24. Final Code Verification

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport/app/CustomerSupportAgent

python -m py_compile main.py
```

Starter copy:

```bash
cd /workspaces/cd14763-project-starter

python -m py_compile starter/main.py
```

## 25. Final Git Verification

```bash
cd /workspaces/cd14763-project-starter

git status
git diff
```

Check that there are no credentials, tokens, temporary archives, or local caches.

## 26. Final Commit and Push

```bash
cd /workspaces/cd14763-project-starter

git add README.md PROJECT_2_COMPLETE_RUNBOOK.md PROJECT_2_REFLECTION.md PROJECT_2_EVIDENCE_INDEX.md Test_Evidences/ starter/ agentcore-deployment/

git status

git commit -m "Finalize Project 2 submission and evidence"

git push origin main

git status
```

Expected:

```text
nothing to commit, working tree clean
```

## 27. Final Submission Review

Before submitting to Udacity:

```text
1. Runtime status is READY
2. Gateway has six tools
3. RAG test succeeds
4. MCP API test succeeds
5. MCP Lambda test succeeds
6. Order tracking succeeds
7. Refund initiation succeeds
8. Refund status succeeds
9. Return label succeeds
10. Memory test succeeds
11. Loyalty calculation succeeds
12. Browser test succeeds
13. Runtime logs are available
14. CloudWatch alarm evidence is present
15. All required screenshots are in Test_Evidences
16. README and runbook are updated
17. Reflection is present
18. GitHub main branch contains the final code
19. No credentials are committed
20. Working tree is clean
```
