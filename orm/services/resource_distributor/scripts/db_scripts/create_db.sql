SET sql_notes=0;

use orm;


#*****
#* MySql script for Creating Table resource_status
#*****

create table if not exists resource_status
(
    id integer auto_increment not null,
	timestamp bigint not null,
	region varchar(64) not null,
	resource_id varchar(64) not null,
	status varchar(16) not null,
	transaction_id varchar(64),
	ord_notifier varchar(64) not null,
	err_msg varchar(255),
	err_code varchar(64),
	operation varchar(64),
	primary key (id),
	unique(resource_id, region));

#*****
#* MySql script for Creating Table image_metadata
#*****

create table if not exists image_metadata
(
    image_meta_data_id integer not null,
    checksum varchar(64) ,
	virtual_size varchar(64) ,
	size varchar(64) ,
	foreign key (image_meta_data_id) references resource_status(id) ON DELETE CASCADE ON UPDATE NO ACTION,
	primary key (image_meta_data_id));

#
