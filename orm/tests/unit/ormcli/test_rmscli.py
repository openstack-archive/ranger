from cStringIO import StringIO
import json
import mock
from orm.orm_client.ormcli import ormcli
from orm.orm_client.ormcli import rmscli
import requests
import sys
from unittest import TestCase

TJ = {'access': {'token': {'id': 'test'}}}


class RmsTests(TestCase):
    def setUp(self):
        out, sys.stdout, err, sys.stderr = sys.stdout, StringIO(), \
            sys.stderr, StringIO()
        self.mock_response = mock.Mock()

    def respond(self, value, code, headers={}):
        self.mock_response.json.return_value = value
        self.mock_response.status_code = code
        self.mock_response.headers = headers
        return self.mock_response

    def test_cmd_details(self):
        args = mock.MagicMock()
        args.get_group = 'test_get_group'
        args.list_groups = 'test_list_groups'
        args.create_group = 'test_create_group'
        args.update_group = 'test_update_group'
        args.region_name_or_id = 'test_region_name_or_id'
        args.type = '1'
        args.status = '2'
        args.metadata = '3'
        args.ranger_agent_version = '4'
        args.clli = '5'
        args.regionname = '6'
        args.osversion = '7'
        args.location_type = '8'
        args.state = '9'
        args.country = '10'
        args.city = '11'
        args.street = '12'
        args.zip = '13'
        args.clcp_name = '14'

        list_region_url = '/?type=%s&status=%s&metadata=%s&ranger_agent_version=%s'\
            '&clli=%s&regionname=%s&osversion=%s&location_type=%s&state=%s'\
            '&country=%s&city=%s&street=%s&zip=%s&clcp_name=%s'

        subcmd_to_result = {
            'get_region': (requests.get, '/%s' % args.region_name_or_id),
            'get_group': (requests.get, '/%s' % args.group_id),
            'list_groups': (requests.get, '/'),
            'create_group': (requests.post, '/'),
            'update_group': (requests.put, '/%s' % args.group_id),
            'list_regions': (requests.get,
                             list_region_url
                             % (args.type, args.status, args.metadata,
                                args.ranger_agent_version, args.clli, args.regionname,
                                args.osversion, args.location_type,
                                args.state, args.country, args.city,
                                args.street, args.zip, args.clcp_name))
        }

        for subcmd in subcmd_to_result:
            args.subcmd = subcmd
            self.assertEqual(subcmd_to_result[subcmd],
                             rmscli.cmd_details(args))

    @mock.patch.object(rmscli.cli_common, 'get_keystone_ep',
                       return_value=None)
    def test_get_token_keystone_ep_not_found(self, mock_get_keystone_ep):
        args = mock.MagicMock()
        args.username = 'test'
        self.assertRaises(rmscli.ConnectionError, rmscli.get_token,
                          'a', args, 'c')

    @mock.patch.object(rmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(rmscli.requests, 'post')
    def test_get_token_errors(self, mock_post, mock_get_keystone_ep):
        # Bad status code
        my_response = mock.MagicMock()
        my_response.status_code = 200
        mock_post.return_value = my_response
        self.assertRaises(rmscli.ConnectionError, rmscli.get_token,
                          3, mock.MagicMock(), 'c')

        # Post fails
        mock_post.side_effect = ValueError('test')
        self.assertRaises(rmscli.ConnectionError, rmscli.get_token,
                          3, mock.MagicMock(), 'c')

    @mock.patch.object(rmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(rmscli.requests, 'post')
    @mock.patch.object(rmscli.requests, 'get')
    @mock.patch.object(rmscli, 'get_token')
    @mock.patch.object(rmscli, 'globals')
    def test_list_regions(self, mock_globals, mock_get_token,
                          mock_get, mock_post, mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.return_value = self.mock_response
        args = ormcli.main('orm rms list_regions t'.split())
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn(json.dumps(TJ), output)

    @mock.patch.object(rmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(rmscli.requests, 'post')
    @mock.patch.object(rmscli.requests, 'get')
    @mock.patch.object(rmscli, 'get_token')
    def test_list_regions_a(self, mock_get_token, mock_get,
                            mock_post, mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.return_value = self.mock_response
        mock_get.__name__ = 'a'
        args = ormcli.main('orm rms --verbose list_regions t'.split())
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn(json.dumps(TJ), output)

    @mock.patch.object(rmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(rmscli.requests, 'post')
    @mock.patch.object(rmscli.requests, 'get')
    def test_list_regions_e(self, mock_get, mock_post, mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.side_effect = Exception('e')
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm rms list_regions t'.split())
        self.assertEqual(cm.exception.code, 1)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('e', output)

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_list_regions_with_filters(self, mock_post, mock_get):
        cli = ormcli.Cli()
        cli.create_parser()
        cli.parse(
            'orm rms list_regions --city StLouis --zip 63101 client1'.split())
        resp = self.respond('{"Howdy, mate"}', 200, {'X-Subject-Token': 989})
        mock_post.return_value = self.respond(
            {"access": {"token": {"id": 989}}}, 200)

    @mock.patch.object(rmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(rmscli.requests, 'post')
    @mock.patch.object(rmscli.requests, 'get')
    @mock.patch.object(rmscli, 'get_token')
    @mock.patch.object(rmscli, 'globals')
    def test_list_regions_errors(self, mock_globals, mock_get_token,
                                 mock_get, mock_post,
                                 mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.return_value = self.respond(TJ, 204)
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm rms list_regions t'.split())
        self.assertEqual(cm.exception.code, 0)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertEqual('', output)

        mock_get.return_value = self.respond(TJ, 404)
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm rms --faceless list_regions t'.split())
        self.assertEqual(cm.exception.code, 1)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('API error:', output)

#    @mock.patch('requests.post')
#    @mock.patch.object(rmscli, 'get_token')
#    def test_response_code(self, mock_get_token, mock_post):
#        cli = ormcli.Cli()
#        cli.create_parser()
#        cli.parse(
#            'orm rms create_region client1 '
#            'ormcli/tests/data/rms-create-region.json'.split())
#        resp = self.respond({"access": {"token": {"id": 989}}}, 400)
#        mock_post.return_value = resp
#        with self.assertRaises(SystemExit) as cm:
#            cli.logic()
#
#    @mock.patch('requests.post')
#    def test_ok(self, mock_post):
#        cli = ormcli.Cli()
#        cli.create_parser()
#        cli.parse(
#            'orm rms create_region client1 '
#            'ormcli/tests/data/rms-create-region.json'.split())
#        mock_post.return_value = self.respond(
#            {"access": {"token": {"id": 989}}}, 200)
#
#    def test_parsing(self):
#        cli = ormcli.Cli()
#        cli.create_parser()
#        cli.parse(
#            'orm rms --orm-base-url 12.11.10.9 --port 8832 --timeout 150 '
#            'list_regions --type big '.split())
#        args = cli.args
#        self.assertEqual(args.orm_base_url, '12.11.10.9')
#        self.assertEqual(args.port, 8832)
#        self.assertEqual(args.type, 'big')
#        self.assertEqual(args.timeout, 150)
#
#    @mock.patch('requests.get')
#    def test_timeout(self, mock_get):
#        cli = ormcli.Cli()
#        cli.create_parser()
#        cli.parse(
#            'orm rms --faceless --orm-base-url 12.11.10.9 --port 8832'
#            ' --timeout 1 get_region x'.split())
#        mock_get.side_effect = Exception("timeout boom")
#        with self.assertRaises(SystemExit) as cm:
#            cli.logic()
#        self.assertEqual(cm.exception.code, 1)
#        sys.stdout.seek(0)
#        output = sys.stdout.read()
#        self.assertIn('timeout boom', output)

    @mock.patch('requests.get')
    def test_one_zone(self, mock_get):
        cli = ormcli.Cli()
        cli.create_parser()
        cli.parse(
            'orm rms --faceless --rms-base-url 12.11.10.9 --port 8832'
            ' --timeout 150 get_region zoneone'.split())
        resp = self.respond(
            {
                "clli": "n/a",
                "name": "SNA 1",
                "enabled": 1,
                "state": "functional",
                "ranger_agent_version": "aic3.0",
                "endpoints": [
                    {
                        "type": "horizon",
                        "publicurl": "http://horizon1.com"
                    },
                    {
                        "type": "identity",
                        "publicurl": "http://identity1.com"
                    },
                    {
                        "type": "ord",
                        "publicurl": "http://ord1.com"
                    }
                ],
                "id": "SNA1",
                "metadata": []
            }, 200,
            {'X-Subject-Token': 989})
        mock_get.return_value = resp
        cli.logic()
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('"ranger_agent_version": "aic3.0"', output)

        # def test_error_with_wrong_port(self):
        #     args = self.parser.parse_args('--port 1111'.split())
        #     with self.assertRaises(SystemExit) as cm:
        #         rmscli.rmscli_logic(args)
        #     self.assertEqual(cm.exception.code, 1)
        #     sys.stdout.seek(0)
        #     output = sys.stdout.read()
        #     self.assertIn('Connection refused', output)

        # def test_help_command(self):
        #     with self.assertRaises(SystemExit) as cm:
        #         args = self.parser.parse_args(['--help'])
        #     self.assertEqual(cm.exception.code, 0)
        #     sys.stdout.seek(0)
        #     output = sys.stdout.read()
        #     self.assertIn('usage:', output)
        #     self.assertIn('timeout', output)
        #     self.assertIn('optional arguments:', output)
        #     self.assertIn('--host', output)

        # @mock.patch('requests.get')
        # def test_timeout(self, mock_get):
        #     args = self.parser.parse_args('--host 1.1.1.1 --timeout
        # 1000'.split())
        #     mock_get.side_effect = Exception("HTTPConnectionPool(
        # host='1.1.1.1', port=8080): Max retries exceeded with url: /lcp (
        # Caused by ConnectTimeoutError(
        # <requests.packages.urllib3.connection.HTTPConnection object at
        # 0x7f9469c1a310>, 'Connection to 1.1.1.1 timed out. (connect
        # timeout=1.0)'))")
        #     with self.assertRaises(SystemExit) as cm:
        #         rmscli.rmscli_logic(args)
        #     self.assertEqual(cm.exception.code, 1)
        #     sys.stdout.seek(0)
        #     output = sys.stdout.read()
        #     self.assertIn('ConnectTimeoutError', output)

        # learn how to mock 'real' request.get

        # @mock.patch('rmscli.rmscli.rmscli.requests.get', autospec=True)
        # def test_bad_status(self, mock_get):
        #     args = self.parser.parse_args([])
        #     mock_get.return_value = Response({},500)
        #     with self.assertRaises(SystemExit) as cm:
        #         rmscli.rmscli_logic(args)
        #     self.assertEqual(cm.exception.code, 1)
        #     sys.stdout.seek(0)
        #     output = sys.stdout.read()
        #     self.assertIn('GET', output)
