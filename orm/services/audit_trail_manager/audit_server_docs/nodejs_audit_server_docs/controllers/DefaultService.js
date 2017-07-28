'use strict';

exports.auditTransactionGET = function(args, res, next) {
  /**
   * parameters expected in the args:
  * q.timestampFrom (BigDecimal)
  * q.timestampTo (BigDecimal)
  * q.userId (String)
  * q.applicationId (String)
  * q.trackingId (String)
  * q.externalId (String)
  * q.transactionId (String)
  * q.transactionType (String)
  * q.eventDetails (String)
  * q.status (String)
  * q.resourceId (String)
  * q.serviceName (String)
  * limit (String)
  **/
  
  
  var examples = {};
  examples['application/json'] = {
  "transactions" : [ {
    "transaction_id" : "aeiou",
    "user_id" : "aeiou",
    "service_name" : "aeiou",
    "resource_id" : "aeiou",
    "external_id" : "aeiou",
    "event_details" : "aeiou",
    "transaction_type" : "aeiou",
    "application_id" : "aeiou",
    "tracking_id" : "aeiou",
    "timestamp" : 1.3579000000000001069366817318950779736042022705078125,
    "status" : "aeiou"
  } ]
};
  
  if(Object.keys(examples).length > 0) {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(examples[Object.keys(examples)[0]] || {}, null, 2));
  }
  else {
    res.end();
  }
  
  
}

exports.auditTransactionPOST = function(args, res, next) {
  /**
   * parameters expected in the args:
  * transaction (Transaction)
  **/
  // no response value expected for this operation
  
  
  res.end();
}

