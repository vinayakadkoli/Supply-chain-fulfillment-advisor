"""Unit tests for the mock purchase order tool."""
import pytest
from datetime import date, timedelta
from app.tools.mock_purchase_order_tool import get_open_purchase_orders


def _deadline(days_from_now: int) -> str:
    return (date.today() + timedelta(days=days_from_now)).isoformat()


def test_qualifying_po_within_deadline():
    # PO ETA is 5 days, deadline is 7 days → should qualify
    result = get_open_purchase_orders.invoke({
        "material_id": "MAT-1042",
        "delivery_deadline": _deadline(7),
    })
    assert result["total_qualifying_qty"] == 200.0
    assert len(result["pos"]) == 1
    assert result["pos"][0]["id"] == "PO-4471"
    assert result["earliest_eta"] is not None


def test_po_not_qualifying_before_eta():
    # Deadline is 4 days, PO ETA is 5 days → should NOT qualify
    result = get_open_purchase_orders.invoke({
        "material_id": "MAT-1042",
        "delivery_deadline": _deadline(4),
    })
    assert result["total_qualifying_qty"] == 0.0
    assert result["pos"] == []
    assert result["earliest_eta"] is None


def test_unknown_material_no_pos():
    result = get_open_purchase_orders.invoke({
        "material_id": "MAT-UNKNOWN",
        "delivery_deadline": _deadline(7),
    })
    assert result["total_qualifying_qty"] == 0.0
    assert result["pos"] == []


def test_invalid_deadline_returns_error():
    result = get_open_purchase_orders.invoke({
        "material_id": "MAT-1042",
        "delivery_deadline": "not-a-date",
    })
    assert "error" in result
    assert result["total_qualifying_qty"] == 0.0
