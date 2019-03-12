import orm.base_config as config
# Pecan Application configurations
app = {
    'root': 'orm.services.resource_distributor.rds.controllers.root.RootController',
    'modules': ['orm.services.resource_distributor.rds'],
    'service_name': 'rds'
}

server = {
    'port': config.rds['port'],
    'host': config.orm_host
}

# DB configurations
database = {
    'url': config.db_connect
}

sot = {
    'type': 'git',
}

git = {
    # possible values : 'native', 'gittle'
    'type': 'native',
    'local_repository_path': config.rds['repo_local_location'],
    'file_name_format': 's_{}.yml',
    'relative_path_format': '/{}/hot/{}/{}',
    'commit_message_format': 'File was added to repository: {}',
    'commit_user': config.rds['repo_user'],
    'commit_email': config.rds['repo_email'],
    'git_server_url': config.rds['repo_remote_location'],
    'git_cmd_timeout': 45
}

audit = {
    'audit_server_url': config.audit_server['base_url'] + 'v1/audit/transaction',
    'num_of_send_retries': 3,
    'time_wait_between_retries': 1
}

cms = {
    'base_url': config.cms['base_url'],
    'delete_region': 'v1/orm/customers/{0}/regions/{1}',
    'delete_groups_region': 'v1/orm/groups/{0}/regions/{1}'
}

fms = {
    'base_url': config.fms['base_url'],
    'delete_region': 'v1/orm/flavors/{0}/regions/{1}'
}

ims = {
    'base_url': config.ims['base_url'],
    'metadata_path': 'v1/orm/images/{0}/regions/{1}/metadata',
    'delete_region': 'v1/orm/images/{0}/regions/{1}'
}

rms = {
    'base_url': config.rms['base_url'],
    'all_regions_path': 'v2/orm/regions'
}

ordupdate = {
    'discovery_url': 'http://' + config.orm_host,
    'discovery_port': config.rms['port'],
    'template_type': 'hot',
    # This flag should be false only in case the ord does not support https.
    'https_enabled': config.https_enabled,
    # ORD supports HTTPS and you don't need a certificate? set 'cert_path': ''
    'cert_path': config.cert_path
}

UUID_URL = config.uuid['base_url'] + 'v1/uuids'

# yaml configurations
yaml_configs = {
    'customer_yaml': {
        'customer_domain': config.rds['customer_domain'],
        'yaml_version': '2014-10-16',
        'yaml_options': {
            'quotas': True,
            'type': 'ldap'
        },
        'yaml_keys': {
            'quotas_keys': {
                'keypairs': 'key_pairs',
                'security_group_rules': 'security_group_rule',
                'security_groups': 'security_group',
                'floating_ips': 'floatingip',
                'networks': 'network',
                'ports': 'port',
                'routers': 'router',
                'members': 'member',
                'health_monitors': 'health_monitor',
                'pools': 'pool',
                'vips': 'vip',
                'vcpus': 'cores',
                'subnets': 'subnet'
            }
        },
        'cms_quota': {
            'resource_quotas': {
                'quota_unsupported_params': ['vip', 'member', 'pool',
                                             'nat_instance', 'route_table',
                                             'health_monitor', 'loadbalancer',
                                             'listener']
            }
        }
    },
    'flavor_yaml': {
        'yaml_version': '2013-05-23',
        'yaml_args': {
            'rxtx_factor': 1
        }
    },
    'image_yaml': {
        'yaml_version': '2014-10-16'
    },
    'group_yaml': {
        'yaml_version': '2014-10-16'
    }
}

# value of status to be blocked before creating any resource
block_by_status = "Submitted"

# this tells which values to allow resource submit the region
allow_region_statuses = ['functional']

region_resource_id_status = {
    # interval_time_validation in minutes
    'max_interval_time': {
        'images': 2,
        'tenants': 2,
        'flavors': 2,
        'users': 2,
        'default': 2
    },
    'allowed_status_values': {
        'Success',
        'Error',
        'Submitted'
    },
    'allowed_operation_type':
    {
        'create',
        'modify',
        'delete'
    },
    'allowed_resource_type':
    {
        'customer',
        'image',
        'flavor',
        'group'
    },
    'allowed_ranger_agent_resource_version':
    {
        'customer': '1.0',
        'image': '1.0',
        'flavor': '1.0',
        'group': '1.0'
    }
}

app_module = app['modules'][0]
logging = config.get_log_config(config.rds['log'],
                                app['service_name'],
                                app_module)

verify = config.ssl_verify

authentication = config.server_request_auth(app['service_name'])
