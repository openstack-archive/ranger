var router = require('express').Router();
var fs = require('fs');

router.post('/v1/rds/resources', (req, res)=> {
   var model = JSON.parse(req.body.service_template.model);
   console.log(model, null, 2);
   res.status(201).json({
       'customer': {
           'id': '70383330-f107-11e5-9d3c-005056a504e9',
           'links': {
               'own': 'http://127.0.0.1:8777/v1/rds/customer/70383330-f107-11e5-9d3c-005056a504e9'
           }
           'created': '703ca0a0-f107-11e5-9d3c-005056a504e9'
       }
   });

    fs.writeFileSync(__dirname + '/rds_resource_put.json', req.body.service_template.model);
});

router.put('/v1/rds/resources', (req, res)=> {
   var model = JSON.parse(req.body.service_template.model);
   console.log(model, null, 2);
   res.status(201).json({
       'customer': {
           'id': '70383330-f107-11e5-9d3c-005056a504e9',
           'links': {
               'own': 'http://127.0.0.1:8777/v1/rds/customer/70383330-f107-11e5-9d3c-005056a504e9'
           },
           'created': '703ca0a0-f107-11e5-9d3c-005056a504e9'
       }
   });

    fs.writeFileSync(__dirname + '/rds_resource_put.json', req.body.service_template.model);
});

router.get('/v1/rds/status/resource/:id', (req, res)=>{
	id = req.params.id
	res.status(200).json({
		'status': 'pending', 
		'regions': [
		           {
		        	'region': 'SAN1',
		        	'status': 'success',
		        	'resource-id': id
		           },
		           {
		        	'region': 'AIC_MEDIUM',
		        	'status': 'error',
		        	'resource-id': id
		           },
		           {
		        	'region': 'dla1',
		        	'status': 'success',
		        	'resource-id': id
		           },
	           ]
	})
})

module.exports = router;
