#!/usr/bin/env python3

import configparser
import glob
import datetime
import os
import subprocess
import sys
import re

from string import Template

crop_templates = { 'Corn': '''

TILLAGE
YEAR                $year_num   # $year
DOY                 90
TOOL                Kill_Crop
DEPTH               0
SOIL_DISTURB_RATIO  0
MIXING_EFFICIENCY   0
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

FIXED_FERTILIZATION
YEAR                $year_num
DOY                 90
SOURCE              25-25-00
MASS                $mass
FORM                Solid
METHOD              Broadcast
LAYER               1
C_Organic           0
C_Charcoal          0
N_Organic           0
N_Charcoal          0
N_NH4               0.25
N_NO3               0
P_Organic           0
P_CHARCOAL          0
P_INORGANIC         0.25
K                   0
S                   0

TILLAGE
YEAR                $year_num
DOY                 90
TOOL                Hand_hoeing
DEPTH               0.11
SOIL_DISTURB_RATIO  25
MIXING_EFFICIENCY   0.85
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

PLANTING
YEAR                $year_num
DOY                 100
CROP                Corn
USE_AUTO_IRR        0
USE_AUTO_FERT       0
FRACTION            0.67
CLIPPING_START      1
CLIPPING_END        366

TILLAGE
YEAR                $year_num
DOY                 120
TOOL                Hand_hoeing_weeding
DEPTH               0.06
SOIL_DISTURB_RATIO  15
MIXING_EFFICIENCY   0.25
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

###

FIXED_FERTILIZATION
YEAR                $year_num
DOY                 220
SOURCE              25-25-00
MASS                $mass
FORM                Solid
METHOD              Broadcast
LAYER               1
C_Organic           0
C_Charcoal          0
N_Organic           0
N_Charcoal          0
N_NH4               0.25
N_NO3               0
P_Organic           0
P_CHARCOAL          0
P_INORGANIC         0.25
K                   0
S                   0

TILLAGE
YEAR                $year_num
DOY                 221
TOOL                Hand_hoeing
DEPTH               0.11
SOIL_DISTURB_RATIO  25
MIXING_EFFICIENCY   0.85
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

PLANTING
YEAR                $year_num
DOY                 225
CROP                Corn
USE_AUTO_IRR        0
USE_AUTO_FERT       0
FRACTION            0.67
CLIPPING_START      1
CLIPPING_END        366

TILLAGE
YEAR                $year_num
DOY                 240
TOOL                Hand_hoeing_weeding
DEPTH               0.06
SOIL_DISTURB_RATIO  15
MIXING_EFFICIENCY   0.25
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0
''', ###########################################################
'Peanut': '''

TILLAGE
YEAR                $year_num  # $year
DOY                 90
TOOL                Kill_Crop
DEPTH               0   
SOIL_DISTURB_RATIO  0   
MIXING_EFFICIENCY   0   
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

FIXED_FERTILIZATION
YEAR                $year_num
DOY                 90
SOURCE              25-25-00
MASS                0 
FORM                Solid
METHOD              Broadcast
LAYER               1     
C_Organic           0     
C_Charcoal          0     
N_Organic           0     
N_Charcoal          0     
N_NH4               0.25  
N_NO3               0     
P_Organic           0     
P_CHARCOAL          0     
P_INORGANIC         0.25
K                   0     
S                   0     

TILLAGE
YEAR                $year_num
DOY                 90
TOOL                Hand_hoeing
DEPTH               0.11
SOIL_DISTURB_RATIO  25   
MIXING_EFFICIENCY   0.85
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

PLANTING
YEAR                $year_num
DOY                 100
CROP                Peanut
USE_AUTO_IRR        0
USE_AUTO_FERT       0
FRACTION            0.67
CLIPPING_START      1
CLIPPING_END        366

TILLAGE
YEAR                $year_num
DOY                 120
TOOL                Hand_hoeing_weeding
DEPTH               0.06
SOIL_DISTURB_RATIO  15   
MIXING_EFFICIENCY   0.25
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0
''', ###########################################################
'Sorghum': '''

TILLAGE
YEAR                $year_num  # $year
DOY                 90
TOOL                Kill_Crop
DEPTH               0   
SOIL_DISTURB_RATIO  0   
MIXING_EFFICIENCY   0   
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

FIXED_FERTILIZATION
YEAR                $year_num
DOY                 90
SOURCE              25-25-00
MASS                $mass
FORM                Solid
METHOD              Broadcast
LAYER               1     
C_Organic           0     
C_Charcoal          0     
N_Organic           0     
N_Charcoal          0     
N_NH4               0.25  
N_NO3               0     
P_Organic           0     
P_CHARCOAL          0     
P_INORGANIC         0.25
K                   0     
S                   0     

TILLAGE
YEAR                $year_num
DOY                 90
TOOL                Hand_hoeing
DEPTH               0.11
SOIL_DISTURB_RATIO  25   
MIXING_EFFICIENCY   0.85
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

PLANTING
YEAR                $year_num
DOY                 100
CROP                Sorghum
USE_AUTO_IRR        0
USE_AUTO_FERT       0
FRACTION            0.67
CLIPPING_START      1
CLIPPING_END        366

TILLAGE
YEAR                $year_num
DOY                 120
TOOL                Hand_hoeing_weeding
DEPTH               0.06
SOIL_DISTURB_RATIO  15   
MIXING_EFFICIENCY   0.25
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

###

FIXED_FERTILIZATION
YEAR                $year_num
DOY                 220
SOURCE              25-25-00
MASS                $mass
FORM                Solid
METHOD              Broadcast
LAYER               1     
C_Organic           0     
C_Charcoal          0     
N_Organic           0     
N_Charcoal          0     
N_NH4               0.25  
N_NO3               0     
P_Organic           0     
P_CHARCOAL          0     
P_INORGANIC         0.25
K                   0     
S                   0 

TILLAGE
YEAR                $year_num
DOY                 221
TOOL                Hand_hoeing
DEPTH               0.11
SOIL_DISTURB_RATIO  25   
MIXING_EFFICIENCY   0.85
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0

PLANTING
YEAR                $year_num
DOY                 225
CROP                Sorghum
USE_AUTO_IRR        0
USE_AUTO_FERT       0
FRACTION            0.67
CLIPPING_START      1
CLIPPING_END        366

TILLAGE
YEAR                $year_num
DOY                 240
TOOL                Hand_hoeing_weeding
DEPTH               0.06
SOIL_DISTURB_RATIO  15   
MIXING_EFFICIENCY   0.25
CROP_NAME           N/A
FRAC_THERMAL_TIME   0.0
KILL_EFFICIENCY     0.0
GRAIN_HARVEST       0
FORAGE_HARVEST      0.0
'''}


def my_cmd(cmd):
    print()
    print(cmd)
    exit_code = subprocess.call(cmd, shell=True)
    if exit_code != 0:
        print('Command failed with exit code %d' %(exit_code))
        sys.exit(1)

def find_file(pattern):
    '''
    Finds a file matching the pattern. Note that this should only
    return success iff 1 file is found
    '''
    files = glob.glob(pattern)
    if len(files) == 0:
        raise RuntimeError('No file found matching ' + pattern)
    if len(files) > 1:
        raise RuntimeError('Multiple files found matching ' + pattern)
    return files[0]

def main():

    # get the general configuration from the global mint_run.config
    fp = open(sys.argv[1], 'r')
    config_string = '[DEFAULT]\n' + fp.read()
    fp.close()
    run_config = configparser.ConfigParser()
    run_config.read_string(config_string)

    start_year = int(run_config.get('DEFAULT', 'start_year'))
    end_year = int(run_config.get('DEFAULT', 'end_year'))
    num_years = end_year - start_year + 1

    # arguments
    crop = sys.argv[2]
    scenario = sys.argv[3]

    fertilization_factor = 1.0
    if 'percent_inc' in scenario:
        fertilization_factor = 1.0 + (float(re.sub('_percent_inc', '', scenario)) / 100.0)

    # grab the base state
    my_cmd('wget -nv -O Cycles-base.tar.gz http://workflow.isi.edu/MINT/MINT-Workflow/v2/Cycles-base.tar.gz')
    my_cmd('tar xzf Cycles-base.tar.gz')
    my_cmd('mv Cycles-base input')

    # put the weahter and reinit files in place
    my_cmd('rm -f input/*.weather input/*.REINIT')
    my_cmd('cp *.weather *.REINIT input/')

    os.chdir('input')

    # create control file
    f = open('my.ctrl', 'w')
    f.write('''
## SIMULATION YEARS ##

SIMULATION_START_YEAR   %d
SIMULATION_END_YEAR     %d
ROTATION_SIZE           %d

## SIMULATION OPTIONS ##

USE_REINITIALIZATION    1
ADJUSTED_YIELDS         0
HOURLY_INFILTRATION     1
AUTOMATIC_NITROGEN      0
AUTOMATIC_PHOSPHORUS    0
AUTOMATIC_SULFUR        0
DAILY_WEATHER_OUT       1
DAILY_CROP_OUT          1
DAILY_RESIDUE_OUT       0
DAILY_WATER_OUT         1
DAILY_NITROGEN_OUT      1
DAILY_SOIL_CARBON_OUT   0
DAILY_SOIL_LYR_CN_OUT   0
ANNUAL_SOIL_OUT         1
ANNUAL_PROFILE_OUT      1
SEASON_OUT              1

## OTHER INPUT FILES ##

CROP_FILE               %s
OPERATION_FILE          my.operation
SOIL_FILE               %s
WEATHER_FILE            %s
REINIT_FILE             %s
''' %(start_year, end_year, num_years,
       find_file('*.crop'),
       find_file('*.soil'),
       find_file('*.weather'),
       find_file('*.REINIT'))
)
    f.close()
        
    if crop not in crop_templates:
        raise('I do not know how to handle crop: ' + crop)
    op = Template(crop_templates[crop]) 

    # create the operations file
    f = open('my.operation', 'w')
    for year in range(start_year, end_year + 1):
        year_num = year - start_year + 1
        f.write(op.substitute(year = year, year_num = year_num, mass = 100 * fertilization_factor))
    f.close()

    # now run Cycles
    os.chdir('..')
    my_cmd('Cycles my')

    # move/create expected outputs
    my_cmd('mv output Cycles-' + crop + '-' + scenario + '-results')
    my_cmd('tar czf Cycles-' + crop + '-' + scenario + '-results.tar.gz Cycles-' + crop + '-' + scenario + '-results')
    

main()




