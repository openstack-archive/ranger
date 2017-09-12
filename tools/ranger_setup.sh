#!/bin/bash
root_dir=/opt/stack/ranger
orm_dir=$root_dir/orm/
cd $root_dir
echo "-------------"
echo `pwd`
echo "-------------"
sudo python setup.py develop 2>&1 | tee ~/${dir}.log
sudo pip install -r requirements.txt
cd $orm_dir/common/client
cd audit
echo "-------------"
echo `pwd`
echo "-------------"
sudo python setup.py develop 2>&1 | tee ~/${dir}.log
sudo pip install -r requirements.txt
cd ../keystone
echo "-------------"
echo `pwd`
echo "-------------"
sudo python setup.py develop 2>&1 | tee ~/${dir}.log
sudo pip install -r requirements.txt
cd $orm_dir/orm_client
echo "-------------"
echo `pwd`
echo "-------------"
sudo python setup.py develop 2>&1 | tee ~/${dir}.log
sudo pip install -r requirements.txt
cd ormcli
echo "-------------"
echo `pwd`
echo "-------------"
sudo python setup.py develop 2>&1 | tee ~/${dir}.log
sudo pip install -r requirements.txt
cd $root_dir
