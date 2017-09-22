import orm.base_config as config
# Server Specific Configurations
server = {
    'port': config.uuid['port'],
    'host': config.orm_host
}
# Pecan Application Configurations
app = {
    'root': 'orm.services.id_generator.uuidgen.controllers.root.RootController',
    'modules': ['orm.services.id_generator.uuidgen'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/uuidgen/templates',
    'debug': True,
    'errors': {
        404: '/error/404',
        '__force_dict__': True
    }
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'uuidgen': {'level': 'DEBUG', 'handlers': ['console', 'Logfile'],
                    'propagate': False},
        'pecan': {'level': 'DEBUG', 'handlers': ['console'],
                  'propagate': False},
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
            'filename': config.uuid['log'],
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

verify = False

database = {
    'connection_string': 'mysql://root:stack@localhost:3306/orm'
}
# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
