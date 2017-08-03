import mock
from mock import patch

from rds.ordupdate import ord_notifier
import unittest


class MyResponse(object):
    def __init__(self, status_code, json_result):
        self.status_code = status_code
        self.json_result = json_result

    def json(self):
        return self.json_result


def validate_http_post(addr, **kwargs):
    if addr.startswith('https'):
        raise ValueError('Received an HTTPS address!')
    else:
        return MyResponse(ord_notifier.ACK_CODE, 'OK')


def validate_https_post(addr, **kwargs):
    if not addr.startswith('https'):
        raise ValueError('Received an HTTPS address!')
    else:
        return MyResponse(ord_notifier.ACK_CODE, 'OK')


class MyOrdupdate(object):
    def __init__(self):
        self.discovery_url = '3'
        self.discovery_port = 3
        self.template_type = '3'


class MyDefault(object):
    def __init__(self):
        self.application_name = 'RDS'


class MyConf(object):
    def __init__(self):
        self.ordupdate = MyOrdupdate()
        self.DEFAULT = MyDefault()

    def __call__(self, *args, **kwargs):
        pass

    def register_group(self, param):
        pass

    def register_opts(self, param1, param2):
        pass


class MainTest(unittest.TestCase):
    def setUp(self):
        super(MainTest, self).setUp()
        self.addCleanup(mock.patch.stopall)
        ord_notifier.CONF = MyConf()

    @mock.patch.object(ord_notifier, 'conf')
    def test_find_correct_ord_get_failure(self, mock_conf):
        ord_notifier.requests.get = mock.MagicMock(
            return_value=MyResponse(404, 'test'))
        result = ord_notifier._find_correct_ord(None, None)
        self.assertIsNone(result)

    @mock.patch.object(ord_notifier, 'conf')
    def test_find_correct_ord_bad_response(self, mock_conf):
        ord_notifier.requests.get = mock.MagicMock(
            return_value=MyResponse(ord_notifier.OK_CODE,
                                    {'regions': [{'endpoints': [
                                        {'publicurl': 'test',
                                         'type': 'test'}]}]}))
        result = ord_notifier._find_correct_ord(None, None)
        self.assertIsNone(result)
        ord_notifier.requests.get = mock.MagicMock(
            return_value=MyResponse(ord_notifier.OK_CODE,
                                    {'regions': [{'endqoints': [
                                        {'publicurl': 'test',
                                         'type': 'test'}]}]}))
        result = ord_notifier._find_correct_ord(None, None)
        self.assertIsNone(result)

    @mock.patch.object(ord_notifier, 'conf')
    def test_find_correct_ord_sanity(self, mock_conf):
        ord_notifier.requests.get = mock.MagicMock(
            return_value=MyResponse(ord_notifier.OK_CODE,
                                    {'regions': [{'endpoints': [
                                        {'publicURL': 'test',
                                         'type': 'ord'}]}]}))
        result = ord_notifier._find_correct_ord(None, 'gigi')
        self.assertEqual('test', result)

    @mock.patch.object(ord_notifier, 'conf')
    @mock.patch.object(ord_notifier.json, 'dumps')
    def test_notify_sanity(self, mock_dumps, mock_conf):
        ord_notifier.requests.post = mock.MagicMock(
            return_value=MyResponse(ord_notifier.ACK_CODE, None))
        ord_notifier._notify(*("1",) * 8)

    @mock.patch.object(ord_notifier, 'conf')
    @mock.patch.object(ord_notifier.json, 'dumps')
    def test_notify_not_acknowledged(self, mock_dumps, mock_conf):
        ord_notifier.requests.post = mock.MagicMock(
            return_value=MyResponse(404, None))

        try:
            ord_notifier._notify(*("1",) * 8)
            self.fail('notify() passed successfully'
                      '(expected NotifyNotAcknowledgedError)')
        except ord_notifier.NotifyNotAcknowledgedError:
            pass

    @mock.patch.object(ord_notifier, 'conf')
    def test_notify_https_disabled_but_received(self, mock_conf):
        ord_notifier.requests.post = validate_http_post
        mock_conf.ordupdate.https_enabled = False
        mock_conf.ordupdate.template_type = 'a'
        ord_notifier._notify('https://127.0.0.1:1337', * ("1", ) * 7)

    @mock.patch.object(ord_notifier, 'conf')
    @mock.patch.object(ord_notifier.json, 'dumps')
    def test_notify_https_enabled_and_no_certificate(self, mock_dumps,
                                                     mock_conf):
        ord_notifier.requests.post = validate_https_post
        mock_conf.ordupdate.https_enabled = True
        mock_conf.ordupdate.cert_path = ''
        ord_notifier._notify('https://127.0.0.1:1337', *("1",) * 7)

    @mock.patch.object(ord_notifier, 'conf')
    @mock.patch.object(ord_notifier.json, 'dumps')
    def test_notify_https_enabled_and_ssl_error(self, mock_dumps, mock_conf):
        ord_notifier.requests.post = mock.MagicMock(
            side_effect=ord_notifier.requests.exceptions.SSLError('test'))
        mock_conf.ordupdate.https_enabled = True
        mock_conf.ordupdate.cert_path = ''
        self.assertRaises(ord_notifier.requests.exceptions.SSLError,
                          ord_notifier._notify, 'https://127.0.0.1:1337',
                          *("1",) * 7)

    @patch.object(ord_notifier.audit, 'audit')
    @patch.object(ord_notifier, 'regionResourceIdStatus')
    @mock.patch.object(ord_notifier, 'conf')
    def test_main_ord_not_found(self, mock_audit, mock_region, mock_conf):
        ord_notifier.requests.get = mock.MagicMock(
            return_value=MyResponse(404, 'test'))
        try:
            ord_notifier.notify_ord('test', '1', '2', '3', '4', '5', '6',
                                    'gigi', '7', '')
            self.fail('notify_ord() passed successfully (expected OrdNotFoundError)')
        except ord_notifier.OrdNotFoundError as e:
            self.assertEqual(e.message, 'ORD of LCP %s not found' % (
                'gigi', ))

    @patch.object(ord_notifier.audit, 'audit')
    @patch.object(ord_notifier, 'regionResourceIdStatus')
    @mock.patch.object(ord_notifier, 'conf')
    def test_main_error(self, mock_audit, mock_region, mock_conf):
        ord_notifier.requests.get = mock.MagicMock(
            return_value=MyResponse(ord_notifier.OK_CODE,
                                    {'regions': [{'endpoints': [
                                        {'publicurl': 'test',
                                         'type': 'ord'}]}]}))
        ord_notifier.requests.post = mock.MagicMock(
            return_value=MyResponse(ord_notifier.ACK_CODE, None))

        ord_notifier.notify_ord('test', '1', '2', '3', '4', '5', '6', '7',
                                '8', '9', '10', True)
