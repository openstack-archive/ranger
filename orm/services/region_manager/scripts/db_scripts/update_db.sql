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
-- Check if table 'group' exists even if no rows in table
    SET _table_exist = (  SELECT COUNT(*)
                          FROM information_schema.tables
                          WHERE table_schema = 'orm_rms_db'
                          AND table_name like 'group');
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

