#!/bin/bash
echo Creating database: orm
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/db_create.sql &> /dev/null
echo Done!
