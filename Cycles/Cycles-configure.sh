#!/bin/bash

#set -e

SITE_NAME=$1

touch Cycles-${SITE_NAME}-inputs.tar.gz

echo
echo
ls -l 
echo
echo

# cycles wants an "input" directory
mkdir -p input
for FILE in `find . -maxdepth 1 -type f | grep -v condor | grep -v pegasus`; do
    echo "Putting '$FILE' in to the input/ directory..."
    mv $FILE input/
done

tar czf Cycles-${SITE_NAME}-inputs.tar.gz input

