#!/bin/bash
echo Updating database: orm_fms
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/ranger_fms_update_db.sql &> /dev/null
echo Done!
