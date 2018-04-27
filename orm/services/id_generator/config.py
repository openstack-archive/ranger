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

verify = config.ssl_verify
database = {
    'connection_string': config.db_url + 'orm'
}
# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
