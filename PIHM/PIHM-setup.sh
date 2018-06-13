#!/bin/bash

set -e

# Set up the PIHM watershed. This is currently a manual process, but
# might become an automatic one in the future. For now, just simulate
# a data catalog download of an already prepared watershed (Gel-Aliab)

wget -nv http://workflow.isi.edu/MINT/MINT-Workflow/v2/PIHM-base.tar.gz

tar xzf PIHM-base.tar.gz

# only run for 1 month for testing
perl -p -i -e 's/5256000/44640/' PIHM-base/ga.para

tar czf PIHM-base.tar.gz PIHM-base

