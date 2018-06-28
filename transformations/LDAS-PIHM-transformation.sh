#!/bin/bash

set -e

# we need FLDAS_NOAH01_A_EA_D.001/
tar xzf weather.tar.gz

# as well as PIHM-base
chmod 755 PIHM-data-find
./PIHM-data-find
tar xzf PIHM_base.tar.gz

# now do the transform - output is pihm.forc
# TODO: parameterize 
chmod 755 FLDAS-to-PIHM.R
./FLDAS-to-PIHM.R

