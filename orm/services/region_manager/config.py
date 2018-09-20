import orm.base_config as config
from orm.common.orm_common.hooks.api_error_hook import APIErrorHook
from orm.common.orm_common.hooks.security_headers_hook import SecurityHeadersHook
from orm.common.orm_common.hooks.transaction_id_hook import TransactionIdHook
global TransactionIdHook
global APIErrorHook
global SecurityHeadersHook

# Server Specific Configurations
server = {
    'port': config.rms['port'],
    'host': config.orm_host,
    'name': 'rms'
}

# Pecan Application Configurations
app = {
    'root': 'orm.services.region_manager.rms.controllers.root.RootController',
    'modules': ['orm.services.region_manager.rms'],
    'debug': True,
    'hooks': lambda: [TransactionIdHook(), APIErrorHook(), SecurityHeadersHook()]
}

app_module = app['modules'][0]
logging = config.get_log_config(config.rms['log'], server['name'], app_module)

# user input validations
region_options = {
    'allowed_status_values': [
        'functional',
        'maintenance',
        'down',
        'building'
    ],
    'endpoints_types_must_have': [
        'dashboard',
        'identity',
        'ord'
    ]
}

# DB configurations
db_url = config.db_connect

database = {
    'url': db_url.endswith('/orm') and db_url.replace("/orm", "/orm_rms_db") or (db_url + 'orm_rms_db'),
    'max_retries': 3,
    'retries_interval': 10
}

endpoints = {
    'lcp': config.rms['base_url'] + 'lcp'
}

verify = config.ssl_verify

authentication = config.server_request_auth(server['name'])

api = {
    'uuid_server': {
        'base': config.uuid['base_url'],
        'uuids': 'v1/uuids'
    },
    'audit_server': {
        'base': config.audit_server['base_url'],
        'trans': 'v1/audit/transaction'
    },
    'fms_server': {
        'base': config.fms['base_url'],
        'flavors': 'v1/orm/flavors'
    },
    'cms_server': {
        'base': config.cms['base_url'],
        'customers': 'v1/orm/customers'
    },
    'ims_server': {
        'base': config.ims['base_url'],
        'images': 'v1/orm/images'
    }
}
