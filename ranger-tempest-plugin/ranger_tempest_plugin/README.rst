=================================
Tempest Integration of ORM
=================================

This directory contains Tempest tests to cover the ORM project, as well
as a plugin to automatically load these tests into tempest.

See the tempest plugin docs for information on using it:
https://docs.openstack.org/tempest/latest/#using-plugins

See the tempest docs for information on writing new tests etc:
https://docs.openstack.org/tempest/latest/

Quickstart
----------

#. You first need to install Tempest in a venv.   If virtual environment is not
   installed install it using "sudo apt-get install python-virtualenv"::

   $ virtualenv .venv
   $ source .venv/bin/activate
   $ cd tempest
   $ pip install tox
   $ pip install tempest

#. Clone/install the plugin::

   $ pip install -e <path_of_the_plugin>
	For example:
	pip install -e /opt/stack/ranger



tempest.conf file
--------------------

This file should be present in tempest/etc


Following content must be added in tempest.conf file:


[auth]
# Use predefined credentials instead of creating users on the fly.
use_dynamic_credentials=false
admin_username = username
admin_password = password
admin_project_name= tenant/project/customer name
test_accounts_file=/opt/stack/tempest/etc/accounts.yaml -- Provide the accurate path of the accounts.yaml file

[oslo_concurrency]
lock_path = Provide respective path for oslo_concurrency

[orm]
uri = Provide orm url. For exmple: http://orm.***.***.***.com  
catalog_type = orm

accounts.yaml file
------------------

accounts.yaml file must be added in the path tempest/etc

Following content must be present with the given format in accounts.yaml file:

- username: 'username1'
  tenant_name: 'tenant_name1'
  password: 'password1'
- username: 'username2'
  tenant_name: 'tenant_name2'
  password: 'password2'



Running the tests
-----------------

To run all tests from this plugin, run from the tempest repo::

    $ tox -e all-plugin -- ranger

To run all tempest tests including this plugin, run::

    $ tox -e all-plugin


