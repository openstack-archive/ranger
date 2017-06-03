'use strict';

exports.statusPOST = function(args, res, next) {
  /**
   * parameters expected in the args:
  * statusInput (StatusInput)
  **/
  // no response value expected for this operation
  
  
  res.end();
}

exports.statusResourceIdGET = function(args, res, next) {
  /**
   * parameters expected in the args:
  * id (String)
  **/
  
  
  var examples = {};
  examples['application/json'] = {
  "regions" : [ {
    "ord_transaction_id" : "aeiou",
    "error_msg" : "aeiou",
    "resource_id" : "aeiou",
    "error_code" : "aeiou",
    "region" : "aeiou",
    "timestamp" : "aeiou",
    "ord_notifier_id" : "aeiou",
    "status" : "aeiou"
  } ],
  "status" : "aeiou"
};
  
  if(Object.keys(examples).length > 0) {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(examples[Object.keys(examples)[0]] || {}, null, 2));
  }
  else {
    res.end();
  }
  
  
}

