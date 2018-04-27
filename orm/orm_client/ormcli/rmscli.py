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
    parser = service_sub.add_parser('rms', help='Resource Management Service',
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
    parser.add_argument('--port', type=int, help='port number of RMS server')
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

    clnt_hdr = '[<"X-AIC-ORM-Client" header>] '

    # get group
    h1 = '<group_id>'
    parser_get_group = subparsers.add_parser('get_group', help=h1)
    parser_get_group.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_get_group.add_argument('group_id', type=str, help=h1)

    # get all groups
    parser_list_groups = subparsers.add_parser('list_groups', help="")
    parser_list_groups.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)

    # create group
    h1 = '<data file group json file>'
    parser_create_group = subparsers.add_parser('create_group',
                                                help='%s %s' % (clnt_hdr, h1))
    parser_create_group.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_create_group.add_argument('datafile', type=argparse.FileType('r'),
                                     help='<data file with new group JSON>')

    # update group
    h1, h2 = '<group_id>', '<group json file>'
    parser_update_group = subparsers.add_parser('update_group',
                                                help="%s %s %s" % (clnt_hdr,
                                                                   h1, h2))
    parser_update_group.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_update_group.add_argument('group_id', help=h2)
    parser_update_group.add_argument('datafile', type=argparse.FileType('r'),
                                     help='<data file with updated group '
                                          'JSON>')

    # delete group
    h1 = '<group id>'
    parser_delete_group = subparsers.add_parser('delete_group',
                                                help='%s %s' % (clnt_hdr, h1))
    parser_delete_group.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_group.add_argument('group_id', type=str, help=h1)

    # get region
    h1, h2 = '<region_name_or_id>', '[--use_version <api version>]'
    parser_get_region = subparsers.add_parser('get_region',
                                              help='%s %s' % (h1, h2))
    parser_get_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_get_region.add_argument('--use_version', type=int,
                                   help='<api version to use (1 or 2)>')
    parser_get_region.add_argument('region_name_or_id', type=str, help=h1)

    # update region
    h1, h2 = '<region_id>', '<full region json file>'
    parser_update_region = subparsers.add_parser('update_region',
                                                 help='%s %s %s' % (clnt_hdr,
                                                                    h1, h2))
    parser_update_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_update_region.add_argument('region_id', type=str, help=h1)
    parser_update_region.add_argument('datafile', type=argparse.FileType('r'),
                                      help='<data file with updated region '
                                      'JSON>')

    # create region
    h1 = '<full region json file>'
    parser_create_region = subparsers.add_parser('create_region',
                                                 help='%s %s' % (clnt_hdr, h1))
    parser_create_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_create_region.add_argument('datafile', type=argparse.FileType('r'),
                                      help='<data file with new region JSON>')

    # delete region
    h1 = '<region id>'
    parser_delete_region = subparsers.add_parser('delete_region',
                                                 help='%s %s' % (clnt_hdr, h1))
    parser_delete_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_region.add_argument('region_id', type=str, help=h1)

    # list regions
    parser_list_region = subparsers.add_parser('list_regions',
                                               help='\
[--use_version <api version>] [--type <type>][--status <status>]\
[--metadata <metadata>] [--aicversion <aicversion>][--clli <clli>]\
[--regionname <regionname>] [--osversion <osversion>]\
[--location_type <location_type>]\
[--state <state>] [--country <country>] [--city <city>] [--street <street>]\
[--zip <zip>] [--vlcp_name <vlcp_name>]')
    parser_list_region.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_list_region.add_argument('--use_version', type=int,
                                    help='<api version to use>')
    parser_list_region.add_argument('--type', type=str, help='<type>')
    parser_list_region.add_argument('--status', type=str, help='<status>')
    parser_list_region.add_argument('--metadata', action='append', nargs="+",
                                    type=str, help='<metadata>')
    parser_list_region.add_argument('--aicversion', type=str,
                                    help='<aicversion>')
    parser_list_region.add_argument('--clli', type=str, help='<clli>')
    parser_list_region.add_argument('--regionname', type=str,
                                    help='<regionname>')
    parser_list_region.add_argument('--osversion', type=str,
                                    help='<osversion>')
    parser_list_region.add_argument('--location_type', type=str,
                                    help='<location_type>')
    parser_list_region.add_argument('--state', type=str, help='<state>')
    parser_list_region.add_argument('--country', type=str, help='<country>')
    parser_list_region.add_argument('--city', type=str, help='<city>')
    parser_list_region.add_argument('--street', type=str, help='<street>')
    parser_list_region.add_argument('--zip', type=str, help='<zip>')
    parser_list_region.add_argument('--vlcp_name', type=str,
                                    help='<vlcp_name>')

    # add metadata to region
    h1, h2 = '<region_id>', '<metadata json file>'
    parser_add_metadata = subparsers.add_parser('add_metadata',
                                                help='%s %s %s' % (clnt_hdr,
                                                                   h1, h2))
    parser_add_metadata.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_add_metadata.add_argument('region_id', type=str, help=h1)
    parser_add_metadata.add_argument('datafile', type=argparse.FileType('r'),
                                     help=h2)

    # update region's metadata
    h1, h2 = '<region_id>', '<metadata json file>'
    parser_update_metadata = subparsers.add_parser('update_metadata',
                                                   help='%s %s %s' % (clnt_hdr,
                                                                      h1, h2))
    parser_update_metadata.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_update_metadata.add_argument('region_id', type=str, help=h1)
    parser_update_metadata.add_argument('datafile',
                                        type=argparse.FileType('r'),
                                        help=h2)
    # delete metadata key from region
    h1, h2 = '<region id>', '<metadata key>'
    parser_delete_metadata = subparsers.add_parser('delete_metadata',
                                                   help='%s %s %s' % (clnt_hdr,
                                                                      h1, h2))
    parser_delete_metadata.add_argument('client',
                                        **cli_common.ORM_CLIENT_KWARGS)
    parser_delete_metadata.add_argument('region_id', type=str, help=h1)
    parser_delete_metadata.add_argument('metadata_key', type=str, help=h2)

    # get region's metadata
    h1 = '<region id>'
    parser_get_metadata = subparsers.add_parser('get_metadata',
                                                help='%s' % (h1))
    parser_get_metadata.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_get_metadata.add_argument('region_id', type=str, help=h1)

    # update region's status
    h1, h2 = '<region_id>', '<status>'
    parser_update_status = subparsers.add_parser('update_status',
                                                 help='%s %s %s' % (clnt_hdr,
                                                                    h1, h2))
    parser_update_status.add_argument('client', **cli_common.ORM_CLIENT_KWARGS)
    parser_update_status.add_argument('region_id', type=str, help=h1)
    parser_update_status.add_argument('status', type=str, help=h2)


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
            # If it does not exist in the configuration, we would like the
            # exception to be raised
            configuration_value = getattr(config, argument)
            if configuration_value:
                globals()[argument] = configuration_value
            else:
                message = ('ERROR: {} for token generation was not supplied. '
                           'Please use its command-line argument or '
                           'environment variable.'.format(argument))
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


def preparm(p):
    return ('' if len(p) else '?') + ('&' if len(p) else '')


def cmd_details(args):
    if args.subcmd == 'get_region':
        return requests.get, '/%s' % args.region_name_or_id
    elif args.subcmd == 'create_region':
        return requests.post, ''
    elif args.subcmd == 'update_region':
        return requests.put, '/%s' % args.region_id
    elif args.subcmd == 'delete_region':
        return requests.delete, '/%s' % args.region_id
    elif args.subcmd == 'list_regions':
        param = ''
        if args.type:
            param += '%stype=%s' % (preparm(param), args.type)
        if args.status:
            param += '%sstatus=%s' % (preparm(param), args.status)
        if args.metadata:
            for meta in args.metadata:
                param += '%smetadata=%s' % (preparm(param), meta[0])
        if args.aicversion:
            param += '%saicversion=%s' % (preparm(param), args.aicversion)
        if args.clli:
            param += '%sclli=%s' % (preparm(param), args.clli)
        if args.regionname:
            param += '%sregionname=%s' % (preparm(param), args.regionname)
        if args.osversion:
            param += '%sosversion=%s' % (preparm(param), args.osversion)
        if args.location_type:
            param += '%slocation_type=%s' % (preparm(param),
                                             args.location_type)
        if args.state:
            param += '%sstate=%s' % (preparm(param), args.state)
        if args.country:
            param += '%scountry=%s' % (preparm(param), args.country)
        if args.city:
            param += '%scity=%s' % (preparm(param), args.city)
        if args.street:
            param += '%sstreet=%s' % (preparm(param), args.street)
        if args.zip:
            param += '%szip=%s' % (preparm(param), args.zip)
        if args.vlcp_name:
            param += '%svlcp_name=%s' % (preparm(param), args.vlcp_name)
        return requests.get, '/%s' % param
    elif args.subcmd == 'add_metadata':
        return requests.post, '/%s/metadata' % args.region_id
    elif args.subcmd == 'update_metadata':
        return requests.put, '/%s/metadata' % args.region_id
    elif args.subcmd == 'delete_metadata':
        return requests.delete, '/%s/metadata/%s' % (args.region_id,
                                                     args.metadata_key)
    elif args.subcmd == 'get_metadata':
        return requests.get, '/%s/metadata' % args.region_id
    elif args.subcmd == 'update_status':
        return requests.put, '/%s/status' % args.region_id
    elif args.subcmd == 'get_group':
        return requests.get, '/%s' % args.group_id
    elif args.subcmd == 'list_groups':
        return requests.get, '/'
    elif args.subcmd == 'create_group':
        return requests.post, '/'
    elif args.subcmd == 'update_group':
        return requests.put, '/%s' % args.group_id
    elif args.subcmd == 'delete_group':
        return requests.delete, '/%s' % args.group_id


def get_path(args):
    path = 'v2/orm/regions'
    if 'group' in args.subcmd:
        path = 'v2/orm/groups'
    return path


def get_environment_variable(argument):
    # The rules are: all caps, underscores instead of dashes and prefixed
    environment_variable = 'AIC_ORM_{}'.format(
        argument.replace('-', '_').upper())

    return os.environ.get(environment_variable)


def run(args):
    url_path = get_path(args)
    host = args.orm_base_url if args.orm_base_url else config.orm_base_url
    port = args.port if args.port else 8080
    data = args.datafile.read() if 'datafile' in args else '{}'
    timeout = args.timeout if args.timeout else 10
    rest_cmd, cmd_url = cmd_details(args)
    url = '%s:%d/%s' % (host, port, url_path) + cmd_url
    if args.faceless or \
            args.subcmd == 'get_region' or \
            args.subcmd == 'list_regions' or \
            args.subcmd == 'list_groups' or \
            args.subcmd == 'get_group':
        auth_token = auth_region = requester = client = ''
    else:
        try:
            auth_token = get_token(timeout, args, host)
        except Exception:
            exit(1)
        auth_region = globals()['auth_region']
        requester = globals()['username']
        client = requester

    if (args.subcmd == 'get_region' or args.subcmd == 'list_regions') \
            and "use_version" in args:
        if args.use_version == 1:
            url = '%s:%d/lcp' % (host, port) + cmd_url
        elif args.use_version is not None and args.use_version != 2:
            print 'API error: use_version argument - invalid value,  ' \
                  'allowed values: 1 or 2'
            exit(1)

    if args.subcmd == "update_status":
        data = '{"status": "%s"}' % args.status

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
        print("Sending API:\ntimeout: %d\ndata: %s\n"
              "headers: %s\ncmd: %s\nurl: %s\n" % (timeout,
                                                   data,
                                                   headers,
                                                   rest_cmd.__name__,
                                                   url))
    try:
        resp = rest_cmd(url, data=data, timeout=timeout, headers=headers,
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
