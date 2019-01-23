from orm.tests.unit.fms.simple_hook_mock import SimpleHookMock

global SimpleHookMock

# Server Specific Configurations
server = {
    'port': '8082',
    'host': '0.0.0.0',
    'name': 'fms'
}

# Pecan Application Configurations
app = {
    'root': 'orm.services.flavor_manager.fms_rest.controllers.root.RootController',
    'modules': ['orm.services.flavor_manager.fms_rest'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/fms_rest/templates',
    'debug': True,
    'errors': {
        '__force_dict__': True
    },
    'hooks': lambda: [SimpleHookMock()]
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'fms_rest': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        },
        'pecan': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        },
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
    'password': 'root',
    'db_name': 'orm_fms_db',

}

database['connection_string'] = 'mysql://{0}:{1}@{2}:3306/{3}'.format(
    database['username'],
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
    "rms_url": "http://127.0.0.1:8080",
    "tenant_name": "admin",
    "keystone_version": "3",
    "policy_file": "orm/services/flavor_manager/fms_rest/etc/policy.json",
    "user_domain_name": "default",
    "project_domain_name": "default"
}
