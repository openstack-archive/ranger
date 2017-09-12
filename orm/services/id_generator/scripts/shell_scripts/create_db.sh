#!/bin/bash
echo Creating database: orm_id
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/db_create.sql &> /dev/null
echo Done!
