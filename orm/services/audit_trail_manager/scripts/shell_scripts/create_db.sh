#!/bin/bash
source ~/devstack/local.conf &> /dev/null
echo Creating database: orm_audit
echo Creating table: transactions
mysql -uroot -p$MYSQL_PASSWORD < ../db_scripts/create_db.sql &> /dev/null
echo Done !
















