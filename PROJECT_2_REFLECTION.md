# Project 2 Reflection

## Design Decision

A key design decision was to separate customer-specific operational actions from general product and policy knowledge. Customer and order operations are exposed through the AgentCore Gateway using MCP tools, while product and policy information is retrieved from the Bedrock Knowledge Base. This separation keeps customer-specific actions connected to backend systems while allowing the agent to use RAG for informational questions.

I also used AgentCore Memory hooks so customer facts and preferences can be retrieved before an interaction and saved after the response. The application distinguishes historical customer context from current operational data. For live order and refund questions, the agent is instructed to call the appropriate Gateway tool and treat the successful tool result as authoritative.

## Tool and Integration Choice

The AgentCore Gateway was used as the integration boundary for customer and order operations. MCP provides a consistent tool interface for the agent while the Gateway connects the agent to two different backend targets: an API Gateway based Orders target and a Lambda based Refund target.

The Knowledge Base was kept separate from those operational tools because product catalog and policy information is informational rather than customer-specific transactional data. AgentCore Code Interpreter was used for loyalty calculations so the business rules could be executed deterministically rather than relying only on natural-language arithmetic.

## Challenge and Solution

The main challenge was integrating several AgentCore services into one deployed Strands agent. The runtime needed the correct dependencies and configuration for Gateway, Memory, Knowledge Base, Code Interpreter, and Browser integrations.

The project also exposed two important integration issues during final verification. First, the deployed runtime initially could not retrieve Knowledge Base content because its execution role did not have the required `bedrock:Retrieve` permission. I identified the permission failure and added the least-privilege permission for the specific Knowledge Base resource. The deployed RAG test then succeeded.

Second, the MCP integration needed explicit Gateway failure handling and stronger live-data instructions. I added exception handling around Gateway tool loading and strengthened the system instructions so the agent does not treat historical memory as current order or refund data. I then verified the Gateway directly with successful calls to both an Orders API tool and a Refund Lambda tool.

Runtime initialization and deployment issues were diagnosed by reviewing AgentCore logs instead of changing the application blindly. The Python environment was synchronized, dependencies were verified, and the runtime was redeployed and tested again.

## Production Extension

For production, I would strengthen authentication and authorization, apply stricter least-privilege IAM policies, add structured logging and tracing, and introduce automated unit and integration tests.

Refund operations should include stronger request validation, idempotency controls, audit logging, authorization checks, and human escalation for sensitive cases. Configuration and secrets should be separated from application code.

I would also add CI/CD, automated regression tests for all Gateway tools, RAG evaluation tests, memory isolation tests, monitoring dashboards, alarms, rate limiting, retry and timeout policies, and clear fallback behaviour for unavailable tools.

The Gateway error-handling approach used in this project should be expanded into production-grade observability. Tool failures should produce structured logs and metrics so operations teams can distinguish dependency outages, authorization failures, validation errors, and application defects.

These changes would make the agent more secure, observable, reliable, and maintainable at production scale.
