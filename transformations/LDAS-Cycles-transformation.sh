#!/bin/bash

# TODO: implement weather->cycles forcing transform

POINT=$1

wget -nv -O Cycles-${POINT}.weather http://workflow.isi.edu/MINT/MINT-Workflow/v2/Cycles.weather

