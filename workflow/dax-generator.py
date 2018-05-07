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
dax.invoke('all', '/usr/share/pegasus/notification/email')

inputs = []

# need the real Cycles binary
cycles_binary = File('Cycles')
cycles_binary.addPFN(PFN('file://' + top_dir + '/Cycles/Cycles', 'local'))
dax.addFile(cycles_binary)

# Cycles inputs (set of files) - temporary until we have a transform
for fname in glob.glob('Cycles/input/*'):
    # do not include inputs/ part in the lfn
    fname = re.sub('Cycles/input/', '', fname)
    f = File(fname)
    f.addPFN(PFN('file://' + top_dir + '/Cycles/input/' + fname, 'local'))
    dax.addFile(f)
    inputs.append(f)

# create a job to execute PIHM
pihm_job = Job('PIHM-wrapper.sh')
# sample input set
for fname in glob.glob('PIHM/input/*'):
    fname = re.sub('PIHM/input/', '', fname)
    f = File(fname)
    f.addPFN(PFN('file://' + top_dir + '/PIHM/input/' + fname, 'local'))
    dax.addFile(f)
    pihm_job.uses(f, link=Link.INPUT)
# output is a tarball of the state
pihm_state = File('PIHM-state.tar.gz')
pihm_job.uses(pihm_state, link=Link.OUTPUT, transfer=True)
dax.addJob(pihm_job)

for point in ['ContinuousCorn', 'CornSilageSoyWheat', 'CornSoyWheatPasture']:

    # data transform PIHM->Cycles
    # this is just a placeholder for a real transform
    prepare_job = Job('Cycles-prepare-inputs.sh')
    prepare_job.addArguments(point)
    prepare_job.uses(pihm_state, link=Link.INPUT)
    for f in inputs:
        prepare_job.uses(f, link=Link.INPUT)
    cycles_inputs = File('Cycles-%s-inputs.tar.gz' %(point))
    prepare_job.uses(cycles_inputs, link=Link.OUTPUT, transfer=True)
    dax.addJob(prepare_job)
    dax.depends(parent=pihm_job, child=prepare_job)

    # create a job to execute Cycles
    cycles_job = Job('Cycles-wrapper.sh')
    cycles_job.addArguments(point)
    cycles_job.uses(cycles_binary, link=Link.INPUT)
    cycles_job.uses(cycles_inputs, link=Link.INPUT)
    cycles_outputs = File('Cycles-%s-results.tar.gz' %(point))
    cycles_job.uses(cycles_outputs, link=Link.OUTPUT, transfer=True)
    dax.addJob(cycles_job)
    dax.depends(parent=prepare_job, child=cycles_job)

# Write the DAX
f = open('workflow/dax.xml', 'w')
dax.writeXML(f)
f.close()

