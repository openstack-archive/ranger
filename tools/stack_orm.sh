
source ./setenv.sh

root_dir=$RANGER_BASE

cd $root_dir
mkdir $root_dir/logs
sudo pip install -r requirements.txt --proxy $HTTP_PROXY
echo "-------------"
sudo python setup.py develop 2>&1 | tee $root_dir/tools/install.log

