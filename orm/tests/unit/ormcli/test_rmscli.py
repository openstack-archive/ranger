from cStringIO import StringIO
import mock
from orm.orm_client.ormcli import ormcli
from orm.orm_client.ormcli import rmscli
import requests
import sys
from unittest import TestCase


class RmsTests(TestCase):
    def setUp(self):
        out, sys.stdout, err, sys.stderr = sys.stdout, StringIO(), sys.stderr, StringIO()
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
        args.rangerversion = '4'
        args.clli = '5'
        args.regionname = '6'
        args.osversion = '7'
        args.valet = '8'
        args.state = '9'
        args.country = '10'
        args.city = '11'
        args.street = '12'
        args.zip = '13'
        args.vlcp_name = '14'

        AAAAAAA = '/?type=%s&status=%s&metadata=%s&rangerversion=%s&clli=%s'\
            '&regionname=%s&osversion=%s&valet=%s&state=%s&country=%s'\
            '&city=%s&street=%s&zip=%s&vlcp_name=%s' % (args.type,
                                                        args.status,
                                                        args.metadata,
                                                        args.rangerversion,
                                                        args.clli,
                                                        args.regionname,
                                                        args.osversion,
                                                        args.valet,
                                                        args.state,
                                                        args.country,
                                                        args.city,
                                                        args.street,
                                                        args.zip,
                                                        args.vlcp_name,)

        subcmd_to_result = {'get_region': (requests.get,
                                           '/%s' % args.region_name_or_id),
                            'get_group': (requests.get, '/%s' % args.group_id),
                            'list_groups': (requests.get, '/'),
                            'create_group': (requests.post, '/'),
                            'update_group': (
                                requests.put, '/%s' % args.group_id),
                            'list_regions': (requests.get, AAAAAAA)
                            }

        for subcmd in subcmd_to_result:
            args.subcmd = subcmd
            self.assertEqual(subcmd_to_result[subcmd],
                             rmscli.cmd_details(args))

    def test_parsing(self):
        cli = ormcli.Cli()
        cli.create_parser()
        cli.parse(
            'orm rms --orm-base-url 12.11.10.9 --port 8832 --timeout 150 '
            'list_regions --type big '.split())
        args = cli.args
        self.assertEqual(args.orm_base_url, '12.11.10.9')
        self.assertEqual(args.port, 8832)
        self.assertEqual(args.type, 'big')
        self.assertEqual(args.timeout, 150)

    @mock.patch('requests.get')
    def test_timeout(self, mock_get):
        cli = ormcli.Cli()
        cli.create_parser()
        cli.parse(
            'orm rms --faceless --orm-base-url 12.11.10.9 --port 8832'
            ' --timeout 1 get_region x'.split())
        mock_get.side_effect = Exception("timeout boom")
        with self.assertRaises(SystemExit) as cm:
            cli.logic()
        self.assertEqual(cm.exception.code, 1)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('timeout boom', output)

    @mock.patch('requests.get')
    def test_one_zone(self, mock_get):
        cli = ormcli.Cli()
        cli.create_parser()
        cli.parse(
            'orm rms --faceless --orm-base-url 12.11.10.9 --port 8832'
            ' --timeout 150 get_region zoneone'.split())
        resp = self.respond(
            {
                "clli": "n/a",
                "name": "SNA 1",
                "enabled": 1,
                "state": "functional",
                "ranger_version": "ranger3.0",
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
        self.assertIn('"ranger_version": "ranger3.0"', output)

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
