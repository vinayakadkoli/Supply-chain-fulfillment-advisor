const BASE = '/fulfillment';

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${txt}`);
  }
  return res.json();
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export async function triggerAnalysis(salesOrderId) {
  return post('/triggerAnalysis', { salesOrderId });
}

export async function confirmDelivery(sessionId) {
  const r = await post('/confirmDelivery', { sessionId });
  return r.value ?? r;
}

export async function createBackorder(sessionId) {
  const r = await post('/createBackorder', { sessionId });
  return r.value ?? r;
}

export async function raiseProcurementAlert(sessionId) {
  const r = await post('/raiseProcurementAlert', { sessionId });
  return r.value ?? r;
}

export async function listSessions() {
  const d = await get('/FulfillmentSessions?$expand=result,nodes&$orderby=createdAt desc&$top=20');
  return d.value || [];
}
