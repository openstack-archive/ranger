import orm.base_config as config
from orm.common.orm_common.hooks.api_error_hook import APIErrorHook
from orm.common.orm_common.hooks.security_headers_hook import SecurityHeadersHook
from orm.common.orm_common.hooks.transaction_id_hook import TransactionIdHook
global TransactionIdHook
global APIErrorHook
global SecurityHeadersHook

# Server Specific Configurations
server = {
    'port': config.cms['port'],
    'host': config.orm_host,
    'name': 'cms',
    'host_ip': config.orm_host
}

# Pecan Application Configurations

app = {
    'root': 'orm.services.customer_manager.cms_rest.controllers.root.RootController',
    'modules': ['orm.services.customer_manager.cms_rest'],
    'debug': True,
    'hooks': lambda: [TransactionIdHook(), APIErrorHook(), SecurityHeadersHook()]
}

app_module = app['modules'][0]
logging = config.get_log_config(config.cms['log'], server['name'], app_module)

quotas_default_values = {
    'compute': {
        'vcpus': '20',
        'metadata_items': '128',
        'injected_file_content_bytes': '10240'
    },
    'network': {
        'security_groups': '10',
        'security_group_rules': '20'
    }
}

# DB configurations
db_url = config.db_connect

database = {
    'connection_string': db_url.endswith('/orm') and db_url.replace("/orm", "/orm_cms_db") or (db_url + 'orm_cms_db')
}

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
        'regions': 'v2/orm/regions',
        'groups': 'v2/orm/groups',
        'cache_seconds': 30
    },
    'audit_server': {
        'base': config.audit_server['base_url'],
        'trans': 'v1/audit/transaction'
    }
}

verify = config.ssl_verify

authentication = {
    "enabled": config.token_auth_enabled,
    "mech_id": config.token_auth_user,
    "mech_pass": config.token_auth_pass,
    "rms_url": config.rms['base_url'],
    "tenant_name": config.token_auth_tenant,
    "token_role": config.token_auth_user_role,
    # The Keystone collection under which the role was granted.
    # The key can be either "tenant" (for Keystone v2.0) or "domain"
    # (for Keystone v3) and the value is the tenant/domain name.
    "role_location": {"domain": "admin"},
    # The Keystone version currently in use. Can be either "2.0" or "3".
    "keystone_version": config.token_auth_version,
    "policy_file": config.cms['policy_file']
}
