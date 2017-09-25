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
    'host': {db_host},
    'username': {db_user},
    'password': {db_pass},
    'db_name': 'orm_ims_db',

}

verify_ssl_cert = False

database['connection_string'] = 'mysql://{0}:{1}@{2}:3306/{3}'.format(database['username'],
                                                                      database['password'],
                                                                      database['host'],
                                                                      database['db_name'])

application_root = 'http://localhost:{0}'.format(server['port'])

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
        'groups': 'v2/orm/groups',
        'regions': 'v2/orm/regions',
        'cache_seconds': 60
    },
    'audit_server': {
        'base': 'http://127.0.0.1:8776/',
        'trans': 'v1/audit/transaction'
    }

}

authentication = {
    "enabled": {keystone_auth_enable},
    "mech_id": {orm_keystone_user},
    "mech_pass": {orm_keystone_pass},
    "rms_url": config.base_url + ':' + config.rms['port'],
    "tenant_name": {orm_keystone_tenant},
    "token_role": "admin",
    "keystone_version": {openstack_keystone_version},
    "policy_file": "ims/etc/policy.json"
}
