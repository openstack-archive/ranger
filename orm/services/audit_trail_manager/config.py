"""config module."""
import orm.base_config as config
# Server Specific Configurations
server = {
    'port': config.audit_server['port'],
    'host': config.orm_host
}

# DB configurations
database = {
    'url': 'mysql://root:stack@127.0.0.1/orm_audit?charset=utf8',
    # 'url': 'mysql://root:root@127.0.0.1/orm_audit?charset=utf8',
    'echo_statements': True
}

# Pecan Application Configurations
app = {
    'root': 'audit_server.controllers.root.RootController',
    'modules': ['audit_server'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/audit_server/templates',
    'debug': True,
    'errors': {
        404: '/error/404',
        '__force_dict__': True
    }
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'audit_server': {'level': 'DEBUG', 'handlers': ['console', 'logfile'],
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
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'color',
            'filename': config.audit_server['log']
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

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
