#!/bin/bash
echo Creating database: orm_fms
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/ranger_fms_create_db.sql &> /dev/null
echo Done!
