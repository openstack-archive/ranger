import os
orm_host = '127.0.0.1'
log_location = '{}'
ranger_base = '/opt/stack/ranger'
log_location = ranger_base + '/logs/{}'
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
    'port': '7002',
    'log': log_location.format('audit_server.log')
}
ims = {
    'port': '8084',
    'log': log_location.format('ims.log')
}
rms = {
    'port': '7003',
    'log': log_location.format('rms.log')
}
rds = {
    'port': '8777'
    'log': log_location.format('rds.log')
}
