root_dir=/opt/stack/ranger
audit_dir=$root_dir/orm/services/audit_manager
customer_dir=$root_dir/orm/services/customer_manager
flavor_dir=$root_dir/orm/services/flavor_manager
id_dir=$root_dir/orm/services/id_generator
image_dir=$root_dir/orm/services/image_manager
region_dir=$root_dir/orm/services/region_manager
resource_dir=$root_dir/orm/services/resource_distributor
cd $root_dir
list_dirs=`ls -d */ | xargs`
for dir in $list_dirs; do
  cd $dir
  echo "-------------"
  echo `pwd`
  echo "-------------"
  sudo python setup.py develop 2>&1 | tee ~/${dir}.log
  sudo pip install -r ../requirements.txt
  #sudo pecan serve config.py & 2>&1 | tee ~/${dir}.log
  cd $root_dir
done
sudo pecan serve $audit_dir/config.py & 2>&1 | tee ~/${dir}.log
sudo pecan serve $customer_dir/config.py & 2>&1 | tee ~/${dir}.log
sudo pecan serve $flavor_dir/config.py & 2>&1 | tee ~/${dir}.log
sudo pecan serve $id_id/config.py & 2>&1 | tee ~/${dir}.log
sudo pecan serve $image_dir/config.py & 2>&1 | tee ~/${dir}.log
sudo pecan serve $region_dir/config.py & 2>&1 | tee ~/${dir}.log
sudo pecan serve $resource_dir/config.py & 2>&1 | tee ~/${dir}.log
