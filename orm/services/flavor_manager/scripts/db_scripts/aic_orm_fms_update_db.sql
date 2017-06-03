USE orm_fms_db;

DELIMITER ;;

DROP PROCEDURE IF EXISTS add_regoion_type ;;
CREATE PROCEDURE add_regoion_type()
BEGIN

	-- add a column safely
	IF NOT EXISTS( (SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE()
			AND COLUMN_NAME='region_type' AND TABLE_NAME='flavor_region') ) THEN
		ALTER TABLE flavor_region ADD region_type varchar(32) NOT NULL DEFAULT 'single';
	END IF;

	IF NOT EXISTS( (SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE()
			AND COLUMN_NAME='alias' AND TABLE_NAME='flavor') ) THEN
		ALTER TABLE flavor ADD alias varchar(64) NULL;
	END IF;

END ;;

CALL add_regoion_type() ;;
ALTER TABLE `flavor`  CHANGE COLUMN `name` `name` VARCHAR(250) NOT NULL;;

DELIMITER ;

