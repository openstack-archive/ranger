#!/bin/bash

echo Creating database: orm_audit
echo Creating table: transactions

mysql -uroot -pstack < ../db_scripts/create_db.sql

echo Done !
















