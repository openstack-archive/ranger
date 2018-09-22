SET sql_notes=0;

use orm;

create table if not exists cms_role
   (
	 id integer auto_increment not null,
	 name varchar(64) not null,
	 primary key (id));

create table if not exists cms_user
   (
	 id integer auto_increment not null,
	 name varchar(64) not null,
	 primary key (id),
	 unique name_idx (name));

create table if not exists cms_region
   (
	 id integer auto_increment not null,
	 name varchar(64) not null,
	 type varchar(64) not null DEFAULT 'single',
	 primary key (id),
	 unique name_idx (name));


create table if not exists customer
   (
	 id integer auto_increment not null,
	 uuid varchar(64) not null,
 	 name varchar(64) not null,
	 description varchar(255) not null,
	 enabled tinyint not null,
	 primary key (id),
	 unique uuid_idx (uuid),
	 unique name_idx(name));

create table if not exists customer_metadata
	(
	 customer_id integer not null,
	 field_key varchar(64) not null,
	 field_value varchar(64) not null,
	 primary key (customer_id, field_key),
	 foreign key (customer_id) references customer(id) ON DELETE CASCADE
	);

create table if not exists customer_region
   (
	 customer_id integer not null,
	 region_id integer not null,
	 primary key (customer_id,region_id),
	 index region_id (region_id),
  	 foreign key (customer_id) REFERENCES `customer` (`id`) ON DELETE CASCADE,
	 foreign key (region_id) REFERENCES `cms_region` (`id`));

create table if not exists quota
   (
	 id integer auto_increment not null,
	 customer_id integer not null,
	 region_id integer not null,
	 quota_type varchar(64) not null,
	 foreign key (region_id) references cms_region(id),
	 primary key (id),
	 unique quota_type (customer_id,region_id,quota_type),
	 foreign key (`customer_id`, `region_id`) REFERENCES `customer_region` (`customer_id`, `region_id`) ON DELETE CASCADE ON UPDATE NO ACTION
   );

create table if not exists quota_field_detail
   (
	 id integer auto_increment not null,
	 quota_id integer not null,
	 field_key varchar(64) not null,
	 field_value varchar(64) not null,
	 primary key (id),
	 foreign key (quota_id) references quota(id) ON DELETE CASCADE,
	 unique key_idx (quota_id,field_key));

create table if not exists user_role
   (
	 customer_id integer not null,
	 region_id integer not null,
	 user_id integer not null,
	 role_id integer not null,
	 primary key (customer_id,region_id,user_id,role_id),
	 foreign key (customer_id, region_id) REFERENCES customer_region (`customer_id`, `region_id`) ON DELETE CASCADE,
	 foreign key (customer_id) references customer(id) ON DELETE CASCADE,
	 foreign key (region_id) references cms_region(id),
	 foreign key (user_id) references cms_user(id),
	 foreign key (role_id) references cms_role(id),
	 index region_id (region_id),
	 index user_id (user_id));

create table if not exists cms_domain
   (
         id integer auto_increment not null,
         name varchar(64) not null,
         primary key (id),
         unique name_idx (name));

create table if not exists cms_group
   (
         id integer auto_increment not null,
         domain_id integer not null,
         name varchar(64) not null,
         description varchar(255) not null,
         primary key (id, domain_id),
         foreign key (`domain_id`) references `cms_domain` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
         unique name_idx (name),
         unique domain_id_idx (domain_id));

create table if not exists group_role
   (
         role_id integer not null,
         group_id integer not null,
         primary key (role_id, group_id),
         foreign key (`role_id`) references `cms_role` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
         foreign key (`group_id`) references `cms_group` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
         index role_id (role_id),
         index group_id (group_id));

create table if not exists group_region
   (
         region_id integer not null,
         group_id integer not null,
         primary key (region_id, group_id),
         foreign key (`group_id`) references `cms_group` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
         foreign key (`region_id`) references `cms_region` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
         index group_id_idx (group_id));

create table if not exists group_user
   (
         group_id integer not null,
         user_id integer not null,
         region_id integer not null default -1,
         primary key (group_id, user_id),
         foreign key (`user_id`) references `cms_user` (`id`) ON DELETE CASCADE,
         foreign key (`region_id`) references `group_region` (`region_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
         foreign key (`group_id`) references `cms_group` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
         index user_id (user_id),
         index group_id (group_id),
         index region_id (region_id));

create table if not exists group_customer
   (
         group_id integer not null,
         customer_id integer not null,
         region_id integer not null,
         primary key (group_id, customer_id, region_id),
         foreign key (`group_id`) references `cms_group` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
         foreign key (`customer_id`) references `customer` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
         foreign key (`region_id`) references `cms_region` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
         index customer_id_idx (customer_id),
         index regio_id_idx (region_id));

create or replace view rds_resource_status_view AS
    (
        SELECT id, resource_id, region, status,
        err_code, operation from resource_status);
