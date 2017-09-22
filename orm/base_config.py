import os
orm_host = '0.0.0.0'
log_location = '{}'
ranger_base = os.path.dirname(os.path.abspath('orm'))
log_location = ranger_base+'/logs/{}'
uuid = {
    'port': '7001',
    'log': log_location.format('uuidgen.log')
}
cms = {
    'port': '7080',
    'log': log_location.format('cms.log')
}
fms = {
    'port': '8082',
    'log': log_location.format('fms.log')
}
audit_server = {
    'port': '8776',
    'log': log_location.format('audit_server.log')
}
ims = {
    'port': '8084',
    'log': log_location.format('ims.log')
}
rms = {
    'port': '8080',
    'log': log_location.format('rms.log')
}
rds = {
    'port': '8778',
    'log': log_location.format('rds.log')
}
