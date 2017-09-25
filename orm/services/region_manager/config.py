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
    'root': 'rms.controllers.root.RootController',
    'modules': ['rms'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/rms/templates',
    'debug': True,
    'hooks': lambda: [TransactionIdHook(), APIErrorHook(), SecurityHeadersHook()]
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'rms': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'],
                'propagate': False},
        'pecan': {'level': 'DEBUG', 'handlers': ['console'],
                  'propagate': False},
        'audit_client': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'],
                         'propagate': False},
        'orm_common': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'],
                       'propagate': False},
        'keystone_utils': {'level': 'DEBUG',
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
            'filename': config.rms['log'],
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
database = {
    'url': 'mysql://{db_user}:{db_pass}@{db_host}/orm_rms?charset=utf8',
    'max_retries': 3,
    'retries_interval': 10
}

endpoints = {
    'lcp': 'http://127.0.0.1:8082/lcp'
}

api = {
    'uuid_server': {
        'base': 'http://127.0.0.1:8090/',
        'uuids': 'v1/uuids'
    },
    'audit_server': {
        'base': 'http://127.0.0.1:8776/',
        'trans': 'v1/audit/transaction'
    }
}

verify_ssl_cert = False

authentication = {
    "enabled": {keystone_auth_enable},
    "mech_id": {orm_keystone_user},
    "mech_pass": {orm_keystone_pass},
    "tenant_name": {orm_keystone_tenant},
    # The Keystone version currently in use. Can be either "2.0" or "3"
    "keystone_version": {openstack_keystone_version},
    "policy_file": "/stack/orm/services/region_manager/rms/etc/policy.json"
}
