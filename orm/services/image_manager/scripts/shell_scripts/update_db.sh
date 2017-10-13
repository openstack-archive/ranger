#!/bin/bash
echo Creating database: orm_ims_db
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/update_db.sql
echo Done !
