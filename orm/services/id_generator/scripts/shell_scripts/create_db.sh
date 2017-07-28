#!/bin/bash

echo Creating database: orm_rds
echo Creating table: resource_status

mysql -uroot -pstack < ../db_scripts/db_create.sql

echo Done !
