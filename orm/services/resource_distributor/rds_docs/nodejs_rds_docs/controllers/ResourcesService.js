'use strict';

exports.resourcesDELETE = function(args, res, next) {
  /**
   * parameters expected in the args:
  * resource (Resource)
  **/
  
  
  var examples = {};
  examples['application/json'] = "aeiou";
  
  if(Object.keys(examples).length > 0) {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(examples[Object.keys(examples)[0]] || {}, null, 2));
  }
  else {
    res.end();
  }
  
  
}

exports.resourcesPOST = function(args, res, next) {
  /**
   * parameters expected in the args:
  * resource (Resource)
  **/
  
  
  var examples = {};
  examples['application/json'] = {
  "err" : "aeiou",
  "created" : "aeiou",
  "links" : {
    "self" : "aeiou"
  },
  "id" : "aeiou",
  "message" : "aeiou",
  "updated" : "aeiou"
};
  
  if(Object.keys(examples).length > 0) {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(examples[Object.keys(examples)[0]] || {}, null, 2));
  }
  else {
    res.end();
  }
  
  
}

