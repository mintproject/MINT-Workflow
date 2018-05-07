#!/bin/bash

set -e

SITE_NAME=$1

touch Cycles-${SITE_NAME}-results.tar.gz

# Cycles wants input files under an input/ dir
tar xzf Cycles-${SITE_NAME}-inputs.tar.gz 

echo
echo
ls -l
echo
echo

chmod 755 Cycles
./Cycles $SITE_NAME

#echo
#for FILE in `ls output/$SITE_NAME/`; do
#    echo "... moving output to ${SITE_NAME}__${FILE}"
#    mv output/$SITE_NAME/$FILE ${SITE_NAME}__${FILE}
#done

tar czf Cycles-${SITE_NAME}-results.tar.gz output

