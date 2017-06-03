#!/bin/bash

echo Creating database: orm_rms_db
echo Creating tables: rms_groups, region, group_region, region_end_point, region_meta_data

mysql -uroot -pstack < ../db_scripts/create_db.sql

echo Done !







