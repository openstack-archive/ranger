USE orm_ims_db;

DELIMITER ;;

DROP PROCEDURE IF EXISTS add_region_properies;
CREATE PROCEDURE add_region_properies()
BEGIN

        -- add a column safely
        IF NOT EXISTS( (SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE()
                        AND COLUMN_NAME='checksum' AND TABLE_NAME='image_region') ) THEN
                ALTER TABLE image_region ADD checksum varchar(64) NOT NULL;
        END IF;

        IF NOT EXISTS( (SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE()
                        AND COLUMN_NAME='size' AND TABLE_NAME='image_region') ) THEN
                ALTER TABLE image_region ADD size varchar(64) NOT NULL;
        END IF;

        IF NOT EXISTS( (SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE()
                        AND COLUMN_NAME='virtual_size' AND TABLE_NAME='image_region') ) THEN
                ALTER TABLE image_region ADD virtual_size varchar(64) NOT NULL;
        END IF;
END ;;

CALL add_region_properies() ;;

DELIMITER ;

