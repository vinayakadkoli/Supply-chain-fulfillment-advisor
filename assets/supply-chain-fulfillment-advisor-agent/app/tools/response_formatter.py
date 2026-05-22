"""Response formatter — assembles the structured JSON payload for the React dashboard."""
import json
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

SUPPLIER_NODES = [
    {
        "id": "SUP-01",
        "type": "supplier",
        "label": "Chicago Supplier",
        "status": "healthy",
        "lat": 41.8781,
        "lon": -87.6298,
        "stockQty": None,
    }
]

CUSTOMER_NODE = {
    "id": "CUST-001",
    "type": "customer",
    "label": "Customer — US East Coast",
    "status": "neutral",
    "lat": 40.7549,
    "lon": -73.9840,
    "stockQty": None,
}


def build_payload(
    order_id: str,
    customer: str,
    material_id: str,
    ordered_qty: float,
    requested_delivery_date: str,
    inventory_result: dict,
    po_result: dict,
    gap_result: dict,
    agent_summary: str,
    scenario_tag: str = "SCN_01",
) -> dict:
    """Assemble the full JSON payload expected by the React dashboard.

    Args:
        order_id: Sales order ID.
        customer: Customer identifier.
        material_id: Material ID.
        ordered_qty: Ordered quantity.
        requested_delivery_date: Customer delivery deadline (ISO date).
        inventory_result: Output of get_material_stock tool.
        po_result: Output of get_open_purchase_orders tool.
        gap_result: Output of calculate_fulfillment_gap tool.
        agent_summary: Plain-language analyst summary from LLM.
        scenario_tag: Scenario label (default SCN_01).

    Returns:
        dict matching the dashboard JSON contract.
    """
    # Build supply chain nodes list (suppliers + inventory nodes + customer)
    inventory_nodes_for_map = []
    for n in inventory_result.get("nodes", []):
        inventory_nodes_for_map.append({
            "id": n["id"],
            "type": n["type"],
            "label": n["label"],
            "status": n["status"],
            "lat": n["lat"],
            "lon": n["lon"],
            "stockQty": n["stock"],
        })

    supply_chain_nodes = SUPPLIER_NODES + inventory_nodes_for_map + [CUSTOMER_NODE]

    payload = {
        "scenario_tag": scenario_tag,
        "status_badge": gap_result.get("status_badge", "ESCALATION_REQUIRED"),
        "order": {
            "id": order_id,
            "customer": customer,
            "material": material_id,
            "ordered_qty": ordered_qty,
            "requested_delivery_date": requested_delivery_date,
        },
        "inventory": {
            "total_available": inventory_result.get("total_available", 0.0),
            "nodes": inventory_result.get("nodes", []),
        },
        "fulfillment_gap": gap_result.get("gap", ordered_qty),
        "inbound_po": {
            "total_qualifying_qty": po_result.get("total_qualifying_qty", 0.0),
            "earliest_eta": po_result.get("earliest_eta"),
            "pos": po_result.get("pos", []),
        },
        "recommendation": {
            "class": gap_result.get("recommendation", "ESCALATE_PROCUREMENT"),
            "action_label": gap_result.get("action_label", "Raise Procurement Alert"),
            "summary": agent_summary,
        },
        "supply_chain_nodes": supply_chain_nodes,
    }
    return payload


def format_response(payload: dict, summary: str) -> str:
    """Format the final agent response string with summary + JSON payload delimiter."""
    return f"{summary}\n\n---JSON_PAYLOAD---\n{json.dumps(payload, indent=2)}"
