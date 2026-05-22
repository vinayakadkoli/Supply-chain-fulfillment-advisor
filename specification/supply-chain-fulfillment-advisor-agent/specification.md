# Specification: supply-chain-fulfillment-advisor-agent

> **Guidelines**: Read [guidelines.md](../guidelines.md) and [guidelines-agent.md](../guidelines-agent.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` from the project root for full context
- [x] Bootstrap agent code in `assets/supply-chain-fulfillment-advisor-agent/` using skill `sap-agent-bootstrap` (invoke from inside `assets/supply-chain-fulfillment-advisor-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

## MCP Server Integration (Path B — Existing MCP Server)

The Sales Order MCP server is confirmed available at ORD ID `sap.s4:apiResource:CE_SALESORDER_0001_MCP:v1`. MCP spec files are pre-saved at `specification/supply-chain-fulfillment-advisor-agent/mcp-specs/`.

- [ ] Wire MCP tool loading in `app/agent.py` using `get_mcp_tools()` from `mcp_tools.py` (canonical pattern from guidelines-agent.md) — NEVER create direct HTTP clients
- [ ] Add Sales Order MCP server dependency to `assets/supply-chain-fulfillment-advisor-agent/asset.yaml` under `requires`:
  ```yaml
  requires:
    - name: ce-salesorder-mcp
      kind: mcp-server
      ordId: sap.s4:apiResource:CE_SALESORDER_0001_MCP:v1
  ```
- [ ] Invoke `mcp-mock-config` skill to generate `mcp-mock.json` based on the MCP spec files in `specification/supply-chain-fulfillment-advisor-agent/mcp-specs/` and the mock data scenario (SO-10042, MAT-1042, 500 units, 7-day delivery)

## Mock Data Tools (Material Stock + Purchase Orders)

Material Stock and Purchase Order APIs have no MCP servers. Implement them as deterministic mock tools inside the agent codebase, switchable via a `MOCK_MODE=true` environment variable.

- [ ] Create `assets/supply-chain-fulfillment-advisor-agent/app/tools/mock_inventory_tool.py`:
  - Tool name: `get_material_stock`
  - Input: `material_id: str`
  - Returns mock stock data for MAT-1042: Plant P001 (150 units), Plant P002 (170 units), DC01 (30 units — flagged low), DC02 (20 units — flagged low), DC03 (40 units — flagged low)
  - Total available: 320 units across 2 plants + 3 DCs
  - Low-stock threshold: any node below 50 units is flagged as a bottleneck
  - Docstring must describe tool purpose for agent resolution

- [ ] Create `assets/supply-chain-fulfillment-advisor-agent/app/tools/mock_purchase_order_tool.py`:
  - Tool name: `get_open_purchase_orders`
  - Input: `material_id: str`, `delivery_deadline: str` (ISO date)
  - Returns mock open POs for MAT-1042: PO-4471, quantity 200 units, ETA in 5 days (2 days before the 7-day deadline)
  - Filters returned POs to only those with ETA ≤ delivery_deadline
  - Docstring must describe tool purpose for agent resolution

- [ ] Register both mock tools alongside MCP tools in `_get_tools()` so the agent graph has access to all four tool types: Sales Order (MCP), Material Stock (mock), Purchase Orders (mock), plus fulfillment gap logic

## Fulfillment Analysis Logic

- [ ] Create `assets/supply-chain-fulfillment-advisor-agent/app/tools/fulfillment_gap_tool.py`:
  - Tool name: `calculate_fulfillment_gap`
  - Input: `ordered_qty: float`, `available_stock: float`, `inbound_po_qty: float`, `delivery_deadline: str`, `po_eta: str`
  - Returns: `gap: float`, `recommendation: str` (one of: `"FULL_DELIVERY"`, `"PARTIAL_SHIPMENT_BACKORDER"`, `"ESCALATE_PROCUREMENT"`), `status_badge: str` (one of: `"ON_TRACK"`, `"AT_RISK"`, `"ESCALATION_REQUIRED"`)
  - Logic:
    - If `available_stock >= ordered_qty` → FULL_DELIVERY / ON_TRACK
    - Elif `available_stock + inbound_po_qty >= ordered_qty` AND `po_eta <= delivery_deadline` → PARTIAL_SHIPMENT_BACKORDER / AT_RISK
    - Else → ESCALATE_PROCUREMENT / ESCALATION_REQUIRED
  - Pure Python — no external calls, no LLM

## Agent Persona & System Prompt

- [ ] Configure agent system prompt in `app/agent.py` `@prompt_section` to instruct the agent to:
  - Adopt a dry, confident analyst voice: direct, data-led, with a hint of wit
  - Example tone: "DC01 and DC02 are running low. You can ship 320 units today. The remaining 180 can be covered by PO-4471 arriving Thursday — two days before the delivery deadline. Recommend partial shipment now."
  - Always set `$top` to maximum 100 on any list/collection tool call to prevent context overflow
  - Never hallucinate stock figures, PO quantities, or order data — only report what tool calls return
  - After collecting all data, always invoke `calculate_fulfillment_gap` to produce the final recommendation
  - Return structured JSON output matching the dashboard contract (see below)

## Structured JSON Output Contract

The agent MUST return a structured JSON payload (in addition to the natural-language summary) that the React dashboard can consume:

```json
{
  "scenario_tag": "SCN_01",
  "status_badge": "AT_RISK",
  "order": {
    "id": "SO-10042",
    "customer": "CUST-001",
    "material": "MAT-1042",
    "ordered_qty": 500,
    "requested_delivery_date": "2026-05-28"
  },
  "inventory": {
    "total_available": 320,
    "nodes": [
      { "id": "P001", "type": "plant", "stock": 150, "status": "healthy" },
      { "id": "P002", "type": "plant", "stock": 170, "status": "healthy" },
      { "id": "DC01", "type": "dc", "stock": 30, "status": "critical" },
      { "id": "DC02", "type": "dc", "stock": 20, "status": "critical" },
      { "id": "DC03", "type": "dc", "stock": 40, "status": "critical" }
    ]
  },
  "fulfillment_gap": 180,
  "inbound_po": {
    "total_qualifying_qty": 200,
    "earliest_eta": "2026-05-26",
    "pos": [
      { "id": "PO-4471", "qty": 200, "eta": "2026-05-26" }
    ]
  },
  "recommendation": {
    "class": "PARTIAL_SHIPMENT_BACKORDER",
    "action_label": "Create Backorder",
    "summary": "<agent-generated plain-language summary>"
  },
  "supply_chain_nodes": [
    { "id": "SUP-01", "type": "supplier", "lat": 41.8781, "lon": -87.6298, "status": "healthy", "label": "Chicago Supplier" },
    { "id": "P001", "type": "plant", "lat": 39.7684, "lon": -86.1581, "status": "healthy", "label": "Plant Indianapolis" },
    { "id": "P002", "type": "plant", "lat": 39.9612, "lon": -82.9988, "status": "healthy", "label": "Plant Columbus" },
    { "id": "DC01", "type": "dc", "lat": 40.7128, "lon": -74.0060, "status": "critical", "label": "DC01 New York" },
    { "id": "DC02", "type": "dc", "lat": 39.2904, "lon": -76.6122, "status": "critical", "label": "DC02 Baltimore" },
    { "id": "DC03", "type": "dc", "lat": 38.9072, "lon": -77.0369, "status": "critical", "label": "DC03 Washington DC" },
    { "id": "CUST-001", "type": "customer", "lat": 40.7549, "lon": -73.9840, "status": "neutral", "label": "Customer - US East Coast" }
  ]
}
```

- [ ] Implement a response formatter in `app/tools/response_formatter.py` that assembles the above JSON from tool call results
- [ ] Ensure the agent always appends the structured JSON block to the end of its response stream, preceded by a `---JSON_PAYLOAD---` delimiter so the frontend can reliably parse it

## Business Step Instrumentation (Milestones)

- [ ] Implement structured logging and OpenTelemetry spans for all five milestones from the PRD. Extract all business logic from `stream()` into `_run_agent()` async helper — NEVER instrument inside `stream()` directly (causes GeneratorExit errors):

  - **M1 — Sales Order Retrieved**:
    - `logger.info("M1.achieved: sales order %s retrieved — material=%s, qty=%s, delivery=%s", order_id, material_id, ordered_qty, delivery_date)`
    - `logger.warning("M1.missed: sales order retrieval failed for %s — %s", order_id, error_detail)`

  - **M2 — Inventory Assessed**:
    - `logger.info("M2.achieved: inventory assessed for %s — total_available=%s, nodes_queried=%s, bottlenecks=%s", material_id, total_qty, node_count, bottleneck_list)`
    - `logger.warning("M2.missed: inventory query returned no data for %s — %s", material_id, error_detail)`

  - **M3 — Fulfillment Gap Calculated**:
    - `logger.info("M3.achieved: gap calculated — ordered=%s, available=%s, gap=%s, bottlenecks=%s", ordered_qty, available_qty, gap_qty, bottleneck_count)`
    - `logger.warning("M3.missed: gap calculation skipped — missing input data")`

  - **M4 — Inbound PO Scanned**:
    - `logger.info("M4.achieved: PO scan complete — qualifying_inbound_qty=%s, earliest_eta=%s, pos_found=%s", inbound_qty, eta_date, po_count)`
    - `logger.warning("M4.missed: PO scan failed or returned no data — %s", error_detail)`

  - **M5 — Recommendation Issued**:
    - `logger.info("M5.achieved: recommendation issued — class=%s, status=%s, order=%s", recommendation_class, status_badge, order_id)`
    - `logger.warning("M5.missed: recommendation could not be determined — insufficient data")`

- [ ] Verify `auto_instrument()` is called at top of `main.py` before any AI framework imports

## Testing

- [ ] `conftest.py` only sets `IBD_TESTING=true` — causes agent to run with mock MCP tool results
- [ ] Write unit test for `get_material_stock` mock tool in `tests/test_mock_inventory_tool.py` — run immediately after writing
- [ ] Write unit test for `get_open_purchase_orders` mock tool in `tests/test_mock_purchase_order_tool.py` — run immediately after writing
- [ ] Write unit test for `calculate_fulfillment_gap` tool in `tests/test_fulfillment_gap_tool.py` covering all three recommendation cases (FULL_DELIVERY, PARTIAL_SHIPMENT_BACKORDER, ESCALATE_PROCUREMENT) — run immediately after writing
- [ ] Write unit test for `response_formatter` in `tests/test_response_formatter.py` — run immediately after writing
- [ ] Write one integration test in `tests/test_agent_integration.py` that runs the full agent flow for SO-10042 with mocked LLM and mocked MCP tools, verifies the structured JSON payload is returned with `PARTIAL_SHIPMENT_BACKORDER` recommendation
- [ ] Run `pytest` from `assets/supply-chain-fulfillment-advisor-agent/` (no args) — fix failures before proceeding
- [ ] Verify `grep -c "^@agent_model\|^@agent_config\|^@prompt_section" assets/supply-chain-fulfillment-advisor-agent/app/agent.py` returns 3
- [ ] Verify `grep -r "M[0-9]\.achieved" assets/supply-chain-fulfillment-advisor-agent/app/` returns results
- [ ] Run `pytest` from `assets/supply-chain-fulfillment-advisor-agent/` (no args) to generate final `test_report.json`
- [ ] Verify `test_report.json` exists in `assets/supply-chain-fulfillment-advisor-agent/`

## Agent Evaluation

- [ ] Invoke `sap-aeval-generate-tool-schema` skill from `assets/supply-chain-fulfillment-advisor-agent/`
- [ ] Invoke `sap-aeval-generate-testcase` skill from `assets/supply-chain-fulfillment-advisor-agent/` with the PRD file and generated `tools.json`
- [ ] Review generated test cases in `aeval/testcases/` and replace placeholder values with realistic data (SO-10042, MAT-1042, etc.) before running evaluations
