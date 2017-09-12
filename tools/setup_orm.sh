root_dir=/opt/stack/upstream_ranger/ranger

audit_dir=$root_dir/orm/services/audit_manager
customer_dir=$root_dir/orm/services/customer_manager
flavor_dir=$root_dir/orm/services/flavor_manager
id_dir=$root_dir/orm/services/id_generator
image_dir=$root_dir/orm/services/image_manager
region_dir=$root_dir/orm/services/region_manager
resource_dir=$root_dir/orm/services/resource_distributor
cd $root_dir
sudo pip install -r requirements.txt --proxy $HTTP_PROXY
cd $root_dir/orm/services
list_dirs=`ls -d */ | xargs`
for dir in $list_dirs; do
  cd $dir
  echo "-------------"
  echo `pwd`
  echo "-------------"
  sudo python setup.py develop 2>&1 | tee ~/${dir}.log
  cd $root_dir
done
mkdir $root_dir/logs

sudo ln -s $audit_dir/audit_server.conf /etc/apache2/sites-enabled/audit_server.conf
sudo ln -s $customer_dir/cms_rest.conf /etc/apache2/sites-enabled/cms_rest.conf
sudo ln -s $flavor_dir/fms_rest.conf /etc/apache2/sites-enabled/fms_rest.conf
sudo ln -s $id_dir/uuidgen.conf /etc/apache2/sites-enabled/uuidgen.conf
sudo ln -s $image_dir/ims.conf /etc/apache2/sites-enabled/ims.conf
sudo ln -s $region_dir/rms.conf /etc/apache2/sites-enabled/rms.conf
sudo ln -s $resource_dir/rds.conf /etc/apache2/sites-enabled/rds.conf
