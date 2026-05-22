# Product Requirements Document (PRD)

**Title:** Supply Chain Fulfillment Advisor  
**Date:** 2026-05-21  
**Owner:** Supply Chain Operations Team  
**Solution Category:** AI Agent, BTP Extension

---

## Product Purpose & Value Proposition

**Elevator Pitch:**  
Supply chain planners today manually cross-check multiple SAP transactions — sales orders, stock tables, open POs — just to answer "Can we ship this on time?" The Supply Chain Fulfillment Advisor automates that five-step analysis in seconds and surfaces a plain-language recommendation with full visual context through a command-center-style React dashboard.

**Business Need:**  
When a sales order lands, planners must manually query stock levels across plants and distribution centers, calculate the shortfall, reconcile open purchase orders for inbound coverage, and decide on a delivery strategy. This process is slow, inconsistent, and forces planners to context-switch across multiple SAP transactions. The advisor closes this gap with an on-demand AI agent triggered by a single sales order number.

**Expected Value:**
- Reduce per-order fulfillment assessment time from 15–30 minutes to under 60 seconds
- Eliminate manual spreadsheet reconciliation for stock vs. demand gap analysis
- Provide consistent, auditable recommendations across planners and shifts
- Surface bottleneck nodes proactively before they cause delivery failures

**Product Objectives (Prioritized):**
1. Deliver an accurate, fully automated fulfillment feasibility analysis when given a sales order number
2. Surface a structured recommendation (Full Delivery / Partial Shipment + Backorder / Escalate to Procurement) with supporting evidence
3. Render the full analysis in a visually engaging dark-themed React dashboard with KPI cards, bottleneck chips, network map/flow views, and action buttons
4. Design the agent to work against mock data in sandbox and swap cleanly to live SAP S/4HANA APIs in production

---

## User Profiles & Personas

### Primary Persona: Alex — Supply Chain Planner

Alex is a 34-year-old supply chain planner at a mid-size manufacturing company managing 80–120 open sales orders at any time. Each morning Alex reviews a queue of at-risk orders and has to manually check stock in multiple plants and DC locations across SAP. By the time Alex has reconciled stock, looked up open POs, and drafted a recommendation, 25+ minutes have elapsed per order — and higher-priority orders are already piling up. Alex is comfortable with SAP transactions but frustrated by the lack of a single view that connects demand, supply, and inbound flows. Alex needs a tool that gives a clear answer fast, with enough supporting detail to act on it confidently.

### Secondary Persona: Morgan — Logistics Operations Manager

Morgan is a 42-year-old operations manager responsible for on-time delivery KPIs across the distribution network. Morgan doesn't run the individual analyses but needs to trust the recommendations her team acts on. Morgan wants visibility into which DCs and plants are chronic bottlenecks and whether the team is escalating procurement issues in time. Morgan reviews dashboards and exception reports rather than working line-by-line in SAP.

### Other User Types

- **Procurement Officer**: Receives escalation notifications when the agent classifies an order as requiring procurement intervention. Read-only consumer of the advisor output.

---

## User Goals & Tasks

### For Alex (Supply Chain Planner):

**Goals:**
- Determine within one minute whether a given sales order can be fulfilled by the requested delivery date
- Understand exactly which nodes (plants, DCs) are constraining fulfillment
- Act immediately on the recommendation without re-opening SAP transactions

**Key Tasks:**
- Enter a sales order number to trigger the advisor
- Review the KPI card strip (order qty, available stock, fulfillment gap, inbound PO qty, recommendation)
- Inspect bottleneck chips to identify which DCs/plants are low
- Toggle between Map View and Flow View to understand network exposure
- Click the action button (Confirm Delivery / Create Backorder / Raise Procurement Alert)

### For Morgan (Logistics Operations Manager):

**Goals:**
- Monitor recurring bottleneck patterns across the distribution network
- Verify that procurement escalations are being raised in a timely manner

**Key Tasks:**
- Review dashboard status badges (At Risk / On Track / Escalation Required) at a glance
- Read the plain-language recommendation summary to understand the agent's reasoning

---

## Product Principles

1. **Answer first, explain second**: The recommendation is always visible above the fold. Detail is available for those who need it, not mandatory for those who don't.
2. **Mock-first, SAP-ready**: The solution works fully with mock data in sandbox; every integration point is swappable for a live SAP API without changing agent logic.
3. **Human confirms, agent recommends**: The agent never autonomously creates backorders or procurement alerts — it proposes the action and the planner confirms.
4. **Bottlenecks are named, not buried**: Any DC or plant flagged as low stock is called out explicitly by name in the UI, not hidden in aggregated totals.
5. **Analyst voice, not chatbot voice**: The agent's summary text is direct, data-led, and precise — no hedging, no filler.

---

## Business Context

**Current State:**  
Planners access SAP SD for order details, then switch to MM stock overview transactions, cross-reference open PO lists, and manually calculate the gap in a spreadsheet or from memory. The process has no single entry point, no standard output format, and relies entirely on individual planner expertise.

**Strategic Alignment:**  
Supports the company's Plan to Fulfill E2E initiative by automating the feasibility and gap analysis phases that currently consume the most planner time. Aligned with the supply chain digital operations strategy to reduce manual effort on repetitive analytical tasks.

**Success Criteria:**
- End-to-end analysis completed in under 60 seconds per sales order
- Recommendation accuracy validated against planner expert review at ≥90%
- Dashboard renders correctly on standard enterprise desktop displays (1920×1080 and above)
- Agent operates correctly in mock-data sandbox mode before any SAP API connectivity is configured

---

## Goals and Non-Goals

### Goals (In Scope)

- Retrieve and display sales order details (customer, material, quantity, requested delivery date)
- Query and aggregate material stock across plants and distribution centers
- Calculate fulfillment gap (ordered qty − available stock)
- Scan open purchase orders for the material, check ETA vs. delivery date, and compute inbound coverage
- Issue one of three recommendations: Full Delivery / Partial Shipment + Backorder / Escalate to Procurement
- Render all results in a dark-themed React dashboard with KPI cards, bottleneck chips, network map/flow toggle, recommendation panel, and action buttons
- Operate against realistic mock data in sandbox mode

### Non-Goals (Out of Scope)

- Automatically creating backorder documents or procurement alerts in SAP without planner confirmation
- Multi-order batch analysis (the advisor processes one sales order per session)
- Real-time inventory reservation or ATP (Available-to-Promise) commitment
- Integration with SAP IBP or SAP TM in this release
- Mobile or tablet layout optimization

---

## Requirements

### Must-Have Requirements

**R01: Sales Order Retrieval**

- **Problem to Solve**: Planners must navigate to SAP SD and manually look up order details before they can begin any analysis.
- **User Story**: As a Supply Chain Planner, I need to enter a sales order number and immediately see the order's customer, material, ordered quantity, and requested delivery date so that I can start the fulfillment assessment without opening SAP.
- **Acceptance Criteria**:
  - Given a valid sales order number, when I submit it to the advisor, then the agent returns customer name, material ID, ordered quantity, and requested delivery date within 10 seconds
  - Given an invalid or non-existent order number, when I submit it, then the agent returns a clear error message identifying the problem
- **Maps to Objective**: Objective 1
- **Priority Rank**: 1

**R02: Multi-Site Inventory Check**

- **Problem to Solve**: Stock is spread across multiple plants and DCs; planners must query each individually in SAP.
- **User Story**: As a Supply Chain Planner, I need the agent to aggregate available stock for the ordered material across all plants and distribution centers so that I can see the total available quantity in a single view.
- **Acceptance Criteria**:
  - Given a material ID from the sales order, when the agent queries inventory, then it returns per-node stock quantities and a total available quantity
  - Nodes below a configurable low-stock threshold are flagged as bottlenecks and displayed as red-bordered chips in the UI
- **Maps to Objective**: Objective 1
- **Priority Rank**: 2

**R03: Fulfillment Gap Calculation**

- **Problem to Solve**: Planners manually subtract available stock from the ordered quantity, with no standard formula or display.
- **User Story**: As a Supply Chain Planner, I need to see the fulfillment gap (ordered quantity minus available stock) displayed as a KPI so that I immediately know whether a shortfall exists and how large it is.
- **Acceptance Criteria**:
  - Given ordered quantity and total available stock, the dashboard KPI card displays the gap value and a delta indicator (positive gap = red, zero gap = green)
  - Gap calculation is visible in the KPI strip without scrolling
- **Maps to Objective**: Objectives 1, 3
- **Priority Rank**: 3

**R04: Inbound PO Scan**

- **Problem to Solve**: Planners must manually search open POs to identify inbound supply that could cover a shortfall before the delivery deadline.
- **User Story**: As a Supply Chain Planner, I need the agent to identify open purchase orders for the ordered material with ETA before the delivery date so that I know whether the shortfall can be covered by inbound supply.
- **Acceptance Criteria**:
  - Given a material ID and delivery deadline, when the agent scans open POs, then it returns the total inbound quantity from qualifying POs (ETA ≤ delivery date) and the earliest PO ETA
  - Inbound PO quantity is displayed as a KPI card; PO reference and ETA are included in the recommendation panel detail
- **Maps to Objective**: Objective 1
- **Priority Rank**: 4

**R05: Three-Way Delivery Recommendation**

- **Problem to Solve**: Planners make inconsistent delivery decisions based on the same data; there is no standard decision logic.
- **User Story**: As a Supply Chain Planner, I need the agent to recommend Full Delivery, Partial Shipment + Backorder, or Escalate to Procurement based on the gap and inbound PO analysis so that I can act immediately with confidence.
- **Acceptance Criteria**:
  - Full Delivery: recommended when available stock ≥ ordered quantity
  - Partial Shipment + Backorder: recommended when available stock < ordered quantity but available stock + qualifying inbound PO qty ≥ ordered quantity before delivery date
  - Escalate to Procurement: recommended when neither condition above is satisfied
  - Recommendation is displayed as the fifth KPI card and as the primary label in the recommendation panel with a color-coded status badge (green / amber / red)
- **Maps to Objective**: Objective 2
- **Priority Rank**: 5

**R06: Dark-Themed React Operational Dashboard**

- **Problem to Solve**: Planners receive raw data from SAP but have no unified visual interface for the fulfillment analysis.
- **User Story**: As a Supply Chain Planner, I need a visually structured dashboard that presents all fulfillment data in a single view so that I can assess the situation at a glance and take action without reading raw data.
- **Acceptance Criteria**:
  - Header bar displays agent name, scenario tag, and color-coded status badge
  - KPI strip renders five cards: Order Quantity, Available Stock, Fulfillment Gap, Inbound PO Qty, Recommended Action — each with metric label, bold value, and delta indicator
  - Bottleneck chips are displayed below the KPI strip; critical nodes have red borders
  - Supply chain network panel supports Map View (geographic node plot) and Flow View (left-to-right swimlane) with a toggle switch
  - Recommendation panel shows plain-language agent summary and a single action button matching the recommendation
  - Design tokens: background #0d1b2a, card background #1a2b3c, alert accent coral/red, healthy green, warning amber; clean sans-serif font; KPI values in bold large type
- **Maps to Objective**: Objective 3
- **Priority Rank**: 6

**R07: Mock-Data Sandbox Operation**

- **Problem to Solve**: The solution must be demonstrable and testable without live SAP S/4HANA connectivity.
- **User Story**: As a developer, I need the agent to operate against a realistic mock dataset so that the full analysis and dashboard can be built, tested, and demonstrated before SAP API credentials are available.
- **Acceptance Criteria**:
  - Mock dataset covers: Sales Order SO-10042 for 500 units of MAT-1042, delivery in 7 days; plant stock 320 units across 2 plants; DC01, DC02, DC03 flagged low; open PO for 200 units ETA in 5 days; customer location US East Coast
  - Agent logic produces a Partial Shipment + Backorder recommendation against this mock dataset
  - Mock mode is switchable via a configuration flag without code changes
- **Maps to Objective**: Objective 4
- **Priority Rank**: 7

### High-Want Requirements

**R08: Agent Persona Voice**

- **Problem to Solve**: Generic system messages feel impersonal and do not convey analytical confidence.
- **User Story**: As a Supply Chain Planner, I need the agent's recommendation summary to be written in a direct, data-led analyst voice so that the output feels authoritative and is easy to act on.
- **Priority Rank**: 1

**R09: Status Badge Color Coding**

- **Problem to Solve**: Planners need an at-a-glance status signal before reading detailed KPIs.
- **User Story**: As a Logistics Operations Manager, I need the header status badge to reflect the current recommendation state (green = On Track, amber = At Risk, red = Escalation Required) so that I can triage multiple order scenarios rapidly.
- **Priority Rank**: 2

---

## Non-Functional Requirements

### Performance

- **Latency**: Full agent analysis (order retrieval → inventory → gap → PO scan → recommendation) completes in under 60 seconds end-to-end
- **UI Render**: Dashboard renders initial state in under 2 seconds after the agent response is received

### Reliability

- **Mock Fallback**: If SAP API calls fail or credentials are not configured, the agent falls back to mock data and displays a banner indicating mock mode is active
- **Partial Results**: If inventory data is partially unavailable, the agent surfaces what it has and flags the missing nodes rather than failing entirely

### Explainability

- **Recommendation Traceability**: The recommendation panel displays the specific quantities (available stock, inbound PO qty, gap) that drove the classification
- **Decision Logging**: All five milestone steps are logged with structured messages (see Milestones section) for observability and debugging

---

## Solution Architecture

**Architecture Overview:**  
A Python A2A AI agent runs on SAP BTP, receives a sales order number as input, executes the five-step analysis using MCP tool calls (or mock data), and returns a structured JSON response. A React BTP Extension renders the response as the operational dashboard.

**Key Components:**

- **Python AI Agent (A2A)**: Core reasoning engine. Executes the five-step fulfillment analysis, invokes MCP tools, calculates gap logic, issues recommendation. Runs on SAP BTP AI Core.
- **React Dashboard (BTP Extension)**: Dark-themed command-center UI. Consumes the agent's structured JSON output and renders KPI cards, bottleneck chips, network map/flow panels, recommendation panel, and action buttons.
- **Sales Order MCP Server** (`CE_SALESORDER_0001_MCP:v1`): Confirmed available in landscape. Called by the agent to retrieve order header data.
- **Material Stock Mock / API** (`API_MATERIAL_STOCK_SRV:v1`): Mock data in sandbox; production integration requires MCP translation file.
- **Purchase Order Mock / API** (`CE_PURCHASEORDER_0001:v1`): Mock data in sandbox; production integration requires MCP translation file.

**Integration Points:**

- Sales Order MCP Server: read-only, called once per analysis session to retrieve order header
- Material Stock API: read-only, called once per analysis to aggregate plant/DC stock
- Purchase Order API: read-only, called once per analysis to retrieve open POs for the material

**Deployment Environments:**

- **Dev / Sandbox**: Mock data active; no SAP credentials required; full dashboard functional
- **Production**: Live MCP and API calls; mock flag disabled; credentials injected via BTP service bindings

---

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
- The agent exposes extension points for additional analysis steps (e.g., transportation lead time checks, supplier reliability scoring) that can be added as new MCP tool calls without modifying core reasoning logic
- The recommendation rule set (thresholds for bottleneck flagging, low-stock levels) is externalized as configuration to allow tenant-specific tuning

**Business Step Instrumentation:**
- All five fulfillment analysis milestones (see Milestones section) emit structured log statements on achievement and on miss
- Log format: `[MILESTONE_ID].[achieved|missed]: [description]`
- Logs are emitted to standard output and captured by the BTP observability stack for monitoring and debugging

---

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent (reasoning over multi-step tool calls) with human confirmation gate before any write action

**Actions the system performs without human approval:**
- Retrieve sales order details via MCP
- Query material stock across plants and DCs
- Calculate fulfillment gap and classify bottleneck nodes
- Scan open purchase orders and filter by ETA
- Generate a delivery recommendation and render dashboard

**Actions that require human review or approval:**
- Confirming delivery (triggers downstream SAP delivery document creation — out of scope for this release, action button is a stub)
- Creating a backorder
- Raising a procurement alert

**Model or engine used:** LLM via SAP Generative AI Hub (GPT-4o or equivalent) for natural language recommendation generation; deterministic Python logic for gap calculation and recommendation classification

**Knowledge & data sources accessed:**

- SAP S/4HANA Sales Order data (via `CE_SALESORDER_0001_MCP:v1` or mock)
- SAP S/4HANA Material Stock data (via `API_MATERIAL_STOCK_SRV:v1` or mock)
- SAP S/4HANA Purchase Order data (via `CE_PURCHASEORDER_0001:v1` or mock)

**Tools or connectors invoked:**

- `get_sales_order`: reads order header; read-only; safe
- `get_material_stock`: reads plant/DC stock levels; read-only; safe
- `get_open_purchase_orders`: reads open PO list for a material; read-only; safe
- `calculate_fulfillment_gap`: deterministic Python function; no external call
- `generate_recommendation`: calls LLM to produce plain-language summary; read-only

**Guardrails & fail-safes:**

- Agent never writes to SAP — all tool calls are read-only in this release
- If gap calculation returns negative (unexpected data), agent flags the anomaly and requests planner review before issuing a recommendation
- If LLM-generated summary is unavailable, the dashboard falls back to a templated message built from structured data
- Mock mode banner is displayed prominently when live data is not available to prevent planners from acting on simulated figures

---

## Milestones

### M1: Sales Order Retrieved

- **Description**: Agent has successfully fetched the order header from SAP S/4HANA (or mock) and extracted customer, material, quantity, and delivery date
- **Achieved when**: Sales order data object is populated with all four required fields without error
- **Log on achievement**: `M1.achieved: sales order {order_id} retrieved — material={material_id}, qty={ordered_qty}, delivery={delivery_date}`
- **Log on miss**: `M1.missed: sales order retrieval failed for {order_id} — {error_detail}`

### M2: Inventory Assessed

- **Description**: Agent has queried all relevant plants and DCs and aggregated total available stock for the ordered material
- **Achieved when**: Stock query returns results from at least one node and total available quantity is computed
- **Log on achievement**: `M2.achieved: inventory assessed for {material_id} — total_available={total_qty}, nodes_queried={node_count}, bottlenecks={bottleneck_list}`
- **Log on miss**: `M2.missed: inventory query returned no data for {material_id} — {error_detail}`

### M3: Fulfillment Gap Calculated

- **Description**: Agent has computed the fulfillment gap and identified which nodes are below the low-stock threshold
- **Achieved when**: Gap value (ordered qty − available stock) is computed and bottleneck node list is populated
- **Log on achievement**: `M3.achieved: gap calculated — ordered={ordered_qty}, available={available_qty}, gap={gap_qty}, bottlenecks={bottleneck_count}`
- **Log on miss**: `M3.missed: gap calculation skipped — missing input data`

### M4: Inbound PO Scanned

- **Description**: Agent has retrieved open purchase orders for the material and filtered those with ETA on or before the delivery date
- **Achieved when**: PO query returns a result set (even if empty) and qualifying inbound quantity is summed
- **Log on achievement**: `M4.achieved: PO scan complete — qualifying_inbound_qty={inbound_qty}, earliest_eta={eta_date}, pos_found={po_count}`
- **Log on miss**: `M4.missed: PO scan failed or returned no data — {error_detail}`

### M5: Recommendation Issued

- **Description**: Agent has classified the scenario and issued a plain-language recommendation to the planner
- **Achieved when**: One of the three recommendation classes is assigned and the dashboard JSON payload is returned
- **Log on achievement**: `M5.achieved: recommendation issued — class={recommendation_class}, status={status_badge}, order={order_id}`
- **Log on miss**: `M5.missed: recommendation could not be determined — insufficient data`

---

## Risks, Assumptions, and Dependencies

### Risks

- **MCP gap for Material Stock and Purchase Orders**: No MCP servers exist for these APIs in the current landscape. Production deployment requires generating MCP translation files; this is deferred to a follow-on release.
- **Data freshness**: Stock and PO data reflects a point-in-time snapshot. Planners acting on the recommendation may encounter changes if stock is consumed between query and confirmation.
- **LLM summary accuracy**: The plain-language recommendation summary is LLM-generated. Edge cases with unusual data combinations may produce unexpected phrasing; human review is always the final gate.

### Assumptions (Validate These)

- SAP S/4HANA Cloud (Public or Private Edition) is the system of record for sales orders, stock, and purchase orders
- The Sales Order MCP server (`CE_SALESORDER_0001_MCP:v1`) is accessible from the BTP tenant where the agent is deployed
- Mock data for sandbox operation is sufficient to validate all UI components and agent logic before live SAP access is provisioned
- Low-stock threshold for bottleneck flagging is configurable per deployment (default: any DC/plant with stock below 10% of ordered quantity)

### Dependencies

- SAP BTP AI Core: required for agent runtime and LLM access via Generative AI Hub
- SAP BTP Cloud Foundry: required for React frontend hosting
- Sales Order MCP Server (`CE_SALESORDER_0001_MCP:v1`): must be accessible and credentialed in the target BTP subaccount
- Material Stock and Purchase Order API credentials: required for production mode; not needed for sandbox mock mode

---

## Appendix

### Glossary

- **Fulfillment Gap**: The quantity difference between a customer's ordered quantity and the total available stock (ordered qty − available stock). A positive gap indicates a shortfall.
- **Bottleneck Node**: A plant or distribution center whose available stock falls below the configured low-stock threshold for the ordered material.
- **Inbound PO Qty**: The sum of open purchase order quantities for the ordered material with an ETA on or before the customer's requested delivery date.
- **A2A Agent**: Agent-to-Agent protocol — a Python-based AI agent that communicates using a standardized protocol enabling tool use and structured output.
- **MCP Server**: Model Context Protocol server — an adapter that exposes SAP API operations as tools callable by an AI agent.

### References

- SAP Sales Order API (A2X): `sap.s4:apiResource:CE_SALESORDER_0001:v1`
- SAP Material Stock API: `sap.s4:apiResource:API_MATERIAL_STOCK_SRV:v1`
- SAP Purchase Order API: `sap.s4:apiResource:CE_PURCHASEORDER_0001:v1`
- Sales Order MCP Server: `sap.s4:apiResource:CE_SALESORDER_0001_MCP:v1`
- SAP BTP AI Core documentation: https://help.sap.com/docs/sap-ai-core
