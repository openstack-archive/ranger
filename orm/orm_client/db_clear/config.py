"""config module."""

# db configs
sql_user = 'root'
sql_password = 'xxxxxxxxxxx'
sql_server = '127.0.0.1'
sql_port = '3306'

# cms configs
customer_table_name = "customer"
customer_tbl_column = "uuid"
customer_region_table_name = "customer_region"
cms_db_name = "orm_cms_db"

# fms configs
flavor_table_name = "flavor"
flavor_tbl_column = "id"
flavor_region_table_name = "flavor_region"
fms_db_name = "orm_fms_db"

# ims configs
image_table_name = "image"
image_tbl_column = "id"
image_region_table_name = "image_region"
ims_db_name = "orm_ims_db"

# cli configs
cli_dir = '../ormcli'

# rds configs
rds_db_name = 'orm_rds'
resource_status_table_name = 'resource_status'
image_metadata_table_name = 'image_metadata'

# sot configs
local_repository_path = '/opt/app/orm/ORM'
file_name_format = 's_{}.yml'
relative_path_format = '/{}/hot/{}/{}'
