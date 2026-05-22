# Specification

> **Guidelines**: Read [guidelines.md](./guidelines.md) before executing ANY tasks below.

Check off items as completed.

## Solution Setup

- [x] Create asset directories: `mkdir -p assets/supply-chain-fulfillment-advisor-agent/ assets/supply-chain-fulfillment-advisor-cap/`
- [x] Invoke `setup-solution` skill to create `solution.yaml` and `asset.yaml` files for every asset
- [x] Validate all `asset.yaml` and `solution.yaml` files exist and are well-formed

## Asset Implementation

- [ ] Execute [specification/supply-chain-fulfillment-advisor-agent/specification.md](./supply-chain-fulfillment-advisor-agent/specification.md) (all items)
- [ ] Execute [specification/supply-chain-fulfillment-advisor-cap/specification.md](./supply-chain-fulfillment-advisor-cap/specification.md) (all items)
- [ ] Cross-implementation compatibility check:
  - [ ] Agent returns structured JSON payload with `---JSON_PAYLOAD---` delimiter — CAP handler parses this delimiter correctly
  - [ ] Agent JSON payload shape matches the fields expected by CAP handler (`statusBadge`, `inventory.nodes`, `fulfillment_gap`, `inbound_po`, `recommendation`, `supply_chain_nodes`)
  - [ ] CAP service `AGENT_URL` env var is documented; default `http://localhost:8000` matches agent default port from bootstrap
  - [ ] React frontend OData paths (`/odata/v4/fulfillment/...`) match the CAP service name defined in `fulfillment-service.cds`
  - [ ] SupplyChainNode `lat`/`lon` fields in CDS match the float values returned by the agent JSON
  - [ ] Status badge values (`ON_TRACK`, `AT_RISK`, `ESCALATION_REQUIRED`) are consistent between agent output, CAP model, and React `STATUS_COLORS` constant
