from cStringIO import StringIO
import json
import mock
import requests
import sys
from unittest import TestCase

from orm.orm_client.ormcli import cmscli
from orm.orm_client.ormcli import ormcli

TJ = {'access': {'token': {'id': 'test'}}}


class CmsTests(TestCase):
    def setUp(self):
        out, sys.stdout, err, sys.stderr = sys.stdout, StringIO(), \
            sys.stderr, StringIO()
        self.mock_response = mock.Mock()

    def respond(self, value, code, headers={}, oy=False):
        # Set the response according to the parameter
        if oy:
            response = mock.Mock()
        else:
            response = self.mock_response

        response.json.return_value = value
        response.status_code = code
        response.headers = headers
        return response

    def test_cmd_details(self):
        # Set up the args parameter
        args = mock.MagicMock()
        args.custid = 'test_custid'
        args.regionid = 'test_region'
        args.userid = 'test_userid'
        args.region = 'test_region'
        args.user = 'test_user'
        args.starts_with = 'test_startswith'
        args.contains = 'test_contains'
        args.force_delete is False

        subcmd_to_result = {
            'create_customer': (requests.post, '',),
            'delete_customer': (requests.delete, '/%s' % args.custid,),
            'update_customer': (requests.put, '/%s' % args.custid,),
            'add_region': (requests.post, '/%s/regions' % args.custid,),
            'replace_region': (requests.put, '/%s/regions' % args.custid,),
            'delete_region': (
                requests.delete,
                '/%s/regions/%s/%s' % (args.custid, args.regionid,
                                       args.force_delete),),
            'add_user': (
                requests.post,
                '/%s/regions/%s/users' % (args.custid, args.regionid),),
            'replace_user': (
                requests.put,
                '/%s/regions/%s/users' % (args.custid, args.regionid),),
            'delete_user': (requests.delete, '/%s/regions/%s/users/%s' % (
                args.custid, args.regionid, args.userid),),
            'add_default_user': (requests.post, '/%s/users' % args.custid,),
            'replace_default_user': (requests.put, '/%s/users' % args.custid,),
            'delete_default_user': (
                requests.delete, '/%s/users/%s' % (args.custid, args.userid),),
            'add_metadata': (requests.post, '/%s/metadata' % args.custid,),
            'replace_metadata': (requests.put, '/%s/metadata' % args.custid,),
            'get_customer': (requests.get, '/%s' % args.custid,),
            'list_customers': (requests.get,
                               '/?region=%s&user=%s&starts_with=%s'
                               '&contains=%s' % (args.region,
                                                 args.user, args.starts_with,
                                                 args.contains))
        }

        # Assert that each subcommand returns the expected details
        for subcmd in subcmd_to_result:
            args.subcmd = subcmd
            self.assertEqual(subcmd_to_result[subcmd],
                             cmscli.cmd_details(args))

    @mock.patch.object(cmscli.cli_common, 'get_keystone_ep',
                       return_value=None)
    def test_get_token_keystone_ep_not_found(self, mock_get_keystone_ep):
        args = mock.MagicMock()
        args.username = 'test'
        self.assertRaises(cmscli.ConnectionError, cmscli.get_token,
                          'a', args, 'c')

    @mock.patch.object(cmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(cmscli.requests, 'post')
    def test_get_token_errors(self, mock_post, mock_get_keystone_ep):
        # Bad status code
        my_response = mock.MagicMock()
        my_response.status_code = 201
        mock_post.return_value = my_response
        self.assertRaises(cmscli.ConnectionError, cmscli.get_token,
                          3, mock.MagicMock(), 'c')

        # Post fails
        mock_post.side_effect = ValueError('test')
        self.assertRaises(cmscli.ConnectionError, cmscli.get_token,
                          3, mock.MagicMock(), 'c')

    @mock.patch.object(cmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(cmscli.requests, 'post')
    @mock.patch.object(cmscli.requests, 'get')
    def test_list_customers(self, mock_get, mock_post, mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.return_value = self.mock_response
        args = ormcli.main('orm cms list_customers t'.split())
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn(json.dumps(TJ), output)

#    @mock.patch.object(cmscli.cli_common, 'get_keystone_ep')
#    @mock.patch.object(cmscli.requests, 'post')
#    @mock.patch.object(cmscli.requests, 'get')
#    @mock.patch.object(cmscli, 'get_token')
#    def test_list_customers_a(self, mock_get_token,
#                              mock_get, mock_post, mock_get_keystone_ep):
#        mock_post.return_value = self.respond(TJ, 200)
#        mock_get.return_value = self.mock_response
#        mock_get.__name__ = 'a'
#        args = ormcli.main('orm cms --verbose list_customers t'.split())
#        sys.stdout.seek(0)
#        output = sys.stdout.read()
#        self.assertIn(json.dumps(TJ), output)

    @mock.patch.object(cmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(cmscli.requests, 'post')
    @mock.patch.object(cmscli.requests, 'get')
    def test_list_customers_e(self, mock_get, mock_post, mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.side_effect = Exception('e')
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm cms list_customers t'.split())
        self.assertEqual(cm.exception.code, 1)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('e', output)

    @mock.patch.object(cmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(cmscli.requests, 'post')
    @mock.patch.object(cmscli.requests, 'get')
    @mock.patch.object(cmscli, 'get_token')
    @mock.patch.object(cmscli, 'globals')
    def test_list_customers_errors(self, mock_globals, mock_get_token,
                                   mock_get, mock_post,
                                   mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.return_value = self.respond(TJ, 204, oy=True)
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm cms list_customers t'.split())
        self.assertEqual(cm.exception.code, 0)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertEqual('', output)

#    def test_parsing(self):
#        cli = ormcli.Cli()
#        cli.create_parser()
#        cli.parse(
#            'orm cms --orm-base-url 12.11.10.9 --port 8832 --timeout 150 '
#            'add_user '
#            'client1 customer1 region1 '
#            'ormcli/tests/data/cms-add-cust.json'.split())
#        args = cli.args
#        self.assertEqual(args.orm_base_url, '12.11.10.9')
#        self.assertEqual(args.port, 8832)
#        self.assertEqual(args.timeout, 150)
#
#    @mock.patch('requests.post')
#    def test_timeout(self, mock_post):
#        mock_post.side_effect = Exception("timeout boom")
#        cli = ormcli.Cli()
#        cli.create_parser()
#        cli.parse(
#            'orm cms --faceless add_user client1 customer1 region1 '
#            'ormcli/tests/data/cms-add-cust.json'.split())
#        with self.assertRaises(SystemExit) as cm:
#            cli.logic()
#        self.assertEqual(cm.exception.code, 1)
#        sys.stdout.seek(0)
#        output = sys.stdout.read()
#        self.assertIn('timeout boom', output)
#
#    @mock.patch('requests.post')
#    @mock.patch.object(cmscli, 'get_token')
#    def test_no_keystone(self, mock_get_token, mock_post):
#        mock_post.side_effect = Exception("timeout boom")
#        cli = ormcli.Cli()
#        cli.create_parser()
#        cli.parse(
#            'orm cms add_user client1 customer1 region1 '
#            'ormcli/tests/data/cms-add-cust.json'.split())
#        with self.assertRaises(SystemExit) as cm:
#            cli.logic()
#
#    @mock.patch('requests.post')
#    @mock.patch.object(cmscli, 'get_token')
#    def test_response_code(self, mock_get_token, mock_post):
#        cli = ormcli.Cli()
#        cli.create_parser()
#        cli.parse(
#            'orm cms create_customer client1 '
#            'ormcli/tests/data/cms-add-cust.json'.split())
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
#            'orm cms create_customer client1 '
#            'ormcli/tests/data/cms-add-cust.json'.split())
#        mock_post.return_value = self.respond(
#            {"access": {"token": {"id": 989}}}, 200)

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_list_customers(self, mock_post, mock_get):
        cli = ormcli.Cli()
        cli.create_parser()
        cli.parse(
            'orm cms list_customers --region 2 --user bob client1'.split())
        resp = self.respond('{"Hi, mom"}', 200, {'X-Subject-Token': 989})
        mock_post.return_value = self.respond(
            {"access": {"token": {"id": 989}}}, 200)
