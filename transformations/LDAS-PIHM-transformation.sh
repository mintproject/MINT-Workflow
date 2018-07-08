#!/bin/bash

set -e

# we need FLDAS_NOAH01_A_EA_D.001/
tar xzf $4

# as well as PIHM-base
chmod 755 $3
./$3
tar xzf PIHM_base.tar.gz

# figure out the start/end years
START_YEAR=`grep ^start_year mint_run.config | sed 's/.*= *//'`
END_YEAR=`grep ^end_year mint_run.config | sed 's/.*= *//'`

# now do the transform - output is pihm.forc
# TODO: parameterize 
chmod 755 $2 
./$2 $START_YEAR $END_YEAR $5

