use orm_rms_db;

# This SQL script is used for upgrading ORM_RMS_DB.

# PROCEDURE Update_Region_Status()
# The following defines and then calls a stored procedure that updates and replaces
# region_status from 'commissioning' to 'building'.

DROP PROCEDURE IF EXISTS Rename_group_table;

DELIMITER $$

CREATE PROCEDURE Rename_group_table()
BEGIN
    DECLARE _table_exist INT;
-- Check if table rms_groups exists, if not then need to rename 'group' table
    SET _table_exist = (  SELECT COUNT(*)
                          FROM information_schema.tables
                          WHERE table_schema = 'orm_rms_db'
                          AND table_name = 'rms_groups');
    IF _table_exist > 0 THEN
        RENAME TABLE `group` TO rms_groups;
    END IF;
END $$
DELIMITER ;

CALL Rename_group_table;

DROP PROCEDURE IF EXISTS Update_Region_Status;

DELIMITER $$

CREATE PROCEDURE Update_Region_Status()
BEGIN
--  Add a new enum value 'building' to the end of the enum list
    ALTER TABLE region CHANGE region_status
        region_status ENUM('commissioning','functional','maintenance','down','building');

-- Update the table to change the old to the new value
    UPDATE region set region_status = 'building' where region_status = 'commissioning';

-- after changing to the new values, safe to remove the old "commissioning" value from the ENUM list
    ALTER TABLE region CHANGE region_status
        region_status ENUM('building','functional','maintenance','down');

END $$
DELIMITER ;

CALL Update_Region_Status;

# PROCEDURE Upgrade_Region_Meta_Data;
# The following defines and then calls a stored procedure that does the following for the region_meta_data table:
#     1. Check if a column named 'id' not exist, if exist the db already up to date.
#     2. Remove old fk, pk and unique constraint.
#     3. Add a new column to the region_meta_data table named 'id' set it as auto increment and primary key.
#     4. Add a new constraint to define unique values.

DROP PROCEDURE IF EXISTS Upgrade_Region_Meta_Data;

DELIMITER $$
CREATE PROCEDURE Upgrade_Region_Meta_Data()
BEGIN
    DECLARE _count INT;
    SET _count = (  SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE   TABLE_NAME = 'region_meta_data' AND
                            COLUMN_NAME = 'id');
    IF _count = 0 THEN
        ALTER TABLE region_meta_data DROP FOREIGN KEY region_meta_data_ibfk_1;
        ALTER TABLE region_meta_data DROP PRIMARY KEY;
        ALTER TABLE region_meta_data DROP index region_meta_data_key;

        ALTER TABLE region_meta_data ADD COLUMN id int NOT NULL AUTO_INCREMENT primary key FIRST;
        ALTER TABLE region_meta_data ADD CONSTRAINT region_meta_data_key_value UNIQUE (region_id, meta_data_key, meta_data_value);
    END IF;
END $$
DELIMITER ;

CALL Upgrade_Region_Meta_Data;


# PROCEDURE Upgrade_Region_and_Rms_Groups_column_key;
# The following defines and then calls a stored procedure that does the following for the region and rms_groups tables:
#     1. region_id and name column  as primary key and add name column a unique constraint  in region table
#     2. group_id column  as primary key and add name column a unique constrain in rms_group table
#     3. Add a new columns to the region table named 'created_at' and 'modified_at'.

DROP PROCEDURE IF EXISTS Upgrade_Region_and_Rms_Groups_column_key;

DELIMITER $$
CREATE PROCEDURE Upgrade_Region_and_Rms_Groups_column_key()
BEGIN
    DECLARE _count INT;
    SET _count = (  SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE   TABLE_NAME = 'region' AND
                            COLUMN_NAME in ('region_id', 'name')
                            AND COLUMN_KEY= 'PRI');
    IF _count = 0 THEN
        UPDATE region SET name = region_id;
        ALTER TABLE region DROP PRIMARY KEY, ADD PRIMARY KEY(id,region_id,name);
        ALTER TABLE region add unique region_namex (name);
    END IF;

    SET _count = (  SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE   TABLE_NAME = 'region' AND
                            COLUMN_NAME in('created', 'modified'));
    IF _count = 0 THEN
        ALTER TABLE region ADD `created` TIMESTAMP NOT NULL DEFAULT 0;
        UPDATE region SET created = CURRENT_TIMESTAMP where created = 0;
        ALTER TABLE region ADD `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
    END IF;

    SET _count = (  SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE   TABLE_NAME = 'rms_groups' AND
                            COLUMN_NAME = 'group_id' AND
                            COLUMN_KEY= 'PRI');
    IF _count = 0 THEN
        UPDATE rms_groups SET name = group_id;
        ALTER TABLE rms_groups DROP PRIMARY KEY, ADD PRIMARY KEY(id,group_id);
        ALTER TABLE rms_groups add unique grp_namex (name);
    END IF;

    SET _count = (  SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE   TABLE_NAME = 'rms_groups' AND
                           COLUMN_NAME in('created', 'modified'));

    IF _count = 0 THEN
	    ALTER TABLE rms_groups ADD `created` TIMESTAMP NOT NULL DEFAULT 0;
	    UPDATE rms_groups SET created = CURRENT_TIMESTAMP where created = 0;
	    ALTER TABLE rms_groups ADD `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
    END IF;
END $$
DELIMITER ;

CALL Upgrade_Region_and_Rms_Groups_column_key;

