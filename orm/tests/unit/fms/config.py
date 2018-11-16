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
        'fms_rest': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False},
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

database = {
    'host': 'localhost',
    'username': 'root',
    'password': 'xxxxxxxxxxx',
    'db_name': 'orm',

}

flavor_series = {
    'valid_series': [
        'p1'
    ]
}

# valid_flavor_options
flavor_options = {

    'valid_p1_numa_value': 'n0',
    'valid_p1_opt_values': [
        'n0', 'i2'
    ]
}

# this table is for calculating default extra specs needed
extra_spec_needed_table = {
    "p1": {
        "aggregate_instance_extra_specs____p1": "true",
        "hw____mem_page_size": "large"
    }
}

# any key will be added to extra_spec_needed_table need to be added here
default_extra_spec_calculated_table = {
    "aggregate_instance_extra_specs____p1": "",
    "hw____mem_page_size": "",
    "hw____cpu_policy": "",
    "hw____numa_nodes": ""
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
    "mech_pass": "xxxxxxxxxxx",
    "rms_url": "http://127.0.0.1:8080",
    "tenant_name": "admin",
    "keystone_version": "3",
    "policy_file": "orm/services/flavor_manager/fms_rest/etc/policy.json",
    "user_domain_name": "default",
    "project_domain_name": "default"
}

flavor_limits = {
    # All flavor limits will be converted to integers, and must not be non-numeric.
    # Root disk, block storage and object storage don't have set limits
    # vcpu_limit and ephemeral_limit values are in GB
    # vram_limit and swap_file_limit values are in MB and must be a multiple of 1024

    "swap_file_limit": "327680",
    "ephemeral_limit": "2000",

    # for 'p1' series:
    # vcpu_limit and vram_limit for 'p1' series with "n0":"true" option
    "p1_n0_vcpu_limit": "80",
    "p1_n0_vram_limit": "327680",
    # vcpu_limit and vram_limit for 'p1' series with  "n0":"false" option
    "p1_nx_vcpu_limit": "40",
    "p1_nx_vram_limit": "163840"

}
