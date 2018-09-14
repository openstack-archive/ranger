#!/bin/sh

set -e

echo "Starting the audit service"

nohup ranger-audit > /dev/null 2>&1&

echo "Starting the uuidgen service"

nohup ranger-uuidgen > /dev/null 2>&1&

echo "Starting the rds service"

nohup ranger-rds > /dev/null 2>&1&

echo "Starting the rms service"

nohup ranger-rms > /dev/null 2>&1&

echo "Starting the cms service"

nohup ranger-cms > /dev/null 2>&1&

echo "Starting the ims service"

nohup ranger-ims > /dev/null 2>&1&


echo "Starting the fms service"

nohup ranger-fms > /dev/null 2>&1&


