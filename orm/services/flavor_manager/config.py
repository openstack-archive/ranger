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
db_url = config.db_connect

database = {
    'connection_string': db_url.endswith('/orm') and db_url.replace("/orm", "/orm_fms_db") or (db_url + 'orm_fms_db')
}

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
    # The Keystone version currently in use. Can be either "2.0" or "3"
    "keystone_version": config.token_auth_version,
    "policy_file": config.fms['policy_file'],
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
    'valid_numa_values': ['n0'],
    'valid_nd_vnf_values': ['v8'],
    'valid_ss_vnf_values': ['v3']
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
    "ephemeral_limit": "10000",
}
