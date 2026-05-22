"""Unit tests for the mock inventory tool."""
import pytest
from app.tools.mock_inventory_tool import get_material_stock


def test_get_material_stock_known_material():
    result = get_material_stock.invoke({"material_id": "MAT-1042"})
    assert result["material_id"] == "MAT-1042"
    assert result["total_available"] == 410.0  # 150+170+30+20+40
    assert len(result["nodes"]) == 5
    assert len(result["bottlenecks"]) == 3
    assert "DC01" in result["bottlenecks"]
    assert "DC02" in result["bottlenecks"]
    assert "DC03" in result["bottlenecks"]


def test_get_material_stock_healthy_nodes():
    result = get_material_stock.invoke({"material_id": "MAT-1042"})
    healthy = [n for n in result["nodes"] if n["status"] == "healthy"]
    critical = [n for n in result["nodes"] if n["status"] == "critical"]
    assert len(healthy) == 2  # P001, P002
    assert len(critical) == 3  # DC01, DC02, DC03


def test_get_material_stock_unknown_material():
    result = get_material_stock.invoke({"material_id": "MAT-UNKNOWN"})
    assert result["total_available"] == 0.0
    assert result["nodes"] == []
    assert "error" in result


def test_get_material_stock_node_fields():
    result = get_material_stock.invoke({"material_id": "MAT-1042"})
    for node in result["nodes"]:
        assert "id" in node
        assert "type" in node
        assert "label" in node
        assert "stock" in node
        assert "status" in node
        assert "lat" in node
        assert "lon" in node
