"""Integration test — full agent flow for SO-10042 with mocked LLM.

IBD_TESTING=1 is set by conftest.py, so mcp_tools.get_mcp_tools() returns
deterministic mock tools from mcp-mock.json — no network calls needed.
"""
import json
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage

DELIVERY_DATE = (date.today() + timedelta(days=7)).isoformat()
PO_ETA = (date.today() + timedelta(days=5)).isoformat()

MOCK_LLM_RESPONSE = f"""DC01, DC02, and DC03 are running critically low. You can ship 320 units today from P001 and P002. The remaining 180 units can be covered by PO-4471 arriving in 5 days — 2 days before the {DELIVERY_DATE} deadline. Recommend partial shipment now.

---JSON_PAYLOAD---
{{
  "scenario_tag": "SCN_01",
  "status_badge": "AT_RISK",
  "order": {{
    "id": "SO-10042",
    "customer": "CUST-001",
    "material": "MAT-1042",
    "ordered_qty": 500,
    "requested_delivery_date": "{DELIVERY_DATE}"
  }},
  "inventory": {{
    "total_available": 410,
    "nodes": [
      {{"id": "P001", "type": "plant", "stock": 150, "status": "healthy"}},
      {{"id": "P002", "type": "plant", "stock": 170, "status": "healthy"}},
      {{"id": "DC01", "type": "dc", "stock": 30, "status": "critical"}},
      {{"id": "DC02", "type": "dc", "stock": 20, "status": "critical"}},
      {{"id": "DC03", "type": "dc", "stock": 40, "status": "critical"}}
    ]
  }},
  "fulfillment_gap": 90,
  "inbound_po": {{
    "total_qualifying_qty": 200,
    "earliest_eta": "{PO_ETA}",
    "pos": [{{"id": "PO-4471", "qty": 200, "eta": "{PO_ETA}"}}]
  }},
  "recommendation": {{
    "class": "PARTIAL_SHIPMENT_BACKORDER",
    "action_label": "Create Backorder",
    "summary": "DC01, DC02, DC03 critically low. Ship 320 now; PO-4471 covers the rest."
  }},
  "supply_chain_nodes": []
}}"""


@pytest.mark.asyncio
async def test_agent_integration_so10042(add_agent_to_path):
    """End-to-end: agent processes SO-10042, returns PARTIAL_SHIPMENT_BACKORDER payload."""
    from agent import SampleAgent

    agent = SampleAgent()

    mock_llm = AsyncMock()
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content=MOCK_LLM_RESPONSE))
    agent.llm = mock_llm

    result = await agent.invoke(
        query="Analyze fulfillment for sales order SO-10042",
        context_id="test-session-001",
    )

    assert result.status == "completed"
    assert "---JSON_PAYLOAD---" in result.message

    json_part = result.message.split("---JSON_PAYLOAD---", 1)[1].strip()
    payload = json.loads(json_part)

    assert payload["status_badge"] == "AT_RISK"
    assert payload["order"]["id"] == "SO-10042"
    assert payload["recommendation"]["class"] == "PARTIAL_SHIPMENT_BACKORDER"
    assert payload["recommendation"]["action_label"] == "Create Backorder"
    assert payload["fulfillment_gap"] == 90


@pytest.mark.asyncio
async def test_agent_stream_yields_content(add_agent_to_path):
    """Stream method yields at least two chunks: processing + final result."""
    from agent import SampleAgent

    agent = SampleAgent()

    mock_llm = AsyncMock()
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content=MOCK_LLM_RESPONSE))
    agent.llm = mock_llm

    chunks = []
    async for chunk in agent.stream(
        query="Analyze fulfillment for sales order SO-10042",
        context_id="test-session-002",
    ):
        chunks.append(chunk)

    assert len(chunks) >= 2
    assert chunks[0]["is_task_complete"] is False
    assert chunks[-1]["is_task_complete"] is True
    assert "---JSON_PAYLOAD---" in chunks[-1]["content"]
