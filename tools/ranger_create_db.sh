root_dir=/opt/stack/ranger
tools_dir=/opt/stack/ranger/tools
cd ..
cd orm/services/audit_trail_manager/scripts/shell_scripts/
bash create_db.sh
cd $root_dir
cd orm/services/customer_manager/scripts/shell_scripts/
bash create_db.sh
cd $root_dir
cd orm/services/flavor_manager/scripts/shell_scripts/
bash create_db.sh
cd $root_dir
cd orm/services/id_generator/scripts/shell_scripts/
bash create_db.sh
cd $root_dir
cd orm/services/image_manager/scripts/shell_scripts/
bash create_db.sh
cd $root_dir
cd orm/services/region_manager/scripts/shell_scripts/
bash create_db.sh
cd $root_dir
cd orm/services/resource_distributor/scripts/shell_scripts/
echo "Databases Created!"
cd $tools_dir
