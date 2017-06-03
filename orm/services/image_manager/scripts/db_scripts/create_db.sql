create database if not exists orm_ims_db DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
use orm_ims_db;

#***** 
#* MySql script for Creating Table image
#*****

create table if not exists image
   (
	 id varchar(64) not null,
	 name varchar(64) not null,
	 enabled smallint not null,
	 url varchar(250) not null,
	 protected smallint not null,
	 visibility varchar(10) not null,
	 disk_format varchar(64) not null,
	 container_format varchar(64) not null,
	 min_disk integer not null,
	 min_ram integer not null,
	 owner varchar(128) not null,
	 `schema` varchar(128) not null,
	 created_at integer not null,
	 updated_at integer not null,
	 primary key (id),
	 unique name (name),
	 index visibility (visibility)
   );
#

#***** 
#* MySql script for Creating Table image_property
#*****

create table if not exists image_property
   (
	 image_id varchar(64) not null,
	 key_name varchar(64) not null,
	 key_value varchar(64) not null,
	 primary key (image_id,key_name),
	 foreign key (image_id) references image(id) ON DELETE CASCADE ON UPDATE NO ACTION
   );
#

#***** 
#* MySql script for Creating Table image_region
#*****

create table if not exists image_region
   (
	 image_id varchar(64) not null,
	 region_name varchar(64) not null,
	 region_type varchar(32) not null,
	 checksum varchar(64) not null,
	 size varchar(64) not null,
	 virtual_size varchar(64) not null,
	 primary key (image_id,region_name),
	 foreign key (image_id) references image(id) ON DELETE CASCADE ON UPDATE NO ACTION
   );
#

#***** 
#* MySql script for Creating Table image_tag
#*****

create table if not exists image_tag
   (
	 image_id varchar(64) not null,
	 tag varchar(64) not null,
	 primary key (image_id,tag),
	 foreign key (image_id) references image(id) ON DELETE CASCADE ON UPDATE NO ACTION
   );
#


#***** 
#* MySql script for Creating Table image_customer
#*****

create table if not exists image_customer
   (
	 image_id varchar(64) not null,
	 customer_id varchar(64) not null,
	 primary key (image_id,customer_id),
	 foreign key (image_id) references image(id) ON DELETE CASCADE ON UPDATE NO ACTION
   );
#
