source ./setenv.sh

root_dir=$RANGER_BASE

audit_dir=$root_dir/orm/services/audit_trail_manager
customer_dir=$root_dir/orm/services/customer_manager
flavor_dir=$root_dir/orm/services/flavor_manager
id_dir=$root_dir/orm/services/id_generator
image_dir=$root_dir/orm/services/image_manager
region_dir=$root_dir/orm/services/region_manager
resource_dir=$root_dir/orm/services/resource_distributor

sudo ln -s $audit_dir/audit_server.conf /etc/apache2/sites-enabled/audit_server.conf
sudo ln -s $customer_dir/cms_rest.conf /etc/apache2/sites-enabled/cms_rest.conf
sudo ln -s $flavor_dir/fms_rest.conf /etc/apache2/sites-enabled/fms_rest.conf
sudo ln -s $id_dir/uuidgen.conf /etc/apache2/sites-enabled/uuidgen.conf
sudo ln -s $image_dir/ims.conf /etc/apache2/sites-enabled/ims.conf
sudo ln -s $region_dir/rms.conf /etc/apache2/sites-enabled/rms.conf
sudo ln -s $resource_dir/rds.conf /etc/apache2/sites-enabled/rds.conf

