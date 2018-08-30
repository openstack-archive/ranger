# Pecan Application configurations
app = {
    'root': 'orm.services.resource_distributor.rds.controllers.root.RootController',
    'modules': ['orm.services.resource_distributor.rds'],
    'service_name': 'RDS'
}

server = {
    'port': '8777',
    'host': '0.0.0.0'
}

# DB configurations
database = {
    'url': 'mysql://root:stack@127.0.0.1/orm_rds?charset=utf8'
}

sot = {
    'type': 'git',
}

git = {
    # possible values : 'native', 'gittle'
    'type': 'gittle',
    'local_repository_path': '/home/orm/SoT/ORM',
    'file_name_format': 's_{}.yml',
    'relative_path_format': '/Document_Store/LCP/{}/{}/{}',
    'commit_message_format': 'File was added to repository: {}',
    'commit_user': 'orm_rds',
    'commit_email': 'orm_rds@att.com',
    'git_server_url': 'orm_rds@127.0.0.1:~/SoT/ORM.git'

}

audit = {
    'audit_server_url': 'http://127.0.0.1:8776/v1/audit/transaction',
    'num_of_send_retries': 3,
    'time_wait_between_retries': 1
}

authentication = {
    'enabled': False,
    'mech_id': 'admin',
    'mech_pass': 'stack',
    'rms_url': 'http://127.0.0.1:8080',
    'tenant_name': 'admin'
}

ordupdate = {
    'discovery_url': '127.0.0.1',
    'discovery_port': '8080',
    'template_type': 'hot'
}

verify = False

UUID_URL = 'http://127.0.0.1:8090/v1/uuids'

yaml_configs = {
    'customer_yaml': {
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
    }
}

# yaml configuration for create flavor
yaml_flavor_version = '2014-10-16'

# value of status to be blocked before creating any resource
block_by_status = "Submitted"

# this tells which values to allow resource submit the region
allow_region_statuses = ['functional']

keystone_role_list = {
    'member': '68cddd1a64eb4eae9c5d82581bc55426',
    'reselleradmin': '2f358be4320a401cb7517c5938d93003',
    'wwiftoperator': '852113b8aeba420eb6176f896e85d1fb',
    '_member_': '6b29638c65de4df09b4d3ee0bee3ca39',
    'admin': '084103f31503413a93d4e3b3383ca954'
}

# region_resource_id_status configurations
region_resource_id_status = {
    # interval_time_validation in minutes
    'max_interval_time': {
        'images': 60,
        'tenants': 60,
        'flavors': 60,
        'users': 60,
        'default': 60
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
        'flavor'
    }
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'rds': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
        'pecan': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False},
        'py.warnings': {'handlers': ['console']},
        '__force_dict__': True
    },
    'handlers': {
        'console': {
            'level': 'CRITICAL',
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        },
        'Logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 50000000,
            'backupCount': 10,
            'filename': '/tmp/rds.log',
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
            'format': '%(asctime)s [%(padded_color_levelname)s] [%(name)s] [%(threadName)s] %(message)s',
            '__force_dict__': True
        }
    }
}
