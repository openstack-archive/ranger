python /opt/stack/ranger/orm/services/region_manager/csv2db.py  
mysql -uroot -p$MYSQL_PASSWORD < create_customer.sql &> /dev/null
