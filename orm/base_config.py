orm_protocal = 'http'
orm_host = '127.0.0.1'
log_location = '{}'
ranger_base = '/opt/app/ranger'
log_location = '/var/log/ranger/{}'
db_user = 'root'
db_pass = 'devstack'
db_host = '127.0.0.1'
ssl_verify = False
token_auth_enabled = False
token_auth_user = 'admin'
token_auth_pass = 'devstack'
token_auth_tenant = 'admin'
token_auth_user_role = 'admin'
uuid_port = 7001
audit_port = 7002
rms_port = 7003
rds_port = 8777
cms_port = 7080
fms_port = 8082
ims_port = 8084

db_url = 'mysql://' + db_user + ':' + db_pass + '@' + db_host + ':3306/'

uuid = {
    'port': uuid_port,
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, uuid_port),
    'log': log_location.format('uuidgen.log')
}
cms = {
    'port': cms_port,
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, cms_port),
    'policy_file': ranger_base + '/orm/services/customer_manager/cms_rest/etc/policy.json',
    'log': log_location.format('cms.log')
}
fms = {
    'port': fms_port,
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, fms_port),
    'policy_file': ranger_base + '/orm/services/flavor_manager/fms_rest/etc/policy.json',
    'log': log_location.format('fms.log')
}
audit_server = {
    'port': audit_port,
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, audit_port),
    'log': log_location.format('audit_server.log')
}
ims = {
    'port': ims_port,
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, ims_port),
    'policy_file': ranger_base + '/orm/services/image_manager/ims/etc/policy.json',
    'log': log_location.format('ims.log')
}
rms = {
    'port': rms_port,
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, rms_port),
    'policy_file': ranger_base + '/orm/services/region_manager/rms/etc/policy.json',
    'log': log_location.format('rms.log')
}
rds = {
    'port': rds_port,
    'repo_local_location': '/opt/app/git_repo',
    'repo_user': 'orm',
    'repo_email': 'orm@test.com',
    'repo_remote_location': 'git@127.0.0.1:/home/repo/ORM.git',
    'base_url': '{}://{}:{}/'.format(orm_protocal, orm_host, rds_port),
    'log': log_location.format('rds.log')
}
cli = {
    'base_region': 'local'
}
