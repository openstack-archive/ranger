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

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'orm.services.customer_manager.cms_rest': {'level': 'DEBUG',
                                                   'handlers': ['console', 'Logfile'],
                                                   'propagate': False},
        'orm.common.orm_common': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'],
                                  'propagate': False},
        'orm.common.client.keystone.keystone_utils': {'level': 'DEBUG',
                                                      'handlers': ['console', 'Logfile'],
                                                      'propagate': False},
        'pecan': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False},
        'orm.common.client.audit.audit_client': {'level': 'DEBUG',
                                                 'handlers': ['console', 'Logfile'],
                                                 'propagate': False},
        'py.warnings': {'handlers': ['console']},
        '__force_dict__': True
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        },
        'Logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 50000000,
            'backupCount': 10,
            'filename': config.cms['log'],
            'formatter': 'simple'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                       '[%(threadName)s] %(message)s')
        },
        'color': {
            '()': 'pecan.log.ColorFormatter',
            'format': ('%(asctime)s [%(padded_color_levelname)s] [%(name)s]'
                       '[%(threadName)s] %(message)s'),
            '__force_dict__': True
        }
    }
}

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

database = {
    'connection_string': config.db_url + 'orm_cms_db'
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
    "role_location": {"tenant": "admin"},
    # The Keystone version currently in use. Can be either "2.0" or "3".
    "keystone_version": "2.0",
    "policy_file": config.cms['policy_file']
}
