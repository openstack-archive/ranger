#!/bin/bash
echo Updating database: orm_audit
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/update_db.sql &> /dev/null
echo Done!
