from orm_common.hooks.api_error_hook import APIErrorHook
from orm_common.hooks.security_headers_hook import SecurityHeadersHook
from orm_common.hooks.transaction_id_hook import TransactionIdHook

global TransactionIdHook
global APIErrorHook
global SecurityHeadersHook

# Server Specific Configurations
server = {
    'port': '7080',
    'host': '0.0.0.0',
    'name': 'cms',
    'host_ip': '0.0.0.0'
}

# Pecan Application Configurations

app = {
    'root': 'cms_rest.controllers.root.RootController',
    'modules': ['cms_rest'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/cms_rest/templates',
    'debug': True,
    'hooks': lambda: [TransactionIdHook(), APIErrorHook(), SecurityHeadersHook()]
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'cms_rest': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
        'orm_common': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
        'keystone_utils': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
        'pecan': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False},
        'orm_common': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
        'keystone_utils': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
        'audit_client': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
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
            'filename': '/opt/app/orm/logs/cms_rest.log',
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
    'connection_string': 'mysql://root:stack@localhost:3306/orm_cms_db'
}

api = {
    'uuid_server': {
        'base': 'http://127.0.0.1:8090/',
        'uuids': 'v1/uuids'
    },
    'rds_server': {
        'base': 'http://127.0.0.1:8777/',
        'resources': 'v1/rds/resources',
        'status': 'v1/rds/status/resource/'
    },
    'rms_server': {
        'base': 'http://127.0.0.1:8080/',
        'regions': 'v2/orm/regions',
        'groups': 'v2/orm/groups',
        'cache_seconds': 30
    },
    'audit_server': {
        'base': 'http://127.0.0.1:8776/',
        'trans': 'v1/audit/transaction'
    }
}

verify = False

authentication = {
    "enabled": True,
    "mech_id": "admin",
    "mech_pass": "stack",
    "rms_url": "http://127.0.0.1:8080",
    "tenant_name": "admin",
    "token_role": "admin",
    # The Keystone collection under which the role was granted.
    # The key can be either "tenant" (for Keystone v2.0) or "domain"
    # (for Keystone v3) and the value is the tenant/domain name.
    "role_location": {"tenant": "admin"},
    # The Keystone version currently in use. Can be either "2.0" or "3".
    "keystone_version": "2.0",
    "policy_file": "/opt/app/orm/cms_rest/cms_rest/etc/policy.json"
}
