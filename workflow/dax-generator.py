#!/usr/bin/env python

import glob
import math
import os
import re
import sys

from Pegasus.DAX3 import *

top_dir = os.getcwd()

dax = ADAG('MINT')

# email notifications
dax.invoke('all', top_dir + '/workflow/generate-graphs.sh')

inputs = []

# Run config
run_config = File('mint_run.config')
run_config.addPFN(PFN('file://' + top_dir + '/mint_run.config', 'local'))
dax.addFile(run_config)

# LDAS-data-find binary
ldas_data_find = File('LDAS-data-find')
ldas_data_find.addPFN(PFN('file://' + top_dir + '/weather/LDAS-data-find', 'local'))
dax.addFile(ldas_data_find)

# weather data
ldas = Job('LDAS-data-find')
ldas.uses(run_config, link=Link.INPUT)
weather_data = File('weather.tar.gz')
ldas.uses(weather_data, link=Link.OUTPUT, transfer=False)
dax.addJob(ldas)

# PIHM-data-find binary
pihm_data_find = File('PIHM-data-find')
pihm_data_find.addPFN(PFN('file://' + top_dir + '/PIHM/PIHM-data-find', 'local'))
dax.addFile(pihm_data_find)

# FLDAS-to-PIHM.R binary
fldas_to_pihm = File('FLDAS-to-PIHM.R')
fldas_to_pihm.addPFN(PFN('file://' + top_dir + '/PIHM/FLDAS-to-PIHM.R', 'local'))
dax.addFile(fldas_to_pihm)

# transformation: LDAS->PIHM
ldas_pihm = Job('LDAS-PIHM-transformation.sh')
ldas_pihm.uses(run_config, link=Link.INPUT)
ldas_pihm.uses(fldas_to_pihm, link=Link.INPUT)
ldas_pihm.uses(pihm_data_find, link=Link.INPUT)
ldas_pihm.uses(weather_data, link=Link.INPUT)
pihm_forcing = File('pihm.forc')
ldas_pihm.uses(pihm_forcing, link=Link.OUTPUT, transfer=True)
# positional arguments to match WINGS
ldas_pihm.addArguments(run_config, fldas_to_pihm, pihm_data_find, weather_data)
dax.addJob(ldas_pihm)
dax.depends(parent=ldas, child=ldas_pihm)

# PIHM
pihm = Job('PIHM-wrapper.py')
pihm.uses(run_config, link=Link.INPUT)
pihm.uses(pihm_data_find, link=Link.INPUT)
pihm.uses(pihm_forcing, link=Link.INPUT)
# output is a tarball of the state
pihm_state = File('PIHM-state.tar.gz')
pihm.uses(pihm_state, link=Link.OUTPUT, transfer=True)
dax.addJob(pihm)
dax.depends(parent=ldas_pihm, child=pihm)

# create a job to execute cycles_to_crop transformation - this comes after cycles!
cycles_to_crop = Job('Cycles-to-crop.py')
crops_output =  File('yieldelast.csv')
cycles_to_crop.uses(crops_output, link=Link.OUTPUT, transfer=True)
dax.addJob(cycles_to_crop)

# we need two cycles run - one base line and one 10% increase in fertilization
for point in ['baseline', '10_percent_inc']:

    # cycles config
    cycles_config = File('mint_cycles-' + str(point) + '.config')
    cycles_config.addPFN(PFN('file://' + top_dir + '/Cycles/mint_cycles.config', 'local'))
    dax.addFile(cycles_config)

    # transformation: LDAS->Cycles
    ldas_cycles = Job('FLDAS-Cycles-transformation.py')
    ldas_cycles.uses(run_config, link=Link.INPUT)
    ldas_cycles.uses(cycles_config, link=Link.INPUT)
    ldas_cycles.uses(weather_data, link=Link.INPUT)
    cycles_weather = File('Cycles-%s.weather' %(point))
    ldas_cycles.uses(cycles_weather, link=Link.OUTPUT, transfer=True)
    ldas_cycles.addArguments(point)
    dax.addJob(ldas_cycles)
    dax.depends(parent=ldas, child=ldas_cycles)
    
    # transformation: PIHM->Cycles
    pihm_cycles = Job('PIHM-Cycles-transformation.py')
    pihm_cycles.uses(run_config, link=Link.INPUT)
    pihm_cycles.uses(pihm_state, link=Link.INPUT)
    cycles_reinit = File('Cycles-%s.REINIT' %(point))
    pihm_cycles.uses(cycles_reinit, link=Link.OUTPUT, transfer=True)
    pihm_cycles.addArguments(point)
    dax.addJob(pihm_cycles)
    dax.depends(parent=pihm, child=pihm_cycles)

    # create a job to execute Cycles
    cycles = Job('Cycles-wrapper.sh')
    cycles.uses(cycles_weather, link=Link.INPUT)
    cycles.uses(cycles_reinit, link=Link.INPUT)
    cycles_outputs = File('Cycles-%s-results.tar.gz' %(point))
    cycles.uses(cycles_outputs, link=Link.OUTPUT, transfer=True)
    cycles.addArguments(point)
    dax.addJob(cycles)
    dax.depends(parent=ldas_cycles, child=cycles)
    dax.depends(parent=pihm_cycles, child=cycles)

    # update cycles_to_crop job
    dax.depends(parent=cycles, child=cycles_to_crop)
    cycles_to_crop.uses(cycles_outputs, link=Link.INPUT)
    cycles_to_crop.addArguments(cycles_outputs)

# economic model gams file
land_use = File('land-use.gams')
land_use.addPFN(PFN('file://' + top_dir + '/economic/land-use.gams', 'local'))
dax.addFile(land_use)

# create a job to execute economic model
economic = Job('economic-wrapper.sh')
economic.uses(land_use, link=Link.INPUT)
economic.uses(crops_output, link=Link.INPUT)
#economic.uses(economic_outputs, link=Link.OUTPUT, transfer=True)
dax.addJob(economic)
dax.depends(parent=cycles_to_crop, child=economic)

# Write the DAX
f = open('workflow/generated/dax.xml', 'w')
dax.writeXML(f)
f.close()

