import mock
from ims.proxies import rds_proxy
from ims.tests import FunctionalTest


class Response:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def json(self):
        return {"res": self.content}


class TestRdsProxy(FunctionalTest):
    """rds proxy unittests."""

    def setUp(self):
        FunctionalTest.setUp(self)

    def tearDown(self):
        FunctionalTest.tearDown(self)

    @mock.patch.object(rds_proxy, 'di')
    @mock.patch.object(rds_proxy, 'request')
    def test_send_post_rds_success(self, mock_request, mock_di):
        req = mock.MagicMock()
        req.post.return_value = Response(201, "any cont")
        mock_di.resolver.unpack.return_value = req
        result = rds_proxy.send_image({"not real": "only for test"}, "tran_id",
                                      "post")
        self.assertEqual(result, {'res': 'any cont'})

    @mock.patch.object(rds_proxy, 'di')
    @mock.patch.object(rds_proxy, 'request')
    def test_send_put_rds_success(self, mock_request, mock_di):
        req = mock.MagicMock()
        req.put.return_value = Response(200, "any cont")
        mock_di.resolver.unpack.return_value = req
        result = rds_proxy.send_image({"not real": "only for test"}, "tran_id",
                                      "put")
        self.assertEqual(result, {'res': 'any cont'})

    @mock.patch.object(rds_proxy, 'di')
    @mock.patch.object(rds_proxy, 'request')
    def test_send_delete_rds_success(self, mock_request, mock_di):
        req = mock.MagicMock()
        req.delete.return_value = Response(204, "any cont")
        mock_di.resolver.unpack.return_value = req
        result = rds_proxy.send_image({"not real": "only for test"}, "tran_id",
                                      "delete")
        self.assertEqual(result, {'res': 'any cont'})

    @mock.patch.object(rds_proxy, 'di')
    def test_send_bad_rds_bad(self, mock_di):
        req = mock.MagicMock()
        req.post.return_value = Response(204, "any cont")
        mock_di.resolver.unpack.return_value = req
        with self.assertRaises(Exception) as exp:
            rds_proxy.send_image({"not real": "only for test"}, "tran_id",
                                 "any")

    @mock.patch.object(rds_proxy, 'di')
    @mock.patch.object(rds_proxy, 'request')
    def test_send_rds_req_bad_resp(self, mock_request, mock_di):
        req = mock.MagicMock()
        req.post.return_value = Response(301, '{"faultstring": ":("}')
        mock_di.resolver.unpack.return_value = req
        with self.assertRaises(rds_proxy.ErrorStatus):
            rds_proxy.send_image({"not real": "only for test"}, "tran_id",
                                 "post")

    @mock.patch.object(rds_proxy, 'di')
    def test_get_rsource_status_rds(self, mock_di):
        req = mock.MagicMock()
        req.get.return_value = Response(200, "any cont")
        mock_di.resolver.unpack.return_value = req
        result = rds_proxy.get_status(resource_id="123abc", json_convert=True)
        self.assertEqual(result, {'res': 'any cont'})

    @mock.patch.object(rds_proxy, 'di')
    def test_get_rsource_status_rds_nojson(self, mock_di):
        req = mock.MagicMock()
        req.get.return_value = Response(200, "any cont")
        mock_di.resolver.unpack.return_value = req
        rds_proxy.get_status(resource_id="123abc", json_convert=False)
