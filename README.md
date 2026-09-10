# Project 2 — Production-Style Customer Support AI Agent with Amazon Bedrock AgentCore

**Udacity AWS AI Engineering Nanodegree — Course 2**

## Overview

This project implements a production-style AI customer support agent for a fictional Amazon store using Amazon Bedrock AgentCore and Strands Agents.

The completed agent can:

- Answer product and policy questions using Retrieval-Augmented Generation (RAG)
- Retrieve customer and order information through an AgentCore Gateway using MCP
- Initiate refunds, check refund status, and obtain return-label information
- Remember customer facts and preferences across sessions
- Calculate loyalty discounts using AgentCore Code Interpreter
- Use AgentCore Browser for live web information
- Run as a deployed Amazon Bedrock AgentCore Runtime

## Architecture

```text
Customer
   |
   v
CustomerSupportAgent
   |
   +-- Strands Agent
   |     +-- CustomerSupportKB
   |     +-- Loyalty / Code Interpreter
   |     +-- AgentCore Browser
   |     +-- AgentCore Memory
   |     +-- AgentCore Gateway
   |
   +--> CustomerSupportGateway
   |      +--> CustomerSupportOrdersTarget
   |      |      +--> CustomerSupportOrdersAPI
   |      |             +--> customer-order-tracker Lambda
   |      |
   |      +--> CustomerSupportRefundTarget
   |             +--> customer-refund-processor Lambda
   |
   +--> CustomerSupportKB
   |      +--> S3 product_catalog.txt
   |
   +--> CustomerSupportMemory
          +--> SEMANTIC / customer facts
          +--> USER_PREFERENCE / customer preferences
```

## Repository Structure

```text
cd14763-project-starter/
├── starter/
│   ├── main.py
│   ├── product_catalog.txt
│   ├── pyproject.toml
│   └── lambda/
│       ├── order_tracker.py
│       ├── refund_processor.py
│       └── lambda_schema
│
├── agentcore-deployment/
│   └── customersupport/
│       ├── agentcore/
│       └── app/
│           └── CustomerSupportAgent/
│               ├── main.py
│               ├── pyproject.toml
│               └── uv.lock
│
├── Test_Evidences/
├── PROJECT_2_COMPLETE_RUNBOOK.md
├── PROJECT_2_REFLECTION.md
└── PROJECT_2_EVIDENCE_INDEX.md
```

The deployment copy of `main.py` contains the completed Project 2 implementation. The root `starter/main.py` is synchronized with the deployed application copy.

## AWS Region

```text
us-east-1
```

## AWS Resources

### Lambda

| Resource | Purpose |
|---|---|
| `customer-order-tracker` | Customer, customer-order, and order lookup |
| `customer-refund-processor` | Refund initiation, refund status, and return-label operations |

### API Gateway

```text
Name: CustomerSupportOrdersAPI
API ID: vyr6af1wee
Stage: prod
```

Routes:

```text
GET /orders/{order_id}
GET /customers/{customer_id}/orders
GET /customers/{customer_id}
```

### AgentCore Gateway

```text
Name: CustomerSupportGateway
Authorizer: NONE
```

Targets:

```text
CustomerSupportOrdersTarget
CustomerSupportRefundTarget
```

Gateway tools:

```text
get_customer
get_customer_orders
get_order
initiate_refund
check_refund_status
get_return_label
```

The Gateway execution role is configured to invoke the Orders API and refund Lambda.

The deployed application includes explicit Gateway tool-loading error handling. Gateway failures are logged and the agent is instructed not to silently substitute memory data for current order or refund information.

### Knowledge Base

```text
Name: CustomerSupportKB
ID: 48BT8JT5TB
```

Source:

```text
S3 product_catalog.txt
```

Embedding model:

```text
Amazon Titan Text Embeddings V2
```

The application uses the Bedrock Knowledge Base Retrieve API through `search_knowledge_base()`.

The runtime execution role includes permission to perform `bedrock:Retrieve` against this Knowledge Base.

### AgentCore Memory

```text
Name: CustomerSupportMemory
ID: CustomerSupportMemory-mXkuh4BqSK
```

Strategies:

| Strategy | Namespace |
|---|---|
| `SEMANTIC` | `cs_agent/{actorId}/facts` |
| `USER_PREFERENCE` | `cs_agent/{actorId}/preferences` |

The `MemoryHook` retrieves relevant customer context before invocation and saves completed customer and assistant interactions after invocation.

## Agent Implementation

The deployed application is:

```text
agentcore-deployment/customersupport/app/CustomerSupportAgent/main.py
```

The synchronized starter application is:

```text
starter/main.py
```

It implements:

1. `BedrockAgentCoreApp`
2. AWS resource configuration
3. `BedrockModel`
4. `MemoryClient`
5. Memory namespace discovery
6. `MemoryHook`
7. Knowledge Base retrieval
8. Loyalty calculation through Code Interpreter
9. AgentCore Browser
10. AgentCore Gateway MCP integration
11. Main AgentCore entrypoint

## Live Data and Memory Handling

The agent is explicitly instructed that:

- Current order questions must use the appropriate Gateway order tool.
- Refund initiation must use the appropriate Gateway refund tool.
- Existing refund and return-label questions must use the appropriate Gateway refund tool.
- Memory is historical or personalized context and is not treated as current order or refund system data.
- The agent must not claim that a tool or API failed unless it actually attempted the corresponding call and received an error.
- If a required Gateway call fails, the response must clearly state that the live system could not be accessed.
- Successful Gateway results are treated as authoritative live data.

This behaviour was added to address the final MCP review requirement and reduce stale-memory responses for live operational questions.

## Loyalty Rules

The implemented calculation uses:

- Standard products: 1 point per dollar
- Device products: 2 points per dollar
- Fresh groceries: 5 points per dollar
- Silver: 0% tier discount
- Gold: 10% tier discount
- Platinum: 15% tier discount
- Redemption in multiples of 500 points
- 100 points = $1 discount
- Maximum redemption = 50% of order total
- Tier discount is applied after the points discount
- Points earned are calculated from the full order total

### Example

For a Gold member with 4,250 points and a $150 standard order:

```text
Points redeemed: 4,000
Points discount: $40
Remaining order amount: $110
Tier discount: $11
Final total: $99
Total savings: $51
Points earned: 150
Remaining points: 250
```

## Deployment

The deployment project uses the AgentCore CLI with a Python/Strands runtime.

```text
Project: customersupport
Runtime: CustomerSupportAgent
Build: CodeZip
Protocol: HTTP
Network: PUBLIC
Runtime: Python 3.14
Model provider: Bedrock
```

Useful commands:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport

agentcore validate
agentcore status
agentcore logs --runtime CustomerSupportAgent --since 30m -n 100
```

## Final Functional Evidence Tests

### Test 1. Order Tracking

```bash
agentcore invoke '{"prompt":"Can you track order ORD-001?","customer_id":"CUST-123","session_id":"final-order-tracking-001"}'
```

Expected live order information includes:

```text
Order: ORD-001
Status: SHIPPED
Tracking: TRK987654321
Carrier: UPS
```

The estimated delivery date is generated by the order-tracker Lambda and should be treated as live output rather than a hard-coded README value.

Recommended evidence:

```text
Test_Evidences/Evidence-5A-Order-Tracking.jpg
```

### Test 2. Refund Initiation

```bash
agentcore invoke '{"prompt":"I want to request a refund for order ORD-001. Please use the Gateway refund tool to initiate the refund for the full order amount of $89.99. Give me the refund ID, status, amount, and refund timeline.","customer_id":"CUST-123","session_id":"final-refund-initiation-001"}'
```

Expected:

- Gateway refund tool is called
- Refund processor returns a refund result
- Refund ID is reported
- Status and amount are reported
- Refund timeline is reported

Recommended evidence:

```text
Test_Evidences/Evidence-6A-Refund-Initiation.jpg
```

### Test 3. Knowledge Base / RAG

Use a clean customer/session so unrelated memory does not appear in the evidence:

```bash
agentcore invoke '{"prompt":"Use the search_knowledge_base tool to answer this question. What is the return policy for electronics? Base your answer only on the information returned by the Knowledge Base. Report only the electronics return window, required item condition, accessories requirement, and Prime member return benefit. Do not mention any customer, order, refund, return-label, memory, or other information.","customer_id":"CUST-RAG-CLEAN-EVIDENCE-001","session_id":"rag-clean-evidence-001"}'
```

Expected Knowledge Base information includes:

```text
Electronics return window: 15 days from delivery date
```

The response should be based on Knowledge Base retrieval and should not contain unrelated customer memory.

Recommended final evidence:

```text
Test_Evidences/New Tests/TEST 3 - KNOWLEDGE BASE (RAG).jpg
```

This clean RAG test directly addresses the previous review concern about a failed Knowledge Base retrieval screenshot.

### Test 4. MCP API Gateway Tool

The test must demonstrate a successful Gateway-backed API operation.

Run from the deployment application directory:

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

Expected:

```text
CustomerSupportOrdersTarget___get_order
ORD-001
SHIPPED
UPS
TRK987654321
isError: False
```

Recommended evidence:

```text
Test_Evidences/New Tests/Test 4 - MCP API Tool.jpg
```

### Test 5. MCP Lambda Gateway Tool

Run:

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

Expected:

```text
CustomerSupportRefundTarget___initiate_refund
statusCode: 200
status: APPROVED
amount: 89.99
isError: False
```

Recommended evidence:

```text
Test_Evidences/New Tests/Test 5 - MCP Lambda Tool.jpg
```

This test demonstrates the second distinct Gateway target and Lambda-backed operation required by the MCP rubric.

## Gateway Error Handling Evidence

The application includes explicit handling for Gateway tool loading failures:

```python
with gateway_client:
    try:
        gateway_tools = gateway_client.list_tools_sync()
        tools.extend(gateway_tools)

        logger.info(
            "Gateway connected successfully. Loaded %d tools.",
            len(gateway_tools),
        )

    except TimeoutError:
        logger.exception("Gateway tool loading timed out")

    except ConnectionError:
        logger.exception("Gateway connection failed")

    except Exception as exc:
        logger.exception(
            "Gateway tool loading failed: %s", exc
        )
```

Supporting code evidence can be captured with:

```bash
cd /workspaces/cd14763-project-starter

grep -n -A25 -B5 "Gateway connected successfully" starter/main.py
```

The required behaviour is that a Gateway problem is logged clearly instead of causing a silent failure.

## Test 6. Long-Term Memory

Session A:

```bash
agentcore invoke '{"prompt":"Hi, I am Jane. I prefer concise responses.","customer_id":"CUST-MEMORY-EVIDENCE-001","session_id":"memory-A-final"}'
```

Session B:

```bash
agentcore invoke '{"prompt":"Do you remember my name and communication preference?","customer_id":"CUST-MEMORY-EVIDENCE-001","session_id":"memory-B-final"}'
```

Expected: the agent can recall the stored name and preference after the memory processing pipeline has stored the first interaction.

Recommended evidence:

```text
Test_Evidences/Evidence-4B-Memory-Strategies.jpg
```

## Test 7. Loyalty / Code Interpreter

```bash
agentcore invoke '{"prompt":"I am a Gold member with 4250 points. Calculate my discount on a $150 standard order.","customer_id":"CUST-LOYALTY-EVIDENCE-001","session_id":"loyalty-final-001"}'
```

Expected:

```text
Points redeemed: 4,000
Points discount: $40
Tier discount: $11
Final total: $99
Total savings: $51
Points earned: 150
Remaining points: 250
```

Recommended evidence:

```text
Test_Evidences/Evidence-7A-Loyalty-Calculation.jpg
```

## Test 8. Browser

```bash
agentcore invoke '{"prompt":"Go to https://www.amazon.com and tell me the page title.","customer_id":"CUST-BROWSER-EVIDENCE-001","session_id":"browser-final-001"}'
```

Expected: the title is obtained through the live browser tool.

Recommended evidence:

```text
Test_Evidences/Evidence-8A-Browser-Test.jpg
```

## CloudWatch Monitoring

The final project should have monitoring evidence showing:

- AgentCore Runtime log group
- `ERROR` metric filter
- Alarm configured for more than 5 errors in a 5-minute evaluation window

Recommended evidence filename:

```text
Test_Evidences/Evidence-CloudWatch-Alarm.jpg
```

Do not claim this evidence is complete until the screenshot is actually captured and committed to the repository.

## Evidence Organization

The repository contains implementation and functional evidence covering:

- Main application configuration
- Memory implementation and strategies
- Knowledge Base implementation and retrieval
- AgentCore Gateway
- Gateway Orders tools
- Gateway Refund tools
- Order tracking
- Refund initiation
- Refund status
- Return label
- Loyalty calculation
- Browser
- AgentCore deployment
- Runtime logs
- Final end-to-end testing

The `Test_Evidences/New Tests/` directory contains the newer evidence specifically prepared to address the previous RAG and MCP review requirements.

See:

```text
PROJECT_2_EVIDENCE_INDEX.md
```

for the evidence-to-rubric mapping.

## Submission Checklist

### Implementation

- [x] Required `main.py` sections completed
- [x] `BedrockAgentCoreApp` configured at module level
- [x] Async `@app.entrypoint` implemented
- [x] AgentCore Runtime deployed
- [x] Gateway integrated through MCP
- [x] Six Gateway tools available
- [x] Knowledge Base retrieval implemented
- [x] Memory hooks implemented
- [x] Code Interpreter loyalty calculation implemented
- [x] Browser integrated
- [x] Gateway failure handling implemented
- [x] Live order/refund priority over historical memory implemented

### AWS Resources

- [x] Order tracker Lambda deployed
- [x] Refund processor Lambda deployed
- [x] Orders API Gateway configured
- [x] AgentCore Gateway configured
- [x] Gateway Orders target ready
- [x] Gateway Refund target ready
- [x] Knowledge Base available
- [x] Knowledge Base data source synchronized
- [x] AgentCore Memory configured
- [x] Runtime deployed

### Functional Evidence

- [x] Order tracking evidence
- [x] Refund initiation evidence
- [x] Refund status evidence
- [x] Return-label evidence
- [x] Clean RAG evidence
- [x] MCP API evidence
- [x] MCP Lambda evidence
- [x] Memory evidence
- [x] Loyalty evidence
- [x] Browser evidence
- [x] Deployment evidence
- [x] Runtime log evidence
- [ ] CloudWatch alarm screenshot, if not yet captured

### Documentation

- [x] README updated
- [x] Complete command runbook updated
- [x] Reflection included
- [x] Evidence index included
- [ ] Final GitHub status checked after uploading all evidence
- [ ] Final submission re-run after all evidence is uploaded

## Security

Do not commit:

- AWS access keys
- Secret keys
- Session tokens
- API secrets
- Private credentials
- Local credential files
- Temporary archives containing credentials

Before final push:

```bash
git status
git diff
```

Confirm the working tree contains only intended project files and evidence.

## Final Git Commands

From the repository root:

```bash
cd /workspaces/cd14763-project-starter

git status
git add README.md PROJECT_2_COMPLETE_RUNBOOK.md PROJECT_2_REFLECTION.md PROJECT_2_EVIDENCE_INDEX.md Test_Evidences/ starter/ agentcore-deployment/
git status
git commit -m "Finalize Project 2 submission and evidence"
git push origin main
git status
```

Expected final state:

```text
nothing to commit, working tree clean
```
