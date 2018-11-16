import orm.base_config as config
from orm.common.orm_common.hooks.api_error_hook import APIErrorHook
from orm.common.orm_common.hooks.security_headers_hook import SecurityHeadersHook
from orm.services.flavor_manager.fms_rest.hooks.service_hooks import TransIdHook
global TransIdHook
global APIErrorHook
global SecurityHeadersHook

# Server Specific Configurations
server = {
    'port': config.fms['port'],
    'host': config.orm_host,
    'name': 'fms'
}

cache_seconds = 0

# Pecan Application Configurations
app = {
    'root': 'orm.services.flavor_manager.fms_rest.controllers.root.RootController',
    'modules': ['orm.services.flavor_manager.fms_rest'],
    'debug': True,
    'hooks': lambda: [TransIdHook(), APIErrorHook(), SecurityHeadersHook()]
}

app_module = app['modules'][0]
logging = config.get_log_config(config.fms['log'], server['name'], app_module)

# DB configurations
database = {
    'connection_string': config.db_connect
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

application_root = 'http://localhost:{0}'.format(server['port'])

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

flavor_series = {
    'valid_series': [
        'p1'
    ]
}

# valid_flavor_options
flavor_options = {
    'valid_p1_numa_values': [
        'n0', 'n1'
    ],
    'valid_p1_opt_values': [
        'n0', 'n1', 'i2'
    ]
}

flavor_limits = {
    # All flavor limits will be converted to integers, and must not
    # have any non-numeric values.
    # Root disk, block storage and object storage don't have limits
    "vcpu_limit": "64",
    # vram_limit is in MB and must be a multiple of 1024
    "vram_limit": "393216",
    # swap_file_limit is in MB and must be a multiple of 1024
    "swap_file_limit": "393216",
    # ephemeral_limit is in GB
    "ephemeral_limit": "10000"
}

verify = config.CONF.ssl_verify

authentication = config.server_request_auth(server['name'])
