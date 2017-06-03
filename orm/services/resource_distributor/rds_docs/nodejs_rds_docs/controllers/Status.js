'use strict';

var url = require('url');


var Status = require('./StatusService');


module.exports.statusPOST = function statusPOST (req, res, next) {
  Status.statusPOST(req.swagger.params, res, next);
};

module.exports.statusResourceIdGET = function statusResourceIdGET (req, res, next) {
  Status.statusResourceIdGET(req.swagger.params, res, next);
};
