# Project: Building a Production-Grade Customer Support AI Agent with Amazon Bedrock AgentCore

**Udacity — AWS AI Engineering Nanodegree — Course 2**

---

## Overview

This project builds a production-style AI customer support agent for a fictional Amazon store using Amazon Bedrock AgentCore, Strands Agents, AWS Lambda, API Gateway, Amazon Bedrock Knowledge Bases, AgentCore Memory, Code Interpreter, Browser, and an AgentCore Gateway using MCP.

The completed agent can:

- Answer product and policy questions using Retrieval-Augmented Generation (RAG)
- Retrieve customer and order information through Gateway tools
- Initiate refunds, check refund status, and obtain return labels
- Remember customer facts and preferences across sessions
- Calculate loyalty discounts using the AgentCore Code Interpreter
- Use a browser for live web information
- Run as a deployed AgentCore Runtime

---

## Learning Objectives

After completing this project you will be able to:

1. Deploy an AI agent to Amazon Bedrock AgentCore
2. Expose external AWS services through an AgentCore Gateway using MCP
3. Implement RAG with a Bedrock Knowledge Base
4. Implement long-term customer memory with AgentCore Memory
5. Use AgentCore Code Interpreter for deterministic calculations
6. Integrate AgentCore Browser for live web access
7. Monitor and troubleshoot an AgentCore Runtime with CloudWatch

---

## AWS Region

All project resources are deployed in:

```text
us-east-1
```

---

## Current Project Architecture

```text
Customer
   |
   v
AgentCore Runtime
   |
   +-- Strands Agent
   |     |
   |     +-- Knowledge Base tool
   |     +-- Loyalty / Code Interpreter tool
   |     +-- AgentCore Browser
   |     +-- AgentCore Memory hooks
   |     +-- MCP Gateway tools
   |
   +---------------------> CustomerSupportGateway
   |                              |
   |                              +--> Orders API Gateway
   |                              |       |
   |                              |       +--> customer-order-tracker Lambda
   |                              |
   |                              +--> customer-refund-processor Lambda
   |
   +---------------------> CustomerSupportKB
   |                              |
   |                              +--> S3 product_catalog.txt
   |
   +---------------------> CustomerSupportMemory
                                  |
                                  +--> customer_facts
                                  +--> customer_preferences
```

---

## Repository / Deployment Structure

The original starter repository remains the source project. The deployed AgentCore application is maintained in a separate deployment project so the starter files can be preserved for submission and comparison.

```text
cd14763-project-starter/
├── starter/
│   ├── main.py
│   └── lambda/
│       ├── order_tracker.py
│       ├── refund_processor.py
│       └── lambda_schema
│
├── Test_Evidences/
│   └── project evidence and screenshots
│
└── agentcore-deployment/
    └── customersupport/
        ├── agentcore/
        │   ├── agentcore.json
        │   └── ...
        └── app/
            └── CustomerSupportAgent/
                ├── main.py
                ├── pyproject.toml
                └── uv.lock
```

The deployed `main.py` contains the completed implementations for all starter TODO sections.

---

# Part 1 — AWS Infrastructure

## 1.1 Lambda Functions

Two Lambda functions are deployed:

| Function | Purpose |
|---|---|
| `customer-order-tracker` | Retrieves customer, customer-order, and order information |
| `customer-refund-processor` | Initiates refunds, checks refund status, and generates return-label information |

The order Lambda is exposed through API Gateway. The refund Lambda is invoked by the AgentCore Gateway.

---

## 1.2 Orders API Gateway

API Gateway REST API:

```text
Name: CustomerSupportOrdersAPI
API ID: vyr6af1wee
Stage: prod
Region: us-east-1
```

Configured routes:

```text
GET /orders/{order_id}
GET /customers/{customer_id}/orders
GET /customers/{customer_id}
```

The routes use Lambda proxy integration with `customer-order-tracker`.

---

## 1.3 AgentCore Gateway

Gateway:

```text
Name: CustomerSupportGateway
Region: us-east-1
Authorizer: NONE
```

Gateway MCP endpoint:

```text
https://customersupportgateway-bi9wbwaick.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp
```

### Orders target

```text
CustomerSupportOrdersTarget
```

Tools exposed:

- `get_customer`
- `get_customer_orders`
- `get_order`

### Refund target

```text
CustomerSupportRefundTarget
```

Tools exposed:

- `initiate_refund`
- `check_refund_status`
- `get_return_label`

The Gateway execution role has permissions for both the Orders API Gateway and the refund Lambda.

---

## 1.4 Knowledge Base

```text
Name: CustomerSupportKB
KB ID: 48BT8JT5TB
Region: us-east-1
```

Data source:

```text
CustomerSupportProductCatalog
```

The source document is `product_catalog.txt`, stored in S3 and synchronized into the Knowledge Base.

Embedding model:

```text
Amazon Titan Text Embeddings V2
```

The agent calls the Bedrock Knowledge Base Retrieve API through the `search_knowledge_base()` tool.

Example verification query:

```text
What is the return policy for electronics?
```

Expected knowledge-base result includes the 15-day electronics return window.

---

## 1.5 AgentCore Memory

```text
Name: CustomerSupportMemory
Memory ID: CustomerSupportMemory-mXkuh4BqSK
```

Configured strategies:

| Strategy | Namespace |
|---|---|
| `SEMANTIC` / `customer_facts` | `cs_agent/{actorId}/facts` |
| `USER_PREFERENCE` / `customer_preferences` | `cs_agent/{actorId}/preferences` |

The `MemoryHook` retrieves relevant memories before agent invocation and stores completed customer/assistant interactions after invocation.

---

# Part 2 — Agent Implementation

The completed application is located at:

```text
agentcore-deployment/customersupport/app/CustomerSupportAgent/main.py
```

The implementation includes:

### Section 1 — AgentCore application and configuration

- `BedrockAgentCoreApp`
- Gateway URL
- Knowledge Base ID
- Region
- Memory ID
- Amazon Nova model configuration
- `MemoryClient`
- Bedrock runtime client

### Section 2 — Memory

`MemoryHook` implements:

- Customer memory retrieval
- Namespace handling
- Customer context injection
- Saving completed support interactions

### Section 3 — Knowledge Base tool

`search_knowledge_base(query)`:

- Uses the Bedrock Knowledge Base Retrieve API
- Searches `CustomerSupportKB`
- Returns relevant retrieved text chunks
- Handles missing configuration and retrieval errors

### Section 4 — Loyalty calculation

`calculate_loyalty_discount(...)`:

- Uses AgentCore Code Interpreter
- Calculates loyalty-point redemption
- Applies tier discounts
- Calculates points earned
- Calculates remaining points
- Returns structured JSON results

Current loyalty rules implemented in the tool:

- Standard products: 1 point per dollar
- Device products: 2 points per dollar
- Fresh groceries: 5 points per dollar
- Silver tier: 0% tier discount
- Gold tier: 10% tier discount
- Platinum tier: 15% tier discount
- Points redeem in multiples of 500
- 100 points = $1 discount
- Maximum points redemption is 50% of the order total
- Tier discount is applied after the points discount
- Points earned are calculated from the full order total

### Section 5 — Main entrypoint

The deployed entrypoint:

- Extracts `prompt`, `customer_id`, and `session_id`
- Creates the memory hook
- Creates the AgentCore Browser
- Connects to the AgentCore Gateway through `MCPClient`
- Loads Gateway tools
- Builds the Strands Agent
- Invokes the agent asynchronously
- Returns the final response

---

# Part 3 — AgentCore Deployment

The deployment project was created with the AgentCore CLI using a Strands Python runtime.

```text
Project: customersupport
Runtime: CustomerSupportAgent
Build: CodeZip
Language: Python
Framework: Strands
Model provider: Bedrock
Protocol: HTTP
Network: PUBLIC
Runtime version: Python 3.14
```

Current deployed runtime:

```text
CustomerSupportAgent: READY
```

The deployed application uses the existing AWS resources described above rather than creating duplicate infrastructure.

Useful commands from the deployment project root:

```bash
cd /workspaces/cd14763-project-starter/agentcore-deployment/customersupport

agentcore status
agentcore logs --runtime CustomerSupportAgent --since 30m -n 100
agentcore invoke '{"prompt":"Hello, what can you help me with?","customer_id":"CUST-123","session_id":"test-1"}'
```

---

# Part 4 — Functional Testing

The following scenarios are used to verify the completed agent. Screenshots and terminal outputs are maintained in `Test_Evidences/`.

## Test 1 — Order Tracking

```bash
agentcore invoke '{"prompt":"What is the status of order ORD-001? Please give me the tracking number, carrier, and estimated delivery date.","customer_id":"CUST-123","session_id":"evidence-order-1"}'
```

Expected information:

- Order `ORD-001`
- Status `SHIPPED`
- Tracking `TRK987654321`
- Carrier `UPS`
- Estimated delivery `September 11, 2026`

## Test 2 — Refund Processing

```bash
agentcore invoke '{"prompt":"I want to return my Kindle Paperwhite (ORD-002). Please initiate a refund.","customer_id":"CUST-123","session_id":"evidence-refund-1"}'
```

Expected behaviour: the agent uses the Gateway refund tool and returns the refund result supplied by the refund processor.

## Test 3 — Knowledge Base / RAG

```bash
agentcore invoke '{"prompt":"What are the benefits of the Platinum loyalty tier?","customer_id":"CUST-123","session_id":"evidence-kb-1"}'
```

Expected information comes from the product/support Knowledge Base.

## Test 4 — Long-Term Memory

```bash
agentcore invoke '{"prompt":"Hi, I am Jane. I prefer concise responses.","customer_id":"CUST-123","session_id":"s-A"}'

agentcore invoke '{"prompt":"Do you remember my name and communication preference?","customer_id":"CUST-123","session_id":"s-B"}'
```

Expected: the second session can use stored customer facts/preferences when available.

## Test 5 — Loyalty Discount Calculation

```bash
agentcore invoke '{"prompt":"I have 4250 loyalty points. My order total is $220. I am a Gold member and the order contains fresh groceries. Calculate my loyalty discount and tell me my final total, total savings, points earned, and remaining points.","customer_id":"CUST-123","session_id":"evidence-loyalty-1"}'
```

For this scenario, the implemented calculation is expected to produce:

| Result | Expected |
|---|---:|
| Points redeemed | 4,000 |
| Points discount | $40 |
| Tier discount | $18 |
| Final total | $162 |
| Total savings | $58 |
| Points earned | 1,100 |
| Remaining points | 250 |

## Test 6 — Browser Tool

```bash
agentcore invoke '{"prompt":"Use the browser to open https://www.udacity.com and tell me the title of the page.","customer_id":"CUST-123","session_id":"evidence-browser-1"}'
```

Expected: the agent uses the live browser tool to obtain the current page title rather than guessing it.

---

# Part 5 — CloudWatch Monitoring

The deployed AgentCore Runtime writes operational logs to CloudWatch.

Recommended monitoring evidence:

1. Open **CloudWatch → Log Groups**.
2. Locate the AgentCore Runtime log group for `CustomerSupportAgent`.
3. Review successful and failed invocation logs.
4. Create a metric filter for `ERROR` entries.
5. Create an alarm for more than 5 errors in a 5-minute window.
6. Capture the alarm configuration for the project evidence package.

---

# Part 6 — Evidence / Submission Checklist

- [ ] Completed `starter/main.py` with all required TODO sections implemented
- [ ] Deployed `CustomerSupportAgent` runtime is READY
- [ ] AgentCore Gateway screenshot and configuration evidence
- [ ] Evidence for all 6 Gateway tools
- [ ] Knowledge Base configuration and retrieval evidence
- [ ] AgentCore Memory configuration and cross-session evidence
- [ ] Order tracking functional test
- [ ] Refund initiation functional test
- [ ] Refund status and return-label functional tests
- [ ] Loyalty / Code Interpreter functional test
- [ ] Browser functional test
- [ ] CloudWatch alarm configuration screenshot
- [ ] Final project reflection (200–400 words)

---

## Project Status

The core Project 2 implementation and AWS infrastructure are complete. Current work is focused on final functional verification, rubric evidence screenshots, CloudWatch monitoring evidence, and final submission preparation.
