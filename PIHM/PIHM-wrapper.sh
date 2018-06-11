#!/bin/bash

set -e

tar xzf PIHM-base.tar.gz

# detemin the project name
cd PIHM-base
PROJECT_NAME=`ls *.mesh | sed 's;\.mesh;;'`
echo "Setting up PIHM to run project '$PROJECT_NAME'..."
echo "$PROJECT_NAME" >projectName.txt

# copy the forcing data into place
cp ../pihm.forc ${PROJECT_NAME}.forc

echo
echo
/usr/bin/pihm 2>&1
echo
echo

cd ..
mv PIHM-base PIHM-state
tar czf PIHM-state.tar.gz PIHM-state

