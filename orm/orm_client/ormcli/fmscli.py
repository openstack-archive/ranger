#!/usr/bin/python
import argparse
import cli_common
import config
import os
import requests


class ResponseError(Exception):
    pass


class ConnectionError(Exception):
    pass


def add_to_parser(service_sub):
    parser = \
        service_sub.add_parser('fms', help='Flavor Management Service',
                               formatter_class=lambda prog:
                               argparse.HelpFormatter(prog,
                                                      max_help_position=30,
                                                      width=120))
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--auth-region', type=str,
                        help='Region used for authentication',
                        default=get_environment_variable('auth-region'))
    parser.add_argument('--orm-base-url', type=str, help='ORM base URL',
                        default=get_environment_variable('orm-base-url'))
    parser.add_argument('--tracking_id', type=str, help='tracking id')
    parser.add_argument('--tenant-name', type=str,
                        help='Keystone user tenant name',
                        default=get_environment_variable('tenant-name'))
    parser.add_argument('--username', type=str, help='Keystone user name',
                        default=get_environment_variable('username'))
    parser.add_argument('--password', type=str, help='Keystone user password',
                        default=get_environment_variable('password'))
    parser.add_argument('--port', type=int, help='port number of FMS server')
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

    # flavor
    h1, h2 = ('[<"X-RANGER-Client" header>]',
              '<data file with new flavor JSON>')
    parser_create_flavor = subparsers.add_parser('create_flavor',
                                                 help='%s %s' % (h1, h2))
    parser_create_flavor.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_create_flavor.add_argument('datafile', type=argparse.FileType('r'),
                                      help=h2)

    h1, h2, h3 = ('[<"X-RANGER-Client" header>]', '<flavor id>',
                  '<data file with tag(s) JSON>',)
    parser_add_tags = subparsers.add_parser('add_tags',
                                            help='%s %s %s' % (h1, h2, h3))
    parser_add_tags.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_add_tags.add_argument('flavorid', type=str, help=h2)
    parser_add_tags.add_argument('datafile', type=argparse.FileType('r'),
                                 help=h3)

    h1, h2, h3 = ('[<"X-RANGER-Client" header>]', '<flavor id>',
                  '<data file with tag(s) JSON>',)
    parser_replace_tags = subparsers.add_parser('replace_tags',
                                                help='%s %s %s' % (h1, h2, h3))
    parser_replace_tags.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_replace_tags.add_argument('flavorid', type=str, help=h2)
    parser_replace_tags.add_argument('datafile', type=argparse.FileType('r'),
                                     help=h3)

    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<flavor id>', '<tag name>'
    parser_delete_tag = subparsers.add_parser('delete_tag',
                                              help='%s %s %s' % (h1, h2, h3))
    parser_delete_tag.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_tag.add_argument('flavorid', type=str, help=h2)
    parser_delete_tag.add_argument('tagname', type=str, help=h3)

    h1, h2 = '[<"X-RANGER-Client" header>]', '<flavor id>'
    parser_delete_all_tags = subparsers.add_parser('delete_all_tags',
                                                   help='%s %s' % (h1, h2))
    parser_delete_all_tags.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_all_tags.add_argument('flavorid', type=str, help=h2)

    h1, h2 = '[<"X-RANGER-Client" header>]', '<flavor id>'
    parser_get_tags = subparsers.add_parser('get_tags',
                                            help='%s %s' % (h1, h2))
    parser_get_tags.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_get_tags.add_argument('flavorid', type=str, help=h2)

    # extra specs
    h1, h2 = '[<"X-RANGER-Client" header>]', '<flavor id>'
    parser_get_extra_specs = subparsers.add_parser('get_extra_specs',
                                                   help='%s %s' % (h1, h2))
    parser_get_extra_specs.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_get_extra_specs.add_argument('flavorid', type=str, help=h2)

    h1, h2, h3 = ('[<"X-RANGER-Client" header>]', '<flavor id>',
                  '<datafile with extra_specs json>',)
    parser_replace_extra_specs = subparsers.add_parser('replace_extra_specs',
                                                       help='%s %s %s' % (h1,
                                                                          h2,
                                                                          h3))
    parser_replace_extra_specs.add_argument('client',
                                            **cli_common.ORM_CLIENT_KWARGS)
    parser_replace_extra_specs.add_argument('flavorid', type=str, help=h2)
    parser_replace_extra_specs.add_argument('datafile',
                                            type=argparse.FileType('r'),
                                            help=h3)

    h1, h2 = '[<"X-RANGER-Client" header>]', '<flavor id>'
    parser_delete_all_extra_specs = subparsers.add_parser(
        'delete_all_extra_specs', help='%s %s' % (h1, h2))
    parser_delete_all_extra_specs.add_argument('client',
                                               **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_all_extra_specs.add_argument('flavorid', type=str, help=h2)

    h1, h2, h3 = ('[<"X-RANGER-Client" header>]', '<flavor id>',
                  '<extra_spec key name>',)
    parser_delete_extra_spec = subparsers.add_parser('delete_extra_spec',
                                                     help='%s%s%s' % (
                                                         h1, h2, h3))
    parser_delete_extra_spec.add_argument('client',
                                          **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_extra_spec.add_argument('flavorid', type=str, help=h2)
    parser_delete_extra_spec.add_argument('eskeyname', type=str, help=h3)

    h1, h2, h3 = ('[<"X-RANGER-Client" header>]', '<flavor id>',
                  '<datafile with extra_specs json>',)
    parser_add_extra_specs = subparsers.add_parser('add_extra_specs',
                                                   help='%s%s%s' % (
                                                       h1, h2, h3))
    parser_add_extra_specs.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_add_extra_specs.add_argument('flavorid', type=str, help=h2)
    parser_add_extra_specs.add_argument('datafile',
                                        type=argparse.FileType('r'),
                                        help=h3)

    h1, h2 = '[<"X-RANGER-Client" header>]', '<flavor id>'
    parser_delete_flavor = subparsers.add_parser('delete_flavor',
                                                 help='%s %s' % (h1, h2))
    parser_delete_flavor.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_flavor.add_argument('flavorid', type=str, help=h2)

    h1, h2 = '[<"X-RANGER-Client" header>]', '<flavor id or flavor_name>'
    parser_get_flavor = subparsers.add_parser('get_flavor',
                                              help='%s %s' % (h1, h2))
    parser_get_flavor.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_get_flavor.add_argument('flavorid', type=str, help=h2)

    h1, h2 = ('[<"X-RANGER-Client" header>]',
              '[--visibility <public|private>] [--region <name>] [--tenant '
              '<id>] [--series {gv,nv,ns,nd,ss}] [--alias <alias>]')
    parser_list_flavor = subparsers.add_parser('list_flavors',
                                               help='%s %s' % (h1, h2))
    parser_list_flavor.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_list_flavor.add_argument('--visibility', type=str,
                                    choices=['public', 'private'])
    parser_list_flavor.add_argument('--region', type=str, help='region name')
    parser_list_flavor.add_argument('--tenant', type=str, help='tenant id')
    parser_list_flavor.add_argument('--starts_with', type=str,
                                    help='flavor name starts with *')
    parser_list_flavor.add_argument('--contains', type=str,
                                    help='* contains in flavor name')
    parser_list_flavor.add_argument('--series', type=str,
                                    choices=['gv', 'nv', 'ns', 'nd', 'ss'])
    parser_list_flavor.add_argument('--alias', type=str, help='flavor alias')

    # region for flavor
    h1, h2, h3 = ('[<"X-RANGER-Client" header>]', '<flavor id>',
                  '<data file with region(s) JSON>',)
    parser_add_region = subparsers.add_parser('add_region',
                                              help='%s %s %s' % (h1, h2, h3))
    parser_add_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_add_region.add_argument('flavorid', type=str, help=h2)
    parser_add_region.add_argument('datafile', type=argparse.FileType('r'),
                                   help=h3)

    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<flavor id>', '<region id>'
    parser_delete_region = subparsers.add_parser('delete_region',
                                                 help='%s %s %s' % (
                                                     h1, h2, h3))
    parser_delete_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_region.add_argument('flavorid', type=str, help=h2)
    parser_delete_region.add_argument('regionid', type=str, help=h3)

    # tenant for flavor
    h1, h2, h3 = ('[<"X-RANGER-Client" header>]', '<flavor id>',
                  '<data file with tenant(s) JSON>',)
    parser_add_tenant = subparsers.add_parser('add_tenant',
                                              help='%s %s %s' % (h1, h2, h3))
    parser_add_tenant.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_add_tenant.add_argument('flavorid', type=str, help=h2)
    parser_add_tenant.add_argument('datafile', type=argparse.FileType('r'),
                                   help=h3)

    h1, h2, h3 = '[<"X-RANGER-Client" header>]', '<flavor id>', '<tenant id>'
    parser_delete_tenant = subparsers.add_parser('delete_tenant',
                                                 help='%s %s %s' % (
                                                     h1, h2, h3))
    parser_delete_tenant.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_tenant.add_argument('flavorid', type=str, help=h2)
    parser_delete_tenant.add_argument('tenantid', type=str, help=h3)


def preparm(p):
    return ('' if len(p) else '?') + ('&' if len(p) else '')


def cmd_details(args):
    if args.subcmd == 'create_flavor':
        return requests.post, ''
    elif args.subcmd == 'update_flavor':
        return requests.put, '/%s' % args.flavorid
    elif args.subcmd == 'delete_flavor':
        return requests.delete, '/%s' % args.flavorid
    elif args.subcmd == 'add_region':
        return requests.post, '/%s/regions' % args.flavorid
    elif args.subcmd == 'add_tags':
        return requests.post, '/%s/tags' % args.flavorid
    elif args.subcmd == 'replace_tags':
        return requests.put, '/%s/tags' % args.flavorid
    elif args.subcmd == 'delete_tag':
        return requests.delete, '/%s/tags/%s' % (args.flavorid, args.tagname)
    elif args.subcmd == 'delete_all_tags':
        return requests.delete, '/%s/tags' % args.flavorid
    elif args.subcmd == 'get_tags':
        return requests.get, '/%s/tags' % args.flavorid
    elif args.subcmd == 'delete_region':
        return requests.delete, '/%s/regions/%s' % (
            args.flavorid, args.regionid)
    elif args.subcmd == 'add_tenant':
        return requests.post, '/%s/tenants' % args.flavorid
    elif args.subcmd == 'delete_tenant':
        return requests.delete, '/%s/tenants/%s' % (
            args.flavorid, args.tenantid)
    elif args.subcmd == 'get_flavor':
        return requests.get, '/%s' % args.flavorid
    elif args.subcmd == 'get_extra_specs':
        return requests.get, '/%s/os_extra_specs' % args.flavorid
    elif args.subcmd == 'delete_all_extra_specs':
        return requests.delete, '/%s/os_extra_specs' % args.flavorid
    elif args.subcmd == 'delete_extra_spec':
        return requests.delete, '/%s/os_extra_specs/%s' % (
            args.flavorid, args.eskeyname)
    elif args.subcmd == 'add_extra_specs':
        return requests.post, '/%s/os_extra_specs' % args.flavorid
    elif args.subcmd == 'replace_extra_specs':
        return requests.put, '/%s/os_extra_specs' % args.flavorid
    elif args.subcmd == 'list_flavors':
        param = ''
        if args.visibility:
            param += '%svisibility=%s' % (preparm(param), args.visibility)
        if args.region:
            param += '%sregion=%s' % (preparm(param), args.region)
        if args.tenant:
            param += '%stenant=%s' % (preparm(param), args.tenant)
        if args.series:
            param += '%sseries=%s' % (preparm(param), args.series)
        if args.starts_with:
            param += '%sstarts_with=%s' % (preparm(param), args.starts_with)
        if args.contains:
            param += '%scontains=%s' % (preparm(param), args.contains)
        if args.alias:
            param += '%salias=%s' % (preparm(param), args.alias)
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
                           'argument or environment variable.'.format(argument))
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
    port = args.port if args.port else 8082
    data = args.datafile.read() if 'datafile' in args else '{}'
    timeout = args.timeout if args.timeout else 10

    rest_cmd, cmd_url = cmd_details(args)
    url = '%s:%d/v1/orm/flavors' % (host, port,) + cmd_url
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
        print(
            "Sending API:\ntimeout: %d\ndata: %s\nheaders: %s\ncmd: %s\nurl:"
            " %s\n" % (
                timeout, data, headers, rest_cmd.__name__, url))
    try:
        resp = rest_cmd(url, timeout=timeout, data=data, headers=headers,
                        verify=config.verify)
    except Exception as e:
        print e
        exit(1)

    if not 200 <= resp.status_code < 300:
        content = resp.content
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
