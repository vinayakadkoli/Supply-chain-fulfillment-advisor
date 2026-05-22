using { scfa } from '../db/schema';

service FulfillmentService @(path: '/fulfillment') {

  entity FulfillmentSessions as projection on scfa.FulfillmentSession;
  entity FulfillmentResults  as projection on scfa.FulfillmentResult;
  entity SupplyChainNodes    as projection on scfa.SupplyChainNode;

  action triggerAnalysis(salesOrderId: String) returns FulfillmentSessions;
  action confirmDelivery(sessionId: UUID) returns Boolean;
  action createBackorder(sessionId: UUID) returns Boolean;
  action raiseProcurementAlert(sessionId: UUID) returns Boolean;
}
