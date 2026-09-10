# Project 2 Evidence Index

This document maps the repository evidence to the major Project 2 implementation and functional requirements.

## A. Application Configuration and Implementation

| Evidence | Purpose |
|---|---|
| `Evidence-1A-Main-Py-Config-Memory.jpg` | Main configuration and Memory setup |
| `Evidence-1AB-Main-Py-Config-Memory.jpg` | Additional configuration evidence |
| `Evidence-1B-Memory-Implementation.jpg` | MemoryHook implementation |
| `Evidence-1C-KB-Implementation.jpg` | Knowledge Base retrieval implementation |
| `Evidence-1C-Loyalty-Implementation.jpg` | Loyalty / Code Interpreter implementation |

## B. AgentCore Gateway and MCP

| Evidence | Purpose |
|---|---|
| `Evidence-2A-AgentCore-Gateway.jpg` | Gateway configuration |
| `Evidence-2B-Gateway-Orders-Tools.jpg` | Orders Gateway tools |
| `Evidence-2C-Gateway-Refund-Tools.jpg` | Refund Gateway tools |
| `New Tests/Test 4 - MCP API Tool.jpg` | Successful MCP API-backed tool invocation |
| `New Tests/Test 5 - MCP Lambda Tool.jpg` | Successful MCP Lambda-backed tool invocation |

The new MCP evidence is especially important because the previous review required successful invocations of at least two distinct Gateway-backed tools, including an API and a Lambda target.

## C. Knowledge Base / RAG

| Evidence | Purpose |
|---|---|
| `Evidence-3A-Knowledge-Base.jpg` | Knowledge Base configuration |
| `Evidence-3B1-KB-Data-Source.jpg` | S3 data source |
| `Evidence-3B2-KB-Retrieval-Test.jpg` | Knowledge Base retrieval |
| `New Tests/TEST 3 - KNOWLEDGE BASE (RAG).jpg` | Clean final RAG test |

The clean final RAG test is intended to address the previous review comment that the submitted RAG screenshot showed a failed Knowledge Base retrieval.

## D. Memory

Use the existing Memory strategy and implementation screenshots in `Test_Evidences/` to demonstrate:

- Memory resource configuration
- Semantic customer facts
- User preference strategy
- MemoryHook retrieval
- MemoryHook saving behaviour
- Cross-session memory

## E. Order Tracking

| Evidence | Purpose |
|---|---|
| `Evidence-5A-Order-Tracking.jpg` | Order tracking functional evidence |
| `Test_01_Order_Tracking_Passed.jpg` | Earlier passed order test |
| `test-order-001.jpg` | Supporting order test |

The live estimated delivery date should be taken from the current tool output rather than copied as a permanent hard-coded value into documentation.

## F. Refunds

| Evidence | Purpose |
|---|---|
| `Evidence-6A-Refund-Initiation.jpg` | Refund initiation |
| `Evidence-6B1-Refund-Status.jpg` | Refund status |
| `Evidence-6B2-Return-Label.jpg` | Return label |
| `Test_02_Refund_Processing_Passed.jpg` | Earlier passed refund test |

## G. Loyalty

| Evidence | Purpose |
|---|---|
| `Evidence-7A-Loyalty-Calculation.jpg` | Code Interpreter loyalty calculation |

The evidence should demonstrate the business rules for points redemption, tier discount, final total, savings, points earned, and remaining points.

## H. Browser

| Evidence | Purpose |
|---|---|
| `Evidence-8A-Browser-Test.jpg` | AgentCore Browser functional test |

## I. AgentCore Deployment and Runtime

| Evidence | Purpose |
|---|---|
| `Evidence-9A-AgentCore-Deployment-Status.jpg` | Runtime deployment/status |
| `Evidence-9B-AgentCore-Runtime-Logs.jpg` | Runtime logs |
| `Evidence-10A-Final-End-to-End-Test.jpg` | Final end-to-end evidence |

## J. CloudWatch

Recommended final evidence:

```text
Evidence-CloudWatch-Alarm.jpg
```

It should show:

```text
AgentCore Runtime log group
ERROR metric filter
Alarm threshold: more than 5 errors
Evaluation period: 5 minutes
```

Do not mark this evidence complete unless the screenshot is actually present in the repository.

## K. Previous Review Corrections

The previous submission required changes in two areas:

### RAG

The reviewer reported that the submitted RAG screenshot showed a failed Knowledge Base retrieval.

Correction:

```text
New Tests/TEST 3 - KNOWLEDGE BASE (RAG).jpg
```

This should show a clean successful Knowledge Base test using the electronics return-policy question.

### MCP

The reviewer required:

- Gateway failure handling
- Meaningful handling instead of silent crashing
- Successful Gateway-backed tool invocation
- At least two distinct Gateway tools
- One API-backed tool
- One Lambda-backed tool

Corrections:

```text
starter/main.py
```

contains explicit Gateway loading exception handling.

Functional evidence:

```text
New Tests/Test 4 - MCP API Tool.jpg
New Tests/Test 5 - MCP Lambda Tool.jpg
```

## L. Final Evidence Checklist

- [x] Main configuration
- [x] Memory implementation
- [x] Knowledge Base implementation
- [x] Loyalty implementation
- [x] Gateway configuration
- [x] Gateway Orders tools
- [x] Gateway Refund tools
- [x] Clean RAG test
- [x] MCP API test
- [x] MCP Lambda test
- [x] Order tracking
- [x] Refund initiation
- [x] Refund status
- [x] Return label
- [x] Loyalty
- [x] Browser
- [x] Deployment status
- [x] Runtime logs
- [x] Final end-to-end test
- [ ] CloudWatch alarm screenshot, if not yet captured

## Final Submission Rule

Before submission, make sure the evidence files in GitHub correspond to the final deployed code and final AWS configuration. Do not submit an old screenshot when a newer final test was created specifically to address reviewer feedback.
