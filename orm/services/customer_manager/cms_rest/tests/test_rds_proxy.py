import mock
from mock import MagicMock
from cms_rest.tests import FunctionalTest
from cms_rest.logger import get_logger
from testfixtures import log_capture, compare, Comparison as C
import logging
from cms_rest import rds_proxy
from cms_rest.data.sql_alchemy import models
from cms_rest.logic.error_base import ErrorStatus


class Response:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def json(self):
        return self.content


class TestUtil(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)
        self.rp = rds_proxy.RdsProxy()

    @mock.patch.object(rds_proxy, 'request')
    @mock.patch('requests.post')
    @log_capture('cms_rest.rds_proxy')
    def test_send_good(self, mock_post, mock_request, l):
        resp = Response(200, 'my content')
        mock_post.return_value = resp
        send_res = self.rp.send_customer(models.Customer(), "1234", "POST")
        self.assertRegexpMatches(l.records[-3].getMessage(), 'Wrapper JSON before sending action')
        self.assertRegexpMatches(l.records[-1].getMessage(), 'Response Content from rds server')
        self.assertEqual(send_res, 'my content')

    @mock.patch.object(rds_proxy, 'request')
    @mock.patch('requests.post')
    @log_capture('cms_rest.rds_proxy')
    def test_bad_status(self, mock_post, mock_request, l):
        resp = Response(400, 'my content')
        mock_post.return_value = resp
        self.assertRaises(ErrorStatus, self.rp.send_customer, models.Customer(), "1234", "POST")
        self.assertRegexpMatches(l.records[-3].getMessage(), 'Wrapper JSON before sending action')
        self.assertRegexpMatches(l.records[-1].getMessage(), 'Response Content from rds server')

    @mock.patch.object(rds_proxy, 'request')
    @mock.patch('requests.post')
    @log_capture('cms_rest.rds_proxy')
    def test_no_content(self, mock_post, mock_request, l):
        resp = Response(200, None)
        mock_post.return_value = resp
        self.assertRaises(ErrorStatus, self.rp.send_customer, models.Customer(), "1234", "POST")
        for r in l.records:
            self.assertNotRegexpMatches(r.getMessage(), 'Response Content from rds server')
