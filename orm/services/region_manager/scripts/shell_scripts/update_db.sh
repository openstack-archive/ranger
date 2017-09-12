#!/bin/bash
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/update_db.sql
echo Done !
