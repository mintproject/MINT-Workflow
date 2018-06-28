#!/bin/bash

set -e

# It is unclear if we need a LDAS job - this will depend on if getting the
# LDAS data is mostly a download or a more complex query

chmod 755 LDAS-data-find
./LDAS-data-find
tar czf weather.tar.gz FLDAS_NOAH01_A_EA_D.001



