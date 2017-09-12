#!/bin/bash
source ~/devstack/local.conf &> /dev/null
echo Creating database: orm_id
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/db_create.sql &> /dev/null
echo Done !
