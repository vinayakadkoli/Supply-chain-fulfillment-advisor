'use strict';

const cds = require('@sap/cds');
const { GET, POST, PATCH, DELETE, axios } = cds.test(__dirname + '/..');

describe('FulfillmentService — triggerAnalysis via OData', () => {
  it('creates a session via triggerAnalysis action', async () => {
    delete process.env.AGENT_URL;

    const response = await POST('/fulfillment/triggerAnalysis', {
      salesOrderId: 'SO-10042',
    });

    expect(response.status).toBe(200);
    const data = response.data;
    expect(data.salesOrderId).toBe('SO-10042');
    expect(data.statusBadge).toBe('AT_RISK');
    expect(data.scenarioTag).toBe('SCN_01');
    expect(data.analysisPayload).toBeTruthy();

    const payload = JSON.parse(data.analysisPayload);
    expect(payload.recommendation.class).toBe('PARTIAL_SHIPMENT_BACKORDER');
  });

  it('confirmDelivery action returns true', async () => {
    const { randomUUID } = require('crypto');
    const response = await POST('/fulfillment/confirmDelivery', {
      sessionId: randomUUID(),
    });
    expect(response.status).toBe(200);
    expect(response.data.value).toBe(true);
  });

  it('createBackorder action returns true', async () => {
    const { randomUUID } = require('crypto');
    const response = await POST('/fulfillment/createBackorder', {
      sessionId: randomUUID(),
    });
    expect(response.status).toBe(200);
    expect(response.data.value).toBe(true);
  });

  it('raiseProcurementAlert action returns true', async () => {
    const { randomUUID } = require('crypto');
    const response = await POST('/fulfillment/raiseProcurementAlert', {
      sessionId: randomUUID(),
    });
    expect(response.status).toBe(200);
    expect(response.data.value).toBe(true);
  });
});

describe('FulfillmentService — FulfillmentSessions read', () => {
  it('GET FulfillmentSessions returns a list', async () => {
    const response = await GET('/fulfillment/FulfillmentSessions');
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data.value)).toBe(true);
  });
});
