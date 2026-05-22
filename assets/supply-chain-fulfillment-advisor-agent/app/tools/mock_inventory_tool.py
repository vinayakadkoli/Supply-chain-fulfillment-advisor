"""Mock inventory tool — returns material stock data across plants and DCs.

In sandbox mode this returns deterministic mock data for MAT-1042.
In production this would be replaced by a live Material Stock MCP tool.
"""
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Low-stock threshold: any node below this quantity is flagged as a bottleneck
LOW_STOCK_THRESHOLD = 50

# Mock stock dataset keyed by material_id
MOCK_STOCK_DATA = {
    "MAT-1042": [
        {"id": "P001", "type": "plant",  "label": "Plant Indianapolis",  "stock": 150, "lat": 39.7684, "lon": -86.1581},
        {"id": "P002", "type": "plant",  "label": "Plant Columbus",       "stock": 170, "lat": 39.9612, "lon": -82.9988},
        {"id": "DC01", "type": "dc",     "label": "DC01 New York",        "stock": 30,  "lat": 40.7128, "lon": -74.0060},
        {"id": "DC02", "type": "dc",     "label": "DC02 Baltimore",       "stock": 20,  "lat": 39.2904, "lon": -76.6122},
        {"id": "DC03", "type": "dc",     "label": "DC03 Washington DC",   "stock": 40,  "lat": 38.9072, "lon": -77.0369},
    ]
}


@tool
def get_material_stock(material_id: str) -> dict:
    """Retrieve available stock for a material across all plants and distribution centers.

    Returns per-node stock quantities, total available stock, and a list of
    bottleneck nodes (nodes whose stock is below the low-stock threshold).

    Args:
        material_id: The SAP material identifier (e.g. MAT-1042).

    Returns:
        dict with keys:
            - material_id: str
            - total_available: float (sum across all nodes)
            - nodes: list of node dicts with id, type, label, stock, status, lat, lon
            - bottlenecks: list of node IDs flagged as critical
    """
    nodes_raw = MOCK_STOCK_DATA.get(material_id, [])
    if not nodes_raw:
        logger.warning("M2.missed: inventory query returned no data for %s — material not found in mock dataset", material_id)
        return {
            "material_id": material_id,
            "total_available": 0.0,
            "nodes": [],
            "bottlenecks": [],
            "error": f"No stock data found for material {material_id}",
        }

    nodes = []
    bottlenecks = []
    total = 0.0

    for n in nodes_raw:
        status = "critical" if n["stock"] < LOW_STOCK_THRESHOLD else "healthy"
        node = {
            "id": n["id"],
            "type": n["type"],
            "label": n["label"],
            "stock": float(n["stock"]),
            "status": status,
            "lat": n["lat"],
            "lon": n["lon"],
        }
        nodes.append(node)
        total += n["stock"]
        if status == "critical":
            bottlenecks.append(n["id"])

    logger.info(
        "M2.achieved: inventory assessed for %s — total_available=%s, nodes_queried=%s, bottlenecks=%s",
        material_id, total, len(nodes), bottlenecks
    )
    return {
        "material_id": material_id,
        "total_available": total,
        "nodes": nodes,
        "bottlenecks": bottlenecks,
    }
