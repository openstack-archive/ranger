Prerequisites
-------------

Before you install and configure the ranger service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``ranger`` database:

     .. code-block:: none

        CREATE DATABASE ranger;

   * Grant proper access to the ``ranger`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON ranger.* TO 'ranger'@'localhost' \
          IDENTIFIED BY 'RANGER_DBPASS';
        GRANT ALL PRIVILEGES ON ranger.* TO 'ranger'@'%' \
          IDENTIFIED BY 'RANGER_DBPASS';

     Replace ``RANGER_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``ranger`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt ranger

   * Add the ``admin`` role to the ``ranger`` user:

     .. code-block:: console

        $ openstack role add --project service --user ranger admin

   * Create the ranger service entities:

     .. code-block:: console

        $ openstack service create --name ranger --description "ranger" ranger

#. Create the ranger service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        ranger public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        ranger internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        ranger admin http://controller:XXXX/vY/%\(tenant_id\)s
