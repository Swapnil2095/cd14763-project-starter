"""
Customer Support AI Agent — Starter Code
==========================================
Your task is to complete this file by implementing all sections marked
with # TODO comments.

Reference the step-by-step solution files and INSTRUCTIONS.md for guidance.
Do NOT copy the solution directly — work through each section yourself.

Run locally (after filling in config values):
  uv run main.py '{"prompt": "Hello", "customer_id": "CUST-123", "session_id": "s1"}'

Deploy to AgentCore:
  agentcore deploy

Invoke deployed agent:
  agentcore invoke '{"prompt": "Hello", "customer_id": "CUST-123", "session_id": "s1"}'
"""

# ── Imports ───────────────────────────────────────────────────────────────────
# These imports are provided. Do not remove them.
from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamable_http_client
import argparse, json
import os, asyncio, boto3
from strands.hooks import (
    HookProvider, AfterInvocationEvent, HookRegistry, MessageAddedEvent,
)
import logging
import uuid
from typing import Dict
from bedrock_agentcore.tools.code_interpreter_client import code_session
from strands_tools.browser import AgentCoreBrowser


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("CSAI_Agent")

# ── TODO 1 — App Initialisation ───────────────────────────────────────────────
# Create a BedrockAgentCoreApp instance.
# This registers the ASGI server for AgentCore deployment.
# There must be exactly one instance per deployment.
#
# Hint: app = BedrockAgentCoreApp()

# TODO: Create the BedrockAgentCoreApp instance
app = BedrockAgentCoreApp()  # Replace this line


# Suppress interactive tool-consent prompts (required in headless deployments).
os.environ["BYPASS_TOOL_CONSENT"] = "true"


# ── TODO 2 — Configuration ────────────────────────────────────────────────────
# Replace the placeholder strings with your actual AWS resource values.
# You collected these in Part 1 of the INSTRUCTIONS.
#
# GATEWAY_URL format: https://<alias>.gateway.bedrock-agentcore.<region>.amazonaws.com/mcp
# KB_ID       format: 10-character alphanumeric string from the KB console
# REGION:     your AWS region, e.g. "us-east-1"
# MEMORY_ID   format: shown in the AgentCore Memory console

GATEWAY_URL = "https://customersupportgateway-bi9wbwaick.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
KB_ID = "48BT8JT5TB"
REGION = "us-east-1"
MEMORY_ID = "CustomerSupportMemory-mXkuh4BqSK"


# ── TODO 3 — Model and Clients ────────────────────────────────────────────────
# Create:
#   1. A BedrockModel using model_id "global.amazon.nova-2-lite-v1:0"
#   2. A MemoryClient with region_name=REGION
#   3. A boto3 client for the "bedrock-agent-runtime" service in REGION
#
# Hint: model = BedrockModel(model_id=model_id)

model_id = "global.amazon.nova-2-lite-v1:0"

# TODO: Create the BedrockModel instance
#model = None  # Replace this line

# TODO: Create the MemoryClient instance
#memory_client = None  # Replace this line

# TODO: Create the boto3 bedrock-agent-runtime client
#_bedrock_runtime = None  # Replace this line

model = BedrockModel(model_id=model_id)

memory_client = MemoryClient(region_name=REGION)

_bedrock_runtime = boto3.client(
    "bedrock-agent-runtime",
    region_name=REGION,
)


# ── TODO 4 — Namespace Helper ─────────────────────────────────────────────────
# Implement get_namespaces() to return a dict mapping strategy type to
# namespace template string.
#
# Steps:
#   1. Call mem_client.get_memory_strategies(memory_id) to get strategy list
#   2. Return a dict: { strategy["type"]: strategy["namespaces"][0] for each strategy }
#
# Example output:
#   { "SEMANTIC": "cs_agent/{actorId}/facts",
#     "USER_PREFERENCE": "cs_agent/{actorId}/preferences" }

def get_namespaces(mem_client: MemoryClient, memory_id: str) -> Dict:
    """Return a dict mapping strategy type to namespace template string."""
    strategies = mem_client.get_memory_strategies(memory_id)

    namespaces = {}

    for strategy in strategies:
        strategy_type = strategy["type"]

        # Current API format
        templates = strategy.get("namespaceTemplates")

        # Legacy API format
        if not templates:
            templates = strategy.get("namespaces")

        if templates:
            namespaces[strategy_type] = templates[0]

    return namespaces


# ── TODO 5 — Memory Hook ──────────────────────────────────────────────────────
# Implement MemoryHook, a HookProvider subclass that adds long-term memory.
#
# The class needs:
#   __init__(self, actor_id, session_id, memory_client, memory_id)
#     — store all four as instance attributes
#     — call get_namespaces() and store the result as self.namespaces
#
#   retrieve_customer_context(self, event: MessageAddedEvent)
#     — only runs for plain-text user messages (not tool results)
#     — for each strategy namespace, call memory_client.retrieve_memories(
#          memory_id, namespace (formatted with actorId), query, top_k=5)
#     — collect non-empty memory texts tagged with their strategy type
#     — if any memories found, prepend them to the user message as:
#          "Customer Context:\n<memories>\n\n<original_message>"
#
#   save_support_interaction(self, event: AfterInvocationEvent)
#     — walk the message list backwards to find the last plain-text user
#       query and the last assistant response
#     — call memory_client.create_event(memory_id, actor_id, session_id,
#          messages=[(customer_query, "USER"), (agent_response, "ASSISTANT")])
#
#   register_hooks(self, registry: HookRegistry)
#     — register retrieve_customer_context on MessageAddedEvent
#     — register save_support_interaction on AfterInvocationEvent

class MemoryHook(HookProvider):
    """Long-term memory hook for the customer support agent."""

    def __init__(
        self,
        actor_id: str,
        session_id: str,
        memory_client: MemoryClient,
        memory_id: str,
    ):
        self.actor_id = actor_id
        self.session_id = session_id
        self.memory_client = memory_client
        self.memory_id = memory_id
        self.namespaces = get_namespaces(memory_client, memory_id)

    def retrieve_customer_context(self, event: MessageAddedEvent):
        """Retrieve relevant memories and prepend them to the user message."""
        try:
            messages = event.agent.messages

            if not messages:
                return

            last_message = messages[-1]

            if last_message.get("role") != "user":
                return

            content = last_message.get("content", [])

            if not isinstance(content, list):
                return

            text_parts = []

            for block in content:
                if isinstance(block, dict) and "text" in block:
                    text_parts.append(block["text"])

            if not text_parts:
                return

            user_query = "\n".join(text_parts).strip()

            if not user_query:
                return

            memories = []

            for strategy_type, namespace_template in self.namespaces.items():
                namespace = namespace_template.replace(
                    "{actorId}",
                    self.actor_id,
                )

                try:
                    results = self.memory_client.retrieve_memories(
                        self.memory_id,
                        namespace,
                        user_query,
                        top_k=5,
                    )

                    for result in results or []:
                        memory_text = None

                        if isinstance(result, dict):
                            memory_text = (
                                result.get("content", {}).get("text")
                                if isinstance(result.get("content"), dict)
                                else result.get("text")
                            )

                        if memory_text:
                            memories.append(
                                f"[{strategy_type}] {memory_text}"
                            )

                except Exception as exc:
                    logger.warning(
                        "Memory retrieval failed for %s: %s",
                        strategy_type,
                        exc,
                    )

            if memories:
                context_text = (
                    "Customer Context:\n"
                    + "\n".join(memories)
                    + "\n\n"
                    + user_query
                )

                last_message["content"] = [
                    {"text": context_text}
                ]

        except Exception as exc:
            logger.warning("Customer memory retrieval failed: %s", exc)

    def save_support_interaction(self, event: AfterInvocationEvent):
        """Save the completed turn to memory after the agent responds."""
        try:
            messages = event.agent.messages

            customer_query = None
            agent_response = None

            for message in reversed(messages):
                role = message.get("role")
                content = message.get("content", [])

                if not isinstance(content, list):
                    continue

                text_parts = []

                for block in content:
                    if isinstance(block, dict) and "text" in block:
                        text_parts.append(block["text"])

                text = "\n".join(text_parts).strip()

                if not text:
                    continue

                if customer_query is None and role == "user":
                    customer_query = text

                if agent_response is None and role == "assistant":
                    agent_response = text

                if customer_query and agent_response:
                    break

            if customer_query and agent_response:
                self.memory_client.create_event(
                    memory_id=self.memory_id,
                    actor_id=self.actor_id,
                    session_id=self.session_id,
                    messages=[
                        (customer_query, "USER"),
                        (agent_response, "ASSISTANT"),
                    ],
                )

        except Exception as exc:
            logger.warning("Saving customer memory failed: %s", exc)

    def register_hooks(self, registry: HookRegistry) -> None:  # type: ignore
        """Register both memory callbacks."""
        registry.add_callback(
            MessageAddedEvent,
            self.retrieve_customer_context,
        )

        registry.add_callback(
            AfterInvocationEvent,
            self.save_support_interaction,
        )


# ── TODO 6 — Knowledge Base Tool ─────────────────────────────────────────────
# Implement search_knowledge_base(query) using the @tool decorator.
#
# Steps:
#   1. Guard: if KB_ID is empty return "Knowledge base not configured."
#   2. Call _bedrock_runtime.retrieve(
#          knowledgeBaseId=KB_ID,
#          retrievalQuery={"text": query}
#      )
#   3. Extract resp["retrievalResults"]; return a message if empty
#   4. Join the text chunks with "\n---\n" and return the result
#
# The docstring is the tool description — the model uses it to decide when
# to call this tool, so keep it clear and accurate.

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the Amazon product catalog and support knowledge base.
    Use this for product specifications, return policies, warranty
    information, loyalty program details, and order status definitions.

    Args:
        query: The question or topic to search for

    Returns:
        Relevant information retrieved from the knowledge base
    """
    if not KB_ID:
        return "Knowledge base not configured."

    try:
        response = _bedrock_runtime.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={
                "text": query
            },
        )

        results = response.get("retrievalResults", [])

        if not results:
            return "No relevant information found in the knowledge base."

        chunks = []

        for result in results:
            content = result.get("content", {})

            if isinstance(content, dict):
                text = content.get("text", "")
            else:
                text = str(content)

            if text:
                chunks.append(text)

        if not chunks:
            return "No relevant information found in the knowledge base."

        return "\n---\n".join(chunks)

    except Exception as exc:
        logger.warning("Knowledge base retrieval failed: %s", exc)
        return f"Knowledge base search failed: {exc}"


# ── TODO 7 — Loyalty Discount Tool (Code Interpreter) ────────────────────────
# Implement calculate_loyalty_discount() using the @tool decorator.
#
# The tool must:
#   1. Build a self-contained Python code string that:
#        • Defines earn_rates: {"standard": 1, "device": 2, "fresh": 5}
#        • Defines tier_rates: {"Silver": 0.00, "Gold": 0.10, "Platinum": 0.15}
#        • Calculates points_redeemed (floor to nearest 500, cap at 50% of order)
#        • Calculates tier_discount (applied to subtotal after points)
#        • Calculates final_total, total_savings, points_earned, remaining_points
#        • Prints a JSON result dict
#   2. Execute the code with code_session(REGION).invoke("executeCode", {...})
#      using language="python" and clearContext=True
#   3. Return the first result event as a JSON string
#   4. Include a fallback that computes only the tier discount if the
#      Code Interpreter is unavailable

@tool
def calculate_loyalty_discount(
    loyalty_points: int,
    tier: str,
    order_total: float,
    product_category: str = "standard",
) -> str:
    """
    Calculate the loyalty discount for a customer order using the
    AgentCore Code Interpreter. Runs exact arithmetic in a secure sandbox.

    Args:
        loyalty_points:   Customer's current points balance
        tier:             Customer tier — Silver, Gold, or Platinum
        order_total:      Order total in USD
        product_category: standard, device, or fresh

    Returns:
        Full discount breakdown and final price
    """

    code = f"""
import json
import math

loyalty_points = {int(loyalty_points)}
tier = {json.dumps(tier)}
order_total = {float(order_total)}
product_category = {json.dumps(product_category)}

earn_rates = {{
    "standard": 1,
    "device": 2,
    "fresh": 5
}}

tier_rates = {{
    "Silver": 0.00,
    "Gold": 0.10,
    "Platinum": 0.15
}}

# Redeem points only in multiples of 500.
# 100 points = $1, so 500 points = $5.
max_redeemable_dollars = order_total * 0.50
max_redeemable_points = int(max_redeemable_dollars * 100)

points_redeemed = min(
    (loyalty_points // 500) * 500,
    (max_redeemable_points // 500) * 500
)

points_discount = points_redeemed / 100.0

subtotal_after_points = order_total - points_discount

tier_discount_pct = tier_rates.get(tier, 0.00)
tier_discount = subtotal_after_points * tier_discount_pct

final_total = subtotal_after_points - tier_discount

total_savings = order_total - final_total

points_earned = int(
    math.floor(
        order_total * earn_rates.get(product_category, 1)
    )
)

remaining_points = loyalty_points - points_redeemed

result = {{
    "points_redeemed": points_redeemed,
    "points_discount": round(points_discount, 2),
    "tier_discount_pct": round(tier_discount_pct * 100, 2),
    "tier_discount": round(tier_discount, 2),
    "final_total": round(final_total, 2),
    "total_savings": round(total_savings, 2),
    "points_earned": points_earned,
    "remaining_points": remaining_points
}}

print(json.dumps(result))
"""

    try:
        with code_session(REGION) as code_client:
            result = code_client.invoke(
                "executeCode",
                {
                    "language": "python",
                    "code": code,
                    "clearContext": True,
                },
            )

        if isinstance(result, dict):
            stream = result.get("stream")

            if stream is not None:
                for event in stream:
                    if isinstance(event, dict):
                        return json.dumps(event)

            return json.dumps(result)

        return json.dumps(result)

    except Exception as e:
        logger.warning(
            "Code Interpreter unavailable, using fallback: %s",
            e,
        )

        tier_rates = {
            "Silver": 0.00,
            "Gold": 0.10,
            "Platinum": 0.15,
        }

        tier_discount_pct = tier_rates.get(tier, 0.00)
        tier_discount = order_total * tier_discount_pct
        final_total = order_total - tier_discount

        fallback = {
            "points_redeemed": 0,
            "tier_discount_pct": tier_discount_pct * 100,
            "final_total": round(final_total, 2),
            "total_savings": round(tier_discount, 2),
            "points_earned": int(
                order_total
                * {
                    "standard": 1,
                    "device": 2,
                    "fresh": 5,
                }.get(product_category, 1)
            ),
            "remaining_points": loyalty_points,
        }

        return json.dumps(fallback)


# ── TODO 8 — Agent Entrypoint ─────────────────────────────────────────────────
# Implement the invoke() function decorated with @app.entrypoint.
#
# Steps:
#   1. Extract user_input, actor_id, and session_id from the payload
#      (generate a UUID if session_id is missing)
#   2. Instantiate MemoryHook for this actor/session
#   3. Instantiate AgentCoreBrowser(region=REGION)
#   4. Build the tools list: [search_knowledge_base, calculate_loyalty_discount,
#                              agent_core_browser.browser]
#   5. Connect to the Gateway via MCPClient, load gateway_tools, extend tools list
#   6. Create and invoke the Agent with all tools, hooks, and system_prompt
#   7. Return the text from the first content block of the response
#   8. Handle exceptions gracefully

@app.entrypoint
async def invoke(payload, context=None):
    """
    Main handler called by AgentCore for every incoming request.

    Expected payload keys:
      prompt      (str, required) — the customer's message
      customer_id (str, optional) — unique customer identifier
      session_id  (str, optional) — session identifier; generated if absent
    """

    try:
        user_input = payload.get("prompt", "")
        actor_id = payload.get("customer_id", "anonymous")
        session_id = payload.get("session_id") or str(uuid.uuid4())

        if not user_input:
            return "Please provide a customer support question."

        # Create the long-term memory hook for this customer/session.
        memory_hook = MemoryHook(
            actor_id=actor_id,
            session_id=session_id,
            memory_client=memory_client,
            memory_id=MEMORY_ID,
        )

        # Create the AgentCore browser tool.
        agent_core_browser = AgentCoreBrowser(region=REGION)

        # Start with the tools implemented directly by this application.
        tools = [
            search_knowledge_base,
            calculate_loyalty_discount,
            agent_core_browser.browser,
        ]

        # Connect to the AgentCore Gateway and discover its MCP tools.
        gateway_client = MCPClient(
            lambda: streamable_http_client(GATEWAY_URL)
        )

        with gateway_client:
            gateway_tools = gateway_client.list_tools_sync()
            tools.extend(gateway_tools)

            system_prompt = """
You are a helpful customer support AI agent.

You help customers with:
- order tracking and order information
- refunds and return labels
- product information
- return policies
- refund timelines
- loyalty points and loyalty discounts
- general customer support questions

Use the available tools whenever they provide authoritative or
customer-specific information.

Use the knowledge base for product catalog information, return policies,
refund timelines, loyalty program details, and order status definitions.

Use the Gateway tools for customer-specific order information and refund
operations.

Use the loyalty discount tool when an exact loyalty calculation is required.

Use the browser tool when current information from a live web page is
needed.

Use customer memory when relevant to personalize the response.

Be concise, accurate, and transparent. Do not invent customer information,
order information, refund details, or policies.
"""

            agent = Agent(
                model=model,
                tools=tools,
                hooks=[memory_hook],
                system_prompt=system_prompt,
            )

            response = await agent.invoke_async(user_input)

            if hasattr(response, "content") and response.content:
                first_block = response.content[0]

                if isinstance(first_block, dict):
                    return first_block.get("text", str(first_block))

                if hasattr(first_block, "text"):
                    return first_block.text

                return str(first_block)

            return str(response)

    except Exception as exc:
        logger.exception("Agent invocation failed")
        return f"Sorry, I encountered an error while processing your request: {exc}"


# ── CLI entry point (do not modify) ──────────────────────────────────────────
def main():
    """Run one invocation from the command line for local testing."""
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=str)
    args = parser.parse_args()
    response = asyncio.run(invoke(json.loads(args.payload)))
    print(response)


if __name__ == "__main__":
    app.run()
    # Uncomment the line below and comment app.run() for local CLI testing:
    # main()
