import mock
from unittest import TestCase
from ormcli import ormcli
from ormcli.imscli import cmd_data
from ormcli import imscli
import sys
from cStringIO import StringIO


class ImsTests(TestCase):
    def setUp(self):
        out, sys.stdout, err, sys.stderr = sys.stdout, StringIO(), \
                                           sys.stderr, StringIO()
        self.mock_response = mock.Mock()

    def respond(self, value, code, headers={}):
        self.mock_response.json.return_value = value
        self.mock_response.status_code = code
        self.mock_response.headers = headers
        return self.mock_response

    def test_error_with_empty_args(self):
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main([])
        self.assertEqual(cm.exception.code, 2)
        sys.stderr.seek(0)
        output = sys.stderr.read()
        self.assertIn('too few arguments', output)

    def test_help_command(self):
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm --help'.split())
        self.assertEqual(cm.exception.code, 0)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('usage:', output)
        self.assertIn('optional arguments:', output)
        self.assertIn('<service>', output)
        self.assertIn('ims', output)
        self.assertIn('Image Management', output)

    def test_ims_help_command(self):
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm ims --help'.split())
        self.assertEqual(cm.exception.code, 0)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('usage:', output)
        self.assertIn('timeout', output)
        self.assertIn('optional arguments:', output)
        self.assertIn('orm ims', output)

    @mock.patch.object(imscli, 'cli_common')
    @mock.patch('requests.put')
    @mock.patch('requests.post')
    @mock.patch.object(imscli, 'get_token')
    @mock.patch.object(imscli, 'globals')
    def test_timeout(self, mock_globals, mock_get_token,
                     mock_post, mock_put, mock_common):
        mock_post.side_effect = Exception("timeout boom")
        cli = ormcli.Cli()
        cli.create_parser()
        cli.parse(
            'orm ims create_image client1 '
            'ormcli/tests/data/ims-create-image.json'.split())
        with self.assertRaises(SystemExit) as cm:
            cli.logic()
        self.assertEqual(cm.exception.code, 1)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('timeout boom', output)

    @mock.patch('requests.post')
    @mock.patch.object(imscli, 'get_token')
    @mock.patch.object(imscli, 'globals')
    def test_no_keystone(self, mock_globals, mock_get_token, mock_post):
        mock_post.side_effect = Exception("timeout boom")
        cli = ormcli.Cli()
        cli.create_parser()
        globals()['auth_region'] = 'test'
        cli.parse(
            'orm ims create_image client1 '
            'ormcli/tests/data/ims-create-image.json'.split())
        with self.assertRaises(SystemExit) as cm:
            cli.logic()

    # @mock.patch.object(imscli, 'cli_common')
    # @mock.patch('requests.post')
    # def test_response_code(self, mock_post, mock_common):
    #     cli = ormcli.Cli()
    #     cli.create_parser()
    #     cli.parse(
    #         'orm ims create_image client1 '
    #         'ormcli/tests/data/ims-create-image.json'.split())
    #     resp = self.respond({"access": {"token": {"id": 989}}}, 200)
    #     mock_post.return_value = resp
    #     cli.logic()
    #     sys.stdout.seek(0)
    #     output = sys.stdout.read()
    #     # The response json should be printed, but since we mock post() only
    #     # once, the response would be the same response received
    #     # from Keystone
    #     self.assertIn('{\'access\': {\'token\': {\'id\': 989}}}', output)

    # @mock.patch.object(imscli, 'cli_common')
    # @mock.patch('requests.get')
    # @mock.patch('requests.post')
    # def test_get_image_sanity(self, mock_post, mock_get, mock_common):
    #     mock_post.return_value = self.respond(
    #         {"access": {"token": {"id": 989}}}, 201)
    #     cli = ormcli.Cli()
    #     cli.create_parser()
    #     cli.parse('orm ims get_image client1 test'.split())
    #     mock_get.return_value = self.respond(
    #         {"access": {"token": {"id": 989}}}, 200)
    #     cli.logic()
    #     sys.stdout.seek(0)
    #     output = sys.stdout.read()
    #     self.assertIn('{\'access\': {\'token\': {\'id\': 989}}}', output)

    # @mock.patch.object(imscli, 'cli_common')
    # @mock.patch('requests.get')
    # @mock.patch('requests.post')
    # def test_list_images(self, mock_post, mock_get, mock_common):
    #     mock_post.return_value = self.respond(
    #         {"access": {"token": {"id": 989}}}, 201)
    #     cli = ormcli.Cli()
    #     cli.create_parser()
    #     cli.parse(
    #         'orm ims list_images client1 --visibility public --region a '
    #         '--tenant b'.split())
    #     resp = self.respond({"access": {"token": {"id": 989}}}, 200)
    #     mock_get.return_value = self.respond(
    #         {"access": {"token": {"id": 989}}}, 200)
    #     cli.logic()
    #     sys.stdout.seek(0)
    #     output = sys.stdout.read()
    #     self.assertIn('{\'access\': {\'token\': {\'id\': 989}}}', output)

    @mock.patch.object(imscli, 'cli_common')
    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch.object(imscli, 'get_token')
    @mock.patch.object(imscli, 'globals')
    def test_list_images_bad_request(self, mock_get_token, mock_globals,
                                     mock_post, mock_get, mock_common):
        mock_post.return_value = self.respond(
            {"access": {"token": {"id": 989}}}, 201)
        cli = ormcli.Cli()
        cli.create_parser()
        cli.parse(
            'orm ims list_images client1 --visibility public --region a '
            '--customer b'.split())
        resp = self.respond({"access": {"token": {"id": 989}}}, 200)
        with self.assertRaises(SystemExit) as cm:
            cli.logic()
        self.assertEqual(cm.exception.code, 1)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('API error', output)

    def test_cmd_data_enable(self):
        my_args = mock.MagicMock()
        my_args.subcmd = 'enable'
        cm_data = cmd_data(my_args)
        self.assertEqual("{\n            \"enabled\": true\n}", cm_data)

    def test_cmd_data_disable(self):
        my_args = mock.MagicMock()
        my_args.subcmd = 'disable'
        cm_data = cmd_data(my_args)
        self.assertEqual("{\n            \"enabled\": false\n}", cm_data)

    def test_cmd_data_no_data_file(self):
        my_args = mock.MagicMock()
        my_args.subcmd = 'xyz'

        my_args.datafile.read.return_value = "123"
        cm_data = cmd_data(my_args)
        self.assertEqual("{}", cm_data)

    def test_cmd_data_from_data_file(self):
        my_args = MyDataFile()
        cm_data = cmd_data(my_args)

        self.assertEqual("123", cm_data)


class MyDataFile(object):
    def __init__(self):
        self.subcmd = '1'
        self.datafile = FakeDataFIle()

    def __iter__(self):
        return iter(['datafile'])


class FakeDataFIle(object):
    def read(self):
        return '123'
