#!/bin/bash

set -e

TOP_DIR=`dirname $0`
TOP_DIR=`cd $TOP_DIR/.. && pwd`
cd $TOP_DIR

export RUN_ID=cycles-`date +'%s'`
export RUN_DIR=/local-scratch/$USER/workflow/$RUN_ID

mkdir -p $RUN_DIR

# create a site catalog from the template
envsubst < workflow/sites.template.xml > workflow/generated/sites.xml

# generate a transformation catalog
./workflow/tc-generator.sh >workflow/generated/tc.data

# generate the workflow
./workflow/dax-generator.py

# plan and submit
pegasus-plan \
    --conf workflow/pegasus.conf \
    --sites condor_pool \
    --output-site local \
    --cleanup inplace \
    --relative-dir $RUN_ID \
    --dir $RUN_DIR \
    --dax workflow/generated/dax.xml \
    --submit



