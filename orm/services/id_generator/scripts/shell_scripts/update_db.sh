#!/bin/bash
echo Update database: orm_id
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/update_db.sql &> /dev/null
echo Done!
