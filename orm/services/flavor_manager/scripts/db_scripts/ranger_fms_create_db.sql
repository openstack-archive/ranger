SET sql_notes=0;

use orm;

#***** 
#* MySql script for Creating Table Flavor
#*****

create table if not exists flavor
	(
		internal_id bigint auto_increment not null,
		id varchar(64) not null,
		name varchar(250) not null,
		alias varchar(64) null,
		description varchar(100) not null,
		series enum('ns', 'nd', 'nv', 'gv', 'ss') not null,
		ram integer not null,
		vcpus integer not null,
		disk integer not null,
		swap integer not null,
		ephemeral integer not null,
		visibility varchar(10) not null,
		primary key (internal_id),
		unique id (id),
		index series (series),
		index visibility (visibility),
		unique name_idx (name)
	);
#


#***** 
#* MySql script for Creating Table flavor_extra_spec
#*****

create table if not exists flavor_extra_spec
	(
		flavor_internal_id bigint not null,
		key_name varchar(64) not null,
		key_value varchar(64) not null,
		foreign key (flavor_internal_id) references flavor(internal_id) ON DELETE CASCADE ON UPDATE NO ACTION,
		primary key (flavor_internal_id,key_name)
	);
#


#***** 
#* MySql script for Creating Table flavor_region
#*****

create table if not exists flavor_region
	(
		flavor_internal_id bigint not null,
		region_name varchar(64) not null,
		region_type varchar(32) not null DEFAULT 'single',
		foreign key (flavor_internal_id) references flavor(internal_id) ON DELETE CASCADE ON UPDATE NO ACTION,
		primary key (flavor_internal_id,region_name)
	);
#


#***** 
#* MySql script for Creating Table flavor_tenant
#*****

create table if not exists flavor_tenant
   (
	 flavor_internal_id bigint not null,
	 tenant_id varchar(64) not null,
	 foreign key (flavor_internal_id) references flavor(internal_id) ON DELETE CASCADE ON UPDATE NO ACTION,
	 primary key (flavor_internal_id,tenant_id));
#


#*****
#* MySql script for Creating Table flavor_tag
#*****

create table if not exists flavor_tag
	(
		flavor_internal_id bigint not null,
		key_name varchar(64) not null,
		key_value varchar(64) not null,
		foreign key (flavor_internal_id) references flavor(internal_id) ON DELETE CASCADE ON UPDATE NO ACTION,
		primary key (flavor_internal_id,key_name)
	);
#


#*****
#* MySql script for Creating Table flavor_option
#*****

create table if not exists flavor_option
	(
		flavor_internal_id bigint not null,
		key_name varchar(64) not null,
		key_value varchar(64) not null,
		foreign key (flavor_internal_id) references flavor(internal_id) ON DELETE CASCADE ON UPDATE NO ACTION,
		primary key (flavor_internal_id,key_name)
	);
#


#*****
#* MySql script for Creating View rds_resource_status_view
#*****

create or replace view rds_resource_status_view AS
    (
      SELECT ID, RESOURCE_ID, REGION,STATUS,
      ERR_CODE,OPERATION from resource_status);
