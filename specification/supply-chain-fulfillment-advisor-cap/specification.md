# Specification: supply-chain-fulfillment-advisor-cap

> **Guidelines**: Read [guidelines.md](../guidelines.md) and [guidelines-cap.md](../guidelines-cap.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` from the project root for full context
- [ ] Invoke the `cap-development` skill from `assets/supply-chain-fulfillment-advisor-cap/` to set up the CAP project structure
- [ ] Install dependencies (`npm install`), validate the project starts (`cds watch`) and responds

## CDS Data Model

Define the data model to persist fulfillment analysis sessions and drive the OData service consumed by the React frontend.

- [ ] Create `assets/supply-chain-fulfillment-advisor-cap/db/schema.cds` with the following entities:

  **FulfillmentSession** — one analysis session per sales order trigger:
  - `ID: UUID (key)`
  - `salesOrderId: String(10)`
  - `scenarioTag: String(10)`
  - `statusBadge: String(30)` — ON_TRACK | AT_RISK | ESCALATION_REQUIRED
  - `createdAt: DateTime`
  - `analysisPayload: LargeString` — raw JSON from the agent

  **FulfillmentResult** — parsed summary for quick UI access:
  - `ID: UUID (key)`
  - `session: Association to FulfillmentSession`
  - `orderedQty: Decimal`
  - `availableStock: Decimal`
  - `fulfillmentGap: Decimal`
  - `inboundPoQty: Decimal`
  - `recommendationClass: String(40)`
  - `recommendationLabel: String(60)`
  - `agentSummary: LargeString`

  **SupplyChainNode** — individual node data for map/flow rendering:
  - `ID: UUID (key)`
  - `session: Association to FulfillmentSession`
  - `nodeId: String(20)`
  - `nodeType: String(20)` — supplier | plant | dc | customer
  - `label: String(80)`
  - `status: String(20)` — healthy | critical | warning | neutral
  - `lat: Decimal(9,6)`
  - `lon: Decimal(9,6)`
  - `stockQty: Decimal`

- [ ] Run `cds compile db/` to validate schema compiles without errors

## OData Service

- [ ] Create `assets/supply-chain-fulfillment-advisor-cap/srv/fulfillment-service.cds`:
  - Expose `FulfillmentSession`, `FulfillmentResult`, `SupplyChainNode` as read/write entities
  - Add custom action `triggerAnalysis(salesOrderId: String) returns FulfillmentSession` — this calls the Python agent and persists the result
  - Add custom action `confirmDelivery(sessionId: UUID) returns Boolean` — stub action, logs the confirmation, returns true
  - Add custom action `createBackorder(sessionId: UUID) returns Boolean` — stub action, logs intent, returns true
  - Add custom action `raiseProcurementAlert(sessionId: UUID) returns Boolean` — stub action, logs escalation, returns true

- [ ] Run `cds compile srv/` to validate service compiles without errors

## Custom Service Handlers

- [ ] Create `assets/supply-chain-fulfillment-advisor-cap/srv/fulfillment-service.js` with custom handler for `triggerAnalysis`:
  - Accepts `salesOrderId` input
  - Makes an HTTP POST to the agent service at `process.env.AGENT_URL` (default: `http://localhost:8000`) with the sales order ID as the user message
  - Parses the `---JSON_PAYLOAD---` delimiter from the agent response to extract the structured JSON
  - Persists a new `FulfillmentSession` with the raw `analysisPayload`
  - Persists a `FulfillmentResult` record parsed from the structured JSON
  - Persists `SupplyChainNode` records for each node in `supply_chain_nodes`
  - Returns the created `FulfillmentSession`
  - If `AGENT_URL` is not set or agent call fails, use the mock data scenario (SO-10042) to create a canned response for sandbox mode
  - Handler for `confirmDelivery`, `createBackorder`, `raiseProcurementAlert` stub actions: log the action and return `true`

- [ ] Add initial mock data seed file at `assets/supply-chain-fulfillment-advisor-cap/db/data/` with one pre-seeded FulfillmentSession for SO-10042 (uses the mock JSON payload from the agent spec) so the UI renders immediately on first load without requiring an agent call

- [ ] Run `cds watch` and verify `POST /odata/v4/fulfillment/triggerAnalysis` returns a valid FulfillmentSession when called with `{"salesOrderId": "SO-10042"}`

## React Frontend (Dark-Themed Command Center Dashboard)

- [ ] Scaffold React frontend in `assets/supply-chain-fulfillment-advisor-cap/ui/` following the `cap-development` skill frontend guidelines (Vite + React + SAP UI5 Web Components)

- [ ] Install additional frontend dependencies:
  - `react-leaflet` + `leaflet` — for the geographic map view
  - `@sap-ui/webcomponents-react` — for SAP UI5 components

### Design Token Constants

- [ ] Create `ui/src/constants/theme.js` with design tokens:
  ```js
  export const COLORS = {
    bgNavy: '#0d1b2a',
    bgCard: '#1a2b3c',
    bgCardElevated: '#1e3248',
    accentRed: '#e63946',
    accentGreen: '#2ec4b6',
    accentAmber: '#f4a261',
    textPrimary: '#e0e6ed',
    textMuted: '#7a94a8',
    borderSubtle: '#243447',
  };
  export const STATUS_COLORS = {
    ON_TRACK: '#2ec4b6',
    AT_RISK: '#f4a261',
    ESCALATION_REQUIRED: '#e63946',
    healthy: '#2ec4b6',
    critical: '#e63946',
    warning: '#f4a261',
    neutral: '#7a94a8',
  };
  ```

### App Shell & Global Styles

- [ ] Create `ui/src/App.jsx` as the root component:
  - Dark navy background (`#0d1b2a`) applied to `body` and root `div`
  - Renders `<HeaderBar />`, `<KPIStrip />`, `<BottleneckChips />`, `<NetworkPanel />`, `<RecommendationPanel />`
  - Fetches the latest `FulfillmentSession` + related entities on mount via OData call to CAP service
  - Passes parsed data as props to child components
  - Shows a loading skeleton while data is loading
  - Shows an order input field (text input + "Analyze" button) at the top to trigger `triggerAnalysis` action

### Header Bar Component

- [ ] Create `ui/src/components/HeaderBar.jsx`:
  - Left: Agent name "Supply Chain Fulfillment Advisor" in bold white, subtitle showing scenario tag (e.g., "SCN_01")
  - Right: Status badge pill with label and color-coded background:
    - ON_TRACK → green (`#2ec4b6`) background, "On Track" label
    - AT_RISK → amber (`#f4a261`) background, "At Risk" label
    - ESCALATION_REQUIRED → red (`#e63946`) background, "Escalation Required" label
  - Background: slightly elevated card color (`#1a2b3c`), bottom border `1px solid #243447`
  - Full-width, sticky at top

### KPI Cards Strip

- [ ] Create `ui/src/components/KPIStrip.jsx`:
  - Horizontal flex row of exactly 5 cards, equal width, with small gaps
  - Card structure: metric label (small, muted, uppercase) on top, bold large value in center, delta indicator below
  - Cards:
    1. **Order Quantity** — value from `orderedQty`, delta: "Ordered"
    2. **Available Stock** — value from `availableStock`, delta indicator: green if ≥ orderedQty, red if < orderedQty
    3. **Fulfillment Gap** — value from `fulfillmentGap`, red text if gap > 0, green if 0
    4. **Inbound PO Qty** — value from `inboundPoQty`, amber if gap > 0 but covered, green if 0 gap
    5. **Recommended Action** — short label from `recommendationLabel`, colored by status
  - Card background: `#1a2b3c`, border-radius 8px, padding 16px, `box-shadow: 0 2px 8px rgba(0,0,0,0.3)`

### Bottleneck Chips

- [ ] Create `ui/src/components/BottleneckChips.jsx`:
  - Section label "Bottleneck Nodes" in muted small text
  - Renders one chip per `SupplyChainNode` where `status === 'critical'`
  - Each chip: node ID label + node type icon (plant/DC), red border (`2px solid #e63946`), dark background
  - If no critical nodes: render a single green chip "All Nodes Healthy"
  - Horizontal scrollable row

### Supply Chain Network Panel

- [ ] Create `ui/src/components/NetworkPanel.jsx`:
  - Toggle switch at top-right: "Map View" | "Flow View"
  - Renders `<MapView />` or `<FlowView />` based on toggle state

- [ ] Create `ui/src/components/MapView.jsx`:
  - Uses `react-leaflet` `MapContainer` with dark tile layer (CartoDB dark matter: `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`)
  - Renders one `CircleMarker` per `SupplyChainNode` using `lat`/`lon`
  - Marker color determined by node `status` using `STATUS_COLORS`
  - Marker radius: 12 for plants/DCs, 8 for suppliers/customers
  - Tooltip on hover: shows `label`, `nodeType`, `stockQty` (if applicable)
  - Map center: US East Coast (`[39.5, -77.5]`), zoom 5
  - Map height: 380px, full-width, border-radius 8px, overflow hidden

- [ ] Create `ui/src/components/FlowView.jsx`:
  - SVG-based left-to-right swimlane flow
  - Four swimlane columns: Suppliers → Plants → Distribution Centers → Customer
  - Each column header in muted text, vertical dashed separator lines
  - Render nodes as rounded rectangles, color-coded by status
  - Render directed arrows (SVG `<path>` with arrowhead markers) connecting: Suppliers → Plants → DCs → Customer
  - Highlight the connection to critical DC nodes in red
  - Gap indicator: red dashed box between DC column and Customer column when fulfillment gap > 0, labeled "Gap: {gap} units"
  - Height: 380px, full-width

### Recommendation Panel

- [ ] Create `ui/src/components/RecommendationPanel.jsx`:
  - Background: `#1a2b3c`, border-radius 8px, padding 20px
  - Header: "Agent Analysis" in muted small text
  - Body: `agentSummary` text rendered in clean sans-serif, line-height 1.6, text color `#e0e6ed`
  - Footer: single action button, full-width, colored by recommendation:
    - FULL_DELIVERY → green button, label "Confirm Delivery"
    - PARTIAL_SHIPMENT_BACKORDER → amber button, label "Create Backorder"
    - ESCALATE_PROCUREMENT → red button, label "Raise Procurement Alert"
  - On button click: call corresponding CAP stub action (`confirmDelivery`, `createBackorder`, `raiseProcurementAlert`) and show a brief success toast

### OData Integration

- [ ] Create `ui/src/services/fulfillmentService.js`:
  - `fetchLatestSession()` — GET `/odata/v4/fulfillment/FulfillmentSession?$orderby=createdAt desc&$top=1&$expand=FulfillmentResult,SupplyChainNodes`
  - `triggerAnalysis(salesOrderId)` — POST `/odata/v4/fulfillment/triggerAnalysis` with `{"salesOrderId": salesOrderId}`
  - `confirmDelivery(sessionId)` — POST `/odata/v4/fulfillment/confirmDelivery` with `{"sessionId": sessionId}`
  - `createBackorder(sessionId)` — POST `/odata/v4/fulfillment/createBackorder` with `{"sessionId": sessionId}`
  - `raiseProcurementAlert(sessionId)` — POST `/odata/v4/fulfillment/raiseProcurementAlert` with `{"sessionId": sessionId}`
  - All calls use `fetch` with JSON headers

## Wiring & Final Integration

- [ ] Implement all backend functionality described above also in the UI — no backend-only features
- [ ] Verify the full flow end-to-end: enter "SO-10042" in the order input → agent is called (or mock fallback) → session persisted → dashboard renders with correct KPIs, bottleneck chips (DC01, DC02, DC03), map view showing critical DCs in red, flow view showing gap, recommendation panel showing "Create Backorder" in amber, agent summary text
- [ ] Run `cds compile srv/` to validate all CDS models compile without errors
- [ ] Write tests for the `triggerAnalysis` custom handler (mock the agent HTTP call, verify session is persisted and parsed correctly)
- [ ] Write tests for the stub action handlers (`confirmDelivery`, `createBackorder`, `raiseProcurementAlert`)
- [ ] Run `cds watch` and perform manual end-to-end smoke test
