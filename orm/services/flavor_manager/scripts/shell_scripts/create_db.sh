#!/bin/bash

echo Creating database: orm_rds
echo Creating table: resource_status

mysql -uroot -pstack < ../db_scripts/ranger_fms_create_db.sql

echo Done !
