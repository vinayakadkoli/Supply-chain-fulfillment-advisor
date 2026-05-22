"""Unit tests for the fulfillment gap calculation tool — covers all 3 recommendation cases."""
import pytest
from datetime import date, timedelta
from app.tools.fulfillment_gap_tool import calculate_fulfillment_gap


def _date(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


# --- FULL_DELIVERY ---

def test_full_delivery_exact():
    result = calculate_fulfillment_gap.invoke({
        "ordered_qty": 320.0,
        "available_stock": 320.0,
        "inbound_po_qty": 0.0,
        "delivery_deadline": _date(7),
        "po_eta": "",
    })
    assert result["recommendation"] == "FULL_DELIVERY"
    assert result["status_badge"] == "ON_TRACK"
    assert result["gap"] == 0.0
    assert result["action_label"] == "Confirm Delivery"
    assert result["backorder_qty"] == 0.0


def test_full_delivery_surplus():
    result = calculate_fulfillment_gap.invoke({
        "ordered_qty": 300.0,
        "available_stock": 500.0,
        "inbound_po_qty": 0.0,
        "delivery_deadline": _date(7),
        "po_eta": "",
    })
    assert result["recommendation"] == "FULL_DELIVERY"
    assert result["gap"] == -200.0  # surplus


# --- PARTIAL_SHIPMENT_BACKORDER ---

def test_partial_shipment_when_po_covers_gap():
    result = calculate_fulfillment_gap.invoke({
        "ordered_qty": 500.0,
        "available_stock": 320.0,
        "inbound_po_qty": 200.0,
        "delivery_deadline": _date(7),
        "po_eta": _date(5),  # arrives 5 days, deadline 7 → in time
    })
    assert result["recommendation"] == "PARTIAL_SHIPMENT_BACKORDER"
    assert result["status_badge"] == "AT_RISK"
    assert result["gap"] == 180.0
    assert result["action_label"] == "Create Backorder"
    assert result["can_ship_now"] == 320.0


# --- ESCALATE_PROCUREMENT ---

def test_escalate_when_po_late():
    result = calculate_fulfillment_gap.invoke({
        "ordered_qty": 500.0,
        "available_stock": 320.0,
        "inbound_po_qty": 200.0,
        "delivery_deadline": _date(4),
        "po_eta": _date(5),  # PO arrives AFTER deadline → doesn't help
    })
    assert result["recommendation"] == "ESCALATE_PROCUREMENT"
    assert result["status_badge"] == "ESCALATION_REQUIRED"


def test_escalate_when_po_insufficient():
    result = calculate_fulfillment_gap.invoke({
        "ordered_qty": 500.0,
        "available_stock": 100.0,
        "inbound_po_qty": 50.0,
        "delivery_deadline": _date(7),
        "po_eta": _date(3),
    })
    assert result["recommendation"] == "ESCALATE_PROCUREMENT"
    assert result["gap"] == 400.0


def test_escalate_when_no_po():
    result = calculate_fulfillment_gap.invoke({
        "ordered_qty": 500.0,
        "available_stock": 320.0,
        "inbound_po_qty": 0.0,
        "delivery_deadline": _date(7),
        "po_eta": "",
    })
    assert result["recommendation"] == "ESCALATE_PROCUREMENT"
