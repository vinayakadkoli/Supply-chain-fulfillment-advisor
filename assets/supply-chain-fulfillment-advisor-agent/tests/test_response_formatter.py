"""Unit tests for the response formatter."""
import json
import pytest
from datetime import date, timedelta
from app.tools.response_formatter import build_payload, format_response

INVENTORY_RESULT = {
    "material_id": "MAT-1042",
    "total_available": 410.0,
    "nodes": [
        {"id": "P001", "type": "plant", "label": "Plant Indianapolis", "stock": 150.0, "status": "healthy", "lat": 39.7684, "lon": -86.1581},
        {"id": "DC01", "type": "dc",    "label": "DC01 New York",      "stock": 30.0,  "status": "critical","lat": 40.7128, "lon": -74.0060},
    ],
    "bottlenecks": ["DC01"],
}

PO_RESULT = {
    "material_id": "MAT-1042",
    "delivery_deadline": "2026-05-28",
    "total_qualifying_qty": 200.0,
    "earliest_eta": "2026-05-26",
    "pos": [{"id": "PO-4471", "supplier": "SUP-01", "quantity": 200.0, "eta": "2026-05-26"}],
}

GAP_RESULT = {
    "gap": 90.0,
    "recommendation": "PARTIAL_SHIPMENT_BACKORDER",
    "status_badge": "AT_RISK",
    "action_label": "Create Backorder",
    "can_ship_now": 410.0,
    "backorder_qty": 90.0,
}


def test_build_payload_structure():
    payload = build_payload(
        order_id="SO-10042",
        customer="CUST-001",
        material_id="MAT-1042",
        ordered_qty=500.0,
        requested_delivery_date="2026-05-28",
        inventory_result=INVENTORY_RESULT,
        po_result=PO_RESULT,
        gap_result=GAP_RESULT,
        agent_summary="DC01 is low. Ship 410 now, backorder 90 from PO-4471.",
    )
    assert payload["scenario_tag"] == "SCN_01"
    assert payload["status_badge"] == "AT_RISK"
    assert payload["order"]["id"] == "SO-10042"
    assert payload["order"]["material"] == "MAT-1042"
    assert payload["inventory"]["total_available"] == 410.0
    assert payload["fulfillment_gap"] == 90.0
    assert payload["inbound_po"]["total_qualifying_qty"] == 200.0
    assert payload["recommendation"]["class"] == "PARTIAL_SHIPMENT_BACKORDER"
    assert payload["recommendation"]["action_label"] == "Create Backorder"


def test_build_payload_supply_chain_nodes_include_supplier_and_customer():
    payload = build_payload(
        order_id="SO-10042", customer="CUST-001", material_id="MAT-1042",
        ordered_qty=500.0, requested_delivery_date="2026-05-28",
        inventory_result=INVENTORY_RESULT, po_result=PO_RESULT, gap_result=GAP_RESULT,
        agent_summary="Test summary.",
    )
    node_types = {n["type"] for n in payload["supply_chain_nodes"]}
    assert "supplier" in node_types
    assert "customer" in node_types
    assert "plant" in node_types
    assert "dc" in node_types


def test_format_response_has_delimiter():
    payload = build_payload(
        order_id="SO-10042", customer="CUST-001", material_id="MAT-1042",
        ordered_qty=500.0, requested_delivery_date="2026-05-28",
        inventory_result=INVENTORY_RESULT, po_result=PO_RESULT, gap_result=GAP_RESULT,
        agent_summary="Summary here.",
    )
    response = format_response(payload, "Summary here.")
    assert "---JSON_PAYLOAD---" in response
    json_part = response.split("---JSON_PAYLOAD---", 1)[1].strip()
    parsed = json.loads(json_part)
    assert parsed["order"]["id"] == "SO-10042"
