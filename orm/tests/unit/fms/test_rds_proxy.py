from orm.services.flavor_manager.fms_rest import proxies
from orm.tests.unit.fms import FunctionalTest

import mock
from testfixtures import log_capture


class Response:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def json(self):
        return self.content


class TestUtil(FunctionalTest):

    @mock.patch.object(proxies.rds_proxy, 'request')
    @mock.patch('requests.post')
    @log_capture('orm.services.flavor_manager.fms_rest.proxies.rds_proxy')
    def test_send_good(self, mock_post, mock_request, l):
        resp = Response(200, 'my content')
        mock_post.return_value = resp
        # send_res = proxies.rds_proxy.send_flavor(db_models.Flavor().todict(), "1234", "post")
        # self.assertRegexpMatches(l.records[-2].getMessage(), 'Wrapper JSON before sending action')
        # self.assertRegexpMatches(l.records[-1].getMessage(), 'return from rds server status code')

    @mock.patch('requests.post')
    @log_capture('orm.services.flavor_manager.fms_rest.proxies.rds_proxy')
    def test_bad_status(self, mock_post, l):
        resp = Response(400, 'my content')
        mock_post.return_value = resp
        # self.assertRegexpMatches(l.records[-2].getMessage(), 'Wrapper JSON before sending action')
        # self.assertRegexpMatches(l.records[-1].getMessage(), 'return from rds server status code')

    @mock.patch('requests.post')
    @log_capture('orm.services.flavor_manager.fms_rest.proxies.rds_proxy')
    def test_no_content(self, mock_post, l):
        resp = Response(200, None)
        mock_post.return_value = resp
        # self.assertRaises(ErrorStatus, proxies.rds_proxy.send_flavor, db_models.Flavor(), "1234")
        for r in l.records:
            self.assertNotRegexpMatches(r.getMessage(), 'return from rds server status code')
