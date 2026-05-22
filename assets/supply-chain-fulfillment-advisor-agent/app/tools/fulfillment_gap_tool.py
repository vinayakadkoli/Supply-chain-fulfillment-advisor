"""Fulfillment gap calculation tool — pure deterministic logic, no external calls.

Classifies a sales order scenario into one of three recommendation classes based
on ordered quantity, available stock, and qualifying inbound PO coverage.
"""
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def calculate_fulfillment_gap(
    ordered_qty: float,
    available_stock: float,
    inbound_po_qty: float,
    delivery_deadline: str,
    po_eta: str,
) -> dict:
    """Calculate the fulfillment gap and produce a delivery recommendation.

    Classification logic:
    - FULL_DELIVERY:              available_stock >= ordered_qty
    - PARTIAL_SHIPMENT_BACKORDER: available_stock < ordered_qty
                                   AND (available_stock + inbound_po_qty) >= ordered_qty
                                   AND po_eta <= delivery_deadline
    - ESCALATE_PROCUREMENT:       neither condition above is satisfied

    Args:
        ordered_qty: Quantity requested by the customer.
        available_stock: Total stock available across all plants and DCs.
        inbound_po_qty: Total qualifying inbound PO quantity (ETAs within deadline).
        delivery_deadline: ISO date string for the customer delivery deadline.
        po_eta: ISO date string for the earliest qualifying inbound PO ETA.

    Returns:
        dict with keys:
            - gap: float (ordered_qty - available_stock; negative means surplus)
            - recommendation: str (FULL_DELIVERY | PARTIAL_SHIPMENT_BACKORDER | ESCALATE_PROCUREMENT)
            - status_badge: str (ON_TRACK | AT_RISK | ESCALATION_REQUIRED)
            - action_label: str (human-readable button label)
            - can_ship_now: float (units shippable immediately)
            - backorder_qty: float (units needing backorder if partial)
    """
    gap = ordered_qty - available_stock
    can_ship_now = min(available_stock, ordered_qty)

    # Determine if inbound PO arrives in time
    po_in_time = (po_eta and po_eta <= delivery_deadline) if po_eta else False

    if available_stock >= ordered_qty:
        recommendation = "FULL_DELIVERY"
        status_badge = "ON_TRACK"
        action_label = "Confirm Delivery"
        backorder_qty = 0.0
    elif (available_stock + inbound_po_qty) >= ordered_qty and po_in_time:
        recommendation = "PARTIAL_SHIPMENT_BACKORDER"
        status_badge = "AT_RISK"
        action_label = "Create Backorder"
        backorder_qty = gap
    else:
        recommendation = "ESCALATE_PROCUREMENT"
        status_badge = "ESCALATION_REQUIRED"
        action_label = "Raise Procurement Alert"
        backorder_qty = gap

    logger.info(
        "M3.achieved: gap calculated — ordered=%s, available=%s, gap=%s, bottlenecks=calculated",
        ordered_qty, available_stock, gap
    )
    logger.info(
        "M5.achieved: recommendation issued — class=%s, status=%s, order=pending",
        recommendation, status_badge
    )

    return {
        "gap": gap,
        "recommendation": recommendation,
        "status_badge": status_badge,
        "action_label": action_label,
        "can_ship_now": can_ship_now,
        "backorder_qty": backorder_qty,
    }
