#!/bin/bash
echo Updating database: orm_cms_db
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/ranger_cms_update_db.sql &> /dev/null
echo Done!
