var router = require('express').Router();

router.post('/v1/audit/transaction', (req, res)=> {
    res.status(200).end();
    console.log(req.body);
});

module.exports = router;
