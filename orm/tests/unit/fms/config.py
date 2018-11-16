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
    'db_name': 'orm_fms_db',

}

# valid_flavor_options
flavor_options = {
    'valid_cpin_opt_values': [
        'c2', 'c4'
    ],
    'valid_stor_opt_values': [
        's1', 's2'
    ],
    'valid_vnf_opt_values': [
        'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7'
    ],
    'valid_ns_numa_values': ['n0'],
    'valid_p1_numa_values': ['n0', 'n1', 'i2'],
    'valid_nd_vnf_values': ['v8'],
    'valid_ss_vnf_values': ['v3']
}

# this table is for calculating default extra specs needed
extra_spec_needed_table = {
    "ns": {
        "aggregate_instance_extra_specs____ns": "true",
        "hw____mem_page_size": "large"
    },
    "nd": {
        "aggregate_instance_extra_specs____nd": "true",
        "aggregate_instance_extra_specs____v8": "true",
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
        "aggregate_instance_extra_specs____ss": "true",
        "aggregate_instance_extra_specs____s1": "true",
        "aggregate_instance_extra_specs____v3": "true"
    }
}

# any key will be added to extra_spec_needed_table need to be added here
default_extra_spec_calculated_table = {
    "aggregate_instance_extra_specs____ns": "",
    "aggregate_instance_extra_specs____nd": "",
    "aggregate_instance_extra_specs____nv": "",
    "aggregate_instance_extra_specs____gv": "",
    "aggregate_instance_extra_specs____ss": "",
    "aggregate_instance_extra_specs____c2": "",
    "aggregate_instance_extra_specs____c4": "",
    "aggregate_instance_extra_specs____v": "",
    "aggregate_instance_extra_specs____s1": "",
    "aggregate_instance_extra_specs____v3": "",
    "aggregate_instance_extra_specs____v8": "",
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
    # All flavor limits will be converted to integers, and must not
    # have any non-numeric values.
    # Root disk, block storage and object storage don't have limits
    # in ORM, but may be limited via SSP
    "vcpu_limit": "64",
    # vram_limit is in MB and must be a multiple of 1024
    "vram_limit": "393216",
    # swap_file_limit is in MB and must be a multiple of 1024
    "swap_file_limit": "393216",
    # ephemeral_limit is in GB
    "ephemeral_limit": "10000",
}
