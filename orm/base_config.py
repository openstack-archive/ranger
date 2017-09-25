orm_protocal = 'http'
orm_host = '127.0.0.1'
log_location = '{}'
ranger_base = '/opt/stack/ranger'
log_location = ranger_base + '/logs/{}'
db_user = 'root'
db_pass = 'stack'
db_host = '127.0.0.1'
ssl_verify = False
token_auth_enabled = True
token_auth_user = 'admin'
token_auth_pass = 'nova'
token_auth_tenant = 'admin'
token_auth_user_role = 'admin'

db_url = 'mysql://' + db_user + ':' + db_pass + '@' + db_host + ':3306/'

uuid = {
    'port': '7001',
    'log': log_location.format('uuidgen.log')
}
cms = {
    'port': '7080',
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, cms['port']),
    'policy_file': ranger_base + 'orm/services/customer_manager/cms_rest/etc/policy.json',
    'log': log_location.format('cms.log')
}
fms = {
    'port': '8082',
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, fms['port']),
    'policy_file': ranger_base + 'orm/services/flavor_manager/fms_rest/etc/policy.json',
    'log': log_location.format('fms.log')
}
audit_server = {
    'port': '7002',
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, audit_server['port']),
    'log': log_location.format('audit_server.log')
}
ims = {
    'port': '8084',
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, ims['port']),
    'policy_file': ranger_base + 'orm/services/image_manager/ims/etc/policy.json',
    'log': log_location.format('ims.log')
}
rms = {
    'port': '7003',
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, rms['port']),
    'policy_file': ranger_base + 'orm/services/region_manager/rms/etc/policy.json',
    'log': log_location.format('rms.log')
}
rds = {
    'port': '8777',
    'repo_local_location': '/opt/app/orm/ORM',
    'repo_user': 'orm_rds',
    'repo_email': 'orm_rds@test.com',
    'repo_remote_location': 'orm_rds@127.0.0.1:~/SoT/ORM.git',
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, rds['port']),
    'log': log_location.format('rds.log')
}
