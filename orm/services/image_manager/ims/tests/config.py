from ims.tests.simple_hook_mock import SimpleHookMock

global SimpleHookMock

# Server Specific Configurations
server = {
    'port': '8084',
    'host': '0.0.0.0',
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
    'hooks': lambda: [SimpleHookMock()]
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'ims': {'level': 'DEBUG', 'handlers': ['console'],
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
    'host': 'localhost',
    'username': 'root',
    'password': 'stack',
    'db_name': 'orm_ims_db',

}

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
        # 'base': 'http://172.20.90.179:8777/',
        'base': 'http://127.0.0.1:8777/',
        'resources': 'v1/rds/resources',
        'status': 'v1/rds/status/resource/'
    },
    'rms_server': {
        'base': 'http://127.0.0.1:8080/',
        # 'base': 'http://172.20.90.179:8080/',
        'groups': 'v1/orm/groups',
        'regions': 'v1/orm/regions',
        'cache_seconds': 60
    },
    'audit_server': {
        'base': 'http://127.0.0.1:8776/',
        'trans': 'v1/audit/transaction'
    }

}

verify = False

authentication = {
    "enabled": False,
    "mech_id": "admin",
    "mech_pass": "stack",
    "rms_url": "http://172.20.90.174:8080",
    "tenant_name": "admin",
    "keystone_version": "2.0",
    "token_role": "admin",
    "policy_file": "/opt/app/orm/aic-orm-ims/ims/etc/policy.json"
}
