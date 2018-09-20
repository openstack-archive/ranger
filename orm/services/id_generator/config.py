from orm import base_config as config


# Server Specific Configurations
server = {
    'port': config.uuid['port'],
    'host': config.orm_host,
    'name': 'uuid'
}
# Pecan Application Configurations
app = {
    'root': 'orm.services.id_generator.uuidgen.controllers.root.RootController',
    'modules': ['orm.services.id_generator.uuidgen'],
    'debug': True,
}

app_module = app['modules'][0]
logging = config.get_log_config(config.uuid['log'], server['name'], app_module)

verify = config.ssl_verify

# DB configurations
database = {
    'connection_string': config.db_connect
}
