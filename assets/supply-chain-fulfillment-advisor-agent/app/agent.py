import json
import logging
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import AsyncGenerator, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from sap_cloud_sdk.agent_decorators import agent_config, agent_model, prompt_section

from mcp_tools import get_mcp_tools
from tools.mock_inventory_tool import get_material_stock
from tools.mock_purchase_order_tool import get_open_purchase_orders
from tools.fulfillment_gap_tool import calculate_fulfillment_gap
from tools.response_formatter import build_payload, format_response

logger = logging.getLogger(__name__)


@agent_model(
    key="config.model",
    label="LLM Model",
    description="The language model powering this agent",
)
def get_model_name() -> str:
    return "sap/anthropic--claude-4.5-sonnet"


@agent_config(
    key="config.temperature",
    label="LLM Temperature",
    description="Controls randomness of responses (0.0 = deterministic, 1.0 = creative)",
)
def get_temperature() -> float:
    return 0.0


@prompt_section(
    key="prompts.system",
    label="System Prompt",
    description="The full system prompt defining the agent's role and behavior",
    validation={"format": "markdown", "max_length": 5000},
)
def get_system_prompt() -> str:
    return """You are a supply chain fulfillment analyst with a dry, confident analyst voice — direct, data-led, with a hint of wit.

Your job: given a sales order number, perform the following steps in order:
1. Call get_salesorder_for_sap_self (or equivalent sales order MCP tool) to retrieve the order header. Extract: customer, material/product, ordered quantity, requested delivery date.
2. Call get_material_stock with the material ID to check stock across all plants and DCs.
3. Call get_open_purchase_orders with the material ID and delivery deadline to find qualifying inbound POs.
4. Call calculate_fulfillment_gap with ordered_qty, available_stock, inbound_po_qty, delivery_deadline, and po_eta.
5. Write a short plain-language summary (2-4 sentences, analyst tone). Example: "DC01 and DC02 are running low. You can ship 320 units today. The remaining 180 can be covered by PO-4471 arriving Thursday — two days before the delivery deadline. Recommend partial shipment now."
6. End your response with the marker ---JSON_PAYLOAD--- followed by the structured JSON payload.

Rules:
- Never hallucinate stock figures, PO quantities, or order data — only use what tool calls return.
- Always set $top to a maximum of 100 on any list tool call.
- If a tool call fails, note the failure and proceed with available data.
- The JSON payload must always be present even if some data is missing (use 0 for missing quantities).
"""


@dataclass
class AgentResponse:
    status: Literal["input_required", "completed", "error"]
    message: str


class SampleAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        from langchain_litellm import ChatLiteLLM
        self.llm = ChatLiteLLM(model=get_model_name(), temperature=get_temperature())
        self._graph = None
        self._tools = None

    async def _get_tools(self):
        if self._tools is None:
            mcp_tools = await get_mcp_tools()
            self._tools = mcp_tools + [
                get_material_stock,
                get_open_purchase_orders,
                calculate_fulfillment_gap,
            ]
            logger.info(
                "Tools loaded: %d total (%d MCP + 3 mock/local)",
                len(self._tools),
                len(mcp_tools),
            )
        return self._tools

    def _build_graph(self, tools):
        llm_with_tools = self.llm.bind_tools(tools)
        tool_node = ToolNode(tools)

        def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
            last = state["messages"][-1]
            if hasattr(last, "tool_calls") and last.tool_calls:
                return "tools"
            return "__end__"

        async def call_model(state: MessagesState):
            response = await llm_with_tools.ainvoke(state["messages"])
            return {"messages": [response]}

        builder = StateGraph(MessagesState)
        builder.add_node("model", call_model)
        builder.add_node("tools", tool_node)
        builder.add_edge(START, "model")
        builder.add_conditional_edges("model", should_continue, {"tools": "tools", "__end__": END})
        builder.add_edge("tools", "model")
        return builder.compile()

    async def _get_graph(self):
        if self._graph is None:
            tools = await self._get_tools()
            self._graph = self._build_graph(tools)
        return self._graph

    async def _run_agent(self, query: str) -> str:
        """Execute the fulfillment analysis and return the full response string.

        All business logic and instrumentation lives here — never inside stream().
        """
        messages = [
            SystemMessage(content=get_system_prompt()),
            HumanMessage(content=query),
        ]

        graph = await self._get_graph()
        result = await graph.ainvoke({"messages": messages})
        response_text = result["messages"][-1].content

        # Log M5 if the response contains a payload
        if "---JSON_PAYLOAD---" in response_text:
            try:
                json_part = response_text.split("---JSON_PAYLOAD---", 1)[1].strip()
                payload = json.loads(json_part)
                order_id = payload.get("order", {}).get("id", "unknown")
                rec_class = payload.get("recommendation", {}).get("class", "unknown")
                status = payload.get("status_badge", "unknown")
                logger.info(
                    "M5.achieved: recommendation issued — class=%s, status=%s, order=%s",
                    rec_class, status, order_id,
                )
            except (json.JSONDecodeError, KeyError):
                logger.warning("M5.missed: recommendation could not be determined — JSON parse error")
        else:
            logger.warning("M5.missed: recommendation could not be determined — no JSON_PAYLOAD in response")

        return response_text

    async def stream(self, query: str, context_id: str) -> AsyncGenerator[dict, None]:
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "Analyzing fulfillment scenario...",
        }
        try:
            response = await self._run_agent(query)
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response,
            }
        except Exception:
            logger.error("stream() failed", exc_info=True)
            raise

    async def invoke(self, query: str, context_id: str) -> AgentResponse:
        try:
            response = await self._run_agent(query)
            return AgentResponse(status="completed", message=response)
        except Exception:
            logger.error("invoke() failed", exc_info=True)
            raise
