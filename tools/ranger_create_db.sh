#list_dirs=`ls -d */ | xargs` 
#for dir in $list_dirs; do
#  cd $dir
#  if [ -f /scripts/shell_scripts/"create_db.sh" ];
#  then
#     cd /scripts/shell_scripts
#     bash create_db.sh
#  else
#     echo "-------------"
#     echo WARNING `pwd` create_db.sh file DOES NOT EXIST
#     echo "-------------"
#  fi
#  cd $root_dir
#done
source ~/devstack/local.conf &> /dev/null
cd ~/ranger
cd orm/services/audit_trail_manager/scripts/shell_scripts
bash create_db.sh
cd ~/ranger
cd orm/services/customer_manager/scripts/shell_scripts
bash create_db.sh
cd ~/ranger
cd orm/services/flavor_manager/scripts/shell_scripts
bash create_db.sh
cd ~/ranger
cd orm/services/id_generator/scripts/shell_scripts
bash create_db.sh
cd ~/ranger
cd orm/services/image_manager/scripts/shell_scripts
bash create_db.sh
cd ~/ranger
cd orm/services/region_manager/scripts/shell_scripts
bash create_db.sh
cd ~/ranger
cd orm/services/resource_distributor/scripts/shell_scripts
bash create_db.sh
cd ~/ranger/tools
