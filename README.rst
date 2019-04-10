===============================
Ranger
===============================

Ranger is an OpenStack Resource Management tool capable of managing different types of clouds into 
one platform. Here are the following of what it provides:

	- Multi-region common resource management.
	- Light weight, stateless and interface with external self-service portals.
	- Runs on DCP.
	- Resource agents will run on LCP to orchestrate and keep resources in sync from a 
          centralized repository.

Before Setting Up
-----------------

Make sure ranger-agent is running before installing and running ranger since that
is required for connecting with Openstack.


Devstack Installation
---------------------
1. Add the following line in `local.conf` to include ranger repository in your devstack.
	`enable_plugin ranger https://git.openstack.org/openstack/ranger`

2. Make sure `MYSQL_PASSWORD` is included for creating and accessing the database.

3. Run ./stack.sh from devstack directory.


Installation
------------

1. Navigate to ranger/tools directory: 
  $ `cd /opt/stack/ranger/tools`

2. To make changes to the port numbers and other configurations, please go to `base_config.py` under
   the `orm` folder before continuing to the next steps.

3. Run `./ranger_create_db.sh` to create ranger databases.

4. Run `./setup_apache.sh` to create conf files for each of the services to apache.

5. Run `stack_orm.sh` to set up ranger.

6. If `stack_orm.sh` is not running properly, navigate to /opt/stack/ranger and run the following:
	a. `sudo pip install -r requirements.txt`
	b. `sudo python setup.py develop 2>&1 | tee $root_dir/tools/install.log`


Generate ranger.conf file
-------------------------

$tox -e genconfig

A blank configuration file will be generated at etc/ranger.conf


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

For RMS, FMS, CMS, and IMS to be running, Audit, Uuidgen, and RDS must also be running properly as 
well in order to use them.


Docker Container: 
-----------------

1. $ `cd ranger`

2. Update /ranger/tools/.ssh/ranger with your ssh key to your git repo
   containing heat templates.
   You can clone https://github.com/ranger , but pull requests won't be accepted.

3. $ `sudo docker build -t ranger .`

4. $ `sudo docker run -h "ranger" --net host -it --privileged  ranger  bash`
   Creating docker image and publish will be done by deployment jobs.
   For Refernce and validation manually image could push using.
   a). $ `docker login <docker_user_id>`
   b). $ `docker tag ranger <docker_user_id>/ranger:0.1.0`
   c). $ `docker push <docker_user_id>/ranger:0.1.0`

5. This docker container will be used by helm chart to deploy ranger.
