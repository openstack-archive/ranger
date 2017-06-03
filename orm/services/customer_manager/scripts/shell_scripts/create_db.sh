#!/bin/bash

echo Creating database: orm_cms_db

mysql -uroot -pstack < ../db_scripts/aic_orm_cms_create_db.sql

echo Done !
