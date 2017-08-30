from orm.tests.unit.ims import FunctionalTest


class TestLogsController(FunctionalTest):
    """logs controller unittests."""

    def setUp(self):
        FunctionalTest.setUp(self)

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_logs_api_put_success(self):
        level = 'info'
        response = self.app.put('/v1/orm/logs/{}'.format(level))
        self.assertEqual(response.json,
                         {"result": "Log level changed to {}.".format(level)})
        self.assertEqual(201, response.status_code)

    def test_logs_api_put_level_none(self):
        response = self.app.put('/v1/orm/logs/', expect_errors=True)
        self.assertEqual(response.status_code, 400)

    def test_logs_api_put_level_bad(self):
        level = "not_valid_level"
        response = self.app.put('/v1/orm/logs/{}'.format(level),
                                expect_errors=True)
        print response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['faultstring'],
                         "The given log level [{}] doesn't exist.".format(
                             level))

    def test_logs_api_put_level_bad(self):
        level = "not_valid_level"
        response = self.app.put('/v1/orm/logs/{}'.format(level),
                                expect_errors=True)
        print response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['faultstring'],
                         "The given log level [{}] doesn't exist.".format(
                             level))
