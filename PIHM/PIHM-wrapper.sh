#!/bin/bash

set -e

chmod 755 PIHM-data-find
./PIHM-data-find

tar xzf PIHM_base.tar.gz

# only run for 1 year for testing
perl -p -i -e 's/5256000/525600/' PIHM-base/ga.para

# detemin the project name
cd PIHM-base
PROJECT_NAME=`ls *.mesh | sed 's;\.mesh;;'`
echo "Setting up PIHM to run project '$PROJECT_NAME'..."
echo "$PROJECT_NAME" >projectName.txt

# copy the forcing data into place
cp ../pihm.forc ${PROJECT_NAME}.forc

# TODO: TEMP - USE ORIG FORCING DATA
wget -nv -O ${PROJECT_NAME}.forc http://workflow.isi.edu/MINT//MINT-Workflow/v2/PIHM-forcing

echo
echo
/usr/bin/pihm 2>&1
echo
echo

cd ..
mv PIHM-base PIHM-state
tar czf PIHM-state.tar.gz PIHM-state

