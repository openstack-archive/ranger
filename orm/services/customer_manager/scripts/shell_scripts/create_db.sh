#!/bin/bash
echo Creating database: orm_cms_db
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/ranger_cms_create_db.sql &> /dev/null
echo Done!
