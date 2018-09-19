#!/usr/bin/python
import argparse
import config
import orm.base_config as base_config
import os
import requests

from orm.orm_client.ormcli import cli_common


class ResponseError(Exception):
    pass


class ConnectionError(Exception):
    pass


def add_to_parser(service_sub):
    parser = service_sub.add_parser('ims',
                                    help='Image Management Service',
                                    formatter_class=lambda prog: argparse.
                                    HelpFormatter(prog,
                                                  max_help_position=30,
                                                  width=120))
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--auth-region', type=str,
                        help='Region used for authentication',
                        default=get_environment_variable('auth-region'))
    parser.add_argument('--tenant-name', type=str,
                        help='Keystone user tenant name',
                        default=get_environment_variable('tenant-name'))
    parser.add_argument('--username', type=str, help='Keystone user name',
                        default=get_environment_variable('username'))
    parser.add_argument('--password', type=str, help='Keystone user password',
                        default=get_environment_variable('password'))
    parser.add_argument('--orm-base-url', type=str, help='ORM base URL',
                        default=get_environment_variable('orm-base-url'))
    parser.add_argument('--tracking_id', type=str, help='tracking id')
    parser.add_argument('--port', type=int, help='port number of IMS server')
    parser.add_argument('--timeout', type=int,
                        help='request timeout in seconds (default: 10)')
    parser.add_argument('-v', '--verbose', help='show details',
                        action="store_true")
    parser.add_argument('-f', '--faceless',
                        help=argparse.SUPPRESS,
                        default=False,
                        action="store_true")
    subparsers = parser.add_subparsers(dest='subcmd',
                                       metavar='<subcommand> [-h] <args>')

    # image
    h1, h2 = '[<"X-RANGER-Client" header>]', '<data file with new image JSON>'
    parser_create_image = subparsers.add_parser('create_image',
                                                help='%s %s' % (h1, h2))
    parser_create_image.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_create_image.add_argument('datafile', type=argparse.FileType('r'),
                                     help=h2)

    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<image id>', \
                 '<data file with updated image JSON>'
    parser_update_image = subparsers.add_parser('update_image',
                                                help='%s %s %s' % (h1,
                                                                   h2,
                                                                   h3))
    parser_update_image.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_update_image.add_argument('imageid', type=str, help=h2)
    parser_update_image.add_argument('datafile', type=argparse.FileType('r'),
                                     help=h3)

    h1, h2 = '[<"X-RANGER-Client" header>]', '<image id>'
    parser_delete_image = subparsers.add_parser('delete_image',
                                                help='%s %s' % (h1, h2))
    parser_delete_image.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_image.add_argument('imageid', type=str, help=h2)

    # get images
    h1, h2 = '[<"X-RANGER-Client" header>]', '<image id or image name>'
    parser_get_image = subparsers.add_parser('get_image',
                                             help='%s %s' % (h1, h2))
    parser_get_image.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_get_image.add_argument('imageid', type=str, help=h2)

    h1, h2 = '[<"X-RANGER-Client" header>]', \
             '[--visibility <public|private>] ' \
             '[--region <name>] [--customer <id>]'
    parser_list_images = subparsers.add_parser('list_images',
                                               help='%s %s' % (h1, h2))
    parser_list_images.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_list_images.add_argument('--visibility', type=str,
                                    choices=['public', 'private'])
    parser_list_images.add_argument('--region', type=str, help='region name')
    parser_list_images.add_argument('--customer', type=str, help='customer id')

    # activate/deactivate image
    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<image id>', \
                 '<data file with true/false JSON>'
    parser_enable_image = subparsers.add_parser('enabled',
                                                help='%s %s %s' % (h1, h2, h3))
    parser_enable_image.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_enable_image.add_argument('imageid', type=str, help=h2)
    parser_enable_image.add_argument('datafile',
                                     type=argparse.FileType('r'),
                                     help=h3)

    # region for image
    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<image id>', \
                 '<data file with region(s) JSON>'
    parser_add_regions = subparsers.add_parser('add_regions',
                                               help='%s %s %s' % (h1, h2, h3))
    parser_add_regions.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_add_regions.add_argument('imageid', type=str, help=h2)
    parser_add_regions.add_argument('datafile',
                                    type=argparse.FileType('r'),
                                    help=h3)

    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<image id>', \
                 '<data file with region(s) JSON>'
    parser_update_regions = subparsers.add_parser('update_regions',
                                                  help='%s %s %s' % (h1,
                                                                     h2,
                                                                     h3))
    parser_update_regions.add_argument('client',
                                       **cli_common.ORM_CLIENT_KWARGS)
    parser_update_regions.add_argument('imageid', type=str, help=h2)
    parser_update_regions.add_argument('datafile',
                                       type=argparse.FileType('r'),
                                       help=h3)

    h1, h2, h3 = '[<"X-RANGER-Client" header>] [--force_delete]', \
                 '<image id>', '<region id>'
    parser_delete_region = subparsers.add_parser('delete_region',
                                                 help='%s %s %s' % (h1,
                                                                    h2,
                                                                    h3))
    parser_delete_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_region.add_argument('imageid', type=str, help=h2)
    parser_delete_region.add_argument('regionid', type=str, help=h3)
    parser_delete_region.add_argument('--force_delete',
                                      help='force delete region',
                                      action="store_true")

    # customer for image
    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<image id>', \
                 '<data file with customer(s) JSON>'
    parser_add_customers = subparsers.add_parser('add_customers',
                                                 help='%s %s %s' % (h1,
                                                                    h2,
                                                                    h3))
    parser_add_customers.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_add_customers.add_argument('imageid', type=str, help=h2)
    parser_add_customers.add_argument('datafile',
                                      type=argparse.FileType('r'),
                                      help=h3)

    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<image id>', \
                 '<data file with customer(s) JSON>'
    parser_update_customer = subparsers.add_parser('update_customers',
                                                   help='%s %s %s' % (h1,
                                                                      h2,
                                                                      h3))
    parser_update_customer.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_update_customer.add_argument('imageid', type=str, help=h2)
    parser_update_customer.add_argument('datafile',
                                        type=argparse.FileType('r'),
                                        help=h3)

    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<image id>', \
                 '<customer id>'
    parser_delete_customer = subparsers.add_parser('delete_customer',
                                                   help='%s %s %s' % (h1,
                                                                      h2,
                                                                      h3))
    parser_delete_customer.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_customer.add_argument('imageid', type=str, help=h2)
    parser_delete_customer.add_argument('customerid', type=str, help=h3)


def get_token(timeout, args, host):
    headers = {
        'Content-Type': 'application/json',
    }
    url = '%s/v3/auth/tokens'
    data = '''
{
   "auth":{
      "identity":{
         "methods":[
            "password"
         ],
         "password":{
            "user":{
               "domain":{
                  "name":"%s"
               },
               "name":"%s",
               "password":"%s"
            }
         }
      },
      "scope":{
         "project":{
            "name":"%s",
            "domain":{
               "id":"%s"
            }
         }
      }
   }
}'''
    for argument in ('tenant_name', 'username', 'password', 'auth_region'):
        argument_value = getattr(args, argument, None)
        if argument_value is not None:
            globals()[argument] = argument_value
        else:
            configuration_value = getattr(config, argument)
            if configuration_value:
                globals()[argument] = configuration_value
            else:
                message = ('ERROR: {} for token generation was not supplied. '
                           'Please use its command-line argument or '
                           'environment variable.'.format(argument))
                print message
                raise cli_common.MissingArgumentError(message)

    keystone_ep = cli_common.get_keystone_ep(
        '{}:{}'.format(host, base_config.rms['port']), auth_region)
    if keystone_ep is None:
        raise ConnectionError(
            'Failed in get_token, host: {}, region: {}'.format(host,
                                                               auth_region))
    url = url % (keystone_ep,)
    data = data % (base_config.user_domain_name, username, password, tenant_name, base_config.project_domain_name,)

    if args.verbose:
        print(
            "Getting token:\ntimeout: %d\nheaders: %s\nurl: %s\n" % (
                timeout, headers, url))
    try:
        resp = requests.post(url, timeout=timeout, data=data, headers=headers)
        if resp.status_code != 201:
            raise ResponseError(
                'Failed to get token (Reason: {})'.format(
                    resp.status_code))
        return resp.headers['x-subject-token']

    except Exception as e:
        print e.message
        raise ConnectionError(e.message)


def preparm(p):
    return ('' if len(p) else '?') + ('&' if len(p) else '')


def cmd_details(args):
    if args.subcmd == 'create_image':
        return requests.post, ''
    elif args.subcmd == 'update_image':
        return requests.put, '/%s' % args.imageid

    elif args.subcmd == 'delete_image':
        return requests.delete, '/%s' % args.imageid

    # activate/deactivate image
    elif args.subcmd == 'enabled':
        return requests.put, '/%s/enabled' % args.imageid

    # image regions
    elif args.subcmd == 'add_regions':
        return requests.post, '/%s/regions' % args.imageid
    elif args.subcmd == 'update_regions':
        return requests.put, '/%s/regions' % args.imageid
    elif args.subcmd == 'delete_region':
        return requests.delete, '/%s/regions/%s/%s' % (args.imageid,
                                                       args.regionid,
                                                       args.force_delete)

    # image customers
    elif args.subcmd == 'add_customers':
        return requests.post, '/%s/customers' % args.imageid
    elif args.subcmd == 'update_customers':
        return requests.put, '/%s/customers' % args.imageid
    elif args.subcmd == 'delete_customer':
        return requests.delete, '/%s/customers/%s' % (args.imageid,
                                                      args.customerid)

    # list images
    elif args.subcmd == 'get_image':
        return requests.get, '/%s' % args.imageid
    elif args.subcmd == 'list_images':
        param = ''
        if args.visibility:
            param += '%svisibility=%s' % (preparm(param),
                                          args.visibility)
        if args.region:
            param += '%sregion=%s' % (preparm(param),
                                      args.region)
        if args.customer:
            param += '%scustomer=%s' % (preparm(param),
                                        args.customer)
        return requests.get, '/%s' % param


def cmd_data(args):
    # This is a special case where api has a payload needed but the CLI is
    # seperated into 2 different commands. In this case we need to set the
    # payload.
    if args.subcmd == 'enabled':
        return "{\n            \"enabled\": true\n}"
    else:
        return args.datafile.read() if 'datafile' in args else '{}'


def get_environment_variable(argument):
    # The rules are: all caps, underscores instead of dashes and prefixed
    environment_variable = 'RANGER_{}'.format(
        argument.replace('-', '_').upper())

    return os.environ.get(environment_variable)


def run(args):
    host = args.orm_base_url if args.orm_base_url else config.orm_base_url
    port = args.port if args.port else 8084
    data = args.datafile.read() if 'datafile' in args else '{}'
    timeout = args.timeout if args.timeout else 10

    rest_cmd, cmd_url = cmd_details(args)
    url = '%s:%d/v1/orm/images' % (host, port,) + cmd_url
    if args.faceless:
        auth_token = auth_region = requester = client = ''
    else:
        try:
            auth_token = get_token(timeout, args, host)
        except Exception:
            exit(1)
        auth_region = globals()['auth_region']
        requester = globals()['username']
        client = requester

    tracking_id = args.tracking_id if args.tracking_id else None
    headers = {
        'content-type': 'application/json',
        'X-Auth-Token': auth_token,
        'X-Auth-Region': auth_region,
        'X-RANGER-Requester': requester,
        'X-RANGER-Client': client,
        'X-RANGER-Tracking-Id': tracking_id
    }

    if args.verbose:
        print("Sending API:\ntimeout: %d\ndata: %s\n"
              "headers: %s\ncmd: %s\nurl: %s\n" % (timeout,
                                                   data,
                                                   headers,
                                                   rest_cmd.__name__,
                                                   url))
    try:
        resp = rest_cmd(url, timeout=timeout, data=data, headers=headers,
                        verify=config.verify)
    except Exception as e:
        print e
        exit(1)

    if not 200 <= resp.status_code < 300:
        content = resp.content
        print 'API error: %s %s (Reason: %d)\n%s' % (
            rest_cmd.func_name.upper(),
            url,
            resp.status_code,
            content)
        exit(1)

    if resp.status_code == 204:  # no content
        exit(0)

    rj = resp.json()
    if rj == 'Not found':
        print 'No output was found'
    else:
        cli_common.pretty_print_json(rj)
