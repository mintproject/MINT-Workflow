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

# weather data
ldas = Job('LDAS.sh')
weather_data = File('weather.data')
ldas.uses(weather_data, link=Link.OUTPUT, transfer=False)
dax.addJob(ldas)

# configure PIHM
pihm_configure = Job('PIHM-configure.sh')
pihm_config = File('PIHM-config.tar.gz')
pihm_configure.uses(pihm_config, link=Link.OUTPUT, transfer=False)
dax.addJob(pihm_configure)

# transformation: LDAS->PIHM
ldas_pihm = Job('LDAS-PIHM-transformation.sh')
ldas_pihm.uses(weather_data, link=Link.INPUT)
pihm_forcing = File('pihm.forc')
ldas_pihm.uses(pihm_forcing, link=Link.OUTPUT, transfer=False)
dax.addJob(ldas_pihm)
dax.depends(parent=ldas, child=ldas_pihm)
dax.depends(parent=pihm_configure, child=ldas_pihm)

# PIHM
pihm = Job('PIHM-wrapper.sh')
pihm.uses(pihm_config, link=Link.INPUT)
pihm.uses(pihm_forcing, link=Link.INPUT)
# output is a tarball of the state
pihm_state = File('PIHM-state.tar.gz')
pihm.uses(pihm_state, link=Link.OUTPUT, transfer=True)
dax.addJob(pihm)
dax.depends(parent=pihm_configure, child=pihm)
dax.depends(parent=ldas_pihm, child=pihm)
   
# need the real Cycles binary - will probably be a Docker image in the future
cycles_binary = File('Cycles')
cycles_binary.addPFN(PFN('file://' + top_dir + '/Cycles/Cycles', 'local'))
dax.addFile(cycles_binary)

# fake points for now - we only have one real one
for point in ['one', 'two', 'three']:

    # configure Cycles
    cycles_configure = Job('Cycles-configure.sh')
    cycles_config = File('Cycles-config.tar.gz')
    cycles_configure.uses(cycles_config, link=Link.OUTPUT, transfer=False)
    dax.addJob(cycles_configure)
    dax.depends(parent=pihm, child=cycles_configure)
    
    # transformation: LDAS->Cycles
    ldas_cycles = Job('LDAS-Cycles-transformation.sh')
    ldas_cycles.uses(weather_data, link=Link.INPUT)
    cycles_forcing = File('cycles-%s.forcing' %(point))
    ldas_cycles.uses(cycles_forcing, link=Link.OUTPUT, transfer=False)
    dax.addJob(ldas_cycles)
    dax.depends(parent=cycles_configure, child=ldas_cycles)
    dax.depends(parent=ldas, child=ldas_cycles)
    
    # transformation: PIHM->Cycles
    pihm_cycles = Job('PIHM-Cycles-transformation.sh')
    pihm_cycles.uses(pihm_state, link=Link.INPUT)
    pihm_cycles.uses(cycles_config, link=Link.INPUT)
    cycles_reinit = File('cycles-%s.REINIT' %(point))
    pihm_cycles.uses(cycles_reinit, link=Link.OUTPUT, transfer=False)
    dax.addJob(pihm_cycles)
    dax.depends(parent=cycles_configure, child=pihm_cycles)
    dax.depends(parent=pihm, child=pihm_cycles)

    # create a job to execute Cycles
    cycles = Job('Cycles-wrapper.sh')
    cycles.addArguments(point)
    cycles.uses(cycles_binary, link=Link.INPUT)
    cycles.uses(cycles_config, link=Link.INPUT)
    cycles.uses(cycles_forcing, link=Link.INPUT)
    cycles.uses(cycles_reinit, link=Link.INPUT)
    cycles_outputs = File('Cycles-%s-results.tar.gz' %(point))
    cycles.uses(cycles_outputs, link=Link.OUTPUT, transfer=True)
    dax.addJob(cycles)
    dax.depends(parent=cycles_configure, child=cycles)
    dax.depends(parent=ldas_cycles, child=cycles)
    dax.depends(parent=pihm_cycles, child=cycles)

# Write the DAX
f = open('workflow/generated/dax.xml', 'w')
dax.writeXML(f)
f.close()

