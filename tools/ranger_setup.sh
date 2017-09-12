source openrc
root_dir=~/ranger
cd $root_dir
list_dirs=`ls -d */ | xargs`
for dir in $list_dirs; do
  cd $dir
  echo "-------------"
  echo `pwd`
  echo "-------------"
  #cd ~/scripts/shell_scripts
  #bash ~/create_db.sh
  sudo python ~/ranger/setup.py develop 2>&1 | tee ~/${dir}.log
  sudo pip install -r ~/ranger/requirements.txt
  #sudo pecan serve config.py & 2>&1 | tee ~/${dir}.log
  cd $root_dir
done
