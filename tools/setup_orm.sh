root_dir=/opt/stack/ranger
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
sudo pecan serve $id_dir/config.py > /dev/null 2>&1 &
