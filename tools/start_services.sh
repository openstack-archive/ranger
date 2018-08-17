#!/bin/sh

set -e

echo "Starting the audit service"

nohup orm-audit > /dev/null 2>&1&

echo "Starting the uuidgen service"

nohup orm-uuidgen > /dev/null 2>&1&

echo "Starting the rds service"

nohup orm-rds > /dev/null 2>&1&

echo "Starting the rms service"

nohup orm-rms > /dev/null 2>&1&

echo "Starting the cms service"

nohup orm-cms > /dev/null 2>&1&

echo "Starting the ims service"

nohup orm-ims > /dev/null 2>&1&


echo "Starting the fms service"

nohup orm-fms > /dev/null 2>&1&


