import os

from orm.tests.unit.cms.simple_hook_mock import SimpleHookMock

global SimpleHookMock

# Server Specific Configurations
server = {
    'port': '7080',
    'host': '0.0.0.0',
    'name': 'cms',
    'host_ip': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'orm.services.customer_manager.cms_rest.controllers.root.RootController',
    'modules': ['orm.services.customer_manager.cms_rest'],
    'static_root': '%(confdir)s/../../public',
    'template_path': '%(confdir)s/../templates',
    'debug': True,
    'errors': {
        '404': '/error/404',
        '__force_dict__': True
    },
    'hooks': lambda: [SimpleHookMock()]
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'cms_rest': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False},
        'pecan': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False},
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

api_options = {
    'mock': {
        'uuid_server': {
            'base': 'http://127.0.0.1:3000/uuid/',
            'uuids': 'v1/uuids'
        },
        'rds_server': {
            'base': 'http://127.0.0.1:3000/rds/',
            'resources': 'v1/rds/resources',
            'status': 'v1/rds/status/resource/'
        },
        'audit_server': {
            'base': 'http://127.0.0.1:8776/',
            'trans': 'v1/audit/transaction'
        }
    },
    'dev': {
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
}

cms_mode = None
if not ('CMS_ENV' in os.environ) or not (os.environ['CMS_ENV'] in api_options):
    print('!!! NO ENVIRONMENT VARIABLE CMS_ENV SPECIFIED OR NO ENV VARIABLE '
          'WITH THIS NAME AVAILABLE, RUNNING WITH DEFAULT <dev>')
    cms_mode = 'dev'
else:
    cms_mode = os.environ['CMS_ENV']
    print('Environment variable found, running under <{0}> environment'.format(cms_mode))

api = api_options[cms_mode]

database = {
    'connection_string': 'mysql://root:root@localhost:3306/orm_cms_db'
}

verify = False

authentication = {
    "enabled": False,
    "mech_id": "admin",
    "mech_pass": "stack",
    "rms_url": "http://127.0.0.1:8080",
    "tenant_name": "admin",
    "token_role": "admin",
    "role_location": {"tenant": "admin"},
    "keystone_version": "3",
    "policy_file": "orm/services/customer_manager/cms_rest/etc/policy.json",
    "user_domain_name": "default",
    "project_domain_name": "default"
}
