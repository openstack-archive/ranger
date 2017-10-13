USE orm_cms_db;
DROP PROCEDURE IF EXISTS MoveKeyToQuota;
DELIMITER ;;
CREATE PROCEDURE `MoveKeyToQuota`(p_field_key varchar(64), p_quota varchar(64))
BEGIN
  DECLARE bDone INT;

  # quota_field_detail fields
  DECLARE v_quota_field_id INT;    -- or approriate type
  DECLARE v_quota_field_quota_id INT;
  DECLARE v_quota_field_field_key VARCHAR(64);
  DECLARE v_quota_field_field_value VARCHAR(64);

  # quota fields
  DECLARE v_quota_id INT;    -- or approriate type
  DECLARE v_quota_customer_id INT;
  DECLARE v_quota_region_id INT;
  DECLARE v_quota_quota_type VARCHAR(64);


  DECLARE security_elements CURSOR FOR SELECT id, quota_id, field_key, field_value FROM quota_field_detail where field_key = p_field_key;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET bDone = 1;

  START TRANSACTION;

  OPEN security_elements;

  SET bDone = 0;

  label_begin_loop: LOOP
    FETCH security_elements INTO v_quota_field_id, v_quota_field_quota_id, v_quota_field_field_key, v_quota_field_field_value;
    IF bDone = 1 THEN
      LEAVE label_begin_loop;
    END IF;

    BEGIN
        DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;
        SELECT v_quota_field_id, v_quota_field_quota_id, v_quota_field_field_key, v_quota_field_field_value;

        # get the first quota for this quota_field
        SELECT id, customer_id, region_id, quota_type INTO v_quota_id, v_quota_customer_id, v_quota_region_id, v_quota_quota_type FROM quota WHERE id = v_quota_field_quota_id LIMIT 1;
        # disply the quata
        SELECT v_quota_id, v_quota_customer_id, v_quota_region_id, v_quota_quota_type;

        SET v_quota_id = 0;

        SELECT id, customer_id, region_id, quota_type INTO v_quota_id, v_quota_customer_id, v_quota_region_id, v_quota_quota_type FROM quota
             WHERE customer_id = v_quota_customer_id AND region_id = v_quota_region_id AND quota_type = p_quota LIMIT 1;

        SELECT v_quota_id, v_quota_customer_id, v_quota_region_id, v_quota_quota_type;

        IF  v_quota_id = 0 THEN
          INSERT INTO `quota`
          (`customer_id`, `region_id`, `quota_type`)
          VALUES
          (v_quota_customer_id, v_quota_region_id, p_quota);

          SELECT last_insert_id() INTO v_quota_id;
              SELECT v_quota_id;
        END IF;

        UPDATE quota_field_detail SET quota_id = v_quota_id WHERE id = v_quota_field_id;
    END;
  END LOOP label_begin_loop;

  CLOSE security_elements;

  COMMIT;
END;;
DELIMITER ;

CALL MoveKeyToQuota('security_groups', 'network');
CALL MoveKeyToQuota('security_group_rules', 'network');
SELECT "LIST OF ALL Security Items" as "";
SELECT "==========================" as "";
SELECT q.*, qfd.* FROM quota_field_detail qfd
	left join quota q on (q.id = qfd.quota_id) where qfd.field_key like "security%";

DELIMITER ;;

DROP PROCEDURE IF EXISTS add_regoion_type ;;
CREATE PROCEDURE add_regoion_type()
BEGIN

	-- add a column safely
	IF NOT EXISTS( (SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE()
			AND COLUMN_NAME='type' AND TABLE_NAME='region') ) THEN
		ALTER TABLE region ADD type varchar(32) NOT NULL DEFAULT 'single';
  ELSE
    UPDATE region set type = "single" where id = -1;
	END IF;

	IF NOT EXISTS( SELECT * FROM region WHERE id=-1) THEN
  	insert ignore into region(id,name,type) values(-1, "DEFAULT", "single");
	END IF;

END ;;

CALL add_regoion_type() ;;

DELIMITER ;

