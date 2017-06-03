var router = require('express').Router();
var uuid = require('uuid');

router.post('/v1/uuids', (req, res)=>{
    res.json({
        uuid: uuid.v1()
    });
});

module.exports = router;