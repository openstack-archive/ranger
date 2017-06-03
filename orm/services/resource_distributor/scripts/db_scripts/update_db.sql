use orm_rds;


DELIMITER ;;

#*****
#* MySql script for Creating Table image_metadata
#*****
DROP PROCEDURE IF EXISTS add_table_image_metadata ;;
CREATE PROCEDURE add_table_image_metadata()
BEGIN

    create table if not exists image_metadata
    (
        image_meta_data_id integer not null,
        checksum varchar(64) ,
        virtual_size varchar(64) ,
        size varchar(64) ,
        foreign key (image_meta_data_id) references resource_status(id) ON DELETE CASCADE ON UPDATE NO ACTION,
        primary key (image_meta_data_id));


END ;;
#
#***********
#* add operation field to resource_status table
#***********

DROP PROCEDURE IF EXISTS add_operation_in_resource_status ;;
CREATE PROCEDURE add_operation_in_resource_status()
BEGIN

    IF NOT EXISTS( (SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE()
            AND COLUMN_NAME='operation' AND TABLE_NAME='resource_status') ) THEN
            ALTER TABLE resource_status ADD operation varchar(64) DEFAULT '';
    END IF;

END ;;
CALL add_operation_in_resource_status() ;;
CALL add_table_image_metadata();;
DELIMITER ;