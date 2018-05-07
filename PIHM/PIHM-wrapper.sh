#!/bin/bash

set -e

touch PIHM-state.tar.gz

PROJECT_NAME=`cat projectName.txt`
echo "Setting up PIHM to run project '$PROJECT_NAME'..."

echo
echo
/usr/bin/pihm 2>&1
echo
echo

tar czf PIHM-state.tar.gz ${PROJECT_NAME}.*

