'use strict';

const cds = require('@sap/cds');
const LOG = cds.log('fulfillment-service');

// Mock analysis payload — used when AGENT_URL is not configured (sandbox mode)
function buildMockPayload(salesOrderId) {
  const today = new Date();
  const deliveryDate = new Date(today.getTime() + 7 * 86400000).toISOString().slice(0, 10);
  const poEta = new Date(today.getTime() + 5 * 86400000).toISOString().slice(0, 10);

  return {
    scenario_tag: 'SCN_01',
    status_badge: 'AT_RISK',
    order: {
      id: salesOrderId,
      customer: 'CUST-001',
      material: 'MAT-1042',
      ordered_qty: 500,
      requested_delivery_date: deliveryDate,
    },
    inventory: {
      total_available: 410,
      nodes: [
        { id: 'P001', type: 'plant', label: 'Plant Indianapolis', stock: 150, status: 'healthy', lat: 39.7684, lon: -86.1581 },
        { id: 'P002', type: 'plant', label: 'Plant Columbus',     stock: 170, status: 'healthy', lat: 39.9612, lon: -82.9988 },
        { id: 'DC01', type: 'dc',    label: 'DC01 New York',      stock: 30,  status: 'critical',lat: 40.7128, lon: -74.0060 },
        { id: 'DC02', type: 'dc',    label: 'DC02 Baltimore',     stock: 20,  status: 'critical',lat: 39.2904, lon: -76.6122 },
        { id: 'DC03', type: 'dc',    label: 'DC03 Washington DC', stock: 40,  status: 'critical',lat: 38.9072, lon: -77.0369 },
      ],
    },
    fulfillment_gap: 90,
    inbound_po: {
      total_qualifying_qty: 200,
      earliest_eta: poEta,
      pos: [{ id: 'PO-4471', qty: 200, eta: poEta }],
    },
    recommendation: {
      class: 'PARTIAL_SHIPMENT_BACKORDER',
      action_label: 'Create Backorder',
      summary: `DC01, DC02, and DC03 are running critically low. You can ship 320 units today from P001 and P002. The remaining 180 units can be covered by PO-4471 arriving on ${poEta} — two days before the ${deliveryDate} deadline. Recommend partial shipment now.`,
    },
    supply_chain_nodes: [
      { id: 'SUP-01', type: 'supplier', label: 'Chicago Supplier',        status: 'healthy',  lat: 41.8781, lon: -87.6298, stockQty: null },
      { id: 'P001',   type: 'plant',    label: 'Plant Indianapolis',       status: 'healthy',  lat: 39.7684, lon: -86.1581, stockQty: 150 },
      { id: 'P002',   type: 'plant',    label: 'Plant Columbus',           status: 'healthy',  lat: 39.9612, lon: -82.9988, stockQty: 170 },
      { id: 'DC01',   type: 'dc',       label: 'DC01 New York',            status: 'critical', lat: 40.7128, lon: -74.0060, stockQty: 30 },
      { id: 'DC02',   type: 'dc',       label: 'DC02 Baltimore',           status: 'critical', lat: 39.2904, lon: -76.6122, stockQty: 20 },
      { id: 'DC03',   type: 'dc',       label: 'DC03 Washington DC',       status: 'critical', lat: 38.9072, lon: -77.0369, stockQty: 40 },
      { id: 'CUST-001', type: 'customer', label: 'Customer — US East Coast', status: 'neutral', lat: 40.7549, lon: -73.9840, stockQty: null },
    ],
  };
}

async function callAgent(salesOrderId) {
  const agentUrl = process.env.AGENT_URL;
  if (!agentUrl) {
    LOG.info('AGENT_URL not set — using mock payload for', salesOrderId);
    return buildMockPayload(salesOrderId);
  }

  try {
    const res = await fetch(`${agentUrl}/invoke`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: `Analyze fulfillment for sales order ${salesOrderId}`, session_id: salesOrderId }),
    });
    if (!res.ok) throw new Error(`Agent returned HTTP ${res.status}`);
    const body = await res.json();
    const text = body.result || body.message || body.content || '';
    if (text.includes('---JSON_PAYLOAD---')) {
      const jsonPart = text.split('---JSON_PAYLOAD---')[1].trim();
      return JSON.parse(jsonPart);
    }
    LOG.warn('Agent response missing JSON_PAYLOAD delimiter — falling back to mock');
    return buildMockPayload(salesOrderId);
  } catch (err) {
    LOG.error('Agent call failed, falling back to mock:', err.message);
    return buildMockPayload(salesOrderId);
  }
}

module.exports = class FulfillmentService extends cds.ApplicationService {
  async init() {
    const { FulfillmentSessions, FulfillmentResults, SupplyChainNodes } = this.entities;

    // ── triggerAnalysis ──────────────────────────────────────────────
    this.on('triggerAnalysis', async (req) => {
      const { salesOrderId } = req.data;
      if (!salesOrderId) return req.reject(400, 'salesOrderId is required');

      LOG.info('triggerAnalysis called for', salesOrderId);
      const payload = await callAgent(salesOrderId);

      const sessionId = cds.utils.uuid();
      const resultId  = cds.utils.uuid();

      // Persist session
      await INSERT.into(FulfillmentSessions).entries({
        ID: sessionId,
        salesOrderId,
        scenarioTag: payload.scenario_tag || 'SCN_01',
        statusBadge: payload.status_badge || 'ESCALATION_REQUIRED',
        analysisPayload: JSON.stringify(payload),
      });

      // Persist parsed result
      await INSERT.into(FulfillmentResults).entries({
        ID: resultId,
        session_ID: sessionId,
        salesOrderId: payload.order?.id || salesOrderId,
        customer: payload.order?.customer || '',
        material: payload.order?.material || '',
        deliveryDate: payload.order?.requested_delivery_date || '',
        orderedQty: payload.order?.ordered_qty || 0,
        availableStock: payload.inventory?.total_available || 0,
        fulfillmentGap: payload.fulfillment_gap || 0,
        inboundPoQty: payload.inbound_po?.total_qualifying_qty || 0,
        poEta: payload.inbound_po?.earliest_eta || '',
        recommendationClass: payload.recommendation?.class || '',
        recommendationLabel: payload.recommendation?.action_label || '',
        agentSummary: payload.recommendation?.summary || '',
      });

      // Persist supply chain nodes
      const nodeRows = (payload.supply_chain_nodes || []).map(n => ({
        ID: cds.utils.uuid(),
        session_ID: sessionId,
        nodeId: n.id,
        nodeType: n.type,
        label: n.label,
        status: n.status,
        lat: n.lat || 0,
        lon: n.lon || 0,
        stockQty: n.stockQty || 0,
      }));
      if (nodeRows.length) await INSERT.into(SupplyChainNodes).entries(nodeRows);

      // Return the created session
      return SELECT.one.from(FulfillmentSessions).where({ ID: sessionId });
    });

    // ── Stub actions ─────────────────────────────────────────────────
    this.on('confirmDelivery', async (req) => {
      LOG.info('confirmDelivery stub called for session', req.data.sessionId);
      return true;
    });

    this.on('createBackorder', async (req) => {
      LOG.info('createBackorder stub called for session', req.data.sessionId);
      return true;
    });

    this.on('raiseProcurementAlert', async (req) => {
      LOG.info('raiseProcurementAlert stub called for session', req.data.sessionId);
      return true;
    });

    return super.init();
  }
};
