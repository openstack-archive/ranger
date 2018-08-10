#    Copyright 2018 AT&T Corporation.
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from oslo_config import cfg

CONF = cfg.CONF


# Orm config options in DEFAULT block
OrmOpts = [
    cfg.StrOpt('orm_protocol',
               default='http',
               help='Orm protocol used.'),
    cfg.StrOpt('orm_host',
               default='127.0.0.1',
               help='Orm server IP address.'),
    cfg.StrOpt('ranger_base',
               default='/opt/app/ranger',
               help='Orm base directory.'),
    cfg.StrOpt('db_user',
               default='root',
               help='DB user name.'),
    cfg.StrOpt('db_pass',
               default='devstack',
               help='DB user password.'),
    cfg.StrOpt('db_host',
               default='127.0.0.1',
               help='DB server IP address.')
]

CONF.register_opts(OrmOpts)

#  Authentication config options in [auth] group
orm_auth_group = cfg.OptGroup(name='auth', title='Orm Authentication Options')

OrmAuthGroup = [
    cfg.BoolOpt('ssl_verify',
                default=False,
                help='Flag for SSL verfiy Enabled/Disabled.'),
    cfg.BoolOpt('token_auth_enabled',
                default=False,
                help='Flag for token authentication Enabled/Disabled.'),
    cfg.StrOpt('token_auth_user',
               default='admin',
               help='Token authentication user name.'),
    cfg.StrOpt('token_auth_pass',
               default='devstack',
               help='Token authentication password.'),
    cfg.StrOpt('token_auth_tenant',
               default='admin',
               help='Token authentication tenant name.'),
    cfg.StrOpt('token_auth_user_role',
               default='admin',
               help='Token authentication user role.')
]

CONF.register_group(orm_auth_group)
CONF.register_opts(OrmAuthGroup, orm_auth_group)

#  UUID config options in [uuid] group
orm_uuid_group = cfg.OptGroup(name='uuid', title='Orm UUID Options')

OrmUuidGroup = [
    cfg.PortOpt('port',
                default=7001,
                help='UUID port.'),
    cfg.StrOpt('url',
               default='$orm_protocol://$orm_host:$port/',
               help='URL for UUID port.'),
    cfg.StrOpt('log',
               default='/var/log/ranger/uuidgen.log',
               help='UUID log location.')
]

CONF.register_group(orm_uuid_group)
CONF.register_opts(OrmUuidGroup, orm_uuid_group)


#  cms config options in [cms] group
orm_cms_group = cfg.OptGroup(name='cms', title='Orm Cms Options')

OrmCmsGroup = [
    cfg.PortOpt('port',
                default=7080,
                help='Cms port.'),
    cfg.StrOpt('url',
               default='$orm_protocol://$orm_host:$port/',
               help='URL for cms port.'),
    cfg.StrOpt('log',
               default='/var/log/ranger/cms.log',
               help='Cms log location.')
]

CONF.register_group(orm_cms_group)
CONF.register_opts(OrmCmsGroup, orm_cms_group)


#  fms config options in [fms] group
orm_fms_group = cfg.OptGroup(name='fms', title='Orm Fms Options')

OrmFmsGroup = [
    cfg.PortOpt('port',
                default=8082,
                help='Fms port.'),
    cfg.StrOpt('url',
               default='$orm_protocol://$orm_host:$port/',
               help='URL for fms port.'),
    cfg.StrOpt('log',
               default='/var/log/ranger/fms.log',
               help='Fms log location.')
]

CONF.register_group(orm_fms_group)
CONF.register_opts(OrmFmsGroup, orm_fms_group)


#  audit config options in [audit] group
orm_audit_group = cfg.OptGroup(name='audit', title='Orm Audit Options')

OrmAuditGroup = [
    cfg.PortOpt('port',
                default=7002,
                help='Audit port.'),
    cfg.StrOpt('url',
               default='$orm_protocol://$orm_host:$port/',
               help='URL for audit port.'),
    cfg.StrOpt('log',
               default='/var/log/ranger/audit_server.log',
               help='Audit log location.')
]

CONF.register_group(orm_audit_group)
CONF.register_opts(OrmAuditGroup, orm_audit_group)


#  ims config options in [ims] group
orm_ims_group = cfg.OptGroup(name='ims', title='Orm Ims Options')

OrmImsGroup = [
    cfg.PortOpt('port',
                default=8084,
                help='Ims port.'),
    cfg.StrOpt('url',
               default='$orm_protocol://$orm_host:$port/',
               help='URL for ims port.'),
    cfg.StrOpt('log',
               default='/var/log/ranger/ims.log',
               help='Ims log location.')
]

CONF.register_group(orm_ims_group)
CONF.register_opts(OrmImsGroup, orm_ims_group)


#  rms config options in [rms] group
orm_rms_group = cfg.OptGroup(name='rms', title='Orm Rms Options')

OrmRmsGroup = [
    cfg.PortOpt('port',
                default=7003,
                help='Rms port.'),
    cfg.StrOpt('url',
               default='$orm_protocol://$orm_host:$port/',
               help='URL for rms port.'),
    cfg.StrOpt('log',
               default='/var/log/ranger/rms.log',
               help='Rms log location.')
]

CONF.register_group(orm_rms_group)
CONF.register_opts(OrmRmsGroup, orm_rms_group)


#  rds config options in [rds] group
orm_rds_group = cfg.OptGroup(name='rds', title='Orm Rds Options')

OrmRdsGroup = [
    cfg.PortOpt('port',
                default=8777,
                help='Rds port.'),
    cfg.StrOpt('repo_local_location',
               default='/opt/app/git_repo',
               help='Path to repo location.'),
    cfg.StrOpt('repo_remote_location',
               default='git@127.0.0.1:/home/repo/ORM.git',
               help='Repo remote location.'),
    cfg.StrOpt('repo_user',
               default='orm',
               help='Repo user name.'),
    cfg.StrOpt('repo_email',
               default='orm@test.com',
               help='Repo email address.'),
    cfg.StrOpt('url',
               default='$orm_protocol://$orm_host:$port/',
               help='URL for rds port.'),
    cfg.StrOpt('log',
               default='/var/log/ranger/rds.log',
               help='Rds log location.')
]

CONF.register_group(orm_rds_group)
CONF.register_opts(OrmRdsGroup, orm_rds_group)


#  cli config options in [cli] group
orm_cli_group = cfg.OptGroup(name='cli', title='Orm CLI Options')

OrmCliGroup = [
    cfg.StrOpt('base_region',
               default='local',
               help='Base region.')
]

CONF.register_group(orm_cli_group)
CONF.register_opts(OrmCliGroup, orm_cli_group)

# Config options can be overriden by config file
# in 'ranger/etc/ranger.conf'
#
# Example:
# CONF(['--config-file', '/home/ubuntu/ranger/ranger/etc/ranger.conf'])

################################################################
# The following global variables are kept in here for
# backward compatiblitiy as other modules still
# referenced to them.
################################################################

orm_protocol = CONF.orm_protocol
orm_host = CONF.orm_host
ranger_base = CONF.ranger_base
db_user = CONF.db_user
db_pass = CONF.db_pass
db_host = CONF.db_host
ssl_verify = CONF.auth.ssl_verify
token_auth_enabled = CONF.auth.token_auth_enabled
token_auth_user = CONF.auth.token_auth_user
token_auth_pass = CONF.auth.token_auth_pass
token_auth_tenant = CONF.auth.token_auth_tenant
token_auth_user_role = CONF.auth.token_auth_user_role

db_url = 'mysql://{}:{}@{}:3306/'.format(CONF.db_user,
                                         CONF.db_pass,
                                         CONF.db_host)

uuid = {'port': CONF.uuid.port,
        'base_url': CONF.uuid.url,
        'log': CONF.uuid.log}

cms = {'port': CONF.cms.port,
       'base_url': CONF.cms.url,
       'policy_file': CONF.ranger_base +
       '/orm/services/customer_manager/cms_rest/etc/policy.json',
       'log': CONF.cms.log}

fms = {'port': CONF.fms.port,
       'base_url': CONF.fms.url,
       'policy_file': CONF.ranger_base +
       '/orm/services/flavor_manager/fms_rest/etc/policy.json',
       'log': CONF.fms.log}

audit_server = {'port': CONF.audit.port,
                'base_url': CONF.audit.url,
                'log': CONF.audit.log}

ims = {'port': CONF.ims.port,
       'base_url': CONF.ims.url,
       'policy_file': CONF.ranger_base +
       '/orm/services/image_manager/ims/etc/policy.json',
       'log': CONF.ims.log}

rms = {'port': CONF.rms.port,
       'base_url': CONF.rms.url,
       'policy_file': CONF.ranger_base +
       '/orm/services/region_manager/rms/etc/policy.json',
       'log': CONF.rms.log}

rds = {'port': CONF.rds.port,
       'repo_local_location': CONF.rds.repo_local_location,
       'repo_remote_location': CONF.rds.repo_remote_location,
       'repo_user': CONF.rds.repo_user,
       'repo_email': CONF.rds.repo_email,
       'base_url': CONF.rds.url,
       'log': CONF.rds.log}

cli = {'base_region': CONF.cli.base_region}
