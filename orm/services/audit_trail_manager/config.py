"""config module."""
import orm.base_config as config
# Server Specific Configurations
server = {
    'port': config.audit_server['port'],
    'host': config.orm_host,
    'name': 'audit'
}

# DB configurations
database = {
    'url': config.db_connect, 'echo_statements': False
}

# Pecan Application Configurations
app = {
    'root': 'orm.services.audit_trail_manager.audit_server.controllers.root.RootController',
    'modules': ['orm.services.audit_trail_manager.audit_server'],
    'debug': True,
}

app_module = app['modules'][0]
logging = config.get_log_config(config.audit_server['log'], server['name'], app_module)

verify = config.ssl_verify

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
