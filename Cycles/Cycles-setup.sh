#!/bin/bash

set -e

# This should be replaced by an automatic setup of the model

POINT=$1

wget -nv -O Cycles-base.tar.gz http://workflow.isi.edu/MINT/MINT-Workflow/v2/Cycles-base.tar.gz

# make it unique
tar xzf Cycles-base.tar.gz
mv Cycles-base Cycles-${POINT}-base
tar czf Cycles-${POINT}-base.tar.gz Cycles-${POINT}-base

