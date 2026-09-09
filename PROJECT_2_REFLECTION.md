# Project 2 Reflection

## Design Decision

A key design decision was to separate customer-specific operational actions from general product and policy knowledge. Customer and order operations are exposed through the AgentCore Gateway using MCP tools, while product and policy information is retrieved from the Bedrock Knowledge Base. This separation keeps customer-specific actions connected to backend systems while allowing the agent to use RAG for informational questions. I also used AgentCore Memory hooks so customer facts and preferences can be retrieved before an interaction and saved after the response.

## Challenge and Solution

The main challenge was integrating several AgentCore services into one deployed Strands agent. The runtime needed the correct dependencies and configuration for Gateway, Memory, Knowledge Base, Code Interpreter, and Browser integrations. Runtime initialization issues were diagnosed by reviewing AgentCore logs instead of changing the application blindly. I resolved the dependency/configuration problems, synchronized the Python environment and lock file, redeployed the runtime, verified the Gateway permissions, and tested each integration separately before running the final end-to-end scenarios.

## Production Extension

For production, I would strengthen authentication and authorization, apply stricter least-privilege IAM policies, add structured logging and tracing, and introduce automated unit and integration tests. Refund operations should include validation, idempotency controls, audit logging, and human escalation for sensitive cases. Configuration and secrets should be separated from application code. I would also add CI/CD, automated regression tests, monitoring dashboards, alarms, rate limiting, and clear fallback behaviour for unavailable tools. These changes would make the agent more secure, observable, reliable, and maintainable at production scale.
