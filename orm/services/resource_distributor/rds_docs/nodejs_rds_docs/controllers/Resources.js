'use strict';

var url = require('url');


var Resources = require('./ResourcesService');


module.exports.resourcesDELETE = function resourcesDELETE (req, res, next) {
  Resources.resourcesDELETE(req.swagger.params, res, next);
};

module.exports.resourcesPOST = function resourcesPOST (req, res, next) {
  Resources.resourcesPOST(req.swagger.params, res, next);
};
