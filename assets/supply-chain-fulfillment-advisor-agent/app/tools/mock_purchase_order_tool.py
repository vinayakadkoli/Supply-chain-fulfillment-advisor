"""Mock purchase order tool — returns open POs for a material filtered by delivery deadline.

In sandbox mode this returns deterministic mock data for MAT-1042.
In production this would be replaced by a live Purchase Order MCP tool.
"""
import logging
from datetime import date, timedelta
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Reference date anchor — PO ETA is 5 days from today in mock data
def _mock_eta() -> str:
    return (date.today() + timedelta(days=5)).isoformat()


MOCK_PO_DATA = {
    "MAT-1042": [
        {
            "id": "PO-4471",
            "supplier": "SUP-01",
            "quantity": 200.0,
            "eta_days_from_now": 5,
            "currency": "USD",
        }
    ]
}


@tool
def get_open_purchase_orders(material_id: str, delivery_deadline: str) -> dict:
    """Retrieve open purchase orders for a material that will arrive by the delivery deadline.

    Returns qualifying POs (ETA <= delivery_deadline), total inbound quantity,
    and the earliest ETA among qualifying POs.

    Args:
        material_id: The SAP material identifier (e.g. MAT-1042).
        delivery_deadline: ISO date string for the customer delivery deadline (e.g. 2026-05-28).

    Returns:
        dict with keys:
            - material_id: str
            - delivery_deadline: str
            - total_qualifying_qty: float
            - earliest_eta: str | None
            - pos: list of qualifying PO dicts (id, supplier, quantity, eta)
    """
    try:
        deadline = date.fromisoformat(delivery_deadline)
    except ValueError:
        logger.warning("M4.missed: invalid delivery_deadline format '%s'", delivery_deadline)
        return {
            "material_id": material_id,
            "delivery_deadline": delivery_deadline,
            "total_qualifying_qty": 0.0,
            "earliest_eta": None,
            "pos": [],
            "error": f"Invalid date format: {delivery_deadline}",
        }

    raw_pos = MOCK_PO_DATA.get(material_id, [])
    qualifying = []

    for po in raw_pos:
        eta = date.today() + timedelta(days=po["eta_days_from_now"])
        if eta <= deadline:
            qualifying.append({
                "id": po["id"],
                "supplier": po["supplier"],
                "quantity": po["quantity"],
                "eta": eta.isoformat(),
            })

    total_qty = sum(p["quantity"] for p in qualifying)
    earliest_eta = min((p["eta"] for p in qualifying), default=None)

    if qualifying:
        logger.info(
            "M4.achieved: PO scan complete — qualifying_inbound_qty=%s, earliest_eta=%s, pos_found=%s",
            total_qty, earliest_eta, len(qualifying)
        )
    else:
        logger.warning(
            "M4.missed: PO scan found no qualifying POs for %s before %s",
            material_id, delivery_deadline
        )

    return {
        "material_id": material_id,
        "delivery_deadline": delivery_deadline,
        "total_qualifying_qty": total_qty,
        "earliest_eta": earliest_eta,
        "pos": qualifying,
    }
