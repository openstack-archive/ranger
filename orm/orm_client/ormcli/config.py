# these values are used by ormcli to retrieve auth_token which is sent,
# along with region, with each cms and fms api request
import orm.base_config as config

tenant_name = config.token_auth_tenant
username = config.token_auth_user
password = config.token_auth_pass
auth_region = config.token_auth_version
orm_base_url = config.ranger_url
verify = config.ssl_verify
