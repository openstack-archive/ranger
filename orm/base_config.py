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
    cfg.StrOpt('protocol',
               default='http',
               help='Orm protocol used.'),
    cfg.HostAddressOpt('orm_host',
                       default='127.0.0.1',
                       help='Orm server IP address.'),
    cfg.StrOpt('ranger_base',
               default='/opt/stack/ranger',
               help='Orm base directory.'),
    cfg.BoolOpt('ssl_verify',
                default=False,
                help='Flag for SSL verfiy Enabled/Disabled.'),
    cfg.BoolOpt('use_stderr',
                default=True,
                help='Log output to standard error.'),
    cfg.BoolOpt('verbose',
                short='v',
                default=False,
                help='Print more verbose output (set logging level to '
                     'INFO instead of default WARNING level).'),
    cfg.StrOpt('log_location',
               default='/var/log/ranger',
               help='Orm log directory.'),
    cfg.StrOpt('debug_level',
               default='DEBUG',
               help='logging debug level')
]

CONF.register_opts(OrmOpts)

#  Keystone config options in [keystone_autotoken] group
orm_token_group = cfg.OptGroup(name='token',
                               title='Orm Keystone Token Options')

OrmAuthGroup = [
    cfg.StrOpt('username',
               default='admin',
               help='Token user name.'),
    cfg.StrOpt('password',
               default='devstack',
               help='Token password.'),
    cfg.StrOpt('project_name',
               default='admin',
               help='Project name.'),
    cfg.StrOpt('region',
               default='local',
               help='Region.'),
    cfg.StrOpt('project_domain_name',
               default='default',
               help='Project domain name.'),
    cfg.StrOpt('user_domain_name',
               default='default',
               help='User domain name.')
]

CONF.register_group(orm_token_group)
CONF.register_opts(OrmAuthGroup, orm_token_group)

#  Database config options in [database] group
orm_database_group = cfg.OptGroup(name='database',
                                  title='Orm Database Options')

OrmDatabaseGroup = [
    cfg.StrOpt('connection',
               help='The SQLAlchemy connection string to use to connect to '
                    'the ORM database.',
               secret=True),
    cfg.IntOpt('max_retries',
               default=-1,
               help='The maximum number of retries for database connection.')
]

CONF.register_group(orm_database_group)
CONF.register_opts(OrmDatabaseGroup, orm_database_group)

#  UUID config options in [uuid] group
orm_uuid_group = cfg.OptGroup(name='uuid', title='Orm UUID Options')

OrmUuidGroup = [
    cfg.PortOpt('port',
                default=7001,
                help='UUID port.'),
    cfg.StrOpt('log',
               default='uuidgen.log',
               help='UUID log name.')
]

CONF.register_group(orm_uuid_group)
CONF.register_opts(OrmUuidGroup, orm_uuid_group)


#  cms config options in [cms] group
orm_cms_group = cfg.OptGroup(name='cms', title='Orm Cms Options')

OrmCmsGroup = [
    cfg.PortOpt('port',
                default=7080,
                help='Cms port.'),
    cfg.StrOpt('log',
               default='cms.log',
               help='Cms log name.')
]

CONF.register_group(orm_cms_group)
CONF.register_opts(OrmCmsGroup, orm_cms_group)


#  fms config options in [fms] group
orm_fms_group = cfg.OptGroup(name='fms', title='Orm Fms Options')

OrmFmsGroup = [
    cfg.PortOpt('port',
                default=8082,
                help='Fms port.'),
    cfg.StrOpt('log',
               default='fms.log',
               help='Fms log name.')
]

CONF.register_group(orm_fms_group)
CONF.register_opts(OrmFmsGroup, orm_fms_group)


#  audit config options in [audit] group
orm_audit_group = cfg.OptGroup(name='audit', title='Orm Audit Options')

OrmAuditGroup = [
    cfg.PortOpt('port',
                default=7002,
                help='Audit port.'),
    cfg.StrOpt('log',
               default='audit_server.log',
               help='Audit log name.')
]

CONF.register_group(orm_audit_group)
CONF.register_opts(OrmAuditGroup, orm_audit_group)


#  ims config options in [ims] group
orm_ims_group = cfg.OptGroup(name='ims', title='Orm Ims Options')

OrmImsGroup = [
    cfg.PortOpt('port',
                default=8084,
                help='Ims port.'),
    cfg.StrOpt('log',
               default='ims.log',
               help='Ims log name.')
]

CONF.register_group(orm_ims_group)
CONF.register_opts(OrmImsGroup, orm_ims_group)


#  rms config options in [rms] group
orm_rms_group = cfg.OptGroup(name='rms', title='Orm Rms Options')

OrmRmsGroup = [
    cfg.PortOpt('port',
                default=7003,
                help='Rms port.'),
    cfg.StrOpt('log',
               default='rms.log',
               help='Rms log name.')
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
               default='/opt/stack/git_repo',
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
    cfg.StrOpt('log',
               default='rds.log',
               help='Rds log name.')
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

################################################################
# The following global variables are kept in here for
# backward compatiblitiy as other modules still
# referenced to them.
################################################################

debug_level = CONF.debug_level
protocol = CONF.protocol
orm_host = CONF.orm_host
ranger_base = CONF.ranger_base
db_user = 'root'
db_pass = 'devstack'
db_host = '127.0.0.1'
ssl_verify = CONF.ssl_verify
token_auth_enabled = False
token_auth_user = CONF.token.username
token_auth_pass = CONF.token.password
token_auth_tenant = CONF.token.project_name
token_auth_user_role = 'admin'

db_url = 'mysql://{}:{}@{}:3306/'.format(db_user, db_pass, db_host)

uuid = {'port': CONF.uuid.port,
        'base_url': '{}://{}:{}/'.
                    format(protocol, orm_host, CONF.uuid.port),
        'log': '{}/{}'.format(CONF.log_location, CONF.uuid.log)}

cms = {'port': CONF.cms.port,
       'base_url': '{}://{}:{}/'.format(protocol, orm_host, CONF.cms.port),
       'policy_file': CONF.ranger_base +
       '/orm/services/customer_manager/cms_rest/etc/policy.json',
       'log': '{}/{}'.format(CONF.log_location, CONF.cms.log)}

fms = {'port': CONF.fms.port,
       'base_url': '{}://{}:{}/'.format(protocol, orm_host, CONF.fms.port),
       'policy_file': CONF.ranger_base +
       '/orm/services/flavor_manager/fms_rest/etc/policy.json',
       'log': '{}/{}'.format(CONF.log_location, CONF.fms.log)}

audit_server = {'port': CONF.audit.port,
                'base_url': '{}://{}:{}/'
                            .format(protocol, orm_host, CONF.audit.port),
                'log': '{}/{}'.format(CONF.log_location, CONF.audit.log)}

ims = {'port': CONF.ims.port,
       'base_url': '{}://{}:{}/'.format(protocol, orm_host, CONF.ims.port),
       'policy_file': CONF.ranger_base +
       '/orm/services/image_manager/ims/etc/policy.json',
       'log': '{}/{}'.format(CONF.log_location, CONF.ims.log)}

rms = {'port': CONF.rms.port,
       'base_url': '{}://{}:{}/'.format(protocol, orm_host, CONF.rms.port),
       'policy_file': CONF.ranger_base +
       '/orm/services/region_manager/rms/etc/policy.json',
       'log': '{}/{}'.format(CONF.log_location, CONF.rms.log)}

rds = {'port': CONF.rds.port,
       'repo_local_location': CONF.rds.repo_local_location,
       'repo_remote_location': CONF.rds.repo_remote_location,
       'repo_user': CONF.rds.repo_user,
       'repo_email': CONF.rds.repo_email,
       'base_url': '{}://{}:{}/'.format(protocol, orm_host, CONF.rds.port),
       'log': '{}/{}'.format(CONF.log_location, CONF.rds.log)}

cli = {'base_region': CONF.cli.base_region}
