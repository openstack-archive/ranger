#!/usr/bin/python
import argparse
import cli_common
import config
import os
import requests
import sys


class ResponseError(Exception):
    pass


class ConnectionError(Exception):
    pass


def add_to_parser(service_sub):
    parser = \
        service_sub.add_parser('cms',
                               help='Customer Management Service',
                               formatter_class=lambda prog:
                               argparse.HelpFormatter(prog,
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
    parser.add_argument('--tracking_id', type=str,
                        help='"X-AIC-ORM-Tracking-Id" header')
    parser.add_argument('--port', type=int, help='port number of CMS server')
    parser.add_argument('--timeout', type=int,
                        help='request timeout in seconds (default: 10)')
    parser.add_argument('-v', '--verbose', help='show details',
                        action="store_true")
    parser.add_argument('-f', '--faceless',
                        help='run without authentication',
                        default=False,
                        action="store_true")
    subparsers = parser.add_subparsers(dest='subcmd',
                                       metavar='<subcommand> [-h] <args>')

    # customer
    parser_create_customer = subparsers.add_parser('create_customer',
                                                   help='[<"X-AIC-ORM-Client" '
                                                        'header>] <data file '
                                                        'with new customer '
                                                        'JSON>')
    parser_create_customer.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_create_customer.add_argument('datafile',
                                        type=argparse.FileType('r'),
                                        help='<data file with new customer '
                                             'JSON>')

    parser_delete_customer = subparsers.add_parser('delete_customer',
                                                   help='[<"X-AIC-ORM-Client" '
                                                        'header>] <customer '
                                                        'id>')
    parser_delete_customer.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_customer.add_argument('custid', type=str,
                                        help='<customer id>')

    parser_update_customer = subparsers.add_parser('update_customer',
                                                   help='[<"X-AIC-ORM-Client" '
                                                        'header>] <customer '
                                                        'id> <data file with '
                                                        'updated customer '
                                                        'JSON>')
    parser_update_customer.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_update_customer.add_argument('custid', type=str,
                                        help='<customer id>')
    parser_update_customer.add_argument('datafile',
                                        type=argparse.FileType('r'),
                                        help='<data file with updated '
                                             'customer JSON>')

    # region
    parser_add_region = subparsers.add_parser('add_region',
                                              help='[<"X-AIC-ORM-Client" '
                                                   'header>] <customer id> '
                                                   '<data file with region('
                                                   's) JSON>')
    parser_add_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_add_region.add_argument('custid', type=str, help='<customer id>')
    parser_add_region.add_argument('datafile', type=argparse.FileType('r'),
                                   help='<data file with region(s) JSON>')

    parser_replace_region = subparsers.add_parser('replace_region',
                                                  help='[<"X-AIC-ORM-Client" '
                                                       'header>] <customer '
                                                       'id> <data file with '
                                                       'region(s) JSON>')
    parser_replace_region.add_argument('client',
                                       **cli_common.ORM_CLIENT_KWARGS)
    parser_replace_region.add_argument('custid', type=str,
                                       help='<customer id>')
    parser_replace_region.add_argument('datafile', type=argparse.FileType('r'),
                                       help='<data file with region(s) JSON>')

    parser_delete_region = subparsers.add_parser('delete_region',
                                                 help='[<"X-AIC-ORM-Client" '
                                                      'header>] <customer id> '
                                                      '<region id>')
    parser_delete_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_region.add_argument('custid', type=str, help='<customer id>')
    parser_delete_region.add_argument('regionid', type=str, help='<region id>')

    # add user
    parser_add_user = subparsers.add_parser('add_user',
                                            help='[<"X-AIC-ORM-Client" '
                                                 'header>] <customer id> '
                                                 '<region id> <data file '
                                                 'with user(s) JSON>')
    parser_add_user.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_add_user.add_argument('custid', type=str, help='<customer id>')
    parser_add_user.add_argument('regionid', type=str, help='<region id>')
    parser_add_user.add_argument('datafile', type=argparse.FileType('r'),
                                 help='<data file with user(s) JSON>')

    # replace user
    parser_replace_user = subparsers.add_parser('replace_user',
                                                help='[<"X-AIC-ORM-Client" '
                                                     'header>] <customer id> '
                                                     '<region id> <data file '
                                                     'with user(s) JSON>')
    parser_replace_user.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_replace_user.add_argument('custid', type=str, help='<customer id>')
    parser_replace_user.add_argument('regionid', type=str, help='<region id>')
    parser_replace_user.add_argument('datafile', type=argparse.FileType('r'),
                                     help='<data file with user(s) JSON>')

    # delete user
    parser_delete_user = subparsers.add_parser(
        'delete_user',
        help='[<"X-AIC-ORM-Client" header>] '
             '<customer id> <region id> <user id>')
    parser_delete_user.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_user.add_argument('custid', type=str,
                                    help='<customer id>')
    parser_delete_user.add_argument('regionid', type=str,
                                    help='<region id>')
    parser_delete_user.add_argument('userid', type=str,
                                    help='<user id>')

    # add default user
    parser_add_default_user = \
        subparsers.add_parser('add_default_user',
                              help='[<"X-AIC-ORM-Client" header>] '
                                   '<customer id> '
                                   '<data file with '
                                   'region(s) JSON>')
    parser_add_default_user.add_argument('client',
                                         **cli_common.ORM_CLIENT_KWARGS)
    parser_add_default_user.add_argument('custid', type=str,
                                         help='<customer id>')
    parser_add_default_user.add_argument('datafile',
                                         type=argparse.FileType('r'),
                                         help='<data file with user(s) JSON>')

    # replace default user
    parser_replace_default_user = \
        subparsers.add_parser('replace_default_user',
                              help='[<"X-AIC-ORM-Client" header>] '
                                   '<customer id> '
                                   '<data file '
                                   'with region(s) '
                                   'JSON>')
    parser_replace_default_user.add_argument('client',
                                             **cli_common.ORM_CLIENT_KWARGS)
    parser_replace_default_user.add_argument('custid', type=str,
                                             help='<customer id>')
    parser_replace_default_user.add_argument('datafile',
                                             type=argparse.FileType('r'),
                                             help='<data file with user(s) '
                                                  'JSON>')

    # change enable
    parser_enable_customer = subparsers.add_parser('enabled',
                                                   help='[<"X-AIC-ORM-Client" '
                                                        'header>] '
                                                        '<customer id> '
                                                        '<data file with '
                                                        'true/false JSON>')
    parser_enable_customer.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_enable_customer.add_argument('custid', type=str,
                                        help='<customer id>')
    parser_enable_customer.add_argument('datafile',
                                        type=argparse.FileType('r'),
                                        help='<data file with true/false '
                                             'JSON>')

    # delete default user
    parser_delete_default_user = \
        subparsers.add_parser('delete_default_user',
                              help='[<"X-AIC-ORM-Client" header>] <customer '
                                   'id> <user id>')
    parser_delete_default_user.add_argument('client',
                                            **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_default_user.add_argument('custid', type=str,
                                            help='<customer id>')
    parser_delete_default_user.add_argument('userid', type=str,
                                            help='<user id>')

    # add metadata
    h1, h2, h3 = \
        '[<"X-AIC-ORM-Client" header>]', '<customer id>', '<data file ' \
                                                          'with ' \
                                                          'metadata(' \
                                                          's) JSON>'
    parser_add_metadata = subparsers.add_parser('add_metadata',
                                                help='%s %s %s' % (h1, h2, h3))
    parser_add_metadata.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_add_metadata.add_argument('custid', type=str,
                                     help=h2)
    parser_add_metadata.add_argument('datafile', type=argparse.FileType('r'),
                                     help=h3)

    # replace metadata
    h1, h2, h3 = \
        '[<"X-AIC-ORM-Client" header>]', '<customer id>', '<data file ' \
                                                          'with ' \
                                                          'metadata(' \
                                                          's) JSON>'
    parser_replace_metadata = subparsers.add_parser('replace_metadata',
                                                    help='%s %s %s' % (
                                                        h1, h2, h3))
    parser_replace_metadata.add_argument('client',
                                         **cli_common.ORM_CLIENT_KWARGS)
    parser_replace_metadata.add_argument('custid', type=str,
                                         help=h2)
    parser_replace_metadata.add_argument('datafile',
                                         type=argparse.FileType('r'),
                                         help=h3)

    # get customer
    parser_get_customer = subparsers.add_parser('get_customer',
                                                help='[<"X-AIC-ORM-Client" '
                                                     'header>] <customer id>')
    parser_get_customer.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_get_customer.add_argument('custid', type=str, help='<customer id>')

    # list customers
    h1 = '[<"X-AIC-ORM-Client" header>]'
    h2 = '[--region <name>] [--user <name>] [--metadata <key:value>]' \
         ' [starts_with <name>] [contains <name>]'
    parser_list_customer = subparsers.add_parser('list_customers',
                                                 help='%s %s' % (h1, h2))
    parser_list_customer.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_list_customer.add_argument('--region', type=str, help='region name')
    parser_list_customer.add_argument('--user', type=str, help='user name')
    parser_list_customer.add_argument('--starts_with', type=str,
                                      help='customer name')
    parser_list_customer.add_argument('--contains', type=str,
                                      help='* contains in customer name')
    parser_list_customer.add_argument('--metadata', action='append', nargs="+",
                                      type=str, help='<key:value>')

    return parser


def preparm(p):
    return ('' if len(p) else '?') + ('&' if len(p) else '')


def cmd_details(args):
    if args.subcmd == 'create_customer':
        return requests.post, ''
    elif args.subcmd == 'delete_customer':
        return requests.delete, '/%s' % args.custid
    elif args.subcmd == 'update_customer':
        return requests.put, '/%s' % args.custid
    elif args.subcmd == 'add_region':
        return requests.post, '/%s/regions' % args.custid
    elif args.subcmd == 'replace_region':
        return requests.put, '/%s/regions' % args.custid
    elif args.subcmd == 'delete_region':
        return requests.delete, '/%s/regions/%s' % (args.custid, args.regionid)
    elif args.subcmd == 'add_user':
        return requests.post, '/%s/regions/%s/users' % (
            args.custid, args.regionid)
    elif args.subcmd == 'replace_user':
        return requests.put, '/%s/regions/%s/users' % (
            args.custid, args.regionid)
    elif args.subcmd == 'delete_user':
        return requests.delete, '/%s/regions/%s/users/%s' % (
            args.custid, args.regionid, args.userid)
    elif args.subcmd == 'add_default_user':
        return requests.post, '/%s/users' % args.custid
    elif args.subcmd == 'replace_default_user':
        return requests.put, '/%s/users' % args.custid
    elif args.subcmd == 'delete_default_user':
        return requests.delete, '/%s/users/%s' % (args.custid, args.userid)
    elif args.subcmd == 'add_metadata':
        return requests.post, '/%s/metadata' % args.custid
    elif args.subcmd == 'replace_metadata':
        return requests.put, '/%s/metadata' % args.custid
    elif args.subcmd == 'get_customer':
        return requests.get, '/%s' % args.custid
    elif args.subcmd == 'enabled':
        return requests.put, '/%s/enabled' % args.custid
    elif args.subcmd == 'list_customers':
        param = ''
        if args.region:
            param += '%sregion=%s' % (preparm(param), args.region)
        if args.user:
            param += '%suser=%s' % (preparm(param), args.user)
        if args.starts_with:
            param += '%sstarts_with=%s' % (preparm(param), args.starts_with)
        if args.contains:
            param += '%scontains=%s' % (preparm(param), args.contains)
        if args.metadata:
            for meta in args.metadata:
                param += '%smetadata=%s' % (preparm(param), meta[0])
        return requests.get, '/%s' % param


def get_token(timeout, args, host):
    headers = {
        'Content-Type': 'application/json',
    }
    url = '%s/v2.0/tokens'
    data = '''
{
"auth": {
    "tenantName": "%s",
    "passwordCredentials": {
        "username": "%s",
        "password": "%s"
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
                           'Please use its command-line '
                           'argument or environment variable.'.format(
                            argument))
                print message
                raise cli_common.MissingArgumentError(message)

    keystone_ep = cli_common.get_keystone_ep('{}:8080'.format(host),
                                             auth_region)
    if keystone_ep is None:
        raise ConnectionError(
            'Failed in get_token, host: {}, region: {}'.format(host,
                                                               auth_region))
    url = url % (keystone_ep,)
    data = data % (tenant_name, username, password,)

    if args.verbose:
        print(
            "Getting token:\ntimeout: %d\nheaders: %s\nurl: %s\n" % (
                timeout, headers, url))
    try:
        resp = requests.post(url, timeout=timeout, data=data, headers=headers)
        if resp.status_code != 200:
            raise ResponseError(
                'Failed to get token (Reason: {})'.format(
                    resp.status_code))
        return resp.json()['access']['token']['id']

    except Exception as e:
        print e.message
        raise ConnectionError(e.message)


def get_environment_variable(argument):
    # The rules are: all caps, underscores instead of dashes and prefixed
    environment_variable = 'AIC_ORM_{}'.format(
        argument.replace('-', '_').upper())

    return os.environ.get(environment_variable)


def run(args):
    host = args.orm_base_url if args.orm_base_url else config.orm_base_url
    port = args.port if args.port else 7080
    data = args.datafile.read() if 'datafile' in args else '{}'
    timeout = args.timeout if args.timeout else 10

    rest_cmd, cmd_url = cmd_details(args)
    url = '%s:%d/v1/orm/customers' % (host, port,) + cmd_url
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
        'X-AIC-ORM-Requester': requester,
        'X-AIC-ORM-Client': client,
        'X-AIC-ORM-Tracking-Id': tracking_id
    }

    if args.verbose:
        print(
            "Sending API:\ntimeout: %d\ndata: %s\nheaders: %s\ncmd: %s\nurl: "
            "%s\n" % (
                timeout, data, headers, rest_cmd.__name__, url))

    try:
        resp = rest_cmd(url, timeout=timeout, data=data, headers=headers,
                        verify=config.verify)
    except Exception as e:
        print e
        exit(1)

    if not 200 <= resp.status_code < 300:
        content = resp.json() if resp.status_code == 500 else ''
        print 'API error: %s %s (Reason: %d)\n%s' % (
            rest_cmd.func_name.upper(), url, resp.status_code, content)
        exit(1)

    if resp.status_code == 204:  # no content
        exit(0)

    rj = resp.json()
    if rj == 'Not found':
        print 'No output was found'
    else:
        cli_common.pretty_print_json(rj)
