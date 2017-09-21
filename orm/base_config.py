import os
orm_host = '0.0.0.0'
log_location = '{}'
ranger_base = os.path.dirname(os.path.abspath('orm'))
log_location = ranger_base + '/logs/{}'

uuid = {
    'port': '7001',
    'log': log_location.format('uuidgen.log')
}
