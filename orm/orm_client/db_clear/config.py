"""config module."""

# db configs
sql_user = 'root'
sql_password = 'stack'
sql_server = '127.0.0.1'
sql_port = '3306'

# cms configs
customer_table_name = "customer"
customer_region_table_name = "customer_region"
cms_db_name = "orm_cms_db"


# cli configs
cli_dir = '../ormcli'

# rds configs
rds_db_name = 'orm_rds'
resource_status_table_name = 'resource_status'

# sot configs
local_repository_path = '/opt/app/orm/ORM'
file_name_format = 's_{}.yml'
relative_path_format = '/{}/hot/{}/{}'
