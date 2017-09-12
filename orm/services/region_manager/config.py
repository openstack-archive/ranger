from orm.common.orm_common.hooks.api_error_hook import APIErrorHook
from orm.common.orm_common.hooks.security_headers_hook import SecurityHeadersHook
from orm.common.orm_common.hooks.transaction_id_hook import TransactionIdHook

global TransactionIdHook
global APIErrorHook
global SecurityHeadersHook

# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0',
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
            'filename': '/var/logs/ranger/rms.log',
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
    'url': 'mysql://root:stack@127.0.0.1/orm_rms_db?charset=utf8',
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

verify = False

authentication = {
    "enabled": True,
    "mech_id": "admin",
    "mech_pass": "stack",
    "tenant_name": "admin",
    # The Keystone version currently in use. Can be either "2.0" or "3"
    "keystone_version": "2.0",
    "policy_file": "/stack/orm/services/region_manager/rms/etc/policy.json"
}
