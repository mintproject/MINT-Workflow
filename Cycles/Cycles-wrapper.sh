#!/bin/bash

set -e

SCENARIO=$1

# set up the input directory
wget -nv -O Cycles-base.tar.gz http://workflow.isi.edu/MINT/MINT-Workflow/v2/Cycles-base.tar.gz
tar xzf Cycles-base.tar.gz
mv Cycles-base input

# only run 2017 for now
perl -p -i -e 's/SIMULATION_START_YEAR.*/SIMULATION_START_YEAR   2017/' input/SS_sorghum.ctrl
perl -p -i -e 's/SIMULATION_END_YEAR.*/SIMULATION_END_YEAR   2017/' input/SS_sorghum.ctrl
perl -p -i -e 's/ROTATION_SIZE.*/ROTATION_SIZE    1/' input/SS_sorghum.ctrl

if [ "x$SCENARIO" = "x10_percent_inc" ]; then
    perl -p -i -e 's/^MASS.*/MASS                110/' input/SS_sorghum.operation
fi

# TODO: determine target names
mv Cycles-${SCENARIO}.weather input/SS_x3085y0535_ldas.weather
mv Cycles-${SCENARIO}.REINIT input/SS_fswc.REINIT

Cycles SS_sorghum

mv output Cycles-${SCENARIO}-results
tar czf Cycles-${SCENARIO}-results.tar.gz Cycles-${SCENARIO}-results

