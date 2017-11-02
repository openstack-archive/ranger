from oslo_config import cfg


CONF = cfg.CONF

# Server Specific Configurations
server = {
    'port': CONF.uuid.port,
    'host': CONF.api.host
}
# Pecan Application Configurations
app = {
    'root': 'orm.services.id_generator.uuidgen.controllers.root.RootController',
    'modules': ['orm.services.id_generator.uuidgen'],
    'debug': True,
}

verify = CONF.api.ssl_verify

database = {
    'connection_string': 'mysql://' + CONF.db.user + ':'
                                    + CONF.db.password + '@'
                                    + CONF.db.host + ':'
                                    + str(CONF.db.port) + '/' + 'orm'
}
# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
