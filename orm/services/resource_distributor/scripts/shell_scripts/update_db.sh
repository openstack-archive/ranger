#!/bin/bash
echo Updating database: orm_rds
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/update_db.sql &> /dev/null
echo Done!
