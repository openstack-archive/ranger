from orm import base_config as config


# Server Specific Configurations
server = {
    'port': config.uuid['port'],
    'host': config.orm_host
}
# Pecan Application Configurations
app = {
    'root': 'orm.services.id_generator.uuidgen.controllers.root.RootController',
    'modules': ['orm.services.id_generator.uuidgen'],
    'debug': True,
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'orm.services.id_generator.uuidgen': {
            'level': config.debug_level,
            'handlers': ['console', 'Logfile'],
            'propagate': False
        },
        'pecan': {'level': config.debug_level, 'handlers': ['console'],
                  'propagate': False},
        'py.warnings': {'handlers': ['console']},
        '__force_dict__': True
    },
    'handlers': {
        'console': {
            'level': config.debug_level,
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        },
        'Logfile': {
            'level': config.debug_level,
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

verify = config.ssl_verify

# DB configurations
db_url = config.db_connect

database = {
    'connection_string': db_url.endswith('/orm') or (db_url + 'orm')
}
# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
