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

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'orm.services.image_manager.ims': {'level': config.debug_level,
                                           'handlers': ['console', 'Logfile'],
                                           'propagate': False},
        'orm.common.client.audit.audit_client': {
            'level': config.debug_level,
            'handlers': ['console', 'Logfile'],
            'propagate': False},
        'orm.common.orm_common': {'level': config.debug_level,
                                  'handlers': ['console', 'Logfile'],
                                  'propagate': False},
        'pecan': {'level': config.debug_level, 'handlers': ['console'],
                  'propagate': False},
        'py.warnings': {'handlers': ['console']},
        '__force_dict__': True
    },
    'handlers': {
        'console': {
            'level': config.debug_level,
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        },
        'Logfile': {
            'level': config.debug_level,
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

# DB configurations
db_url = config.db_connect

database = {
    'connection_string': db_url.endswith('/orm') and db_url.replace("/orm", "/orm_ims_db") or (db_url + 'orm_ims_db')
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

authentication = {
    "enabled": config.token_auth_enabled,
    "mech_id": config.token_auth_user,
    "mech_pass": config.token_auth_pass,
    "rms_url": config.rms['base_url'],
    "tenant_name": config.token_auth_tenant,
    "token_role": config.token_auth_user_role,
    "keystone_version": config.token_auth_version,
    "policy_file": config.ims['policy_file'],
    "user_domain_name": config.user_domain_name,
    "project_domain_name": config.project_domain_name
}