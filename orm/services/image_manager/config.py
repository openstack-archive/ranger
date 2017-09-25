from ims.hooks.service_hooks import TransIdHook
import orm.base_config as config
from orm_common.hooks.api_error_hook import APIErrorHook
from orm_common.hooks.security_headers_hook import SecurityHeadersHook
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
    'root': 'ims.controllers.root.RootController',
    'modules': ['ims'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/ims/templates',
    'debug': True,
    'errors': {
        '__force_dict__': True
    },
    'hooks': lambda: [TransIdHook(), APIErrorHook(), SecurityHeadersHook()]
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'ims': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'],
                'propagate': False},
        'audit_client': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'],
                         'propagate': False},
        'orm_common': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'],
                       'propagate': False},
        'pecan': {'level': 'DEBUG', 'handlers': ['console'],
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
            'filename': config.ims['log'],
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

database = {
    'host': config.db_host,
    'username': config.db_user,
    'password': config.db_pass,
    'db_name': 'orm_ims_db',

}
database['connection_string'] = 'mysql://{0}:{1}@{2}:3306/{3}'.format(database['username'],
                                                                      database['password'],
                                                                      database['host'],
                                                                      database['db_name'])

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

authentication = {
    "enabled": config.token_auth_enabled,
    "mech_id": config.token_auth_user,
    "mech_pass": config.token_auth_pass,
    "rms_url": config.rms['base_url'],
    "tenant_name": config.token_auth_tenant,
    "token_role": config.token_auth_user_role,
    "keystone_version": "2.0",
    "policy_file": config.ims['policy_file']
}
