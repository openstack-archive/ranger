#!/bin/bash

source devstack/openrc admin admin

openstack project create 'tempest_m07057'
openstack project create 'tempest_m01690'
openstack project create 'tempest_m01691'

openstack user create 'm07057' --project 'tempest_m07057' --password devstack
openstack user create 'm01690' --project 'tempest_m01690' --password devstack
openstack user create 'm01691' --project 'tempest_m01691' --password devstack

openstack role add --project 'tempest_m07057' --user m07057 admin

openstack role add --project 'tempest_m01690' --user m01690 ResellerAdmin
openstack role add --project 'tempest_m01690' --user m01690 Member

openstack role add --project 'tempest_m01691' --user m01691 ResellerAdmin
openstack role add --project 'tempest_m01691' --user m01691 Member

openstack role add --project 'tempest_m07057' --user admin admin
openstack role add --project 'tempest_m01690' --user admin admin
openstack role add --project 'tempest_m01691' --user admin admin