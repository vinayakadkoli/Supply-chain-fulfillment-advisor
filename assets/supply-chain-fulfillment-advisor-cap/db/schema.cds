namespace scfa;

using { cuid, managed } from '@sap/cds/common';

/**
 * One analysis session per sales order trigger.
 */
entity FulfillmentSession : cuid, managed {
  salesOrderId    : String(10);
  scenarioTag     : String(10) default 'SCN_01';
  statusBadge     : String(30);
  analysisPayload : LargeString;
  result          : Composition of one FulfillmentResult on result.session = $self;
  nodes           : Composition of many SupplyChainNode on nodes.session = $self;
}

/**
 * Parsed summary for direct UI access.
 */
entity FulfillmentResult : cuid {
  session            : Association to FulfillmentSession;
  orderedQty         : Decimal(15,2);
  availableStock     : Decimal(15,2);
  fulfillmentGap     : Decimal(15,2);
  inboundPoQty       : Decimal(15,2);
  recommendationClass: String(40);
  recommendationLabel: String(60);
  agentSummary       : LargeString;
  salesOrderId       : String(10);
  customer           : String(20);
  material           : String(40);
  deliveryDate       : String(20);
  poEta              : String(20);
}

/**
 * Individual supply chain node for map / flow rendering.
 */
entity SupplyChainNode : cuid {
  session   : Association to FulfillmentSession;
  nodeId    : String(20);
  nodeType  : String(20);
  label     : String(80);
  status    : String(20);
  lat       : Decimal(9,6);
  lon       : Decimal(9,6);
  stockQty  : Decimal(15,2);
}
