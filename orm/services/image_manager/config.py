import orm.base_config as config
from orm.common.orm_common.hooks.api_error_hook import APIErrorHook
from orm.common.orm_common.hooks.security_headers_hook import SecurityHeadersHook
from orm.services.image_manager.ims.hooks.service_hooks import TransIdHook
global TransIdHook
global APIErrorHook
global SecurityHeadersHook

# Server Specific Configurations
server = {
    'port': config.ims['port'],
    'host': config.orm_host,
    'name': 'ims'
}

# Pecan Application Configurations
app = {
    'root': 'orm.services.image_manager.ims.controllers.root.RootController',
    'modules': ['orm.services.image_manager.ims'],
    'debug': True,
    'hooks': lambda: [TransIdHook(), APIErrorHook(), SecurityHeadersHook()]
}

app_module = app['modules'][0]
logging = config.get_log_config(config.ims['log'], server['name'], app_module)

# DB configurations
database = {
    'connection_string': config.db_connect
}


application_root = config.ims['base_url']

api = {
    'uuid_server': {
        'base': config.uuid['base_url'],
        'uuids': 'v1/uuids'
    },
    'rds_server': {
        'base': config.rds['base_url'],
        'resources': 'v1/rds/resources',
        'status': 'v1/rds/status/resource/'
    },
    'rms_server': {
        'base': config.rms['base_url'],
        'groups': 'v2/orm/groups',
        'regions': 'v2/orm/regions',
        'cache_seconds': 60
    },
    'audit_server': {
        'base': config.audit_server['base_url'],
        'trans': 'v1/audit/transaction'
    }

}

verify = config.ssl_verify

authentication = config.server_request_auth(server['name'])
