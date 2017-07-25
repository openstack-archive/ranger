.. _install-ubuntu:

Install and configure for Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section describes how to install and configure the ranger
service for Ubuntu 14.04 (LTS).

.. include:: common_prerequisites.rst

Install and configure components
--------------------------------

#. Install the packages:

   .. code-block:: console

      # apt-get update

      # apt-get install

.. include:: common_configure.rst

Finalize installation
---------------------

Restart the ranger services:

.. code-block:: console

   # service openstack-ranger-api restart
