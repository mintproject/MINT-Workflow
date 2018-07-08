#!/usr/bin/env python3

import configparser
import datetime
import math
import subprocess
import sys

from netCDF4 import Dataset
from dateutil import parser


def closest(start_dt, lat, lon):
    '''
    read a FLDAS NC file, and figure out what the closest x,y grid point
    is to the give lat,lon
    '''
    best_x = None
    best_y = None
    best_distance = 1000000000
    nc_path = 'FLDAS_NOAH01_A_EA_D.001/%d/%02d/FLDAS_NOAH01_A_EA_D.A%d%02d%02d.001.nc' \
              %(start_dt.year, start_dt.month, start_dt.year, start_dt.month, start_dt.day)
    nc = Dataset(nc_path, 'r')

    dim_x = nc.dimensions['X'].size                                                                 
    dim_y = nc.dimensions['Y'].size   
    for x in range(0, dim_x):
        for y in range(0, dim_y):
            grid_lat = float(nc['Y'][y])
            grid_lon = float(nc['X'][x])
            distance = math.sqrt((lat - grid_lat)**2 + (lon - grid_lon)**2)
            if distance < best_distance:
                best_distance = distance
                best_x = x
                best_y = y

    print("Closest grid point is: y=%d, x=%d (lat=%.2f, lon=%.2f)" \
          %(best_y, best_x, nc['Y'][best_y], nc['X'][best_x]))
    return (best_y, best_x, nc['Y'][best_y], nc['X'][best_x])


def satvp(temp):
    return .6108 * math.exp(17.27 * temp / (temp + 237.3))


def tdew(ea):
    return 237.3 * math.log(ea / 0.6108) / (17.27 - math.log(ea / 0.6108))


def ea(patm, q):
    return patm * q / (0.622 * (1 - q) + q)


def process_day(dt, y, x):
    '''
    process one day of FLDAS data and convert it to Cycles input
    '''
    nc_path = 'FLDAS_NOAH01_A_EA_D.001/%d/%02d/FLDAS_NOAH01_A_EA_D.A%d%02d%02d.001.nc' \
              %(dt.year, dt.month, dt.year, dt.month, dt.day)
    print('Opening ' + nc_path)
    nc = Dataset(nc_path, 'r')
 
    tavg = nc['Tair_f_tavg'][0, y, x] - 273.15
    ea_kPa = ea(nc['Psurf_f_tavg'][0, y, x], nc['Qair_f_tavg'][0, y, x]) / 1000
    rH = ea_kPa / satvp(tavg)
    vpd_ea = satvp(tavg) - ea_kPa

    #This formula is empiric and location / season dependent; hopefully is not needed
    # if LDAS provides Tmax and Tmin instead of the average for the day
    delta_T = 17.37 * (1 - 1 / (1 + vpd_ea / (0.33 * ea_kPa)))
    Tdew = tdew(ea_kPa)
    Patm = nc['Psurf_f_tavg'][0, y, x]
    
    pp = nc['Rainf_f_tavg'][0, y, x] * 86400
    tx = tavg + .5 * delta_T
    tn = tavg - .5 * delta_T
    solar =  nc['SWdown_f_tavg'][0, y, x] * 86400 / 1000000
    if tn > Tdew:
        rhx = 100 * ea_kPa / satvp(tn)
    else:
        rhx = 99.9
    if tx > Tdew:
        rhn = 100 * ea_kPa / satvp(tx)
    else:
        rhn = 99.8
    wind = nc['Wind_f_tavg'][0, y, x]

    data = '%s  %6.2f  %6.2f  %6.2f  %8.4f  %8.4f %8.4f %6.2f\n' \
           %(dt.strftime('%Y  %j'), pp, tx, tn, solar, rhx, rhn, wind)

    return (data, Patm)


def main():

    # unique name is argv[1]
    unique_name = sys.argv[1]

    # weater input is a tarball
    if subprocess.call('tar xzf weather.tar.gz', shell=True) != 0:
        print("Untaring weather.tar.gz failed")
        sys.exit(1)

    # get the general configuration from the global mint_run.config
    fp = open('mint_run.config', 'r')
    config_string = '[DEFAULT]\n' + fp.read()
    fp.close()
    run_config = configparser.ConfigParser()
    run_config.read_string(config_string)

    # get the model configuration from mint_cycles.config
    fp = open('mint_cycles-' + unique_name + '.config', 'r')
    config_string = '[DEFAULT]\n' + fp.read()
    fp.close()
    config = configparser.ConfigParser()
    config.read_string(config_string)

    start_year = run_config.get('DEFAULT', 'start_year')
    start_dt = parser.parse(start_year + '-01-01T00:00:00')
    end_year = run_config.get('DEFAULT', 'end_year')
    end_dt = parser.parse(end_year + '-12-31T23:59:59')

    lat = config.get('DEFAULT', 'lat')
    lon = config.get('DEFAULT', 'lon')

    # find the FLDAS x,y closest to the lon,lat
    (y, x, grid_lat, grid_lon) = closest(start_dt, float(lat), float(lon))
    
    # now extract daily values for the time range
    data = ""
    Patm_total = 0.0
    Patm_count = 0
    dt = start_dt
    while dt <= end_dt:
        (line, Patm) = process_day(dt, y, x)
        data += line
        Patm_total += Patm
        Patm_count += 1
        # move on to the next day
        dt = dt + datetime.timedelta(days = 1)

    Patm_avg = Patm_total / Patm_count
    elevation = - 8200 * math.log(Patm_avg / 101325) 

    fname = 'Cycles-' + unique_name + '.weather'
    fp = open(fname, 'w')
    fp.write('LATITUDE %.2f\n' %float(lat))
    # TODO, were do we get altitude and screening height from?
    fp.write('ALTITUDE %.2f\n' %(elevation))
    fp.write('SCREENING_HEIGHT 2\n')
    fp.write('YEAR  DOY     PP      TX      TN     SOLAR      RHX      RHN     WIND\n')
    fp.write(data)
    fp.close()

main()

