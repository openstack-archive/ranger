# Server Specific Configurations
server = {
    'port': '1337',
    'host': '0.0.0.0'
}

UUID_URL = 'http://127.0.0.1:8090/v1/uuids'
RDS_STATUS_URL = 'http://127.0.0.1:8777/v1/rds/status'
SECONDS_BEFORE_STATUS_UPDATE = 5

status_data = {
    'ord_notifier_id': '1',
    'region': 'mtn6',
    'status': 'Success',
    'error_code': '',
    'error_msg': ''
}

image_extra_metadata = {
    'checksum': 'd4ea426817a742328da91438e3a3208b',
    # Size should be int and virtual_size should be real None once our
    # database supports these values
    'size': '1337',
    'virtual_size': 'None'
}

# Pecan Application Configurations
app = {
    'root': 'ordmockserver.controllers.root.RootController',
    'modules': ['ordmockserver'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/restapi/templates',
    'debug': True,
    'errors': {
        404: '/error/404',
        '__force_dict__': True
    }
}

verify = False

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'restapi': {'level': 'DEBUG', 'handlers': ['console','logfile'], 'propagate': False},
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
        'logfile' : {
            'class': 'logging.FileHandler',
            'filename' : '/home/pecanlogs.log',
            'level' : 'DEBUG',
            'formatter' : 'simple'
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


"""
# orign logging
logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'restapi': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False},
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
"""
# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
