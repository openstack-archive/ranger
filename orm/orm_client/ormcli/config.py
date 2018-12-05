# these values are used by ormcli to retrieve auth_token which is sent,
# along with region, with each cms and fms api request
import orm.base_config as config

tenant_name = config.CONF.keystone_authtoken.project_name
username = config.CONF.keystone_authtoken.username
password = config.CONF.keystone_authtoken.password
auth_region = config.CONF.cli.base_region
rms_base_url = config.rms['rms_url']
cms_base_url = config.cms['cms_url']
fms_base_url = config.fms['fms_url']
ims_base_url = config.ims['ims_url']
verify = config.CONF.ssl_verify
