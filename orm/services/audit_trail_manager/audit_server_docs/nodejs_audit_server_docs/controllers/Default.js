'use strict';

var url = require('url');


var Default = require('./DefaultService');


module.exports.auditTransactionGET = function auditTransactionGET (req, res, next) {
  Default.auditTransactionGET(req.swagger.params, res, next);
};

module.exports.auditTransactionPOST = function auditTransactionPOST (req, res, next) {
  Default.auditTransactionPOST(req.swagger.params, res, next);
};
