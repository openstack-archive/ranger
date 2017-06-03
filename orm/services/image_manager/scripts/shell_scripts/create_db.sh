#!/bin/bash

echo Creating database: orm_ims_db

mysql -uroot -pstack < ../db_scripts/create_db.sql

echo Done !
