# Pecan Application configurations
app = {
    'root': 'rds.controllers.root.RootController',
    'modules': ['rds'],
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
    'type': 'native',
    'local_repository_path': '/opt/app/orm/ORM',
    'file_name_format': 's_{}.yml',
    'relative_path_format': '/{}/hot/{}/{}',
    'commit_message_format': 'File was added to repository: {}',
    'commit_user': 'orm_rds',
    'commit_email': 'orm_rds@att.com',
    'git_server_url': 'orm_rds@127.0.0.1:~/SoT/ORM.git',
    'git_cmd_timeout': 45
}

audit = {
    'audit_server_url': 'http://127.0.0.1:8776/v1/audit/transaction',
    'num_of_send_retries': 3,
    'time_wait_between_retries': 1
}

ims = {
    'base_url': 'http://127.0.0.1:8084/',
    'metadata_path': 'v1/orm/images/{0}/regions/{1}/metadata'
}

rms = {
    'base_url': 'http://127.0.0.1:8080/',
    'all_regions_path': 'v2/orm/regions'
}

ordupdate = {
    'discovery_url': 'http://127.0.0.1',
    'discovery_port': 8080,
    'template_type': 'hot',
    # This flag should be false only in case the ord does not support https.
    'https_enabled': True,
    # ORD supports HTTPS and you don't need a certificate? set 'cert_path': ''
    'cert_path': '../resources/ord.crt'
}

verify = False

UUID_URL = 'http://127.0.0.1:8090/v1/uuids'

# yaml configurations
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
                'network': 'networks',
                'port': 'ports',
                'router': 'routers',
                'subnet': 'subnets',
                'floatingip': 'floating_ips'
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

# value of status to be blocked before creating any resource
block_by_status = "Submitted"

# this tells which values to allow resource submit the region
allow_region_statuses = ['functional']

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
        'orm_common': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
        'audit_client': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'], 'propagate': False},
        'pecan': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False},
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
            'filename': '/var/logs/ranger/rds.log',
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


authentication = {
    "enabled": True,
    "mech_id": "admin",
    "mech_pass": "stack",
    "tenant_name": "admin",
    # The Keystone version currently in use. Can be either "2.0" or "3"
    "keystone_version": "2.0"
}
