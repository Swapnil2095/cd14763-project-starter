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
└── PROJECT_2_REFLECTION.md
```

The deployment copy of `main.py` contains the completed Project 2 implementation.

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

The Gateway execution role is configured with permission to invoke the Orders API and refund Lambda.

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

The `MemoryHook` retrieves relevant customer context before invocation and saves completed customer/assistant interactions after invocation.

## Agent Implementation

The deployed application is:

```text
agentcore-deployment/customersupport/app/CustomerSupportAgent/main.py
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

### Loyalty Rules

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

## Functional Tests

### 1. Order Tracking

```bash
agentcore invoke '{"prompt":"Can you track order ORD-001?","customer_id":"CUST-123","session_id":"t1"}'
```

Expected information includes:

```text
Status: SHIPPED
Tracking: TRK987654321
Carrier: UPS
Estimated delivery: September 11, 2026
```

### 2. Refund Processing

```bash
agentcore invoke '{"prompt":"I want to return my Kindle Paperwhite (ORD-002). Please initiate a refund.","customer_id":"CUST-123","session_id":"t2"}'
```

Expected: the agent uses the Gateway refund tool and returns the refund processor result.

### 3. Knowledge Base / RAG

```bash
agentcore invoke '{"prompt":"What are the benefits of the Platinum loyalty tier?","customer_id":"CUST-123","session_id":"t3"}'
```

Expected: information retrieved from the Knowledge Base.

### 4. Long-Term Memory

```bash
agentcore invoke '{"prompt":"Hi, I am Jane. I prefer concise responses.","customer_id":"CUST-123","session_id":"s-A"}'
```

Then use a new session:

```bash
agentcore invoke '{"prompt":"Do you remember my name and communication preference?","customer_id":"CUST-123","session_id":"s-B"}'
```

Expected: the agent can recall the stored name and preference when memory retrieval has processed the previous interaction.

### 5. Loyalty / Code Interpreter

```bash
agentcore invoke '{"prompt":"I am a Gold member with 4250 points. Calculate my discount on a $150 standard order.","customer_id":"CUST-123","session_id":"t5"}'
```

Expected calculation:

```text
Points redeemed: 4,000
Points discount: $40
Tier discount: 10% of remaining $110 = $11
Final total: $99
Total savings: $51
Points earned: 150
Remaining points: 250
```

### 6. Browser

```bash
agentcore invoke '{"prompt":"Go to https://www.amazon.com and tell me the page title.","customer_id":"CUST-123","session_id":"t6"}'
```

Expected: the title is obtained through the live browser tool.

## CloudWatch Monitoring

The runtime writes operational logs to CloudWatch.

Final monitoring evidence should show:

- AgentCore Runtime log group
- `ERROR` metric filter
- Alarm configured for more than 5 errors in a 5-minute evaluation window

## Evidence

The `Test_Evidences/` folder contains screenshots for:

- Code/configuration
- Memory
- Knowledge Base
- Gateway
- Gateway tools
- Order tracking
- Refund processing
- Refund status
- Return label
- Loyalty calculation
- Browser
- AgentCore deployment
- Runtime logs
- Final end-to-end testing
- CloudWatch alarm

## Submission Checklist

- [ ] All required `main.py` sections completed
- [ ] Runtime deployed and READY
- [ ] Gateway and six tools verified
- [ ] Knowledge Base verified
- [ ] Memory strategies verified
- [ ] Cross-session memory test verified
- [ ] Order tracking verified
- [ ] Refund initiation verified
- [ ] Refund status verified
- [ ] Return label verified
- [ ] Loyalty calculation verified
- [ ] Browser verified
- [ ] CloudWatch alarm verified
- [ ] Evidence screenshots complete
- [ ] Reflection complete
- [ ] No credentials or secrets committed
- [ ] GitHub repository cleaned and reviewed
