#!/usr/bin/env python3

# reads infiltration from PIHM (*.infil) and creates a Cycles reinit file

import csv
import subprocess
import sys

def main():

    # TODO: this is the correct patch id for Gel-Aliab demo, but should
    # be found dynamically in the future
    patch_id = 282 

    # TODO: parameter? Glob?
    pihm_infil_fname = "PIHM-state/ga.infil"

    # TODO: parameter?
    cycles_reinit_fname = "Cycles-%s.REINIT" %(sys.argv[1])

    # PIHM state comes in as a tarball
    subprocess.call('tar xzf PIHM-state.tar.gz', shell=True)
    
    outf = open(cycles_reinit_fname, 'w')
    outf.write('ROT_YEAR\tDOY\tVARIABLE\tVALUE\n')

    inf = open(pihm_infil_fname, 'r')
    data = csv.reader(inf, delimiter='\t')
    day = 1
    for row in data:
        # TODO: handle years/days 
        # TODO: are the units correct?
        infiltration = float(row[patch_id])
        outf.write('1\t%d\tINFILTRATION\t%8.4f\n' %(day, infiltration))
        day += 1

    inf.close()
    outf.close()


main()

