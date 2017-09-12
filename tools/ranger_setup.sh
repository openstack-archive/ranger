root_dir=/opt/stack/ranger
cd $root_dir
list_dirs=`ls -d */ | xargs`
echo `dir`
for dir in $list_dirs; do
  cd $dir
  echo "-------------"
  echo `pwd`
  echo "-------------"
  sudo python setup.py develop 2>&1 | tee ~/${dir}.log
  sudo pip install -r $root_dir/requirements.txt
  sudo pecan serve config.py & 2>&1 | tee ~/${dir}.log
  cd $root_dir
done
