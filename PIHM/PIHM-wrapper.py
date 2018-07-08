#!/usr/bin/env python3

import configparser
import glob
import datetime
import os
import subprocess
import sys
import re


def my_cmd(cmd):
    print()
    print(cmd)
    exit_code = subprocess.call(cmd, shell=True)
    if exit_code != 0:
        print('Command failed with exit code %d' %(exit_code))
        sys.exit(1)


def main():

    # get the general configuration from the global mint_run.config
    fp = open(sys.argv[1], 'r')
    config_string = '[DEFAULT]\n' + fp.read()
    fp.close()
    run_config = configparser.ConfigParser()
    run_config.read_string(config_string)

    start_year = run_config.get('DEFAULT', 'start_year')
    end_year = run_config.get('DEFAULT', 'end_year')

    start_date = datetime.date(int(start_year), 1, 1)
    end_date = datetime.date(int(end_year), 12, 31)
    delta = end_date - start_date
    duration_mins = delta.days * 24 * 60

    my_cmd('chmod 755 PIHM-data-find && ./PIHM-data-find')
    
    my_cmd('tar xzf PIHM_base.tar.gz')
    
    # determine project name
    os.chdir('PIHM-base')
    project_name = glob.glob('*.para')
    if len(project_name) != 1:
        print('Unable to determine project name!')
        sys.exit(1)
    project_name = project_name[0]
    project_name = re.sub('\.para', '', project_name)

    # create new para file with out duration
    f = open(project_name + '.para', 'w')
    f.write('''0	1	3
1	1	1	1
1	1	1
1	1	1
1	1	1	1	1	1	1	1	1	1
1440	1440	1440	1440
1440	1440	1440	1440	1440
2	2	2
2	1	0	0
0.0001	0.001	1e-05	30	1
0	%d	0
1	1
''' %(duration_mins))
    f.close()

    # copy the forcing data into place
    my_cmd('cp ../' + sys.argv[3] + ' ' + project_name + '.forc')

    # run the model
    my_cmd('/usr/bin/pihm ' + project_name + ' 2>&1')

    os.chdir('..')
    my_cmd('mv PIHM-base PIHM-state && tar czf PIHM-state.tar.gz PIHM-state')


main()


