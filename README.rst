===============================
Ranger
===============================

Openstack Resource Management


Devstack Installation
---------------------
1. You can include ranger repository in `local.conf` when running devstack.
	`enable_plugin ranger git://git.openstack.org/openstack/ranger`

2. Make sure `MYSQL_PASSWORD` is included for creating and accessing the database.

Installation
------------

1. Clone the repo and go to the `tools` directory.

  $ `git clone https://git.openstack.org/openstack/ranger`

  $ `cd ranger/tools`

2. Run `./ranger_create_db.sh` to create the database.

3. Run `./setup_apache.sh` to create conf files for each of the services to apache.

4. Run `stack_orm.sh` to run ranger.

5. If `stack_orm.sh` is not running properly, please do the following:
	1. Go to the root of ranger.
	
	2. `sudo pip install -r requirements.txt`
	
	3. `sudo python setup.py develop 2>&1 | tee $root_dir/tools/install.log`

6. To make changes to the port numbers and other configurations, please go to `base_config.py` under the `orm` folder.
