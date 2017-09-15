from cStringIO import StringIO
import json
import mock
from orm.orm_client.ormcli import fmscli
from orm.orm_client.ormcli import ormcli
import requests
import sys
from unittest import TestCase

TJ = {'access': {'token': {'id': 'test'}}}


class FmsTests(TestCase):
    def setUp(self):
        out, sys.stdout, err, sys.stderr = sys.stdout, StringIO(), sys.stderr, StringIO()
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
        args.flavorid = 'test_flavorid'
        args.regionid = 'test_region'
        args.region = 'test_region'
        args.tagname = 'test_tagname'
        args.eskeyname = 'test_eskeyname'
        args.visibility = 'test_visibility'
        args.tenant = 'test_tenant'
        args.series = 'test_series'
        args.starts_with = 'test_startswith'
        args.contains = 'test_contains'
        args.alias = 'test_alias'
        list_flavors_url = '/?visibility=%s&region=%s&tenant=%s&series=%s' \
                           '&starts_with=%s&contains=%s&alias=%s'
        subcmd_to_result = {
            'create_flavor': (requests.post, '',),
            'delete_flavor': (requests.delete, '/%s' % args.flavorid,),
            'add_region': (requests.post, '/%s/regions' % args.flavorid,),
            'add_tags': (requests.post, '/%s/tags' % args.flavorid,),
            'replace_tags': (requests.put, '/%s/tags' % args.flavorid,),
            'delete_tag': (
                requests.delete,
                '/%s/tags/%s' % (args.flavorid, args.tagname),),
            'delete_all_tags': (requests.delete, '/%s/tags' % args.flavorid,),
            'get_tags': (requests.get, '/%s/tags' % args.flavorid,),
            'delete_region': (requests.delete, '/%s/regions/%s' % (
                args.flavorid, args.regionid),),
            'add_tenant': (requests.post, '/%s/tenants' % args.flavorid,),
            'delete_tenant': (requests.delete, '/%s/tenants/%s' % (
                args.flavorid, args.tenantid),),
            'get_flavor': (requests.get, '/%s' % args.flavorid,),
            'get_extra_specs': (
                requests.get, '/%s/os_extra_specs' % args.flavorid,),
            'delete_all_extra_specs': (
                requests.delete, '/%s/os_extra_specs' % args.flavorid,),
            'delete_extra_spec': (requests.delete, '/%s/os_extra_specs/%s' % (
                args.flavorid, args.eskeyname),),
            'add_extra_specs': (
                requests.post, '/%s/os_extra_specs' % args.flavorid,),
            'list_flavors': (requests.get,
                             list_flavors_url % (args.visibility, args.region,
                                                 args.tenant, args.series,
                                                 args.starts_with,
                                                 args.contains, args.alias))
        }

        # Assert that each subcommand returns the expected details
        for subcmd in subcmd_to_result:
            args.subcmd = subcmd
            self.assertEqual(subcmd_to_result[subcmd],
                             fmscli.cmd_details(args))

    @mock.patch.object(fmscli.cli_common, 'get_keystone_ep',
                       return_value=None)
    def test_get_token_keystone_ep_not_found(self, mock_get_keystone_ep):
        args = mock.MagicMock()
        args.username = 'test'
        self.assertRaises(fmscli.ConnectionError, fmscli.get_token,
                          'a', args, 'c')

    @mock.patch.object(fmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(fmscli.requests, 'post')
    def test_get_token_errors(self, mock_post, mock_get_keystone_ep):
        # Bad status code
        my_response = mock.MagicMock()
        my_response.status_code = 201
        mock_post.return_value = my_response
        self.assertRaises(fmscli.ConnectionError, fmscli.get_token,
                          3, mock.MagicMock(), 'c')

        # Post fails
        mock_post.side_effect = ValueError('test')
        self.assertRaises(fmscli.ConnectionError, fmscli.get_token,
                          3, mock.MagicMock(), 'c')

    @mock.patch.object(fmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(fmscli.requests, 'post')
    @mock.patch.object(fmscli.requests, 'get')
    @mock.patch.object(fmscli, 'get_token')
    @mock.patch.object(fmscli, 'globals')
    def test_list_flavors(self, mock_globals, mock_get_token,
                          mock_get, mock_post, mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.return_value = self.mock_response
        args = ormcli.main('orm fms list_flavors t'.split())
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn(json.dumps(TJ), output)

    @mock.patch.object(fmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(fmscli.requests, 'post')
    @mock.patch.object(fmscli.requests, 'get')
    @mock.patch.object(fmscli, 'get_token')
    @mock.patch.object(fmscli, 'globals')
    def test_list_flavors_a(self, mock_globals, mock_get_token,
                            mock_get, mock_post, mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.return_value = self.mock_response
        mock_get.__name__ = 'a'
        args = ormcli.main('orm fms --verbose list_flavors t'.split())
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn(json.dumps(TJ), output)

    @mock.patch.object(fmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(fmscli.requests, 'post')
    @mock.patch.object(fmscli.requests, 'get')
    def test_list_flavors_e(self, mock_get, mock_post, mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.side_effect = Exception('e')
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm fms list_flavors t'.split())
        self.assertEqual(cm.exception.code, 1)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('e', output)

    @mock.patch.object(fmscli.cli_common, 'get_keystone_ep')
    @mock.patch.object(fmscli.requests, 'post')
    @mock.patch.object(fmscli.requests, 'get')
    @mock.patch.object(fmscli, 'get_token')
    @mock.patch.object(fmscli, 'globals')
    def test_list_flavors_errors(self, mock_globals, mock_get_token,
                                 mock_get, mock_post,
                                 mock_get_keystone_ep):
        mock_post.return_value = self.respond(TJ, 200)
        mock_get.return_value = self.respond(TJ, 204, oy=True)
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm fms list_flavors t'.split())
        self.assertEqual(cm.exception.code, 0)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertEqual('', output)

        mock_get.return_value = self.respond(TJ, 404, oy=True)
        with self.assertRaises(SystemExit) as cm:
            args = ormcli.main('orm fms --faceless list_flavors t'.split())
        self.assertEqual(cm.exception.code, 1)
        sys.stdout.seek(0)
        output = sys.stdout.read()
        self.assertIn('API error:', output)
