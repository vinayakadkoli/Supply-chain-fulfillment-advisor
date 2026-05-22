# Supply Chain Fulfillment Advisor

Supply Chain Fulfillment Advisor — conversational AI agent with rich React dashboard

## Business challenge

Supply chain planners need a fast, data-driven way to assess whether a customer sales order can be fulfilled before the requested delivery date. Today this requires manually checking stock across multiple plants and DCs, reconciling open purchase orders against the shortfall, and making judgment calls about partial shipment or procurement escalation — a time-consuming, error-prone process. The advisor automates this analysis end-to-end and surfaces the recommendation through an immersive operational dashboard.

## Key Milestones

1. **Sales Order Retrieved** — agent fetches order header, customer, product, quantity, and delivery date from SAP S/4HANA via Sales Order MCP
2. **Inventory Assessed** — agent queries material stock across all relevant plants and distribution centers and aggregates available quantity
3. **Fulfillment Gap Calculated** — agent computes ordered quantity vs. available stock and flags bottleneck nodes (DCs/plants below threshold)
4. **Inbound PO Scanned** — agent retrieves open purchase orders for the material and checks if ETA falls before the delivery deadline
5. **Recommendation Issued** — agent classifies scenario as Full Delivery / Partial Shipment + Backorder / Escalate to Procurement and surfaces result to planner

## Business Architecture (RBA)

### End-to-End Process

Plan to Fulfill (E2E)

### Process Hierarchy

```
Plan to Fulfill (E2E)
└── Procure to Receipt (generic)
    └── Purchase products and services (BPS-329)
        └── Manage purchase order
└── Orchestrate Fulfillment Process (BA-2811)
    └── Sales order feasibility assessment
    └── Delivery action recommendation
└── Balance Inventory (BA-3003)
    └── Multi-site stock availability check
    └── Fulfillment gap calculation
└── Manage Inventory & Warehouse Operations (BA-2937)
    └── Plant and DC stock queries
    └── Bottleneck node identification
└── Manage Purchase Order (BA-2922)
    └── Open PO scanning for inbound supply
    └── ETA-to-delivery-date alignment
```

### Summary

The challenge maps squarely to the Plan to Fulfill E2E, spanning inventory balance, fulfillment orchestration, warehouse operations, and purchase order management. The AI agent automates the cross-system analysis that a planner would otherwise do manually.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | Gap? | Notes / assumptions |
|---|---|---|---|---|---|
| Retrieve sales order details (customer, product, qty, delivery date) | SAP S/4HANA Cloud (SD module) | `sap.s4:apiResource:CE_SALESORDER_0001:v1` | `sap.s4:apiResource:CE_SALESORDER_0001_MCP:v1` ✓ | No | MCP server confirmed available |
| Check inventory stock levels across plants and DCs | SAP S/4HANA Cloud (MM module) | `sap.s4:apiResource:API_MATERIAL_STOCK_SRV:v1` | — | Yes | No MCP server found; API integration required |
| Calculate fulfillment gap and flag bottleneck nodes | SAP S/4HANA / SAP IBP | — | — | Yes | Custom agent logic required; IBP covers planning but not conversational gap analysis |
| Scan open purchase orders for inbound supply coverage | SAP S/4HANA Cloud (MM module) | `sap.s4:apiResource:CE_PURCHASEORDER_0001:v1` | — | Yes | No MCP server found; API integration required |
| Recommend delivery action (Full / Partial+BO / Escalate) | None (custom logic) | — | — | Yes | No standard SAP product provides AI-driven tri-option recommendation |
| Rich dark-themed React operational dashboard | None (custom UI) | — | — | Yes | Custom BTP Extension required; no standard Fiori app covers this visual scope |

### Key findings

- Sales Order API has a confirmed MCP server (`CE_SALESORDER_0001_MCP:v1`) — agent can call it directly without a custom adapter
- Material Stock and Purchase Order APIs have no MCP servers; mock data will be used in sandbox; real integration would require MCP translation files
- SAP S/4HANA Cloud (Public and Private) covers Purchase Order Processing and Inventory Management natively, but exposes no out-of-the-box AI fulfillment advisor interface
- SAP IBP covers supply balancing but is a separate planning product — not applicable for a real-time conversational agent
- The fulfillment gap calculation, bottleneck flagging, and three-way recommendation logic are custom and constitute the core agent intelligence
- The React dashboard (dark navy, command-center aesthetic, map/flow toggle) is a full custom BTP Extension with no standard SAP equivalent

## Recommendations

### Supply Chain Fulfillment Advisor — AI Agent + BTP Extension

#### Executive Summary

Python AI agent + React dashboard on BTP for order fulfillment advisory

#### Recommended Solution

A Python-based A2A AI agent backed by SAP S/4HANA APIs (Sales Order MCP, Material Stock API, Purchase Order API) performs the five-step fulfillment analysis. The agent exposes a conversational interface and returns structured JSON consumed by a React BTP Extension rendering a dark-themed supply chain operations dashboard with KPI cards, bottleneck chips, supply network map/flow views, and action buttons.

Mock data is used in the sandbox to simulate S/4HANA responses. In production, the agent connects to the confirmed Sales Order MCP server and integrates Material Stock and Purchase Order APIs via MCP translation files.

#### Problem Statement

Supply chain planners lack a single tool to rapidly assess order-level fulfillment risk, identify which nodes are bottlenecks, and receive a clear recommendation — without switching between multiple SAP transactions.

#### Affected User Roles

- Supply Chain Planner
- Logistics Operations Manager
- Procurement Officer (escalation recipient)

#### Important factors

##### Real-time feasibility over batch planning
The agent runs on-demand when triggered with a sales order number, giving planners an immediate answer rather than waiting for overnight MRP runs.

##### Mock-first, SAP-ready design
Sandbox mode uses realistic mock data so the UI and agent logic can be built and demonstrated without live S/4HANA connectivity. The architecture is designed to swap mocks for live API calls.

##### MCP server reuse
The Sales Order MCP server (`CE_SALESORDER_0001_MCP:v1`) is already available in the landscape — the agent can use it directly, reducing integration effort for that data source.

#### Potential risks

##### MCP gap for Material Stock and Purchase Orders
No MCP servers found for these APIs; real-world deployment requires generating MCP translation files or building REST adapters.

##### Data freshness
Stock and PO data is point-in-time; agent must communicate clearly that the analysis reflects a snapshot, not a live reservation.

#### Recommended solution category

AI Agent, BTP Extension

#### Intent fit
92%
