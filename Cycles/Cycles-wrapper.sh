#!/bin/bash

set -e

POINT=$1

# set up the input directory
wget -nv -O Cycles-base.tar.gz http://workflow.isi.edu/MINT/MINT-Workflow/v2/Cycles-base.tar.gz
tar xzf Cycles-base.tar.gz
mv Cycles-base input

# only run 2017 for now
perl -p -i -e 's/SIMULATION_START_YEAR.*/SIMULATION_START_YEAR   2017/' input/SS_sorghum_ry17.ctrl
perl -p -i -e 's/SIMULATION_END_YEAR.*/SIMULATION_END_YEAR   2017/' input/SS_sorghum_ry17.ctrl
perl -p -i -e 's/ROTATION_SIZE.*/ROTATION_SIZE    1/' input/SS_sorghum_ry17.ctrl

# TODO: determine target names
mv Cycles-${POINT}.weather input/SS_x3085y0535_ldas.weather
mv Cycles-${POINT}.REINIT input/SS_fswc.REINIT

chmod 755 Cycles
#./Cycles $POINT
./Cycles SS_sorghum_ry17

mv output Cycles-${POINT}-results
tar czf Cycles-${POINT}-results.tar.gz Cycles-${POINT}-results

