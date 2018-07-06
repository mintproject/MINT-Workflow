#!/usr/bin/env python3

# reads infiltration from PIHM (*.infil) and creates a Cycles reinit file

import csv
import subprocess
import sys

def main():

    # get the general configuration from the global mint_run.config
    fp = open('mint_run.config', 'r')
    config_string = '[DEFAULT]\n' + fp.read()
    fp.close()
    run_config = configparser.ConfigParser()
    run_config.read_string(config_string)

    start_time = run_config.get('DEFAULT', 'start_time')
    start_dt = parser.parse(start_time)
    end_time = run_config.get('DEFAULT', 'end_time')
    end_dt = parser.parse(end_time)

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
    dt = start_dt
    for row in data:

        year = dt.year - start_dt.year + 1
        day_of_year  = int(dt.strftime('%j'))

        infiltration = float(row[patch_id]) * 1000 # m to mm
        outf.write('%d\t%d\tINFILTRATION\t%8.4f\n' \
                   %(year, day_of_year, infiltration))

        # move to the next day
        dt = dt + datetime.timedelta(days = 1)

    inf.close()
    outf.close()


main()

