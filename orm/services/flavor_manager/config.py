from orm_common.hooks.api_error_hook import APIErrorHook
from fms_rest.hooks.service_hooks import TransIdHook
from orm_common.hooks.security_headers_hook import SecurityHeadersHook

global TransIdHook
global APIErrorHook
global SecurityHeadersHook

# Server Specific Configurations
server = {
    'port': '8082',
    'host': '0.0.0.0',
    'name': 'fms'
}

cache_seconds = 0

# Pecan Application Configurations
app = {
    'root': 'fms_rest.controllers.root.RootController',
    'modules': ['fms_rest'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/fms_rest/templates',
    'debug': True,
    'errors': {
        '__force_dict__': True
    },
    'hooks': lambda: [TransIdHook(), APIErrorHook(), SecurityHeadersHook()]
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'fms_rest': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
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
            'filename': '/opt/app/orm/fms_rest/fms_rest.log',
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
    'host': 'localhost',
    'username': 'root',
    'password': 'stack',
    'db_name': 'orm_fms_db',

}

database['connection_string'] = 'mysql://{0}:{1}@{2}:3306/{3}'.format(database['username'],
                                                                      database['password'],
                                                                      database['host'],
                                                                      database['db_name'])

# this table is for calculating default extra specs needed
extra_spec_needed_table = {
    "ns": {
        "aggregate_instance_extra_specs____ns": "true",
        "hw____mem_page_size": "large"
    },
    "nd": {
        "aggregate_instance_extra_specs____nd": "true",
        "hw____mem_page_size": "large"
    },
    "nv": {
        "aggregate_instance_extra_specs____nv": "true",
        "hw____mem_page_size": "large"
    },
    "gv": {
        "aggregate_instance_extra_specs____gv": "true",
        "aggregate_instance_extra_specs____c2": "true"
    },
    "ss": {
        "aggregate_instance_extra_specs____ss": "true"
    }
}

# any key will be added to extra_spec_needed_table need to be added here
default_extra_spec_calculated_table = {
    "aggregate_instance_extra_specs____ns": "",
    "aggregate_instance_extra_specs____nd": "",
    "aggregate_instance_extra_specs____nv": "",
    "aggregate_instance_extra_specs____gv": "",
    "aggregate_instance_extra_specs____c2": "",
    "aggregate_instance_extra_specs____ss": "",
    "aggregate_instance_extra_specs____c2": "",
    "aggregate_instance_extra_specs____c4": "",
    "aggregate_instance_extra_specs____v": "",
    "hw____mem_page_size": "",
    "hw____cpu_policy": "",
    "hw____numa_nodes": ""
}

application_root = 'http://localhost:{0}'.format(server['port'])

api = {
    'uuid_server': {
        'base': 'http://127.0.0.1:8090/',
        'uuids': 'v1/uuids'
    },
    'rds_server': {
        'base': 'http://127.0.0.1:8777/',
        # 'base': 'http://172.20.91.35:8777/',
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

verify = False

authentication = {
    "enabled": False,
    "mech_id": "admin",
    "mech_pass": "stack",
    "rms_url": "http://127.0.0.1:8080",
    # "rms_url": "http://172.20.90.174:8080",
    "tenant_name": "admin",
    "token_role": "admin",
    # The Keystone version currently in use. Can be either "2.0" or "3"
    "keystone_version": "2.0",
    "policy_file": "/opt/app/orm/aic-orm-fms/fms_rest/etc/policy.json",
    # "policy_file": "/orm/aic-orm-fms/fms_rest/etc/policy.json"
}
