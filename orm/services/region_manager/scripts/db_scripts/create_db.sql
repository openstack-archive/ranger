SET sql_notes=0;

create database if not exists orm_rms_db DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
use orm_rms_db;

create table if not exists rms_groups
   (
	id integer auto_increment not null,
	group_id varchar(64) not null,
	name varchar(64) not null,
	description varchar(255) not null,
	created TIMESTAMP not null DEFAULT 0,
	modified TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	primary key (id,group_id),
        unique grp_namex (name),
	unique group_idx (group_id));


create table if not exists region
   (
	id integer auto_increment not null,
	region_id varchar(64) not null,
	name varchar(64) not null,
	address_state varchar(64) not null,
	address_country varchar(64) not null,
	address_city varchar(64) not null,
	address_street varchar(64) not null,
	address_zip varchar(64) not null,
	region_status enum('building', 'functional', 'maintenance', 'down') not null,
	ranger_agent_version varchar(64) not null,
	open_stack_version varchar(64) not null,
	design_type Varchar(64) not null,
    location_type varchar(64) not null,
	vlcp_name varchar(64) not null,
	clli varchar(64) not null,
	description varchar(255) not null,
  created TIMESTAMP not null DEFAULT 0,
  modified TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	primary key (id,region_id,name),
        unique region_namex (name),
	unique region_idx (region_id));


create table if not exists group_region
   (
	group_id varchar(64) not null,
	region_id varchar(64) not null,
	primary key (group_id, region_id),
	foreign key (group_id) REFERENCES `rms_groups` (`group_id`) ON DELETE CASCADE,
	foreign key (region_id) REFERENCES `region` (`region_id`)  ON DELETE CASCADE);


create table if not exists region_end_point
   (
	region_id varchar(64) not null,
	end_point_type varchar(64) not null,
	public_url varchar(255) not null,
	primary key (region_id, end_point_type),
	foreign key (region_id) REFERENCES `region` (`region_id`) ON DELETE CASCADE,
	unique region_end_point_type(region_id, end_point_type));


create table if not exists region_meta_data
   (
    id integer auto_increment not null,
	region_id varchar(64) not null,
	meta_data_key varchar(64) not null,
	meta_data_value varchar(255) not null,
	primary key (id),
	foreign key (region_id) REFERENCES `region` (`region_id`) ON DELETE CASCADE,
    unique region_meta_data_key_value(region_id, meta_data_key, meta_data_value));
