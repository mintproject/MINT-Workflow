#!/bin/bash

set -e

# TODO: generate a Cycles REINIT file from the PIHM data

POINT=$1

wget -nv -O Cycles-${POINT}.REINIT http://workflow.isi.edu/MINT/MINT-Workflow/v2/Cycles.REINIT


