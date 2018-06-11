#!/bin/bash

set -e

POINT=$1

# set up the input directory
tar xzf Cycles-${POINT}-base.tar.gz 
mv Cycles-${POINT}-base input

# TODO: determine target names
mv Cycles-${POINT}.weather input/SS_x3085y0535_ldas.weather
mv Cycles-${POINT}.REINIT input/SS_fswc.REINIT

chmod 755 Cycles
#./Cycles $POINT
./Cycles SS_sorghum_ry17

mv output Cycles-${POINT}-results
tar czf Cycles-${POINT}-results.tar.gz Cycles-${POINT}-results

