===============================
Ranger
===============================

Ranger is an OpenStack Resource Management tool capable of managing different types of clouds into one platform. Here are the following of what it provides: 
	- Multi-region common resource management.
	- Light weight, stateless (to a degree) and interface with external self-service portals.
	- Runs on DCP.
	- Resource agents will run on LCP to orchestrate and keep resources in sync from the centralized repository.  

Devstack Installation
---------------------
1. You can include ranger repository in `local.conf` when running devstack.
	`enable_plugin ranger git://git.openstack.org/openstack/ranger`

2. Make sure `MYSQL_PASSWORD` is included for creating and accessing the database.

Before Setting Up
-----------------

Make sure ranger-agent is running before installing and running ranger since that
is required for connecting with Openstack.

Installation
------------

1. Clone the repo and go to the `tools` directory.
  $ `git clone https://git.openstack.org/openstack/ranger`
  $ `cd ranger/tools`
2. To make changes to the port numbers and other configurations, please go to `base_config.py` under the `orm` folder before continuing to the next steps.
3. Run `./ranger_create_db.sh` to create the database.
4. Run `./setup_apache.sh` to create conf files for each of the services to apache.
5. Run `stack_orm.sh` to run ranger.
6. If `stack_orm.sh` is not running properly, please do the following:
	1. Go to the root of ranger.
	2. `sudo pip install -r requirements.txt`
	3. `sudo python setup.py develop 2>&1 | tee $root_dir/tools/install.log`

Running Ranger Services
-----------------------

To run each of the services, type in these commands in order to run each of the services.
	- Audit: `orm-audit`
	- Uuidgen: `orm-uuidgen`
	- RDS (Resource Distributor Service): `orm-rds`
	- RMS (Resource Management Service): `orm-rms`
	- FMS (Flavor Management Service): `orm-fms`
	- CMS (Customer Management Service): `orm-cms`
	- IMS (Image Management Service): `orm-ims`

For RMS, FMS, CMS, and IMS to be running, Audit, Uuidgen, and RDS must also be running properly as well in order to use them.
