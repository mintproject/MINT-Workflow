#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 14:12:29 2018

@author: deborahkhider

Transformation code from CYCLES double output to Crop model
"""
#import numpy as np
import tarfile
import pandas as pd
import csv
import sys

#
#CYCLES needs to be run twice. One is the baseline scenario. The second has an
#increase in 10% fertilizer. 
#
percent_fertilizer = 0.1 #This should become a parameter

# Set the tarfiles path
base_run_file = sys.argv[1]
scenario_run_file = sys.argv[2]

# Open the base tar file
base_run = tarfile.open(name = base_run_file)
base_run_names = base_run.getnames()
for item in base_run_names:
    if 'season' in item:
        file_name = item
        base_file = base_run.extract(item)

# Open the files and look for the grain yield
data = pd.read_table(file_name, delimiter = '\t',\
                     skiprows = [1], index_col=False)

# Get the Grain yield header
for item in list(data):
    if 'GRAIN YIELD' in item:
        header = item

base_grain = data[header].mean()

# Do the same with the increased fertilizer run
scenario_run = tarfile.open(name = scenario_run_file)
scenario_run_names = scenario_run.getnames()
for item in scenario_run_names:
    if 'season' in item:
        file_name = item
        scenario_file = scenario_run.extract(item)

# Open the files and look for the grain yield
data = pd.read_table(file_name, delimiter = '\t',\
                     skiprows = [1], index_col=False)

# Get the Grain yield header
for item in list(data):
    if 'GRAIN YIELD' in item:
        header = item

scenario_grain = data[header].mean()
         
# Calculate the yield %
percent_yield = (scenario_grain-base_grain)/base_grain

#elasticity
el = percent_yield/percent_fertilizer

# write out as csv file
csv_file = 'yieldelast.csv'

with open(csv_file,'w',newline='') as csvfile:
    yieldwriter = csv.writer(csvfile, delimiter=',')
    yieldwriter.writerow(['sorghum',el])

